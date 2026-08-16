# Borttagna fragment (2026-08-16)

Små bitar som togs bort ur befintliga filer. Se `README.md` för helheten.

## 1. Huvudmeny — desktop

Låg i `<nav class="nav-links">` direkt efter `<a href="/tjanster">Tjänster</a>`,
på **alla 27 publicerade sidor** (indrag: 8 mellanslag):

```html
        <a href="/portfolio">Portfolio</a>
        <a href="/kundcase">Kundcase</a>
```

## 2. Huvudmeny — mobil

Låg i `<div class="mobile-menu">` direkt efter `<a href="/tjanster">Tjänster</a>`,
på alla 27 sidor (indrag: 6 mellanslag):

```html
      <a href="/portfolio">Portfolio</a>
      <a href="/kundcase">Kundcase</a>
```

## 3. Footer — kolumnen "Innehåll"

Låg i `<div class="footer-links">` direkt efter `<a href="/tjanster">Tjänster</a>`,
på alla 27 sidor (indrag: 10 mellanslag):

```html
          <a href="/portfolio">Portfolio</a>
          <a href="/kundcase">Kundcase</a>
```

## 4. Hero-knappen på startsidan

Låg i `<div class="hero-cta">` i `index.html`, direkt efter knappen
"Boka gratis rådgivning":

```html
          <a href="/portfolio" class="btn btn-ghost btn-lg" data-umami-event="se-projekt-hero">Se våra projekt</a>
```

## 5. "Relaterade guider" i blogginläggen

Sista `<li>` i `<ul class="related-list">`. Ett per inlägg, 20 totalt.
Indrag: 12 mellanslag.

| Fil | Borttagen rad |
|---|---|
| `blogg/490-frisorer-stockholm.html` | `<li><a href="/kundcase/salong-stella">Kundcase: Salong Stella — så byggde vi en salongssida</a></li>` |
| `blogg/7-tecken-frisorsalong-hemsida.html` | `<li><a href="/kundcase/salong-stella">Kundcase: Salong Stella — från DM-bokningar till egen sida</a></li>` |
| `blogg/bokningssystem-frisorer.html` | `<li><a href="/kundcase/salong-stella">Kundcase: Salong Stella — bokningsflöde för en salong</a></li>` |
| `blogg/priser-pa-hemsidan-frisorer.html` | `<li><a href="/kundcase/salong-stella">Kundcase: Salong Stella — bokningsflöde för en salong</a></li>` |
| `blogg/fler-google-recensioner.html` | `<li><a href="/kundcase/bjorklunds-el">Kundcase: Björklunds El — hemsida för en elfirma</a></li>` |
| `blogg/offert-hantverkare-mall.html` | `<li><a href="/kundcase/bjorklunds-el">Kundcase: Björklunds El — hemsida för en elfirma</a></li>` |
| `blogg/google-business-profile-hantverkare.html` | `<li><a href="/kundcase/bjorklunds-el">Kundcase: Björklunds El — synlig för den som söker</a></li>` |
| `blogg/kontaktformular-misstag.html` | `<li><a href="/kundcase/bjorklunds-el">Kundcase: Björklunds El — offertformulär som ger underlag</a></li>` |
| `blogg/rot-avdrag-elinstallationer-2026.html` | `<li><a href="/kundcase/bjorklunds-el">Kundcase: Björklunds El — offertformulär som ger underlag</a></li>` |
| `blogg/lokal-seo-restauranger-google-maps.html` | `<li><a href="/kundcase/restaurang-hamnen">Kundcase: Restaurang Hamnen — menyn ut ur PDF:en</a></li>` |
| `blogg/meny-pa-hemsidan-restaurang.html` | `<li><a href="/kundcase/restaurang-hamnen">Kundcase: Restaurang Hamnen — menyn som låg som PDF</a></li>` |
| `blogg/checklista-hemsida.html` | `<li><a href="/portfolio">Se sex exempelprojekt i portfolion</a></li>` |
| `blogg/digital-narvaro-semestertider.html` | `<li><a href="/portfolio">Se sex exempelprojekt i portfolion</a></li>` |
| `blogg/hemsida-eller-google-business-profile.html` | `<li><a href="/portfolio">Se sex exempelprojekt i portfolion</a></li>` |
| `blogg/hemsida-vs-instagram.html` | `<li><a href="/portfolio">Se sex exempelprojekt i portfolion</a></li>` |
| `blogg/langsam-hemsida-laddtid.html` | `<li><a href="/portfolio">Se sex exempelprojekt i portfolion</a></li>` |
| `blogg/mobilanpassad-hemsida.html` | `<li><a href="/portfolio">Se sex exempelprojekt i portfolion</a></li>` |
| `blogg/vad-ar-meta-description.html` | `<li><a href="/portfolio">Se sex exempelprojekt i portfolion</a></li>` |
| `blogg/vad-kostar-en-hemsida-2026.html` | `<li><a href="/portfolio">Se sex exempelprojekt i portfolion</a></li>` |
| `blogg/valja-ratt-webbyra.html` | `<li><a href="/portfolio">Se sex exempelprojekt i portfolion</a></li>` |

---

# Ändringar som INTE ska rullas tillbaka

Dessa gjordes samtidigt men hör inte ihop med arkiveringen:

- **Org.nr borttaget.** Raden `<span>Org.nr [ORG.NR]</span>` togs bort ur
  footern på alla 27 sidor. Lägg tillbaka den först när bolaget är registrerat.
- **"AB" borttaget.** `Svea Digital AB` → `Svea Digital` på 73 ställen
  (copyrightrad, JSON-LD `Organization`/`ProfessionalService`/`author`/`publisher`,
  samt integritetspolicyns avsnitt om personuppgiftsansvarig). Ska tillbaka om
  och när aktiebolaget registreras — sök på `Svea Digital` och lägg till `AB` på
  copyrightraden, i JSON-LD och i integritetspolicyn.
- **Telefonnummer tillagt.** `073 649 18 52` / `tel:+46736491852` i footern
  (alla sidor), i kontaktsektionen på startsidan och som `"telephone"` i
  startsidans JSON-LD (`Organization` + `ProfessionalService`).

## CSS som blev oanvänd

`style.css` avsnitt **8. PORTFOLIO & KUNDCASE** (rad ~595–705) samt reglerna för
`.stat-grid`, `.rating-slot`, `.review-card`, `.logo-row`, `.placeholder-tag` och
`.placeholder-note` används inte av någon publicerad sida just nu. De är
medvetet kvar orörda så att återställning bara handlar om HTML.
