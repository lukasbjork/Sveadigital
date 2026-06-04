#!/usr/bin/env python3
"""Hämtar föregående månads statistik från Umami Cloud och levererar en
månadsrapport via Web3Forms (mejl) + sparar den som reports/YYYY-MM.md.

Körs av GitHub Actions (.github/workflows/monthly-report.yml).
Endast Python-standardbibliotek används (ingen pip install behövs).

Konfiguration via miljövariabler:
  UMAMI_API_KEY        (hemlig, GitHub secret) – KRÄVS
  UMAMI_WEBSITE_ID     – default = sveadigital.se:s website-id
  WEB3FORMS_ACCESS_KEY – publik nyckel för mejlleverans (tom = hoppa över mejl)
  REPORT_MONTH         – 'YYYY-MM' för en specifik månad (tom = föregående månad)
"""
import os
import sys
import json
import calendar
from datetime import datetime, timezone, timedelta
from urllib import request, parse, error

API_BASE = "https://api.umami.is/v1"
SITE_URL = "https://sveadigital.se"

# Umamis API ligger bakom Cloudflare som blockerar Pythons standard-User-Agent
# (Error 1010). En vanlig webbläsar-UA krävs för att komma igenom.
USER_AGENT = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
              "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")

API_KEY = os.environ.get("UMAMI_API_KEY", "").strip()
WEBSITE_ID = os.environ.get(
    "UMAMI_WEBSITE_ID", "bc0ebba3-a1f1-4047-b0be-d72153b63645"
).strip()
WEB3FORMS_KEY = os.environ.get("WEB3FORMS_ACCESS_KEY", "").strip()
REPORT_MONTH = os.environ.get("REPORT_MONTH", "").strip()

MANADER_SV = [
    "januari", "februari", "mars", "april", "maj", "juni",
    "juli", "augusti", "september", "oktober", "november", "december",
]

# Snygga svenska etiketter för dina konverterings-events
EVENT_LABELS = {
    "boka-samtal-hero": "Boka samtal – hero-knapp",
    "boka-samtal-nav": "Boka samtal – meny",
    "boka-samtal-mobil": "Boka samtal – mobilmeny",
    "kontakta-oss": "Kontakta oss-knapp",
    "se-priser": "Se priser-knapp",
    "pris-start": "Prisknapp: Start",
    "pris-vax": "Prisknapp: Väx",
    "pris-partner": "Prisknapp: Partner",
    "mejl": "Mejlklick (kontaktsektion)",
    "mejl-footer": "Mejlklick (sidfot)",
    "scroll-botten": "Läste hela startsidan",
    "lead-formular": "LEAD – kontaktformulär skickat",
    "lead-analys": "LEAD – gratis analys skickad",
}
LEAD_EVENTS = {"lead-formular", "lead-analys"}


def fail(msg):
    print(f"FEL: {msg}", file=sys.stderr)
    sys.exit(1)


def month_bounds(yy, mm):
    """Returnerar (start_ms, end_ms) för en hel kalendermånad i UTC."""
    start = datetime(yy, mm, 1, tzinfo=timezone.utc)
    last_day = calendar.monthrange(yy, mm)[1]
    end = datetime(yy, mm, last_day, 23, 59, 59, 999000, tzinfo=timezone.utc)
    return int(start.timestamp() * 1000), int(end.timestamp() * 1000)


def resolve_month():
    """Returnerar (year, month) – från REPORT_MONTH eller föregående månad."""
    if REPORT_MONTH:
        try:
            y, m = (int(x) for x in REPORT_MONTH.split("-"))
            datetime(y, m, 1)  # validerar
            return y, m
        except (ValueError, TypeError):
            fail(f"Ogiltig REPORT_MONTH: {REPORT_MONTH!r} (förväntar YYYY-MM)")
    today = datetime.now(timezone.utc).date()
    last_prev = today.replace(day=1) - timedelta(days=1)
    return last_prev.year, last_prev.month


def api_get(path, params):
    url = f"{API_BASE}{path}?{parse.urlencode(params)}"
    req = request.Request(url, headers={
        "Accept": "application/json",
        "x-umami-api-key": API_KEY,
        "User-Agent": USER_AGENT,
    })
    try:
        with request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except error.HTTPError as e:
        body = e.read().decode("utf-8", "replace")
        fail(f"API {path} svarade {e.code}: {body[:300]}")
    except Exception as e:  # noqa: BLE001
        fail(f"API {path} misslyckades: {e}")


def num(v):
    """Stats-fält kan vara {'value': N, 'prev': M} eller bara N."""
    if isinstance(v, dict):
        return v.get("value", 0) or 0
    return v or 0


def pct_change(curr, prev):
    if not prev:
        return None
    return (curr - prev) / prev * 100.0


def fmt_delta(curr, prev):
    p = pct_change(curr, prev)
    if p is None:
        return "(ingen jämförelse)"
    arrow = "▲" if p > 0 else ("▼" if p < 0 else "—")
    return f"{arrow} {p:+.0f}% mot förra månaden"


def get_stats(start_ms, end_ms):
    return api_get(f"/websites/{WEBSITE_ID}/stats",
                   {"startAt": start_ms, "endAt": end_ms}) or {}


def get_metric(typ, start_ms, end_ms, limit=10):
    data = api_get(f"/websites/{WEBSITE_ID}/metrics",
                   {"startAt": start_ms, "endAt": end_ms,
                    "type": typ, "limit": limit})
    return [(row.get("x"), row.get("y", 0)) for row in (data or [])]


