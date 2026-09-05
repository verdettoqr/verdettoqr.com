"""Build the verdettoqr.com pages: one header, footer, and stylesheet, the
logo and card icons inlined as SVG symbols, so every page is self-contained:
no scripts run, nothing loads from another host. Run assets.py first, then
python build.py. Flip PUBLISH and DRAFT at publication."""
import html
import base64
import hashlib
import json
import re
from pathlib import Path

HERE = Path(__file__).parent
DRAFT = False       # True while drafting: shows the review banner
PUBLISH = True      # True at publication: clean URLs in links (GitHub Pages serves /privacy for privacy.html)
SITE = "https://verdettoqr.com"
PLAY_ID = "app.scanner.free"  # the app's applicationId (app/build.gradle.kts)


def play_link(source, medium="app", campaign=None):
    """The Play listing link with a referrer, so Play Console's acquisition report counts installs per channel without
    identifying anyone. The referrer reaches the installed app through the Install Referrer API; nothing else is sent.
    Channels the app itself uses: share (the share-the-app screen), card (the warning share card), developers (the
    fallback snippet on the developers page). Posts use utm_medium=post; the site's badge uses utm_medium=badge."""
    referrer = f"utm_source={source}&utm_medium={medium}&utm_campaign={campaign or source}"
    return f"https://play.google.com/store/apps/details?id={PLAY_ID}&referrer=" + referrer.replace("=", "%3D").replace("&", "%26")
DATE = "2026-09-04"  # lastmod for the sitemap and the article; update when copy changes
ADDRESS = "1520 Belle View Blvd, Suite #5992, Alexandria, VA 22307"
EMAIL = "support@verdettoqr.com"

svg = (HERE / "logo.svg").read_text(encoding="utf-8")
# the transparent mark (the splash mark, no mint disc): the qr and accent groups, filled with the text color of the ground
_groups = "".join(re.findall(r'<g id="(?:qr|accent)"[^>]*>.*?</g>', svg, re.S))
# the body takes the brand teal on light grounds and white on dark grounds (a CSS variable set per ground); the accent
# is always the signal amber, as on the splash; never the text color
mark_inner = _groups.replace('id="qr" fill="#003D35"', 'id="qr" fill="var(--mark-body,#003D35)"').replace('id="accent" fill="#B8650A"', 'id="accent" fill="var(--mark-accent,#B8650A)"')
assert 'var(--mark-body' in mark_inner and 'var(--mark-accent' in mark_inner, "mark fills not set"
assert mark_inner.count("<path") >= 30, "mark paths missing"
inner = svg[svg.index(">", svg.index("<svg")) + 1: svg.rindex("</svg>")]
inner = re.sub(r'<rect width="108" height="108" fill="#D5E8E3"/>', '<rect width="108" height="108" rx="24" fill="#D5E8E3"/>', inner)
inner = re.sub(r' id="(background|qr|accent)"', "", inner)

# Card icons: own 24-unit outlines, stroke-based, so no icon font or library is loaded.
ICONS = {
    "scan": '<path d="M4 8V5a1 1 0 0 1 1-1h3M16 4h3a1 1 0 0 1 1 1v3M20 16v3a1 1 0 0 1-1 1h-3M8 20H5a1 1 0 0 1-1-1v-3"/><path fill="currentColor" stroke="none" d="M9 9h2v2H9zM13 9h2v2h-2zM9 13h2v2H9zM13 13h2v2h-2z"/>',
    "eye": '<path d="M2 12s3.5-6 10-6 10 6 10 6-3.5 6-10 6S2 12 2 12z"/><circle cx="12" cy="12" r="3"/>',
    "warning": '<path d="M12 3l10 17H2z"/><path d="M12 9v5M12 17.2h.01"/>',
    "shield": '<path d="M12 3l7 3v5c0 5-3.5 8.5-7 10-3.5-1.5-7-5-7-10V6z"/><path d="M9 11h6M9 14h6"/>',
    "barcode": '<path fill="currentColor" stroke="none" d="M3 5h2v14H3zM7 5h1v14H7zM10 5h3v14h-3zM15 5h1v14h-1zM18 5h3v14h-3z"/>',
    "history": '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
    "offline": '<path d="M7 18h10a4 4 0 0 0 .5-8A6 6 0 0 0 6 11.5 3.5 3.5 0 0 0 7 18z"/><path d="M4 4l16 16"/>',
    "heart": '<path d="M12 20s-7-4.5-7-10a4 4 0 0 1 7-2.5A4 4 0 0 1 19 10c0 5.5-7 10-7 10z"/>',
    "clock": '<circle cx="12" cy="12" r="9"/><path d="M12 8v4l2.5 1.5"/>',
    "language": '<circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c2.8 2.6 4.2 5.6 4.2 9s-1.4 6.4-4.2 9c-2.8-2.6-4.2-5.6-4.2-9S9.2 5.6 12 3z"/>',
}
SYMBOLS = ('<svg width="0" height="0" style="position:absolute" aria-hidden="true">'
           f'<symbol id="logo" viewBox="0 0 108 108">{inner}</symbol>'
           + f'<symbol id="mark" viewBox="18 18 72 72">{mark_inner}</symbol>'
           + "".join(f'<symbol id="ic-{k}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">{v}</symbol>' for k, v in ICONS.items())
           + "</svg>")

CSS = """
/* Material 3 color roles, copied from the app's Theme.kt so the site and the app are one palette. */
:root{--mark-body:#003D35;--mark-accent:#B8650A;--surface:#E9F5F1;--on-surface:#191C1B;--on-surface-variant:#3F4946;--primary:#006B5E;--on-primary:#FFFFFF;--surface-container:#D5E8E3;--surface-container-high:#CFE2DC;--outline:#6F7977;--outline-variant:#B4CAC4;--tertiary:#8A5A00;--on-tertiary:#FFFFFF}
@media (prefers-color-scheme:dark){:root{--mark-body:#FFFFFF;--mark-accent:#FFB95A;--surface:#0F1312;--on-surface:#DFE4E1;--on-surface-variant:#BEC9C5;--primary:#54DBC8;--on-primary:#003731;--surface-container:#1C201F;--surface-container-high:#262B29;--outline:#899390;--outline-variant:#3F4946;--tertiary:#FFB95A;--on-tertiary:#462A00}}
/* M3 type scale (body-large 16/24, title-medium 16/24 500, title-large 22/28, headline-large 32/40, label-large 14/20 500),
   shape scale (chips 8, cards 12, large containers 16), tonal surfaces instead of shadows. Roboto is the app's face: the
   variable latin file under fonts/ (Apache 2.0, fonts/LICENSE.txt) serves every weight; the system stack stands in
   while it loads and for other scripts. */
@font-face{font-family:Roboto;font-style:normal;font-weight:100 900;font-display:swap;src:url(fonts/Roboto-latin.woff2) format("woff2");unicode-range:U+0000-00FF,U+0131,U+0152-0153,U+02BB-02BC,U+02C6,U+02DA,U+02DC,U+0304,U+0308,U+0329,U+2000-206F,U+20AC,U+2122,U+2191,U+2193,U+2212,U+2215,U+FEFF,U+FFFD}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--surface);color:var(--on-surface);font:16px/1.5 Roboto,system-ui,-apple-system,"Segoe UI",Helvetica,Arial,sans-serif}
a{color:var(--primary)}
:focus-visible{outline:2px solid var(--primary);outline-offset:2px;border-radius:4px}
.skip{position:absolute;inset-inline-start:0;top:0;transform:translateY(-150%);background:var(--primary);color:var(--on-primary);padding:.5rem 1rem;border-radius:0 0 8px 0;z-index:2}
.skip:focus{transform:none}
.wrap{max-width:44rem;margin:0 auto;padding:0 1rem}
.draft{background:var(--tertiary);color:var(--on-tertiary);text-align:center;padding:.4rem;font-size:.875rem;line-height:1.25rem;font-weight:500;letter-spacing:.01em}
header{border-bottom:1px solid var(--outline-variant)}
header .wrap{display:flex;align-items:center;gap:.75rem;min-height:64px;padding-top:.5rem;padding-bottom:.5rem;flex-wrap:wrap}
.brand{display:inline-flex;align-items:center;gap:.4rem;color:var(--on-surface);text-decoration:none;font-weight:500;font-size:1.375rem;line-height:1.75rem}
.brand svg{width:.78em;height:.78em;flex:none}
.lockup{white-space:nowrap}.lockup svg{width:.78em;height:.78em;vertical-align:-.04em;margin-inline-end:.3em}
nav{margin-left:auto;display:flex;gap:.25rem;flex-wrap:wrap}
nav a{color:var(--on-surface-variant);text-decoration:none;font-weight:500;font-size:.875rem;line-height:1.25rem;padding:.6rem .75rem;border-radius:20px}
nav a:hover{background:var(--surface-container)}
.lang{position:relative;margin-inline-start:.25rem}.lang summary{list-style:none;display:inline-flex;align-items:center;gap:.4rem;padding:.6rem .75rem;border-radius:20px;color:var(--on-surface-variant);font-weight:500;font-size:.875rem;line-height:1.25rem;cursor:pointer;position:relative}.lang summary::-webkit-details-marker{display:none}.lang summary::after{content:"";position:absolute;inset:-5px 0}.lang summary svg{width:20px;height:20px;fill:none;stroke:currentColor;stroke-width:1.8;stroke-linecap:round;stroke-linejoin:round}.lang summary:hover,.lang[open] summary{background:var(--surface-container)}.lang .menu{position:absolute;inset-inline-end:0;top:calc(100% + 4px);margin:0;padding:.5rem 0;list-style:none;min-width:12.5rem;background:var(--surface-container);border-radius:4px;box-shadow:0 1px 3px rgba(0,0,0,.3),0 4px 8px 3px rgba(0,0,0,.15);z-index:4}.lang .menu a{display:flex;align-items:center;min-height:48px;padding:0 .75rem;color:var(--on-surface);text-decoration:none;font-size:.875rem;line-height:1.25rem}.lang .menu a:hover{background:var(--surface-container-high)}.lang .menu a[aria-current]{color:var(--primary);font-weight:600}
nav a[aria-current]{color:var(--primary);background:var(--surface-container-high)}
main{padding:.5rem 0 2rem}
h1{color:var(--on-surface);font-size:2rem;line-height:2.5rem;font-weight:500;margin:1.5rem 0 .5rem}
h2{color:var(--primary);font-size:1.375rem;line-height:1.75rem;font-weight:500;margin:2rem 0 .5rem;padding-top:.75rem;border-top:1px solid var(--outline-variant)}
h3{font-size:1rem;line-height:1.5rem;font-weight:500;margin:1.25rem 0 .25rem}
p,li{margin:.5rem 0}
.meta{color:var(--on-surface-variant);font-size:.875rem;line-height:1.25rem}
.card{background:var(--surface-container);border-radius:12px;padding:1rem;margin:1rem 0}
.hero{display:grid;grid-template-columns:1fr auto;gap:2rem;align-items:center;padding:1.5rem 0 .5rem}
.hero .mark{width:64px;height:64px;display:block;margin-bottom:.5rem}
.hero h1{margin:.25rem 0 .5rem;font-size:2.25rem;line-height:2.75rem}
.hero p{font-size:1.125rem;line-height:1.75rem;margin:0}
.hero .label{display:inline-flex;align-items:center;gap:.4rem;margin-top:1rem;color:var(--on-surface-variant);font-weight:500;font-size:.875rem;line-height:1.25rem}
.hero .label svg{width:18px;height:18px}.hero .support{margin:.75rem 0 0;font-size:.9375rem;line-height:1.375rem;color:var(--on-surface-variant)}
.shot{width:250px;height:auto;border-radius:20px;border:1px solid var(--outline-variant);background:var(--surface-container);display:block}
.grid{display:grid;grid-template-columns:1fr;gap:1rem;margin:1.25rem 0;align-items:stretch}
.grid .card{margin:0;padding:1rem;background:var(--surface-container);border-radius:12px;display:grid;grid-template-columns:auto 1fr;gap:.75rem;align-items:start}
.grid .card svg{width:24px;height:24px;color:var(--primary);margin-top:.15rem}
.grid h3{margin:0 0 .25rem;color:var(--on-surface)}
.grid p{margin:0;font-size:.875rem;line-height:1.25rem;color:var(--on-surface-variant)}
.callout{background:var(--surface-container-high);border-left:4px solid var(--primary);border-radius:0 12px 12px 0;display:grid;grid-template-columns:1fr auto;gap:1rem;align-items:center}.callout .shot.small{width:120px;margin:0}nav a,.more summary{position:relative}nav a::after,.more summary::after{content:"";position:absolute;inset:-5px 0}
.faq p strong{color:var(--on-surface);font-weight:500}
.prose ol,.prose ul{padding-left:1.4rem}
.prose li{margin:.6rem 0}
table{border-collapse:collapse;width:100%;font-size:.875rem;line-height:1.25rem;display:block;overflow-x:auto;margin:1rem 0}
pre{background:var(--container);border-radius:.5rem;padding:.9rem 1rem;overflow-x:auto;font-size:.8125rem;line-height:1.35rem;margin:1rem 0}
code{font-family:Consolas,'Cascadia Mono',Menlo,monospace;font-size:.92em}
pre code{font-size:inherit}
th,td{text-align:left;vertical-align:top;padding:.5rem .6rem;border-bottom:1px solid var(--outline-variant)}
th{color:var(--on-surface-variant);font-weight:500;white-space:nowrap}
td:first-child{min-width:12rem}
p.langs{font-size:.8125rem;line-height:1.5;color:var(--on-surface-variant)}p.langs a[aria-current]{font-weight:600;text-decoration:none}
details.more{margin:1rem 0}details.more summary{cursor:pointer;color:var(--primary);font-weight:500;font-size:.875rem;line-height:1.25rem;padding:.6rem .75rem;border-radius:20px;display:inline-block;background:var(--surface-container)}details.more[open] summary{margin-bottom:.5rem}
footer{background:var(--surface-container);margin-top:2rem}
footer .wrap{padding:1.5rem 1rem 2rem;color:var(--on-surface-variant);font-size:.875rem;line-height:1.25rem}
footer a{color:var(--primary)}
@media (min-width:640px){.grid{grid-template-columns:1fr 1fr}.grid.three{grid-template-columns:repeat(3,1fr)}}
@media (max-width:600px){.hero{grid-template-columns:1fr}.shot{width:220px;margin:0 auto}h1,.hero h1{font-size:1.75rem;line-height:2.25rem}nav{margin-left:0;width:100%;order:3}.lang{margin-inline-start:auto;order:2}.callout{grid-template-columns:1fr}.callout .shot.small{margin:0 auto}}
@media print{.draft,.skip,nav,footer .links{display:none}body{background:#fff;color:#000;font-size:12pt}a{color:#000}h2{color:#000;border-top-color:#999}.card,.callout{background:#f2f2f2}}
"""


def href(name):
    if not PUBLISH:
        return name
    return "/" if name == "index.html" else "/" + name[:-5]


def url(name):
    return SITE + ("/" if name == "index.html" else "/" + name[:-5])


NAV = [("support.html", "Help"), ("check-qr-code-link.html", "Guide"), ("support-the-work.html", "Support the work")]
SPONSORS_LIVE = False  # True once the GitHub Sponsors profile is approved; the support page then links it

