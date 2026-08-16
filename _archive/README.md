# Arkiv — portfolio, kundcase och omdömessektionen

Arkiverat **2026-08-16** inför lansering. Ingenting här är raderat, bara avpublicerat.

## Varför mappen inte publiceras

Sajten byggs av GitHub Pages med Jekyll (ingen egen workflow, ingen `.nojekyll`).
Jekyll hoppar över alla mappar som börjar med `_`, så allt under `_archive/`
ligger kvar i repot men når aldrig sveadigital.se.

> **Kontrollera efter deploy:** `https://sveadigital.se/_archive/README.md` ska ge 404.
> Skulle den svara 200 har byggmetoden ändrats — flytta då arkivet ur repot
> eller lägg till `exclude: ["_archive"]` i en `_config.yml`.

## Vad som ligger här

| Sökväg | Låg tidigare på |
|---|---|
| `portfolio.html` | `/portfolio` |
| `kundcase/` (index + 6 case) | `/kundcase`, `/kundcase/<slug>` |
| `showcase/` (6 demosidor) | `/showcase/<slug>.html` |
| `assets/portfolio/` (12 webp) | `/assets/portfolio/` |
| `index-sections/portfolio-section.html` | `index.html`, mellan BRANSCHER och PROCESS |
| `index-sections/omdomen-section.html` | `index.html`, mellan PROCESS och TRYGGHET |
| `tjanster-sections/portfolio-cta-section.html` | `tjanster.html`, sist i `<main>` |
| `removed-snippets.md` | Små fragment: menyrader, hero-knapp, relaterade-länkar |

De arkiverade HTML-filerna refererar till `/assets/portfolio/...`. Bilderna
ligger nu i `_archive/assets/portfolio/`, så bilderna är trasiga i arkivet tills
mappen flyttas tillbaka — sökvägarna i filerna behöver alltså inte ändras.

## Omdirigeringar som ligger uppe nu

De 14 gamla adresserna finns kvar som minimala stubbar i sajtroten
(`portfolio.html`, `kundcase/*.html`, `showcase/*.html`). Varje stub har
`<meta http-equiv="refresh" content="0; url=/">` + `<link rel="canonical">` mot
startsidan. GitHub Pages kan inte skicka riktiga HTTP 301-svar; det här är den
etablerade motsvarigheten och behandlas av Google som en permanent flytt.

**Stubbarna måste raderas innan innehållet flyttas tillbaka**, annars skriver de
över de riktiga sidorna.

---

## Så tar du tillbaka portfolio + kundcase

```bash
cd website

# 1. Ta bort omdirigeringsstubbarna
rm portfolio.html
rm -r kundcase showcase

# 2. Flytta tillbaka innehållet
git mv _archive/portfolio.html portfolio.html
git mv _archive/kundcase kundcase
git mv _archive/showcase showcase
mkdir -p assets && git mv _archive/assets/portfolio assets/portfolio
```

3. **Startsidan** (`index.html`): klistra in innehållet i
   `_archive/index-sections/portfolio-section.html` mellan `</section>` för
   BRANSCHER och kommentaren `<!-- PROCESS -->`.
4. **Tjänstesidan** (`tjanster.html`): klistra in
   `_archive/tjanster-sections/portfolio-cta-section.html` sist i `<main>`.
5. **Meny, footer, hero och relaterade guider**: se `removed-snippets.md`.
6. **Bakgrundsrytmen**: ändra tillbaka `<section class="section section--alt" id="process">`
   till `<section class="section" id="process">` i `index.html` och ta bort
   kommentaren ovanför. (Sektionerna växlar ljus/mörk bakgrund; utan portfolio-
   och omdömessektionerna behövdes en flip för att rytmen skulle hålla.)
7. **sitemap.xml**: lägg tillbaka `/portfolio`, `/kundcase` och de sex
   `/kundcase/<slug>` med aktuellt `lastmod`.
8. **robots.txt**: ersätt kommentaren om omdirigeringar med den gamla texten om
   att `/showcase/` hålls crawlbar för sin `noindex`.
9. Kör länkkontrollen (se nedan).

## Så tar du tillbaka omdömessektionen

Gör bara steg 3 (med `omdomen-section.html`, mellan PROCESS och TRYGGHET) och
steg 6. Sektionen har inga egna länkar, ingen sitemap-post och ingen
strukturerad data.

**Innan den publiceras igen:** sektionen innehåller platshållarna `[XX]+`,
`[X,X]/5`, `[Google-betyg]`, `[Trustpilot-betyg]` och tre tomma kundcitat. De
måste bytas mot riktiga uppgifter — annars var det just därför den plockades ned.
Lägg till `aggregateRating`/`Review` i JSON-LD först när betygen är verkliga och
syns på sidan; Google kräver att strukturerad data speglar synligt innehåll.

## Länkkontroll

```bash
python tools/check_links.py   # körs från reporoten, hoppar över _archive/
```

Skriptet går igenom varje publicerad HTML-sida, följer alla interna
`href`/`src`, kontrollerar att målfilen och eventuella `#ankare` finns, och
larmar om platshållare som `[ORG.NR]` eller `[TELEFONNUMMER]` letat sig tillbaka.
