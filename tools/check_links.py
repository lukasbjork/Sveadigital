# -*- coding: utf-8 -*-
"""Länkkontroll för sveadigital.se.

Går igenom varje publicerad HTML-sida (allt utom mappar som börjar med _ eller .),
följer alla interna href/src och kontrollerar att målet finns. Efterliknar
GitHub Pages URL-hantering: /sida -> sida.html, /mapp/ -> mapp/index.html.

Kör:  python tools/check_links.py   (från reporoten)
"""
from __future__ import print_function

import io
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

ATTR_RE = re.compile(r'(?:href|src|srcset)\s*=\s*"([^"]+)"', re.I)
ID_RE = re.compile(r'\bid\s*=\s*"([^"]+)"')
EXTERNAL = ("http://", "https://", "mailto:", "tel:", "data:", "javascript:")

# Platshållare och strängar som inte får finnas kvar på en publicerad sida
FORBIDDEN = [
    "[ORG.NR]",
    "[TELEFONNUMMER]",
    "[TELEFONNUMMER — fyll i eller ta bort raden]",
    "Svea Digital AB",
    "Org.nr",
]


def published_files():
    """Alla filer som faktiskt hamnar på sajten."""
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if not d.startswith((".", "_"))]
        for name in filenames:
            yield os.path.join(dirpath, name)


def rel(path):
    return os.path.relpath(path, ROOT).replace("\\", "/")


existing = set(rel(p) for p in published_files())
pages = sorted(p for p in existing if p.endswith(".html"))

# Samla id:n per sida för ankarkontroll
ids = {}
text = {}
for page in pages:
    with io.open(os.path.join(ROOT, page), encoding="utf-8") as fh:
        body = fh.read()
    text[page] = body
    ids[page] = set(ID_RE.findall(body))


def resolve(target, from_page):
    """URL -> kandidatsökvägar i repot, i den ordning GitHub Pages provar dem."""
    if target.startswith("/"):
        base = target.lstrip("/")
    else:
        base = os.path.normpath(
            os.path.join(os.path.dirname(from_page), target)
        ).replace("\\", "/")
        if base == ".":
            base = ""

    if base == "" or base.endswith("/"):
        return [(base + "index.html").lstrip("/")]
    return [base, base + ".html", base + "/index.html"]


broken = []
anchors = []
placeholders = []

for page in pages:
    body = text[page]

    for bad in FORBIDDEN:
        if bad in body:
            placeholders.append((page, bad))

    for raw in ATTR_RE.findall(body):
        target = raw.strip()
        if not target or target.startswith(EXTERNAL) or target.startswith("#"):
            # ankare på samma sida
            if target.startswith("#") and len(target) > 1:
                if target[1:] not in ids[page]:
                    anchors.append((page, target))
            continue

        path_part, _, frag = target.partition("#")
        if not path_part:
            continue

        candidates = resolve(path_part, page)
        hit = next((c for c in candidates if c in existing), None)
        if hit is None:
            broken.append((page, target))
        elif frag and hit.endswith(".html") and frag not in ids.get(hit, set()):
            anchors.append((page, target))

print("Kontrollerade %d publicerade sidor, %d filer totalt.\n" % (len(pages), len(existing)))

fail = False

if broken:
    fail = True
    print("TRASIGA LANKAR (%d):" % len(broken))
    for page, target in broken:
        print("  %s -> %s" % (page, target))
else:
    print("OK  Inga trasiga interna lankar.")

if anchors:
    fail = True
    print("\nSAKNADE ANKARE (%d):" % len(anchors))
    for page, target in anchors:
        print("  %s -> %s" % (page, target))
else:
    print("OK  Alla #ankare pekar pa ett id som finns.")

if placeholders:
    fail = True
    print("\nPLATSHALLARE KVAR (%d):" % len(placeholders))
    for page, bad in placeholders:
        print("  %s innehaller %r" % (page, bad))
else:
    print("OK  Inga platshallare kvar (org.nr, telefon, 'AB').")

sys.exit(1 if fail else 0)
