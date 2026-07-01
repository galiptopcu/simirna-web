# -*- coding: utf-8 -*-
"""
One-off converter: splits the single-file fake-SPA `simirna-website6.html`
into 22 real, bilingual static pages (11 Turkish at site root, 11 English
under /en/), each with its own URL, <title>/description and hreflang tags.

Run once: python convert.py
"""
import copy
import html
import re
from pathlib import Path

from bs4 import BeautifulSoup, NavigableString, Comment

from translations import TRANSLATIONS

ROOT = Path(__file__).parent
SRC = ROOT / 'çalışmalarım' / 'simirna-website6.html'

# Placeholder domain — update once the final domain is chosen.
SITE_URL = 'https://www.simirna.com'

PAGE_FILES = {
    'home':        {'tr': 'index.html',       'en': 'index.html'},
    'simipayment': {'tr': 'simipayment.html', 'en': 'simipayment.html'},
    'simipos':     {'tr': 'simipos.html',     'en': 'simipos.html'},
    'simicard':    {'tr': 'simicard.html',    'en': 'simicard.html'},
    'kampuskart':  {'tr': 'kampuskart.html',  'en': 'campuscard.html'},
    'yemekkarti':  {'tr': 'yemekkarti.html',  'en': 'mealcard.html'},
    'sadakatkart': {'tr': 'sadakatkart.html', 'en': 'loyaltycard.html'},
    'hedijekarti': {'tr': 'hedijekarti.html', 'en': 'giftcard.html'},
    'hakkimizda':  {'tr': 'hakkimizda.html',  'en': 'about.html'},
    'referanslar': {'tr': 'referanslar.html', 'en': 'references.html'},
    'contact':     {'tr': 'contact.html',     'en': 'contact.html'},
}
PAGE_ORDER = list(PAGE_FILES.keys())