def build_report(y, m, stats, prev_stats, referrers, pages,
                 countries, devices, events):
    manad = MANADER_SV[m - 1]
    pv = num(stats.get("pageviews"))
    vis = num(stats.get("visitors"))
    visits = num(stats.get("visits"))
    bounces = num(stats.get("bounces"))
    totaltime = num(stats.get("totaltime"))

    ppv = num(prev_stats.get("pageviews"))
    pvis = num(prev_stats.get("visitors"))

    bounce_rate = (bounces / visits * 100) if visits else 0
    avg_sec = (totaltime / visits) if visits else 0
    avg_min, avg_rest = int(avg_sec // 60), int(avg_sec % 60)

    L = []
    L.append("# 📊 Månadsrapport – sveadigital.se")
    L.append(f"## {manad.capitalize()} {y}")
    L.append("")
    L.append("### Översikt")
    L.append(f"- 👀 Sidvisningar: {pv}  ·  {fmt_delta(pv, ppv)}")
    L.append(f"- 🧑 Unika besökare: {vis}  ·  {fmt_delta(vis, pvis)}")
    L.append(f"- 🔁 Besök (sessioner): {visits}")
    L.append(f"- ⏱️ Snittid på sidan: {avg_min} min {avg_rest} s")
    L.append(f"- 🦘 Avvisningsfrekvens: {bounce_rate:.0f}%")
    L.append("")

    L.append("### 🎯 Konverteringar & leads")
    if events:
        leads = [(n, c) for n, c in events if n in LEAD_EVENTS]
        clicks = [(n, c) for n, c in events if n not in LEAD_EVENTS]
        total_leads = sum(c for _, c in leads)
        L.append(f"- **Totalt antal leads (formulär): {total_leads}**")
        for n, c in sorted(leads, key=lambda t: -t[1]):
            L.append(f"  - {EVENT_LABELS.get(n, n)}: {c}")
        if clicks:
            L.append("- Knappklick:")
            for n, c in sorted(clicks, key=lambda t: -t[1]):
                L.append(f"  - {EVENT_LABELS.get(n, n)}: {c}")
    else:
        L.append("- Inga registrerade events denna månad.")
    L.append("")

    def section(title, rows, label_direct=False):
        L.append(f"### {title}")
        if rows:
            for name, count in rows:
                label = name or ("(direkt / okänd)" if label_direct else "(okänd)")
                L.append(f"- {label}: {count}")
        else:
            L.append("- (ingen data)")
        L.append("")

    section("🔗 Toppkällor (varifrån besökarna kom)", referrers, label_direct=True)
    section("📄 Populäraste sidor", pages)
    section("🌍 Länder", countries)
    section("💻 Enheter", devices)

    L.append("---")
    L.append(f"Genererad {datetime.now(timezone.utc):%Y-%m-%d %H:%M} UTC "
             f"· data från Umami · {SITE_URL}")
    return "\n".join(L)


def send_email(subject, body):
    if not WEB3FORMS_KEY:
        print("WEB3FORMS_ACCESS_KEY saknas – hoppar över mejl.")
        return
    payload = json.dumps({
        "access_key": WEB3FORMS_KEY,
        "subject": subject,
        "from_name": "Sveadigital Statistik",
        "message": body,
    }).encode("utf-8")
    req = request.Request(
        "https://api.web3forms.com/submit", data=payload,
        headers={"Content-Type": "application/json", "Accept": "application/json",
                 "User-Agent": USER_AGENT},
    )
    try:
        with request.urlopen(req, timeout=30) as resp:
            res = json.loads(resp.read().decode("utf-8"))
        if res.get("success"):
            print("Mejl skickat via Web3Forms.")
        else:
            print(f"Web3Forms svarade utan success: {res}", file=sys.stderr)
    except Exception as e:  # noqa: BLE001
        print(f"Mejlutskick misslyckades: {e}", file=sys.stderr)


def main():
    if not API_KEY:
        fail("UMAMI_API_KEY saknas (lägg till som GitHub secret).")

    y, m = resolve_month()
    start_ms, end_ms = month_bounds(y, m)
    pm_y, pm_m = (y - 1, 12) if m == 1 else (y, m - 1)
    pstart_ms, pend_ms = month_bounds(pm_y, pm_m)
    print(f"Genererar rapport för {y}-{m:02d} ...")

    stats = get_stats(start_ms, end_ms)
    prev_stats = get_stats(pstart_ms, pend_ms)
    referrers = get_metric("referrer", start_ms, end_ms)
    pages = get_metric("url", start_ms, end_ms)
    countries = get_metric("country", start_ms, end_ms)
    devices = get_metric("device", start_ms, end_ms)
    events = get_metric("event", start_ms, end_ms, limit=50)

    report = build_report(y, m, stats, prev_stats, referrers, pages,
                          countries, devices, events)

    os.makedirs("reports", exist_ok=True)
    fname = f"reports/{y}-{m:02d}.md"
    with open(fname, "w", encoding="utf-8") as f:
        f.write(report + "\n")
    print(f"Sparade {fname}")

    subject = f"📊 Månadsrapport sveadigital.se – {MANADER_SV[m - 1]} {y}"
    send_email(subject, report)
    print("Klart.")


if __name__ == "__main__":
    main()