SOCIAL = {"Mastodon": "https://mastodon.social/@VerdettoQR", "Reddit": "https://www.reddit.com/user/VerdettoQR/", "GitHub": "https://github.com/verdettoqr"}
SOCIAL_LINKS = " &middot; ".join(f'<a href="{v}" rel="me">{k}</a>' for k, v in SOCIAL.items())
ORG = {"@type": "Organization", "name": "Verdetto", "url": SITE + "/", "email": EMAIL, "logo": SITE + "/icon-512.png",
       "sameAs": list(SOCIAL.values()),
       "address": {"@type": "PostalAddress", "streetAddress": "1520 Belle View Blvd, Suite #5992", "addressLocality": "Alexandria",
                   "addressRegion": "VA", "postalCode": "22307", "addressCountry": "US"}}
APP = {"@type": "SoftwareApplication", "name": "Verdetto: QR & Barcode Scanner", "operatingSystem": "Android",
       "applicationCategory": "UtilitiesApplication", "url": SITE + "/", "image": SITE + "/icon-512.png",
       "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD"}, "isAccessibleForFree": True, "publisher": ORG,
       "description": "See the link before it opens. Free, no ads, no tracking. Made for damaged codes."}


def og_image_for(name, title):
    """The page's own social image (assets.py renders og/<stem>.png per page); the shared one if it is missing."""
    stem = name[:-5] if name.endswith(".html") else name
    if (HERE / "og" / f"{stem}.png").exists():
        return f"{SITE}/og/{stem}.png", f"Verdetto: {title.replace(' - Verdetto', '')}"
    return f"{SITE}/og-image.png", "Verdetto icon with the words QR &amp; Barcode Scanner for Android, See the link before it opens."


def page(name, title, description, body, ld=None, og_type="website", nav_key=None, lang="en", rtl=False, alternates=None):
    nav = "".join(f'<a href="{href(h)}"{" aria-current=\"page\"" if h == name else ""}>{t}</a>' for h, t in NAV)
    menu = lang_menu(alternates, lang) if alternates else ""
    og_image, og_alt = og_image_for(name, title)
    banner = '<div class="draft" role="status">Draft for review. Not published.</div>\n' if DRAFT else ""
    ld_tag = f'<script type="application/ld+json">{json.dumps({"@context": "https://schema.org", **ld}, ensure_ascii=False)}</script>\n' if ld else ""
    canonical = url(name) if name != "404.html" else SITE + "/404"
    alt_tags = "".join(f'<link rel="alternate" hreflang="{code}" href="{url(page_name)}">' + chr(10) for code, page_name in (alternates or []))
    return f"""<!doctype html>
<html lang="{lang}"{' dir="rtl"' if rtl else ''}>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; img-src 'self' data:; font-src 'self'; script-src 'sha256-{REPORT_SCRIPT_HASH}'; frame-src https://docs.google.com; base-uri 'none'; form-action 'none'">
<title>{title}</title>
<meta name="description" content="{description}">
<link rel="canonical" href="{canonical}">
<link rel="me" href="https://mastodon.social/@VerdettoQR">
{alt_tags}<meta name="theme-color" media="(prefers-color-scheme: light)" content="#E9F5F1">
<meta name="theme-color" media="(prefers-color-scheme: dark)" content="#0F1312">
<link rel="icon" href="icon.svg" type="image/svg+xml">
<link rel="icon" href="favicon-32.png" sizes="32x32" type="image/png">
<link rel="apple-touch-icon" href="apple-touch-icon.png">
<meta property="og:type" content="{og_type}">
<meta property="og:site_name" content="Verdetto">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{description}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{og_image}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="{og_alt}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{title}">
<meta name="twitter:description" content="{description}">
<meta name="twitter:image" content="{og_image}">
{ld_tag}<style>{CSS}</style>
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
{banner}{SYMBOLS}
<header><div class="wrap">
  <a class="brand" href="{href('index.html')}"><svg aria-hidden="true"><use href="#mark"/></svg>Verdetto</a>
  <nav aria-label="Site">{nav}</nav>{menu}
</div></header>
<main id="main"><div class="wrap">
{body}
</div></main>
<footer><div class="wrap">
  <p>&copy; 2026 <span class="lockup"><svg aria-hidden="true"><use href="#mark"/></svg>Verdetto</span> &middot; <a href="mailto:{EMAIL}">{EMAIL}</a></p>
  <p class="links"><a href="{href('privacy.html')}">Privacy policy</a> &middot; <a href="{href('terms.html')}">Terms of use</a> &middot; <a href="{href('support.html')}">Help</a> &middot; <a href="{href('check-qr-code-link.html')}">How to check a QR code link</a> &middot; <a href="{href('support-the-work.html')}">Support the work</a> &middot; <a href="{href('report.html')}">Report a problem</a> &middot; <a href="{href('safety-list.html')}">The safety list this week</a> &middot; <a href="{href('developers.html')}">For developers</a> &middot; <a href="{href('press.html')}">Press kit</a></p>
  <p class="links">Where to find us: {SOCIAL_LINKS}</p>
</div></footer>
</body>
</html>
"""


def ic(k):
    return f'<svg aria-hidden="true"><use href="#ic-{k}"/></svg>'


