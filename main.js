/* =============================================================
   SVEA DIGITAL — delad klientlogik
   Laddas med defer på alla sidor. Ingen sida är beroende av att
   skriptet körs: allt här är progressiv förbättring.
   ============================================================= */
(function () {
  'use strict';

  var reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* ---------- Mobilmeny ---------- */
  var burger = document.querySelector('.hamburger');
  var menu = document.getElementById('mobileMenu');

  if (burger && menu) {
    var setMenu = function (open) {
      menu.classList.toggle('open', open);
      burger.setAttribute('aria-expanded', String(open));
      burger.setAttribute('aria-label', open ? 'Stäng meny' : 'Öppna meny');
    };

    burger.addEventListener('click', function () {
      setMenu(burger.getAttribute('aria-expanded') !== 'true');
    });

    // Stäng när en länk valts
    menu.addEventListener('click', function (e) {
      if (e.target.closest('a')) setMenu(false);
    });

    // Esc stänger och lämnar tillbaka fokus till knappen
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && burger.getAttribute('aria-expanded') === 'true') {
        setMenu(false);
        burger.focus();
      }
    });

    // Klick utanför stänger
    document.addEventListener('click', function (e) {
      if (burger.getAttribute('aria-expanded') !== 'true') return;
      if (!e.target.closest('.nav')) setMenu(false);
    });
  }

  /* ---------- Markera aktuell sida i menyn ---------- */
  var here = window.location.pathname.replace(/\/index\.html$/, '/').replace(/\.html$/, '');
  if (here.length > 1) here = here.replace(/\/$/, '');

  document.querySelectorAll('.nav-links a, .mobile-menu a').forEach(function (a) {
    var href = a.getAttribute('href');
    if (!href || href.charAt(0) !== '/') return;
    var path = href.split('#')[0].replace(/\/index\.html$/, '/').replace(/\.html$/, '');
    if (path.length > 1) path = path.replace(/\/$/, '');
    if (path === here && !a.classList.contains('btn')) {
      a.setAttribute('aria-current', 'page');
    }
  });

  /* ---------- Scroll-in-animationer ----------
     Medvetet INTE IntersectionObserver: vid snabb scroll hinner element
     passera mellan två mätningar och blir då aldrig synliga igen. Här
     räknas i stället alla element som ännu inte visats om vid varje scroll,
     vilket gör att ingenting kan bli kvar dolt. */
  var pending = [].slice.call(document.querySelectorAll('.reveal'));

  if (pending.length) {
    if (reduceMotion) {
      pending.forEach(function (el) { el.classList.add('is-visible'); });
      pending = [];
    } else {
      var ticking = false;

      var revealVisible = function () {
        ticking = false;
        var limit = window.innerHeight * 0.9;
        var rest = [];
        for (var i = 0; i < pending.length; i++) {
          var el = pending[i];
          // Synligt om elementet nått in i vyn — eller redan passerats
          if (el.getBoundingClientRect().top < limit) el.classList.add('is-visible');
          else rest.push(el);
        }
        pending = rest;
        if (!pending.length) {
          window.removeEventListener('scroll', onScroll);
          window.removeEventListener('resize', onScroll);
        }
      };

      var onScroll = function () {
        if (ticking) return;
        ticking = true;
        window.requestAnimationFrame(revealVisible);
      };

      window.addEventListener('scroll', onScroll, { passive: true });
      window.addEventListener('resize', onScroll, { passive: true });
      revealVisible();
      // Bilder som laddas in kan flytta innehåll — mät om när sidan är klar
      window.addEventListener('load', onScroll);
    }
  }

  /* ---------- Sticky mobil-CTA ---------- */
  var sticky = document.getElementById('stickyCta');
  if (sticky) {
    var trigger = document.querySelector('.hero, .case-hero, .page-hero');
    var showAfter = trigger ? trigger.offsetHeight * 0.7 : 500;
    var contact = document.getElementById('kontakt');

    var updateSticky = function () {
      // Göm när kontaktsektionen syns — knappen skulle bara vara i vägen där
      var atContact = false;
      if (contact) {
        var r = contact.getBoundingClientRect();
        atContact = r.top < window.innerHeight && r.bottom > 0;
      }
      sticky.classList.toggle('is-visible', window.scrollY > showAfter && !atContact);
    };

    window.addEventListener('scroll', updateSticky, { passive: true });
    window.addEventListener('resize', updateSticky, { passive: true });
    updateSticky();
  }

  /* ---------- Scrolldjup till statistiken ---------- */
  (function () {
    var fired = false;
    window.addEventListener('scroll', function () {
      if (fired) return;
      var pos = (window.scrollY + window.innerHeight) / document.documentElement.scrollHeight;
      if (pos >= 0.9) {
        fired = true;
        if (window.umami) { try { window.umami.track('scroll-botten'); } catch (e) {} }
      }
    }, { passive: true });
  })();

  /* ---------- Formulär ---------- */
  document.querySelectorAll('form input[name="access_key"]').forEach(function (key) {
    var form = key.form;
    if (!form) return;

    var button = form.querySelector('button[type="submit"]');
    var status = form.querySelector('.form-status--error');
    var original = button ? button.textContent : '';
    var event = form.getAttribute('data-umami-event') || 'lead-formular';

    var showError = function (msg) {
      if (!status) { window.alert(msg); return; }
      status.textContent = msg;
      status.classList.remove('hidden');
    };

    var clearError = function () {
      if (status) status.classList.add('hidden');
    };

    // Ta bort felmarkering så fort användaren rättar sig
    form.addEventListener('input', function (e) {
      if (e.target.getAttribute('aria-invalid') === 'true' && e.target.checkValidity()) {
        e.target.removeAttribute('aria-invalid');
      }
    });

    form.addEventListener('submit', function (e) {
      e.preventDefault();
      clearError();

      // Egen validering (formulären har novalidate för att slippa webbläsarbubblor)
      var invalid = null;
      form.querySelectorAll('input, textarea, select').forEach(function (field) {
        if (field.name === 'botcheck') return;
        if (field.checkValidity()) {
          field.removeAttribute('aria-invalid');
        } else {
          field.setAttribute('aria-invalid', 'true');
          if (!invalid) invalid = field;
        }
      });

      if (invalid) {
        showError('Kontrollera de markerade fälten så skickar vi iväg din förfrågan.');
        invalid.focus();
        return;
      }

      // Honeypot: fylls bara i av robotar
      var honey = form.querySelector('[name="botcheck"]');
      if (honey && honey.value) return;

      if (button) {
        button.disabled = true;
        button.textContent = 'Skickar...';
      }

      var payload = {};
      new FormData(form).forEach(function (value, name) { payload[name] = value; });

      fetch('https://api.web3forms.com/submit', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
        body: JSON.stringify(payload)
      })
        .then(function (res) { return res.json(); })
        .then(function (data) {
          if (!data.success) throw new Error(data.message || 'Okänt fel');
          if (window.umami) { try { window.umami.track(event); } catch (err) {} }
          window.location.href = '/tack';
        })
        .catch(function () {
          if (button) {
            button.disabled = false;
            button.textContent = original;
          }
          showError('Något gick fel när formuläret skulle skickas. Mejla oss gärna direkt på kontakt@sveadigital.se så hör vi av oss.');
        });
    });
  });
})();