SEO = {
    'home': {
        'tr': ('Simirna – Ödeme Teknolojileri ve Kapalı Devre Ödeme Çözümleri',
               'Kart üretiminden ödeme çözümüne uçtan uca kapalı devre ödeme sistemi. '
               'simiPayment, simiPOS ve simiCard ile işletmenize özel ödeme altyapısı kurun.'),
        'en': ('Simirna – Payment Technologies & Closed-Loop Payment Solutions',
               'An end-to-end closed-loop payment system from card production to payment '
               'solutions. Build your own payment infrastructure with simiPayment, simiPOS '
               'and simiCard.'),
    },
    'simipayment': {
        'tr': ("simiPayment – Uçtan Uca Kapalı Devre Ödeme Çözümü | Simirna",
               'simiPayment ile markanıza özel kapalı devre ödeme altyapısı kurun: kart '
               'yönetimi, üye iş yeri ağı ve gerçek zamanlı işlem takibi tek platformda.'),
        'en': ('simiPayment – End-to-End Closed-Loop Payment Solution | Simirna',
               'Build your own closed-loop payment infrastructure with simiPayment: card '
               'management, merchant network and real-time transaction tracking on a '
               'single platform.'),
    },
    'simipos': {
        'tr': ("simiPOS – POS ve ÖKC Uygulama Geliştirme Framework'ü | Simirna",
               'simiPOS ile POS ve ÖKC cihazları için hızlı, güvenli ve ölçeklenebilir '
               'ödeme uygulamaları geliştirin.'),
        'en': ('simiPOS – POS & ÖKC Application Development Framework | Simirna',
               'Develop fast, secure and scalable payment applications for POS and ÖKC '
               'devices with simiPOS.'),
    },
    'simicard': {
        'tr': ('simiCard – Çip Personalizasyon ve Kart Üretim Uygulaması | Simirna',
               'simiCard ile çip kart personalizasyonundan üretim süreçlerine kadar tüm '
               'kart yaşam döngüsünü yönetin.'),
        'en': ('simiCard – Chip Personalization & Card Production Application | Simirna',
               'Manage the entire card lifecycle with simiCard, from chip card '
               'personalization to production processes.'),
    },
    'kampuskart': {
        'tr': ('Kampüs Kart – Üniversiteler için Kapalı Devre Ödeme Çözümü | Simirna',
               'Kampüs Kart ile üniversite ve kampüslerde yemekhane, kütüphane, kırtasiye '
               'gibi tüm hizmetleri tek kart üzerinden yönetin.'),
        'en': ('Campus Card – Closed-Loop Payment Solution for Universities | Simirna',
               'Manage all campus services — dining halls, libraries, stationery and more '
               '— through a single card with Campus Card.'),
    },
    'yemekkarti': {
        'tr': ('Yemek Kartı – Yemek Kartı Şirketleri için Uçtan Uca Altyapı | Simirna',
               'Yemek kartı şirketleri için kart üretiminden üye iş yeri ağı yönetimine '
               'kadar uçtan uca altyapı çözümleri.'),
        'en': ('Meal Card – End-to-End Infrastructure for Meal Card Companies | Simirna',
               'End-to-end infrastructure for meal card companies, from card production '
               'to merchant network management.'),
    },
    'sadakatkart': {
        'tr': ('Sadakat Kartı – Sadakat Programı ve Ödeme Entegrasyonu | Simirna',
               'Sadakat Kartı çözümümüzle müşteri sadakatini artırın; puan kazanma, ödeme '
               've kampanya yönetimini tek platformda birleştirin.'),
        'en': ('Loyalty Card – Loyalty Program & Payment Integration | Simirna',
               'Boost customer loyalty with our Loyalty Card solution — combine points, '
               'payments and campaign management on a single platform.'),
    },
    'hedijekarti': {
        'tr': ('Hediye Kartı – Markanıza Özel Hediye Kartı Programı | Simirna',
               'Markanıza özel fiziksel ve dijital hediye kartı programları ile '
               'müşterilerinize yeni bir deneyim sunun.'),
        'en': ('Gift Card – Branded Physical & Digital Gift Card Programs | Simirna',
               'Offer your customers a new experience with branded physical and digital '
               'gift card programs.'),
    },
    'hakkimizda': {
        'tr': ('Hakkımızda – 20+ Yıllık Deneyim ve Vizyonumuz | Simirna',
               "Simirna olarak 20 yılı aşkın deneyimimizle Türkiye'nin ödeme teknolojileri "
               'alanındaki güvenilir çözüm ortağıyız. Hikayemizi ve vizyonumuzu keşfedin.'),
        'en': ('About Us – 20+ Years of Experience & Our Vision | Simirna',
               "With over 20 years of experience, Simirna is Turkey's trusted solution "
               'partner in payment technologies. Discover our story and vision.'),
    },
    'referanslar': {
        'tr': ('Referanslar – Başarılı Projeler ve İş Ortaklarımız | Simirna',
               'TokenFlex, iWallet, Multinet Up, Sodexo ve Verifone gibi sektör lideri '
               'firmalarla gerçekleştirdiğimiz başarılı projeleri keşfedin.'),
        'en': ('References – Successful Projects & Business Partners | Simirna',
               "Discover the successful projects we've delivered with industry leaders "
               'like TokenFlex, iWallet, Multinet Up, Sodexo and Verifone.'),
    },
    'contact': {
        'tr': ('İletişim – Bizimle İletişime Geçin | Simirna',
               'Ödeme teknolojileri alanındaki ihtiyaçlarınızı konuşmak için formu '
               'doldurun. Uzman ekibimiz en kısa sürede size dönecektir.'),
        'en': ('Contact – Get in Touch With Us | Simirna',
               'Fill in the form to discuss your payment technology needs. Our expert '
               'team will get back to you as soon as possible.'),
    },
}

SHOWPAGE_RE = re.compile(r"showPage\('(\w+)'\)")

HEAD_TEMPLATE = """<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<meta name="description" content="{description}">
<link rel="canonical" href="{canonical}">
<link rel="alternate" hreflang="tr" href="{href_tr}">
<link rel="alternate" hreflang="en" href="{href_en}">
<link rel="alternate" hreflang="x-default" href="{href_tr}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:ital,wght@0,400;0,500;0,600;0,700;0,800;1,400&family=Inter:wght@300;400;500;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{prefix}css/styles.css">"""

DOC_TEMPLATE = """<!DOCTYPE html>
<html lang="{lang}" id="html-root">
<head>
{head}
</head>
<body>
{nav}

{mobile_menu}

{content}

{footer}
<script src="{prefix}js/main.js"></script>
</body>
</html>
"""