def weekly_line():
    """One line of proof of work on the home page from stats/weekly.json: reports received and entries added in the last
    counted week. Empty until a week has numbers to show, so the page never announces zeros."""
    try:
        s = json.loads((HERE / "stats" / "weekly.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return ""
    if not s.get("issues_counted"):
        return ""
    reports = int(s.get("reports_received") or 0)
    added = sum(int(v) for v in (s.get("entries_added") or {}).values())
    if reports + added == 0:
        return ""
    return (f'<p class="meta">The safety list this week: {reports} report{"s" if reports != 1 else ""} received, '
            f'{added} entr{"ies" if added != 1 else "y"} added after review. <a href="{href("safety-list.html")}">The numbers</a>.</p>')



# The privacy policy is offered in the app's eleven languages (the terms stay English: operator, 2026-09-04).
# Translations live in _privacy/<code>.html (an underscore folder, so GitHub Pages does not serve the fragments);
# the first line of a fragment is "<!-- title | description -->". {ADDRESS}, {EMAIL}, and {LANG_ROW} are filled in.
PRIVACY_LANGS = [("en", "English", "privacy.html"), ("es", "Español", "privacy-es.html"), ("fr", "Français", "privacy-fr.html"),
                 ("de", "Deutsch", "privacy-de.html"), ("pt-BR", "Português (Brasil)", "privacy-pt-br.html"), ("ru", "Русский", "privacy-ru.html"),
                 ("id", "Bahasa Indonesia", "privacy-id.html"), ("ja", "日本語", "privacy-ja.html"), ("zh-Hans", "简体中文", "privacy-zh-hans.html"),
                 ("hi", "हिन्दी", "privacy-hi.html"), ("ar", "العربية", "privacy-ar.html")]
PRIVACY_ALTERNATES = [(code, page_name) for code, _, page_name in PRIVACY_LANGS] + [("x-default", "privacy.html")]
# The terms follow the same route since the operator's word of 2026-09-04 ("do 1": terms in the ten languages).
TERMS_LANGS = [(code, label, page_name.replace("privacy", "terms")) for code, label, page_name in PRIVACY_LANGS]
TERMS_ALTERNATES = [(code, page_name) for code, _, page_name in TERMS_LANGS] + [("x-default", "terms.html")]


def lang_row(langs, current):
    links = " &middot; ".join(
        f'<a href="{href(page_name)}" lang="{code}" hreflang="{code}"{" aria-current=\"page\"" if code == current else ""}>{label}</a>'
        for code, label, page_name in langs)
    return f'<p class="langs" aria-label="This page in other languages">{links}</p>'


def privacy_lang_row(current):
    return lang_row(PRIVACY_LANGS, current)


LANG_LABELS = {code: label for code, label, _ in PRIVACY_LANGS}


def lang_menu(alternates, current):
    """The top app bar's language control: the current language behind a globe, opening a menu of the page's alternates.
    A details element, so it needs no script; each item is a 48 px row; the current language is marked."""
    items = "".join(
        f'<li><a href="{href(page_name)}" lang="{code}" hreflang="{code}"{" aria-current=\"page\"" if code == current else ""}>{LANG_LABELS[code]}</a></li>'
        for code, page_name in alternates if code != "x-default")
    return (f'<details class="lang"><summary aria-label="Language: {LANG_LABELS[current]}">{ic("language")}<span>{LANG_LABELS[current]}</span></summary>'
            f'<ul class="menu">{items}</ul></details>')


def translation(folder, langs, code):
    """A translated legal page from <folder>/<code>.html: the first line is "<!-- title | description -->", and the
    body takes {ADDRESS}, {EMAIL}, {LANG_ROW}, {TERMS_HREF}, and {PRIVACY_HREF} (the privacy page in the same language)."""
    text = (HERE / folder / f"{code}.html").read_text(encoding="utf-8")
    first, body = text.split(chr(10), 1)
    m = re.match(r"<!--\s*(.*?)\s*\|\s*(.*?)\s*-->", first)
    title, desc = m.group(1), m.group(2)
    privacy_page = next(p for c, _, p in PRIVACY_LANGS if c == code)
    body = (body.replace("{ADDRESS}", ADDRESS).replace("{EMAIL}", EMAIL).replace("{LANG_ROW}", "")
            .replace("{TERMS_HREF}", href("terms.html")).replace("{PRIVACY_HREF}", href(privacy_page))
            .replace("{COMMUNITY_HREF}", href("community-license.html")))
    return title, desc, body


def privacy_translation(code):
    return translation("_privacy", PRIVACY_LANGS, code)


def terms_translation(code):
    return translation("_terms", TERMS_LANGS, code)


PRIVACY = f"""
<h1>Privacy policy</h1>
<p class="meta">For Verdetto: QR &amp; Barcode Scanner, the Android app published by Verdetto. Effective date: September 5, 2026.</p>

<div class="card"><p><strong>In short.</strong> No accounts, no ads, no analytics. Scanning happens on your phone, and an ID or license scan never leaves it. With online lookups on, the default, only the address, domain, or number you scanned goes out, to the services in the table below, and it goes straight from your phone to them, never through us. Nothing else leaves the phone, apart from your phone's own backup, which you can turn off. The only thing we ever receive is an email you choose to send us. We do not collect, store, sell, or share any data about you. This website sets no cookies.</p></div>

<h2>Who we are</h2>
<p>Verdetto, {ADDRESS}, United States, a small business in Virginia. Contact: <a href="mailto:{EMAIL}">{EMAIL}</a>. Verdetto publishes the app and is the party responsible for this policy wherever a law asks for one. The app sends us nothing, and the one thing we process is the email you may send us, so we have not appointed a representative in the European Union or the United Kingdom or a data protection officer; that email address reaches the person who answers.</p>

<h2>What the app does on your phone</h2>
<ul>
  <li><strong>Camera.</strong> Camera frames are read on the phone to find and decode codes. They are not stored and not uploaded.</li>
  <li><strong>Images you choose.</strong> If you pick an image from your photos, it is read on the phone the same way and is not uploaded.</li>
  <li><strong>Scan history.</strong> Decoded content is kept in a history on your phone so you can find it again. Scans older than 90 days are cleared on their own unless you star them; Settings lets you choose 30, 90, or 365 days, or forever. You can delete any entry with a swipe, or clear the whole history, in the app. Driver's licenses and boarding passes are shown and not saved to history unless you turn that on in Settings.</li>
  <li><strong>Safety checks.</strong> The app inspects scanned content on the phone for warning signs and compares links, sites, and wallet addresses with a list of known phishing, malware, scam, and sanctions entries that is stored on the phone. The comparison never sends what you scanned anywhere.</li>
  <li><strong>Settings.</strong> Your preferences are stored on the phone.</li>
</ul>

<h2>What leaves the phone, and when</h2>
<p>Online lookups are on by default and can be turned off in Settings. Product lookups have a switch of their own under it. While they are on, the app may make these requests. Each carries only what is listed, the app's name and version, our support address, and your phone's internet address, which every internet request carries. Your phone makes each request itself, at your instruction, to the service named; we are not part of it and do not receive, relay, or see it. A license or ID scan never leaves the phone, and the app never looks a person up.</p>
<table><thead><tr><th>What is sent</th><th>When</th><th>Who sees it</th></tr></thead><tbody>
<tr><td>A request for a newer warning list</td><td>A few times a day</td><td>GitHub, where we publish it</td></tr>
<tr><td>A shortened link</td><td>When you scan one</td><td>The shortening service and the sites it points to</td></tr>
<tr><td>A domain name</td><td>When a link's age is checked</td><td>rdap.org, then the domain's registry</td></tr>
<tr><td>A product, book, medicine, journal, device, music, or vehicle number</td><td>When you scan one</td><td>The one database that covers it, named below</td></tr>
</tbody></table>
<ul>
  <li><strong>Warning-list updates.</strong> The app downloads a newer copy of the warning list, a few times a day, from GitHub, where we publish it (github.com/verdettoqr/link-safety-list). GitHub sees the request the way it sees any download. The same download carries the lookup tables for postal codes, Italian and French medicines, German bank sort codes, airline and airport names, and the directory of domain registries (IANA's RDAP bootstrap file). The request carries no scanned content, and the app checks the list's signature before using it.</li>
  <li><strong>Shortened links.</strong> To show you where a shortened or affiliate link leads, the app asks the shortening service for its destination and follows the answer to where it lands. Each address in the chain, including the destination, sees a request the way it would see any visit; the page itself is not read or shown.</li>
  <li><strong>Domain age.</strong> To tell you when a link's domain was registered, the app sends the domain name to rdap.org, a public directory that forwards the question to the domain's registry. The answer is kept on the phone for a week so the same domain is not asked about twice.</li>
  <li><strong>Product, book, medicine, music, journal, and vehicle numbers.</strong> To show details, the app sends the number to the database that covers it: Open Food Facts and its sister databases (Open Beauty Facts, Open Pet Food Facts, Open Products Facts) for products, the US Consumer Product Safety Commission's recall database for a product's recalls, Open Library and the German and French national libraries for books, then Wikidata when none of them has the book, openFDA for US medicines and medical devices, then DailyMed and RxNav (the US National Library of Medicine) for a US medicine and the European Commission's EUDAMED database for a device that openFDA does not know, Spain's medicines agency (AEMPS) for a Spanish medicine, MusicBrainz for music, Crossref for journal and paper numbers, Wikidata for product, magazine, and sheet-music numbers, and the NHTSA vehicle database for a vehicle identification number. Each request carries the number, the app's name and version, and our support address so the service can reach us about the app; nothing about you. Their answers are shown as given. Postal codes, Italian and French medicine codes, airline and airport names, the country and carrier of a phone number, and the bank behind a German sort code are looked up in tables on the phone, so those never leave it. For a vehicle, the year, make, and model also go to NHTSA's recall and crash-test databases and to the EPA fuel-economy database (fueleconomy.gov).</li>
</ul>
<p>These services are run by others, in the United States and in Europe, and they process the request, including your phone's internet address, under their own privacy policies: <a href="https://docs.github.com/en/site-policy/privacy-policies/github-general-privacy-statement">GitHub</a>, <a href="https://about.rdap.org/">rdap.org</a> and the registry it forwards to, <a href="https://world.openfoodfacts.org/privacy">Open Food Facts</a>, <a href="https://archive.org/about/terms.php">Open Library</a> (the Internet Archive), the <a href="https://www.dnb.de/EN/Service/Datenschutz/datenschutz_node.html">German National Library</a>, the <a href="https://www.bnf.fr/fr/politique-de-confidentialite">French National Library</a>, <a href="https://www.fda.gov/about-fda/about-website/website-policies">openFDA</a> (the US Food and Drug Administration), the <a href="https://www.cpsc.gov/about-cpsc/policies-statements-and-directives/privacy-policy">US Consumer Product Safety Commission</a>, <a href="https://www.nlm.nih.gov/web_policies.html">DailyMed and RxNav</a> (the US National Library of Medicine), <a href="https://webgate.ec.europa.eu/eudamed-static-play/documents/assets/privacy-policy/privacy_statement_en.pdf">EUDAMED</a> (the European Commission), <a href="https://www.aemps.gob.es/politica-privacidad/">AEMPS</a> (Spain's medicines agency), <a href="https://metabrainz.org/privacy">MusicBrainz</a>, <a href="https://www.crossref.org/operations-and-sustainability/privacy/">Crossref</a>, <a href="https://foundation.wikimedia.org/wiki/Policy:Privacy_policy">Wikidata</a> (the Wikimedia Foundation), and the NHTSA vehicle database (the US Department of Transportation). The United States has no general EU or UK adequacy decision; your phone sends the request there because you scanned the code. They may change or stop. With online lookups off, nothing leaves the phone.</p>

<h2>Your phone's backup</h2>
<p>Unless you turn off "Include in the phone's backup" in Settings, your history, settings, and your card ride along in your phone's own Android backup, the same way other apps' data does. That backup goes to your Google account under Google's policy; Verdetto never sees it. History includes what codes contained, such as a Wi-Fi password you scanned, so turn the setting off if you would rather it stayed on the phone. If you turn on read-aloud, the result's title goes to your phone's speech engine, under its maker's policy.</p>

<h2>What never leaves the phone</h2>
<p>Your scan history, except through your phone's backup if you leave that on. The pages behind links, which the app never opens or inspects. Wi-Fi passwords, contacts, and calendar entries you scan. Anything about you.</p>

<h2>Permissions</h2>
<p>The app asks for the camera, which it needs to scan, and for contacts access only if you fill your own card from your phone's profile. It uses the network only for the lookups described above, vibration for the buzz on scan, and, on Android 10 and older, the Wi-Fi setting needed to join a network you scanned. Joining a Wi-Fi network, adding a contact, or saving an event goes through the standard Android prompt for that action, and only when you choose it. The contribution goes through Google Play's own billing.</p>

<h2>Purchases</h2>
<p>The optional contribution inside the app is sold through Google Play. Google processes the payment under <a href="https://policies.google.com/privacy">its own privacy policy</a>; we never see your name, email address, or payment details. Google's billing code inside the app also reports to Google how its own steps went, such as whether a connection or a purchase succeeded or failed, which Google uses to improve that code and its support for errors. Those reports go to Google, not to us, under the same policy, and only when the app talks to Google Play for the contribution. Google shows us, in its developer console and its sales reports, an order record for refunds and tax: at most an order number, the item, the amount and currency, the phone's model, and the country, state, city and postal code the purchase was made from; where Google itself is the seller, in the EEA and the UK, only the country. The app itself keeps only a note on your phone that a contribution was made, for the thank-you badge.</p>

<h2>Reports you send</h2>
<p>If you choose to report something, from the app or from this website, the report form is a Google Form that opens in your browser; the app itself sends nothing. The report contains only what you see on the form: the category, the scanned text if you leave it in, your description, where you found the code if you say, the app's version, and, only if you add it, your email address so we can reply. Reports are stored in Verdetto's Google account under <a href="https://policies.google.com/privacy">Google's privacy policy</a> and are used only to handle the report: a person reads it, and nothing is added to the warning list without that review. Reports are kept for up to two years and then deleted; write to us to have yours deleted sooner. For a license or ID scan, a report carries the card's format numbers and the check's outcome, never anything printed on the card.</p>

<h2>When you write to us</h2>
<p>If you email us, we receive your address and what you wrote, and we use them to answer you. That is the only personal data we process, and we process it because you asked us something (in the European Union and the United Kingdom, that is a contract-like request and our legitimate interest in answering it). Your message stays in our mailbox like any email, is not added to any list, and is not shared or used for anything else. Ask, and we delete the thread.</p>

<h2>Children</h2>
<p>The app is not directed at children under 13, asks no one's age, builds no profile, and collects no data from anyone.</p>

<h2>Keeping and deleting data</h2>
<p>Everything the app keeps is on your phone, and in your phone's backup if you leave that on. Delete history entries in the app, or uninstall the app to remove all of it. We hold no data about you from the app, so there is nothing for us to delete or hand over.</p>

<h2>Your rights</h2>
<p>Wherever you live, you can ask what we hold about you and ask for a copy, a correction, or deletion, or object to our processing it. Because the app sends us nothing, what we hold is at most an email you sent us. Write to <a href="mailto:{EMAIL}">{EMAIL}</a>; we answer within the time your law sets, and in any case within a month. You may also complain to your data protection authority: in the European Economic Area, the authority of your country; in the United Kingdom, the Information Commissioner's Office; in Brazil, the ANPD; elsewhere, the authority your law names. In California and the other US states with privacy laws: we collect no personal information through the app, and we do not sell or share it.</p>

<h2>This website</h2>
<p>These pages are static and hosted on <a href="https://docs.github.com/en/pages/getting-started-with-github-pages/about-github-pages#data-collection">GitHub Pages</a>. They set no cookies and run no analytics. The report page embeds a Google Form, which loads from Google under its privacy policy; every other page loads nothing from anywhere but this site. The safety-list page shows weekly numbers that this site serves as a small file of its own, copied from the public list repository once a week; your browser makes no request to any third party for it, and the numbers hold nothing about anyone's phone or scans. GitHub may keep standard server logs, such as the address a page was requested from and when, under its own privacy statement.</p>

<h2>Changes</h2>
<p>If this policy changes, the new version will be posted here with a new effective date.</p>

<h2>Contact</h2>
<p>Questions about privacy: <a href="mailto:{EMAIL}">{EMAIL}</a>.</p>

<details class="more"><summary>Details for specific laws</summary>
<ul>
  <li><strong>European Economic Area and United Kingdom (GDPR, UK GDPR).</strong> Verdetto is the controller only for the email you send us, processed under Article 6(1)(b) and (f). The app's lookups are requests your phone makes to independent controllers, named above, at your instruction; we are not a party to them. For the contribution, Google Commerce Limited is the seller and Google is the controller for the payment and for its billing code's own reports; our part is limited to the app carrying that code, and Google's privacy policy governs what Google does with it. You have the rights in Articles 15 to 21 and may complain under Article 77. No representative under Article 27 and no data protection officer have been appointed, because our processing is occasional, small, and low-risk. No automated decision-making or profiling takes place.</li>
  <li><strong>Brazil (LGPD).</strong> Verdetto is the controlador for the email you send us, processed to answer your request (Article 7, V and IX). The contact for data-protection matters, the encarregado, is {EMAIL}. You have the rights in Article 18 and may complain to the ANPD. Requests are answered in Portuguese or the language you wrote in.</li>
  <li><strong>Canada and Quebec.</strong> No personal information is collected through the app. The person in charge of the protection of personal information is reached at {EMAIL}, which also handles access and correction requests under Quebec's Law 25 and PIPEDA.</li>
  <li><strong>Mexico.</strong> This page is the aviso de privacidad integral, and its summary above is the simplified notice: the responsible party is Verdetto at the address above, the only data processed is the email you send us, for the purpose of answering you, and ARCO rights are exercised by writing to {EMAIL}.</li>
  <li><strong>Japan (APPI).</strong> We acquire no personal information through the app; an email you send us is used only to reply.</li>
  <li><strong>India, Indonesia, Saudi Arabia, the United Arab Emirates, Egypt, Argentina, Colombia, Chile, Peru, Switzerland, Australia, Russia, and elsewhere.</strong> The same facts apply: the app sends us nothing, we keep nothing about you, and any right your law gives you is exercised by writing to {EMAIL}.</li>
</ul>
</details>
"""

TERMS = f"""
<h1>Terms of use</h1>
<p class="meta">For Verdetto: QR &amp; Barcode Scanner. Last updated: September 5, 2026.</p>

<div class="card"><p><strong>In short.</strong> The app looks at what a code contains and tells you what it found. It never says anything is safe. Whether to open, join, dial, or act on scanned content is your decision. These are the same terms shown inside the app; if the two ever differ, the installed version applies.</p></div>

<h2>The app</h2>
<p>This app is free. Its safety list's pipeline is open source today, and the app's own code is published under the GNU General Public License, version 3 or later. It is provided as is and as available, without warranty of any kind, express or implied, including fitness for a particular purpose. It is not security software and not a substitute for security advice.</p>

<h2>Who provides the app</h2>
<p>Verdetto, {ADDRESS}, United States, a small business in Virginia. Contact: <a href="mailto:{EMAIL}">{EMAIL}</a>. Support requests and legal notices go to that address.</p>

<h2>What the safety checks are</h2>
<p>When you scan a code, the app looks at the content itself, on your phone, for known warning signs: hidden sign-in details, raw IP addresses, lookalike or imitation names, shortened links, unencrypted addresses, unusual ports, app or program downloads, unusually deep subdomains, script or file addresses, tracking and affiliate parameters, premium-rate numbers, open Wi-Fi networks, and payment destinations. It also compares links, sites, and wallet addresses with a list of known phishing, malware, and scam entries kept on the phone, compiled from public sources (PhishTank, the CERT Polska warning list, PhishDestroy, PhishIndex, the polkadot-js phishing list, and the US Treasury's OFAC sanctions list). With online lookups on, the app can download a newer list, follow a shortened or affiliate link to where it leads, ask a domain's registry when it was registered, and send a product number to Open Food Facts and its sister databases, the US Consumer Product Safety Commission's recall database, Open Library, the German and French national libraries, openFDA (medicines and medical devices), DailyMed and RxNav, Spain's medicines agency AEMPS, the European Commission's EUDAMED database, MusicBrainz, Crossref, Wikidata, or the NHTSA vehicle database. Their answers are shown as given. Postal codes, Italian and French medicine codes, phone-number regions and carriers, and German bank sort codes are named from tables kept on the phone.</p>

<h2>What they are not</h2>
<p>The checks do not open or inspect the page behind a link, cannot see what a network, contact, calendar entry, or product will do, and cannot catch every scam, unsafe site, or harmful code. "No warnings found" means none of the app's checks matched. It is never a statement that anything is safe, genuine, or trustworthy. The app never looks a person up: a license or ID scan is shown from the barcode alone, with the age, the expiry, and the issuer worked out on the phone, and the app cannot tell a genuine card from a copy.</p>

<h2>Your decisions</h2>
<p>Whether to open a link, join a network, add a contact or event, dial a number, or act on any scanned content is your decision, made at your own risk. Automatic opening, when you turn it on, opens links you have not looked at; you accept that when you turn it on.</p>

<h2>Liability</h2>
<p>To the fullest extent permitted by law, the developers and contributors of this app are not liable for any loss, damage, or harm arising from the use of the app or from acting on scanned content, including opening a link, joining a network, or relying on a check or a lookup.</p>

<h2>Your rights as a consumer</h2>
<p>Nothing in these terms takes away rights that the consumer law of your country gives you and that cannot be waived by agreement, including the guarantees of the Australian Consumer Law and the rights of consumers in the European Union, the United Kingdom, and Brazil. The Liability section applies only as far as your law allows: it does not exclude liability for intent or gross negligence, for death or personal injury caused by negligence, or for anything else the law does not let us exclude.</p>

<h2>Your data</h2>
<p>Online lookups are on by default and can be turned off in Settings. Product lookups have a switch of their own under it. While on, only the address, domain, or the product, book, medicine, device, journal, or vehicle number goes, with the app's name and our support address, to the named services (Open Food Facts and its sisters, the US Consumer Product Safety Commission's recall database, Open Library, the German and French national libraries, openFDA, DailyMed and RxNav, Spain's medicines agency AEMPS and the European Commission's EUDAMED database for medicines and medical devices, MusicBrainz, Crossref, Wikidata, and the NHTSA vehicle database); with them off, nothing leaves the phone. There are no ads, no analytics, and no accounts. The <a href="{href('privacy.html')}">privacy policy</a> has the details. For a vehicle, the year, make, and model also go to NHTSA's recall and crash-test databases and to the EPA fuel-economy database (fueleconomy.gov).</p>

<h2>Contributions</h2>
<p>The app is free and complete: every check and every decode is free for everyone, and nothing is locked. It offers one optional, one-time contribution, sold as an in-app item through Google Play from US$0.99 or the local equivalent, which pays for the work and earns a thank-you badge and the small extras listed on the Support screen as they arrive. The price in the purchase flow is the price you pay, including any tax Google Play charges. In the European Economic Area and the United Kingdom, Google is the merchant of record for the purchase; everywhere else, Verdetto is the seller and Google Play handles the payment. Refunds follow Google Play's refund policy and the consumer law of your country; if something went wrong, write to <a href="mailto:{EMAIL}">{EMAIL}</a> and we will help. Where Google Play's billing is unavailable, the contribution is not offered. A contribution buys no protection and no promise of future features. Verdetto is a small business; a contribution is a purchase, not a gift, and it brings no tax benefit.</p>

<h2>Third-party services</h2>
<p>The lookup services and the shortening services the app can ask are run by others under their own terms and privacy policies. Their answers are shown as given; they may change or stop, and we are not responsible for them. NHTSA's recall and crash-test databases and the EPA fuel-economy database are among them; recall and rating information is for the model year and is not a statement about the individual vehicle.</p>

<h2>Open source and trademarks</h2>
<p>The safety list's pipeline is published under the MIT License. The app's own code is licensed under the GNU General Public License, version 3 or later, and its scanner core under the Apache License 2.0; both are published with the first release. Those licenses cover code. They do not cover the Verdetto name, icon, wordmark, splash screen, screenshots or store material, which are not licensed and stay ours; a fork may not use that name or artwork as its own. Use of the name, the icon and the 'Built on Verdetto' badge is governed by the <a href="{href('community-license.html')}">Verdetto Community License</a>, a trademark license. The app also includes work by others under their own licenses, listed under About, Licenses; the safety list names its sources and their terms in its repository.</p>

<h2>Governing law</h2>
<p>These terms are governed by the laws of the Commonwealth of Virginia, United States. If you are a consumer in a country whose law protects you regardless of that choice, that protection applies, and you may bring a claim before the courts of your own country.</p>

<h2>Language</h2>
<p>These terms are written in English and offered in ten other languages. The English text is the reference, except where the law of your country says otherwise.</p>

<h2>Changes</h2>
<p>These terms may change with a new version of the app. The text in the installed version is the one that applies.</p>
"""

FAQ = [
    ("It said \"No warnings found.\" Is the link safe?",
     "The app does not know, and it never says something is safe. \"No warnings found\" means none of its checks matched. Look at the address it shows you, and open it only if you would have opened it anyway."),
    ("Does it work offline?",
     "Yes. Scanning and every built-in check run on the phone. Online lookups add where a short link leads, how old a domain is, product details, and, for a vehicle, its recall campaigns, crash-test ratings, and fuel economy from NHTSA and the EPA. They need a connection and can be turned off in Settings."),
    ("Why does it ask for the camera?",
     "To scan. The only other thing it can ask for is contacts access, once, if you fill your card from your phone's profile."),
    ("How do I turn off online lookups?", "Settings, then Allow online lookups. With them off, nothing leaves the phone. Product lookups have a switch of their own under it."),
    ("How do I delete my history?", "Swipe an entry, or Clear history in Settings. Scans older than 90 days clear on their own unless you star them. History also rides in your phone's own backup unless you turn that off; uninstalling removes it."),
    ("A code will not scan.",
     "Fill more of the screen with it, hold still, and let the camera focus. Damaged or faded codes take a moment longer. If it still will not read, send us a photo of the code if it is not sensitive."),
    ("What does the contribution unlock?",
     "Nothing you need; everything stays free. Supporters get a badge you can hide, and a few small extras are planned."),
]
SUPPORT = f"""
<h1>Help</h1>
<div class="card"><p>Something wrong with a scan, a warning, or the app? <a href="{href('report.html')}">Report it</a>; a person reads every report. A site listed by mistake is reviewed the same day.</p></div>
<div class="card"><p>Write to <a href="mailto:{EMAIL}">{EMAIL}</a>. It helps to include your phone model, your Android version, and what you were scanning if you can share it. Do not send a code that contains a password, a sign-in link, or anything you would not put in an email. We keep your message for as long as it takes to answer, then delete it.</p></div>

<h2>Common questions</h2>
<div class="faq">
""" + "\n".join(f"<p><strong>{q}</strong><br>\n{a}</p>\n" for q, a in FAQ) + f"""
</div>
<p>Not sure what to look for in a link? Read <a href="{href('check-qr-code-link.html')}">how to check a QR code link before you open it</a>. Want to keep the app free for everyone? <a href="{href('support-the-work.html')}">Support the work</a>.</p>
"""

SPONSORS_CARD = (f"""<div class="card">{ic('heart')}<div><h3>From a browser</h3><p>GitHub Sponsors, monthly ($2 or $5) or once ($3 or $10), through GitHub. It reaches the same place. <a href="https://github.com/sponsors/verdettoqr">Sponsor on GitHub</a></p></div></div>"""
                 if SPONSORS_LIVE else
                 f"""<div class="card">{ic('clock')}<div><h3>From a browser</h3><p>GitHub Sponsors is being set up. Until it opens, the app is the way to give. The link appears here when it does.</p></div></div>""")
SUPPORT_FAQ = [
    ("Is Verdetto really free?",
     "Yes. Every feature, every check, and every decode is free for everyone, with no ads and no tracking: nothing about you or your scans goes to us, and the only code in the app that reports to anyone else is Google's own billing code, which reports to Google about the purchase. A contribution is optional and changes nothing you can do."),
    ("How does Verdetto make money?",
     "From one-time contributions by the people who use it: from $0.99 in the app through Google Play" + (", or through GitHub Sponsors from a browser" if SPONSORS_LIVE else "") + ". There are no ads, no data sales, and no paid tier."),
    ("What does a contribution unlock?",
     "Nothing you need. Supporters get a badge in About that they can hide, and a few small extras as they arrive."),
    ("Is a contribution a gift?",
     "No. Verdetto is a small business, so a contribution is a purchase, and it brings no tax benefit."),
    ("Will the app ask me for money?",
     "Not with prompts, banners, or reminders. After the app does something for you, it may say thank you and mention that the people who use it pay for it, at most once a month; a switch in Settings turns that off. The Support screen is there when you look for it, under Settings."),
    ("Can I give from a computer?",
     "Yes, through GitHub Sponsors, monthly or once." if SPONSORS_LIVE else "Not yet. GitHub Sponsors is being set up; this page will say when it opens."),
]
SUPPORT_WORK = f"""
<h1>Support the work</h1>
<p>Verdetto has no ads and nothing to sell, so the people who use it pay for it and pass it on. Every check and every decode is free for everyone. The app never nags: no ads, no pop-ups, no rating prompts. After it does something for you, it may say thank you and mention that the people who use it pay for it, at most once a month, and a switch in Settings turns that off.</p>
<div class="grid three">
  <div class="card">{ic('heart')}<div><h3>On your phone</h3><p>Settings, then Support development. From $0.99, once, $2.99 suggested, through Google Play. The app never sees your card.</p></div></div>
  {SPONSORS_CARD}
  <div class="card">{ic('scan')}<div><h3>Pass it on</h3><p>Free because people share it. Send a friend verdettoqr.com, or open Share in the app and let them scan the code. Sharing sends nothing anywhere.</p></div></div>
</div>

<h2>Where it goes</h2>
<p>The domain and the mailbox, the Google Play developer account, cheap test phones (the ones where scanners fail), and the time to keep the safety list and the reader current. About $25 a month keeps the lights on; everything above that goes to test phones and time.</p>

<h2>What you get</h2>
<p>A thank-you badge in About that you can hide, and the small extras listed on the Support screen as they arrive. Nothing you need: every feature stays free for everyone, and no check is ever held back.</p>

<h2>What it is not</h2>
<p class="meta">Verdetto is a small business. A contribution is a purchase, not a gift, and it brings no tax benefit. Refunds follow Google Play's{" or GitHub's" if SPONSORS_LIVE else ""} own policy and the law where you live.</p>

<h2>Questions</h2>
<div class="faq">
""" + "\n".join(f"<p><strong>{q}</strong><br>\n{a}</p>\n" for q, a in SUPPORT_FAQ) + """
</div>
"""
SUPPORT_WORK_LD = {"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in SUPPORT_FAQ]}
FAQ_LD = {"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in FAQ]}

GUIDE_TITLE = "How to check a QR code link before you open it"
GUIDE_DESC = "Six things to look at in a QR code's link before you tap it: the domain, short links, lookalike names, the connection, downloads, and its placement."
GUIDE = f"""
<div class="prose">
<h1>{GUIDE_TITLE}</h1>
<p class="meta">Updated {DATE}. About a four-minute read.</p>

<div class="card"><p><strong>In short.</strong> Before you open a link from a QR code: read the domain, not the whole address; treat shortened links as unknown until they are expanded; look for lookalike names; check for <code>https</code> and no unusual port; never install anything a code hands you; and ask why the code is where it is. A scanner can show you all of that. It cannot tell you a page is safe.</p></div>

<p>A QR code is just a way of typing a link so you do not have to. The trouble is that the link is invisible until something reads it, and many scanner apps open it the instant they do. Fake codes on parking meters, restaurant tables, posters, and even in emails rely on exactly that. The fix is simple: look at the link before you open it. Here is what to look at, in order.</p>

<h2>1. Read the domain, not the whole link</h2>
<p>The domain is the part after <code>https://</code> and before the first single slash. In <code>https://accounts.example.com/login?ref=qr</code> the domain is <code>accounts.example.com</code>, and the part that matters most is the last two labels, <code>example.com</code>. Everything after the slash can say anything; it is the domain that decides where you land. A good scanner shows the domain by itself in large type, so you do not have to find it in a long string.</p>

<h2>2. Treat shortened links as unknown</h2>
<p>Links through bit.ly, t.co, tinyurl, and similar services hide their destination on purpose. A code that shows one of these tells you nothing until it is expanded. Either expand it first, with a scanner that follows the short link and shows you where it ends up, or do not open it.</p>

<h2>3. Look for lookalikes</h2>
<p>The oldest trick is a domain that reads like a familiar one. Watch for a digit standing in for a letter (<code>paypa1.com</code>), an extra word or hyphen (<code>paypal-secure.com</code>), a familiar name pushed into the wrong place (<code>paypal.com.example.net</code>, where the domain is <code>example.net</code>), and letters from another alphabet that draw the same shape. If a name looks almost right, treat it as wrong until you have typed the real one yourself.</p>

<h2>4. Check the connection and the port</h2>
<p>A link that starts with <code>http://</code> rather than <code>https://</code> sends everything you type in the open. A link with a number after the domain, such as <code>example.com:8080</code>, is talking to something other than an ordinary website. Neither proves a scam, but neither belongs on a code that asks you to sign in or pay.</p>

<h2>5. Do not install what a code hands you</h2>
<p>A link that ends in <code>.apk</code> is an Android program, not a page. Apps come from the store, not from stickers. The same goes for links that ask for permission to install "an update" or "a viewer" before you can see anything.</p>

<h2>6. Ask why the code is there</h2>
<p>A QR code stuck over another QR code, a code on a parking meter that already has a payment terminal, a code in a text message from a number you do not know, a code that promises a refund or a prize: the placement is the warning. Criminals print stickers because stickers are cheap. When a code appears where a code would not naturally be, skip it and use the official app or website directly.</p>

<h2>What a scanner can and cannot tell you</h2>
<p>A scanner can show you the link in full, expand a short one, flag the patterns above, and compare the address with lists of known phishing and scam sites. What it cannot do is open the page and judge it for you, and no list is complete. That is why Verdetto reports "No warnings found" rather than "safe": it means none of its checks matched, and the last check is the one you make by reading the address. If a code asks you to sign in, enter card details, or install something, close it and go to the site you already know.</p>

<h2>If you already opened one</h2>
<p>Close the page. If you typed a password, change it on the real site and anywhere else you used it. If you entered card details, tell your bank. If you installed something, uninstall it and run a scan with the security software already on the phone. Then delete the code from your history so you do not open it again by accident.</p>

<div class="card callout"><p>Verdetto shows every link before it opens, expands shortened and affiliate links when online lookups are on, and flags each of the patterns above on your phone. Free, with no ads, paid for by the people who use it. <a href="{href('index.html')}">See what it does</a>.</p></div>
</div>
"""
GUIDE_LD = {"@type": "Article", "headline": GUIDE_TITLE, "description": GUIDE_DESC, "datePublished": DATE, "dateModified": DATE,
            "author": ORG, "publisher": ORG, "mainEntityOfPage": url("check-qr-code-link.html"), "image": SITE + "/og-image.png"}

NOT_FOUND = f"""
<h1>That page is not here.</h1>
<p>The address may have changed, or the code that brought you here was wrong. Try one of these:</p>
<ul>
  <li><a href="{href('index.html')}">Home</a></li>
  <li><a href="{href('privacy.html')}">Privacy policy</a></li>
  <li><a href="{href('terms.html')}">Terms of use</a></li>
  <li><a href="{href('support.html')}">Help</a></li>
  <li><a href="{href('check-qr-code-link.html')}">How to check a QR code link before you open it</a></li>
  <li><a href="{href('support-the-work.html')}">Support the work</a></li>
</ul>
"""

# The report form: a Google Form owned by the Verdetto Google account. The page embeds it and passes the app's
# prefill through, so the app and every link only ever point at this page; the form behind it can change.
FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSfjC-Acjlr82CUOF-f5j3dPTkjQjArNrwaRJujiPiPb-PLH4g/viewform"
FORM_FIELDS = {"k": "entry.500397725", "c": "entry.140033470", "p": "entry.763672602", "w": "entry.937128776", "v": "entry.1720664752"}
# These are the published form's field ids (from the live page's FB_PUBLIC_LOAD_DATA_); the editor's preview shows different ones.
# k kind, c scanned text, p where found, w warnings shown, v versions; f (card format, from a license or ID scan) is folded into c
FORM_KINDS = {"s": "A link, Wi-Fi network, payment address, or phone number that looks like a scam",
              "r": "The app read a code wrong, or could not read it",
              "d": "Product, book, medicine, or other details were wrong",
              "o": "Something else: a mistake in the app, a translation, a suggestion",
              "m": "My site or link is listed by mistake"}
# The one script on the site, allowed by its hash in the content-security policy; no other script runs anywhere.
REPORT_SCRIPT = ("(function(){var F=" + json.dumps(FORM_URL) + ",M=" + json.dumps(FORM_FIELDS) + ",K=" + json.dumps(FORM_KINDS) + ";"
                 "var p=new URLSearchParams(location.search),q=[];"
                 "var cf=p.get('f');"   # a license or ID scan sends its card-format numbers as f; they ride in the scanned-text field, labelled
                 "for(var k in M){var v=p.get(k);if(k==='k'){v=K[v]||null;}if(k==='c'&&cf){v=(v?v+'\\n':'')+'Card format: '+cf;}if(v){q.push(M[k]+'='+encodeURIComponent(v.slice(0,2000)));}}"
                 "var s=q.length?'?usp=pp_url&'+q.join('&'):'';"
                 "var i=document.getElementById('report-form');if(i){i.src=F+s+(s?'&':'?')+'embedded=true';}"
                 "var a=document.getElementById('report-open');if(a){a.href=F+s;}})();")
REPORT_SCRIPT_HASH = base64.b64encode(hashlib.sha256(REPORT_SCRIPT.encode("utf-8")).digest()).decode("ascii")

REPORT = f"""
<div class="prose">
<h1>Report to <span class="lockup"><svg aria-hidden="true"><use href="#mark"/></svg>Verdetto</span></h1>
<p class="meta">A link that looks like a scam, a code the app read wrong, details that were wrong, or anything else that isn't right.</p>

<div class="card"><p>A person reviews every report. Nothing is added to the safety list automatically, and Verdetto never says a link is safe. Please don't include passwords, payment details, or personal documents; if you came here from the app, the scanned text is already filled in, and you can remove anything private before you send it.</p></div>
<div class="card"><p><strong>What happens next.</strong> A scam or mistaken-listing report becomes a case in the public <a href="https://github.com/verdettoqr/link-safety-list/issues?q=label%3Acase">list repository</a>: the address you reported, what the checks found, and the decision, never your email or your description. The case is decided by fixed rules, and only a page that shows a credential or payment form beside a brand or domain warning sign is listed.</p></div>
<div class="card"><p><strong>Listed by mistake?</strong> Choose "My site or link is listed by mistake". The page is fetched again the same day; if it no longer shows a credential or payment form, the entry is suppressed from every source in the next list update, and the public feed that listed it gets a false-positive report from us. Our own entries and their evidence are public in the <a href="https://github.com/verdettoqr/link-safety-list/tree/main/own">list repository</a>.</p></div>

<iframe id="report-form" title="Report form" src="{FORM_URL}?embedded=true" width="100%" height="1900" frameborder="0" marginheight="0" marginwidth="0" loading="lazy">Loading…</iframe>

<p>If the form does not load here, <a id="report-open" href="{FORM_URL}" rel="noopener" target="_blank">open it in a new tab</a>, or write to <a href="mailto:{EMAIL}">{EMAIL}</a>. The form is a Google Form; what you send is stored in Verdetto's Google account and is used only to handle your report. Details are in the <a href="{href('privacy.html')}">privacy policy</a>.</p>
</div>
<script>{REPORT_SCRIPT}</script>
"""

PRESS = f"""
<div class="prose">
<h1>Press kit</h1>
<p class="meta">Everything needed to describe Verdetto accurately, in one place. Quote freely; the sentence below is the one we use everywhere.</p>

<div class="card"><p><strong>In one sentence.</strong> Verdetto is a free QR code and barcode scanner for Android with no ads and no fake buttons. It shows the link before it opens, is built to read damaged codes, and checks scanned content for warning signs on the phone. It never says anything is safe: "No warnings found" means none of its checks matched.</p></div>

<h2>Boilerplate</h2>
<p>Verdetto: QR &amp; Barcode Scanner is a free Android app from Verdetto, a solo developer in Virginia. It reads QR codes and barcodes, including damaged ones, shows the person exactly what a code contains before anything opens, and checks links, Wi-Fi networks, payment addresses, and phone numbers for known warning signs on the phone itself. Its list of known phishing and scam entries is compiled in the open from public feeds, and its signature is checked on the device. The app has no ads, no accounts, and no analytics; an optional one-time contribution supports development, and nothing is locked behind it. Verdetto is pronounced "ver-DET-oh" and is Italian for verdict.</p>

<h2>Facts you can check</h2>
<ul>
  <li>Platform: Android 8 and later. Price: free. Ads: none. Accounts: none. Analytics: none.</li>
  <li>Scanning and every built-in check run on the phone. Online lookups are on by default and can be turned off with one switch, and product lookups have a switch of their own.</li>
  <li>Reads QR codes and barcodes including EAN, UPC, Code 128, Data Matrix, PDF417, and Aztec.</li>
  <li>The safety list is built in the open at <a href="https://github.com/verdettoqr/link-safety-list">github.com/verdettoqr/link-safety-list</a> and refreshed four times a day; the app verifies its signature before use.</li>
  <li>What the app never says: that a link, network, or product is safe. The wording is "No warnings found."</li>
  <li>Comparison basis: the ten most-installed free QR scanners on Google Play as of September 4, 2026, identified by install count that day; each listing's ads label and its most relevant reviews read the same day; 'fake button' is the reviewers' description, not ours; no scanner is named; the list and the notes are kept on file.</li>
  <li>Privacy policy: <a href="{href('privacy.html')}">verdettoqr.com/privacy</a>.</li>
  <li>Terms: <a href="{href('terms.html')}">verdettoqr.com/terms</a>.</li>
</ul>

<h2>Assets</h2>
<ul>
  <li><a href="icon-512.png">App icon, 512 px PNG</a> and <a href="logo.svg">the icon as SVG</a>. Mint ground, deep teal QR mark, one amber finder.</li>
  <li><a href="lockup-teal-amber.png">Lockup, mark and name, transparent PNG</a> for light grounds (teal body, amber accent) and <a href="lockup-white-amber.png">the same with a white body</a> for dark grounds; the mark keeps its colors and sits at the cap height of the name.</li>
  <li><a href="og-image.png">Share image, 1200 by 630</a> and <a href="play-header-4096x2304.jpg">wide banner, 4096 by 2304</a>.</li>
  <li><a href="screens/result-sheet.webp">Result sheet screenshot</a>: a scanned link shown before it opens, with the "No warnings found" chip.</li>
  <li><a href="screens/result-sheet-warning.webp">Result sheet, warning state</a>: a lookalike address (paypa1.com) flagged as imitating paypal.com before anything opens.</li>
</ul>
<p>Please do not alter the icon's colors or add effects; the mark is the brand.</p>
<p>Verdetto and the Verdetto QR mark are trademarks; a United States application for VERDETTO is pending (serial no. 50092495).</p>

<h2>Where to find us</h2>
<ul>
""" + "".join(f'  <li>{k}: <a href="{v}">{v}</a></li>\n' for k, v in SOCIAL.items()) + f"""  <li>Contact: <a href="mailto:{EMAIL}">{EMAIL}</a></li>
</ul>
</div>
"""

def weekly_page():
    """The safety list this week: the producer in verdettoqr/link-safety-list writes stats/weekly.json every Monday; the
    weekly-stats workflow copies it into this repository and rebuilds, so the numbers are rendered here at build time and
    no page script runs. Public data only: the list files and the case issues, never anything from a phone."""
    path = HERE / "stats" / "weekly.json"
    if not path.exists():
        return "<h1>The safety list this week</h1>\n<p>The first week's numbers arrive on Monday.</p>\n"
    s = json.loads(path.read_text(encoding="utf-8"))

    def day(iso):
        y, m, d = (int(x) for x in iso.split("-"))
        months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
        return months[m - 1], d, y

    m1, d1, y1 = day(s["week_start"])
    m2, d2, y2 = day(s["week_end"])
    span = f"{m1} {d1} to {d2}, {y1}" if m1 == m2 else f"{m1} {d1} to {m2} {d2}, {y2}"
    n = lambda v: f"{int(v):,}"  # noqa: E731
    added = s.get("entries_added", {})
    totals = s.get("totals", {})
    generated = s.get("generated_at", "")[:10]
    rows = [
        ("Reports received", n(s.get("reports_received", 0)), "Reports that reached the list through the report form or the app, counted once each."),
        ("Cases opened", n(s.get("cases_opened", 0)), "Reports a person took up for review as a public case."),
        ("Cases closed", n(s.get("cases_closed", 0)), "Cases decided this week: listed, listed by mistake, or not a phish."),
        ("Entries added", f"{n(added.get('urls', 0))} links, {n(added.get('hosts', 0))} hosts, {n(added.get('addresses', 0))} wallet addresses",
         "Addresses or hosts added to the list after a person reviewed a report."),
        ("Removed after review", n(s.get("unlisted", 0)), "Entries taken off the list after a listed-by-mistake report checked out."),
        ("On the list now", f"{n(totals.get('urls', 0))} links, {n(totals.get('hosts', 0))} hosts, {n(totals.get('addresses', 0))} wallet addresses; {n(totals.get('allow', 0))} allowed",
         "Verdetto's own entries, the ones people reported and a person confirmed; the public feeds the list also carries are counted on the repository."),
    ]
    table = "".join(f"<tr><td>{k}</td><td>{v}</td><td>{d}</td></tr>\n" for k, v, d in rows)
    return f"""
<h1>The safety list this week</h1>
<p class="meta">{span}. Updated {generated} from the public repository; the next update is the coming Monday.</p>
<p>These are the numbers behind Verdetto's own part of the warning list: what people reported, what a person reviewed, and what changed on the list. They come from the public case issues and the list files in the repository, nothing else. No telemetry, no per-scan data, nothing from anyone's phone; the app never reports what it scanned, and this page could not show it if it did.</p>
<div class="tablewrap"><table><thead><tr><th>Number</th><th>This week</th><th>What it counts</th></tr></thead><tbody>
{table}</tbody></table></div>
<p>Every case is a public issue, every listing carries the case that caused it, and every entry expires unless a person renews it: <a href="https://github.com/verdettoqr/link-safety-list">github.com/verdettoqr/link-safety-list</a>. Think something is listed by mistake? <a href="{href('report.html')}?k=m">Report it</a>; a person re-checks it and the removal shows up here.</p>
<p class="meta">The weekly numbers are a small file this site serves itself, copied from the repository once a week; your browser makes no request to any third party for this page.</p>
"""


WEEKLY_LD = {"@type": "Dataset", "name": "The safety list this week", "description": "Weekly counts of reports, cases, and list entries for Verdetto's own part of the warning list, from public data.",
             "publisher": ORG, "license": "https://creativecommons.org/publicdomain/zero/1.0/", "isAccessibleForFree": True,
             "distribution": {"@type": "DataDownload", "encodingFormat": "application/json", "contentUrl": SITE + "/stats/weekly.json"}}

DEVELOPERS_LD = {"@type": "TechArticle", "name": "Scanning with Verdetto from another app", "publisher": ORG,
                 "about": "Android intents for scanning QR codes and barcodes and receiving the result"}

KOTLIN_SAMPLE = """private val scan = registerForActivityResult(ActivityResultContracts.StartActivityForResult()) { result ->
    if (result.resultCode == Activity.RESULT_OK) {
        val text = result.data?.getStringExtra("SCAN_RESULT")
        val format = result.data?.getStringExtra("SCAN_RESULT_FORMAT")
        // use text and format
    }
}

fun startScan() {
    val intent = Intent("app.scanner.action.SCAN")
    if (intent.resolveActivity(packageManager) != null) scan.launch(intent)
    else startActivity(Intent(Intent.ACTION_VIEW, Uri.parse(GET_VERDETTO)))
}

// the store page, with the developers referrer
private const val GET_VERDETTO =
    "PLAY_LINK"
"""

QUERIES_SAMPLE = """<queries>
    <intent>
        <action android:name="app.scanner.action.SCAN" />
    </intent>
</queries>
"""

JAVA_SAMPLE = """private final ActivityResultLauncher<Intent> scan = registerForActivityResult(
        new ActivityResultContracts.StartActivityForResult(), result -> {
            if (result.getResultCode() == Activity.RESULT_OK && result.getData() != null) {
                String text = result.getData().getStringExtra("SCAN_RESULT");
                String format = result.getData().getStringExtra("SCAN_RESULT_FORMAT");
                // use text and format
            }
        });

void startScan() {
    Intent intent = new Intent("app.scanner.action.SCAN");
    if (intent.resolveActivity(getPackageManager()) != null) scan.launch(intent);
    else startActivity(new Intent(Intent.ACTION_VIEW, Uri.parse(GET_VERDETTO)));
}
"""

FORMATS_DELIVERED = ("QR_CODE", "MICRO_QR_CODE", "RMQR_CODE", "DATA_MATRIX", "AZTEC", "PDF417", "MAXICODE", "HAN_XIN",
                     "EAN_13", "EAN_8", "UPC_A", "UPC_E", "CODE_128", "CODE_39", "CODE_93", "CODABAR", "ITF",
                     "DATABAR", "DATABAR_EXPANDED", "DATABAR_LIMITED", "DX_FILM_EDGE")


def code_block(text):
    return "<pre><code>" + html.escape(text) + "</code></pre>"


def developers_page():
    """The developers page: the app's INTENT.md (verdetto-android f9f2927) as a web page. The name once per block, the
    domain never (the footer carries it), one link per block (operator, 2026-09-05)."""
    play = play_link("developers", "docs")
    kotlin = KOTLIN_SAMPLE.replace("PLAY_LINK", play)
    formats = ", ".join(f"<code>{f}</code>" for f in FORMATS_DELIVERED)
    return f"""
<div class="prose">
<h1>Scanning from another app</h1>
<p class="meta">Verdetto answers three intents and one share. Nothing here needs a permission, a library, or a key. The person keeps every safety check and every setting of the app; your app receives the text of the code the moment they confirm it.</p>

<h2>The intents</h2>
<table>
<thead><tr><th>Action</th><th>Filter in the manifest</th><th>What happens</th><th>Result</th></tr></thead>
<tbody>
<tr><td><code>com.google.zxing.client.android.SCAN</code></td><td>Yes, implicit intents work.</td><td>Opens the scanner. The first code the person locks on is handed back, as the ZXing Barcode Scanner did it.</td><td><code>RESULT_OK</code> with <code>SCAN_RESULT</code> and <code>SCAN_RESULT_FORMAT</code></td></tr>
<tr><td><code>app.scanner.action.SCAN</code></td><td>Yes.</td><td>Opens the scanner. Started for a result (a result launcher or <code>startActivityForResult</code>) it hands the code back the same way; started plainly it just opens the app on the scanner.</td><td><code>RESULT_OK</code> with the two extras when started for a result</td></tr>
<tr><td><code>app.scanner.action.CARD</code></td><td>No filter: an explicit intent with the package <code>app.scanner.free</code> only.</td><td>Opens the person's own contact card editor, the code they show to share their details. Meant for the app's own widgets and shortcuts; another app may call it, but nothing comes back.</td><td>None</td></tr>
<tr><td><code>android.intent.action.SEND</code> with <code>image/*</code></td><td>Yes.</td><td>Decodes a picture: the app shows the result sheet for the codes in it.</td><td>None</td></tr>
</tbody>
</table>

<p>The person can turn the hand-back off in Settings under "Hand results to other apps" ("When an app asks for a scan, the code goes back to it"), which is on by default. With it off, either scan action opens the scanner as a normal launch and your launcher receives <code>RESULT_CANCELED</code> when the person leaves. Back from the scanner is <code>RESULT_CANCELED</code> too.</p>

<p>No request extras are read today: not <code>SCAN_MODE</code>, <code>SCAN_FORMATS</code>, <code>PROMPT_MESSAGE</code>, <code>SAVE_HISTORY</code>, or any other. The scanner reads every symbology it knows on every call. A code the app's checks flag is still handed back; the person sees the warning first and decides.</p>

<h2>The result</h2>
<ul>
  <li><code>SCAN_RESULT</code> (String): the code's content, exactly the bytes the code carried, decoded as text (UTF-8 where the symbology allows it, the symbology's own character set otherwise).</li>
  <li><code>SCAN_RESULT_FORMAT</code> (String): the symbology in upper case with underscores, the ZXing names where they exist. Delivered today: {formats}, and the other symbologies the app's own decoders add, in the same spelling (the name shown on the result sheet, upper-cased, spaces and hyphens as underscores).</li>
</ul>
<p>Nothing else travels: no image, no location, no history.</p>

<h2>Kotlin</h2>
{code_block(kotlin)}
<p>On Android 11 and later, add the query to your manifest so <code>resolveActivity</code> can see the app:</p>
{code_block(QUERIES_SAMPLE)}

<h2>Java</h2>
{code_block(JAVA_SAMPLE)}

<h2>The ZXing action</h2>
<p>Code written for the ZXing Barcode Scanner keeps working: send <code>com.google.zxing.client.android.SCAN</code> the same way and read the same two extras. If more than one scanner on the phone answers it, the system asks the person which to use; sending the intent to the package <code>app.scanner.free</code> skips that.</p>

<h2>What the person sees</h2>
<p>The scanner opens as it always does, with its own checks. When a code locks, the app hands it back and closes; nothing of yours appears on the screen, and nothing of theirs (history, settings, the safety list) is touched by the call.</p>

<div class="card"><p><strong>Testing on a phone without the app.</strong> The store page with the developers referrer, the same address the fallback in the samples opens: <a href="{play}">Get it on Google Play</a>. The source of this page is the app's own INTENT.md; when the two differ, the app repository is right and this page is behind.</p></div>
</div>
"""


# ---- the home page in eleven languages: one template, one strings table (terminology follows the Play listings) -----
HOME_T = {
 "en": dict(title="Verdetto: QR & Barcode Scanner for Android", desc="See the link before it opens. Free, no ads, no tracking. Made for damaged codes.",
  h1="See the link before it opens.",
  lede="A QR and barcode scanner for Android with no ads and no fake buttons. It shows what a code holds, checks it on your phone, and leaves the decision to you.",
  coming="Coming soon to Google Play", support="Free and ad-free because the people who use it pay for it and pass it on.", support_link="How that works",
  what="What it does",
  cards=[("Look before it opens", "The link, the network name or the contact is shown before anything opens."),
         ("Checked on your phone", "Lookalike names, short links, hidden sign-ins and more, flagged in one line."),
         ("Built for damaged codes", "Faded, torn and badly printed QR codes and barcodes."),
         ("Free, no ads, nothing collected", "Every feature free for everyone, kept that way by the people who use it."),
         ("Works offline", "Every check runs on the phone. One switch turns online lookups off."),
         ("History that is yours", "Searchable, starrable, swipe to delete. Older than 90 days clears itself.")],
  more="Everything it does",
  cards2=[("A warning list on the phone", "Known phishing, scam and sanctions entries, checked on the phone."),
          ("Looks things up", "Products, books, medicines and vehicles from open databases, only if you allow it. {privacy}."),
          ("Made for the hand", "Quick Settings tile, batch mode, left-handed layout, read aloud, eleven languages."),
          ("Works with other apps", "Any app can ask it for a scan and get the code back. ZXing calls still work. {developers}.")],
  privacy="Privacy policy", developers="For developers",
  why="Why another QR scanner",
  why_p="Of the ten most-installed free scanners on Google Play, checked on September 4, 2026, all ten carry ads, and reviews of seven describe a fake button in the ad. Many open a link the moment they read it. Verdetto does neither. It is made by a solo developer in Virginia; write any time: {email}.",
  never="What it will never tell you",
  never_p='That something is safe. "No warnings found" means none of its checks matched; opening is your call. {guide}.', guide="How to check a link yourself",
  alt_warn="The Verdetto result sheet for a QR code that leads to paypa1.com: the address shown before anything opens, a Danger chip reading Imitates paypal.com, and an Open anyway button.",
  alt_calm="The Verdetto result sheet showing a scanned QR code that leads to wikipedia.org, the No warnings found chip, and an Open button that names the site."),
 "es": dict(title="Verdetto: escáner de códigos QR y de barras para Android", desc="Mira el enlace antes de que se abra. Gratis, sin anuncios, sin rastreo. Hecho para códigos dañados.",
  h1="Mira el enlace antes de que se abra.",
  lede="Un escáner de códigos QR y de barras para Android sin anuncios y sin botones falsos. Muestra lo que contiene un código, lo comprueba en tu teléfono y te deja la decisión a ti.",
  coming="Próximamente en Google Play", support="Gratis y sin anuncios porque las personas que lo usan lo pagan y lo pasan a otros.", support_link="Cómo funciona",
  what="Qué hace",
  cards=[("Mira antes de abrir", "El enlace, el nombre de la red o el contacto se muestra antes de que se abra nada."),
         ("Comprobado en tu teléfono", "Nombres parecidos, enlaces cortos, datos de acceso ocultos y más, señalados en una línea."),
         ("Hecho para códigos dañados", "Códigos QR y de barras descoloridos, rotos y mal impresos."),
         ("Gratis, sin anuncios, sin recopilar nada", "Todas las funciones gratis para todos, gracias a las personas que lo usan."),
         ("Funciona sin conexión", "Cada comprobación se hace en el teléfono. Un interruptor apaga las consultas en línea."),
         ("Un historial que es tuyo", "Con búsqueda, favoritos y borrado al deslizar. Lo de más de 90 días se borra solo.")],
  more="Todo lo que hace",
  cards2=[("Una lista de avisos en el teléfono", "Entradas conocidas de phishing, estafas y sanciones, comprobadas en el teléfono."),
          ("Busca información", "Productos, libros, medicamentos y vehículos en bases de datos abiertas, solo si lo permites. {privacy}."),
          ("Hecho para la mano", "Mosaico de ajustes rápidos, modo por lotes, diseño para zurdos, lectura en voz alta, once idiomas."),
          ("Funciona con otras apps", "Cualquier app puede pedirle un escaneo y recibir el código. Las llamadas ZXing siguen funcionando. {developers}.")],
  privacy="Política de privacidad", developers="Para desarrolladores",
  why="Por qué otro escáner de QR",
  why_p="De los diez escáneres gratuitos más instalados en Google Play, comprobados el 4 de septiembre de 2026, los diez llevan anuncios, y las reseñas de siete describen un botón falso en el anuncio. Muchos abren el enlace en cuanto lo leen. Verdetto no hace ninguna de las dos cosas. Lo hace un desarrollador independiente en Virginia; escribe cuando quieras: {email}.",
  never="Lo que nunca te dirá",
  never_p="Que algo es seguro. «No se encontraron avisos» significa que ninguna de sus comprobaciones coincidió; abrir es decisión tuya. {guide}.", guide="Cómo comprobar un enlace tú mismo",
  alt_warn="La hoja de resultado de Verdetto para un código QR que lleva a paypa1.com: la dirección mostrada antes de que se abra nada, un chip de peligro que dice Imita a paypal.com y un botón Abrir de todos modos.",
  alt_calm="La hoja de resultado de Verdetto con un código QR escaneado que lleva a wikipedia.org, el chip No se encontraron avisos y un botón Abrir que nombra el sitio."),
 "fr": dict(title="Verdetto: scanner de codes QR et codes-barres pour Android", desc="Vois le lien avant qu'il ne s'ouvre. Gratuit, sans publicité, sans pistage. Conçu pour les codes abîmés.",
  h1="Vois le lien avant qu'il ne s'ouvre.",
  lede="Un scanner de codes QR et de codes-barres pour Android, sans publicité et sans faux boutons. Il montre ce que contient un code, le vérifie sur ton téléphone et te laisse la décision.",
  coming="Bientôt sur Google Play", support="Gratuit et sans publicité parce que les personnes qui l'utilisent le financent et le font connaître.", support_link="Comment ça marche",
  what="Ce qu'il fait",
  cards=[("Voir avant d'ouvrir", "Le lien, le nom du réseau ou le contact s'affiche avant que rien ne s'ouvre."),
         ("Vérifié sur ton téléphone", "Noms imitant une marque, liens courts, identifiants cachés et plus, signalés en une ligne."),
         ("Conçu pour les codes abîmés", "Codes QR et codes-barres délavés, déchirés ou mal imprimés."),
         ("Gratuit, sans publicité, rien de collecté", "Toutes les fonctions gratuites pour tous, grâce aux personnes qui l'utilisent."),
         ("Fonctionne hors ligne", "Chaque vérification se fait sur le téléphone. Un interrupteur coupe les recherches en ligne."),
         ("Un historique qui est le tien", "Recherche, favoris, suppression d'un glissement. Au-delà de 90 jours, il s'efface tout seul.")],
  more="Tout ce qu'il fait",
  cards2=[("Une liste d'alertes sur le téléphone", "Entrées connues de phishing, d'arnaque et de sanctions, vérifiées sur le téléphone."),
          ("Recherche des informations", "Produits, livres, médicaments et véhicules dans des bases ouvertes, seulement si tu l'autorises. {privacy}."),
          ("Conçu pour la main", "Tuile de réglages rapides, mode par lot, disposition pour gauchers, lecture à voix haute, onze langues."),
          ("Fonctionne avec d'autres applis", "Toute appli peut lui demander un scan et recevoir le code. Les appels ZXing fonctionnent toujours. {developers}.")],
  privacy="Politique de confidentialité", developers="Pour les développeurs",
  why="Pourquoi un scanner QR de plus",
  why_p="Sur les dix scanners gratuits les plus installés sur Google Play, vérifiés le 4 septembre 2026, les dix contiennent de la publicité, et les avis de sept d'entre eux décrivent un faux bouton dans la publicité. Beaucoup ouvrent un lien dès qu'ils l'ont lu. Verdetto ne fait ni l'un ni l'autre. Il est fait par un développeur indépendant en Virginie ; écris quand tu veux : {email}.",
  never="Ce qu'il ne te dira jamais",
  never_p="Que quelque chose est sûr. « Aucune alerte trouvée » signifie qu'aucune de ses vérifications n'a réagi ; ouvrir ou non, c'est ta décision. {guide}.", guide="Comment vérifier un lien toi-même",
  alt_warn="La fiche de résultat Verdetto pour un code QR qui mène à paypa1.com : l'adresse affichée avant que rien ne s'ouvre, une puce Danger « Imite paypal.com » et un bouton Ouvrir quand même.",
  alt_calm="La fiche de résultat Verdetto avec un code QR scanné qui mène à wikipedia.org, la puce « Aucune alerte trouvée » et un bouton Ouvrir qui nomme le site."),
 "de": dict(title="Verdetto: QR- und Barcode-Scanner für Android", desc="Sieh den Link, bevor er sich öffnet. Kostenlos, ohne Werbung, ohne Tracking. Gemacht für beschädigte Codes.",
  h1="Sieh den Link, bevor er sich öffnet.",
  lede="Ein QR- und Barcode-Scanner für Android ohne Werbung und ohne falsche Buttons. Er zeigt, was ein Code enthält, prüft ihn auf deinem Handy und lässt dir die Entscheidung.",
  coming="Bald bei Google Play", support="Kostenlos und werbefrei, weil die Menschen, die die App nutzen, sie bezahlen und weitergeben.", support_link="So funktioniert das",
  what="Was sie kann",
  cards=[("Erst sehen, dann öffnen", "Der Link, der Netzwerkname oder der Kontakt wird gezeigt, bevor sich etwas öffnet."),
         ("Geprüft auf deinem Handy", "Täuschend ähnliche Namen, Kurzlinks, versteckte Anmeldedaten und mehr, in einer Zeile markiert."),
         ("Gemacht für beschädigte Codes", "Verblasste, zerrissene und schlecht gedruckte QR-Codes und Barcodes."),
         ("Kostenlos, ohne Werbung, nichts gesammelt", "Jede Funktion kostenlos für alle, gehalten von den Menschen, die die App nutzen."),
         ("Funktioniert offline", "Jede Prüfung läuft auf dem Handy. Ein Schalter stellt Online-Abfragen ab."),
         ("Ein Verlauf, der dir gehört", "Durchsuchbar, mit Sternen markierbar, zum Löschen wischen. Älter als 90 Tage löscht sich von selbst.")],
  more="Alles, was sie kann",
  cards2=[("Eine Warnliste auf dem Handy", "Bekannte Phishing-, Betrugs- und Sanktionseinträge, geprüft auf dem Handy."),
          ("Schlägt Dinge nach", "Produkte, Bücher, Medikamente und Fahrzeuge aus offenen Datenbanken, nur wenn du es erlaubst. {privacy}."),
          ("Gemacht für die Hand", "Schnelleinstellungen-Kachel, Stapelmodus, Linkshänder-Layout, Vorlesen, elf Sprachen."),
          ("Arbeitet mit anderen Apps", "Jede App kann einen Scan anfordern und den Code zurückbekommen. ZXing-Aufrufe funktionieren weiter. {developers}.")],
  privacy="Datenschutzerklärung", developers="Für Entwickler",
  why="Warum noch ein QR-Scanner",
  why_p="Von den zehn meistinstallierten kostenlosen Scannern bei Google Play, geprüft am 4. September 2026, enthalten alle zehn Werbung, und Bewertungen von sieben beschreiben einen falschen Button in der Werbung. Viele öffnen einen Link, sobald sie ihn gelesen haben. Verdetto tut beides nicht. Die App macht ein einzelner Entwickler in Virginia; schreib jederzeit: {email}.",
  never="Was sie dir nie sagen wird",
  never_p="Dass etwas sicher ist. „Keine Warnungen gefunden“ heißt: Keine ihrer Prüfungen hat angeschlagen; ob du öffnest, entscheidest du. {guide}.", guide="Wie du einen Link selbst prüfst",
  alt_warn="Das Verdetto-Ergebnisblatt für einen QR-Code, der zu paypa1.com führt: die Adresse vor dem Öffnen angezeigt, ein Gefahr-Chip „Imitiert paypal.com“ und ein Button „Trotzdem öffnen“.",
  alt_calm="Das Verdetto-Ergebnisblatt mit einem gescannten QR-Code zu wikipedia.org, dem Chip „Keine Warnungen gefunden“ und einem Öffnen-Button, der die Seite nennt."),
 "pt-BR": dict(title="Verdetto: leitor de QR e código de barras para Android", desc="Veja o link antes de abrir. Grátis, sem anúncios, sem rastreamento. Feito para códigos danificados.",
  h1="Veja o link antes de abrir.",
  lede="Um leitor de QR e código de barras para Android sem anúncios e sem botões falsos. Ele mostra o que um código contém, verifica no seu celular e deixa a decisão com você.",
  coming="Em breve no Google Play", support="Grátis e sem anúncios porque as pessoas que usam pagam por ele e passam adiante.", support_link="Como isso funciona",
  what="O que ele faz",
  cards=[("Veja antes de abrir", "O link, o nome da rede ou o contato aparece antes que qualquer coisa abra."),
         ("Verificado no seu celular", "Nomes parecidos, links curtos, dados de login escondidos e mais, sinalizados em uma linha."),
         ("Feito para códigos danificados", "Códigos QR e de barras desbotados, rasgados e mal impressos."),
         ("Grátis, sem anúncios, nada coletado", "Todos os recursos grátis para todos, mantidos assim pelas pessoas que usam."),
         ("Funciona offline", "Toda verificação roda no celular. Uma chave desliga as consultas online."),
         ("Um histórico que é seu", "Com busca, favoritos e exclusão ao deslizar. O que tem mais de 90 dias se apaga sozinho.")],
  more="Tudo o que ele faz",
  cards2=[("Uma lista de alertas no celular", "Entradas conhecidas de phishing, golpes e sanções, verificadas no celular."),
          ("Consulta informações", "Produtos, livros, medicamentos e veículos em bases de dados abertas, só se você permitir. {privacy}."),
          ("Feito para a mão", "Bloco de configurações rápidas, modo em lote, layout para canhotos, leitura em voz alta, onze idiomas."),
          ("Funciona com outros apps", "Qualquer app pode pedir uma leitura e receber o código. As chamadas ZXing continuam funcionando. {developers}.")],
  privacy="Política de privacidade", developers="Para desenvolvedores",
  why="Por que mais um leitor de QR",
  why_p="Dos dez leitores gratuitos mais instalados no Google Play, verificados em 4 de setembro de 2026, todos os dez têm anúncios, e avaliações de sete descrevem um botão falso no anúncio. Muitos abrem o link no instante em que o leem. O Verdetto não faz nenhuma das duas coisas. Ele é feito por um desenvolvedor independente na Virgínia; escreva quando quiser: {email}.",
  never="O que ele nunca vai te dizer",
  never_p='Que algo é seguro. "Nenhum alerta encontrado" significa que nenhuma das verificações bateu; abrir é decisão sua. {guide}.', guide="Como verificar um link por conta própria",
  alt_warn="A folha de resultado do Verdetto para um código QR que leva a paypa1.com: o endereço mostrado antes que qualquer coisa abra, um chip de perigo dizendo Imita paypal.com e um botão Abrir mesmo assim.",
  alt_calm="A folha de resultado do Verdetto com um código QR lido que leva a wikipedia.org, o chip Nenhum alerta encontrado e um botão Abrir que nomeia o site."),
 "ru": dict(title="Verdetto: сканер QR-кодов и штрихкодов для Android", desc="Увидьте ссылку до того, как она откроется. Бесплатно, без рекламы, без слежки. Создан для повреждённых кодов.",
  h1="Увидьте ссылку до того, как она откроется.",
  lede="Сканер QR-кодов и штрихкодов для Android без рекламы и без поддельных кнопок. Он показывает, что содержит код, проверяет его на вашем телефоне и оставляет решение за вами.",
  coming="Скоро в Google Play", support="Бесплатно и без рекламы, потому что люди, которые им пользуются, платят за него и рассказывают другим.", support_link="Как это устроено",
  what="Что он умеет",
  cards=[("Сначала посмотреть, потом открыть", "Ссылка, имя сети или контакт показываются до того, как что-либо откроется."),
         ("Проверено на вашем телефоне", "Имена-подделки, короткие ссылки, скрытые данные входа и не только, отмечены одной строкой."),
         ("Создан для повреждённых кодов", "Выцветшие, порванные и плохо напечатанные QR-коды и штрихкоды."),
         ("Бесплатно, без рекламы, ничего не собирается", "Все функции бесплатны для всех, и так остаётся благодаря людям, которые им пользуются."),
         ("Работает офлайн", "Каждая проверка выполняется на телефоне. Один переключатель отключает онлайн-запросы."),
         ("История, которая принадлежит вам", "Поиск, избранное, удаление свайпом. Записи старше 90 дней удаляются сами.")],
  more="Всё, что он умеет",
  cards2=[("Список предупреждений на телефоне", "Известные записи фишинга, мошенничества и санкций, проверяемые на телефоне."),
          ("Ищет сведения", "Товары, книги, лекарства и автомобили в открытых базах данных, только если вы разрешите. {privacy}."),
          ("Сделан под руку", "Плитка быстрых настроек, пакетный режим, раскладка для левшей, чтение вслух, одиннадцать языков."),
          ("Работает с другими приложениями", "Любое приложение может запросить сканирование и получить код. Вызовы ZXing по-прежнему работают. {developers}.")],
  privacy="Политика конфиденциальности", developers="Разработчикам",
  why="Зачем ещё один сканер QR",
  why_p="Из десяти самых устанавливаемых бесплатных сканеров в Google Play, проверенных 4 сентября 2026 года, все десять содержат рекламу, а отзывы на семь из них описывают поддельную кнопку в рекламе. Многие открывают ссылку, едва прочитав её. Verdetto не делает ни того, ни другого. Его делает независимый разработчик из Виргинии; пишите в любое время: {email}.",
  never="Чего он никогда вам не скажет",
  never_p="Что что-то безопасно. «Предупреждений не найдено» означает, что ни одна из его проверок не сработала; открывать или нет, решаете вы. {guide}.", guide="Как проверить ссылку самостоятельно",
  alt_warn="Карточка результата Verdetto для QR-кода, ведущего на paypa1.com: адрес показан до открытия, чип «Опасность» с надписью «Имитирует paypal.com» и кнопка «Всё равно открыть».",
  alt_calm="Карточка результата Verdetto с отсканированным QR-кодом, ведущим на wikipedia.org, чипом «Предупреждений не найдено» и кнопкой «Открыть», называющей сайт."),
 "id": dict(title="Verdetto: pemindai QR dan barcode untuk Android", desc="Lihat tautannya sebelum terbuka. Gratis, tanpa iklan, tanpa pelacakan. Dibuat untuk kode yang rusak.",
  h1="Lihat tautannya sebelum terbuka.",
  lede="Pemindai QR dan barcode untuk Android tanpa iklan dan tanpa tombol palsu. Ia menampilkan isi kode, memeriksanya di ponselmu, dan menyerahkan keputusan padamu.",
  coming="Segera hadir di Google Play", support="Gratis dan bebas iklan karena orang-orang yang memakainya membayarnya dan meneruskannya.", support_link="Begini caranya",
  what="Apa yang dilakukannya",
  cards=[("Lihat sebelum membuka", "Tautan, nama jaringan, atau kontak ditampilkan sebelum apa pun terbuka."),
         ("Diperiksa di ponselmu", "Nama mirip, tautan pendek, data masuk tersembunyi, dan lainnya, ditandai dalam satu baris."),
         ("Dibuat untuk kode yang rusak", "Kode QR dan barcode yang pudar, sobek, dan tercetak buruk."),
         ("Gratis, tanpa iklan, tidak ada yang dikumpulkan", "Semua fitur gratis untuk semua orang, dijaga oleh orang-orang yang memakainya."),
         ("Bekerja offline", "Setiap pemeriksaan berjalan di ponsel. Satu sakelar mematikan pencarian online."),
         ("Riwayat milikmu", "Bisa dicari, diberi bintang, digeser untuk dihapus. Yang lebih dari 90 hari terhapus sendiri.")],
  more="Semua yang dilakukannya",
  cards2=[("Daftar peringatan di ponsel", "Entri phishing, penipuan, dan sanksi yang dikenal, diperiksa di ponsel."),
          ("Mencari informasi", "Produk, buku, obat, dan kendaraan dari basis data terbuka, hanya jika kamu mengizinkan. {privacy}."),
          ("Dibuat untuk tangan", "Ubin Setelan Cepat, mode kumpulan, tata letak tangan kiri, dibacakan, sebelas bahasa."),
          ("Bekerja dengan aplikasi lain", "Aplikasi mana pun bisa meminta pemindaian dan menerima kodenya. Panggilan ZXing tetap berfungsi. {developers}.")],
  privacy="Kebijakan privasi", developers="Untuk pengembang",
  why="Mengapa pemindai QR lagi",
  why_p="Dari sepuluh pemindai gratis terbanyak dipasang di Google Play, diperiksa pada 4 September 2026, kesepuluhnya memuat iklan, dan ulasan tujuh di antaranya menggambarkan tombol palsu di iklan. Banyak yang membuka tautan begitu membacanya. Verdetto tidak melakukan keduanya. Dibuat oleh seorang pengembang independen di Virginia; tulislah kapan saja: {email}.",
  never="Yang tidak akan pernah dikatakannya",
  never_p='Bahwa sesuatu itu aman. "Tidak ada peringatan ditemukan" berarti tidak satu pun pemeriksaannya cocok; membuka atau tidak adalah keputusanmu. {guide}.', guide="Cara memeriksa tautan sendiri",
  alt_warn="Lembar hasil Verdetto untuk kode QR yang mengarah ke paypa1.com: alamat ditampilkan sebelum apa pun terbuka, chip Bahaya bertuliskan Meniru paypal.com, dan tombol Buka saja.",
  alt_calm="Lembar hasil Verdetto dengan kode QR terpindai yang mengarah ke wikipedia.org, chip Tidak ada peringatan ditemukan, dan tombol Buka yang menyebut nama situs."),
 "ja": dict(title="Verdetto: Android 向け QR・バーコードスキャナー", desc="開く前にリンクを見る。無料、広告なし、追跡なし。傷んだコードのために作られました。",
  h1="開く前にリンクを見る。",
  lede="広告も偽ボタンもない Android 向け QR・バーコードスキャナー。コードの中身を表示し、端末内でチェックし、判断はあなたに委ねます。",
  coming="Google Play で近日公開", support="無料で広告がないのは、使う人が支え、人に伝えてくれるからです。", support_link="その仕組み",
  what="できること",
  cards=[("開く前に見る", "何かが開く前に、リンク、ネットワーク名、連絡先を表示します。"),
         ("端末内でチェック", "紛らわしい名前、短縮リンク、隠されたログイン情報などを一行で知らせます。"),
         ("傷んだコードのために", "色あせた、破れた、印刷の悪い QR コードやバーコードも読み取ります。"),
         ("無料、広告なし、収集なし", "すべての機能が誰でも無料。使う人の支えで守られています。"),
         ("オフラインで動く", "すべてのチェックは端末内で行われます。スイッチひとつでオンライン検索を切れます。"),
         ("履歴はあなたのもの", "検索、スター、スワイプで削除。90 日を過ぎたものは自動で消えます。")],
  more="できることすべて",
  cards2=[("端末内の警告リスト", "既知のフィッシング、詐欺、制裁のエントリを端末内で照合します。"),
          ("情報を調べる", "公開データベースから製品、本、医薬品、車両を調べます。許可した場合のみ。{privacy}。"),
          ("手のために", "クイック設定タイル、一括モード、左手レイアウト、読み上げ、11 言語。"),
          ("他のアプリと連携", "どのアプリからもスキャンを依頼してコードを受け取れます。ZXing の呼び出しも引き続き使えます。{developers}。")],
  privacy="プライバシーポリシー", developers="開発者向け",
  why="なぜもうひとつの QR スキャナーか",
  why_p="Google Play でインストール数の多い無料スキャナー 10 本を 2026 年 9 月 4 日に確認したところ、10 本すべてに広告があり、7 本のレビューには広告内の偽ボタンが記されていました。多くは読み取った瞬間にリンクを開きます。Verdetto はどちらもしません。バージニア州の個人開発者が作っています。いつでもご連絡ください: {email}。",
  never="決して言わないこと",
  never_p="何かが安全だということ。「警告は見つかりませんでした」は、どのチェックにも該当しなかったという意味で、開くかどうかはあなたの判断です。{guide}。", guide="リンクを自分で確認する方法",
  alt_warn="paypa1.com に向かう QR コードの Verdetto 結果シート。何かが開く前にアドレスが表示され、「paypal.com を模倣」という危険チップと「それでも開く」ボタンがあります。",
  alt_calm="wikipedia.org に向かう読み取り済み QR コードの Verdetto 結果シート。「警告は見つかりませんでした」チップと、サイト名を示す「開く」ボタンがあります。"),
 "zh-Hans": dict(title="Verdetto: Android 的二维码和条形码扫描器", desc="在链接打开前先看清它。免费、无广告、无跟踪。为破损的码而生。",
  h1="在链接打开前先看清它。",
  lede="一款没有广告、没有假按钮的 Android 二维码和条形码扫描器。它显示码里是什么，在你的手机上检查，并把决定权留给你。",
  coming="即将登陆 Google Play", support="免费且无广告，因为使用它的人为它付费并把它传给别人。", support_link="它是如何运作的",
  what="它能做什么",
  cards=[("先看再打开", "在任何东西打开之前，先显示链接、网络名称或联系人。"),
         ("在你的手机上检查", "易混淆的名称、短链接、隐藏的登录信息等，一行标出。"),
         ("为破损的码而生", "褪色、撕破和印刷不良的二维码和条形码。"),
         ("免费、无广告、不收集任何数据", "每项功能对所有人免费，由使用它的人共同维持。"),
         ("离线可用", "每项检查都在手机上完成。一个开关即可关闭在线查询。"),
         ("属于你的历史记录", "可搜索、可加星、滑动即删。超过 90 天的记录会自行清除。")],
  more="它能做的一切",
  cards2=[("手机上的警告名单", "已知的钓鱼、诈骗和制裁条目，在手机上检查。"),
          ("查询信息", "从公开数据库查询商品、图书、药品和车辆，仅在你允许时。{privacy}。"),
          ("为手而设计", "快捷设置磁贴、批量模式、左手布局、朗读、十一种语言。"),
          ("与其他应用协作", "任何应用都可以请求扫描并取回码。ZXing 调用仍然可用。{developers}。")],
  privacy="隐私政策", developers="面向开发者",
  why="为什么还要一个二维码扫描器",
  why_p="在 Google Play 安装量最高的十款免费扫描器中（2026 年 9 月 4 日核查），十款全部带广告，其中七款的评价描述了广告里的假按钮。许多会在读取到链接的瞬间就打开它。Verdetto 两者都不做。它由弗吉尼亚州的一位独立开发者制作；随时来信：{email}。",
  never="它永远不会告诉你的事",
  never_p="说某样东西安全。“未发现警告”意味着它的检查都没有命中；是否打开，由你决定。{guide}。", guide="如何自己检查一个链接",
  alt_warn="Verdetto 对一个指向 paypa1.com 的二维码的结果页：在任何东西打开前显示地址，一枚写着“仿冒 paypal.com”的危险标签，以及一个“仍然打开”按钮。",
  alt_calm="Verdetto 对一个指向 wikipedia.org 的已扫描二维码的结果页，带有“未发现警告”标签和写明网站名称的“打开”按钮。"),
 "hi": dict(title="Verdetto: Android के लिए QR और बारकोड स्कैनर", desc="लिंक खुलने से पहले देखें। मुफ़्त, बिना विज्ञापन, बिना ट्रैकिंग। क्षतिग्रस्त कोड के लिए बना।",
  h1="लिंक खुलने से पहले देखें।",
  lede="Android के लिए एक QR और बारकोड स्कैनर, बिना विज्ञापन और बिना नकली बटन। यह दिखाता है कि कोड में क्या है, उसे आपके फ़ोन पर जाँचता है, और निर्णय आप पर छोड़ता है।",
  coming="Google Play पर जल्द आ रहा है", support="मुफ़्त और विज्ञापन-रहित, क्योंकि इसे इस्तेमाल करने वाले लोग इसका खर्च उठाते हैं और इसे आगे बढ़ाते हैं।", support_link="यह कैसे काम करता है",
  what="यह क्या करता है",
  cards=[("खोलने से पहले देखें", "कुछ भी खुलने से पहले लिंक, नेटवर्क का नाम या संपर्क दिखाया जाता है।"),
         ("आपके फ़ोन पर जाँचा गया", "मिलते-जुलते नाम, छोटे लिंक, छिपी लॉगिन जानकारी और भी बहुत कुछ, एक पंक्ति में चिह्नित।"),
         ("क्षतिग्रस्त कोड के लिए बना", "धुँधले, फटे और खराब छपे QR कोड और बारकोड।"),
         ("मुफ़्त, बिना विज्ञापन, कुछ भी संग्रहित नहीं", "हर सुविधा सभी के लिए मुफ़्त, इसे इस्तेमाल करने वाले लोगों की बदौलत।"),
         ("ऑफ़लाइन काम करता है", "हर जाँच फ़ोन पर होती है। एक स्विच ऑनलाइन लुकअप बंद कर देता है।"),
         ("इतिहास जो आपका है", "खोजने योग्य, स्टार लगाने योग्य, स्वाइप करके हटाएँ। 90 दिन से पुराना अपने आप साफ़ हो जाता है।")],
  more="यह सब कुछ जो यह करता है",
  cards2=[("फ़ोन पर एक चेतावनी सूची", "ज्ञात फ़िशिंग, धोखाधड़ी और प्रतिबंध प्रविष्टियाँ, फ़ोन पर जाँची गईं।"),
          ("जानकारी खोजता है", "खुले डेटाबेस से उत्पाद, किताबें, दवाएँ और वाहन, केवल तब जब आप अनुमति दें। {privacy}।"),
          ("हाथ के लिए बना", "क्विक सेटिंग्स टाइल, बैच मोड, बाएँ हाथ का लेआउट, ज़ोर से पढ़ना, ग्यारह भाषाएँ।"),
          ("अन्य ऐप्स के साथ काम करता है", "कोई भी ऐप इससे स्कैन माँग सकता है और कोड वापस पा सकता है। ZXing कॉल अभी भी काम करते हैं। {developers}।")],
  privacy="गोपनीयता नीति", developers="डेवलपरों के लिए",
  why="एक और QR स्कैनर क्यों",
  why_p="Google Play पर सबसे ज़्यादा इंस्टॉल किए गए दस मुफ़्त स्कैनरों में से, जिनकी जाँच 4 सितंबर 2026 को की गई, सभी दस में विज्ञापन हैं, और सात की समीक्षाएँ विज्ञापन में नकली बटन का वर्णन करती हैं। कई लिंक पढ़ते ही उसे खोल देते हैं। Verdetto इनमें से कुछ भी नहीं करता। इसे वर्जीनिया में एक स्वतंत्र डेवलपर बनाता है; कभी भी लिखें: {email}।",
  never="यह आपको कभी क्या नहीं बताएगा",
  never_p='कि कुछ सुरक्षित है। "कोई चेतावनी नहीं मिली" का मतलब है कि इसकी कोई भी जाँच मेल नहीं खाई; खोलना आपका निर्णय है। {guide}।', guide="लिंक की जाँच स्वयं कैसे करें",
  alt_warn="paypa1.com की ओर ले जाने वाले QR कोड के लिए Verdetto की परिणाम शीट: कुछ भी खुलने से पहले पता दिखाया गया, \"paypal.com की नक़ल\" लिखा खतरे का चिप, और \"फिर भी खोलें\" बटन।",
  alt_calm="wikipedia.org की ओर ले जाने वाले स्कैन किए गए QR कोड के साथ Verdetto की परिणाम शीट, \"कोई चेतावनी नहीं मिली\" चिप और साइट का नाम बताने वाला \"खोलें\" बटन।"),
 "ar": dict(title="Verdetto: قارئ رموز QR والباركود لنظام Android", desc="شاهد الرابط قبل أن يُفتح. مجاني، بلا إعلانات، بلا تتبّع. مصمَّم للرموز المتضررة.",
  h1="شاهد الرابط قبل أن يُفتح.",
  lede="قارئ رموز QR وباركود لنظام Android بلا إعلانات وبلا أزرار زائفة. يعرض ما يحتويه الرمز، ويفحصه على هاتفك، ويترك القرار لك.",
  coming="قريبًا على Google Play", support="مجاني وبلا إعلانات لأن من يستخدمونه يدفعون ثمنه ويمرّرونه لغيرهم.", support_link="كيف يعمل ذلك",
  what="ماذا يفعل",
  cards=[("انظر قبل أن تفتح", "يُعرض الرابط أو اسم الشبكة أو جهة الاتصال قبل أن يُفتح أي شيء."),
         ("مفحوص على هاتفك", "أسماء متشابهة، روابط مختصرة، بيانات تسجيل دخول مخفية وغيرها، مُعلَّمة في سطر واحد."),
         ("مصمَّم للرموز المتضررة", "رموز QR وباركود باهتة أو ممزقة أو سيئة الطباعة."),
         ("مجاني، بلا إعلانات، لا يجمع شيئًا", "كل ميزة مجانية للجميع، ويبقيها كذلك من يستخدمونه."),
         ("يعمل دون اتصال", "كل فحص يجري على الهاتف. مفتاح واحد يوقف عمليات البحث عبر الإنترنت."),
         ("سجلّ يخصّك أنت", "قابل للبحث والتمييز بنجمة والحذف بالسحب. ما يتجاوز 90 يومًا يُمحى من تلقاء نفسه.")],
  more="كل ما يفعله",
  cards2=[("قائمة تحذيرات على الهاتف", "مدخلات تصيّد واحتيال وعقوبات معروفة، تُفحص على الهاتف."),
          ("يبحث عن المعلومات", "المنتجات والكتب والأدوية والمركبات من قواعد بيانات مفتوحة، فقط إذا سمحت بذلك. {privacy}."),
          ("مصمَّم لليد", "بلاطة الإعدادات السريعة، وضع الدُفعات، تخطيط لليد اليسرى، القراءة بصوت عالٍ، إحدى عشرة لغة."),
          ("يعمل مع التطبيقات الأخرى", "يمكن لأي تطبيق أن يطلب منه مسحًا ويستلم الرمز. استدعاءات ZXing ما زالت تعمل. {developers}.")],
  privacy="سياسة الخصوصية", developers="للمطوّرين",
  why="لماذا قارئ QR آخر",
  why_p="من بين أكثر عشرة قارئات مجانية تثبيتًا على Google Play، والتي فُحصت في 4 سبتمبر 2026، تحمل العشرة كلها إعلانات، وتصف مراجعات سبعة منها زرًا زائفًا داخل الإعلان. وكثير منها يفتح الرابط لحظة قراءته. Verdetto لا يفعل أيًّا من الأمرين. يصنعه مطوّر مستقل في فرجينيا؛ اكتب في أي وقت: {email}.",
  never="ما لن يقوله لك أبدًا",
  never_p='إن شيئًا ما آمن. "لم يُعثر على تحذيرات" تعني أن أي فحص من فحوصاته لم يتطابق؛ والفتح قرارك أنت. {guide}.', guide="كيف تفحص رابطًا بنفسك",
  alt_warn="ورقة نتيجة Verdetto لرمز QR يقود إلى paypa1.com: العنوان معروض قبل أن يُفتح أي شيء، وشارة خطر تقول يقلّد paypal.com، وزر افتح على أي حال.",
  alt_calm="ورقة نتيجة Verdetto لرمز QR ممسوح يقود إلى wikipedia.org، مع شارة لم يُعثر على تحذيرات وزر افتح الذي يسمّي الموقع."),
}
HOME_LANGS = [(code, label, "index.html" if code == "en" else f"{code.lower()}.html") for code, label, _ in PRIVACY_LANGS]
HOME_ALTERNATES = [(code, page) for code, _, page in HOME_LANGS] + [("x-default", "index.html")]
for _t in HOME_T.values():
    assert len(_t["desc"]) <= 160, _t["desc"]


def home_body(t, code):
    """The home page from one strings table; links to the policies in the same language, the rest of the site in English."""
    privacy_page = next(p for c, _, p in PRIVACY_LANGS if c == code)
    link = lambda page, label: f'<a href="{href(page)}">{label}</a>'
    icons = ("eye", "warning", "scan", "heart", "offline", "history")
    cards = "".join(f'  <div class="card">{ic(i)}<div><h3>{title}</h3><p>{text}</p></div></div>\n' for i, (title, text) in zip(icons, t["cards"]))
    c2 = t["cards2"]
    texts2 = [c2[0][1], c2[1][1].replace("{privacy}", link(privacy_page, t["privacy"])), c2[2][1],
              c2[3][1].replace("{developers}", link("developers.html", t["developers"]))]
    cards2 = "".join(f'  <div class="card">{ic(i)}<div><h3>{title}</h3><p>{text}</p></div></div>\n'
                     for i, (title, _), text in zip(("shield", "barcode", "scan", "eye"), c2, texts2))
    why_p = t["why_p"].replace("{email}", f'<a href="mailto:{EMAIL}">{EMAIL}</a>')
    never_p = t["never_p"].replace("{guide}", link("check-qr-code-link.html", t["guide"]))
    weekly = weekly_line() if code == "en" else ""
    return f"""
<div class="hero">
  <div>
    <svg class="mark" role="img" aria-label="Verdetto"><use href="#logo"/></svg>
    <h1>{t["h1"]}</h1>
    <p>{t["lede"]}</p>
    <span class="label">{ic('clock')}{t["coming"]}</span>
    <p class="support">{t["support"]} {link("support-the-work.html", t["support_link"])}</p>
  </div>
  <img class="shot" src="screens/result-sheet-warning.webp" width="540" height="1140" alt="{t["alt_warn"]}">
</div>

<h2>{t["what"]}</h2>
<div class="grid">
{cards}</div>
<details class="more"><summary>{t["more"]}</summary>
<div class="grid">
{cards2}</div>
</details>

<h2>{t["why"]}</h2>
<p>{why_p}</p>

<h2>{t["never"]}</h2>
<div class="card callout"><div><p>{never_p}</p></div><img class="shot small" src="screens/result-sheet.webp" width="540" height="1140" alt="{t["alt_calm"]}"></div>
{weekly}
"""


HOME = home_body(HOME_T["en"], "en")


# The community license (a trademark license) is a legal text like the Terms, kept as a fragment: first line "<!-- title | description -->"
_cl_first, COMMUNITY = (HERE / "_legal" / "community-license.html").read_text(encoding="utf-8").split(chr(10), 1)
_cl_m = re.match(r"<!--\s*(.*?)\s*\|\s*(.*?)\s*-->", _cl_first)
COMMUNITY_TITLE, COMMUNITY_DESC = _cl_m.group(1), _cl_m.group(2)
assert len(COMMUNITY_DESC) <= 160, len(COMMUNITY_DESC)

PAGES = {
    "index.html": ("Verdetto: QR & Barcode Scanner for Android", "See the link before it opens. Free, no ads, no tracking. Made for damaged codes.", HOME, APP),
    "privacy.html": ("Privacy policy - Verdetto", "Privacy policy for Verdetto: QR & Barcode Scanner. No accounts, no ads, no analytics. Scanning happens on your phone.", PRIVACY, {"@type": "WebPage", "name": "Privacy policy", "publisher": ORG}),
    "terms.html": ("Terms of use - Verdetto", "Terms of use for Verdetto: QR & Barcode Scanner. What the safety checks are and are not, and that every decision on scanned content is yours.", TERMS, {"@type": "WebPage", "name": "Terms of use", "publisher": ORG}),
    "support.html": ("Help - Verdetto", "Help for Verdetto: QR & Barcode Scanner. How to reach us and answers to common questions.", SUPPORT, FAQ_LD),
    "support-the-work.html": ("Support the work - Verdetto", "How Verdetto stays free with no ads and no tracking: one-time contributions from the people who use it, from $0.99 on Google Play" + (" or through GitHub Sponsors" if SPONSORS_LIVE else "") + ". Nothing is locked.", SUPPORT_WORK, SUPPORT_WORK_LD),
    "check-qr-code-link.html": (GUIDE_TITLE + " - Verdetto", GUIDE_DESC, GUIDE, GUIDE_LD),
    "report.html": ("Report to Verdetto", "Report a scam-looking link, a code the app read wrong, or anything else that isn't right in Verdetto: QR & Barcode Scanner. A person reviews every report.", REPORT, {"@type": "WebPage", "name": "Report to Verdetto", "publisher": ORG}),
    "press.html": ("Press kit - Verdetto", "The one-sentence description, boilerplate, checkable facts, and image assets for writing about Verdetto: QR & Barcode Scanner.", PRESS, {"@type": "WebPage", "name": "Press kit", "publisher": ORG}),
    "safety-list.html": ("The safety list this week - Verdetto", "Weekly numbers from Verdetto's public warning list: reports, cases, entries added after review, removals, totals. Public data only, nothing from anyone's phone.", weekly_page(), WEEKLY_LD),
    "developers.html": ("For developers - Verdetto", "How another Android app opens Verdetto to scan and gets the code back: the intents, the result extras, Kotlin and Java, and what the person sees.", developers_page(), DEVELOPERS_LD),
    "community-license.html": (COMMUNITY_TITLE, COMMUNITY_DESC, COMMUNITY, {"@type": "WebPage", "name": "Verdetto Community License", "publisher": ORG}),
    "404.html": ("Page not found - Verdetto", "That page is not here.", NOT_FOUND, None),
}
PAGE_LANG = {}  # name -> (lang, rtl, alternates) for pages that are not plain English
PAGE_LANG["privacy.html"] = ("en", False, PRIVACY_ALTERNATES)
PAGE_LANG["terms.html"] = ("en", False, TERMS_ALTERNATES)
for _langs, _alternates, _translate in ((PRIVACY_LANGS, PRIVACY_ALTERNATES, privacy_translation), (TERMS_LANGS, TERMS_ALTERNATES, terms_translation)):
    for _code, _label, _page_name in _langs[1:]:
        _title, _desc, _body = _translate(_code)
        PAGES[_page_name] = (_title, _desc, _body, {"@type": "WebPage", "name": _title.split(" - ")[0], "publisher": ORG, "inLanguage": _code})
        PAGE_LANG[_page_name] = (_code, _code == "ar", _alternates)
PAGE_LANG["index.html"] = ("en", False, HOME_ALTERNATES)
for _code, _label, _page in HOME_LANGS[1:]:
    _t = HOME_T[_code]
    PAGES[_page] = (_t["title"], _t["desc"], home_body(_t, _code), {**APP, "inLanguage": _code})
    PAGE_LANG[_page] = (_code, _code == "ar", HOME_ALTERNATES)
BENCH_PUBLISHED = False  # True once the benchmark page is cleared for the live site


def main():
    if BENCH_PUBLISHED:
        import bench
        PAGES["how-we-test.html"] = bench.page_entry()
        NAV.append(("how-we-test.html", "Tests"))
    for name, (title, desc, body, ld) in PAGES.items():
        lang, rtl, alternates = PAGE_LANG.get(name, ("en", False, None))
        html = page(name, title.replace("&", "&amp;"), desc.replace("&", "&amp;"), body, ld, "article" if name.startswith("check") else "website",
                    lang=lang, rtl=rtl, alternates=alternates)
        (HERE / name).write_text(html, encoding="utf-8", newline="\n")
        print("wrote", name)

    AI_CRAWLERS = ("GPTBot", "OAI-SearchBot", "ChatGPT-User", "ClaudeBot", "Claude-SearchBot", "PerplexityBot", "Google-Extended",
                   "Applebot-Extended", "CCBot", "Bingbot")
    (HERE / "robots.txt").write_text(
        "User-agent: *\nAllow: /\n\n# AI crawlers and answer engines are welcome: these pages are written to be read and cited.\n"
        + "".join(f"User-agent: {b}\nAllow: /\n\n" for b in AI_CRAWLERS)
        + f"Sitemap: {SITE}/sitemap.xml\n", encoding="utf-8", newline="\n")
    urls = [n for n in PAGES if n != "404.html"]
    # llms.txt: the site in Markdown for language models, per the llms.txt convention
    (HERE / "llms.txt").write_text(
        "# Verdetto\n\n"
        "> Verdetto is a free QR code and barcode scanner for Android with no ads and no fake buttons. It shows the link "
        "before it opens, is built to read damaged codes, and checks scanned content for warning signs on the phone. It never says "
        "anything is safe: \"No warnings found\" means none of its checks matched.\n\n"
        f"Publisher: Verdetto, Virginia, United States. Contact: {EMAIL}. Store title: \"Verdetto: QR & Barcode Scanner\". "
        "Status: coming soon to Google Play. Verdetto and the Verdetto QR mark are trademarks; a United States application for VERDETTO is pending (serial no. 50092495).\n\n"
        "Official accounts: " + "; ".join(f"{k} {v}" for k, v in SOCIAL.items()) + ". Pronounced ver-DET-oh; Italian for verdict.\n\n"
        "## Pages\n\n"
        + "".join(f"- [{t.replace(' - Verdetto', '')}]({url(n)}): {d}\n" for n, (t, d, _, _) in PAGES.items() if n != "404.html")
        + "\n## Facts\n\n"
        "- Platform: Android. Price: free. Ads: none. Accounts: none. Analytics: none.\n"
        "- Scanning and every built-in check run on the phone; online lookups (list updates, shortened- and affiliate-link destinations, "
        "domain age, and product, book, medicine, music, journal, device, and vehicle details from Open Food Facts, Open Library, the German and "
        "French national libraries, openFDA, DailyMed and RxNav, Spain's medicines agency AEMPS, the European Commission's EUDAMED, the US Consumer Product Safety Commission's recalls, MusicBrainz, Crossref, Wikidata, the NHTSA vehicle, recall, and crash-test databases, and the EPA fuel-economy database) are on by default and can be turned off.\n"
        "- Reads QR codes and barcodes including EAN, UPC, Code 128, Data Matrix, PDF417, and Aztec, and is built to read damaged ones.\n"
        "- Scan history stays on the phone (and in the phone's own backup unless that is turned off); scans older than 90 days clear unless starred; any entry can be deleted.\n"
        "- Permissions: the camera to scan; contacts only if the person fills their own card from the phone's profile.\n"
        "- Funding: no ads, no data sales, no paid tier; paid for and passed on by the people who use it. An optional one-time in-app contribution, from $0.99 ($2.99 suggested) through Google Play, supports development"
        + (", and GitHub Sponsors (https://github.com/sponsors/verdettoqr) is the browser route" if SPONSORS_LIVE else "")
        + "; nothing is locked behind it. The app never nags; after it does something for you it may say thank you, at most once a month, and a switch turns that off. Verdetto is a small business; a contribution is a purchase, not a gift, and brings no tax benefit.\n",
        encoding="utf-8", newline="\n")
    (HERE / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "".join(f"  <url><loc>{url(n)}</loc><lastmod>{DATE}</lastmod></url>\n" for n in urls) + "</urlset>\n",
        encoding="utf-8", newline="\n")
    (HERE / "CNAME").write_text("verdettoqr.com\n", encoding="utf-8", newline="\n")
    print("wrote robots.txt, sitemap.xml, llms.txt, CNAME")


if __name__ == "__main__":
    main()
