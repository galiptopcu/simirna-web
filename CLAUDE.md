# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A static marketing website for **Simirna**, a Turkish B2B payment-technology company. It is plain HTML/CSS/JS — no build tools, no framework, no package manager, no backend. The output is meant to be deployed by drag-and-drop to a static host (Netlify, Vercel, Cloudflare Pages, GitHub Pages, etc.).

## Running / previewing locally

There is no build step. To preview the site, serve the directory root with any static file server, e.g.:

```
python -m http.server 8000
```

then open `http://localhost:8000/index.html`. Opening the HTML files directly via `file://` also works since all asset paths are relative.

## Architecture — bilingual subdirectory i18n (TR root + /en/)

The site uses Google's recommended subdirectory pattern for international SEO: **two parallel page trees**, not client-side language switching.

```
simirnaweb/
├── index.html, simipayment.html, simipos.html, simicard.html,   ← Turkish pages (site root)
│   kampuskart.html, yemekkarti.html, sadakatkart.html,
│   hedijekarti.html, hakkimizda.html, referanslar.html, contact.html
├── en/                                                            ← English mirror, identical filenames
│   ├── index.html, simipayment.html, ...
├── css/styles.css   ← single shared stylesheet for both languages
├── js/main.js       ← single shared script for both languages
└── images/          ← hero.jpg, referanslar/*.png (shared)
```

Key points for editing:
- Each page is a **fully independent HTML document** with its own `<title>`, meta description, `<link rel="canonical">`, and three `<link rel="alternate" hreflang="…">` tags (`tr`, `en`, `x-default`). There is **no runtime language switching JS** — the `EN`/`TR` buttons in the nav (`.lang-btn`) are plain `<a href>` links to the sibling page in the other tree.
- Asset references use relative paths: root pages use `css/styles.css`, `js/main.js`, `images/...`; pages under `en/` use `../css/styles.css`, `../js/main.js`, `../images/...`. Keep this `../` prefix convention whenever adding new shared assets or pages.
- Internal navigation between pages is plain `<a href="pagename.html">` — both language trees use the **same filenames**, so cross-references within one language never need a `../` prefix, only language-switch links do.
- The shared `<nav>`, `<div class="mobile-menu">` panel, and `<footer>` blocks should stay structurally identical across all 22 pages (only `href` targets and language differ). If you change the nav/footer markup, change it consistently in every page — there is no templating/include mechanism.
- `SITE_URL` (currently a placeholder `https://www.simirna.com`) appears in canonical/hreflang `<link>` tags on every page — update it everywhere once a real domain is chosen.

## CSS conventions (css/styles.css)

- CSS custom properties (`--blue-deep`, `--accent`, `--radius`, `--nav-h`, etc.) defined in `:root` drive the color/spacing system — reuse these rather than hardcoding values.
- Breakpoints: `@media (max-width: 900px)` (tablet — switches nav to hamburger menu) and `@media (max-width: 600px)` (phone — tighter grids/typography). When adding responsive rules, place them in the matching existing media-query block rather than creating new ones.
- Class-based selectors are used throughout (not tag-qualified, e.g. `.lang-btn` not `span.lang-btn`) so that elements can be `<a>`, `<span>`, `<div>` or `<button>` interchangeably without losing styles. Follow this pattern — avoid adding tag-qualified selectors like `div.foo`.
- Any element that becomes a real `<a href>` link needs `text-decoration: none` in its class rule (the browser default underlines `:any-link`).

## JS conventions (js/main.js)

Small, dependency-free vanilla JS, four independent pieces: `toggleFaq` (accordion), `initFadeUps` (IntersectionObserver-based scroll-reveal via `.fade-up`/`.visible`), navbar scroll-shadow listener, and `toggleMobileMenu`/`closeMobileMenu` (hamburger panel). There is no router and no i18n logic — each page is its own document.

## One-off conversion tooling (not part of the deployed site)

`convert.py` and `translations.py` (plus `translations_needed.json`) are **build-time helper scripts**, not deployed assets — do not include them when publishing the site. They were used once to generate the 22-page bilingual structure from a legacy single-file "fake SPA" (`çalışmalarım/simirna-website6.html`, kept for reference/history). If the legacy file is ever edited and the site needs regenerating:

```
python convert.py
```

`convert.py` re-derives all 22 pages from the legacy source: it extracts the shared `<nav>`/mobile-menu/`<footer>`/`<style>` blocks and the 11 `<div id="page-XXX">` content fragments, applies the `data-tr`/`data-en` attribute pairs (mirroring the legacy `applyLang()` logic) for the appropriate language, fills in remaining plain-text translation gaps via the `TRANSLATIONS` dict in `translations.py`, rewrites `onclick="showPage('id')"` calls into real `<a href>` links, and injects the per-page SEO/hreflang `<head>` content from the `SEO` table inside the script. It also self-checks its own output (no leftover `showPage(`/`data-tr`/`data-en`, every `href`/`src` target exists on disk) and prints a pass/fail report.

`translations.py` holds the `TRANSLATIONS` dict — Turkish→English string pairs for body text that has no `data-tr`/`data-en` attributes in the legacy source. If you find untranslated Turkish text on an English page, add the exact string (with surrounding punctuation, matching whitespace trimmed) as a new key/value pair here and re-run `convert.py`.

`çalışmalarım/emailimza/` similarly holds the team's HTML email-signature file(s) — version-tracked for reference but **not part of the deployed site**. Skip the whole `çalışmalarım/` directory (along with `convert.py`/`translations.py`) when drag-and-dropping the site to a static host.