MAIN_JS = """/* ── FAQ accordion ── */
function toggleFaq(el) {
  const item = el.closest('.faq-item');
  const isOpen = item.classList.contains('open');
  document.querySelectorAll('.faq-item.open').forEach(i => i.classList.remove('open'));
  if (!isOpen) item.classList.add('open');
}

/* ── Scroll-reveal animations ── */
function initFadeUps() {
  const obs = new IntersectionObserver((entries) => {
    entries.forEach(e => { if (e.isIntersecting) e.target.classList.add('visible'); });
  }, { threshold: 0.1 });
  document.querySelectorAll('.fade-up:not(.visible)').forEach(el => obs.observe(el));
}
initFadeUps();

/* ── Navbar scroll shadow ── */
window.addEventListener('scroll', () => {
  const nb = document.getElementById('navbar');
  if (nb) nb.classList.toggle('scrolled', window.scrollY > 40);
});

/* ── Mobile menu ── */
function toggleMobileMenu() {
  const burger = document.getElementById('navBurger');
  const menu = document.getElementById('mobileMenu');
  if (!burger || !menu) return;
  const isOpen = menu.classList.toggle('open');
  burger.classList.toggle('open', isOpen);
  burger.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
  document.body.style.overflow = isOpen ? 'hidden' : '';
}
function closeMobileMenu() {
  const burger = document.getElementById('navBurger');
  const menu = document.getElementById('mobileMenu');
  if (!burger || !menu || !menu.classList.contains('open')) return;
  menu.classList.remove('open');
  burger.classList.remove('open');
  burger.setAttribute('aria-expanded', 'false');
  document.body.style.overflow = '';
}
"""


def page_url(page_id, lang):
    base = SITE_URL if lang == 'tr' else f'{SITE_URL}/en'
    return f'{base}/' if page_id == 'home' else f'{base}/{PAGE_FILES[page_id][lang]}'


def asset_prefix(lang):
    return '../' if lang == 'en' else ''


# ── i18n transforms (mirrors the old applyLang() logic, but baked at build time) ──

def apply_lang_to_tag(tag, lang):
    for el in tag.find_all(attrs={'data-tr': True}):
        val = el.get('data-' + lang)
        if not val:
            continue
        name = el.name
        classes = el.get('class') or []
        if name in ('input', 'textarea'):
            el['placeholder'] = val
        elif name in ('button', 'option'):
            el.string = val
        elif name == 'span' and 'nav-link' in classes and el.find('svg'):
            svg = el.find('svg')
            for node in list(el.contents):
                if isinstance(node, NavigableString):
                    node.extract()
            svg.insert_before(val + ' ')
        else:
            fragment = BeautifulSoup(val, 'html.parser')
            el.clear()
            for child in list(fragment.contents):
                el.append(child)

    for el in tag.find_all(attrs={'data-placeholder-' + lang: True}):
        el['placeholder'] = el['data-placeholder-' + lang]


def translate_text_nodes(tag):
    """Fill in the ~297 plain-text gaps that never had data-tr/data-en pairs."""
    for node in list(tag.find_all(string=True)):
        if isinstance(node, Comment) or not isinstance(node, NavigableString):
            continue
        text = str(node)
        stripped = text.strip()
        if not stripped or stripped not in TRANSLATIONS:
            continue
        lstripped = text.lstrip()
        rstripped = text.rstrip()
        leading = text[:len(text) - len(lstripped)]
        trailing = text[len(rstripped):]
        node.replace_with(leading + TRANSLATIONS[stripped] + trailing)


def strip_i18n_attrs(tag):
    for el in tag.find_all(True):
        for attr in ('data-tr', 'data-en', 'data-placeholder-tr', 'data-placeholder-en'):
            if el.has_attr(attr):
                del el[attr]


def convert_showpage_links(tag, lang):
    for el in tag.find_all(attrs={'onclick': SHOWPAGE_RE}):
        target = SHOWPAGE_RE.search(el['onclick']).group(1)
        del el['onclick']
        el['href'] = PAGE_FILES[target][lang]
        if el.name != 'a':
            el.name = 'a'


def convert_lang_switcher(tag, lang, page_id):
    tr_fname = PAGE_FILES[page_id]['tr']
    en_fname = PAGE_FILES[page_id]['en']
    tr_href = tr_fname if lang == 'tr' else f'../{tr_fname}'
    en_href = f'en/{en_fname}' if lang == 'tr' else en_fname
    for el in tag.find_all(class_='lang-btn'):
        target_lang = el.get('data-lang')
        if el.has_attr('onclick'):
            del el['onclick']
        el['href'] = tr_href if target_lang == 'tr' else en_href
        if el.name != 'a':
            el.name = 'a'
        classes = [c for c in el.get('class', []) if c != 'active']
        if target_lang == lang:
            classes.append('active')
        el['class'] = classes


def fix_asset_paths(tag, lang):
    if lang != 'en':
        return
    for img in tag.find_all('img', src=True):
        if img['src'].startswith('images/'):
            img['src'] = '../' + img['src']


def process_fragment(tag, lang, page_id):
    apply_lang_to_tag(tag, lang)
    if lang == 'en':
        translate_text_nodes(tag)
    convert_showpage_links(tag, lang)
    convert_lang_switcher(tag, lang, page_id)
    fix_asset_paths(tag, lang)
    strip_i18n_attrs(tag)


def main():
    source_html = SRC.read_text(encoding='utf-8')
    soup = BeautifulSoup(source_html, 'html.parser')

    style_tag = soup.find('style')
    css_content = style_tag.get_text()

    nav_tag = soup.find('nav', id='navbar')
    mobile_menu_tag = soup.find('div', id='mobileMenu')
    footer_tag = soup.find('footer')

    page_divs = {pid: soup.find('div', id=f'page-{pid}') for pid in PAGE_ORDER}
    missing = [pid for pid, div in page_divs.items() if div is None]
    if missing:
        raise SystemExit(f'Could not locate page divs for: {missing}')

    # ── shared assets ──
    (ROOT / 'css').mkdir(exist_ok=True)
    (ROOT / 'js').mkdir(exist_ok=True)
    (ROOT / 'en').mkdir(exist_ok=True)
    (ROOT / 'css' / 'styles.css').write_text(css_content.strip() + '\n', encoding='utf-8')
    (ROOT / 'js' / 'main.js').write_text(MAIN_JS, encoding='utf-8')

    written = []
    for page_id in PAGE_ORDER:
        for lang in ('tr', 'en'):
            nav_copy = copy.deepcopy(nav_tag)
            mm_copy = copy.deepcopy(mobile_menu_tag)
            content_copy = copy.deepcopy(page_divs[page_id])
            footer_copy = copy.deepcopy(footer_tag)

            for frag in (nav_copy, mm_copy, content_copy, footer_copy):
                process_fragment(frag, lang, page_id)

            classes = content_copy.get('class', [])
            if 'active' not in classes:
                classes.append('active')
            content_copy['class'] = classes

            seo_title, seo_desc = SEO[page_id][lang]
            head = HEAD_TEMPLATE.format(
                title=html.escape(seo_title),
                description=html.escape(seo_desc),
                canonical=page_url(page_id, lang),
                href_tr=page_url(page_id, 'tr'),
                href_en=page_url(page_id, 'en'),
                prefix=asset_prefix(lang),
            )
            doc = DOC_TEMPLATE.format(
                lang=lang,
                head=head,
                nav=str(nav_copy),
                mobile_menu=str(mm_copy),
                content=str(content_copy),
                footer=str(footer_copy),
                prefix=asset_prefix(lang),
            )

            out_dir = ROOT if lang == 'tr' else ROOT / 'en'
            out_path = out_dir / PAGE_FILES[page_id][lang]
            out_path.write_text(doc, encoding='utf-8')
            written.append(out_path)

    print(f'Wrote {len(written)} HTML files plus css/styles.css and js/main.js')

    # ── self-checks ──
    problems = []
    for path in written:
        text = path.read_text(encoding='utf-8')
        if 'showPage(' in text:
            problems.append(f'{path}: leftover showPage(...) reference')
        if re.search(r'data-(tr|en|placeholder-tr|placeholder-en)=', text):
            problems.append(f'{path}: leftover data-tr/data-en/data-placeholder attribute')
        for m in re.finditer(r'(?:href|src)="([^"#][^"]*)"', text):
            target = m.group(1)
            if target.startswith(('http://', 'https://', 'mailto:', 'tel:')):
                continue
            resolved = (path.parent / target).resolve()
            if not resolved.exists():
                problems.append(f'{path}: missing target {target!r} -> {resolved}')

    if problems:
        print(f'\n{len(problems)} problem(s) found:')
        for p in problems:
            print('  -', p)
    else:
        print('Self-check passed: no showPage(), no leftover data-tr/data-en, all link/asset targets exist.')


if __name__ == '__main__':
    main()
