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
PLAY_ID = "com.verdettoqr.scanner"  # the app's applicationId (app/build.gradle.kts)


def play_link(source, medium="app", campaign=None):
    """The Play listing link, plain. No referrer tags anywhere (operator's delegated decision through Counsel, 2026-09-05): the
    app classes utm parameters as tracking and shows "Tracking removed", so no Verdetto link may carry them, on the site, in
    posts, in the press kit or in the app; Play Console's acquisition report still shows referring sites by host. The
    arguments are kept so callers read as before; they change nothing."""
    return f"https://play.google.com/store/apps/details?id={PLAY_ID}"

DATE = "2026-09-05"  # lastmod for the sitemap and the article; update when copy changes
POLICY_DATE = "2026-09-05"  # effective date of the privacy policy and the Terms: the dated copies are named by it, not by the build date; bump it with the eleven date lines when the policy text changes
# the formats the validation matrix of 2026-09-04 read (scanner-app SCAN-VALIDATION.md, 31 formats, all reads correct); the
# page renders the count from this list so the number cannot drift from the evidence
FORMATS_READ = ["EAN-13", "EAN-8", "UPC-A", "UPC-E", "ISBN", "GS1 DataBar", "DataBar Limited", "DataBar Stacked", "DataBar Stacked Omni", "DataBar Expanded", "DataBar Expanded Stacked", "Code 128", "Code 39", "Code 93", "Codabar", "ITF", "ITF-14", "Telepen", "MaxiCode", "PZN", "Code 32", "QR Code", "Micro QR", "rMQR", "Aztec", "Aztec Rune", "Data Matrix", "PDF417", "Compact PDF417", "MicroPDF417", "DX film edge"]
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
:root{--mark-body:#003D35;--mark-accent:#B8650A;--surface:#E9F5F1;--on-surface:#191C1B;--on-surface-variant:#3F4946;--primary:#006B5E;--on-primary:#FFFFFF;--surface-container:#D5E8E3;--surface-container-high:#CFE2DC;--primary-container:#74F8E4;--on-primary-container:#00201C;--outline:#6F7977;--outline-variant:#B4CAC4;--tertiary:#8A5A00;--on-tertiary:#FFFFFF}
@media (prefers-color-scheme:dark){:root{--mark-body:#FFFFFF;--mark-accent:#FFB95A;--surface:#0F1312;--on-surface:#DFE4E1;--on-surface-variant:#BEC9C5;--primary:#54DBC8;--on-primary:#003731;--surface-container:#1C201F;--surface-container-high:#262B29;--primary-container:#005047;--on-primary-container:#74F8E4;--outline:#899390;--outline-variant:#3F4946;--tertiary:#FFB95A;--on-tertiary:#462A00}}
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
.wrap.narrow{max-width:36rem}
.draft{background:var(--tertiary);color:var(--on-tertiary);text-align:center;padding:.4rem;font-size:.875rem;line-height:1.25rem;font-weight:500;letter-spacing:.01em}
header{border-bottom:1px solid var(--outline-variant)}
header .wrap{display:flex;align-items:center;gap:.75rem;min-height:64px;padding-top:.5rem;padding-bottom:.5rem;flex-wrap:wrap}
.brand{display:inline-flex;align-items:center;gap:.4rem;color:var(--on-surface);text-decoration:none;font-weight:500;font-size:1.375rem;line-height:1.75rem}
.brand svg{width:.78em;height:.78em;flex:none}
.lockup{white-space:nowrap}.lockup svg{width:.78em;height:.78em;vertical-align:-.04em;margin-inline-end:.3em}
nav{margin-left:auto;display:flex;gap:.25rem;flex-wrap:wrap}
nav a{color:var(--on-surface-variant);text-decoration:none;font-weight:500;font-size:.875rem;line-height:1.25rem;padding:.6rem .75rem;border-radius:20px}
nav a:hover{background:var(--surface-container)}
.lang{position:relative;margin-inline-start:.25rem}.lang summary{list-style:none;display:inline-flex;align-items:center;gap:.4rem;padding:.6rem .75rem;border-radius:20px;color:var(--on-surface-variant);font-weight:500;font-size:.875rem;line-height:1.25rem;cursor:pointer;position:relative}.lang summary::-webkit-details-marker{display:none}.lang summary::after{content:"";position:absolute;inset:-5px 0}.lang summary svg{width:20px;height:20px;fill:none;stroke:currentColor;stroke-width:1.8;stroke-linecap:round;stroke-linejoin:round}.lang summary:hover,.lang[open] summary{background:var(--surface-container)}.lang .menu{position:absolute;inset-inline-end:0;top:calc(100% + 4px);margin:0;padding:.5rem 0;list-style:none;min-width:12.5rem;background:var(--surface-container);border-radius:4px;box-shadow:0 1px 3px rgba(0,0,0,.3),0 4px 8px 3px rgba(0,0,0,.15);z-index:4}.lang .menu a{display:flex;align-items:center;min-height:48px;padding:0 .75rem;color:var(--on-surface);text-decoration:none;font-size:.875rem;line-height:1.25rem}.lang .menu a:hover{background:var(--surface-container-high)}.langs404{columns:2;column-gap:2rem;padding-inline-start:1.25rem}.langs404 li{margin:.25rem 0}.lang .menu a[aria-current]{color:var(--primary);font-weight:600}
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
.grid .card{margin:0;padding:1rem;background:var(--surface-container);border-radius:12px;display:grid;grid-template-columns:auto 1fr;column-gap:1rem;row-gap:.75rem;align-items:start}
.grid .card>svg{width:40px;height:40px;padding:8px;box-sizing:border-box;border-radius:12px;background:var(--primary-container);color:var(--on-primary-container)}
.grid .card.soon{background:transparent;border:1px solid var(--outline-variant)}
.grid .card.soon>svg{background:var(--surface-container-high);color:var(--on-surface-variant)}
.grid h3{margin:0 0 .25rem;color:var(--on-surface);font-size:1rem;line-height:1.5rem;font-weight:500}
.grid p{margin:0;font-size:.875rem;line-height:1.25rem;color:var(--on-surface-variant)}
.grid .card .label{margin:0 0 .25rem;font-size:.75rem;line-height:1rem;font-weight:500;letter-spacing:.03em;color:var(--on-surface-variant)}
.callout{background:var(--surface-container-high);border-left:4px solid var(--primary);border-radius:0 12px 12px 0;display:grid;grid-template-columns:1fr auto;gap:1rem;align-items:center}.callout .shot.small{width:120px;margin:0}nav a,.more summary{position:relative}nav a::after,.more summary::after{content:"";position:absolute;inset:-5px 0}
.faq p strong{color:var(--on-surface);font-weight:500}
.faq h3{margin:1.5rem 0 .25rem}.faq h3+p{margin:0}
.prose ol,.prose ul{padding-left:1.4rem}
.prose li{margin:.6rem 0}
table{border-collapse:collapse;width:100%;font-size:.875rem;line-height:1.25rem;display:block;overflow-x:auto;margin:1rem 0}
.prose table{display:table;table-layout:fixed}.prose th,.prose td{overflow-wrap:anywhere;vertical-align:top}.prose th:nth-child(1){width:27%}.prose th:nth-child(2){width:18%}.prose th:nth-child(3){width:37%}.prose th:nth-child(4){width:18%}
pre{background:var(--container);border-radius:.5rem;padding:.9rem 1rem;overflow-x:auto;font-size:.8125rem;line-height:1.35rem;margin:1rem 0}
code{font-family:Consolas,'Cascadia Mono',Menlo,monospace;font-size:.92em}
pre code{font-size:inherit}
th,td{text-align:left;vertical-align:top;padding:.5rem .6rem;border-bottom:1px solid var(--outline-variant)}
th{color:var(--on-surface-variant);font-weight:500;white-space:nowrap}
td:first-child{min-width:12rem}
p.langs{font-size:.8125rem;line-height:1.5;color:var(--on-surface-variant)}p.langs a[aria-current]{font-weight:600;text-decoration:none}
details.more{margin:1rem 0}details.more summary{cursor:pointer;color:var(--primary);font-weight:500;font-size:.875rem;line-height:1.25rem;padding:.6rem .75rem;border-radius:20px;display:inline-block;background:var(--surface-container)}details.more[open] summary{margin-bottom:.5rem}
footer{background:var(--surface-container);margin-top:2rem}
footer .wrap{padding:1.5rem 1rem 2rem;color:var(--on-surface-variant);font-size:.875rem;line-height:1.25rem;display:grid;grid-template-columns:1fr auto;gap:1rem 2rem;align-items:start}footer .code{display:block;margin-top:.25rem}footer .code img{display:block;width:96px;height:96px}
footer a{color:var(--primary)}
.feature{display:grid;grid-template-columns:1fr 220px;gap:2rem;align-items:start;padding:1.75rem 0;border-top:1px solid var(--outline-variant)}.feature.text{grid-template-columns:1fr}.feature h2{border-top:0;margin:0 0 .5rem;padding-top:0}.feature .shot{width:220px;margin:0}.feature p{margin:.5rem 0}.feature .kicker{margin:0 0 .25rem;font-size:.875rem;line-height:1.25rem;font-weight:500;letter-spacing:.03em;color:var(--primary)}.tags{display:flex;flex-wrap:wrap;gap:.5rem;margin:.75rem 0 0;padding:0;list-style:none}.tags li{margin:0;padding:.25rem .75rem;border:1px solid var(--outline-variant);border-radius:8px;font-size:.875rem;line-height:1.25rem;color:var(--on-surface)}.feature .label{display:inline-flex;align-items:center;gap:.4rem;margin-top:.75rem;color:var(--on-surface-variant);font-weight:500;font-size:.875rem;line-height:1.25rem}.feature .label svg{width:18px;height:18px}
@media (min-width:640px){.grid{grid-template-columns:1fr 1fr}.grid .card{grid-template-columns:1fr}.grid.three{grid-template-columns:1fr}.grid.three .card{grid-template-columns:auto 1fr}}
@media (max-width:600px){.feature{grid-template-columns:1fr}.feature .shot{margin:0 auto}.hero{grid-template-columns:1fr}.shot{width:220px;margin:0 auto}h1,.hero h1{font-size:1.75rem;line-height:2.25rem}nav{margin-left:0;width:100%;order:3}.lang{margin-inline-start:auto;order:2}.callout{grid-template-columns:1fr}.callout .shot.small{margin:0 auto}}
@media print{.draft,.skip,nav,footer .links{display:none}body{background:#fff;color:#000;font-size:12pt}a{color:#000}h2{color:#000;border-top-color:#999}.card,.callout{background:#f2f2f2}}
"""


def href(name):
    if not PUBLISH:
        return name
    return "/" if name == "index.html" else "/" + name[:-5]


def url(name):
    return SITE + ("/" if name == "index.html" else "/" + name[:-5])


NAV = [("features.html", "features"), ("support.html", "help"), ("check-qr-code-link.html", "guide"), ("support-the-work.html", "support_work")]
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


FOOTER = [("privacy.html", "privacy"), ("terms.html", "terms"), ("support.html", "help"), ("features.html", "features"), ("check-qr-code-link.html", "guide_long"),
          ("support-the-work.html", "support_work"), ("report.html", "report"), ("safety-list.html", "safety"), ("developers.html", "developers"),
          ("press.html", "press")]


def footer_links(lang):
    t = chrome(lang)
    return " &middot; ".join(f'<a href="{href(localized(pg, lang))}">{t[key]}</a>' for pg, key in FOOTER)


# Text pages read at a 36rem measure (about 74 characters); pages with side-by-side layouts or wide tables keep 44rem.
NARROW = ("privacy", "terms", "support", "check-qr-code-link", "press", "report", "community-license", "safety-list")


def page(name, title, description, body, ld=None, og_type="website", nav_key=None, lang="en", rtl=False, alternates=None):
    t = chrome(lang)
    nav = "".join(f'<a href="{href(localized(h, lang))}"{" aria-current=\"page\"" if localized(h, lang) == name else ""}>{t.get(key, CHROME["en"].get(key, key))}</a>' for h, key in NAV)
    # the language control is part of the top app bar on every page; a page without a translation offers the home pages
    menu = lang_menu(alternates or HOME_ALTERNATES, lang)
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
<link rel="icon" href="/favicon.ico" sizes="16x16 32x32 48x48">
<link rel="icon" href="/icon.svg" type="image/svg+xml">
<link rel="icon" href="/favicon-48.png" sizes="48x48" type="image/png">
<link rel="icon" href="/favicon-96.png" sizes="96x96" type="image/png">
<link rel="icon" href="/icon-192.png" sizes="192x192" type="image/png">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
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
<a class="skip" href="#main">{t["skip"]}</a>
{banner}{SYMBOLS}
<header><div class="wrap">
  <a class="brand" href="{href(localized('index.html', lang))}"><svg aria-hidden="true"><use href="#mark"/></svg>Verdetto</a>
  <nav aria-label="Site">{nav}</nav>{menu}
</div></header>
<main id="main"><div class="wrap{" narrow" if name.startswith(NARROW) else ""}">
{body}
</div></main>
<footer><div class="wrap"><div>
  <p>&copy; 2026 <span class="lockup"><svg aria-hidden="true"><use href="#mark"/></svg>Verdetto</span> &middot; <a href="mailto:{EMAIL}">{EMAIL}</a></p>
  <p class="links">{footer_links(lang)}</p>
  <p class="links">{t["where"]} {SOCIAL_LINKS}</p>
</div><a class="code" href="{href(localized('index.html', lang))}"><picture><source srcset="verdetto-code-dark.svg" media="(prefers-color-scheme: dark)"><img src="verdetto-code-light.svg" width="96" height="96" alt="{t["code_alt"]}" loading="lazy"></picture></a></div></footer>
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
# The community license follows the same route (operator, 2026-09-05: every page that shows the language menu is translated).
COMMUNITY_LANGS = [(code, label, page_name.replace("privacy", "community-license")) for code, label, page_name in PRIVACY_LANGS]
COMMUNITY_ALTERNATES = [(code, page_name) for code, _, page_name in COMMUNITY_LANGS] + [("x-default", "community-license.html")]


def lang_row(langs, current):
    links = " &middot; ".join(
        f'<a href="{href(page_name)}" lang="{code}" hreflang="{code}"{" aria-current=\"page\"" if code == current else ""}>{label}</a>'
        for code, label, page_name in langs)
    return f'<p class="langs" aria-label="This page in other languages">{links}</p>'


def privacy_lang_row(current):
    return lang_row(PRIVACY_LANGS, current)


LANG_LABELS = {code: label for code, label, _ in PRIVACY_LANGS}
LANG_CODES = [code for code, _, _ in PRIVACY_LANGS]  # English first, then the ten

# the site chrome (skip link, nav, footer, the language control) in the page's own language
CHROME = {
 "en": {
  "skip": "Skip to content",
  "help": "Help",
  "guide": "Guide",
  "support_work": "Support the work",
  "privacy": "Privacy policy",
  "terms": "Terms of use",
  "guide_long": "How to check a QR code link",
  "report": "Report a problem",
  "safety": "The safety list this week",
  "developers": "For developers",
  "press": "Press kit",
  "code_alt": "QR code that opens verdettoqr.com",
  "features": "Features",
  "where": "Where to find us:",
  "language": "Language",
  "tests": "Tests"
 },
 "de": {
  "skip": "Zum Inhalt springen",
  "help": "Hilfe",
  "guide": "Anleitung",
  "support_work": "Die Arbeit unterstützen",
  "privacy": "Datenschutzerklärung",
  "terms": "Nutzungsbedingungen",
  "guide_long": "Wie du einen QR-Code-Link prüfst",
  "report": "Ein Problem melden",
  "safety": "Die Sicherheitsliste diese Woche",
  "developers": "Für Entwickler",
  "press": "Pressematerial",
  "code_alt": "QR-Code, der verdettoqr.com öffnet",
  "features": "Funktionen",
  "where": "Hier findest du uns:",
  "language": "Sprache"
 },
 "es": {
  "skip": "Saltar al contenido",
  "help": "Ayuda",
  "guide": "Guía",
  "support_work": "Apoya el trabajo",
  "privacy": "Política de privacidad",
  "terms": "Condiciones de uso",
  "guide_long": "Cómo comprobar un enlace de código QR",
  "report": "Informar de un problema",
  "safety": "La lista de seguridad esta semana",
  "developers": "Para desarrolladores",
  "press": "Kit de prensa",
  "code_alt": "Código QR que abre verdettoqr.com",
  "features": "Funciones",
  "where": "Dónde encontrarnos:",
  "language": "Idioma"
 },
 "fr": {
  "skip": "Aller au contenu",
  "help": "Aide",
  "guide": "Guide",
  "support_work": "Soutenir le travail",
  "privacy": "Politique de confidentialité",
  "terms": "Conditions d'utilisation",
  "guide_long": "Comment vérifier le lien d'un code QR",
  "report": "Signaler un problème",
  "safety": "La liste de sécurité cette semaine",
  "developers": "Pour les développeurs",
  "press": "Kit presse",
  "code_alt": "Code QR qui ouvre verdettoqr.com",
  "features": "Fonctions",
  "where": "Où nous trouver :",
  "language": "Langue"
 },
 "pt-BR": {
  "skip": "Pular para o conteúdo",
  "help": "Ajuda",
  "guide": "Guia",
  "support_work": "Apoie o trabalho",
  "privacy": "Política de privacidade",
  "terms": "Termos de uso",
  "guide_long": "Como verificar o link de um código QR",
  "report": "Relatar um problema",
  "safety": "A lista de segurança nesta semana",
  "developers": "Para desenvolvedores",
  "press": "Kit de imprensa",
  "code_alt": "Código QR que abre verdettoqr.com",
  "features": "Recursos",
  "where": "Onde nos encontrar:",
  "language": "Idioma"
 },
 "id": {
  "skip": "Lompat ke konten",
  "help": "Bantuan",
  "guide": "Panduan",
  "support_work": "Dukung pekerjaan ini",
  "privacy": "Kebijakan privasi",
  "terms": "Ketentuan penggunaan",
  "guide_long": "Cara memeriksa tautan kode QR",
  "report": "Laporkan masalah",
  "safety": "Daftar keamanan minggu ini",
  "developers": "Untuk pengembang",
  "press": "Kit pers",
  "code_alt": "Kode QR yang membuka verdettoqr.com",
  "features": "Fitur",
  "where": "Temukan kami di:",
  "language": "Bahasa"
 },
 "ru": {
  "skip": "Перейти к содержимому",
  "help": "Помощь",
  "guide": "Руководство",
  "support_work": "Поддержать работу",
  "privacy": "Политика конфиденциальности",
  "terms": "Условия использования",
  "guide_long": "Как проверить ссылку из QR-кода",
  "report": "Сообщить о проблеме",
  "safety": "Список безопасности за неделю",
  "developers": "Разработчикам",
  "press": "Пресс-кит",
  "code_alt": "QR-код, открывающий verdettoqr.com",
  "features": "Возможности",
  "where": "Где нас найти:",
  "language": "Язык"
 },
 "hi": {
  "skip": "सामग्री पर जाएँ",
  "help": "सहायता",
  "guide": "गाइड",
  "support_work": "काम का समर्थन करें",
  "privacy": "गोपनीयता नीति",
  "terms": "उपयोग की शर्तें",
  "guide_long": "QR कोड लिंक की जाँच कैसे करें",
  "report": "समस्या की रिपोर्ट करें",
  "safety": "इस सप्ताह की सुरक्षा सूची",
  "developers": "डेवलपरों के लिए",
  "press": "प्रेस किट",
  "code_alt": "QR कोड जो verdettoqr.com खोलता है",
  "features": "सुविधाएँ",
  "where": "हमें यहाँ पाएँ:",
  "language": "भाषा"
 },
 "ja": {
  "skip": "本文へ移動",
  "help": "ヘルプ",
  "guide": "ガイド",
  "support_work": "活動を支援",
  "privacy": "プライバシーポリシー",
  "terms": "利用規約",
  "guide_long": "QR コードのリンクを確認する方法",
  "report": "問題を報告",
  "safety": "今週の安全リスト",
  "developers": "開発者向け",
  "press": "プレスキット",
  "code_alt": "verdettoqr.com を開く QR コード",
  "features": "機能",
  "where": "公式アカウント:",
  "language": "言語"
 },
 "zh-Hans": {
  "skip": "跳到内容",
  "help": "帮助",
  "guide": "指南",
  "support_work": "支持这项工作",
  "privacy": "隐私政策",
  "terms": "使用条款",
  "guide_long": "如何检查二维码链接",
  "report": "报告问题",
  "safety": "本周安全名单",
  "developers": "面向开发者",
  "press": "媒体资料",
  "code_alt": "打开 verdettoqr.com 的二维码",
  "features": "功能",
  "where": "在这里找到我们：",
  "language": "语言"
 },
 "ar": {
  "skip": "الانتقال إلى المحتوى",
  "help": "المساعدة",
  "guide": "الدليل",
  "support_work": "ادعم العمل",
  "privacy": "سياسة الخصوصية",
  "terms": "شروط الاستخدام",
  "guide_long": "كيف تفحص رابط رمز QR",
  "report": "الإبلاغ عن مشكلة",
  "safety": "قائمة السلامة هذا الأسبوع",
  "developers": "للمطوّرين",
  "press": "ملف الصحافة",
  "code_alt": "رمز QR يفتح verdettoqr.com",
  "features": "الميزات",
  "where": "أين تجدنا:",
  "language": "اللغة"
 }
}


def chrome(lang):
    return CHROME.get(lang, CHROME["en"])


def family_pages(base):
    """The page names of one translated family: support.html -> support-de.html, support-pt-br.html, ..."""
    return {code: (base if code == "en" else f"{base[:-5]}-{code.lower()}.html") for code in LANG_CODES}


# every translated family registers its pages here; the chrome links to the same-language page when one exists
LOCAL = {"privacy.html": {c: pg for c, _, pg in PRIVACY_LANGS}, "terms.html": {c: pg for c, _, pg in TERMS_LANGS},
         "community-license.html": {c: pg for c, _, pg in COMMUNITY_LANGS}}


def localized(page_name, code):
    return LOCAL.get(page_name, {}).get(code, page_name)


def alternates_for(base):
    return [(code, pg) for code, pg in LOCAL[base].items()] + [("x-default", base)]


def lang_menu(alternates, current):
    """The top app bar's language control: the current language behind a globe, opening a menu of the page's alternates.
    A details element, so it needs no script; each item is a 48 px row; the current language is marked."""
    items = "".join(
        f'<li><a href="{href(page_name)}" lang="{code}" hreflang="{code}"{" aria-current=\"page\"" if code == current else ""}>{LANG_LABELS[code]}</a></li>'
        for code, page_name in alternates if code != "x-default")
    return (f'<details class="lang"><summary aria-label="{chrome(current)["language"]}: {LANG_LABELS[current]}">{ic("language")}<span>{LANG_LABELS[current]}</span></summary>'
            f'<ul class="menu">{items}</ul></details>')


def earlier_versions(stem):
    """Links to the dated copies of a policy page on disk, oldest first, excluding today's copy: the Changes sections list them."""
    names = sorted(x.name for x in HERE.glob(f"{stem}-20??-??-??.html") if not x.name.endswith(f"-{POLICY_DATE}.html"))
    return ", ".join(f'<a href="{href(n)}">{n[len(stem) + 1:-5]}</a>' for n in names) or "none yet"


def dated_copy(name, html):
    """A policy page saved under its date, not indexed, canonical to the live page: the archive the Changes sections promise."""
    stem = name[:-5]
    copy = html.replace('<link rel="canonical"', '<meta name="robots" content="noindex">\n<link rel="canonical"', 1)
    (HERE / f"{stem}-{POLICY_DATE}.html").write_text(copy, encoding="utf-8", newline="\n")


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
            .replace("{COMMUNITY_HREF}", href(localized("community-license.html", code)))
            .replace("{EARLIER}", earlier_versions(next(pg for c, _, pg in langs if c == code)[:-5])))
    return title, desc, body


def privacy_translation(code):
    return translation("_privacy", PRIVACY_LANGS, code)


def community_translation(code):
    return translation("_legal/community-license", COMMUNITY_LANGS, code)


def terms_translation(code):
    return translation("_terms", TERMS_LANGS, code)


PRIVACY = f"""
<h1>Privacy policy</h1>
<p class="meta">For Verdetto: QR &amp; Barcode Scanner, the Android app published by Verdetto. Effective date: September 5, 2026.</p>

<div class="card"><p><strong>In short.</strong> No accounts, no ads, no analytics. Scanning happens on your phone, and an ID or license scan never leaves it. With online lookups on, the default, only the address, domain, or number you scanned goes out, to the services in the table below, and it goes straight from your phone to them, never through us. Nothing else leaves the phone, apart from your phone's own backup, which you can turn off. Apart from Google Play's own grouped counts of installs, ratings, and crashes, the only things we ever receive are an email or a report you choose to send us and, if you contribute, Google's order record without your name. Beyond those, we do not collect, store, sell, or share any data about you. This website sets no cookies.</p></div>

<h2>Who we are</h2>
<p>Verdetto, {ADDRESS}, United States, a small business in Virginia. Contact: <a href="mailto:{EMAIL}">{EMAIL}</a>. Verdetto publishes the app and is the party responsible for this policy wherever a law asks for one. The app sends us nothing, and the one thing we process is the email you may send us, so we have not appointed a representative in the European Union or the United Kingdom or a data protection officer; that email address reaches the person who answers.</p>

<h2>What the app does on your phone</h2>
<ul>
  <li><strong>Camera.</strong> Camera frames are read on the phone to find and decode codes. They are not stored and not uploaded.</li>
  <li><strong>Images you choose.</strong> If you pick an image from your photos, it is read on the phone the same way and is not uploaded.</li>
  <li><strong>Scan history.</strong> Decoded content is kept in a history on your phone so you can find it again. Scans older than 90 days are cleared on their own unless you star them; Settings lets you choose 30, 90, or 365 days, or forever. You can delete any entry with a swipe, or clear the whole history, in the app. Driver's licenses, boarding passes, and health certificates are read on the phone, shown once, and never kept.</li>
  <li><strong>Safety checks.</strong> The app inspects scanned content on the phone for warning signs and compares links, sites, and wallet addresses with a list of known phishing, malware, scam, and sanctions entries that is stored on the phone. The comparison never sends what you scanned anywhere.</li>
  <li><strong>Settings.</strong> Your preferences are stored on the phone.</li>
</ul>
<p>Lookup answers are kept on the phone for a day (a shortened link's destination) or a week (a domain's age) so the same question is not asked twice; if you turn on recording under About, Performance, frame and scan timings are kept on the phone and nothing leaves.</p>

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
<p>Actions you choose on a result, such as open, share, search, copy, add a contact, join Wi-Fi, or save an event, hand the content to the app you pick or to your phone's search app (or to a DuckDuckGo search in the browser when no search app answers). If another app asked Verdetto to scan for it, the result goes back to that app.</p>
<p>These services are run by others, in the United States and in Europe, and they process the request, including your phone's internet address, under their own privacy policies: <a href="https://docs.github.com/en/site-policy/privacy-policies/github-general-privacy-statement">GitHub</a>, <a href="https://about.rdap.org/">rdap.org</a> and the registry it forwards to, <a href="https://world.openfoodfacts.org/privacy">Open Food Facts</a>, <a href="https://archive.org/about/terms.php">Open Library</a> (the Internet Archive), the <a href="https://www.dnb.de/EN/Service/Datenschutz/datenschutz_node.html">German National Library</a>, the <a href="https://www.bnf.fr/fr/politique-de-confidentialite">French National Library</a>, <a href="https://www.fda.gov/about-fda/about-website/website-policies">openFDA</a> (the US Food and Drug Administration), the <a href="https://www.cpsc.gov/about-cpsc/policies-statements-and-directives/privacy-policy">US Consumer Product Safety Commission</a>, <a href="https://www.nlm.nih.gov/web_policies.html">DailyMed and RxNav</a> (the US National Library of Medicine), <a href="https://webgate.ec.europa.eu/eudamed-static-play/documents/assets/privacy-policy/privacy_statement_en.pdf">EUDAMED</a> (the European Commission), <a href="https://www.aemps.gob.es/politica-privacidad/">AEMPS</a> (Spain's medicines agency), <a href="https://metabrainz.org/privacy">MusicBrainz</a>, <a href="https://www.crossref.org/operations-and-sustainability/privacy/">Crossref</a>, <a href="https://foundation.wikimedia.org/wiki/Policy:Privacy_policy">Wikidata</a> (the Wikimedia Foundation), and the NHTSA vehicle database (the US Department of Transportation). The United States has no general EU or UK adequacy decision; your phone sends the request there because you scanned the code. They may change or stop. With online lookups off, nothing leaves the phone.</p>

<h2>Your phone's backup</h2>
<p>Unless you turn off "Include in the phone's backup" in Settings, your history, settings, and your card ride along in your phone's own Android backup, the same way other apps' data does. That backup goes to your Google account under Google's policy; Verdetto never sees it. History includes what codes contained, such as a Wi-Fi password you scanned, so turn the setting off if you would rather it stayed on the phone. If you turn on read-aloud, the result's title goes to your phone's speech engine, under its maker's policy.</p>

<h2>What never leaves the phone</h2>
<p>Your scan history, except through your phone's backup if you leave that on. The pages behind links, which the app never opens or inspects. Wi-Fi passwords, contacts, and calendar entries you scan. Anything about you.</p>

<h2>Permissions</h2>
<p>The app asks for the camera, which it needs to scan, and for contacts access only if you fill your own card from your phone's profile. It uses the network only for the lookups described above, vibration for the buzz on scan, and, on Android 10 and older, the Wi-Fi setting needed to join a network you scanned. Joining a Wi-Fi network, adding a contact, or saving an event goes through the standard Android prompt for that action, and only when you choose it. The contribution goes through Google Play's own billing.</p>

<h2>Purchases</h2>
<p>The optional contribution inside the app is sold through Google Play. Google processes the payment under <a href="https://policies.google.com/privacy">its own privacy policy</a>; we never see your name, email address, or payment details. Google's billing code inside the app also reports to Google how its own steps went, such as whether a connection or a purchase succeeded or failed, which Google uses to improve that code and its support for errors. Those reports go to Google, not to us, under the same policy, and only when the app talks to Google Play for the contribution. Google shows us, in its developer console and its sales reports, an order record for refunds and tax: at most an order number, the item, the amount and currency, the phone's model, and the country, state, city and postal code the purchase was made from; where Google itself is the seller, in the EEA and the UK, only the country. The app itself keeps only a note on your phone that a contribution was made, for the thank-you badge.</p>
<p><strong>Google Play's counts.</strong> Google Play shows us, in its developer console, counts of installs, uninstalls, ratings, and crashes, by country and by the site or store page that led to the store page. Google records that when the store page opens, under its own privacy policy; the app does not request it from Google and never sends it anywhere. The counts are grouped and rounded by Google, and we cannot see anyone in them.</p>

<h2>Reports you send</h2>
<p>If you choose to report something, from the app or from this website, the report form is a Google Form that opens in your browser; the app itself sends nothing. The report contains only what you see on the form: the category, the scanned text if you leave it in, your description, where you found the code if you say, the app's version, and, only if you add it, your email address so we can reply. Reports are stored in Verdetto's Google account under <a href="https://policies.google.com/privacy">Google's privacy policy</a> and are used only to handle the report: a person reads it, and nothing is added to the warning list without that review. Reports are kept for up to two years and then deleted; write to us to have yours deleted sooner. For a license or ID scan, a report carries the card's format numbers and the check's outcome, never anything printed on the card.</p>

<h2>When you write to us</h2>
<p>If you email us, we receive your address and what you wrote, and we use them to answer you. That is the only personal data we process, and we process it because you asked us something (in the European Union and the United Kingdom, that is a contract-like request and our legitimate interest in answering it). Your message stays in our mailbox like any email, is not added to any list, and is not shared or used for anything else. Our mailbox is provided by Microsoft (Microsoft 365), in the United States, as our service provider under its own terms. We keep the thread for up to two years after the last message, then delete it; ask, and we delete it sooner.</p>

<h2>Children</h2>
<p>The app is not directed at children under 13, asks no one's age, builds no profile, and collects no data from anyone.</p>

<h2>Keeping and deleting data</h2>
<p>Everything the app keeps is on your phone, and in your phone's backup if you leave that on. Delete history entries in the app, or uninstall the app to remove all of it. We hold no data about you from the app, so there is nothing for us to delete or hand over.</p>

<h2>Security</h2>
<p>The app never sends an unencrypted request: it talks to the services above over encrypted connections (HTTPS), and a shortened link written as plain http is shown as it is, not followed. The warning list is signed, and the app checks the signature before using it. History, settings, and your card sit in the app's private storage, which Android keeps from other apps and protects with the phone's own encryption when the phone has a screen lock. We run no server and keep no database of users. If we ever learned that the mailbox or the report form holding something you sent us had been breached in a way that put you at risk, we would tell you and the authority your law names.</p>

<h2>Your rights</h2>
<p>Wherever you live, you can ask what we hold about you and ask for a copy, a correction, or deletion, or object to our processing it. Because the app sends us nothing, what we hold is at most an email you sent us. Write to <a href="mailto:{EMAIL}">{EMAIL}</a>; we answer within the time your law sets, and in any case within a month. You may also complain to your data protection authority: in the European Economic Area, the authority of your country; in the United Kingdom, the Information Commissioner's Office; in Brazil, the ANPD; elsewhere, the authority your law names. In California and the other US states with privacy laws: we collect no personal information through the app, and we do not sell or share it.</p>

<h2>This website</h2>
<p>These pages are static and hosted on <a href="https://docs.github.com/en/pages/getting-started-with-github-pages/about-github-pages#data-collection">GitHub Pages</a>. They set no cookies and run no analytics. The report page embeds a Google Form, which loads from Google under its privacy policy; every other page loads nothing from anywhere but this site. The safety-list page shows weekly numbers that this site serves as a small file of its own, copied from the public list repository once a week; your browser makes no request to any third party for it, and the numbers hold nothing about anyone's phone or scans. GitHub may keep standard server logs, such as the address a page was requested from and when, under its own privacy statement.</p>

<h2>Changes</h2>
<p>If this policy changes, the new version will be posted here with a new effective date, and earlier versions stay readable on this site. If a change would send more off the phone or have us keep more, the app will say so in its update note before that version applies; we never treat a changed policy as permission for that. Earlier versions: {earlier_versions('privacy')}.</p>

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
<p>This app is free. Its safety list's pipeline is open source today; the app's own code is licensed under the GNU General Public License, version 3 or later, and its scanner core under the Apache License 2.0, both published with the first release. The free app is provided as is and as available, without warranty of any kind, express or implied, including fitness for a particular purpose; the purchase carries the guarantees your law gives for paid digital content. It is not security software and not a substitute for security advice. The app is for people aged 13 and over.</p>

<h2>Who provides the app</h2>
<p>Verdetto, {ADDRESS}, United States, a small business in Virginia. Contact: <a href="mailto:{EMAIL}">{EMAIL}</a>. Support requests and legal notices go to that address.</p>

<h2>What the safety checks are</h2>
<p>When you scan a code, the app looks at the content itself, on your phone, for known warning signs: hidden sign-in details, raw IP addresses, lookalike or imitation names, shortened links, unencrypted addresses, unusual ports, app or program downloads, unusually deep subdomains, script or file addresses, tracking and affiliate parameters, premium-rate numbers, open Wi-Fi networks, and payment destinations. It also compares links, sites, and wallet addresses with a list of known phishing, malware, and scam entries kept on the phone, compiled from public sources (PhishTank, the CERT Polska warning list, PhishDestroy, PhishIndex, the polkadot-js phishing list, and the US Treasury's OFAC sanctions list). With online lookups on, the app can download a newer list, follow a shortened or affiliate link to where it leads, ask a domain's registry when it was registered, and send a product number to Open Food Facts and its sister databases, the US Consumer Product Safety Commission's recall database, Open Library, the German and French national libraries, openFDA (medicines and medical devices), DailyMed and RxNav, Spain's medicines agency AEMPS, the European Commission's EUDAMED database, MusicBrainz, Crossref, Wikidata, or the NHTSA vehicle database. Their answers are shown as given. Postal codes, Italian and French medicine codes, phone-number regions and carriers, and German bank sort codes are named from tables kept on the phone.</p>

<h2>What they are not</h2>
<p>The checks do not open or inspect the page behind a link, cannot see what a network, contact, calendar entry, or product will do, and cannot catch every scam, unsafe site, or harmful code. "No warnings found" means none of the app's checks matched. It is never a statement that anything is safe, genuine, or trustworthy. The app never looks a person up: a license or ID scan is shown from the barcode alone, with the age, the expiry, and the issuer worked out on the phone, and the app cannot tell a genuine card from a copy. The app cannot tell whether a number, link, or account you put in a code is yours to use. Verdetto reads your own documents. A business that scans other people's cards must follow the laws that apply to it, including limits on what it may keep.</p>

<h2>Your decisions</h2>
<p>Whether to open a link, join a network, add a contact or event, dial a number, or act on any scanned content is your decision, made at your own risk. Automatic opening, when you turn it on, opens links you have not looked at; you accept that when you turn it on. Codes you make carry what you typed or copied. Whether you have the right to the numbers, links, or accounts you put in them, and where you use them, is your decision. Use the app lawfully. Do not use it to break into anything, or to flood the lookup services: they see the app's name, not yours, and abuse can get the app cut off for everyone.</p>

<h2>Liability</h2>
<p>We are not liable for loss that comes from acting on scanned content, from a check that missed something, or from a lookup service's answer, including opening a link, joining a network, or relying on a check or a lookup. We are not liable for loss we could not reasonably foresee when you started using the app. Where the law does not let us exclude liability, our total liability to you is limited to the greater of what you paid us in the last twelve months and US$100. None of this limits liability for intent or gross negligence, for death or personal injury caused by negligence, for fraud, or for anything else your law does not let us limit. Your statutory guarantees for the purchase are not affected.</p>

<h2>Your rights as a consumer</h2>
<p>Nothing in these terms takes away rights that the consumer law of your country gives you and that cannot be waived by agreement, including the guarantees of the Australian Consumer Law and the rights of consumers in the European Union, the United Kingdom, and Brazil.</p>

<h2>Your data</h2>
<p>Online lookups are on by default and can be turned off in Settings. Product lookups have a switch of their own under it. While on, only the address, domain, or the product, book, medicine, device, journal, or vehicle number goes, with the app's name and our support address, to the named services (Open Food Facts and its sisters, the US Consumer Product Safety Commission's recall database, Open Library, the German and French national libraries, openFDA, DailyMed and RxNav, Spain's medicines agency AEMPS and the European Commission's EUDAMED database for medicines and medical devices, MusicBrainz, Crossref, Wikidata, and the NHTSA vehicle database); with them off, nothing leaves the phone. There are no ads, no analytics, and no accounts. The <a href="{href('privacy.html')}">privacy policy</a> has the details. For a vehicle, the year, make, and model also go to NHTSA's recall and crash-test databases and to the EPA fuel-economy database (fueleconomy.gov).</p>

<h2>Contributions</h2>
<p>The app is free and complete: every check and every decode is free for everyone, and nothing is locked. It offers one optional contribution, paid once and not a subscription (you can give again if you like), sold as an in-app item through Google Play from US$0.99 or the local equivalent, which pays for the work and earns a thank-you badge and the small extras listed on the Support screen as they arrive. The price in the purchase flow is the price you pay, including any tax Google Play charges. In the European Economic Area and the United Kingdom, Google is the merchant of record for the purchase; everywhere else, Verdetto is the seller and Google Play handles the payment. Refunds follow Google Play's refund policy and the consumer law of your country; if something went wrong, write to <a href="mailto:{EMAIL}">{EMAIL}</a> and we will help. Where Google Play's billing is unavailable, the contribution is not offered. What you get is what the Support screen marks as available when you buy; items marked planned or soon are our intentions, not part of the purchase. A contribution buys no protection and no promise of future features. Verdetto is a small business; a contribution is a purchase, not a gift, and it brings no tax benefit.</p>

<h2>Third-party services</h2>
<p>The lookup services and the shortening services the app can ask are run by others under their own terms and privacy policies. Their answers are shown as given; they may change or stop, and we are not responsible for them. NHTSA's recall and crash-test databases and the EPA fuel-economy database are among them; recall and rating information is for the model year and is not a statement about the individual vehicle.</p>

<h2>Open source and trademarks</h2>
<p>The safety list's pipeline is published under the MIT License. The app's own code is licensed under the GNU General Public License, version 3 or later, and its scanner core under the Apache License 2.0; both are published with the first release. Those licenses cover code. They do not cover the Verdetto name, icon, wordmark, splash screen, screenshots or store material, which are not licensed and stay ours; a fork may not use that name or artwork as its own. Use of the name, the icon and the 'Built on Verdetto' badge is governed by the <a href="{href('community-license.html')}">Verdetto Community License</a>, a trademark license. The app also includes work by others under their own licenses, listed under About, Licenses; the safety list names its sources and their terms in its repository.</p>

<h2>These terms and others</h2>
<p>These terms and the privacy policy are the whole agreement between you and Verdetto about the app. Google Play's terms cover the store and the payment; if they and these terms conflict, Google Play's terms win for the store and the payment. The code licenses cover the source code, and nothing here limits the rights they give you. If a court finds one sentence of these terms unenforceable, the rest still applies. You can stop at any time by uninstalling the app. We may stop offering the app, a lookup, or list updates; the checks that run on the phone keep working in the version you have. You agree to follow the export-control and sanctions laws that apply to you.</p>

<h2>Governing law</h2>
<p>These terms are governed by the laws of the Commonwealth of Virginia, United States. If you are a consumer in a country whose law protects you regardless of that choice, that protection applies, and you may bring a claim before the courts of your own country. Write to support@verdettoqr.com first; most problems are settled by email. If you are not a consumer protected by your own country's law, claims go to the state or federal courts in Virginia. You may also use a small-claims court where you live.</p>

<h2>Language</h2>
<p>These terms are written in English and offered in ten other languages. The English text is the reference, except where the law of your country says otherwise.</p>

<h2>Changes</h2>
<p>These terms may change with a new version of the app, for a reason: a new feature or lookup, a change in the law, or clearer wording. The date at the top and the release notes say when. The text in the installed version is the one that applies. A change never takes away anything you have already bought. Earlier versions: {earlier_versions('terms')}.</p>
"""

SUPPORT_T = {
 "en": {
  "title": "Help - Verdetto",
  "desc": "Help for Verdetto: QR & Barcode Scanner. How to reach us and answers to common questions.",
  "h1": "Help",
  "card1": "Something wrong with a scan, a warning, or the app? {report}; a person reads every report. A site listed by mistake is reviewed the same day.",
  "report": "Report it",
  "card2": "Write to {email}. It helps to include your phone model, your Android version, and what you were scanning if you can share it. Do not send a code that contains a password, a sign-in link, or anything you would not put in an email. We keep your message for as long as it takes to answer, then delete it.",
  "common": "Common questions",
  "faq": [
   [
    "It said \"No warnings found.\" Is the link safe?",
    "The app does not know, and it never says something is safe. \"No warnings found\" means none of its checks matched. Look at the address it shows you, and open it only if you would have opened it anyway."
   ],
   [
    "Does it work offline?",
    "Yes. Scanning and every built-in check run on the phone. Online lookups add where a short link leads, how old a domain is, product details, and, for a vehicle, its recall campaigns, crash-test ratings, and fuel economy from NHTSA and the EPA. They need a connection and can be turned off in Settings."
   ],
   [
    "Why does it ask for the camera?",
    "To scan. The only other thing it can ask for is contacts access, once, if you fill your card from your phone's profile."
   ],
   [
    "How do I turn off online lookups?",
    "Settings, then Allow online lookups. With them off, nothing leaves the phone. Product lookups have a switch of their own under it."
   ],
   [
    "How do I delete my history?",
    "Swipe an entry, or Clear history in Settings. Scans older than 90 days clear on their own unless you star them. History also rides in your phone's own backup unless you turn that off; uninstalling removes it."
   ],
   [
    "A code will not scan.",
    "Fill more of the screen with it, hold still, and let the camera focus. Damaged or faded codes take a moment longer. If it still will not read, send us a photo of the code if it is not sensitive."
   ],
   [
    "What does the contribution unlock?",
    "Nothing you need; everything stays free. Supporters get a badge you can hide, and a few small extras are planned."
   ]
  ],
  "closing": "Not sure what to look for in a link? Read {guide}. Want to keep the app free for everyone? {support}.",
  "guide": "how to check a QR code link before you open it",
  "support": "Support the work"
 },
 "de": {
  "title": "Hilfe - Verdetto",
  "desc": "Hilfe zu Verdetto: QR & Barcode Scanner. Wie du uns erreichst und Antworten auf häufige Fragen.",
  "h1": "Hilfe",
  "card1": "Stimmt etwas mit einem Scan, einer Warnung oder der App nicht? {report}; jede Meldung liest ein Mensch. Eine irrtümlich gelistete Website wird noch am selben Tag geprüft.",
  "report": "Melde es",
  "card2": "Schreib an {email}. Es hilft, wenn du dein Handymodell, deine Android-Version und, falls du es teilen kannst, den gescannten Inhalt nennst. Schick keinen Code, der ein Passwort, einen Anmeldelink oder etwas enthält, das du nicht in eine E-Mail schreiben würdest. Wir behalten deine Nachricht so lange, wie die Antwort dauert, und löschen sie dann.",
  "common": "Häufige Fragen",
  "faq": [
   [
    "Es stand „Keine Warnungen gefunden“. Ist der Link sicher?",
    "Die App weiß es nicht, und sie sagt nie, dass etwas sicher ist. „Keine Warnungen gefunden“ heißt: Keine ihrer Prüfungen hat angeschlagen. Sieh dir die Adresse an, die sie dir zeigt, und öffne sie nur, wenn du sie sowieso geöffnet hättest."
   ],
   [
    "Funktioniert sie offline?",
    "Ja. Das Scannen und jede eingebaute Prüfung laufen auf dem Handy. Online-Abfragen ergänzen, wohin ein Kurzlink führt, wie alt eine Domain ist, Produktdetails und bei einem Fahrzeug seine Rückrufe, Crashtest-Bewertungen und den Verbrauch von NHTSA und EPA. Sie brauchen eine Verbindung und lassen sich in den Einstellungen abschalten."
   ],
   [
    "Warum fragt sie nach der Kamera?",
    "Zum Scannen. Das Einzige, was sie sonst noch fragen kann, ist einmalig der Zugriff auf die Kontakte, wenn du deine Karte aus dem Profil deines Handys füllst."
   ],
   [
    "Wie schalte ich Online-Abfragen ab?",
    "Einstellungen, dann „Online-Abfragen erlauben“. Abgeschaltet verlässt nichts das Handy. Produktabfragen haben darunter einen eigenen Schalter."
   ],
   [
    "Wie lösche ich meinen Verlauf?",
    "Wische einen Eintrag weg oder wähle „Verlauf löschen“ in den Einstellungen. Scans, die älter als 90 Tage sind, löschen sich von selbst, wenn du sie nicht mit einem Stern markierst. Der Verlauf ist auch Teil der Sicherung deines Handys, wenn du das nicht abschaltest; Deinstallieren entfernt ihn."
   ],
   [
    "Ein Code lässt sich nicht scannen.",
    "Fülle mehr vom Bildschirm damit, halte still und lass die Kamera fokussieren. Beschädigte oder verblasste Codes brauchen einen Moment länger. Liest sie ihn immer noch nicht, schick uns ein Foto des Codes, wenn er nichts Vertrauliches enthält."
   ],
   [
    "Was schaltet der Beitrag frei?",
    "Nichts, was du brauchst; alles bleibt kostenlos. Unterstützer bekommen ein Abzeichen, das du ausblenden kannst, und ein paar kleine Extras sind geplant."
   ]
  ],
  "closing": "Nicht sicher, worauf du bei einem Link achten sollst? Lies, {guide}. Möchtest du die App für alle kostenlos halten? {support}.",
  "guide": "wie du einen QR-Code-Link prüfst, bevor du ihn öffnest",
  "support": "Unterstütze die Arbeit"
 },
 "es": {
  "title": "Ayuda - Verdetto",
  "desc": "Ayuda para Verdetto: QR & Barcode Scanner. Cómo contactarnos y respuestas a preguntas frecuentes.",
  "h1": "Ayuda",
  "card1": "¿Algo va mal con un escaneo, un aviso o la aplicación? {report}; una persona lee cada informe. Un sitio incluido por error se revisa el mismo día.",
  "report": "Infórmanos",
  "card2": "Escribe a {email}. Ayuda que incluyas el modelo de tu teléfono, tu versión de Android y qué estabas escaneando si puedes compartirlo. No envíes un código que contenga una contraseña, un enlace de inicio de sesión o algo que no pondrías en un correo. Guardamos tu mensaje el tiempo que tarde la respuesta y después lo borramos.",
  "common": "Preguntas frecuentes",
  "faq": [
   [
    "Dijo «No se encontraron avisos». ¿El enlace es seguro?",
    "La aplicación no lo sabe, y nunca dice que algo sea seguro. «No se encontraron avisos» significa que ninguna de sus comprobaciones coincidió. Mira la dirección que te muestra y ábrela solo si la habrías abierto de todos modos."
   ],
   [
    "¿Funciona sin conexión?",
    "Sí. El escaneo y todas las comprobaciones integradas se hacen en el teléfono. Las consultas en línea añaden adónde lleva un enlace corto, la antigüedad de un dominio, detalles de productos y, para un vehículo, sus campañas de retirada, las valoraciones de pruebas de choque y el consumo de combustible de la NHTSA y la EPA. Necesitan conexión y se pueden desactivar en Ajustes."
   ],
   [
    "¿Por qué pide la cámara?",
    "Para escanear. Lo único que puede pedir además es acceso a los contactos, una vez, si rellenas tu tarjeta desde el perfil de tu teléfono."
   ],
   [
    "¿Cómo desactivo las consultas en línea?",
    "Ajustes y después «Permitir consultas en línea». Desactivadas, nada sale del teléfono. Las consultas de productos tienen su propio interruptor debajo."
   ],
   [
    "¿Cómo borro mi historial?",
    "Desliza una entrada o usa «Borrar historial» en Ajustes. Los escaneos de más de 90 días se borran solos a menos que los marques con una estrella. El historial también va en la copia de seguridad de tu teléfono a menos que la desactives; desinstalar lo elimina."
   ],
   [
    "Un código no se escanea.",
    "Llena más pantalla con él, mantén el teléfono quieto y deja que la cámara enfoque. Los códigos dañados o descoloridos tardan un poco más. Si sigue sin leerse, envíanos una foto del código si no es confidencial."
   ],
   [
    "¿Qué desbloquea la contribución?",
    "Nada que necesites; todo sigue siendo gratis. Quienes apoyan reciben una insignia que puedes ocultar, y hay previstos algunos pequeños extras."
   ]
  ],
  "closing": "¿No sabes qué mirar en un enlace? Lee {guide}. ¿Quieres que la aplicación siga siendo gratis para todos? {support}.",
  "guide": "cómo comprobar un enlace de código QR antes de abrirlo",
  "support": "Apoya el trabajo"
 },
 "fr": {
  "title": "Aide - Verdetto",
  "desc": "Aide pour Verdetto: QR & Barcode Scanner. Comment nous joindre et les réponses aux questions fréquentes.",
  "h1": "Aide",
  "card1": "Un problème avec un scan, une alerte ou l'application ? {report} ; une personne lit chaque signalement. Un site listé par erreur est réexaminé le jour même.",
  "report": "Signale-le",
  "card2": "Écris à {email}. Indique si possible le modèle de ton téléphone, ta version d'Android et ce que tu scannais si tu peux le partager. N'envoie pas un code qui contient un mot de passe, un lien de connexion ou quoi que ce soit que tu ne mettrais pas dans un e-mail. Nous gardons ton message le temps d'y répondre, puis nous le supprimons.",
  "common": "Questions fréquentes",
  "faq": [
   [
    "Il a affiché « Aucune alerte trouvée ». Le lien est-il sûr ?",
    "L'application ne le sait pas, et elle ne dit jamais que quelque chose est sûr. « Aucune alerte trouvée » signifie qu'aucune de ses vérifications n'a réagi. Regarde l'adresse qu'elle te montre et ouvre-la seulement si tu l'aurais ouverte de toute façon."
   ],
   [
    "Fonctionne-t-elle hors ligne ?",
    "Oui. Le scan et toutes les vérifications intégrées se font sur le téléphone. Les recherches en ligne ajoutent la destination d'un lien court, l'âge d'un domaine, les détails d'un produit et, pour un véhicule, ses rappels, ses notes aux essais de choc et sa consommation, depuis la NHTSA et l'EPA. Elles ont besoin d'une connexion et se désactivent dans les Réglages."
   ],
   [
    "Pourquoi demande-t-elle la caméra ?",
    "Pour scanner. La seule autre chose qu'elle peut demander est l'accès aux contacts, une fois, si tu remplis ta carte depuis le profil de ton téléphone."
   ],
   [
    "Comment désactiver les recherches en ligne ?",
    "Réglages, puis « Autoriser les recherches en ligne ». Désactivées, rien ne quitte le téléphone. Les recherches de produits ont leur propre interrupteur juste en dessous."
   ],
   [
    "Comment supprimer mon historique ?",
    "Glisse une entrée, ou « Effacer l'historique » dans les Réglages. Les scans de plus de 90 jours s'effacent d'eux-mêmes sauf si tu les marques d'une étoile. L'historique fait aussi partie de la sauvegarde de ton téléphone sauf si tu la désactives ; désinstaller le supprime."
   ],
   [
    "Un code ne se scanne pas.",
    "Remplis davantage l'écran avec lui, reste immobile et laisse la caméra faire la mise au point. Les codes abîmés ou délavés prennent un peu plus de temps. S'il ne se lit toujours pas, envoie-nous une photo du code s'il n'a rien de sensible."
   ],
   [
    "Que débloque la contribution ?",
    "Rien dont tu aies besoin ; tout reste gratuit. Les soutiens reçoivent un badge que tu peux masquer, et quelques petits extras sont prévus."
   ]
  ],
  "closing": "Tu ne sais pas quoi regarder dans un lien ? Lis {guide}. Tu veux garder l'application gratuite pour tous ? {support}.",
  "guide": "comment vérifier le lien d'un code QR avant de l'ouvrir",
  "support": "Soutiens le travail"
 },
 "pt-BR": {
  "title": "Ajuda - Verdetto",
  "desc": "Ajuda para o Verdetto: QR & Barcode Scanner. Como falar com a gente e respostas às perguntas comuns.",
  "h1": "Ajuda",
  "card1": "Algo errado com uma leitura, um alerta ou o app? {report}; uma pessoa lê cada relato. Um site listado por engano é revisado no mesmo dia.",
  "report": "Relate",
  "card2": "Escreva para {email}. Ajuda incluir o modelo do seu celular, sua versão do Android e o que você estava lendo, se puder compartilhar. Não envie um código que contenha uma senha, um link de login ou qualquer coisa que você não colocaria em um e-mail. Guardamos sua mensagem pelo tempo que a resposta levar e depois a apagamos.",
  "common": "Perguntas comuns",
  "faq": [
   [
    "Apareceu \"Nenhum alerta encontrado\". O link é seguro?",
    "O app não sabe, e nunca diz que algo é seguro. \"Nenhum alerta encontrado\" significa que nenhuma das verificações bateu. Olhe o endereço que ele mostra e abra só se você o abriria de qualquer forma."
   ],
   [
    "Funciona offline?",
    "Sim. A leitura e todas as verificações internas rodam no celular. As consultas online acrescentam para onde um link curto leva, a idade de um domínio, detalhes do produto e, para um veículo, seus recalls, notas de testes de colisão e consumo de combustível da NHTSA e da EPA. Elas precisam de conexão e podem ser desativadas nas Configurações."
   ],
   [
    "Por que ele pede a câmera?",
    "Para ler códigos. A única outra coisa que ele pode pedir é acesso aos contatos, uma vez, se você preencher seu cartão a partir do perfil do celular."
   ],
   [
    "Como desligo as consultas online?",
    "Configurações, depois \"Permitir consultas online\". Desligadas, nada sai do celular. As consultas de produtos têm uma chave própria logo abaixo."
   ],
   [
    "Como apago meu histórico?",
    "Deslize uma entrada ou use \"Limpar histórico\" nas Configurações. Leituras com mais de 90 dias se apagam sozinhas, a menos que você as marque com estrela. O histórico também vai no backup do seu celular, a menos que você desative isso; desinstalar o remove."
   ],
   [
    "Um código não lê.",
    "Preencha mais a tela com ele, segure firme e deixe a câmera focar. Códigos danificados ou desbotados levam um pouco mais. Se ainda não ler, mande uma foto do código, se ele não for sensível."
   ],
   [
    "O que a contribuição desbloqueia?",
    "Nada de que você precise; tudo continua grátis. Quem apoia ganha um selo que você pode ocultar, e alguns pequenos extras estão planejados."
   ]
  ],
  "closing": "Não sabe o que olhar em um link? Leia {guide}. Quer manter o app grátis para todos? {support}.",
  "guide": "como verificar o link de um código QR antes de abrir",
  "support": "Apoie o trabalho"
 },
 "id": {
  "title": "Bantuan - Verdetto",
  "desc": "Bantuan untuk Verdetto: QR & Barcode Scanner. Cara menghubungi kami dan jawaban atas pertanyaan umum.",
  "h1": "Bantuan",
  "card1": "Ada yang salah dengan pemindaian, peringatan, atau aplikasinya? {report}; setiap laporan dibaca oleh seseorang. Situs yang masuk daftar karena keliru ditinjau pada hari yang sama.",
  "report": "Laporkan",
  "card2": "Tulis ke {email}. Akan membantu bila kamu menyertakan model ponselmu, versi Android-mu, dan apa yang kamu pindai jika bisa dibagikan. Jangan kirim kode yang berisi kata sandi, tautan masuk, atau apa pun yang tidak akan kamu tulis di email. Kami menyimpan pesanmu selama dibutuhkan untuk menjawab, lalu menghapusnya.",
  "common": "Pertanyaan umum",
  "faq": [
   [
    "Katanya \"Tidak ada peringatan ditemukan\". Apakah tautannya aman?",
    "Aplikasi tidak tahu, dan ia tidak pernah mengatakan sesuatu itu aman. \"Tidak ada peringatan ditemukan\" berarti tak satu pun pemeriksaannya cocok. Lihat alamat yang ditampilkannya, dan buka hanya jika kamu memang akan membukanya."
   ],
   [
    "Apakah bekerja offline?",
    "Ya. Pemindaian dan setiap pemeriksaan bawaan berjalan di ponsel. Pencarian online menambahkan ke mana tautan pendek mengarah, berapa umur sebuah domain, detail produk, dan untuk kendaraan, penarikan kembali, nilai uji tabrak, dan konsumsi bahan bakarnya dari NHTSA dan EPA. Semua itu butuh koneksi dan bisa dimatikan di Setelan."
   ],
   [
    "Kenapa meminta kamera?",
    "Untuk memindai. Satu-satunya hal lain yang bisa dimintanya adalah akses kontak, sekali, jika kamu mengisi kartumu dari profil ponsel."
   ],
   [
    "Bagaimana mematikan pencarian online?",
    "Setelan, lalu \"Izinkan pencarian online\". Saat mati, tidak ada yang meninggalkan ponsel. Pencarian produk punya sakelar sendiri di bawahnya."
   ],
   [
    "Bagaimana menghapus riwayat saya?",
    "Geser sebuah entri, atau \"Hapus riwayat\" di Setelan. Pindaian yang lebih dari 90 hari terhapus sendiri kecuali kamu memberinya bintang. Riwayat juga ikut dalam cadangan ponselmu kecuali kamu mematikannya; mencopot pemasangan menghapusnya."
   ],
   [
    "Sebuah kode tidak terbaca.",
    "Isi layar lebih banyak dengan kode itu, tahan diam, dan biarkan kamera fokus. Kode yang rusak atau pudar butuh waktu sedikit lebih lama. Jika masih tidak terbaca, kirimkan foto kodenya jika tidak sensitif."
   ],
   [
    "Apa yang dibuka oleh kontribusi?",
    "Tidak ada yang kamu butuhkan; semuanya tetap gratis. Pendukung mendapat lencana yang bisa disembunyikan, dan beberapa tambahan kecil direncanakan."
   ]
  ],
  "closing": "Tidak yakin apa yang harus dilihat pada tautan? Baca {guide}. Ingin menjaga aplikasi gratis untuk semua? {support}.",
  "guide": "cara memeriksa tautan kode QR sebelum membukanya",
  "support": "Dukung pekerjaan ini"
 },
 "ru": {
  "title": "Помощь - Verdetto",
  "desc": "Помощь по Verdetto: QR & Barcode Scanner. Как с нами связаться и ответы на частые вопросы.",
  "h1": "Помощь",
  "card1": "Что-то не так со сканом, предупреждением или приложением? {report}; каждое сообщение читает человек. Сайт, попавший в список по ошибке, проверяется в тот же день.",
  "report": "Сообщите",
  "card2": "Напишите на {email}. Полезно указать модель телефона, версию Android и то, что вы сканировали, если можете этим поделиться. Не отправляйте код, содержащий пароль, ссылку для входа или что-либо, что вы не написали бы в письме. Мы храним сообщение столько, сколько нужно для ответа, а затем удаляем.",
  "common": "Частые вопросы",
  "faq": [
   [
    "Приложение написало «Предупреждений не найдено». Ссылка безопасна?",
    "Приложение этого не знает и никогда не говорит, что что-то безопасно. «Предупреждений не найдено» означает, что ни одна из его проверок не сработала. Посмотрите на адрес, который оно показывает, и открывайте только если открыли бы его и так."
   ],
   [
    "Работает ли оно офлайн?",
    "Да. Сканирование и все встроенные проверки выполняются на телефоне. Онлайн-запросы добавляют, куда ведёт короткая ссылка, сколько лет домену, сведения о товаре, а для автомобиля его отзывные кампании, оценки краш-тестов и расход топлива от NHTSA и EPA. Им нужно соединение, и их можно отключить в настройках."
   ],
   [
    "Почему оно просит камеру?",
    "Чтобы сканировать. Единственное, о чём оно ещё может попросить, это однократный доступ к контактам, если вы заполняете свою карточку из профиля телефона."
   ],
   [
    "Как отключить онлайн-запросы?",
    "Настройки, затем «Разрешить онлайн-запросы». При выключенных запросах ничего не покидает телефон. У поиска товаров есть свой переключатель под ними."
   ],
   [
    "Как удалить историю?",
    "Смахните запись или выберите «Очистить историю» в настройках. Сканы старше 90 дней удаляются сами, если не отмечены звёздочкой. История также попадает в резервную копию телефона, если вы это не отключите; удаление приложения стирает её."
   ],
   [
    "Код не сканируется.",
    "Заполните им большую часть экрана, держите телефон неподвижно и дайте камере сфокусироваться. Повреждённые или выцветшие коды читаются чуть дольше. Если он всё равно не читается, пришлите нам фото кода, если он не содержит ничего конфиденциального."
   ],
   [
    "Что открывает взнос?",
    "Ничего необходимого; всё остаётся бесплатным. Поддержавшие получают значок, который можно скрыть, и планируется несколько небольших дополнений."
   ]
  ],
  "closing": "Не знаете, на что смотреть в ссылке? Прочитайте, {guide}. Хотите, чтобы приложение оставалось бесплатным для всех? {support}.",
  "guide": "как проверить ссылку из QR-кода, прежде чем открыть её",
  "support": "Поддержите работу"
 },
 "hi": {
  "title": "सहायता - Verdetto",
  "desc": "Verdetto: QR & Barcode Scanner के लिए सहायता। हमसे संपर्क कैसे करें और आम सवालों के जवाब।",
  "h1": "सहायता",
  "card1": "किसी स्कैन, चेतावनी या ऐप में कुछ गड़बड़ है? {report}; हर रिपोर्ट एक व्यक्ति पढ़ता है। गलती से सूची में आई साइट उसी दिन जाँची जाती है।",
  "report": "रिपोर्ट करें",
  "card2": "{email} पर लिखें। अपने फ़ोन का मॉडल, Android संस्करण और, अगर साझा कर सकें, तो जो आप स्कैन कर रहे थे, बताना मददगार होता है। ऐसा कोड न भेजें जिसमें पासवर्ड, साइन-इन लिंक या कुछ ऐसा हो जो आप ईमेल में नहीं लिखेंगे। हम आपका संदेश जवाब देने तक रखते हैं, फिर हटा देते हैं।",
  "common": "आम सवाल",
  "faq": [
   [
    "इसने \"कोई चेतावनी नहीं मिली\" कहा। क्या लिंक सुरक्षित है?",
    "ऐप को यह पता नहीं, और यह कभी नहीं कहता कि कुछ सुरक्षित है। \"कोई चेतावनी नहीं मिली\" का मतलब है कि इसकी कोई भी जाँच मेल नहीं खाई। जो पता यह दिखाता है उसे देखें, और उसे तभी खोलें जब आप उसे वैसे भी खोलते।"
   ],
   [
    "क्या यह ऑफ़लाइन काम करता है?",
    "हाँ। स्कैनिंग और हर अंतर्निहित जाँच फ़ोन पर होती है। ऑनलाइन लुकअप बताते हैं कि छोटा लिंक कहाँ जाता है, डोमेन कितना पुराना है, उत्पाद का विवरण, और वाहन के लिए NHTSA और EPA से उसके रिकॉल, क्रैश-टेस्ट रेटिंग और ईंधन खपत। इन्हें कनेक्शन चाहिए और इन्हें सेटिंग्स में बंद किया जा सकता है।"
   ],
   [
    "यह कैमरा क्यों माँगता है?",
    "स्कैन करने के लिए। इसके अलावा यह केवल एक बार संपर्कों की पहुँच माँग सकता है, अगर आप अपने फ़ोन की प्रोफ़ाइल से अपना कार्ड भरें।"
   ],
   [
    "ऑनलाइन लुकअप कैसे बंद करूँ?",
    "सेटिंग्स, फिर \"ऑनलाइन लुकअप की अनुमति दें\"। बंद होने पर फ़ोन से कुछ भी बाहर नहीं जाता। उत्पाद लुकअप का अपना स्विच उसके नीचे है।"
   ],
   [
    "मैं अपना इतिहास कैसे हटाऊँ?",
    "किसी प्रविष्टि को स्वाइप करें, या सेटिंग्स में \"इतिहास साफ़ करें\" चुनें। 90 दिन से पुराने स्कैन अपने आप हट जाते हैं, जब तक आप उन पर स्टार न लगाएँ। इतिहास आपके फ़ोन के बैकअप में भी जाता है, जब तक आप उसे बंद न करें; अनइंस्टॉल करने से यह हट जाता है।"
   ],
   [
    "एक कोड स्कैन नहीं हो रहा।",
    "उससे स्क्रीन का ज़्यादा हिस्सा भरें, स्थिर रहें और कैमरे को फ़ोकस करने दें। क्षतिग्रस्त या धुँधले कोड में थोड़ा ज़्यादा समय लगता है। अगर फिर भी न पढ़े, तो कोड की तस्वीर हमें भेजें, बशर्ते वह संवेदनशील न हो।"
   ],
   [
    "योगदान से क्या मिलता है?",
    "ऐसा कुछ नहीं जिसकी आपको ज़रूरत हो; सब कुछ मुफ़्त रहता है। समर्थकों को एक बैज मिलता है जिसे आप छिपा सकते हैं, और कुछ छोटे अतिरिक्त की योजना है।"
   ]
  ],
  "closing": "पता नहीं लिंक में क्या देखें? पढ़ें {guide}। ऐप को सभी के लिए मुफ़्त रखना चाहते हैं? {support}।",
  "guide": "QR कोड लिंक को खोलने से पहले उसकी जाँच कैसे करें",
  "support": "काम का समर्थन करें"
 },
 "ja": {
  "title": "ヘルプ - Verdetto",
  "desc": "Verdetto: QR & Barcode Scanner のヘルプ。連絡方法と、よくある質問への回答。",
  "h1": "ヘルプ",
  "card1": "スキャン、警告、アプリに何か問題がありますか? {report}。すべての報告を人が読みます。誤ってリストに載ったサイトは当日中に確認します。",
  "report": "報告する",
  "card2": "{email} へお書きください。端末のモデル、Android のバージョン、差し支えなければスキャンしていた内容を添えていただくと助かります。パスワード、ログインリンク、メールに書かないようなものを含むコードは送らないでください。メッセージは回答に必要な期間だけ保持し、その後削除します。",
  "common": "よくある質問",
  "faq": [
   [
    "「警告は見つかりませんでした」と出ました。リンクは安全ですか?",
    "アプリには分かりませんし、何かが安全だと言うことは決してありません。「警告は見つかりませんでした」は、どのチェックにも該当しなかったという意味です。表示されたアドレスを見て、どうせ開くつもりだった場合にだけ開いてください。"
   ],
   [
    "オフラインで動きますか?",
    "はい。スキャンと内蔵のチェックはすべて端末内で行われます。オンライン検索は、短縮リンクの行き先、ドメインの古さ、製品の詳細、車両であれば NHTSA と EPA によるリコール、衝突試験評価、燃費を加えます。接続が必要で、設定でオフにできます。"
   ],
   [
    "なぜカメラを求めるのですか?",
    "スキャンのためです。ほかに求めることがあるのは、端末のプロフィールから自分のカードを作るときの連絡先へのアクセス、一度だけです。"
   ],
   [
    "オンライン検索をオフにするには?",
    "設定の「オンライン検索を許可」です。オフにすると端末から何も出ません。製品の検索にはその下に独自のスイッチがあります。"
   ],
   [
    "履歴を消すには?",
    "項目をスワイプするか、設定の「履歴を消去」を使います。90 日より古いスキャンは、スターを付けない限り自動で消えます。履歴は端末のバックアップにも含まれます（オフにしない限り）。アンインストールすれば消えます。"
   ],
   [
    "コードがスキャンできません。",
    "画面をコードでより大きく満たし、じっと構えて、カメラにピントを合わせさせてください。傷んだり色あせたコードは少し長くかかります。それでも読めなければ、機密でない限りコードの写真をお送りください。"
   ],
   [
    "寄付で何が解放されますか?",
    "必要なものは何もなく、すべて無料のままです。支援者には非表示にできるバッジと、いくつかの小さな特典が予定されています。"
   ]
  ],
  "closing": "リンクの何を見ればよいか分からないときは、{guide}をお読みください。アプリを誰にとっても無料のままにしたいなら、{support}。",
  "guide": "開く前に QR コードのリンクを確認する方法",
  "support": "活動を支援してください"
 },
 "zh-Hans": {
  "title": "帮助 - Verdetto",
  "desc": "Verdetto: QR & Barcode Scanner 的帮助。如何联系我们，以及常见问题的解答。",
  "h1": "帮助",
  "card1": "扫描、警告或应用出了问题？{report}；每份报告都由人来阅读。被误列入名单的网站会在当天复核。",
  "report": "报告它",
  "card2": "写信至 {email}。附上你的手机型号、Android 版本，以及在可以分享的情况下你扫描的内容，会很有帮助。不要发送包含密码、登录链接或任何你不会写进邮件的内容的码。我们保留你的消息直到回复完成，然后删除。",
  "common": "常见问题",
  "faq": [
   [
    "它显示“未发现警告”。这个链接安全吗？",
    "应用不知道，它也从不说某样东西安全。“未发现警告”意味着它的检查都没有命中。看看它显示给你的地址，只有在你本来就会打开的情况下才打开。"
   ],
   [
    "离线可用吗？",
    "可以。扫描和每项内置检查都在手机上完成。在线查询会补充短链接的去向、域名的年龄、商品详情，以及车辆来自 NHTSA 和 EPA 的召回、碰撞测试评级和燃油经济性。它们需要网络连接，可在设置中关闭。"
   ],
   [
    "为什么它要用相机？",
    "为了扫描。它可能另外请求的只有一次联系人访问权限，用于从手机个人资料填写你的名片。"
   ],
   [
    "如何关闭在线查询？",
    "设置，然后“允许在线查询”。关闭后，手机不会发出任何内容。商品查询在其下方有自己的开关。"
   ],
   [
    "如何删除我的历史记录？",
    "滑动一条记录，或在设置中“清除历史记录”。超过 90 天的扫描会自行清除，除非你加了星标。除非你关闭，历史记录也会随手机自身的备份一起保存；卸载会将其删除。"
   ],
   [
    "一个码扫不出来。",
    "让它占满更多屏幕，保持稳定，让相机对焦。破损或褪色的码需要多一点时间。如果仍然读不出，且内容不敏感，请把码的照片发给我们。"
   ],
   [
    "支持款项能解锁什么？",
    "没有你需要的东西；一切保持免费。支持者会获得一枚可隐藏的徽章，还计划有几项小额外内容。"
   ]
  ],
  "closing": "不确定该看链接的哪些地方？请阅读{guide}。想让应用对所有人保持免费？{support}。",
  "guide": "如何在打开前检查二维码链接",
  "support": "支持这项工作"
 },
 "ar": {
  "title": "المساعدة - Verdetto",
  "desc": "مساعدة لتطبيق Verdetto: QR & Barcode Scanner. كيف تتواصل معنا وإجابات عن الأسئلة الشائعة.",
  "h1": "المساعدة",
  "card1": "هل هناك خطأ في عملية مسح أو تحذير أو في التطبيق؟ {report}؛ يقرأ كل بلاغ شخصٌ من طرفنا. والموقع المدرج عن طريق الخطأ يُراجَع في اليوم نفسه.",
  "report": "أبلغ عنه",
  "card2": "اكتب إلى {email}. يساعدنا أن تذكر طراز هاتفك ونسخة Android وما كنت تمسحه إن أمكنك مشاركته. لا ترسل رمزًا يحتوي على كلمة مرور أو رابط تسجيل دخول أو أي شيء لا تكتبه في بريد إلكتروني. نحتفظ برسالتك طوال المدة اللازمة للرد ثم نحذفها.",
  "common": "أسئلة شائعة",
  "faq": [
   [
    "ظهر «لم يُعثر على تحذيرات». هل الرابط آمن؟",
    "لا يعرف التطبيق ذلك، ولا يقول أبدًا إن شيئًا ما آمن. «لم يُعثر على تحذيرات» تعني أن أي فحص من فحوصاته لم يتطابق. انظر إلى العنوان الذي يعرضه لك، وافتحه فقط إن كنت ستفتحه على أي حال."
   ],
   [
    "هل يعمل دون اتصال؟",
    "نعم. المسح وكل فحص مدمج يجريان على الهاتف. وتضيف عمليات البحث عبر الإنترنت وجهة الرابط المختصر وعمر النطاق وتفاصيل المنتج، وللمركبة استدعاءاتها وتقييمات اختبارات التصادم واستهلاك الوقود من NHTSA وEPA. وهي تحتاج إلى اتصال ويمكن إيقافها من الإعدادات."
   ],
   [
    "لماذا يطلب الكاميرا؟",
    "للمسح. والشيء الآخر الوحيد الذي قد يطلبه هو الوصول إلى جهات الاتصال، مرة واحدة، إذا ملأت بطاقتك من ملف هاتفك."
   ],
   [
    "كيف أوقف عمليات البحث عبر الإنترنت؟",
    "الإعدادات، ثم «السماح بالبحث عبر الإنترنت». ومع إيقافها لا يغادر الهاتف شيء. ولعمليات البحث عن المنتجات مفتاح خاص بها تحتها."
   ],
   [
    "كيف أحذف سجلّي؟",
    "اسحب أي مدخل، أو اختر «مسح السجل» من الإعدادات. تُحذف عمليات المسح الأقدم من 90 يومًا من تلقاء نفسها ما لم تميّزها بنجمة. ويدخل السجل أيضًا في نسخة هاتفك الاحتياطية ما لم توقف ذلك؛ وإزالة التطبيق تحذفه."
   ],
   [
    "رمز لا يُمسح.",
    "املأ الشاشة به أكثر، وثبّت يدك، ودع الكاميرا تركّز. تحتاج الرموز المتضررة أو الباهتة إلى لحظة أطول. وإن لم يُقرأ بعد، فأرسل لنا صورة الرمز إن لم يكن حساسًا."
   ],
   [
    "ما الذي تفتحه المساهمة؟",
    "لا شيء تحتاجه؛ يبقى كل شيء مجانيًا. يحصل الداعمون على شارة يمكنك إخفاؤها، وهناك إضافات صغيرة قليلة مخطط لها."
   ]
  ],
  "closing": "لست متأكدًا مما تنظر إليه في الرابط؟ اقرأ {guide}. تريد أن يبقى التطبيق مجانيًا للجميع؟ {support}.",
  "guide": "كيف تفحص رابط رمز QR قبل أن تفتحه",
  "support": "ادعم العمل"
 }
}


def support_body(t, code):
    """The Help page from its strings table; links go to the same-language pages where they exist."""
    link = lambda pg, label: f'<a href="{href(localized(pg, code))}">{label}</a>'
    card1 = t["card1"].replace("{report}", link("report.html", t["report"]))
    card2 = t["card2"].replace("{email}", f'<a href="mailto:{EMAIL}">{EMAIL}</a>')
    faq = "\n".join(f"<h3>{q}</h3>\n<p>{a}</p>\n" for q, a in t["faq"])
    closing = t["closing"].replace("{guide}", link("check-qr-code-link.html", t["guide"])).replace("{support}", link("support-the-work.html", t["support"]))
    return f"""
<h1>{t["h1"]}</h1>
<div class="card"><p>{card1}</p></div>
<div class="card"><p>{card2}</p></div>

<h2>{t["common"]}</h2>
<div class="faq">
{faq}
</div>
<p>{closing}</p>
"""


def faq_ld(t, code):
    return {"@type": "FAQPage", "inLanguage": code, "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in t["faq"]]}


FAQ = SUPPORT_T["en"]["faq"]
SUPPORT = support_body(SUPPORT_T["en"], "en")
LOCAL["support.html"] = family_pages("support.html")
SUPPORT_WORK_T = {
 "en": {
  "title": "Support the work - Verdetto",
  "desc_base": "How Verdetto stays free with no ads and no tracking: one-time contributions from the people who use it, from $0.99 on Google Play",
  "desc_github": " or through GitHub Sponsors",
  "desc_tail": ". Nothing is locked.",
  "h1": "Support the work",
  "lede": "Verdetto has no ads and nothing to sell, so the people who use it pay for it and pass it on. Every check and every decode is free for everyone. The app never nags: no ads, no pop-ups, no rating prompts. After it does something for you, it may say thank you and mention that the people who use it pay for it, at most once a month, and a switch in Settings turns that off.",
  "phone_h": "On your phone",
  "phone_p": "Settings, then Support development. From $0.99, once, $2.99 suggested, through Google Play. The app never sees your card.",
  "browser_h": "From a browser",
  "browser_wait": "GitHub Sponsors is being set up. Until it opens, the app is the way to give. The link appears here when it does.",
  "browser_live": "GitHub Sponsors, monthly ($2 or $5) or once ($3 or $10), through GitHub. It reaches the same place.",
  "browser_link": "Sponsor on GitHub",
  "pass_h": "Pass it on",
  "pass_p": "Free because people share it. Send a friend verdettoqr.com, or open Share in the app and let them scan the code. Sharing sends nothing anywhere.",
  "where_h": "Where it goes",
  "where_p": "The domain and the mailbox, the Google Play developer account, cheap test phones (the ones where scanners fail), and the time to keep the safety list and the reader current. About $25 a month keeps the lights on; everything above that goes to test phones and time.",
  "get_h": "What you get",
  "get_p": "A thank-you badge in About that you can hide, and the small extras listed on the Support screen as they arrive. Nothing you need: every feature stays free for everyone, and no check is ever held back.",
  "not_h": "What it is not",
  "not_base": "Verdetto is a small business. A contribution is a purchase, not a gift, and it brings no tax benefit. Refunds follow Google Play's",
  "not_github": " or GitHub's",
  "not_tail": " own policy and the law where you live.",
  "questions": "Questions",
  "q_free": "Is Verdetto really free?",
  "a_free": "Yes. Every feature, every check, and every decode is free for everyone, with no ads and no tracking: nothing about you or your scans goes to us, and the only code in the app that reports to anyone else is Google's own billing code, which reports to Google about the purchase. A contribution is optional and changes nothing you can do.",
  "q_money": "How does Verdetto make money?",
  "a_money_base": "From one-time contributions by the people who use it: from $0.99 in the app through Google Play",
  "a_money_github": ", or through GitHub Sponsors from a browser",
  "a_money_tail": ". There are no ads, no data sales, and no paid tier.",
  "q_unlock": "What does a contribution unlock?",
  "a_unlock": "Nothing you need. Supporters get a badge in About that they can hide, and a few small extras as they arrive.",
  "q_gift": "Is a contribution a gift?",
  "a_gift": "No. Verdetto is a small business, so a contribution is a purchase, and it brings no tax benefit.",
  "q_ask": "Will the app ask me for money?",
  "a_ask": "Not with prompts, banners, or reminders. After the app does something for you, it may say thank you and mention that the people who use it pay for it, at most once a month; a switch in Settings turns that off. The Support screen is there when you look for it, under Settings.",
  "q_computer": "Can I give from a computer?",
  "a_computer_live": "Yes, through GitHub Sponsors, monthly or once.",
  "a_computer_wait": "Not yet. GitHub Sponsors is being set up; this page will say when it opens.",
  "soon": "Coming soon"
 },
 "de": {
  "title": "Die Arbeit unterstützen - Verdetto",
  "desc_base": "Wie Verdetto ohne Werbung und Tracking kostenlos bleibt: einmalige Beiträge der Menschen, die es nutzen, ab 0,99 $ bei Google Play",
  "desc_github": " oder über GitHub Sponsors",
  "desc_tail": ". Nichts ist gesperrt.",
  "h1": "Die Arbeit unterstützen",
  "lede": "Verdetto hat keine Werbung und nichts zu verkaufen; deshalb bezahlen die Menschen, die die App nutzen, dafür und geben sie weiter. Jede Prüfung und jedes Decodieren ist für alle kostenlos. Die App nervt nie: keine Werbung, keine Pop-ups, keine Bewertungsaufforderungen. Nachdem sie etwas für dich getan hat, sagt sie vielleicht danke und erwähnt, dass die Menschen, die sie nutzen, dafür bezahlen, höchstens einmal im Monat, und ein Schalter in den Einstellungen stellt das ab.",
  "phone_h": "Auf deinem Handy",
  "phone_p": "Einstellungen, dann „Entwicklung unterstützen“. Ab 0,99 $, einmalig, 2,99 $ vorgeschlagen, über Google Play. Die App sieht deine Karte nie.",
  "browser_h": "Im Browser",
  "browser_wait": "GitHub Sponsors wird gerade eingerichtet. Bis es öffnet, ist die App der Weg zu geben. Der Link erscheint hier, sobald es so weit ist.",
  "browser_live": "GitHub Sponsors, monatlich (2 $ oder 5 $) oder einmalig (3 $ oder 10 $), über GitHub. Es kommt am selben Ort an.",
  "browser_link": "Auf GitHub sponsern",
  "pass_h": "Weitersagen",
  "pass_p": "Kostenlos, weil Menschen sie weitergeben. Schick einer Freundin verdettoqr.com oder öffne „Teilen“ in der App und lass sie den Code scannen. Teilen sendet nichts irgendwohin.",
  "where_h": "Wohin es geht",
  "where_p": "Die Domain und das Postfach, das Google-Play-Entwicklerkonto, günstige Testhandys (die, auf denen Scanner scheitern) und die Zeit, die Sicherheitsliste und den Leser aktuell zu halten. Etwa 25 $ im Monat halten das Licht an; alles darüber geht in Testhandys und Zeit.",
  "get_h": "Was du bekommst",
  "get_p": "Ein Dankeschön-Abzeichen unter „Info“, das du ausblenden kannst, und die kleinen Extras, die auf dem Support-Bildschirm aufgeführt werden, sobald sie kommen. Nichts, was du brauchst: Jede Funktion bleibt für alle kostenlos, und keine Prüfung wird je zurückgehalten.",
  "not_h": "Was es nicht ist",
  "not_base": "Verdetto ist ein kleines Unternehmen. Ein Beitrag ist ein Kauf, kein Geschenk, und bringt keinen Steuervorteil. Erstattungen folgen den Regeln von Google Play",
  "not_github": " oder GitHub",
  "not_tail": " und dem Recht deines Wohnorts.",
  "questions": "Fragen",
  "q_free": "Ist Verdetto wirklich kostenlos?",
  "a_free": "Ja. Jede Funktion, jede Prüfung und jedes Decodieren ist für alle kostenlos, ohne Werbung und ohne Tracking: Nichts über dich oder deine Scans geht an uns, und der einzige Code in der App, der an irgendjemanden berichtet, ist Googles eigener Abrechnungscode, der Google über den Kauf berichtet. Ein Beitrag ist freiwillig und ändert nichts an dem, was du tun kannst.",
  "q_money": "Wie verdient Verdetto Geld?",
  "a_money_base": "Durch einmalige Beiträge der Menschen, die die App nutzen: ab 0,99 $ in der App über Google Play",
  "a_money_github": " oder über GitHub Sponsors im Browser",
  "a_money_tail": ". Es gibt keine Werbung, keinen Datenverkauf und keine Bezahlstufe.",
  "q_unlock": "Was schaltet ein Beitrag frei?",
  "a_unlock": "Nichts, was du brauchst. Unterstützer bekommen ein Abzeichen unter „Info“, das sie ausblenden können, und ein paar kleine Extras, sobald sie kommen.",
  "q_gift": "Ist ein Beitrag ein Geschenk?",
  "a_gift": "Nein. Verdetto ist ein kleines Unternehmen, also ist ein Beitrag ein Kauf und bringt keinen Steuervorteil.",
  "q_ask": "Wird mich die App um Geld bitten?",
  "a_ask": "Nicht mit Aufforderungen, Bannern oder Erinnerungen. Nachdem die App etwas für dich getan hat, sagt sie vielleicht danke und erwähnt, dass die Menschen, die sie nutzen, dafür bezahlen, höchstens einmal im Monat; ein Schalter in den Einstellungen stellt das ab. Der Support-Bildschirm ist da, wenn du ihn suchst, unter Einstellungen.",
  "q_computer": "Kann ich vom Computer aus geben?",
  "a_computer_live": "Ja, über GitHub Sponsors, monatlich oder einmalig.",
  "a_computer_wait": "Noch nicht. GitHub Sponsors wird gerade eingerichtet; diese Seite sagt es, wenn es öffnet.",
  "soon": "Bald verfügbar"
 },
 "es": {
  "title": "Apoya el trabajo - Verdetto",
  "desc_base": "Cómo Verdetto sigue siendo gratis sin anuncios ni rastreo: contribuciones únicas de las personas que lo usan, desde 0,99 $ en Google Play",
  "desc_github": " o a través de GitHub Sponsors",
  "desc_tail": ". Nada está bloqueado.",
  "h1": "Apoya el trabajo",
  "lede": "Verdetto no tiene anuncios ni nada que vender, así que las personas que lo usan lo pagan y lo pasan a otros. Cada comprobación y cada decodificación es gratis para todos. La aplicación nunca insiste: sin anuncios, sin ventanas emergentes, sin peticiones de valoración. Después de hacer algo por ti, puede dar las gracias y mencionar que las personas que la usan la pagan, como máximo una vez al mes, y un interruptor en Ajustes lo desactiva.",
  "phone_h": "En tu teléfono",
  "phone_p": "Ajustes y después «Apoyar el desarrollo». Desde 0,99 $, una vez, 2,99 $ sugeridos, a través de Google Play. La aplicación nunca ve tu tarjeta.",
  "browser_h": "Desde un navegador",
  "browser_wait": "GitHub Sponsors se está configurando. Hasta que abra, la aplicación es la forma de dar. El enlace aparecerá aquí cuando lo haga.",
  "browser_live": "GitHub Sponsors, mensual (2 $ o 5 $) o una vez (3 $ o 10 $), a través de GitHub. Llega al mismo sitio.",
  "browser_link": "Patrocinar en GitHub",
  "pass_h": "Pásalo",
  "pass_p": "Gratis porque la gente lo comparte. Envía verdettoqr.com a alguien, o abre Compartir en la aplicación y deja que escanee el código. Compartir no envía nada a ningún sitio.",
  "where_h": "A dónde va",
  "where_p": "El dominio y el buzón, la cuenta de desarrollador de Google Play, teléfonos de prueba baratos (en los que los escáneres fallan) y el tiempo para mantener al día la lista de seguridad y el lector. Unos 25 $ al mes mantienen la luz encendida; todo lo que pasa de ahí va a teléfonos de prueba y tiempo.",
  "get_h": "Qué recibes",
  "get_p": "Una insignia de agradecimiento en Acerca de que puedes ocultar, y los pequeños extras que la pantalla de Apoyo vaya listando cuando lleguen. Nada que necesites: todas las funciones siguen siendo gratis para todos, y ninguna comprobación se retiene.",
  "not_h": "Lo que no es",
  "not_base": "Verdetto es una pequeña empresa. Una contribución es una compra, no un regalo, y no da ningún beneficio fiscal. Los reembolsos siguen la política de Google Play",
  "not_github": " o de GitHub",
  "not_tail": " y la ley del lugar donde vives.",
  "questions": "Preguntas",
  "q_free": "¿Verdetto es gratis de verdad?",
  "a_free": "Sí. Todas las funciones, todas las comprobaciones y todas las decodificaciones son gratis para todos, sin anuncios y sin rastreo: nada sobre ti o tus escaneos nos llega, y el único código de la aplicación que informa a alguien es el propio código de facturación de Google, que informa a Google sobre la compra. Una contribución es opcional y no cambia nada de lo que puedes hacer.",
  "q_money": "¿Cómo gana dinero Verdetto?",
  "a_money_base": "Con contribuciones únicas de las personas que lo usan: desde 0,99 $ en la aplicación a través de Google Play",
  "a_money_github": ", o a través de GitHub Sponsors desde un navegador",
  "a_money_tail": ". No hay anuncios, ni venta de datos, ni nivel de pago.",
  "q_unlock": "¿Qué desbloquea una contribución?",
  "a_unlock": "Nada que necesites. Quienes apoyan reciben una insignia en Acerca de que pueden ocultar, y algunos pequeños extras cuando lleguen.",
  "q_gift": "¿Una contribución es un regalo?",
  "a_gift": "No. Verdetto es una pequeña empresa, así que una contribución es una compra y no da ningún beneficio fiscal.",
  "q_ask": "¿La aplicación me pedirá dinero?",
  "a_ask": "No con avisos, banners ni recordatorios. Después de hacer algo por ti, puede dar las gracias y mencionar que las personas que la usan la pagan, como máximo una vez al mes; un interruptor en Ajustes lo desactiva. La pantalla de Apoyo está ahí cuando la buscas, en Ajustes.",
  "q_computer": "¿Puedo dar desde un ordenador?",
  "a_computer_live": "Sí, a través de GitHub Sponsors, mensual o una vez.",
  "a_computer_wait": "Todavía no. GitHub Sponsors se está configurando; esta página lo dirá cuando abra.",
  "soon": "Próximamente"
 },
 "fr": {
  "title": "Soutenir le travail - Verdetto",
  "desc_base": "Comment Verdetto reste gratuit, sans publicité ni pistage : des contributions ponctuelles, dès 0,99 $ sur Google Play",
  "desc_github": " ou via GitHub Sponsors",
  "desc_tail": ". Rien n'est verrouillé.",
  "h1": "Soutenir le travail",
  "lede": "Verdetto n'a ni publicité ni rien à vendre : ce sont les personnes qui l'utilisent qui le financent et le font connaître. Chaque vérification et chaque décodage sont gratuits pour tous. L'application n'insiste jamais : pas de publicité, pas de fenêtres, pas de demandes de notation. Après avoir fait quelque chose pour toi, elle peut dire merci et rappeler que les personnes qui l'utilisent la financent, au plus une fois par mois, et un interrupteur dans les Réglages désactive cela.",
  "phone_h": "Sur ton téléphone",
  "phone_p": "Réglages, puis « Soutenir le développement ». Dès 0,99 $, une fois, 2,99 $ suggérés, via Google Play. L'application ne voit jamais ta carte.",
  "browser_h": "Depuis un navigateur",
  "browser_wait": "GitHub Sponsors est en cours d'ouverture. Jusque-là, l'application est le moyen de donner. Le lien apparaîtra ici dès l'ouverture.",
  "browser_live": "GitHub Sponsors, mensuel (2 $ ou 5 $) ou une fois (3 $ ou 10 $), via GitHub. Cela arrive au même endroit.",
  "browser_link": "Sponsoriser sur GitHub",
  "pass_h": "Fais-le connaître",
  "pass_p": "Gratuit parce que les gens le partagent. Envoie verdettoqr.com à quelqu'un, ou ouvre Partager dans l'application et laisse-le scanner le code. Partager n'envoie rien nulle part.",
  "where_h": "Où va l'argent",
  "where_p": "Le domaine et la boîte mail, le compte développeur Google Play, des téléphones de test bon marché (ceux sur lesquels les scanners échouent) et le temps de garder la liste de sécurité et le lecteur à jour. Environ 25 $ par mois gardent la lumière allumée ; tout le reste va aux téléphones de test et au temps.",
  "get_h": "Ce que tu reçois",
  "get_p": "Un badge de remerciement dans À propos, que tu peux masquer, et les petits extras listés sur l'écran Soutien à mesure qu'ils arrivent. Rien dont tu aies besoin : toutes les fonctions restent gratuites pour tous, et aucune vérification n'est jamais retenue.",
  "not_h": "Ce que ce n'est pas",
  "not_base": "Verdetto est une petite entreprise. Une contribution est un achat, pas un don, et n'apporte aucun avantage fiscal. Les remboursements suivent la politique de Google Play",
  "not_github": " ou de GitHub",
  "not_tail": " et la loi de ton lieu de résidence.",
  "questions": "Questions",
  "q_free": "Verdetto est-il vraiment gratuit ?",
  "a_free": "Oui. Chaque fonction, chaque vérification et chaque décodage sont gratuits pour tous, sans publicité et sans pistage : rien sur toi ou tes scans ne nous parvient, et le seul code de l'application qui rend compte à quelqu'un est le code de facturation de Google, qui informe Google de l'achat. Une contribution est facultative et ne change rien à ce que tu peux faire.",
  "q_money": "Comment Verdetto gagne-t-il de l'argent ?",
  "a_money_base": "Par des contributions ponctuelles des personnes qui l'utilisent : dès 0,99 $ dans l'application via Google Play",
  "a_money_github": ", ou via GitHub Sponsors depuis un navigateur",
  "a_money_tail": ". Pas de publicité, pas de vente de données, pas de version payante.",
  "q_unlock": "Que débloque une contribution ?",
  "a_unlock": "Rien dont tu aies besoin. Les soutiens reçoivent dans À propos un badge qu'ils peuvent masquer, et quelques petits extras à mesure qu'ils arrivent.",
  "q_gift": "Une contribution est-elle un don ?",
  "a_gift": "Non. Verdetto est une petite entreprise : une contribution est un achat, et elle n'apporte aucun avantage fiscal.",
  "q_ask": "L'application me demandera-t-elle de l'argent ?",
  "a_ask": "Pas avec des invitations, des bannières ou des rappels. Après avoir fait quelque chose pour toi, elle peut dire merci et rappeler que les personnes qui l'utilisent la financent, au plus une fois par mois ; un interrupteur dans les Réglages désactive cela. L'écran Soutien est là quand tu le cherches, dans les Réglages.",
  "q_computer": "Puis-je donner depuis un ordinateur ?",
  "a_computer_live": "Oui, via GitHub Sponsors, chaque mois ou une fois.",
  "a_computer_wait": "Pas encore. GitHub Sponsors est en cours d'ouverture ; cette page le dira quand ce sera le cas.",
  "soon": "Bientôt disponible"
 },
 "pt-BR": {
  "title": "Apoie o trabalho - Verdetto",
  "desc_base": "Como o Verdetto continua grátis, sem anúncios e rastreamento: contribuições únicas de quem o usa, a partir de US$ 0,99 no Google Play",
  "desc_github": " ou pelo GitHub Sponsors",
  "desc_tail": ". Nada fica bloqueado.",
  "h1": "Apoie o trabalho",
  "lede": "O Verdetto não tem anúncios nem nada para vender, então as pessoas que o usam pagam por ele e passam adiante. Toda verificação e toda leitura é grátis para todos. O app nunca insiste: sem anúncios, sem pop-ups, sem pedidos de avaliação. Depois de fazer algo por você, ele pode agradecer e mencionar que as pessoas que o usam pagam por ele, no máximo uma vez por mês, e uma chave nas Configurações desliga isso.",
  "phone_h": "No seu celular",
  "phone_p": "Configurações, depois \"Apoiar o desenvolvimento\". A partir de US$ 0,99, uma vez, US$ 2,99 sugerido, pelo Google Play. O app nunca vê seu cartão.",
  "browser_h": "Pelo navegador",
  "browser_wait": "O GitHub Sponsors está sendo configurado. Até abrir, o app é o jeito de contribuir. O link aparece aqui quando isso acontecer.",
  "browser_live": "GitHub Sponsors, mensal (US$ 2 ou US$ 5) ou uma vez (US$ 3 ou US$ 10), pelo GitHub. Chega ao mesmo lugar.",
  "browser_link": "Apoiar no GitHub",
  "pass_h": "Passe adiante",
  "pass_p": "Grátis porque as pessoas compartilham. Mande verdettoqr.com para alguém, ou abra Compartilhar no app e deixe a pessoa ler o código. Compartilhar não envia nada a lugar nenhum.",
  "where_h": "Para onde vai",
  "where_p": "O domínio e a caixa de e-mail, a conta de desenvolvedor do Google Play, celulares de teste baratos (aqueles em que os leitores falham) e o tempo para manter a lista de segurança e o leitor em dia. Cerca de US$ 25 por mês mantêm as luzes acesas; tudo acima disso vai para celulares de teste e tempo.",
  "get_h": "O que você recebe",
  "get_p": "Um selo de agradecimento em Sobre, que você pode ocultar, e os pequenos extras listados na tela de Apoio conforme chegam. Nada de que você precise: todo recurso continua grátis para todos, e nenhuma verificação é retida.",
  "not_h": "O que não é",
  "not_base": "O Verdetto é uma pequena empresa. Uma contribuição é uma compra, não um presente, e não traz benefício fiscal. Reembolsos seguem a política do Google Play",
  "not_github": " ou do GitHub",
  "not_tail": " e a lei do lugar onde você vive.",
  "questions": "Perguntas",
  "q_free": "O Verdetto é grátis mesmo?",
  "a_free": "Sim. Todo recurso, toda verificação e toda leitura são grátis para todos, sem anúncios e sem rastreamento: nada sobre você ou suas leituras chega até nós, e o único código no app que relata algo a alguém é o código de cobrança do próprio Google, que informa o Google sobre a compra. Uma contribuição é opcional e não muda nada do que você pode fazer.",
  "q_money": "Como o Verdetto ganha dinheiro?",
  "a_money_base": "Com contribuições únicas das pessoas que o usam: a partir de US$ 0,99 no app pelo Google Play",
  "a_money_github": ", ou pelo GitHub Sponsors em um navegador",
  "a_money_tail": ". Não há anúncios, nem venda de dados, nem versão paga.",
  "q_unlock": "O que uma contribuição desbloqueia?",
  "a_unlock": "Nada de que você precise. Quem apoia ganha um selo em Sobre que pode ocultar, e alguns pequenos extras conforme chegam.",
  "q_gift": "Uma contribuição é um presente?",
  "a_gift": "Não. O Verdetto é uma pequena empresa, então uma contribuição é uma compra e não traz benefício fiscal.",
  "q_ask": "O app vai me pedir dinheiro?",
  "a_ask": "Não com avisos, banners ou lembretes. Depois de fazer algo por você, ele pode agradecer e mencionar que as pessoas que o usam pagam por ele, no máximo uma vez por mês; uma chave nas Configurações desliga isso. A tela de Apoio está lá quando você a procura, em Configurações.",
  "q_computer": "Posso contribuir de um computador?",
  "a_computer_live": "Sim, pelo GitHub Sponsors, mensal ou uma vez.",
  "a_computer_wait": "Ainda não. O GitHub Sponsors está sendo configurado; esta página avisará quando abrir.",
  "soon": "Em breve"
 },
 "id": {
  "title": "Dukung pekerjaan ini - Verdetto",
  "desc_base": "Bagaimana Verdetto tetap gratis tanpa iklan dan pelacakan: kontribusi sekali bayar dari para pemakainya, mulai $0,99 di Google Play",
  "desc_github": " atau melalui GitHub Sponsors",
  "desc_tail": ". Tidak ada yang dikunci.",
  "h1": "Dukung pekerjaan ini",
  "lede": "Verdetto tidak punya iklan dan tidak menjual apa pun, jadi orang-orang yang memakainya membayarnya dan meneruskannya. Setiap pemeriksaan dan setiap pemindaian gratis untuk semua orang. Aplikasi tidak pernah mendesak: tanpa iklan, tanpa pop-up, tanpa permintaan penilaian. Setelah melakukan sesuatu untukmu, ia mungkin mengucapkan terima kasih dan menyebut bahwa orang-orang yang memakainya membayarnya, paling banyak sekali sebulan, dan sebuah sakelar di Setelan mematikannya.",
  "phone_h": "Di ponselmu",
  "phone_p": "Setelan, lalu \"Dukung pengembangan\". Mulai $0,99, sekali, $2,99 disarankan, melalui Google Play. Aplikasi tidak pernah melihat kartumu.",
  "browser_h": "Dari peramban",
  "browser_wait": "GitHub Sponsors sedang disiapkan. Sampai dibuka, aplikasi adalah cara untuk memberi. Tautannya muncul di sini saat sudah siap.",
  "browser_live": "GitHub Sponsors, bulanan ($2 atau $5) atau sekali ($3 atau $10), melalui GitHub. Sampainya ke tempat yang sama.",
  "browser_link": "Dukung di GitHub",
  "pass_h": "Teruskan",
  "pass_p": "Gratis karena orang-orang membagikannya. Kirim verdettoqr.com ke seorang teman, atau buka Bagikan di aplikasi dan biarkan mereka memindai kodenya. Membagikan tidak mengirim apa pun ke mana pun.",
  "where_h": "Ke mana uangnya",
  "where_p": "Domain dan kotak surat, akun pengembang Google Play, ponsel uji murah (yang membuat pemindai gagal), dan waktu untuk menjaga daftar keamanan dan pembaca tetap mutakhir. Sekitar $25 sebulan menjaga lampu menyala; selebihnya untuk ponsel uji dan waktu.",
  "get_h": "Apa yang kamu dapat",
  "get_p": "Lencana terima kasih di Tentang yang bisa kamu sembunyikan, dan tambahan kecil yang tercantum di layar Dukungan saat tersedia. Tidak ada yang kamu butuhkan: setiap fitur tetap gratis untuk semua, dan tidak ada pemeriksaan yang ditahan.",
  "not_h": "Yang bukan",
  "not_base": "Verdetto adalah usaha kecil. Kontribusi adalah pembelian, bukan hadiah, dan tidak memberi manfaat pajak. Pengembalian dana mengikuti kebijakan Google Play",
  "not_github": " atau GitHub",
  "not_tail": " sendiri dan hukum tempat tinggalmu.",
  "questions": "Pertanyaan",
  "q_free": "Apakah Verdetto benar-benar gratis?",
  "a_free": "Ya. Setiap fitur, setiap pemeriksaan, dan setiap pemindaian gratis untuk semua orang, tanpa iklan dan tanpa pelacakan: tidak ada apa pun tentangmu atau pindaianmu yang sampai ke kami, dan satu-satunya kode di aplikasi yang melapor kepada pihak lain adalah kode penagihan Google sendiri, yang melapor kepada Google tentang pembelian. Kontribusi bersifat opsional dan tidak mengubah apa pun yang bisa kamu lakukan.",
  "q_money": "Bagaimana Verdetto menghasilkan uang?",
  "a_money_base": "Dari kontribusi sekali bayar orang-orang yang memakainya: mulai $0,99 di aplikasi melalui Google Play",
  "a_money_github": ", atau melalui GitHub Sponsors dari peramban",
  "a_money_tail": ". Tidak ada iklan, tidak ada penjualan data, dan tidak ada tingkat berbayar.",
  "q_unlock": "Apa yang dibuka oleh kontribusi?",
  "a_unlock": "Tidak ada yang kamu butuhkan. Pendukung mendapat lencana di Tentang yang bisa disembunyikan, dan beberapa tambahan kecil saat tersedia.",
  "q_gift": "Apakah kontribusi itu hadiah?",
  "a_gift": "Tidak. Verdetto adalah usaha kecil, jadi kontribusi adalah pembelian dan tidak memberi manfaat pajak.",
  "q_ask": "Apakah aplikasi akan meminta uang?",
  "a_ask": "Tidak dengan permintaan, banner, atau pengingat. Setelah melakukan sesuatu untukmu, ia mungkin mengucapkan terima kasih dan menyebut bahwa orang-orang yang memakainya membayarnya, paling banyak sekali sebulan; sebuah sakelar di Setelan mematikannya. Layar Dukungan ada saat kamu mencarinya, di Setelan.",
  "q_computer": "Bisakah saya memberi dari komputer?",
  "a_computer_live": "Ya, melalui GitHub Sponsors, bulanan atau sekali.",
  "a_computer_wait": "Belum. GitHub Sponsors sedang disiapkan; halaman ini akan memberi tahu saat dibuka.",
  "soon": "Segera hadir"
 },
 "ru": {
  "title": "Поддержать работу - Verdetto",
  "desc_base": "Как Verdetto остаётся бесплатным без рекламы и слежки: разовые взносы людей, которые им пользуются, от 0,99 $ в Google Play",
  "desc_github": " или через GitHub Sponsors",
  "desc_tail": ". Ничего не заблокировано.",
  "h1": "Поддержать работу",
  "lede": "У Verdetto нет рекламы и нечего продавать, поэтому люди, которые им пользуются, платят за него и рассказывают другим. Каждая проверка и каждое сканирование бесплатны для всех. Приложение никогда не надоедает: без рекламы, без всплывающих окон, без просьб оценить. Сделав что-то для вас, оно может сказать спасибо и упомянуть, что за него платят люди, которые им пользуются, не чаще раза в месяц, и переключатель в настройках это отключает.",
  "phone_h": "На вашем телефоне",
  "phone_p": "Настройки, затем «Поддержать разработку». От 0,99 $, один раз, рекомендуется 2,99 $, через Google Play. Приложение никогда не видит вашу карту.",
  "browser_h": "Из браузера",
  "browser_wait": "GitHub Sponsors ещё настраивается. Пока он не открылся, приложение остаётся способом поддержать. Ссылка появится здесь, когда он откроется.",
  "browser_live": "GitHub Sponsors, ежемесячно (2 $ или 5 $) или один раз (3 $ или 10 $), через GitHub. Деньги приходят туда же.",
  "browser_link": "Поддержать на GitHub",
  "pass_h": "Расскажите другим",
  "pass_p": "Бесплатно, потому что люди делятся им. Отправьте другу verdettoqr.com или откройте «Поделиться» в приложении и дайте ему отсканировать код. Поделиться ничего никуда не отправляет.",
  "where_h": "На что идут деньги",
  "where_p": "Домен и почтовый ящик, аккаунт разработчика Google Play, дешёвые тестовые телефоны (те, на которых сканеры не справляются) и время на поддержание списка безопасности и считывателя в актуальном состоянии. Около 25 $ в месяц покрывают основные расходы; всё сверх этого идёт на тестовые телефоны и время.",
  "get_h": "Что вы получаете",
  "get_p": "Значок благодарности в разделе «О приложении», который можно скрыть, и небольшие дополнения, перечисленные на экране поддержки по мере появления. Ничего необходимого: каждая функция остаётся бесплатной для всех, и ни одна проверка не придерживается.",
  "not_h": "Чем это не является",
  "not_base": "Verdetto — небольшой бизнес. Взнос — это покупка, а не подарок, и он не даёт налоговых льгот. Возвраты следуют правилам Google Play",
  "not_github": " или GitHub",
  "not_tail": " и закону страны, где вы живёте.",
  "questions": "Вопросы",
  "q_free": "Verdetto действительно бесплатен?",
  "a_free": "Да. Каждая функция, каждая проверка и каждое сканирование бесплатны для всех, без рекламы и без слежки: ничего о вас или ваших сканах к нам не попадает, а единственный код в приложении, который что-либо кому-либо сообщает, это собственный платёжный код Google, сообщающий Google о покупке. Взнос необязателен и ничего не меняет в том, что вы можете делать.",
  "q_money": "Как Verdetto зарабатывает?",
  "a_money_base": "Разовыми взносами людей, которые им пользуются: от 0,99 $ в приложении через Google Play",
  "a_money_github": " или через GitHub Sponsors из браузера",
  "a_money_tail": ". Нет ни рекламы, ни продажи данных, ни платного уровня.",
  "q_unlock": "Что открывает взнос?",
  "a_unlock": "Ничего необходимого. Поддержавшие получают значок в разделе «О приложении», который можно скрыть, и несколько небольших дополнений по мере появления.",
  "q_gift": "Взнос — это подарок?",
  "a_gift": "Нет. Verdetto — небольшой бизнес, поэтому взнос — это покупка, и он не даёт налоговых льгот.",
  "q_ask": "Будет ли приложение просить денег?",
  "a_ask": "Не запросами, баннерами или напоминаниями. Сделав что-то для вас, приложение может сказать спасибо и упомянуть, что за него платят люди, которые им пользуются, не чаще раза в месяц; переключатель в настройках это отключает. Экран поддержки на месте, когда вы его ищете, в настройках.",
  "q_computer": "Могу ли я поддержать с компьютера?",
  "a_computer_live": "Да, через GitHub Sponsors, ежемесячно или один раз.",
  "a_computer_wait": "Пока нет. GitHub Sponsors ещё настраивается; эта страница сообщит, когда он откроется.",
  "soon": "Скоро"
 },
 "hi": {
  "title": "काम का समर्थन करें - Verdetto",
  "desc_base": "Verdetto बिना विज्ञापन और बिना ट्रैकिंग मुफ़्त कैसे रहता है: इसे इस्तेमाल करने वाले लोगों के एकमुश्त योगदान, Google Play पर $0.99 से",
  "desc_github": " या GitHub Sponsors के ज़रिए",
  "desc_tail": "। कुछ भी बंद नहीं है।",
  "h1": "काम का समर्थन करें",
  "lede": "Verdetto में कोई विज्ञापन नहीं है और बेचने के लिए कुछ नहीं, इसलिए इसे इस्तेमाल करने वाले लोग इसका खर्च उठाते हैं और इसे आगे बढ़ाते हैं। हर जाँच और हर डिकोड सभी के लिए मुफ़्त है। ऐप कभी परेशान नहीं करता: न विज्ञापन, न पॉप-अप, न रेटिंग की माँग। आपके लिए कुछ करने के बाद यह धन्यवाद कह सकता है और बता सकता है कि इसे इस्तेमाल करने वाले लोग इसका खर्च उठाते हैं, महीने में अधिकतम एक बार, और सेटिंग्स का एक स्विच इसे बंद कर देता है।",
  "phone_h": "आपके फ़ोन पर",
  "phone_p": "सेटिंग्स, फिर \"विकास का समर्थन करें\"। $0.99 से, एक बार, $2.99 सुझाया गया, Google Play के ज़रिए। ऐप आपका कार्ड कभी नहीं देखता।",
  "browser_h": "ब्राउज़र से",
  "browser_wait": "GitHub Sponsors तैयार किया जा रहा है। जब तक यह खुले, ऐप ही देने का तरीका है। खुलने पर लिंक यहाँ दिखेगा।",
  "browser_live": "GitHub Sponsors, मासिक ($2 या $5) या एक बार ($3 या $10), GitHub के ज़रिए। यह उसी जगह पहुँचता है।",
  "browser_link": "GitHub पर स्पॉन्सर करें",
  "pass_h": "आगे बढ़ाएँ",
  "pass_p": "मुफ़्त है क्योंकि लोग इसे साझा करते हैं। किसी दोस्त को verdettoqr.com भेजें, या ऐप में शेयर खोलें और उन्हें कोड स्कैन करने दें। साझा करने से कहीं कुछ नहीं जाता।",
  "where_h": "यह कहाँ जाता है",
  "where_p": "डोमेन और मेलबॉक्स, Google Play डेवलपर खाता, सस्ते टेस्ट फ़ोन (जिन पर स्कैनर विफल होते हैं), और सुरक्षा सूची तथा रीडर को अद्यतन रखने का समय। महीने में लगभग $25 से काम चलता रहता है; उससे ऊपर का सब टेस्ट फ़ोन और समय में जाता है।",
  "get_h": "आपको क्या मिलता है",
  "get_p": "परिचय में एक धन्यवाद बैज जिसे आप छिपा सकते हैं, और समर्थन स्क्रीन पर सूचीबद्ध छोटे अतिरिक्त, जैसे-जैसे वे आते हैं। ऐसा कुछ नहीं जिसकी आपको ज़रूरत हो: हर सुविधा सभी के लिए मुफ़्त रहती है, और कोई जाँच कभी रोकी नहीं जाती।",
  "not_h": "यह क्या नहीं है",
  "not_base": "Verdetto एक छोटा व्यवसाय है। योगदान एक ख़रीद है, उपहार नहीं, और इससे कोई कर लाभ नहीं मिलता। रिफ़ंड Google Play",
  "not_github": " या GitHub",
  "not_tail": " की अपनी नीति और आपके निवास स्थान के कानून के अनुसार होते हैं।",
  "questions": "सवाल",
  "q_free": "क्या Verdetto सचमुच मुफ़्त है?",
  "a_free": "हाँ। हर सुविधा, हर जाँच और हर डिकोड सभी के लिए मुफ़्त है, बिना विज्ञापन और बिना ट्रैकिंग: आपके या आपके स्कैन के बारे में कुछ भी हम तक नहीं आता, और ऐप में किसी और को रिपोर्ट करने वाला एकमात्र कोड Google का अपना बिलिंग कोड है, जो ख़रीद के बारे में Google को बताता है। योगदान वैकल्पिक है और आप जो कर सकते हैं उसमें कुछ नहीं बदलता।",
  "q_money": "Verdetto पैसे कैसे कमाता है?",
  "a_money_base": "इसे इस्तेमाल करने वाले लोगों के एकमुश्त योगदान से: ऐप में Google Play के ज़रिए $0.99 से",
  "a_money_github": ", या ब्राउज़र से GitHub Sponsors के ज़रिए",
  "a_money_tail": "। कोई विज्ञापन नहीं, कोई डेटा बिक्री नहीं, और कोई पेड स्तर नहीं।",
  "q_unlock": "योगदान से क्या मिलता है?",
  "a_unlock": "ऐसा कुछ नहीं जिसकी आपको ज़रूरत हो। समर्थकों को परिचय में एक बैज मिलता है जिसे वे छिपा सकते हैं, और कुछ छोटे अतिरिक्त जैसे-जैसे आते हैं।",
  "q_gift": "क्या योगदान उपहार है?",
  "a_gift": "नहीं। Verdetto एक छोटा व्यवसाय है, इसलिए योगदान एक ख़रीद है, और इससे कोई कर लाभ नहीं मिलता।",
  "q_ask": "क्या ऐप मुझसे पैसे माँगेगा?",
  "a_ask": "प्रॉम्प्ट, बैनर या रिमाइंडर से नहीं। आपके लिए कुछ करने के बाद यह धन्यवाद कह सकता है और बता सकता है कि इसे इस्तेमाल करने वाले लोग इसका खर्च उठाते हैं, महीने में अधिकतम एक बार; सेटिंग्स का एक स्विच इसे बंद कर देता है। समर्थन स्क्रीन सेटिंग्स में तब मिलती है जब आप उसे ढूँढें।",
  "q_computer": "क्या मैं कंप्यूटर से दे सकता हूँ?",
  "a_computer_live": "हाँ, GitHub Sponsors के ज़रिए, मासिक या एक बार।",
  "a_computer_wait": "अभी नहीं। GitHub Sponsors तैयार किया जा रहा है; खुलने पर यह पृष्ठ बताएगा।",
  "soon": "जल्द आ रहा है"
 },
 "ja": {
  "title": "活動を支援 - Verdetto",
  "desc_base": "Verdetto が広告も追跡もなしに無料であり続ける仕組み: 使う人からの一回限りの寄付、Google Play で $0.99 から",
  "desc_github": "、または GitHub Sponsors 経由",
  "desc_tail": "。何もロックされません。",
  "h1": "活動を支援",
  "lede": "Verdetto には広告がなく、売るものもありません。だから使う人が支え、人に伝えてくれます。すべてのチェックとすべての読み取りは誰にとっても無料です。アプリがしつこくすることはありません: 広告なし、ポップアップなし、評価のお願いなし。何かをした後に、お礼を言い、使う人の支えで成り立っていると触れることがあります。多くても月に一度で、設定のスイッチでオフにできます。",
  "phone_h": "端末で",
  "phone_p": "設定の「開発を支援」から。$0.99 から一回限り、$2.99 が目安、Google Play 経由です。アプリがあなたのカードを見ることはありません。",
  "browser_h": "ブラウザーから",
  "browser_wait": "GitHub Sponsors は準備中です。開くまでは、アプリが支援の方法です。開いたらここにリンクが表示されます。",
  "browser_live": "GitHub Sponsors、毎月（$2 または $5）または一回限り（$3 または $10）、GitHub 経由。届く先は同じです。",
  "browser_link": "GitHub で支援する",
  "pass_h": "人に伝える",
  "pass_p": "人が広めてくれるから無料でいられます。友人に verdettoqr.com を送るか、アプリの「共有」を開いてコードをスキャンしてもらってください。共有は何もどこにも送りません。",
  "where_h": "お金の行き先",
  "where_p": "ドメインとメールボックス、Google Play のデベロッパーアカウント、安価なテスト端末（スキャナーがうまく動かないもの）、そして安全リストと読み取り機能を最新に保つ時間。月に約 $25 で灯りが保たれ、それ以上はテスト端末と時間に回ります。",
  "get_h": "得られるもの",
  "get_p": "「アプリについて」に表示される、非表示にもできるお礼のバッジと、支援画面に順次載る小さな特典。必要なものは何もありません。すべての機能は誰にとっても無料のままで、どのチェックも出し惜しみされません。",
  "not_h": "これは何ではないか",
  "not_base": "Verdetto は小さな事業です。寄付は購入であって贈与ではなく、税制上の利点はありません。返金は Google Play",
  "not_github": " または GitHub",
  "not_tail": " の規定と、お住まいの地域の法律に従います。",
  "questions": "質問",
  "q_free": "Verdetto は本当に無料ですか?",
  "a_free": "はい。すべての機能、すべてのチェック、すべての読み取りが誰にとっても無料で、広告も追跡もありません。あなたやスキャンに関する情報が当方に届くことはなく、アプリ内で第三者に報告する唯一のコードは Google 自身の課金コードで、購入について Google に報告します。寄付は任意で、できることは何も変わりません。",
  "q_money": "Verdetto はどう収入を得ていますか?",
  "a_money_base": "使う人からの一回限りの寄付です。アプリ内で Google Play を通じて $0.99 から",
  "a_money_github": "、またはブラウザーから GitHub Sponsors を通じて",
  "a_money_tail": "。広告も、データの販売も、有料プランもありません。",
  "q_unlock": "寄付で何が解放されますか?",
  "a_unlock": "必要なものは何もありません。支援者には「アプリについて」に非表示にできるバッジと、順次届く小さな特典があります。",
  "q_gift": "寄付は贈与ですか?",
  "a_gift": "いいえ。Verdetto は小さな事業なので、寄付は購入であり、税制上の利点はありません。",
  "q_ask": "アプリがお金を求めてきますか?",
  "a_ask": "催促やバナー、リマインダーでは求めません。何かをした後に、お礼を言い、使う人の支えで成り立っていると触れることがあり、多くても月に一度です。設定のスイッチでオフにできます。支援画面は設定の中にあり、探せばそこにあります。",
  "q_computer": "パソコンから支援できますか?",
  "a_computer_live": "はい、GitHub Sponsors 経由で、毎月または一回限りで。",
  "a_computer_wait": "まだです。GitHub Sponsors は準備中で、開いたらこのページでお知らせします。",
  "soon": "近日公開"
 },
 "zh-Hans": {
  "title": "支持这项工作 - Verdetto",
  "desc_base": "Verdetto 如何在没有广告、没有跟踪的情况下保持免费：来自使用者的一次性支持款，在 Google Play 上 $0.99 起",
  "desc_github": "，或通过 GitHub Sponsors",
  "desc_tail": "。没有任何功能被锁定。",
  "h1": "支持这项工作",
  "lede": "Verdetto 没有广告，也没有可卖的东西，所以使用它的人为它付费并把它传给别人。每项检查和每次解码对所有人免费。应用从不纠缠你：没有广告，没有弹窗，没有评分请求。在为你做了些什么之后，它可能会说声谢谢，并提到使用它的人在为它付费，每月最多一次，设置中的一个开关可以关闭它。",
  "phone_h": "在你的手机上",
  "phone_p": "设置，然后“支持开发”。$0.99 起，一次性，建议 $2.99，通过 Google Play。应用永远看不到你的银行卡。",
  "browser_h": "通过浏览器",
  "browser_wait": "GitHub Sponsors 正在设置中。在它开放之前，应用是支持的途径。开放后链接会出现在这里。",
  "browser_live": "GitHub Sponsors，每月（$2 或 $5）或一次性（$3 或 $10），通过 GitHub。到达的是同一个地方。",
  "browser_link": "在 GitHub 上赞助",
  "pass_h": "传给别人",
  "pass_p": "因为人们分享它，所以它免费。把 verdettoqr.com 发给朋友，或在应用中打开“分享”，让他们扫描屏幕上的码。分享不会向任何地方发送任何内容。",
  "where_h": "钱花在哪里",
  "where_p": "域名和邮箱、Google Play 开发者账号、廉价的测试手机（扫描器在上面失效的那些），以及保持安全名单和读码器更新所需的时间。每月大约 $25 维持基本运转；超出的部分用于测试手机和时间。",
  "get_h": "你得到什么",
  "get_p": "“关于”中一枚可隐藏的感谢徽章，以及支持页面上陆续列出的小额外内容。没有你需要的东西：每项功能对所有人保持免费，任何检查都不会被扣留。",
  "not_h": "它不是什么",
  "not_base": "Verdetto 是一家小企业。支持款是一笔购买，不是赠与，也不带来税务优惠。退款遵循 Google Play",
  "not_github": " 或 GitHub",
  "not_tail": " 自身的政策以及你所在地的法律。",
  "questions": "问题",
  "q_free": "Verdetto 真的免费吗？",
  "a_free": "是的。每项功能、每项检查、每次解码对所有人免费，没有广告，也没有跟踪：关于你或你的扫描的任何信息都不会到我们这里，而应用中唯一向他人报告的代码是 Google 自己的结算代码，它就购买事项向 Google 报告。支持款是可选的，不改变你能做的任何事。",
  "q_money": "Verdetto 如何赚钱？",
  "a_money_base": "来自使用者的一次性支持款：在应用内通过 Google Play $0.99 起",
  "a_money_github": "，或通过浏览器上的 GitHub Sponsors",
  "a_money_tail": "。没有广告，没有数据销售，没有付费档。",
  "q_unlock": "支持款能解锁什么？",
  "a_unlock": "没有你需要的东西。支持者会在“关于”中获得一枚可隐藏的徽章，以及陆续到来的几项小额外内容。",
  "q_gift": "支持款是赠与吗？",
  "a_gift": "不是。Verdetto 是一家小企业，所以支持款是一笔购买，不带来税务优惠。",
  "q_ask": "应用会向我要钱吗？",
  "a_ask": "不会用提示、横幅或提醒来要。在为你做了些什么之后，它可能会说声谢谢，并提到使用它的人在为它付费，每月最多一次；设置中的一个开关可以关闭它。支持页面在设置里，你想找时就在那里。",
  "q_computer": "我可以从电脑上支持吗？",
  "a_computer_live": "可以，通过 GitHub Sponsors，每月或一次性。",
  "a_computer_wait": "还不行。GitHub Sponsors 正在设置中；开放时本页会说明。",
  "soon": "即将推出"
 },
 "ar": {
  "title": "ادعم العمل - Verdetto",
  "desc_base": "كيف يبقى Verdetto مجانيًا بلا إعلانات وبلا تتبّع: مساهمات لمرة واحدة من الأشخاص الذين يستخدمونه، من 0.99 دولار على Google Play",
  "desc_github": " أو عبر GitHub Sponsors",
  "desc_tail": ". لا شيء مغلق.",
  "h1": "ادعم العمل",
  "lede": "ليس لدى Verdetto إعلانات ولا شيء يبيعه، لذا يدفع ثمنه من يستخدمونه ويمرّرونه لغيرهم. كل فحص وكل قراءة مجانية للجميع. ولا يلحّ التطبيق أبدًا: لا إعلانات ولا نوافذ منبثقة ولا طلبات تقييم. وبعد أن يفعل شيئًا من أجلك قد يشكرك ويذكر أن من يستخدمونه يدفعون ثمنه، مرة واحدة في الشهر على الأكثر، ويوقف ذلك مفتاح في الإعدادات.",
  "phone_h": "على هاتفك",
  "phone_p": "الإعدادات، ثم «ادعم التطوير». من 0.99 دولار، مرة واحدة، والمقترح 2.99 دولار، عبر Google Play. لا يرى التطبيق بطاقتك أبدًا.",
  "browser_h": "من المتصفح",
  "browser_wait": "يجري إعداد GitHub Sponsors. وحتى يُفتح، يبقى التطبيق هو طريقة العطاء. وسيظهر الرابط هنا عندما يُفتح.",
  "browser_live": "GitHub Sponsors، شهريًا (2 أو 5 دولارات) أو مرة واحدة (3 أو 10 دولارات)، عبر GitHub. يصل إلى المكان نفسه.",
  "browser_link": "ادعم على GitHub",
  "pass_h": "مرّره لغيرك",
  "pass_p": "مجاني لأن الناس يتشاركونه. أرسل verdettoqr.com إلى صديق، أو افتح «مشاركة» في التطبيق ودعه يمسح الرمز. والمشاركة لا ترسل شيئًا إلى أي مكان.",
  "where_h": "إلى أين تذهب",
  "where_p": "النطاق وصندوق البريد، وحساب مطوّر Google Play، وهواتف اختبار زهيدة (تلك التي تفشل عليها القارئات)، والوقت اللازم لإبقاء قائمة السلامة والقارئ محدّثين. نحو 25 دولارًا شهريًا تكفي للاستمرار؛ وكل ما يزيد يذهب إلى هواتف الاختبار والوقت.",
  "get_h": "ما الذي تحصل عليه",
  "get_p": "شارة شكر في «حول» يمكنك إخفاؤها، والإضافات الصغيرة المدرجة في شاشة الدعم عند وصولها. لا شيء تحتاجه: تبقى كل ميزة مجانية للجميع، ولا يُحجب أي فحص أبدًا.",
  "not_h": "ما ليس عليه",
  "not_base": "Verdetto عمل تجاري صغير. المساهمة عملية شراء لا هبة، ولا تمنح أي ميزة ضريبية. وتتبع عمليات الاسترداد سياسة Google Play",
  "not_github": " أو GitHub",
  "not_tail": " والقانون في مكان إقامتك.",
  "questions": "أسئلة",
  "q_free": "هل Verdetto مجاني فعلًا؟",
  "a_free": "نعم. كل ميزة وكل فحص وكل قراءة مجانية للجميع، بلا إعلانات وبلا تتبّع: لا يصل إلينا شيء عنك أو عن عمليات المسح لديك، والكود الوحيد في التطبيق الذي يبلّغ أي طرف آخر هو كود الفوترة الخاص بـ Google نفسها، وهو يبلّغ Google عن عملية الشراء. المساهمة اختيارية ولا تغيّر شيئًا مما يمكنك فعله.",
  "q_money": "كيف يكسب Verdetto المال؟",
  "a_money_base": "من مساهمات لمرة واحدة من الأشخاص الذين يستخدمونه: من 0.99 دولار داخل التطبيق عبر Google Play",
  "a_money_github": "، أو عبر GitHub Sponsors من المتصفح",
  "a_money_tail": ". لا إعلانات ولا بيع للبيانات ولا مستوى مدفوع.",
  "q_unlock": "ما الذي تفتحه المساهمة؟",
  "a_unlock": "لا شيء تحتاجه. يحصل الداعمون على شارة في «حول» يمكنهم إخفاؤها، وعلى إضافات صغيرة قليلة عند وصولها.",
  "q_gift": "هل المساهمة هبة؟",
  "a_gift": "لا. Verdetto عمل تجاري صغير، لذا فالمساهمة عملية شراء ولا تمنح أي ميزة ضريبية.",
  "q_ask": "هل سيطلب التطبيق منّي المال؟",
  "a_ask": "ليس بالتنبيهات أو اللافتات أو التذكيرات. بعد أن يفعل شيئًا من أجلك قد يشكرك ويذكر أن من يستخدمونه يدفعون ثمنه، مرة واحدة في الشهر على الأكثر؛ ويوقف ذلك مفتاح في الإعدادات. وشاشة الدعم موجودة حين تبحث عنها، ضمن الإعدادات.",
  "q_computer": "هل يمكنني العطاء من الحاسوب؟",
  "a_computer_live": "نعم، عبر GitHub Sponsors، شهريًا أو مرة واحدة.",
  "a_computer_wait": "ليس بعد. يجري إعداد GitHub Sponsors؛ وستذكر هذه الصفحة موعد افتتاحه.",
  "soon": "قريبًا"
 }
}


def support_work_faq(t):
    return [(t["q_free"], t["a_free"]),
            (t["q_money"], t["a_money_base"] + (t["a_money_github"] if SPONSORS_LIVE else "") + t["a_money_tail"]),
            (t["q_unlock"], t["a_unlock"]), (t["q_gift"], t["a_gift"]), (t["q_ask"], t["a_ask"]),
            (t["q_computer"], t["a_computer_live"] if SPONSORS_LIVE else t["a_computer_wait"])]


def support_work_desc(t):
    return t["desc_base"] + (t["desc_github"] if SPONSORS_LIVE else "") + t["desc_tail"]


def support_work_ld(t, code):
    return {"@type": "FAQPage", "inLanguage": code, "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in support_work_faq(t)]}


def support_work_body(t, code):
    """The Support-the-work page from its strings table: three cards, three sections, the questions."""
    browser = (f'<div class="card">{ic("heart")}<div><h3>{t["browser_h"]}</h3><p>{t["browser_live"]} <a href="https://github.com/sponsors/verdettoqr">{t["browser_link"]}</a></p></div></div>'
               if SPONSORS_LIVE else
               f'<div class="card soon">{ic("clock")}<div><p class="label">{t["soon"]}</p><h3>{t["browser_h"]}</h3><p>{t["browser_wait"]}</p></div></div>')
    faq_html = "\n".join(f"<h3>{q}</h3>\n<p>{a}</p>\n" for q, a in support_work_faq(t))
    not_p = t["not_base"] + (t["not_github"] if SPONSORS_LIVE else "") + t["not_tail"]
    return f"""
<h1>{t["h1"]}</h1>
<p>{t["lede"]}</p>
<div class="grid three">
  <div class="card">{ic('heart')}<div><h3>{t["phone_h"]}</h3><p>{t["phone_p"]}</p></div></div>
  <div class="card">{ic('scan')}<div><h3>{t["pass_h"]}</h3><p>{t["pass_p"]}</p></div></div>
  {browser}
</div>

<h2>{t["where_h"]}</h2>
<p>{t["where_p"]}</p>

<h2>{t["get_h"]}</h2>
<p>{t["get_p"]}</p>

<h2>{t["not_h"]}</h2>
<p class="meta">{not_p}</p>

<h2>{t["questions"]}</h2>
<div class="faq">
{faq_html}
</div>
"""


SUPPORT_FAQ = support_work_faq(SUPPORT_WORK_T["en"])
SUPPORT_WORK = support_work_body(SUPPORT_WORK_T["en"], "en")
SUPPORT_WORK_LD = support_work_ld(SUPPORT_WORK_T["en"], "en")
LOCAL["support-the-work.html"] = family_pages("support-the-work.html")
FAQ_LD = faq_ld(SUPPORT_T["en"], "en")

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
GUIDE_T = {
 "de": {
  "title": "Wie du einen QR-Code-Link prüfst, bevor du ihn öffnest",
  "desc": "Sechs Dinge, die du beim Link eines QR-Codes prüfst, bevor du tippst: Domain, Kurzlinks, ähnliche Namen, Verbindung, Downloads und der Ort des Codes.",
  "meta": "Aktualisiert am {DATE}. Etwa vier Minuten Lesezeit.",
  "inshort": "<strong>Kurz gesagt.</strong> Bevor du einen Link aus einem QR-Code öffnest: Lies die Domain, nicht die ganze Adresse; behandle Kurzlinks als unbekannt, bis sie aufgelöst sind; achte auf ähnlich aussehende Namen; prüfe auf <code>https</code> und keinen ungewöhnlichen Port; installiere nie etwas, das dir ein Code gibt; und frag dich, warum der Code dort ist. Ein Scanner kann dir all das zeigen. Er kann dir nicht sagen, dass eine Seite sicher ist.",
  "intro": "Ein QR-Code ist nur eine Art, einen Link zu tippen, damit du es nicht musst. Das Problem: Der Link ist unsichtbar, bis etwas ihn liest, und viele Scanner-Apps öffnen ihn in genau diesem Moment. Gefälschte Codes auf Parkautomaten, Restauranttischen, Plakaten und sogar in E-Mails setzen genau darauf. Die Lösung ist einfach: Sieh dir den Link an, bevor du ihn öffnest. Hier ist, worauf du achten solltest, in dieser Reihenfolge.",
  "s1h": "1. Lies die Domain, nicht den ganzen Link",
  "s1p": "Die Domain ist der Teil nach <code>https://</code> und vor dem ersten einzelnen Schrägstrich. In <code>https://accounts.example.com/login?ref=qr</code> ist die Domain <code>accounts.example.com</code>, und der wichtigste Teil sind die letzten beiden Glieder, <code>example.com</code>. Alles nach dem Schrägstrich kann irgendetwas behaupten; die Domain entscheidet, wo du landest. Ein guter Scanner zeigt die Domain groß und für sich, damit du sie nicht in einer langen Zeichenkette suchen musst.",
  "s2h": "2. Behandle Kurzlinks als unbekannt",
  "s2p": "Links über bit.ly, t.co, tinyurl und ähnliche Dienste verbergen ihr Ziel absichtlich. Ein Code, der einen davon zeigt, sagt dir nichts, bis er aufgelöst ist. Löse ihn zuerst auf, mit einem Scanner, der dem Kurzlink folgt und dir zeigt, wo er endet, oder öffne ihn nicht.",
  "s3h": "3. Achte auf ähnlich aussehende Namen",
  "s3p": "Der älteste Trick ist eine Domain, die sich wie eine bekannte liest. Achte auf eine Ziffer anstelle eines Buchstabens (<code>paypa1.com</code>), ein zusätzliches Wort oder einen Bindestrich (<code>paypal-secure.com</code>), einen bekannten Namen an der falschen Stelle (<code>paypal.com.example.net</code>, wo die Domain <code>example.net</code> ist) und Buchstaben aus einem anderen Alphabet mit derselben Form. Wenn ein Name fast richtig aussieht, behandle ihn als falsch, bis du den echten selbst getippt hast.",
  "s4h": "4. Prüfe die Verbindung und den Port",
  "s4p": "Ein Link, der mit <code>http://</code> statt <code>https://</code> beginnt, sendet alles, was du eingibst, offen. Ein Link mit einer Zahl nach der Domain, etwa <code>example.com:8080</code>, spricht mit etwas anderem als einer gewöhnlichen Website. Beides beweist keinen Betrug, aber beides gehört nicht auf einen Code, der dich zum Anmelden oder Bezahlen auffordert.",
  "s5h": "5. Installiere nicht, was dir ein Code gibt",
  "s5p": "Ein Link, der auf <code>.apk</code> endet, ist ein Android-Programm, keine Seite. Apps kommen aus dem Store, nicht von Aufklebern. Dasselbe gilt für Links, die um Erlaubnis bitten, „ein Update“ oder „einen Viewer“ zu installieren, bevor du etwas sehen kannst.",
  "s6h": "6. Frag dich, warum der Code dort ist",
  "s6p": "Ein QR-Code, der über einen anderen QR-Code geklebt ist, ein Code an einem Parkautomaten, der schon ein Zahlterminal hat, ein Code in einer SMS von einer unbekannten Nummer, ein Code, der eine Rückerstattung oder einen Preis verspricht: Der Ort ist die Warnung. Kriminelle drucken Aufkleber, weil Aufkleber billig sind. Wenn ein Code dort auftaucht, wo natürlicherweise keiner wäre, lass ihn aus und nutze direkt die offizielle App oder Website.",
  "canh": "Was ein Scanner dir sagen kann und was nicht",
  "canp": "Ein Scanner kann dir den Link vollständig zeigen, einen kurzen auflösen, die obigen Muster markieren und die Adresse mit Listen bekannter Phishing- und Betrugsseiten vergleichen. Was er nicht kann: die Seite öffnen und für dich beurteilen, und keine Liste ist vollständig. Deshalb meldet Verdetto „Keine Warnungen gefunden“ statt „sicher“: Es heißt, keine seiner Prüfungen hat angeschlagen, und die letzte Prüfung ist die, die du durch Lesen der Adresse machst. Wenn ein Code dich auffordert, dich anzumelden, Kartendaten einzugeben oder etwas zu installieren, schließ ihn und geh zu der Website, die du schon kennst.",
  "openedh": "Wenn du schon einen geöffnet hast",
  "openedp": "Schließ die Seite. Hast du ein Passwort eingegeben, ändere es auf der echten Website und überall sonst, wo du es benutzt hast. Hast du Kartendaten eingegeben, sag es deiner Bank. Hast du etwas installiert, deinstalliere es und lass die Sicherheitssoftware, die schon auf dem Handy ist, einen Scan laufen. Lösch den Code dann aus deinem Verlauf, damit du ihn nicht versehentlich noch einmal öffnest.",
  "callout": "Verdetto zeigt jeden Link, bevor er sich öffnet, löst gekürzte und Affiliate-Links auf, wenn Online-Abfragen eingeschaltet sind, und markiert jedes der obigen Muster auf deinem Handy. Kostenlos, ohne Werbung, bezahlt von den Menschen, die die App nutzen. {home}.",
  "callout_link": "Sieh, was sie kann"
 },
 "es": {
  "title": "Cómo comprobar un enlace de código QR antes de abrirlo",
  "desc": "Seis cosas que mirar en el enlace de un código QR antes de tocarlo: dominio, enlaces cortos, nombres parecidos, conexión, descargas y dónde está el código.",
  "meta": "Actualizado el {DATE}. Unos cuatro minutos de lectura.",
  "inshort": "<strong>En resumen.</strong> Antes de abrir un enlace de un código QR: lee el dominio, no la dirección completa; trata los enlaces acortados como desconocidos hasta expandirlos; busca nombres parecidos; comprueba que haya <code>https</code> y ningún puerto inusual; nunca instales nada que te dé un código; y pregúntate por qué el código está donde está. Un escáner puede mostrarte todo eso. No puede decirte que una página es segura.",
  "intro": "Un código QR es solo una forma de escribir un enlace para que no tengas que hacerlo tú. El problema es que el enlace es invisible hasta que algo lo lee, y muchas aplicaciones de escaneo lo abren en ese mismo instante. Los códigos falsos en parquímetros, mesas de restaurante, carteles e incluso correos electrónicos se apoyan justo en eso. La solución es sencilla: mira el enlace antes de abrirlo. Esto es lo que hay que mirar, en orden.",
  "s1h": "1. Lee el dominio, no todo el enlace",
  "s1p": "El dominio es la parte después de <code>https://</code> y antes de la primera barra simple. En <code>https://accounts.example.com/login?ref=qr</code> el dominio es <code>accounts.example.com</code>, y lo que más importa son las dos últimas etiquetas, <code>example.com</code>. Todo lo que hay después de la barra puede decir cualquier cosa; es el dominio el que decide dónde acabas. Un buen escáner muestra el dominio solo y en letra grande, para que no tengas que buscarlo en una cadena larga.",
  "s2h": "2. Trata los enlaces acortados como desconocidos",
  "s2p": "Los enlaces a través de bit.ly, t.co, tinyurl y servicios parecidos ocultan su destino a propósito. Un código que muestra uno de ellos no te dice nada hasta que se expande. Expándelo primero, con un escáner que siga el enlace corto y te muestre dónde termina, o no lo abras.",
  "s3h": "3. Busca nombres parecidos",
  "s3p": "El truco más antiguo es un dominio que se lee como uno conocido. Fíjate en un dígito que sustituye a una letra (<code>paypa1.com</code>), una palabra o un guion de más (<code>paypal-secure.com</code>), un nombre conocido colocado en el lugar equivocado (<code>paypal.com.example.net</code>, donde el dominio es <code>example.net</code>) y letras de otro alfabeto con la misma forma. Si un nombre parece casi correcto, trátalo como incorrecto hasta que hayas escrito tú el verdadero.",
  "s4h": "4. Comprueba la conexión y el puerto",
  "s4p": "Un enlace que empieza por <code>http://</code> en vez de <code>https://</code> envía todo lo que escribes al descubierto. Un enlace con un número después del dominio, como <code>example.com:8080</code>, habla con algo distinto de un sitio web normal. Ninguno de los dos prueba una estafa, pero ninguno tiene sitio en un código que te pide iniciar sesión o pagar.",
  "s5h": "5. No instales lo que te da un código",
  "s5p": "Un enlace que termina en <code>.apk</code> es un programa de Android, no una página. Las aplicaciones vienen de la tienda, no de pegatinas. Lo mismo vale para los enlaces que piden permiso para instalar «una actualización» o «un visor» antes de que puedas ver nada.",
  "s6h": "6. Pregúntate por qué el código está ahí",
  "s6p": "Un código QR pegado sobre otro código QR, un código en un parquímetro que ya tiene terminal de pago, un código en un mensaje de un número que no conoces, un código que promete un reembolso o un premio: la ubicación es la advertencia. Los delincuentes imprimen pegatinas porque las pegatinas son baratas. Cuando un código aparece donde no debería haber uno, sáltatelo y usa directamente la aplicación o el sitio oficial.",
  "canh": "Lo que un escáner puede y no puede decirte",
  "canp": "Un escáner puede mostrarte el enlace completo, expandir uno corto, señalar los patrones anteriores y comparar la dirección con listas de sitios de phishing y estafa conocidos. Lo que no puede hacer es abrir la página y juzgarla por ti, y ninguna lista está completa. Por eso Verdetto informa «No se encontraron avisos» en vez de «seguro»: significa que ninguna de sus comprobaciones coincidió, y la última comprobación es la que haces tú leyendo la dirección. Si un código te pide iniciar sesión, introducir datos de tarjeta o instalar algo, ciérralo y ve al sitio que ya conoces.",
  "openedh": "Si ya abriste uno",
  "openedp": "Cierra la página. Si escribiste una contraseña, cámbiala en el sitio real y en cualquier otro donde la usaras. Si introdujiste datos de tarjeta, avisa a tu banco. Si instalaste algo, desinstálalo y pasa un análisis con el software de seguridad que ya tiene el teléfono. Después borra el código de tu historial para no abrirlo otra vez por accidente.",
  "callout": "Verdetto muestra cada enlace antes de que se abra, expande los enlaces acortados y de afiliado cuando las consultas en línea están activadas, y señala cada uno de los patrones anteriores en tu teléfono. Gratis, sin anuncios, pagado por las personas que lo usan. {home}.",
  "callout_link": "Mira qué hace"
 },
 "fr": {
  "title": "Comment vérifier un lien de code QR avant de l'ouvrir",
  "desc": "Six choses à vérifier dans le lien d'un code QR avant de le toucher : domaine, liens courts, imitations, connexion, téléchargements et emplacement du code.",
  "meta": "Mis à jour le {DATE}. Environ quatre minutes de lecture.",
  "inshort": "<strong>En bref.</strong> Avant d'ouvrir un lien venu d'un code QR : lis le domaine, pas toute l'adresse ; traite les liens raccourcis comme inconnus tant qu'ils ne sont pas développés ; cherche les noms imitant une marque ; vérifie <code>https</code> et l'absence de port inhabituel ; n'installe jamais ce qu'un code te tend ; et demande-toi pourquoi le code est là. Un scanner peut te montrer tout cela. Il ne peut pas te dire qu'une page est sûre.",
  "intro": "Un code QR n'est qu'une façon de taper un lien à ta place. Le problème, c'est que le lien est invisible tant que rien ne le lit, et beaucoup d'applications de scan l'ouvrent à l'instant même. Les faux codes sur les parcmètres, les tables de restaurant, les affiches et même dans les e-mails comptent précisément là-dessus. La solution est simple : regarde le lien avant de l'ouvrir. Voici ce qu'il faut regarder, dans l'ordre.",
  "s1h": "1. Lis le domaine, pas tout le lien",
  "s1p": "Le domaine est la partie après <code>https://</code> et avant la première barre oblique simple. Dans <code>https://accounts.example.com/login?ref=qr</code>, le domaine est <code>accounts.example.com</code>, et ce qui compte le plus, ce sont les deux derniers éléments, <code>example.com</code>. Tout ce qui suit la barre peut dire n'importe quoi ; c'est le domaine qui décide où tu atterris. Un bon scanner affiche le domaine seul, en grand, pour que tu n'aies pas à le chercher dans une longue chaîne.",
  "s2h": "2. Traite les liens raccourcis comme inconnus",
  "s2p": "Les liens via bit.ly, t.co, tinyurl et les services du même genre cachent leur destination à dessein. Un code qui en affiche un ne te dit rien tant qu'il n'est pas développé. Développe-le d'abord, avec un scanner qui suit le lien court et te montre où il aboutit, ou ne l'ouvre pas.",
  "s3h": "3. Cherche les imitations",
  "s3p": "Le plus vieux truc est un domaine qui se lit comme un domaine familier. Guette un chiffre à la place d'une lettre (<code>paypa1.com</code>), un mot ou un tiret en trop (<code>paypal-secure.com</code>), un nom familier placé au mauvais endroit (<code>paypal.com.example.net</code>, où le domaine est <code>example.net</code>) et des lettres d'un autre alphabet qui dessinent la même forme. Si un nom semble presque juste, considère-le comme faux jusqu'à ce que tu aies tapé le vrai toi-même.",
  "s4h": "4. Vérifie la connexion et le port",
  "s4p": "Un lien qui commence par <code>http://</code> plutôt que <code>https://</code> envoie tout ce que tu tapes en clair. Un lien avec un nombre après le domaine, comme <code>example.com:8080</code>, parle à autre chose qu'un site web ordinaire. Aucun des deux ne prouve une arnaque, mais aucun n'a sa place sur un code qui te demande de te connecter ou de payer.",
  "s5h": "5. N'installe pas ce qu'un code te tend",
  "s5p": "Un lien qui finit par <code>.apk</code> est un programme Android, pas une page. Les applications viennent de la boutique, pas d'autocollants. Il en va de même des liens qui demandent la permission d'installer « une mise à jour » ou « un lecteur » avant que tu puisses voir quoi que ce soit.",
  "s6h": "6. Demande-toi pourquoi le code est là",
  "s6p": "Un code QR collé par-dessus un autre code QR, un code sur un parcmètre qui a déjà un terminal de paiement, un code dans un SMS d'un numéro inconnu, un code qui promet un remboursement ou un prix : l'emplacement est l'avertissement. Les criminels impriment des autocollants parce que les autocollants ne coûtent rien. Quand un code apparaît là où il n'y en aurait pas naturellement, passe ton chemin et utilise directement l'application ou le site officiel.",
  "canh": "Ce qu'un scanner peut et ne peut pas te dire",
  "canp": "Un scanner peut te montrer le lien en entier, développer un lien court, signaler les schémas ci-dessus et comparer l'adresse à des listes de sites de phishing et d'arnaque connus. Ce qu'il ne peut pas faire, c'est ouvrir la page et la juger pour toi, et aucune liste n'est complète. C'est pourquoi Verdetto affiche « Aucune alerte trouvée » plutôt que « sûr » : cela signifie qu'aucune de ses vérifications n'a réagi, et la dernière vérification est celle que tu fais en lisant l'adresse. Si un code te demande de te connecter, d'entrer des données de carte ou d'installer quelque chose, ferme-le et va sur le site que tu connais déjà.",
  "openedh": "Si tu en as déjà ouvert un",
  "openedp": "Ferme la page. Si tu as tapé un mot de passe, change-le sur le vrai site et partout où tu l'utilises. Si tu as saisi des données de carte, préviens ta banque. Si tu as installé quelque chose, désinstalle-le et lance une analyse avec le logiciel de sécurité déjà présent sur le téléphone. Puis supprime le code de ton historique pour ne pas le rouvrir par accident.",
  "callout": "Verdetto montre chaque lien avant qu'il ne s'ouvre, développe les liens raccourcis et d'affiliation quand les recherches en ligne sont activées, et signale chacun des schémas ci-dessus sur ton téléphone. Gratuit, sans publicité, financé par les personnes qui l'utilisent. {home}.",
  "callout_link": "Vois ce qu'il fait"
 },
 "pt-BR": {
  "title": "Como verificar o link de um código QR antes de abrir",
  "desc": "Seis coisas para olhar no link de um código QR antes de tocar: o domínio, links curtos, nomes parecidos, a conexão, downloads e onde o código está.",
  "meta": "Atualizado em {DATE}. Cerca de quatro minutos de leitura.",
  "inshort": "<strong>Em resumo.</strong> Antes de abrir um link de um código QR: leia o domínio, não o endereço inteiro; trate links encurtados como desconhecidos até serem expandidos; procure nomes parecidos; confira se há <code>https</code> e nenhuma porta incomum; nunca instale nada que um código lhe entregue; e pergunte por que o código está onde está. Um leitor pode mostrar tudo isso. Ele não pode dizer que uma página é segura.",
  "intro": "Um código QR é só um jeito de digitar um link para que você não precise. O problema é que o link fica invisível até algo o ler, e muitos apps de leitura o abrem no mesmo instante. Códigos falsos em parquímetros, mesas de restaurante, cartazes e até e-mails contam exatamente com isso. A solução é simples: olhe o link antes de abrir. Eis o que olhar, em ordem.",
  "s1h": "1. Leia o domínio, não o link inteiro",
  "s1p": "O domínio é a parte depois de <code>https://</code> e antes da primeira barra simples. Em <code>https://accounts.example.com/login?ref=qr</code> o domínio é <code>accounts.example.com</code>, e a parte que mais importa são os dois últimos rótulos, <code>example.com</code>. Tudo depois da barra pode dizer qualquer coisa; é o domínio que decide onde você vai parar. Um bom leitor mostra o domínio sozinho, em letras grandes, para você não precisar procurá-lo em uma sequência longa.",
  "s2h": "2. Trate links encurtados como desconhecidos",
  "s2p": "Links via bit.ly, t.co, tinyurl e serviços parecidos escondem o destino de propósito. Um código que mostra um deles não diz nada até ser expandido. Expanda primeiro, com um leitor que siga o link curto e mostre onde ele termina, ou não abra.",
  "s3h": "3. Procure nomes parecidos",
  "s3p": "O truque mais antigo é um domínio que se lê como um conhecido. Fique atento a um dígito no lugar de uma letra (<code>paypa1.com</code>), uma palavra ou hífen a mais (<code>paypal-secure.com</code>), um nome conhecido empurrado para o lugar errado (<code>paypal.com.example.net</code>, onde o domínio é <code>example.net</code>) e letras de outro alfabeto com o mesmo desenho. Se um nome parece quase certo, trate-o como errado até você mesmo ter digitado o verdadeiro.",
  "s4h": "4. Confira a conexão e a porta",
  "s4p": "Um link que começa com <code>http://</code> em vez de <code>https://</code> envia tudo o que você digita às claras. Um link com um número depois do domínio, como <code>example.com:8080</code>, fala com algo diferente de um site comum. Nenhum dos dois prova um golpe, mas nenhum pertence a um código que pede login ou pagamento.",
  "s5h": "5. Não instale o que um código lhe entrega",
  "s5p": "Um link que termina em <code>.apk</code> é um programa Android, não uma página. Apps vêm da loja, não de adesivos. O mesmo vale para links que pedem permissão para instalar \"uma atualização\" ou \"um visualizador\" antes de você ver qualquer coisa.",
  "s6h": "6. Pergunte por que o código está ali",
  "s6p": "Um código QR colado sobre outro código QR, um código em um parquímetro que já tem terminal de pagamento, um código em uma mensagem de um número que você não conhece, um código que promete reembolso ou prêmio: o lugar é o aviso. Criminosos imprimem adesivos porque adesivos são baratos. Quando um código aparece onde não haveria um naturalmente, pule-o e use diretamente o app ou site oficial.",
  "canh": "O que um leitor pode e não pode dizer",
  "canp": "Um leitor pode mostrar o link completo, expandir um link curto, sinalizar os padrões acima e comparar o endereço com listas de sites de phishing e golpe conhecidos. O que ele não pode fazer é abrir a página e julgá-la por você, e nenhuma lista é completa. Por isso o Verdetto informa \"Nenhum alerta encontrado\" em vez de \"seguro\": significa que nenhuma das verificações bateu, e a última verificação é a que você faz lendo o endereço. Se um código pede para você fazer login, digitar dados do cartão ou instalar algo, feche-o e vá ao site que você já conhece.",
  "openedh": "Se você já abriu um",
  "openedp": "Feche a página. Se digitou uma senha, troque-a no site verdadeiro e em qualquer outro lugar onde a usou. Se digitou dados do cartão, avise seu banco. Se instalou algo, desinstale e rode uma verificação com o software de segurança que já está no celular. Depois apague o código do seu histórico para não abri-lo de novo por acidente.",
  "callout": "O Verdetto mostra cada link antes de abrir, expande links encurtados e de afiliados quando as consultas online estão ativadas, e sinaliza cada um dos padrões acima no seu celular. Grátis, sem anúncios, pago pelas pessoas que o usam. {home}.",
  "callout_link": "Veja o que ele faz"
 },
 "id": {
  "title": "Cara memeriksa tautan kode QR sebelum membukanya",
  "desc": "Enam hal yang perlu dilihat pada tautan kode QR sebelum mengetuknya: domain, tautan pendek, nama mirip, koneksi, unduhan, dan letak kodenya.",
  "meta": "Diperbarui {DATE}. Sekitar empat menit membaca.",
  "inshort": "<strong>Singkatnya.</strong> Sebelum membuka tautan dari kode QR: baca domainnya, bukan seluruh alamat; anggap tautan pendek tidak dikenal sampai diperluas; cari nama mirip; periksa <code>https</code> dan tidak ada port yang tidak biasa; jangan pernah memasang apa pun yang diberikan kode; dan tanyakan kenapa kode itu ada di sana. Pemindai bisa menampilkan semua itu. Ia tidak bisa mengatakan bahwa sebuah halaman aman.",
  "intro": "Kode QR hanyalah cara mengetik tautan agar kamu tidak perlu melakukannya. Masalahnya, tautan itu tak terlihat sampai ada yang membacanya, dan banyak aplikasi pemindai membukanya seketika itu juga. Kode palsu di meteran parkir, meja restoran, poster, bahkan email mengandalkan hal itu. Solusinya sederhana: lihat tautannya sebelum membuka. Inilah yang perlu dilihat, secara berurutan.",
  "s1h": "1. Baca domainnya, bukan seluruh tautan",
  "s1p": "Domain adalah bagian setelah <code>https://</code> dan sebelum garis miring tunggal pertama. Pada <code>https://accounts.example.com/login?ref=qr</code> domainnya adalah <code>accounts.example.com</code>, dan bagian yang paling penting adalah dua label terakhir, <code>example.com</code>. Segala sesuatu setelah garis miring bisa berkata apa saja; domainlah yang menentukan ke mana kamu mendarat. Pemindai yang baik menampilkan domain saja dengan huruf besar, agar kamu tidak perlu mencarinya dalam rangkaian panjang.",
  "s2h": "2. Anggap tautan pendek tidak dikenal",
  "s2p": "Tautan lewat bit.ly, t.co, tinyurl, dan layanan serupa sengaja menyembunyikan tujuannya. Kode yang menampilkan salah satunya tidak memberi tahu apa pun sampai diperluas. Perluas dulu, dengan pemindai yang mengikuti tautan pendek dan menunjukkan ke mana ujungnya, atau jangan buka.",
  "s3h": "3. Cari nama mirip",
  "s3p": "Trik tertua adalah domain yang terbaca seperti domain yang dikenal. Waspadai angka yang menggantikan huruf (<code>paypa1.com</code>), kata atau tanda hubung tambahan (<code>paypal-secure.com</code>), nama dikenal yang ditaruh di tempat yang salah (<code>paypal.com.example.net</code>, yang domainnya <code>example.net</code>), dan huruf dari abjad lain dengan bentuk yang sama. Jika sebuah nama tampak hampir benar, anggaplah salah sampai kamu sendiri mengetik yang asli.",
  "s4h": "4. Periksa koneksi dan port",
  "s4p": "Tautan yang diawali <code>http://</code>, bukan <code>https://</code>, mengirim semua yang kamu ketik secara terbuka. Tautan dengan angka setelah domain, seperti <code>example.com:8080</code>, berbicara dengan sesuatu selain situs web biasa. Keduanya tidak membuktikan penipuan, tetapi keduanya tidak pantas ada pada kode yang memintamu masuk atau membayar.",
  "s5h": "5. Jangan pasang apa yang diberikan kode",
  "s5p": "Tautan yang berakhiran <code>.apk</code> adalah program Android, bukan halaman. Aplikasi datang dari toko, bukan dari stiker. Begitu pula tautan yang meminta izin memasang \"pembaruan\" atau \"penampil\" sebelum kamu bisa melihat apa pun.",
  "s6h": "6. Tanyakan kenapa kode itu ada di sana",
  "s6p": "Kode QR yang ditempel di atas kode QR lain, kode di meteran parkir yang sudah punya terminal pembayaran, kode di pesan teks dari nomor yang tidak kamu kenal, kode yang menjanjikan pengembalian uang atau hadiah: letaknya adalah peringatannya. Penjahat mencetak stiker karena stiker murah. Ketika kode muncul di tempat yang secara alami tidak ada kode, lewati dan gunakan langsung aplikasi atau situs resminya.",
  "canh": "Apa yang bisa dan tidak bisa dikatakan pemindai",
  "canp": "Pemindai bisa menampilkan tautan lengkap, memperluas tautan pendek, menandai pola di atas, dan membandingkan alamat dengan daftar situs phishing dan penipuan yang dikenal. Yang tidak bisa dilakukannya adalah membuka halaman dan menilainya untukmu, dan tidak ada daftar yang lengkap. Itulah sebabnya Verdetto melaporkan \"Tidak ada peringatan ditemukan\" alih-alih \"aman\": artinya tak satu pun pemeriksaannya cocok, dan pemeriksaan terakhir adalah yang kamu lakukan dengan membaca alamatnya. Jika sebuah kode memintamu masuk, memasukkan data kartu, atau memasang sesuatu, tutup dan pergilah ke situs yang sudah kamu kenal.",
  "openedh": "Jika kamu sudah membuka satu",
  "openedp": "Tutup halamannya. Jika kamu mengetik kata sandi, ganti di situs aslinya dan di mana pun kamu memakainya. Jika kamu memasukkan data kartu, beri tahu bankmu. Jika kamu memasang sesuatu, copot dan jalankan pemindaian dengan perangkat lunak keamanan yang sudah ada di ponsel. Lalu hapus kode itu dari riwayatmu agar tidak terbuka lagi tanpa sengaja.",
  "callout": "Verdetto menampilkan setiap tautan sebelum terbuka, memperluas tautan pendek dan afiliasi saat pencarian online aktif, dan menandai setiap pola di atas di ponselmu. Gratis, tanpa iklan, dibayar oleh orang-orang yang memakainya. {home}.",
  "callout_link": "Lihat apa yang dilakukannya"
 },
 "ru": {
  "title": "Как проверить ссылку из QR-кода, прежде чем открыть её",
  "desc": "Шесть вещей в ссылке из QR-кода, на которые стоит посмотреть до нажатия: домен, короткие ссылки, похожие имена, соединение, загрузки и место кода.",
  "meta": "Обновлено {DATE}. Около четырёх минут чтения.",
  "inshort": "<strong>Коротко.</strong> Прежде чем открыть ссылку из QR-кода: читайте домен, а не весь адрес; считайте короткие ссылки неизвестными, пока они не раскрыты; ищите похожие имена; проверьте <code>https</code> и отсутствие необычного порта; никогда не устанавливайте то, что вам подсовывает код; и спросите себя, почему код находится там, где находится. Сканер может показать вам всё это. Он не может сказать вам, что страница безопасна.",
  "intro": "QR-код — это просто способ набрать ссылку, чтобы вам не пришлось делать это самим. Беда в том, что ссылка невидима, пока её кто-то не прочитает, а многие приложения-сканеры открывают её в ту же секунду. Поддельные коды на парковочных автоматах, столах в ресторанах, плакатах и даже в письмах рассчитаны именно на это. Решение простое: посмотрите на ссылку, прежде чем открывать. Вот на что смотреть, по порядку.",
  "s1h": "1. Читайте домен, а не всю ссылку",
  "s1p": "Домен — это часть после <code>https://</code> и до первой одиночной косой черты. В <code>https://accounts.example.com/login?ref=qr</code> домен — <code>accounts.example.com</code>, а важнее всего последние две части, <code>example.com</code>. Всё после косой черты может говорить что угодно; куда вы попадёте, решает домен. Хороший сканер показывает домен отдельно и крупно, чтобы вам не пришлось искать его в длинной строке.",
  "s2h": "2. Считайте короткие ссылки неизвестными",
  "s2p": "Ссылки через bit.ly, t.co, tinyurl и подобные сервисы намеренно скрывают свою цель. Код, показывающий одну из них, ничего вам не говорит, пока она не раскрыта. Либо сначала раскройте её сканером, который переходит по короткой ссылке и показывает, куда она ведёт, либо не открывайте.",
  "s3h": "3. Ищите подделки",
  "s3p": "Самый старый трюк — домен, который читается как знакомый. Следите за цифрой вместо буквы (<code>paypa1.com</code>), лишним словом или дефисом (<code>paypal-secure.com</code>), знакомым именем не на своём месте (<code>paypal.com.example.net</code>, где домен — <code>example.net</code>) и буквами другого алфавита той же формы. Если имя выглядит почти правильным, считайте его неправильным, пока не набрали настоящее сами.",
  "s4h": "4. Проверьте соединение и порт",
  "s4p": "Ссылка, начинающаяся с <code>http://</code>, а не <code>https://</code>, передаёт всё, что вы вводите, в открытом виде. Ссылка с числом после домена, например <code>example.com:8080</code>, обращается к чему-то, кроме обычного сайта. Ни то ни другое не доказывает мошенничество, но ни тому ни другому не место на коде, который просит вас войти или заплатить.",
  "s5h": "5. Не устанавливайте то, что подсовывает код",
  "s5p": "Ссылка, заканчивающаяся на <code>.apk</code>, — это программа для Android, а не страница. Приложения приходят из магазина, а не с наклеек. То же касается ссылок, которые просят разрешение установить «обновление» или «просмотрщик», прежде чем вы что-то увидите.",
  "s6h": "6. Спросите себя, почему код здесь",
  "s6p": "QR-код, наклеенный поверх другого QR-кода, код на парковочном автомате, где уже есть платёжный терминал, код в сообщении с незнакомого номера, код, обещающий возврат или приз: само расположение — предупреждение. Преступники печатают наклейки, потому что наклейки дёшевы. Когда код появляется там, где ему неоткуда взяться, пропустите его и воспользуйтесь официальным приложением или сайтом напрямую.",
  "canh": "Что сканер может и не может вам сказать",
  "canp": "Сканер может показать ссылку целиком, раскрыть короткую, отметить описанные выше признаки и сравнить адрес со списками известных фишинговых и мошеннических сайтов. Чего он не может — открыть страницу и оценить её за вас, и ни один список не полон. Поэтому Verdetto сообщает «Предупреждений не найдено», а не «безопасно»: это значит, что ни одна из его проверок не сработала, а последняя проверка — та, которую делаете вы, читая адрес. Если код просит вас войти, ввести данные карты или что-то установить, закройте его и зайдите на сайт, который вы уже знаете.",
  "openedh": "Если вы уже открыли такой код",
  "openedp": "Закройте страницу. Если вы ввели пароль, смените его на настоящем сайте и везде, где ещё им пользовались. Если ввели данные карты, сообщите в банк. Если что-то установили, удалите это и запустите проверку тем защитным ПО, что уже есть на телефоне. Затем удалите код из истории, чтобы не открыть его снова случайно.",
  "callout": "Verdetto показывает каждую ссылку до того, как она откроется, раскрывает сокращённые и партнёрские ссылки при включённых онлайн-запросах и отмечает каждый из описанных признаков на вашем телефоне. Бесплатно, без рекламы, оплачено людьми, которые им пользуются. {home}.",
  "callout_link": "Посмотрите, что он умеет"
 },
 "hi": {
  "title": "QR कोड लिंक को खोलने से पहले उसकी जाँच कैसे करें",
  "desc": "टैप करने से पहले QR कोड के लिंक में देखने की छह बातें: डोमेन, छोटे लिंक, मिलते-जुलते नाम, कनेक्शन, डाउनलोड और कोड की जगह।",
  "meta": "{DATE} को अद्यतन। लगभग चार मिनट का पढ़ना।",
  "inshort": "<strong>संक्षेप में।</strong> QR कोड का लिंक खोलने से पहले: पूरा पता नहीं, डोमेन पढ़ें; छोटे किए गए लिंक को तब तक अज्ञात मानें जब तक वे विस्तारित न हों; मिलते-जुलते नामों पर नज़र रखें; <code>https</code> और कोई असामान्य पोर्ट न होने की जाँच करें; कोड जो भी दे, उसे कभी इंस्टॉल न करें; और पूछें कि कोड वहाँ क्यों है। एक स्कैनर आपको यह सब दिखा सकता है। वह आपको यह नहीं बता सकता कि कोई पेज सुरक्षित है।",
  "intro": "QR कोड बस लिंक टाइप करने का एक तरीका है ताकि आपको न करना पड़े। दिक्कत यह है कि लिंक तब तक अदृश्य है जब तक कोई चीज़ उसे पढ़े नहीं, और कई स्कैनर ऐप उसे उसी पल खोल देते हैं। पार्किंग मीटर, रेस्तराँ की मेज़, पोस्टर और ईमेल तक में नकली कोड ठीक इसी पर निर्भर करते हैं। समाधान सरल है: खोलने से पहले लिंक देखें। क्रम से यह देखें।",
  "s1h": "1. पूरा लिंक नहीं, डोमेन पढ़ें",
  "s1p": "डोमेन वह हिस्सा है जो <code>https://</code> के बाद और पहले अकेले स्लैश से पहले आता है। <code>https://accounts.example.com/login?ref=qr</code> में डोमेन <code>accounts.example.com</code> है, और सबसे महत्वपूर्ण हिस्सा अंतिम दो लेबल हैं, <code>example.com</code>। स्लैश के बाद का सब कुछ कुछ भी कह सकता है; आप कहाँ पहुँचेंगे यह डोमेन तय करता है। एक अच्छा स्कैनर डोमेन को अकेले बड़े अक्षरों में दिखाता है, ताकि आपको उसे लंबी स्ट्रिंग में ढूँढना न पड़े।",
  "s2h": "2. छोटे किए गए लिंक को अज्ञात मानें",
  "s2p": "bit.ly, t.co, tinyurl और ऐसी सेवाओं के लिंक जान-बूझकर अपना गंतव्य छिपाते हैं। इनमें से एक दिखाने वाला कोड तब तक कुछ नहीं बताता जब तक वह विस्तारित न हो। या तो पहले उसे ऐसे स्कैनर से विस्तारित करें जो छोटे लिंक का पीछा करके दिखाए कि वह कहाँ पहुँचता है, या उसे न खोलें।",
  "s3h": "3. मिलते-जुलते नामों पर नज़र रखें",
  "s3p": "सबसे पुरानी चाल ऐसा डोमेन है जो किसी परिचित जैसा पढ़ा जाए। अक्षर की जगह अंक (<code>paypa1.com</code>), अतिरिक्त शब्द या हाइफ़न (<code>paypal-secure.com</code>), गलत जगह रखा परिचित नाम (<code>paypal.com.example.net</code>, जहाँ डोमेन <code>example.net</code> है), और उसी आकार के दूसरी लिपि के अक्षरों पर नज़र रखें। अगर कोई नाम लगभग सही लगे, तो उसे गलत मानें जब तक आपने असली नाम स्वयं न टाइप किया हो।",
  "s4h": "4. कनेक्शन और पोर्ट जाँचें",
  "s4p": "<code>https://</code> के बजाय <code>http://</code> से शुरू होने वाला लिंक आपके टाइप किए सब कुछ को खुले में भेजता है। डोमेन के बाद संख्या वाला लिंक, जैसे <code>example.com:8080</code>, किसी साधारण वेबसाइट के अलावा किसी और चीज़ से बात कर रहा है। दोनों में से कोई धोखाधड़ी साबित नहीं करता, लेकिन दोनों में से कोई ऐसे कोड पर नहीं होना चाहिए जो आपसे साइन इन या भुगतान करवाए।",
  "s5h": "5. कोड जो दे, उसे इंस्टॉल न करें",
  "s5p": "<code>.apk</code> पर समाप्त होने वाला लिंक एक Android प्रोग्राम है, पेज नहीं। ऐप स्टोर से आते हैं, स्टिकर से नहीं। यही बात उन लिंक पर लागू होती है जो कुछ भी दिखाने से पहले \"एक अपडेट\" या \"एक व्यूअर\" इंस्टॉल करने की अनुमति माँगते हैं।",
  "s6h": "6. पूछें कि कोड वहाँ क्यों है",
  "s6p": "दूसरे QR कोड पर चिपकाया QR कोड, ऐसे पार्किंग मीटर पर कोड जिसमें पहले से भुगतान टर्मिनल है, अनजान नंबर से आए संदेश में कोड, रिफ़ंड या इनाम का वादा करने वाला कोड: जगह ही चेतावनी है। अपराधी स्टिकर छापते हैं क्योंकि स्टिकर सस्ते हैं। जब कोड वहाँ दिखे जहाँ स्वाभाविक रूप से कोई कोड नहीं होता, उसे छोड़ दें और सीधे आधिकारिक ऐप या वेबसाइट का उपयोग करें।",
  "canh": "स्कैनर आपको क्या बता सकता है और क्या नहीं",
  "canp": "स्कैनर आपको पूरा लिंक दिखा सकता है, छोटे लिंक को विस्तारित कर सकता है, ऊपर के पैटर्न चिह्नित कर सकता है और पते को ज्ञात फ़िशिंग और धोखाधड़ी साइटों की सूचियों से मिला सकता है। जो वह नहीं कर सकता, वह है पेज खोलकर आपके लिए उसका आकलन करना, और कोई सूची पूरी नहीं होती। इसीलिए Verdetto \"सुरक्षित\" के बजाय \"कोई चेतावनी नहीं मिली\" बताता है: इसका मतलब है कि इसकी कोई जाँच मेल नहीं खाई, और आख़िरी जाँच वह है जो आप पता पढ़कर करते हैं। अगर कोई कोड आपसे साइन इन करने, कार्ड विवरण देने या कुछ इंस्टॉल करने को कहे, तो उसे बंद करें और उस साइट पर जाएँ जिसे आप पहले से जानते हैं।",
  "openedh": "अगर आप पहले ही एक खोल चुके हैं",
  "openedp": "पेज बंद करें। अगर आपने पासवर्ड टाइप किया, तो असली साइट पर और जहाँ-जहाँ आपने उसका उपयोग किया, वहाँ उसे बदलें। अगर कार्ड विवरण दिए, तो अपने बैंक को बताएँ। अगर कुछ इंस्टॉल किया, तो उसे अनइंस्टॉल करें और फ़ोन में पहले से मौजूद सुरक्षा सॉफ़्टवेयर से स्कैन चलाएँ। फिर कोड को अपने इतिहास से हटा दें ताकि आप उसे गलती से फिर न खोलें।",
  "callout": "Verdetto हर लिंक को खुलने से पहले दिखाता है, ऑनलाइन लुकअप चालू होने पर छोटे किए गए और एफ़िलिएट लिंक को विस्तारित करता है, और ऊपर के हर पैटर्न को आपके फ़ोन पर चिह्नित करता है। मुफ़्त, बिना विज्ञापन, इसे इस्तेमाल करने वाले लोगों के पैसे से। {home}।",
  "callout_link": "देखें यह क्या करता है"
 },
 "ja": {
  "title": "開く前に QR コードのリンクを確認する方法",
  "desc": "QR コードのリンクをタップする前に見るべき六つのこと: ドメイン、短縮リンク、紛らわしい名前、接続、ダウンロード、そしてコードが貼られた場所。",
  "meta": "{DATE} 更新。読了まで約 4 分。",
  "inshort": "<strong>要点。</strong> QR コードのリンクを開く前に: アドレス全体ではなくドメインを読む。短縮リンクは展開されるまで不明なものとして扱う。紛らわしい名前に注意する。<code>https</code> であること、異常なポートがないことを確認する。コードが差し出すものを決してインストールしない。そして、なぜそのコードがそこにあるのかを考える。スキャナーはそのすべてを見せてくれます。ページが安全だと言うことはできません。",
  "intro": "QR コードは、リンクを自分で入力しなくてすむようにする手段にすぎません。問題は、何かが読み取るまでリンクが見えないこと、そして多くのスキャナーアプリが読み取った瞬間に開いてしまうことです。駐車メーター、レストランのテーブル、ポスター、さらにはメールに仕込まれた偽のコードは、まさにそれを当て込んでいます。対策は単純で、開く前にリンクを見ることです。見るべき点を順に挙げます。",
  "s1h": "1. リンク全体ではなくドメインを読む",
  "s1p": "ドメインとは <code>https://</code> の後、最初の単独のスラッシュの前の部分です。<code>https://accounts.example.com/login?ref=qr</code> ではドメインは <code>accounts.example.com</code> で、最も重要なのは末尾の二つのラベル、<code>example.com</code> です。スラッシュの後は何でも書けますが、どこに着地するかを決めるのはドメインです。良いスキャナーはドメインだけを大きく表示し、長い文字列の中から探させません。",
  "s2h": "2. 短縮リンクは不明なものとして扱う",
  "s2p": "bit.ly、t.co、tinyurl などのサービスを経由するリンクは、意図的に行き先を隠しています。それらを示すコードは、展開されるまで何も教えてくれません。短縮リンクをたどって行き先を示すスキャナーで先に展開するか、開かないことです。",
  "s3h": "3. 紛らわしい名前に注意する",
  "s3p": "最も古い手口は、見慣れた名前のように読めるドメインです。文字の代わりの数字（<code>paypa1.com</code>）、余分な単語やハイフン（<code>paypal-secure.com</code>）、見慣れた名前を間違った位置に置いたもの（<code>paypal.com.example.net</code>、ドメインは <code>example.net</code>）、同じ形をした別の文字体系の文字に注意してください。名前がほぼ正しく見えるなら、本物を自分で入力するまでは間違いとして扱いましょう。",
  "s4h": "4. 接続とポートを確認する",
  "s4p": "<code>https://</code> ではなく <code>http://</code> で始まるリンクは、入力したすべてを平文で送ります。<code>example.com:8080</code> のようにドメインの後に数字が付くリンクは、普通のウェブサイト以外の何かと通信しています。どちらも詐欺の証明ではありませんが、ログインや支払いを求めるコードにあってよいものでもありません。",
  "s5h": "5. コードが差し出すものをインストールしない",
  "s5p": "<code>.apk</code> で終わるリンクは Android のプログラムであり、ページではありません。アプリはストアから来るもので、ステッカーから来るものではありません。何かを見せる前に「アップデート」や「ビューアー」のインストール許可を求めるリンクも同じです。",
  "s6h": "6. なぜそのコードがそこにあるのかを考える",
  "s6p": "別の QR コードの上に貼られた QR コード、すでに支払い端末がある駐車メーターのコード、知らない番号からのメッセージ内のコード、返金や賞品を約束するコード: 貼られた場所そのものが警告です。犯罪者がステッカーを刷るのは、ステッカーが安いからです。自然にはコードがないはずの場所にコードが現れたら、飛ばして公式のアプリやサイトを直接使ってください。",
  "canh": "スキャナーが分かること、分からないこと",
  "canp": "スキャナーは、リンク全体を表示し、短縮リンクを展開し、上記のパターンを知らせ、アドレスを既知のフィッシングや詐欺サイトのリストと照合できます。できないのは、ページを開いてあなたの代わりに判断することで、完全なリストも存在しません。だから Verdetto は「安全」ではなく「警告は見つかりませんでした」と報告します。どのチェックにも該当しなかったという意味で、最後のチェックはアドレスを読むあなた自身が行います。コードがログインやカード情報の入力、何かのインストールを求めるなら、閉じて、すでに知っているサイトへ行ってください。",
  "openedh": "すでに開いてしまったら",
  "openedp": "ページを閉じます。パスワードを入力したなら、本物のサイトと、同じパスワードを使っていたすべての場所で変更します。カード情報を入力したなら、銀行に知らせます。何かをインストールしたなら、アンインストールし、端末にすでにあるセキュリティソフトでスキャンを実行します。それから、誤ってまた開かないように、そのコードを履歴から削除します。",
  "callout": "Verdetto はすべてのリンクを開く前に表示し、オンライン検索がオンのときは短縮リンクとアフィリエイトリンクを展開し、上記のパターンをそれぞれ端末内で知らせます。無料で、広告がなく、使う人の支えで成り立っています。{home}。",
  "callout_link": "できることを見る"
 },
 "zh-Hans": {
  "title": "如何在打开前检查二维码链接",
  "desc": "点开二维码链接前要看的六件事：域名、短链接、易混淆的名称、连接方式、下载，以及码出现的位置。",
  "meta": "更新于 {DATE}。约四分钟读完。",
  "inshort": "<strong>简而言之。</strong> 打开二维码里的链接之前：读域名，而不是整个地址；短链接在展开之前一律视为未知；留意易混淆的名称；确认是 <code>https</code> 且没有异常端口；绝不安装码交给你的任何东西；并问一问这个码为什么出现在这里。扫描器可以把这些都展示给你。它无法告诉你一个页面是安全的。",
  "intro": "二维码只是一种替你输入链接的方式。麻烦在于，链接在被读取之前是看不见的，而许多扫描应用一读到就立刻打开。停车计费器、餐桌、海报乃至电子邮件里的假码，靠的正是这一点。解决办法很简单：打开前先看链接。以下是要看的内容，按顺序。",
  "s1h": "1. 读域名，而不是整个链接",
  "s1p": "域名是 <code>https://</code> 之后、第一个单斜杠之前的部分。在 <code>https://accounts.example.com/login?ref=qr</code> 中，域名是 <code>accounts.example.com</code>，最要紧的是最后两段，<code>example.com</code>。斜杠之后的内容可以随便写；决定你落在哪里的是域名。好的扫描器会用大字单独显示域名，你不必在长串字符里去找。",
  "s2h": "2. 把短链接当作未知",
  "s2p": "经 bit.ly、t.co、tinyurl 及类似服务的链接故意隐藏了去向。显示这类链接的码在展开之前不能告诉你任何事。要么先用能跟随短链接并显示最终去向的扫描器展开它，要么不要打开。",
  "s3h": "3. 留意易混淆的名称",
  "s3p": "最老的花招是一个读起来像熟悉名称的域名。留意用数字替代字母（<code>paypa1.com</code>）、多出的单词或连字符（<code>paypal-secure.com</code>）、被塞到错误位置的熟悉名称（<code>paypal.com.example.net</code>，其域名是 <code>example.net</code>），以及来自另一套字母、形状相同的字符。如果一个名称看起来几乎对了，在你亲自输入真正的名称之前，都把它当作错的。",
  "s4h": "4. 检查连接方式和端口",
  "s4p": "以 <code>http://</code> 而非 <code>https://</code> 开头的链接，会把你输入的一切明文发送。域名后带数字的链接，例如 <code>example.com:8080</code>，是在和普通网站以外的东西通信。两者都不能证明是诈骗，但两者都不该出现在要你登录或付款的码上。",
  "s5h": "5. 不要安装码交给你的东西",
  "s5p": "以 <code>.apk</code> 结尾的链接是一个 Android 程序，不是页面。应用来自应用商店，不是来自贴纸。同样适用于那些在你看到任何内容之前就要求安装“更新”或“查看器”的链接。",
  "s6h": "6. 问一问这个码为什么在这里",
  "s6p": "贴在另一个二维码上面的二维码、已有支付终端的停车计费器上的码、来自陌生号码的短信里的码、承诺退款或奖品的码：位置本身就是警告。骗子印贴纸，因为贴纸便宜。当一个码出现在本不该有码的地方，跳过它，直接使用官方应用或网站。",
  "canh": "扫描器能告诉你什么，不能告诉你什么",
  "canp": "扫描器可以完整显示链接、展开短链接、标出上述模式，并把地址与已知钓鱼和诈骗网站名单比对。它做不到的是替你打开页面并作出判断，而且没有哪份名单是完整的。这就是为什么 Verdetto 报告“未发现警告”而不是“安全”：它意味着它的检查都没有命中，而最后一道检查是由你读地址来完成的。如果一个码要你登录、输入银行卡信息或安装东西，关掉它，去你已经知道的那个网站。",
  "openedh": "如果你已经打开了一个",
  "openedp": "关闭页面。如果你输入了密码，去真正的网站以及所有用过同一密码的地方修改它。如果你输入了银行卡信息，告知你的银行。如果你安装了什么，卸载它，并用手机上已有的安全软件扫描一次。然后从历史记录里删除这个码，免得不小心再次打开。",
  "callout": "Verdetto 在每个链接打开前显示它，在开启在线查询时展开短链接和联盟链接，并在你的手机上标出以上每一种模式。免费，无广告，由使用它的人付费。{home}。",
  "callout_link": "看看它能做什么"
 },
 "ar": {
  "title": "كيف تفحص رابط رمز QR قبل أن تفتحه",
  "desc": "ستة أشياء تنظر إليها في رابط رمز QR قبل أن تنقر: النطاق، والروابط المختصرة، والأسماء المتشابهة، والاتصال، والتنزيلات، ومكان الرمز.",
  "meta": "حُدّث في {DATE}. نحو أربع دقائق للقراءة.",
  "inshort": "<strong>باختصار.</strong> قبل أن تفتح رابطًا من رمز QR: اقرأ النطاق لا العنوان كله؛ واعتبر الروابط المختصرة غير معروفة حتى تُفكّ؛ وابحث عن الأسماء المتشابهة؛ وتحقق من <code>https</code> ومن عدم وجود منفذ غير معتاد؛ ولا تثبّت أبدًا شيئًا يمدّه إليك رمز؛ واسأل لماذا الرمز في مكانه. يستطيع القارئ أن يعرض لك كل ذلك. ولا يستطيع أن يقول لك إن الصفحة آمنة.",
  "intro": "رمز QR مجرد طريقة لكتابة رابط كي لا تكتبه أنت. والمشكلة أن الرابط غير مرئي حتى يقرأه شيء ما، وكثير من تطبيقات المسح تفتحه في اللحظة التي تقرؤه فيها. والرموز المزيفة على عدّادات مواقف السيارات وموائد المطاعم والملصقات وحتى في رسائل البريد تعتمد على ذلك تحديدًا. والحل بسيط: انظر إلى الرابط قبل أن تفتحه. وإليك ما تنظر إليه، بالترتيب.",
  "s1h": "1. اقرأ النطاق لا الرابط كله",
  "s1p": "النطاق هو الجزء بعد <code>https://</code> وقبل أول شرطة مائلة مفردة. في <code>https://accounts.example.com/login?ref=qr</code> النطاق هو <code>accounts.example.com</code>، والجزء الأهم هو آخر جزأين، <code>example.com</code>. وكل ما بعد الشرطة المائلة قد يقول أي شيء؛ فالنطاق هو الذي يقرر أين تصل. والقارئ الجيد يعرض النطاق وحده بخط كبير، فلا تضطر إلى البحث عنه في سلسلة طويلة.",
  "s2h": "2. اعتبر الروابط المختصرة غير معروفة",
  "s2p": "الروابط عبر bit.ly وt.co وtinyurl والخدمات المشابهة تخفي وجهتها عن قصد. والرمز الذي يعرض واحدًا منها لا يقول لك شيئًا حتى يُفكّ. إما أن تفكّه أولًا بقارئ يتبع الرابط المختصر ويعرض لك أين ينتهي، أو لا تفتحه.",
  "s3h": "3. ابحث عن الأسماء المتشابهة",
  "s3p": "أقدم حيلة هي نطاق يُقرأ كنطاق مألوف. انتبه إلى رقم يحل محل حرف (<code>paypa1.com</code>)، وكلمة أو شرطة زائدة (<code>paypal-secure.com</code>)، واسم مألوف في المكان الخطأ (<code>paypal.com.example.net</code>، حيث النطاق هو <code>example.net</code>)، وحروف من أبجدية أخرى ترسم الشكل نفسه. وإذا بدا الاسم صحيحًا تقريبًا، فاعتبره خطأ حتى تكتب الاسم الحقيقي بنفسك.",
  "s4h": "4. تحقق من الاتصال والمنفذ",
  "s4p": "الرابط الذي يبدأ بـ <code>http://</code> بدلًا من <code>https://</code> يرسل كل ما تكتبه مكشوفًا. والرابط الذي يحمل رقمًا بعد النطاق، مثل <code>example.com:8080</code>، يتحدث إلى شيء آخر غير موقع ويب عادي. ولا يثبت أي منهما احتيالًا، لكن لا مكان لأي منهما على رمز يطلب منك تسجيل الدخول أو الدفع.",
  "s5h": "5. لا تثبّت ما يمدّه إليك رمز",
  "s5p": "الرابط الذي ينتهي بـ <code>.apk</code> برنامج أندرويد لا صفحة. والتطبيقات تأتي من المتجر لا من الملصقات. وينطبق الأمر نفسه على الروابط التي تطلب الإذن بتثبيت «تحديث» أو «عارض» قبل أن ترى أي شيء.",
  "s6h": "6. اسأل لماذا الرمز هنا",
  "s6p": "رمز QR ملصق فوق رمز QR آخر، ورمز على عدّاد مواقف فيه محطة دفع أصلًا، ورمز في رسالة نصية من رقم لا تعرفه، ورمز يعدك باسترداد مال أو بجائزة: المكان هو التحذير. يطبع المحتالون الملصقات لأن الملصقات زهيدة. وعندما يظهر رمز حيث لا يكون رمز عادةً، فتجاوزه واستخدم التطبيق الرسمي أو الموقع الرسمي مباشرة.",
  "canh": "ما يستطيع القارئ أن يقوله لك وما لا يستطيع",
  "canp": "يستطيع القارئ أن يعرض لك الرابط كاملًا، ويفكّ الرابط المختصر، ويعلّم على الأنماط أعلاه، ويقارن العنوان بقوائم مواقع التصيّد والاحتيال المعروفة. وما لا يستطيعه هو أن يفتح الصفحة ويحكم عليها بدلًا منك، ولا توجد قائمة كاملة. ولهذا يقول Verdetto «لم يُعثر على تحذيرات» بدلًا من «آمن»: فذلك يعني أن أي فحص من فحوصاته لم يتطابق، والفحص الأخير هو الذي تجريه أنت بقراءة العنوان. وإذا طلب منك رمز تسجيل الدخول أو إدخال بيانات بطاقة أو تثبيت شيء، فأغلقه واذهب إلى الموقع الذي تعرفه أصلًا.",
  "openedh": "إذا كنت قد فتحت واحدًا بالفعل",
  "openedp": "أغلق الصفحة. وإن كتبت كلمة مرور، فغيّرها على الموقع الحقيقي وفي كل مكان آخر استخدمتها فيه. وإن أدخلت بيانات بطاقة، فأبلغ بنكك. وإن ثبّتت شيئًا، فأزله وشغّل فحصًا ببرنامج الحماية الموجود على الهاتف أصلًا. ثم احذف الرمز من سجلك كي لا تفتحه مرة أخرى عن طريق الخطأ.",
  "callout": "يعرض Verdetto كل رابط قبل أن يُفتح، ويفكّ الروابط المختصرة وروابط الإحالة عند تفعيل البحث عبر الإنترنت، ويعلّم على كل نمط من الأنماط أعلاه على هاتفك. مجاني، بلا إعلانات، يدفع ثمنه من يستخدمونه. {home}.",
  "callout_link": "شاهد ماذا يفعل"
 }
}


def guide_body(t, code):
    """The guide from its strings table, in the English page's structure; the callout links to the same-language home."""
    home = f'<a href="{href(localized("index.html", code))}">{t["callout_link"]}</a>'
    parts = [f'<div class="prose">', f'<h1>{t["title"]}</h1>', f'<p class="meta">{t["meta"].replace("{DATE}", DATE)}</p>', '',
             f'<div class="card"><p>{t["inshort"]}</p></div>', '', f'<p>{t["intro"]}</p>']
    for k in ("s1", "s2", "s3", "s4", "s5", "s6"):
        parts += ['', f'<h2>{t[k + "h"]}</h2>', f'<p>{t[k + "p"]}</p>']
    parts += ['', f'<h2>{t["canh"]}</h2>', f'<p>{t["canp"]}</p>', '', f'<h2>{t["openedh"]}</h2>', f'<p>{t["openedp"]}</p>', '',
              f'<div class="card callout"><p>{t["callout"].replace("{home}", home)}</p></div>', '</div>']
    return "\n" + "\n".join(parts) + "\n"


def guide_ld(t, code):
    return {"@type": "Article", "headline": t["title"], "description": t["desc"], "inLanguage": code, "datePublished": DATE, "dateModified": DATE,
            "author": ORG, "publisher": ORG, "mainEntityOfPage": url(LOCAL["check-qr-code-link.html"][code]),
            "image": SITE + "/og/" + LOCAL["check-qr-code-link.html"][code][:-5] + ".png"}


LOCAL["check-qr-code-link.html"] = family_pages("check-qr-code-link.html")

def not_found():
        return f"""
    <h1>That page is not here.</h1>
    <p>The address may have changed, or the code that brought you here was wrong. Try one of these:</p>
    <ul>
      <li><a href="{href('index.html')}">Home</a></li>
      <li><a href="{href('features.html')}">Everything it does</a></li>
      <li><a href="{href('privacy.html')}">Privacy policy</a></li>
      <li><a href="{href('terms.html')}">Terms of use</a></li>
      <li><a href="{href('support.html')}">Help</a></li>
      <li><a href="{href('check-qr-code-link.html')}">How to check a QR code link before you open it</a></li>
      <li><a href="{href('support-the-work.html')}">Support the work</a></li>
    </ul>
    <ul class="langs404">
      <li lang="de"><strong>{LANG_LABELS['de']}:</strong> Diese Seite gibt es hier nicht. <a href="{href(localized('index.html', 'de'))}" hreflang="de">Startseite</a></li>
      <li lang="es"><strong>{LANG_LABELS['es']}:</strong> Esa página no está aquí. <a href="{href(localized('index.html', 'es'))}" hreflang="es">Inicio</a></li>
      <li lang="fr"><strong>{LANG_LABELS['fr']}:</strong> Cette page n'est pas ici. <a href="{href(localized('index.html', 'fr'))}" hreflang="fr">Accueil</a></li>
      <li lang="pt-BR"><strong>{LANG_LABELS['pt-BR']}:</strong> Essa página não está aqui. <a href="{href(localized('index.html', 'pt-BR'))}" hreflang="pt-BR">Início</a></li>
      <li lang="id"><strong>{LANG_LABELS['id']}:</strong> Halaman itu tidak ada di sini. <a href="{href(localized('index.html', 'id'))}" hreflang="id">Beranda</a></li>
      <li lang="ru"><strong>{LANG_LABELS['ru']}:</strong> Такой страницы здесь нет. <a href="{href(localized('index.html', 'ru'))}" hreflang="ru">Главная</a></li>
      <li lang="hi"><strong>{LANG_LABELS['hi']}:</strong> वह पृष्ठ यहाँ नहीं है। <a href="{href(localized('index.html', 'hi'))}" hreflang="hi">मुखपृष्ठ</a></li>
      <li lang="ja"><strong>{LANG_LABELS['ja']}:</strong> そのページはここにありません。 <a href="{href(localized('index.html', 'ja'))}" hreflang="ja">ホーム</a></li>
      <li lang="zh-Hans"><strong>{LANG_LABELS['zh-Hans']}:</strong> 这个页面不在这里。 <a href="{href(localized('index.html', 'zh-Hans'))}" hreflang="zh-Hans">首页</a></li>
      <li lang="ar"><strong>{LANG_LABELS['ar']}:</strong> هذه الصفحة ليست هنا. <a href="{href(localized('index.html', 'ar'))}" hreflang="ar">الصفحة الرئيسية</a></li>
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

REPORT_T = {
 "de": {
  "title": "Meldung an Verdetto",
  "desc": "Melde einen Link, der nach Betrug aussieht, einen falsch gelesenen Code oder etwas anderes, das in Verdetto nicht stimmt. Ein Mensch prüft jede Meldung.",
  "h1": "Meldung an {V}",
  "meta": "Ein Link, der nach Betrug aussieht, ein Code, den die App falsch gelesen hat, falsche Angaben oder etwas anderes, das nicht stimmt.",
  "card1": "Ein Mensch prüft jede Meldung. Nichts wird automatisch in die Sicherheitsliste aufgenommen, und Verdetto sagt nie, dass ein Link sicher ist. Bitte keine Passwörter, Zahlungsdaten oder persönlichen Dokumente angeben; wenn du aus der App kommst, ist der gescannte Text bereits eingetragen, und du kannst alles Private entfernen, bevor du absendest.",
  "card2_lead": "Was danach passiert.",
  "card2": "Eine Meldung über Betrug oder einen Eintrag aus Versehen wird zu einem Fall im öffentlichen <a href=\"{ISSUES}\">Listen-Repository</a>: die gemeldete Adresse, was die Prüfungen gefunden haben und die Entscheidung, nie deine E-Mail oder deine Beschreibung. Der Fall wird nach festen Regeln entschieden, und nur eine Seite, die neben einem Marken- oder Domain-Warnzeichen ein Anmelde- oder Zahlungsformular zeigt, wird gelistet.",
  "card3_lead": "Aus Versehen gelistet?",
  "card3": "Wähle „My site or link is listed by mistake“. Die Seite wird noch am selben Tag erneut abgerufen; zeigt sie kein Anmelde- oder Zahlungsformular mehr, wird der Eintrag beim nächsten Listen-Update aus allen Quellen unterdrückt, und die öffentliche Quelle, die ihn gelistet hat, erhält von uns eine Fehlalarm-Meldung. Unsere eigenen Einträge und ihre Belege sind im <a href=\"{OWN}\">Listen-Repository</a> öffentlich.",
  "iframe_title": "Meldeformular",
  "loading": "Wird geladen…",
  "fallback": "Wenn das Formular hier nicht lädt, <a id=\"report-open\" href=\"{FORM_URL}\" rel=\"noopener\" target=\"_blank\">öffne es in einem neuen Tab</a> oder schreib an <a href=\"mailto:{EMAIL}\">{EMAIL}</a>. Das Formular ist ein Google-Formular und selbst auf Englisch; was du sendest, wird im Google-Konto von Verdetto gespeichert und nur zur Bearbeitung deiner Meldung verwendet. Details stehen in der <a href=\"{PRIVACY_HREF}\">Datenschutzerklärung</a>."
 },
 "es": {
  "title": "Informar a Verdetto",
  "desc": "Informa de un enlace que parece una estafa, de un código mal leído o de cualquier otra cosa que no esté bien en Verdetto. Una persona revisa cada informe.",
  "h1": "Informar a {V}",
  "meta": "Un enlace que parece una estafa, un código que la app leyó mal, datos equivocados o cualquier otra cosa que no esté bien.",
  "card1": "Una persona revisa cada informe. Nada se añade a la lista de seguridad automáticamente, y Verdetto nunca dice que un enlace sea seguro. No incluyas contraseñas, datos de pago ni documentos personales; si vienes desde la app, el texto escaneado ya está rellenado y puedes quitar lo que sea privado antes de enviarlo.",
  "card2_lead": "Qué pasa después.",
  "card2": "Un informe de estafa o de inclusión por error se convierte en un caso en el <a href=\"{ISSUES}\">repositorio público de la lista</a>: la dirección que informaste, lo que encontraron las comprobaciones y la decisión, nunca tu correo ni tu descripción. El caso se decide con reglas fijas, y solo se incluye una página que muestre un formulario de credenciales o de pago junto a una señal de alerta de marca o de dominio.",
  "card3_lead": "¿Incluido por error?",
  "card3": "Elige «My site or link is listed by mistake». La página se vuelve a consultar el mismo día; si ya no muestra un formulario de credenciales o de pago, la entrada se suprime de todas las fuentes en la siguiente actualización de la lista, y la fuente pública que la incluyó recibe de nosotros un aviso de falso positivo. Nuestras propias entradas y sus pruebas son públicas en el <a href=\"{OWN}\">repositorio de la lista</a>.",
  "iframe_title": "Formulario de informe",
  "loading": "Cargando…",
  "fallback": "Si el formulario no carga aquí, <a id=\"report-open\" href=\"{FORM_URL}\" rel=\"noopener\" target=\"_blank\">ábrelo en una pestaña nueva</a> o escribe a <a href=\"mailto:{EMAIL}\">{EMAIL}</a>. El formulario es un formulario de Google y está en inglés; lo que envías se guarda en la cuenta de Google de Verdetto y se usa solo para atender tu informe. Los detalles están en la <a href=\"{PRIVACY_HREF}\">política de privacidad</a>."
 },
 "fr": {
  "title": "Signaler à Verdetto",
  "desc": "Signalez un lien qui ressemble à une arnaque, un code mal lu ou toute autre chose qui ne va pas dans Verdetto. Une personne examine chaque signalement.",
  "h1": "Signaler à {V}",
  "meta": "Un lien qui ressemble à une arnaque, un code que l'application a mal lu, des informations fausses ou toute autre chose qui ne va pas.",
  "card1": "Une personne examine chaque signalement. Rien n'est ajouté automatiquement à la liste de sécurité, et Verdetto ne dit jamais qu'un lien est sûr. N'indiquez ni mots de passe, ni données de paiement, ni documents personnels ; si vous venez de l'application, le texte scanné est déjà rempli et vous pouvez retirer ce qui est privé avant d'envoyer.",
  "card2_lead": "Ce qui se passe ensuite.",
  "card2": "Un signalement d'arnaque ou d'inscription par erreur devient un dossier dans le <a href=\"{ISSUES}\">dépôt public de la liste</a> : l'adresse signalée, ce que les vérifications ont trouvé et la décision, jamais votre e-mail ni votre description. Le dossier est tranché selon des règles fixes, et seule une page qui affiche un formulaire d'identifiants ou de paiement à côté d'un signal d'alerte de marque ou de domaine est inscrite.",
  "card3_lead": "Inscrit par erreur ?",
  "card3": "Choisissez « My site or link is listed by mistake ». La page est rechargée le jour même ; si elle n'affiche plus de formulaire d'identifiants ou de paiement, l'entrée est retirée de toutes les sources à la prochaine mise à jour de la liste, et le flux public qui l'avait inscrite reçoit de notre part un signalement de faux positif. Nos propres entrées et leurs preuves sont publiques dans le <a href=\"{OWN}\">dépôt de la liste</a>.",
  "iframe_title": "Formulaire de signalement",
  "loading": "Chargement…",
  "fallback": "Si le formulaire ne se charge pas ici, <a id=\"report-open\" href=\"{FORM_URL}\" rel=\"noopener\" target=\"_blank\">ouvrez-le dans un nouvel onglet</a> ou écrivez à <a href=\"mailto:{EMAIL}\">{EMAIL}</a>. Le formulaire est un formulaire Google, en anglais ; ce que vous envoyez est stocké dans le compte Google de Verdetto et sert uniquement à traiter votre signalement. Les détails sont dans la <a href=\"{PRIVACY_HREF}\">politique de confidentialité</a>."
 },
 "pt-BR": {
  "title": "Relatar ao Verdetto",
  "desc": "Relate um link que parece golpe, um código lido errado ou qualquer outra coisa que não esteja certa no Verdetto. Uma pessoa analisa cada relato.",
  "h1": "Relatar ao {V}",
  "meta": "Um link que parece golpe, um código que o app leu errado, informações erradas ou qualquer outra coisa que não esteja certa.",
  "card1": "Uma pessoa analisa cada relato. Nada entra na lista de segurança automaticamente, e o Verdetto nunca diz que um link é seguro. Não inclua senhas, dados de pagamento ou documentos pessoais; se você veio do app, o texto escaneado já está preenchido, e você pode remover qualquer coisa privada antes de enviar.",
  "card2_lead": "O que acontece depois.",
  "card2": "Um relato de golpe ou de inclusão por engano vira um caso no <a href=\"{ISSUES}\">repositório público da lista</a>: o endereço relatado, o que as verificações encontraram e a decisão, nunca seu e-mail ou sua descrição. O caso é decidido por regras fixas, e só entra na lista uma página que mostre um formulário de credenciais ou de pagamento ao lado de um sinal de alerta de marca ou de domínio.",
  "card3_lead": "Incluído por engano?",
  "card3": "Escolha \"My site or link is listed by mistake\". A página é consultada de novo no mesmo dia; se ela não mostrar mais um formulário de credenciais ou de pagamento, a entrada é suprimida de todas as fontes na próxima atualização da lista, e a fonte pública que a incluiu recebe de nós um aviso de falso positivo. Nossas próprias entradas e suas evidências são públicas no <a href=\"{OWN}\">repositório da lista</a>.",
  "iframe_title": "Formulário de relato",
  "loading": "Carregando…",
  "fallback": "Se o formulário não carregar aqui, <a id=\"report-open\" href=\"{FORM_URL}\" rel=\"noopener\" target=\"_blank\">abra-o em uma nova aba</a> ou escreva para <a href=\"mailto:{EMAIL}\">{EMAIL}</a>. O formulário é um Formulário Google e está em inglês; o que você envia fica guardado na conta Google do Verdetto e é usado só para tratar seu relato. Os detalhes estão na <a href=\"{PRIVACY_HREF}\">política de privacidade</a>."
 },
 "id": {
  "title": "Laporkan ke Verdetto",
  "desc": "Laporkan tautan yang tampak seperti penipuan, kode yang salah dibaca, atau hal lain yang tidak benar di Verdetto. Setiap laporan ditinjau oleh manusia.",
  "h1": "Laporkan ke {V}",
  "meta": "Tautan yang tampak seperti penipuan, kode yang salah dibaca aplikasi, rincian yang keliru, atau hal lain yang tidak benar.",
  "card1": "Setiap laporan ditinjau oleh manusia. Tidak ada yang ditambahkan ke daftar keamanan secara otomatis, dan Verdetto tidak pernah mengatakan sebuah tautan aman. Jangan sertakan kata sandi, data pembayaran, atau dokumen pribadi; jika Anda datang dari aplikasi, teks hasil pindaian sudah terisi, dan Anda bisa menghapus apa pun yang pribadi sebelum mengirim.",
  "card2_lead": "Apa yang terjadi selanjutnya.",
  "card2": "Laporan penipuan atau salah daftar menjadi sebuah kasus di <a href=\"{ISSUES}\">repositori publik daftar</a>: alamat yang Anda laporkan, temuan pemeriksaan, dan keputusannya, tidak pernah email atau uraian Anda. Kasus diputus dengan aturan tetap, dan hanya halaman yang menampilkan formulir kredensial atau pembayaran di samping tanda peringatan merek atau domain yang didaftar.",
  "card3_lead": "Terdaftar karena keliru?",
  "card3": "Pilih \"My site or link is listed by mistake\". Halaman diambil lagi pada hari yang sama; jika tidak lagi menampilkan formulir kredensial atau pembayaran, entri itu ditekan dari semua sumber pada pembaruan daftar berikutnya, dan umpan publik yang mendaftarkannya menerima laporan positif palsu dari kami. Entri kami sendiri dan buktinya bersifat publik di <a href=\"{OWN}\">repositori daftar</a>.",
  "iframe_title": "Formulir laporan",
  "loading": "Memuat…",
  "fallback": "Jika formulir tidak muncul di sini, <a id=\"report-open\" href=\"{FORM_URL}\" rel=\"noopener\" target=\"_blank\">buka di tab baru</a>, atau tulis ke <a href=\"mailto:{EMAIL}\">{EMAIL}</a>. Formulir ini adalah Google Formulir dan berbahasa Inggris; apa yang Anda kirim disimpan di akun Google Verdetto dan hanya dipakai untuk menangani laporan Anda. Rinciannya ada di <a href=\"{PRIVACY_HREF}\">kebijakan privasi</a>."
 },
 "ru": {
  "title": "Сообщить в Verdetto",
  "desc": "Сообщите о ссылке, похожей на мошенничество, о неверно прочитанном коде или о чём-то ещё, что не так в Verdetto. Каждое сообщение проверяет человек.",
  "h1": "Сообщить в {V}",
  "meta": "Ссылка, похожая на мошенничество, код, который приложение прочитало неверно, ошибочные сведения или что-то ещё, что не так.",
  "card1": "Каждое сообщение проверяет человек. Ничто не попадает в список безопасности автоматически, и Verdetto никогда не говорит, что ссылка безопасна. Не указывайте пароли, платёжные данные и личные документы; если вы пришли из приложения, отсканированный текст уже заполнен, и всё личное можно убрать перед отправкой.",
  "card2_lead": "Что будет дальше.",
  "card2": "Сообщение о мошенничестве или об ошибочном внесении становится делом в <a href=\"{ISSUES}\">публичном репозитории списка</a>: указанный вами адрес, что нашли проверки и решение, но никогда ваша почта или ваше описание. Дело решается по фиксированным правилам, и в список попадает только страница, показывающая форму входа или оплаты рядом с признаком опасности по бренду или домену.",
  "card3_lead": "Внесено по ошибке?",
  "card3": "Выберите «My site or link is listed by mistake». Страница запрашивается снова в тот же день; если она больше не показывает форму входа или оплаты, запись подавляется во всех источниках при следующем обновлении списка, а публичный источник, внёсший её, получает от нас сообщение о ложном срабатывании. Наши собственные записи и их доказательства открыты в <a href=\"{OWN}\">репозитории списка</a>.",
  "iframe_title": "Форма сообщения",
  "loading": "Загрузка…",
  "fallback": "Если форма здесь не загружается, <a id=\"report-open\" href=\"{FORM_URL}\" rel=\"noopener\" target=\"_blank\">откройте её в новой вкладке</a> или напишите на <a href=\"mailto:{EMAIL}\">{EMAIL}</a>. Это Google Форма, и она на английском; отправленное хранится в аккаунте Google Verdetto и используется только для обработки вашего сообщения. Подробности в <a href=\"{PRIVACY_HREF}\">политике конфиденциальности</a>."
 },
 "hi": {
  "title": "Verdetto को रिपोर्ट करें",
  "desc": "धोखाधड़ी जैसा दिखने वाला लिंक, गलत पढ़ा गया कोड या Verdetto में जो कुछ भी ठीक नहीं है, उसकी रिपोर्ट करें। हर रिपोर्ट को एक व्यक्ति देखता है।",
  "h1": "{V} को रिपोर्ट करें",
  "meta": "धोखाधड़ी जैसा दिखने वाला लिंक, ऐप ने जो कोड गलत पढ़ा, गलत जानकारी, या कुछ और जो ठीक नहीं है।",
  "card1": "हर रिपोर्ट को एक व्यक्ति देखता है। सुरक्षा सूची में कुछ भी अपने आप नहीं जोड़ा जाता, और Verdetto कभी नहीं कहता कि कोई लिंक सुरक्षित है। कृपया पासवर्ड, भुगतान विवरण या निजी दस्तावेज़ शामिल न करें; अगर आप ऐप से यहाँ आए हैं, तो स्कैन किया गया टेक्स्ट पहले से भरा है, और भेजने से पहले आप कुछ भी निजी हटा सकते हैं।",
  "card2_lead": "आगे क्या होता है।",
  "card2": "धोखाधड़ी या गलती से सूचीबद्ध होने की रिपोर्ट सार्वजनिक <a href=\"{ISSUES}\">सूची रिपॉज़िटरी</a> में एक केस बन जाती है: आपके द्वारा रिपोर्ट किया गया पता, जाँचों में क्या मिला, और निर्णय; आपका ईमेल या आपका विवरण कभी नहीं। केस तय नियमों से निर्णीत होता है, और केवल वही पेज सूचीबद्ध होता है जो किसी ब्रांड या डोमेन चेतावनी संकेत के साथ क्रेडेंशियल या भुगतान फ़ॉर्म दिखाता है।",
  "card3_lead": "गलती से सूचीबद्ध?",
  "card3": "\"My site or link is listed by mistake\" चुनें। पेज उसी दिन फिर से लाया जाता है; अगर उसमें अब क्रेडेंशियल या भुगतान फ़ॉर्म नहीं है, तो अगली सूची अपडेट में प्रविष्टि हर स्रोत से हटा दी जाती है, और जिस सार्वजनिक फ़ीड ने उसे सूचीबद्ध किया था, उसे हमारी ओर से गलत-सकारात्मक रिपोर्ट मिलती है। हमारी अपनी प्रविष्टियाँ और उनके प्रमाण <a href=\"{OWN}\">सूची रिपॉज़िटरी</a> में सार्वजनिक हैं।",
  "iframe_title": "रिपोर्ट फ़ॉर्म",
  "loading": "लोड हो रहा है…",
  "fallback": "अगर फ़ॉर्म यहाँ लोड न हो, तो <a id=\"report-open\" href=\"{FORM_URL}\" rel=\"noopener\" target=\"_blank\">इसे नए टैब में खोलें</a>, या <a href=\"mailto:{EMAIL}\">{EMAIL}</a> पर लिखें। यह फ़ॉर्म एक Google फ़ॉर्म है और अंग्रेज़ी में है; आप जो भेजते हैं वह Verdetto के Google खाते में रखा जाता है और केवल आपकी रिपोर्ट को निपटाने के लिए इस्तेमाल होता है। विवरण <a href=\"{PRIVACY_HREF}\">गोपनीयता नीति</a> में है।"
 },
 "ja": {
  "title": "Verdetto に報告",
  "desc": "詐欺のように見えるリンク、誤って読み取られたコード、その他 Verdetto でおかしい点を報告してください。すべての報告を人が確認します。",
  "h1": "{V} に報告",
  "meta": "詐欺のように見えるリンク、アプリが誤って読み取ったコード、間違った情報、その他おかしい点。",
  "card1": "すべての報告を人が確認します。安全リストに自動で追加されるものはなく、Verdetto はリンクが安全だとは決して言いません。パスワード、支払い情報、個人の書類は含めないでください。アプリから来た場合は読み取ったテキストがすでに入力されており、送信前に私的な部分を削除できます。",
  "card2_lead": "この後の流れ。",
  "card2": "詐欺や誤登録の報告は、公開の<a href=\"{ISSUES}\">リストのリポジトリ</a>で一件の案件になります。報告されたアドレス、確認で見つかったこと、そして判断が記録され、あなたのメールアドレスや説明は決して含まれません。案件は固定の規則で判断され、ブランドやドメインの警告サインの横に認証情報や支払いのフォームを表示しているページだけが登録されます。",
  "card3_lead": "誤って登録された？",
  "card3": "「My site or link is listed by mistake」を選んでください。ページは同じ日に再取得され、認証情報や支払いのフォームがもう表示されなければ、次のリスト更新ですべてのソースからその項目が除外され、登録した公開フィードには私たちから誤検知の報告が送られます。私たち自身の項目とその根拠は<a href=\"{OWN}\">リストのリポジトリ</a>で公開されています。",
  "iframe_title": "報告フォーム",
  "loading": "読み込み中…",
  "fallback": "フォームがここに表示されない場合は、<a id=\"report-open\" href=\"{FORM_URL}\" rel=\"noopener\" target=\"_blank\">新しいタブで開く</a>か、<a href=\"mailto:{EMAIL}\">{EMAIL}</a> までお書きください。フォームは Google フォームで、英語です。送信内容は Verdetto の Google アカウントに保存され、報告の対応にのみ使われます。詳細は<a href=\"{PRIVACY_HREF}\">プライバシーポリシー</a>にあります。"
 },
 "zh-Hans": {
  "title": "向 Verdetto 报告",
  "desc": "报告看起来像诈骗的链接、被误读的码，或 Verdetto 中任何不对的地方。每一份报告都由人工审核。",
  "h1": "向 {V} 报告",
  "meta": "看起来像诈骗的链接、应用读错的码、错误的信息，或任何其他不对的地方。",
  "card1": "每一份报告都由人工审核。没有任何内容会自动加入安全列表，Verdetto 也从不说某个链接是安全的。请不要填写密码、付款信息或个人证件；如果您从应用跳转而来，扫描到的文本已经填好，发送前可以删除任何私密内容。",
  "card2_lead": "接下来会发生什么。",
  "card2": "诈骗或误列报告会成为公开<a href=\"{ISSUES}\">列表仓库</a>中的一个案例：您报告的地址、检查发现的内容和裁定结果，绝不包含您的邮箱或描述。案例按固定规则裁定，只有在品牌或域名警告迹象旁显示凭据或付款表单的页面才会被列入。",
  "card3_lead": "被误列了？",
  "card3": "请选择“My site or link is listed by mistake”。该页面会在当天重新抓取；如果不再显示凭据或付款表单，该条目会在下次列表更新时从所有来源中移除，列入它的公开源也会收到我们的误报反馈。我们自己的条目及其证据在<a href=\"{OWN}\">列表仓库</a>中公开。",
  "iframe_title": "报告表单",
  "loading": "正在加载…",
  "fallback": "如果表单没有在此加载，请<a id=\"report-open\" href=\"{FORM_URL}\" rel=\"noopener\" target=\"_blank\">在新标签页中打开</a>，或写信至 <a href=\"mailto:{EMAIL}\">{EMAIL}</a>。该表单是 Google 表单，且为英文；您提交的内容保存在 Verdetto 的 Google 账户中，仅用于处理您的报告。详情见<a href=\"{PRIVACY_HREF}\">隐私政策</a>。"
 },
 "ar": {
  "title": "أبلغ Verdetto",
  "desc": "أبلغ عن رابط يبدو احتياليًا، أو رمز قُرئ خطأً، أو أي شيء آخر غير صحيح في Verdetto. يراجع شخصٌ كل بلاغ.",
  "h1": "أبلغ {V}",
  "meta": "رابط يبدو احتياليًا، أو رمز قرأه التطبيق خطأً، أو معلومات خاطئة، أو أي شيء آخر غير صحيح.",
  "card1": "يراجع شخصٌ كل بلاغ. لا يُضاف شيء إلى قائمة الأمان تلقائيًا، ولا يقول Verdetto أبدًا إن رابطًا ما آمن. يُرجى عدم إدراج كلمات المرور أو بيانات الدفع أو المستندات الشخصية؛ وإذا جئت من التطبيق فالنص الممسوح مُدخل مسبقًا، ويمكنك إزالة أي شيء خاص قبل الإرسال.",
  "card2_lead": "ما الذي يحدث بعد ذلك.",
  "card2": "يتحول بلاغ الاحتيال أو الإدراج الخاطئ إلى حالة في <a href=\"{ISSUES}\">مستودع القائمة العام</a>: العنوان الذي أبلغت عنه، وما وجدته الفحوص، والقرار، ولا يُنشر بريدك أو وصفك أبدًا. تُقرَّر الحالة بقواعد ثابتة، ولا تُدرَج إلا صفحة تعرض نموذج بيانات دخول أو دفع بجوار علامة تحذير تتعلق بعلامة تجارية أو نطاق.",
  "card3_lead": "أُدرج خطأً؟",
  "card3": "اختر «My site or link is listed by mistake». تُجلَب الصفحة مجددًا في اليوم نفسه؛ فإن لم تَعُد تعرض نموذج بيانات دخول أو دفع، يُحجب المدخل من كل المصادر في تحديث القائمة التالي، ويتلقى المصدر العام الذي أدرجه بلاغًا منا عن نتيجة إيجابية زائفة. مدخلاتنا وأدلتها علنية في <a href=\"{OWN}\">مستودع القائمة</a>.",
  "iframe_title": "نموذج البلاغ",
  "loading": "جارٍ التحميل…",
  "fallback": "إذا لم يُحمَّل النموذج هنا، <a id=\"report-open\" href=\"{FORM_URL}\" rel=\"noopener\" target=\"_blank\">افتحه في علامة تبويب جديدة</a>، أو اكتب إلى <a href=\"mailto:{EMAIL}\">{EMAIL}</a>. النموذج نموذج Google وهو بالإنجليزية؛ وما ترسله يُخزَّن في حساب Google الخاص بـ Verdetto ويُستخدم فقط لمعالجة بلاغك. التفاصيل في <a href=\"{PRIVACY_HREF}\">سياسة الخصوصية</a>."
 }
}


def report_body(t, code):
    """The report page from its strings table: the same three cards, the same English-only Google Form and prefill script,
    links to the same-language privacy policy."""
    V = '<span class="lockup"><svg aria-hidden="true"><use href="#mark"/></svg>Verdetto</span>'
    issues = "https://github.com/verdettoqr/link-safety-list/issues?q=label%3Acase"
    own = "https://github.com/verdettoqr/link-safety-list/tree/main/own"
    def fill(x):
        return (x.replace("{ISSUES}", issues).replace("{OWN}", own).replace("{FORM_URL}", FORM_URL)
                .replace("{EMAIL}", EMAIL).replace("{PRIVACY_HREF}", href(localized("privacy.html", code))))
    return (f'\n<div class="prose">\n<h1>{t["h1"].replace("{V}", V)}</h1>\n<p class="meta">{t["meta"]}</p>\n\n'
            f'<div class="card"><p>{t["card1"]}</p></div>\n'
            f'<div class="card"><p><strong>{t["card2_lead"]}</strong> {fill(t["card2"])}</p></div>\n'
            f'<div class="card"><p><strong>{t["card3_lead"]}</strong> {fill(t["card3"])}</p></div>\n\n'
            f'<iframe id="report-form" title="{t["iframe_title"]}" src="{FORM_URL}?embedded=true" width="100%" height="1900" frameborder="0" marginheight="0" marginwidth="0" loading="lazy">{t["loading"]}</iframe>\n\n'
            f'<p>{fill(t["fallback"])}</p>\n</div>\n<script>{REPORT_SCRIPT}</script>\n')


LOCAL["report.html"] = family_pages("report.html")


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
  <li>Reads {len(FORMATS_READ)} kinds of codes, measured on the September 4, 2026 validation run, including EAN, UPC, Code 128, Data Matrix, PDF417, and Aztec.</li>
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
  <li><a href="verdetto-code-light.svg">The Verdetto code, SVG</a> (teal on white; <a href="verdetto-code-dark.svg">white on black</a>), as PNG <a href="verdetto-code-light-on-white.png">on white</a>, <a href="verdetto-code-dark-on-black.png">on black</a>, or transparent (<a href="verdetto-code-light-transparent.png">teal</a>, <a href="verdetto-code-dark-transparent.png">white</a>), and the <a href="verdetto-table-card.pdf">printable table card</a> (<a href="verdetto-table-card.png">PNG</a>). It opens https://verdettoqr.com and nothing else; any camera app reads it.</li>
</ul>
<p>Please do not alter the icon's colors or add effects; the mark is the brand.</p>
<p>Verdetto and the Verdetto QR mark are trademarks; a United States application for VERDETTO is pending (serial no. 50092495).</p>

<h2>Where to find us</h2>
<ul>
""" + "".join(f'  <li>{k}: <a href="{v}">{v}</a></li>\n' for k, v in SOCIAL.items()) + f"""  <li>Contact: <a href="mailto:{EMAIL}">{EMAIL}</a></li>
</ul>
</div>
"""

PRESS_T = {
 "de": {
  "title": "Pressematerial",
  "desc": "Die Beschreibung in einem Satz, der Standardtext, prüfbare Fakten und Bildmaterial zum Schreiben über Verdetto: QR & Barcode Scanner.",
  "meta": "Alles, was du brauchst, um Verdetto genau zu beschreiben, an einem Ort. Zitiere frei; der Satz unten ist der, den wir überall verwenden.",
  "lead": "In einem Satz.",
  "sentence": "Verdetto ist ein kostenloser QR-Code- und Barcode-Scanner für Android ohne Werbung und ohne falsche Buttons. Er zeigt den Link, bevor er sich öffnet, ist dafür gebaut, beschädigte Codes zu lesen, und prüft gescannte Inhalte auf dem Telefon auf Warnzeichen. Er sagt nie, dass etwas sicher ist: „Keine Warnungen gefunden“ heißt, dass keine seiner Prüfungen angeschlagen hat.",
  "boiler_h": "Standardtext",
  "boiler": "Verdetto: QR &amp; Barcode Scanner ist eine kostenlose Android-App von Verdetto, einem einzelnen Entwickler in Virginia. Sie liest QR-Codes und Barcodes, auch beschädigte, zeigt der Person genau, was ein Code enthält, bevor sich etwas öffnet, und prüft Links, WLAN-Netzwerke, Zahlungsadressen und Telefonnummern direkt auf dem Telefon auf bekannte Warnzeichen. Ihre Liste bekannter Phishing- und Betrugseinträge wird offen aus öffentlichen Quellen zusammengestellt, und ihre Signatur wird auf dem Gerät geprüft. Die App hat keine Werbung, keine Konten und keine Analysen; ein optionaler einmaliger Beitrag unterstützt die Entwicklung, und nichts ist dahinter gesperrt. Verdetto wird „wer-DET-o“ ausgesprochen und ist Italienisch für Urteil.",
  "facts_h": "Fakten zum Nachprüfen",
  "facts": [
   "Plattform: Android 8 und neuer. Preis: kostenlos. Werbung: keine. Konten: keine. Analysen: keine.",
   "Das Scannen und jede eingebaute Prüfung laufen auf dem Telefon. Online-Abfragen sind standardmäßig an und lassen sich mit einem Schalter abstellen; Produktabfragen haben einen eigenen Schalter.",
   "Liest {N} Arten von Codes, gemessen im Validierungslauf vom 4. September 2026, darunter EAN, UPC, Code 128, Data Matrix, PDF417 und Aztec.",
   "Die Sicherheitsliste entsteht offen unter <a href=\"https://github.com/verdettoqr/link-safety-list\">github.com/verdettoqr/link-safety-list</a> und wird viermal am Tag aktualisiert; die App prüft ihre Signatur vor der Verwendung.",
   "Was die App nie sagt: dass ein Link, ein Netzwerk oder ein Produkt sicher ist. Die Formulierung lautet „Keine Warnungen gefunden“.",
   "Vergleichsgrundlage: die zehn meistinstallierten kostenlosen QR-Scanner bei Google Play am 4. September 2026, bestimmt nach der Installationszahl an diesem Tag; das Werbe-Label jedes Eintrags und seine relevantesten Rezensionen am selben Tag gelesen; „falscher Button“ ist die Beschreibung der Rezensenten, nicht unsere; kein Scanner wird genannt; die Liste und die Notizen liegen bei uns vor.",
   "Datenschutzerklärung: {PRIVACY_LINK}.",
   "Nutzungsbedingungen: {TERMS_LINK}."
  ],
  "assets_h": "Material",
  "assets": [
   "<a href=\"icon-512.png\">App-Symbol, 512 px PNG</a> und <a href=\"logo.svg\">das Symbol als SVG</a>. Mintfarbener Grund, tief-türkises QR-Zeichen, ein amberfarbenes Suchmuster.",
   "<a href=\"lockup-teal-amber.png\">Wort-Bild-Marke, Zeichen und Name, transparentes PNG</a> für helle Gründe (türkiser Körper, Amber-Akzent) und <a href=\"lockup-white-amber.png\">dieselbe mit weißem Körper</a> für dunkle Gründe; das Zeichen behält seine Farben und sitzt auf der Versalhöhe des Namens.",
   "<a href=\"og-image.png\">Vorschaubild, 1200 × 630</a> und <a href=\"play-header-4096x2304.jpg\">breites Banner, 4096 × 2304</a>.",
   "<a href=\"screens/result-sheet.webp\">Screenshot des Ergebnisblatts</a>: ein gescannter Link, gezeigt, bevor er sich öffnet, mit dem Chip „Keine Warnungen gefunden“.",
   "<a href=\"screens/result-sheet-warning.webp\">Ergebnisblatt im Warnzustand</a>: eine ähnlich aussehende Adresse (paypa1.com), markiert als Imitation von paypal.com, bevor sich etwas öffnet.",
   "<a href=\"verdetto-code-light.svg\">Der Verdetto-Code, SVG</a> (Türkis auf Weiß; <a href=\"verdetto-code-dark.svg\">Weiß auf Schwarz</a>), als PNG <a href=\"verdetto-code-light-on-white.png\">auf Weiß</a>, <a href=\"verdetto-code-dark-on-black.png\">auf Schwarz</a> oder transparent (<a href=\"verdetto-code-light-transparent.png\">türkis</a>, <a href=\"verdetto-code-dark-transparent.png\">weiß</a>), und die <a href=\"verdetto-table-card.pdf\">druckbare Tischkarte</a> (<a href=\"verdetto-table-card.png\">PNG</a>). Er öffnet https://verdettoqr.com und sonst nichts; jede Kamera-App liest ihn."
  ],
  "no_alter": "Bitte verändere die Farben des Symbols nicht und füge keine Effekte hinzu; das Zeichen ist die Marke.",
  "trademark": "Verdetto und das Verdetto-QR-Zeichen sind Marken; eine Anmeldung für VERDETTO in den Vereinigten Staaten ist anhängig (Seriennummer 50092495).",
  "contact": "Kontakt"
 },
 "es": {
  "title": "Kit de prensa",
  "desc": "La descripción en una frase, el texto estándar, datos comprobables y recursos gráficos para escribir sobre Verdetto: QR & Barcode Scanner.",
  "meta": "Todo lo necesario para describir Verdetto con precisión, en un solo lugar. Cita con libertad; la frase de abajo es la que usamos en todas partes.",
  "lead": "En una frase.",
  "sentence": "Verdetto es un escáner de códigos QR y de barras gratuito para Android, sin anuncios y sin botones falsos. Muestra el enlace antes de abrirlo, está hecho para leer códigos dañados y revisa el contenido escaneado en busca de señales de alerta en el propio teléfono. Nunca dice que algo sea seguro: «No se encontraron avisos» significa que ninguna de sus comprobaciones coincidió.",
  "boiler_h": "Texto estándar",
  "boiler": "Verdetto: QR &amp; Barcode Scanner es una aplicación gratuita para Android de Verdetto, un desarrollador independiente en Virginia. Lee códigos QR y de barras, incluidos los dañados, muestra a la persona exactamente lo que contiene un código antes de que se abra nada, y revisa enlaces, redes Wi-Fi, direcciones de pago y números de teléfono en busca de señales de alerta conocidas en el propio teléfono. Su lista de entradas conocidas de phishing y estafas se compila de forma abierta a partir de fuentes públicas, y su firma se comprueba en el dispositivo. La aplicación no tiene anuncios, ni cuentas, ni analíticas; una contribución única y opcional apoya el desarrollo, y nada queda bloqueado tras ella. Verdetto se pronuncia «ver-DET-o» y significa veredicto en italiano.",
  "facts_h": "Datos que puedes comprobar",
  "facts": [
   "Plataforma: Android 8 y posteriores. Precio: gratis. Anuncios: ninguno. Cuentas: ninguna. Analíticas: ninguna.",
   "El escaneo y todas las comprobaciones integradas se ejecutan en el teléfono. Las consultas en línea están activadas por defecto y se apagan con un interruptor; las consultas de productos tienen su propio interruptor.",
   "Lee {N} tipos de códigos, medidos en la ejecución de validación del 4 de septiembre de 2026, incluidos EAN, UPC, Code 128, Data Matrix, PDF417 y Aztec.",
   "La lista de seguridad se construye de forma abierta en <a href=\"https://github.com/verdettoqr/link-safety-list\">github.com/verdettoqr/link-safety-list</a> y se actualiza cuatro veces al día; la aplicación verifica su firma antes de usarla.",
   "Lo que la aplicación nunca dice: que un enlace, una red o un producto sea seguro. La redacción es «No se encontraron avisos».",
   "Base de la comparación: los diez escáneres QR gratuitos más instalados en Google Play a 4 de septiembre de 2026, identificados por su número de instalaciones ese día; la etiqueta de anuncios de cada ficha y sus reseñas más relevantes, leídas el mismo día; «botón falso» es la descripción de quienes reseñan, no la nuestra; no se nombra ningún escáner; la lista y las notas quedan archivadas.",
   "Política de privacidad: {PRIVACY_LINK}.",
   "Condiciones: {TERMS_LINK}."
  ],
  "assets_h": "Recursos",
  "assets": [
   "<a href=\"icon-512.png\">Icono de la app, PNG de 512 px</a> y <a href=\"logo.svg\">el icono en SVG</a>. Fondo menta, símbolo QR verde azulado oscuro, un patrón de localización ámbar.",
   "<a href=\"lockup-teal-amber.png\">Logotipo, símbolo y nombre, PNG transparente</a> para fondos claros (cuerpo verde azulado, acento ámbar) y <a href=\"lockup-white-amber.png\">el mismo con cuerpo blanco</a> para fondos oscuros; el símbolo conserva sus colores y se alinea con la altura de las mayúsculas del nombre.",
   "<a href=\"og-image.png\">Imagen para compartir, 1200 × 630</a> y <a href=\"play-header-4096x2304.jpg\">banner ancho, 4096 × 2304</a>.",
   "<a href=\"screens/result-sheet.webp\">Captura de la hoja de resultados</a>: un enlace escaneado que se muestra antes de abrirse, con el chip «No se encontraron avisos».",
   "<a href=\"screens/result-sheet-warning.webp\">Hoja de resultados, estado de aviso</a>: una dirección parecida (paypa1.com) señalada como imitación de paypal.com antes de que se abra nada.",
   "<a href=\"verdetto-code-light.svg\">El código de Verdetto, SVG</a> (verde azulado sobre blanco; <a href=\"verdetto-code-dark.svg\">blanco sobre negro</a>), como PNG <a href=\"verdetto-code-light-on-white.png\">sobre blanco</a>, <a href=\"verdetto-code-dark-on-black.png\">sobre negro</a> o transparente (<a href=\"verdetto-code-light-transparent.png\">verde azulado</a>, <a href=\"verdetto-code-dark-transparent.png\">blanco</a>), y la <a href=\"verdetto-table-card.pdf\">tarjeta de mesa imprimible</a> (<a href=\"verdetto-table-card.png\">PNG</a>). Abre https://verdettoqr.com y nada más; cualquier app de cámara lo lee."
  ],
  "no_alter": "Por favor, no alteres los colores del icono ni añadas efectos; el símbolo es la marca.",
  "trademark": "Verdetto y el símbolo QR de Verdetto son marcas; hay una solicitud pendiente en Estados Unidos para VERDETTO (n.º de serie 50092495).",
  "contact": "Contacto"
 },
 "fr": {
  "title": "Kit presse",
  "desc": "La description en une phrase, le texte de présentation, des faits vérifiables et les visuels pour écrire sur Verdetto: QR & Barcode Scanner.",
  "meta": "Tout ce qu'il faut pour décrire Verdetto avec exactitude, au même endroit. Citez librement ; la phrase ci-dessous est celle que nous utilisons partout.",
  "lead": "En une phrase.",
  "sentence": "Verdetto est un lecteur de codes QR et de codes-barres gratuit pour Android, sans publicité et sans faux boutons. Il montre le lien avant de l'ouvrir, est conçu pour lire les codes abîmés et vérifie le contenu scanné à la recherche de signaux d'alerte, sur le téléphone. Il ne dit jamais que quelque chose est sûr : « Aucune alerte trouvée » signifie qu'aucune de ses vérifications n'a réagi.",
  "boiler_h": "Texte de présentation",
  "boiler": "Verdetto: QR &amp; Barcode Scanner est une application Android gratuite de Verdetto, un développeur indépendant en Virginie. Elle lit les codes QR et les codes-barres, y compris abîmés, montre à la personne exactement ce que contient un code avant que quoi que ce soit ne s'ouvre, et vérifie les liens, les réseaux Wi-Fi, les adresses de paiement et les numéros de téléphone à la recherche de signaux d'alerte connus, sur le téléphone lui-même. Sa liste d'entrées connues de phishing et d'arnaques est constituée au grand jour à partir de flux publics, et sa signature est vérifiée sur l'appareil. L'application n'a ni publicité, ni comptes, ni outils d'analyse ; une contribution unique et facultative soutient le développement, et rien n'est verrouillé derrière. Verdetto se prononce « ver-DET-o » et signifie verdict en italien.",
  "facts_h": "Des faits que vous pouvez vérifier",
  "facts": [
   "Plateforme : Android 8 et versions ultérieures. Prix : gratuit. Publicité : aucune. Comptes : aucun. Analyse d'audience : aucune.",
   "Le scan et chaque vérification intégrée s'exécutent sur le téléphone. Les recherches en ligne sont activées par défaut et se coupent d'un seul interrupteur ; les recherches de produits ont le leur.",
   "Lit {N} sortes de codes, mesurées lors de la validation du 4 septembre 2026, dont EAN, UPC, Code 128, Data Matrix, PDF417 et Aztec.",
   "La liste de sécurité est construite au grand jour sur <a href=\"https://github.com/verdettoqr/link-safety-list\">github.com/verdettoqr/link-safety-list</a> et rafraîchie quatre fois par jour ; l'application vérifie sa signature avant de l'utiliser.",
   "Ce que l'application ne dit jamais : qu'un lien, un réseau ou un produit est sûr. La formulation est « Aucune alerte trouvée ».",
   "Base de comparaison : les dix lecteurs QR gratuits les plus installés sur Google Play au 4 septembre 2026, identifiés par leur nombre d'installations ce jour-là ; l'étiquette « contient des publicités » de chaque fiche et ses avis les plus pertinents, lus le même jour ; « faux bouton » est la description des personnes qui ont laissé un avis, pas la nôtre ; aucun lecteur n'est nommé ; la liste et les notes sont conservées.",
   "Politique de confidentialité : {PRIVACY_LINK}.",
   "Conditions : {TERMS_LINK}."
  ],
  "assets_h": "Visuels",
  "assets": [
   "<a href=\"icon-512.png\">Icône de l'application, PNG 512 px</a> et <a href=\"logo.svg\">l'icône en SVG</a>. Fond menthe, symbole QR bleu sarcelle profond, un motif de repérage ambre.",
   "<a href=\"lockup-teal-amber.png\">Logotype, symbole et nom, PNG transparent</a> pour fonds clairs (corps sarcelle, accent ambre) et <a href=\"lockup-white-amber.png\">le même avec un corps blanc</a> pour fonds sombres ; le symbole garde ses couleurs et s'aligne sur la hauteur des capitales du nom.",
   "<a href=\"og-image.png\">Image de partage, 1200 × 630</a> et <a href=\"play-header-4096x2304.jpg\">bannière large, 4096 × 2304</a>.",
   "<a href=\"screens/result-sheet.webp\">Capture de la feuille de résultat</a> : un lien scanné, affiché avant de s'ouvrir, avec la puce « Aucune alerte trouvée ».",
   "<a href=\"screens/result-sheet-warning.webp\">Feuille de résultat, état d'alerte</a> : une adresse imitée (paypa1.com) signalée comme imitation de paypal.com avant que quoi que ce soit ne s'ouvre.",
   "<a href=\"verdetto-code-light.svg\">Le code Verdetto, SVG</a> (sarcelle sur blanc ; <a href=\"verdetto-code-dark.svg\">blanc sur noir</a>), en PNG <a href=\"verdetto-code-light-on-white.png\">sur blanc</a>, <a href=\"verdetto-code-dark-on-black.png\">sur noir</a> ou transparent (<a href=\"verdetto-code-light-transparent.png\">sarcelle</a>, <a href=\"verdetto-code-dark-transparent.png\">blanc</a>), et la <a href=\"verdetto-table-card.pdf\">carte de table imprimable</a> (<a href=\"verdetto-table-card.png\">PNG</a>). Il ouvre https://verdettoqr.com et rien d'autre ; toute application appareil photo le lit."
  ],
  "no_alter": "Merci de ne pas modifier les couleurs de l'icône ni d'ajouter d'effets ; le symbole est la marque.",
  "trademark": "Verdetto et le symbole QR Verdetto sont des marques ; une demande d'enregistrement de VERDETTO est en cours aux États-Unis (numéro de série 50092495).",
  "contact": "Contact"
 },
 "pt-BR": {
  "title": "Kit de imprensa",
  "desc": "A descrição em uma frase, o texto padrão, fatos verificáveis e imagens para escrever sobre o Verdetto: QR & Barcode Scanner.",
  "meta": "Tudo o que é preciso para descrever o Verdetto com exatidão, em um só lugar. Cite à vontade; a frase abaixo é a que usamos em todo lugar.",
  "lead": "Em uma frase.",
  "sentence": "O Verdetto é um leitor de códigos QR e de barras gratuito para Android, sem anúncios e sem botões falsos. Ele mostra o link antes de abrir, foi feito para ler códigos danificados e verifica o conteúdo escaneado em busca de sinais de alerta, no próprio celular. Ele nunca diz que algo é seguro: \"Nenhum alerta encontrado\" significa que nenhuma das suas verificações bateu.",
  "boiler_h": "Texto padrão",
  "boiler": "Verdetto: QR &amp; Barcode Scanner é um aplicativo gratuito para Android do Verdetto, um desenvolvedor independente na Virgínia. Ele lê códigos QR e de barras, inclusive danificados, mostra à pessoa exatamente o que um código contém antes que qualquer coisa abra, e verifica links, redes Wi-Fi, endereços de pagamento e números de telefone em busca de sinais de alerta conhecidos, no próprio celular. Sua lista de entradas conhecidas de phishing e golpes é montada abertamente a partir de fontes públicas, e sua assinatura é conferida no aparelho. O aplicativo não tem anúncios, contas nem análises de uso; uma contribuição única e opcional apoia o desenvolvimento, e nada fica trancado atrás dela. Verdetto se pronuncia \"ver-DET-o\" e é veredicto em italiano.",
  "facts_h": "Fatos que você pode conferir",
  "facts": [
   "Plataforma: Android 8 ou mais recente. Preço: grátis. Anúncios: nenhum. Contas: nenhuma. Análises de uso: nenhuma.",
   "A leitura e todas as verificações embutidas rodam no celular. As consultas online vêm ativadas e podem ser desligadas com um único botão; as consultas de produtos têm um botão próprio.",
   "Lê {N} tipos de código, medidos na rodada de validação de 4 de setembro de 2026, incluindo EAN, UPC, Code 128, Data Matrix, PDF417 e Aztec.",
   "A lista de segurança é construída abertamente em <a href=\"https://github.com/verdettoqr/link-safety-list\">github.com/verdettoqr/link-safety-list</a> e atualizada quatro vezes por dia; o aplicativo verifica a assinatura dela antes de usar.",
   "O que o aplicativo nunca diz: que um link, uma rede ou um produto é seguro. A frase é \"Nenhum alerta encontrado\".",
   "Base da comparação: os dez leitores de QR gratuitos mais instalados no Google Play em 4 de setembro de 2026, identificados pelo número de instalações naquele dia; o rótulo de anúncios de cada página e suas avaliações mais relevantes, lidos no mesmo dia; \"botão falso\" é a descrição de quem avaliou, não a nossa; nenhum leitor é nomeado; a lista e as anotações ficam arquivadas.",
   "Política de privacidade: {PRIVACY_LINK}.",
   "Termos: {TERMS_LINK}."
  ],
  "assets_h": "Imagens",
  "assets": [
   "<a href=\"icon-512.png\">Ícone do app, PNG de 512 px</a> e <a href=\"logo.svg\">o ícone em SVG</a>. Fundo menta, símbolo QR em verde-azulado escuro, um padrão localizador âmbar.",
   "<a href=\"lockup-teal-amber.png\">Assinatura visual, símbolo e nome, PNG transparente</a> para fundos claros (corpo verde-azulado, destaque âmbar) e <a href=\"lockup-white-amber.png\">a mesma com corpo branco</a> para fundos escuros; o símbolo mantém suas cores e fica na altura das maiúsculas do nome.",
   "<a href=\"og-image.png\">Imagem de compartilhamento, 1200 × 630</a> e <a href=\"play-header-4096x2304.jpg\">banner largo, 4096 × 2304</a>.",
   "<a href=\"screens/result-sheet.webp\">Captura da folha de resultado</a>: um link escaneado mostrado antes de abrir, com o chip \"Nenhum alerta encontrado\".",
   "<a href=\"screens/result-sheet-warning.webp\">Folha de resultado, estado de alerta</a>: um endereço parecido (paypa1.com) marcado como imitação de paypal.com antes que qualquer coisa abra.",
   "<a href=\"verdetto-code-light.svg\">O código do Verdetto, SVG</a> (verde-azulado sobre branco; <a href=\"verdetto-code-dark.svg\">branco sobre preto</a>), como PNG <a href=\"verdetto-code-light-on-white.png\">sobre branco</a>, <a href=\"verdetto-code-dark-on-black.png\">sobre preto</a> ou transparente (<a href=\"verdetto-code-light-transparent.png\">verde-azulado</a>, <a href=\"verdetto-code-dark-transparent.png\">branco</a>), e o <a href=\"verdetto-table-card.pdf\">cartão de mesa para impressão</a> (<a href=\"verdetto-table-card.png\">PNG</a>). Ele abre https://verdettoqr.com e nada mais; qualquer app de câmera o lê."
  ],
  "no_alter": "Por favor, não altere as cores do ícone nem adicione efeitos; o símbolo é a marca.",
  "trademark": "Verdetto e o símbolo QR do Verdetto são marcas; um pedido de registro de VERDETTO está pendente nos Estados Unidos (nº de série 50092495).",
  "contact": "Contato"
 },
 "id": {
  "title": "Kit pers",
  "desc": "Deskripsi satu kalimat, teks baku, fakta yang bisa diperiksa, dan aset gambar untuk menulis tentang Verdetto: QR & Barcode Scanner.",
  "meta": "Semua yang diperlukan untuk menggambarkan Verdetto secara akurat, di satu tempat. Kutip dengan bebas; kalimat di bawah adalah yang kami pakai di mana-mana.",
  "lead": "Dalam satu kalimat.",
  "sentence": "Verdetto adalah pemindai kode QR dan barcode gratis untuk Android tanpa iklan dan tanpa tombol palsu. Ia menampilkan tautan sebelum dibuka, dibuat untuk membaca kode yang rusak, dan memeriksa konten hasil pindaian untuk tanda-tanda peringatan di ponsel. Ia tidak pernah mengatakan sesuatu aman: \"Tidak ada peringatan ditemukan\" berarti tidak satu pun pemeriksaannya cocok.",
  "boiler_h": "Teks baku",
  "boiler": "Verdetto: QR &amp; Barcode Scanner adalah aplikasi Android gratis dari Verdetto, seorang pengembang independen di Virginia. Ia membaca kode QR dan barcode, termasuk yang rusak, menunjukkan kepada orang persis apa isi sebuah kode sebelum apa pun terbuka, dan memeriksa tautan, jaringan Wi-Fi, alamat pembayaran, dan nomor telepon untuk tanda-tanda peringatan yang dikenal, di ponsel itu sendiri. Daftar entri phishing dan penipuan yang dikenalnya disusun secara terbuka dari sumber publik, dan tanda tangannya diperiksa di perangkat. Aplikasi ini tanpa iklan, tanpa akun, dan tanpa analitik; kontribusi sekali bayar yang opsional mendukung pengembangan, dan tidak ada yang dikunci di baliknya. Verdetto diucapkan \"ver-DET-o\" dan berarti putusan dalam bahasa Italia.",
  "facts_h": "Fakta yang bisa Anda periksa",
  "facts": [
   "Platform: Android 8 ke atas. Harga: gratis. Iklan: tidak ada. Akun: tidak ada. Analitik: tidak ada.",
   "Pemindaian dan setiap pemeriksaan bawaan berjalan di ponsel. Pencarian online aktif secara bawaan dan bisa dimatikan dengan satu sakelar; pencarian produk punya sakelar sendiri.",
   "Membaca {N} jenis kode, diukur pada uji validasi 4 September 2026, termasuk EAN, UPC, Code 128, Data Matrix, PDF417, dan Aztec.",
   "Daftar keamanan dibangun secara terbuka di <a href=\"https://github.com/verdettoqr/link-safety-list\">github.com/verdettoqr/link-safety-list</a> dan diperbarui empat kali sehari; aplikasi memverifikasi tanda tangannya sebelum dipakai.",
   "Yang tidak pernah dikatakan aplikasi: bahwa sebuah tautan, jaringan, atau produk aman. Kata-katanya adalah \"Tidak ada peringatan ditemukan\".",
   "Dasar perbandingan: sepuluh pemindai QR gratis dengan pemasangan terbanyak di Google Play per 4 September 2026, ditentukan dari jumlah pemasangan hari itu; label iklan setiap halaman dan ulasan paling relevannya dibaca pada hari yang sama; \"tombol palsu\" adalah gambaran para pengulas, bukan kami; tidak ada pemindai yang disebut namanya; daftar dan catatannya kami simpan.",
   "Kebijakan privasi: {PRIVACY_LINK}.",
   "Ketentuan: {TERMS_LINK}."
  ],
  "assets_h": "Aset",
  "assets": [
   "<a href=\"icon-512.png\">Ikon aplikasi, PNG 512 px</a> dan <a href=\"logo.svg\">ikon dalam SVG</a>. Latar mint, simbol QR teal gelap, satu pola pencari berwarna amber.",
   "<a href=\"lockup-teal-amber.png\">Lockup, simbol dan nama, PNG transparan</a> untuk latar terang (badan teal, aksen amber) dan <a href=\"lockup-white-amber.png\">versi yang sama dengan badan putih</a> untuk latar gelap; simbol mempertahankan warnanya dan sejajar dengan tinggi huruf kapital nama.",
   "<a href=\"og-image.png\">Gambar berbagi, 1200 × 630</a> dan <a href=\"play-header-4096x2304.jpg\">banner lebar, 4096 × 2304</a>.",
   "<a href=\"screens/result-sheet.webp\">Tangkapan layar lembar hasil</a>: tautan hasil pindaian yang ditampilkan sebelum dibuka, dengan chip \"Tidak ada peringatan ditemukan\".",
   "<a href=\"screens/result-sheet-warning.webp\">Lembar hasil, keadaan peringatan</a>: alamat yang mirip (paypa1.com) ditandai sebagai tiruan paypal.com sebelum apa pun terbuka.",
   "<a href=\"verdetto-code-light.svg\">Kode Verdetto, SVG</a> (teal di atas putih; <a href=\"verdetto-code-dark.svg\">putih di atas hitam</a>), sebagai PNG <a href=\"verdetto-code-light-on-white.png\">di atas putih</a>, <a href=\"verdetto-code-dark-on-black.png\">di atas hitam</a>, atau transparan (<a href=\"verdetto-code-light-transparent.png\">teal</a>, <a href=\"verdetto-code-dark-transparent.png\">putih</a>), dan <a href=\"verdetto-table-card.pdf\">kartu meja yang bisa dicetak</a> (<a href=\"verdetto-table-card.png\">PNG</a>). Ia membuka https://verdettoqr.com dan tidak ada yang lain; aplikasi kamera apa pun membacanya."
  ],
  "no_alter": "Mohon jangan mengubah warna ikon atau menambahkan efek; simbol itu adalah mereknya.",
  "trademark": "Verdetto dan simbol QR Verdetto adalah merek dagang; permohonan pendaftaran VERDETTO sedang diproses di Amerika Serikat (nomor seri 50092495).",
  "contact": "Kontak"
 },
 "ru": {
  "title": "Пресс-кит",
  "desc": "Описание в одном предложении, стандартный текст, проверяемые факты и графика для тех, кто пишет о Verdetto: QR & Barcode Scanner.",
  "meta": "Всё, что нужно, чтобы точно описать Verdetto, в одном месте. Цитируйте свободно; предложение ниже мы используем везде.",
  "lead": "В одном предложении.",
  "sentence": "Verdetto — бесплатный сканер QR-кодов и штрихкодов для Android без рекламы и без ложных кнопок. Он показывает ссылку до того, как она откроется, создан для чтения повреждённых кодов и проверяет отсканированное на признаки опасности прямо на телефоне. Он никогда не говорит, что что-то безопасно: «Предупреждений не найдено» означает, что ни одна из его проверок не сработала.",
  "boiler_h": "Стандартный текст",
  "boiler": "Verdetto: QR &amp; Barcode Scanner — бесплатное приложение для Android от Verdetto, независимого разработчика из Вирджинии. Оно читает QR-коды и штрихкоды, в том числе повреждённые, показывает человеку, что именно содержит код, до того как что-либо откроется, и проверяет ссылки, сети Wi-Fi, платёжные адреса и номера телефонов на известные признаки опасности прямо на телефоне. Его список известных фишинговых и мошеннических записей собирается открыто из публичных источников, а подпись списка проверяется на устройстве. В приложении нет рекламы, учётных записей и аналитики; необязательный разовый взнос поддерживает разработку, и ничто за ним не заперто. Verdetto произносится «вер-ДЕТ-то» и по-итальянски означает «вердикт».",
  "facts_h": "Факты, которые можно проверить",
  "facts": [
   "Платформа: Android 8 и новее. Цена: бесплатно. Реклама: нет. Учётные записи: нет. Аналитика: нет.",
   "Сканирование и каждая встроенная проверка выполняются на телефоне. Онлайн-запросы включены по умолчанию и отключаются одним переключателем; у запросов о товарах свой переключатель.",
   "Читает {N} вид кодов, измеренных в проверочном прогоне 4 сентября 2026 года, включая EAN, UPC, Code 128, Data Matrix, PDF417 и Aztec.",
   "Список безопасности собирается открыто на <a href=\"https://github.com/verdettoqr/link-safety-list\">github.com/verdettoqr/link-safety-list</a> и обновляется четыре раза в день; приложение проверяет его подпись перед использованием.",
   "Чего приложение никогда не говорит: что ссылка, сеть или товар безопасны. Формулировка: «Предупреждений не найдено».",
   "База сравнения: десять самых устанавливаемых бесплатных QR-сканеров в Google Play на 4 сентября 2026 года, определённые по числу установок в тот день; метка о рекламе у каждой страницы и её самые релевантные отзывы прочитаны в тот же день; «ложная кнопка» — описание авторов отзывов, а не наше; ни один сканер не назван; список и заметки хранятся у нас.",
   "Политика конфиденциальности: {PRIVACY_LINK}.",
   "Условия: {TERMS_LINK}."
  ],
  "assets_h": "Материалы",
  "assets": [
   "<a href=\"icon-512.png\">Значок приложения, PNG 512 px</a> и <a href=\"logo.svg\">значок в SVG</a>. Мятный фон, тёмно-бирюзовый знак QR, один янтарный поисковый узор.",
   "<a href=\"lockup-teal-amber.png\">Логоблок, знак и имя, прозрачный PNG</a> для светлых фонов (бирюзовое тело, янтарный акцент) и <a href=\"lockup-white-amber.png\">тот же с белым телом</a> для тёмных фонов; знак сохраняет свои цвета и стоит на высоте прописных букв имени.",
   "<a href=\"og-image.png\">Изображение для ссылок, 1200 × 630</a> и <a href=\"play-header-4096x2304.jpg\">широкий баннер, 4096 × 2304</a>.",
   "<a href=\"screens/result-sheet.webp\">Снимок листа результата</a>: отсканированная ссылка показана до открытия, с чипом «Предупреждений не найдено».",
   "<a href=\"screens/result-sheet-warning.webp\">Лист результата в состоянии предупреждения</a>: похожий адрес (paypa1.com) помечен как имитация paypal.com до того, как что-либо откроется.",
   "<a href=\"verdetto-code-light.svg\">Код Verdetto, SVG</a> (бирюзовый на белом; <a href=\"verdetto-code-dark.svg\">белый на чёрном</a>), в PNG <a href=\"verdetto-code-light-on-white.png\">на белом</a>, <a href=\"verdetto-code-dark-on-black.png\">на чёрном</a> или с прозрачным фоном (<a href=\"verdetto-code-light-transparent.png\">бирюзовый</a>, <a href=\"verdetto-code-dark-transparent.png\">белый</a>), и <a href=\"verdetto-table-card.pdf\">настольная карточка для печати</a> (<a href=\"verdetto-table-card.png\">PNG</a>). Он открывает https://verdettoqr.com и ничего больше; его читает любое приложение камеры."
  ],
  "no_alter": "Пожалуйста, не меняйте цвета значка и не добавляйте эффекты; знак и есть бренд.",
  "trademark": "Verdetto и знак Verdetto QR являются товарными знаками; заявка на VERDETTO в США находится на рассмотрении (серийный номер 50092495).",
  "contact": "Контакт"
 },
 "hi": {
  "title": "प्रेस किट",
  "desc": "Verdetto: QR & Barcode Scanner के बारे में लिखने के लिए एक वाक्य का विवरण, मानक पाठ, जाँचने योग्य तथ्य और चित्र सामग्री।",
  "meta": "Verdetto का सही वर्णन करने के लिए जो कुछ चाहिए, एक जगह। बेझिझक उद्धृत करें; नीचे का वाक्य वही है जो हम हर जगह इस्तेमाल करते हैं।",
  "lead": "एक वाक्य में।",
  "sentence": "Verdetto Android के लिए एक मुफ़्त QR कोड और बारकोड स्कैनर है, जिसमें न विज्ञापन हैं, न नकली बटन। यह लिंक खुलने से पहले उसे दिखाता है, क्षतिग्रस्त कोड पढ़ने के लिए बनाया गया है, और स्कैन की गई सामग्री में चेतावनी के संकेत फ़ोन पर ही जाँचता है। यह कभी नहीं कहता कि कुछ सुरक्षित है: \"कोई चेतावनी नहीं मिली\" का मतलब है कि इसकी कोई जाँच मेल नहीं खाई।",
  "boiler_h": "मानक पाठ",
  "boiler": "Verdetto: QR &amp; Barcode Scanner Verdetto का एक मुफ़्त Android ऐप है, जिसे वर्जीनिया में एक स्वतंत्र डेवलपर बनाता है। यह QR कोड और बारकोड पढ़ता है, क्षतिग्रस्त कोड भी, कुछ भी खुलने से पहले व्यक्ति को ठीक-ठीक दिखाता है कि कोड में क्या है, और लिंक, Wi-Fi नेटवर्क, भुगतान पते और फ़ोन नंबरों को ज्ञात चेतावनी संकेतों के लिए फ़ोन पर ही जाँचता है। ज्ञात फ़िशिंग और धोखाधड़ी प्रविष्टियों की इसकी सूची सार्वजनिक स्रोतों से खुले तौर पर बनाई जाती है, और उसका हस्ताक्षर डिवाइस पर जाँचा जाता है। ऐप में न विज्ञापन हैं, न खाते, न एनालिटिक्स; एक वैकल्पिक एक बार का योगदान विकास में मदद करता है, और उसके पीछे कुछ भी बंद नहीं है। Verdetto का उच्चारण \"वेर-डेट-ओ\" है और इतालवी में इसका अर्थ है फ़ैसला।",
  "facts_h": "तथ्य जो आप जाँच सकते हैं",
  "facts": [
   "प्लैटफ़ॉर्म: Android 8 और बाद के संस्करण। कीमत: मुफ़्त। विज्ञापन: कोई नहीं। खाते: कोई नहीं। एनालिटिक्स: कोई नहीं।",
   "स्कैनिंग और हर अंतर्निर्मित जाँच फ़ोन पर चलती है। ऑनलाइन खोज डिफ़ॉल्ट रूप से चालू है और एक स्विच से बंद की जा सकती है; उत्पाद खोज का अपना अलग स्विच है।",
   "{N} तरह के कोड पढ़ता है, 4 सितंबर 2026 के सत्यापन रन में मापे गए, जिनमें EAN, UPC, Code 128, Data Matrix, PDF417 और Aztec शामिल हैं।",
   "सुरक्षा सूची <a href=\"https://github.com/verdettoqr/link-safety-list\">github.com/verdettoqr/link-safety-list</a> पर खुले तौर पर बनाई जाती है और दिन में चार बार ताज़ा होती है; ऐप इस्तेमाल से पहले उसका हस्ताक्षर सत्यापित करता है।",
   "ऐप जो कभी नहीं कहता: कि कोई लिंक, नेटवर्क या उत्पाद सुरक्षित है। शब्द हैं \"कोई चेतावनी नहीं मिली\"।",
   "तुलना का आधार: 4 सितंबर 2026 तक Google Play पर सबसे अधिक इंस्टॉल किए गए दस मुफ़्त QR स्कैनर, उस दिन की इंस्टॉल संख्या से पहचाने गए; हर लिस्टिंग का विज्ञापन लेबल और उसकी सबसे प्रासंगिक समीक्षाएँ उसी दिन पढ़ी गईं; \"नकली बटन\" समीक्षकों का वर्णन है, हमारा नहीं; किसी स्कैनर का नाम नहीं लिया गया; सूची और नोट हमारे पास रखे हैं।",
   "गोपनीयता नीति: {PRIVACY_LINK}।",
   "शर्तें: {TERMS_LINK}।"
  ],
  "assets_h": "सामग्री",
  "assets": [
   "<a href=\"icon-512.png\">ऐप आइकन, 512 px PNG</a> और <a href=\"logo.svg\">SVG में आइकन</a>। पुदीना रंग की पृष्ठभूमि, गहरा टील QR चिह्न, एक एम्बर फ़ाइंडर पैटर्न।",
   "<a href=\"lockup-teal-amber.png\">लॉकअप, चिह्न और नाम, पारदर्शी PNG</a> हल्की पृष्ठभूमि के लिए (टील बॉडी, एम्बर एक्सेंट) और <a href=\"lockup-white-amber.png\">वही सफ़ेद बॉडी के साथ</a> गहरी पृष्ठभूमि के लिए; चिह्न अपने रंग बनाए रखता है और नाम की कैप ऊँचाई पर बैठता है।",
   "<a href=\"og-image.png\">शेयर इमेज, 1200 × 630</a> और <a href=\"play-header-4096x2304.jpg\">चौड़ा बैनर, 4096 × 2304</a>।",
   "<a href=\"screens/result-sheet.webp\">परिणाम शीट का स्क्रीनशॉट</a>: एक स्कैन किया गया लिंक खुलने से पहले दिखाया गया, \"कोई चेतावनी नहीं मिली\" चिप के साथ।",
   "<a href=\"screens/result-sheet-warning.webp\">परिणाम शीट, चेतावनी अवस्था</a>: एक मिलता-जुलता पता (paypa1.com) कुछ भी खुलने से पहले paypal.com की नक़ल के रूप में चिह्नित।",
   "<a href=\"verdetto-code-light.svg\">Verdetto कोड, SVG</a> (सफ़ेद पर टील; <a href=\"verdetto-code-dark.svg\">काले पर सफ़ेद</a>), PNG के रूप में <a href=\"verdetto-code-light-on-white.png\">सफ़ेद पर</a>, <a href=\"verdetto-code-dark-on-black.png\">काले पर</a> या पारदर्शी (<a href=\"verdetto-code-light-transparent.png\">टील</a>, <a href=\"verdetto-code-dark-transparent.png\">सफ़ेद</a>), और <a href=\"verdetto-table-card.pdf\">छपने योग्य टेबल कार्ड</a> (<a href=\"verdetto-table-card.png\">PNG</a>)। यह https://verdettoqr.com खोलता है और कुछ नहीं; कोई भी कैमरा ऐप इसे पढ़ लेता है।"
  ],
  "no_alter": "कृपया आइकन के रंग न बदलें और कोई प्रभाव न जोड़ें; चिह्न ही ब्रांड है।",
  "trademark": "Verdetto और Verdetto QR चिह्न ट्रेडमार्क हैं; VERDETTO के लिए संयुक्त राज्य अमेरिका में एक आवेदन लंबित है (क्रम संख्या 50092495)।",
  "contact": "संपर्क"
 },
 "ja": {
  "title": "プレスキット",
  "desc": "Verdetto: QR & Barcode Scanner について書くための一文の説明、定型文、確認できる事実、画像素材。",
  "meta": "Verdetto を正確に説明するために必要なものを一か所に。自由に引用してください。下の一文は、私たちがどこでも使っているものです。",
  "lead": "一文で。",
  "sentence": "Verdetto は、広告も偽のボタンもない、Android 向けの無料 QR コード・バーコードスキャナーです。リンクを開く前に表示し、傷んだコードを読めるように作られ、読み取った内容に警告のサインがないかを端末上で確認します。何かが安全だとは決して言いません。「警告は見つかりませんでした」は、どの確認にも該当しなかったという意味です。",
  "boiler_h": "定型文",
  "boiler": "Verdetto: QR &amp; Barcode Scanner は、バージニア州の個人開発者 Verdetto による無料の Android アプリです。傷んだものを含む QR コードとバーコードを読み取り、何かが開く前にコードの中身をそのまま表示し、リンク、Wi-Fi ネットワーク、支払い先アドレス、電話番号に既知の警告サインがないかを端末上で確認します。既知のフィッシングや詐欺の一覧は公開されたフィードから公開の場で作られ、その署名は端末上で検証されます。アプリには広告もアカウントも解析もありません。任意の一回限りの支援が開発を支え、その先に何かが隠されていることはありません。Verdetto は「ヴェル・デット」と読み、イタリア語で「判決」を意味します。",
  "facts_h": "確認できる事実",
  "facts": [
   "プラットフォーム: Android 8 以降。価格: 無料。広告: なし。アカウント: なし。解析: なし。",
   "読み取りと内蔵の確認はすべて端末上で行われます。オンライン照会は初期状態でオンで、スイッチ一つで切れます。商品照会には専用のスイッチがあります。",
   "{N} 種類のコードを読み取ります（2026 年 9 月 4 日の検証で測定）。EAN、UPC、Code 128、Data Matrix、PDF417、Aztec を含みます。",
   "安全リストは <a href=\"https://github.com/verdettoqr/link-safety-list\">github.com/verdettoqr/link-safety-list</a> で公開の場で作られ、一日四回更新されます。アプリは使用前にその署名を検証します。",
   "アプリが決して言わないこと: リンク、ネットワーク、商品が安全だということ。表現は「警告は見つかりませんでした」です。",
   "比較の基準: 2026 年 9 月 4 日時点で Google Play のインストール数上位十本の無料 QR スキャナーを、その日のインストール数で特定。各掲載の広告表示と最も参考になるレビューを同じ日に確認。「偽のボタン」はレビュー投稿者の表現で、私たちのものではありません。スキャナー名は挙げません。一覧とメモは保管しています。",
   "プライバシーポリシー: {PRIVACY_LINK}",
   "利用規約: {TERMS_LINK}"
  ],
  "assets_h": "素材",
  "assets": [
   "<a href=\"icon-512.png\">アプリアイコン、512 px PNG</a> と <a href=\"logo.svg\">SVG 版のアイコン</a>。ミントの地、濃いティールの QR マーク、一つの琥珀色のファインダー。",
   "明るい地向けの <a href=\"lockup-teal-amber.png\">ロックアップ（マークと名前）、透過 PNG</a>（ティールの本体、琥珀のアクセント）と、暗い地向けの <a href=\"lockup-white-amber.png\">本体が白の同じもの</a>。マークは色を保ち、名前のキャップハイトに揃います。",
   "<a href=\"og-image.png\">シェア画像、1200 × 630</a> と <a href=\"play-header-4096x2304.jpg\">横長バナー、4096 × 2304</a>。",
   "<a href=\"screens/result-sheet.webp\">結果シートのスクリーンショット</a>: 読み取ったリンクを開く前に表示し、「警告は見つかりませんでした」のチップ付き。",
   "<a href=\"screens/result-sheet-warning.webp\">結果シート、警告の状態</a>: 見間違えやすいアドレス（paypa1.com）を、何かが開く前に paypal.com の模倣として警告。",
   "<a href=\"verdetto-code-light.svg\">Verdetto コード、SVG</a>（白地にティール。<a href=\"verdetto-code-dark.svg\">黒地に白</a>）、PNG は<a href=\"verdetto-code-light-on-white.png\">白地</a>、<a href=\"verdetto-code-dark-on-black.png\">黒地</a>、または透過（<a href=\"verdetto-code-light-transparent.png\">ティール</a>、<a href=\"verdetto-code-dark-transparent.png\">白</a>）、そして<a href=\"verdetto-table-card.pdf\">印刷用テーブルカード</a>（<a href=\"verdetto-table-card.png\">PNG</a>）。開くのは https://verdettoqr.com だけで、他には何もありません。どのカメラアプリでも読み取れます。"
  ],
  "no_alter": "アイコンの色を変えたり、効果を加えたりしないでください。マークがブランドです。",
  "trademark": "Verdetto と Verdetto QR マークは商標です。VERDETTO の米国出願が審査中です（シリアル番号 50092495）。",
  "contact": "連絡先"
 },
 "zh-Hans": {
  "title": "媒体资料",
  "desc": "撰写 Verdetto: QR & Barcode Scanner 相关内容所需的一句话简介、标准介绍、可核实的事实和图片素材。",
  "meta": "准确描述 Verdetto 所需的一切，集中在一处。欢迎自由引用；下面这句话是我们在各处统一使用的。",
  "lead": "一句话。",
  "sentence": "Verdetto 是一款面向 Android 的免费二维码和条形码扫描器，没有广告，也没有假按钮。它在链接打开前先显示链接，专为读取受损的码而设计，并在手机上检查扫描内容是否有警告迹象。它从不说任何东西是安全的：“未发现警告”表示它的各项检查均未命中。",
  "boiler_h": "标准介绍",
  "boiler": "Verdetto: QR &amp; Barcode Scanner 是 Verdetto 出品的免费 Android 应用，开发者是弗吉尼亚州的一位独立开发者。它读取二维码和条形码（包括受损的码），在任何内容打开之前向用户完整显示码中的内容，并在手机本地检查链接、Wi-Fi 网络、付款地址和电话号码是否带有已知的警告迹象。它的已知钓鱼与诈骗条目列表由公开来源公开编制，签名在设备上校验。应用没有广告、没有账户、没有分析统计；可选的一次性支持用于开发，没有任何功能被锁在其后。Verdetto 读作“ver-DET-oh”，在意大利语中意为“判决”。",
  "facts_h": "可核实的事实",
  "facts": [
   "平台：Android 8 及更高版本。价格：免费。广告：无。账户：无。分析统计：无。",
   "扫描和所有内置检查都在手机上运行。在线查询默认开启，一个开关即可关闭；商品查询有单独的开关。",
   "读取 {N} 种码（在 2026 年 9 月 4 日的验证运行中测量），包括 EAN、UPC、Code 128、Data Matrix、PDF417 和 Aztec。",
   "安全列表在 <a href=\"https://github.com/verdettoqr/link-safety-list\">github.com/verdettoqr/link-safety-list</a> 公开构建，每天更新四次；应用在使用前校验其签名。",
   "应用从不说的话：某个链接、网络或商品是安全的。措辞是“未发现警告”。",
   "比较依据：截至 2026 年 9 月 4 日 Google Play 上安装量最高的十款免费二维码扫描器，按当日安装量确定；每个商店页面的广告标注及其最相关的评价于同日阅读；“假按钮”是评价者的说法，不是我们的；不点名任何扫描器；名单和记录留存备查。",
   "隐私政策：{PRIVACY_LINK}。",
   "使用条款：{TERMS_LINK}。"
  ],
  "assets_h": "素材",
  "assets": [
   "<a href=\"icon-512.png\">应用图标，512 px PNG</a> 和 <a href=\"logo.svg\">SVG 格式的图标</a>。薄荷色底，深青色二维码标志，一个琥珀色定位图案。",
   "用于浅色背景的 <a href=\"lockup-teal-amber.png\">标志组合（标志加名称），透明 PNG</a>（青色主体，琥珀色点缀），以及用于深色背景的 <a href=\"lockup-white-amber.png\">白色主体的同一版本</a>；标志保持原色，与名称的大写字母高度对齐。",
   "<a href=\"og-image.png\">分享图，1200 × 630</a> 和 <a href=\"play-header-4096x2304.jpg\">宽幅横幅，4096 × 2304</a>。",
   "<a href=\"screens/result-sheet.webp\">结果面板截图</a>：扫描到的链接在打开前显示，带有“未发现警告”标签。",
   "<a href=\"screens/result-sheet-warning.webp\">结果面板，警告状态</a>：一个仿冒地址（paypa1.com）在任何内容打开前被标记为模仿 paypal.com。",
   "<a href=\"verdetto-code-light.svg\">Verdetto 码，SVG</a>（白底青色；<a href=\"verdetto-code-dark.svg\">黑底白色</a>），PNG 版本<a href=\"verdetto-code-light-on-white.png\">白底</a>、<a href=\"verdetto-code-dark-on-black.png\">黑底</a>或透明底（<a href=\"verdetto-code-light-transparent.png\">青色</a>、<a href=\"verdetto-code-dark-transparent.png\">白色</a>），以及<a href=\"verdetto-table-card.pdf\">可打印的桌卡</a>（<a href=\"verdetto-table-card.png\">PNG</a>）。它只打开 https://verdettoqr.com，别无其他；任何相机应用都能读取。"
  ],
  "no_alter": "请不要更改图标的颜色或添加效果；这个标志就是品牌。",
  "trademark": "Verdetto 和 Verdetto 二维码标志是商标；VERDETTO 的美国商标申请正在审查中（序列号 50092495）。",
  "contact": "联系方式"
 },
 "ar": {
  "title": "ملف الصحافة",
  "desc": "الوصف في جملة واحدة، والنص المعياري، وحقائق يمكن التحقق منها، وصور للكتابة عن Verdetto: QR & Barcode Scanner.",
  "meta": "كل ما يلزم لوصف Verdetto بدقة، في مكان واحد. اقتبس بحرية؛ الجملة أدناه هي التي نستخدمها في كل مكان.",
  "lead": "في جملة واحدة.",
  "sentence": "Verdetto قارئ مجاني لرموز QR والباركود على Android، بلا إعلانات وبلا أزرار زائفة. يعرض الرابط قبل أن يُفتح، ومصمَّم لقراءة الرموز المتضررة، ويفحص المحتوى الممسوح بحثًا عن علامات تحذير على الهاتف نفسه. لا يقول أبدًا إن شيئًا ما آمن: «لم يُعثر على تحذيرات» تعني أن أيًا من فحوصه لم يطابق.",
  "boiler_h": "النص المعياري",
  "boiler": "Verdetto: QR &amp; Barcode Scanner تطبيق Android مجاني من Verdetto، مطوّر مستقل في فرجينيا. يقرأ رموز QR والباركود، بما فيها المتضررة، ويُظهر للشخص بالضبط ما يحتويه الرمز قبل أن يُفتح أي شيء، ويفحص الروابط وشبكات Wi-Fi وعناوين الدفع وأرقام الهواتف بحثًا عن علامات تحذير معروفة على الهاتف نفسه. قائمته بمدخلات التصيّد والاحتيال المعروفة تُجمَع بشكل مفتوح من مصادر عامة، ويُتحقَّق من توقيعها على الجهاز. لا إعلانات في التطبيق ولا حسابات ولا تحليلات؛ مساهمة اختيارية لمرة واحدة تدعم التطوير، ولا شيء مقفل خلفها. يُلفَظ Verdetto «فير-دِت-و» ويعني «الحُكم» بالإيطالية.",
  "facts_h": "حقائق يمكنك التحقق منها",
  "facts": [
   "المنصة: Android 8 وما بعده. السعر: مجاني. الإعلانات: لا شيء. الحسابات: لا شيء. التحليلات: لا شيء.",
   "المسح وكل فحص مدمج يعملان على الهاتف. عمليات البحث عبر الإنترنت مفعّلة افتراضيًا ويمكن إيقافها بمفتاح واحد؛ ولبحث المنتجات مفتاح خاص به.",
   "يقرأ {N} نوعًا من الرموز، قِيست في جولة التحقق بتاريخ 4 سبتمبر 2026، ومنها EAN وUPC وCode 128 وData Matrix وPDF417 وAztec.",
   "تُبنى قائمة الأمان بشكل مفتوح على <a href=\"https://github.com/verdettoqr/link-safety-list\">github.com/verdettoqr/link-safety-list</a> وتُحدَّث أربع مرات يوميًا؛ ويتحقق التطبيق من توقيعها قبل الاستخدام.",
   "ما لا يقوله التطبيق أبدًا: أن رابطًا أو شبكة أو منتجًا آمن. الصياغة هي «لم يُعثر على تحذيرات».",
   "أساس المقارنة: أكثر عشرة قارئات QR مجانية تثبيتًا على Google Play بتاريخ 4 سبتمبر 2026، حُددت بعدد التثبيتات في ذلك اليوم؛ وقُرئت في اليوم نفسه علامة الإعلانات لكل صفحة وأكثر مراجعاتها صلة؛ و«الزر الزائف» وصفُ المراجعين لا وصفنا؛ ولا يُسمّى أي قارئ؛ والقائمة والملاحظات محفوظة لدينا.",
   "سياسة الخصوصية: {PRIVACY_LINK}.",
   "الشروط: {TERMS_LINK}."
  ],
  "assets_h": "المواد",
  "assets": [
   "<a href=\"icon-512.png\">أيقونة التطبيق، PNG بحجم 512 بكسل</a> و<a href=\"logo.svg\">الأيقونة بصيغة SVG</a>. أرضية بلون النعناع، علامة QR بلون أزرق مخضرّ داكن، ونمط تحديد واحد بلون كهرماني.",
   "<a href=\"lockup-teal-amber.png\">الشعار المركّب، العلامة والاسم، PNG شفاف</a> للأرضيات الفاتحة (جسم أزرق مخضرّ، لمسة كهرمانية) و<a href=\"lockup-white-amber.png\">النسخة نفسها بجسم أبيض</a> للأرضيات الداكنة؛ تحتفظ العلامة بألوانها وتقف على ارتفاع الأحرف الكبيرة في الاسم.",
   "<a href=\"og-image.png\">صورة المشاركة، 1200 × 630</a> و<a href=\"play-header-4096x2304.jpg\">لافتة عريضة، 4096 × 2304</a>.",
   "<a href=\"screens/result-sheet.webp\">لقطة شاشة لورقة النتيجة</a>: رابط ممسوح يُعرض قبل أن يُفتح، مع شارة «لم يُعثر على تحذيرات».",
   "<a href=\"screens/result-sheet-warning.webp\">ورقة النتيجة في حالة التحذير</a>: عنوان مشابه (paypa1.com) مُعلَّم بوصفه تقليدًا لـ paypal.com قبل أن يُفتح أي شيء.",
   "<a href=\"verdetto-code-light.svg\">رمز Verdetto، SVG</a> (أزرق مخضرّ على أبيض؛ <a href=\"verdetto-code-dark.svg\">أبيض على أسود</a>)، وبصيغة PNG <a href=\"verdetto-code-light-on-white.png\">على أبيض</a>، أو <a href=\"verdetto-code-dark-on-black.png\">على أسود</a>، أو بخلفية شفافة (<a href=\"verdetto-code-light-transparent.png\">أزرق مخضرّ</a>، <a href=\"verdetto-code-dark-transparent.png\">أبيض</a>)، و<a href=\"verdetto-table-card.pdf\">بطاقة الطاولة القابلة للطباعة</a> (<a href=\"verdetto-table-card.png\">PNG</a>). يفتح https://verdettoqr.com ولا شيء غيره؛ ويقرأه أي تطبيق كاميرا."
  ],
  "no_alter": "يُرجى عدم تغيير ألوان الأيقونة أو إضافة تأثيرات؛ فالعلامة هي الهوية.",
  "trademark": "Verdetto وعلامة Verdetto QR علامتان تجاريتان؛ وهناك طلب تسجيل لـ VERDETTO قيد النظر في الولايات المتحدة (الرقم التسلسلي 50092495).",
  "contact": "للتواصل"
 }
}


def press_body(t, code):
    """The press kit from its strings table, in the English page's structure; asset and repository links are constant,
    the policy links follow the language."""
    def policy(base):
        h = href(localized(base, code))
        return f'<a href="{h}">verdettoqr.com{h}</a>'
    priv, terms = policy("privacy.html"), policy("terms.html")
    items = [x.replace("{PRIVACY_LINK}", priv).replace("{TERMS_LINK}", terms).replace("{N}", str(len(FORMATS_READ))) for x in t["facts"]]
    facts = "\n".join("  <li>" + x + "</li>" for x in items)
    assets = "\n".join("  <li>" + x + "</li>" for x in t["assets"])
    social = "".join(f'  <li>{k}: <a href="{v}">{v}</a></li>\n' for k, v in SOCIAL.items())
    where = chrome(code)["where"].rstrip(":\uff1a")
    return (f'\n<div class="prose">\n<h1>{t["title"]}</h1>\n<p class="meta">{t["meta"]}</p>\n\n'
            f'<div class="card"><p><strong>{t["lead"]}</strong> {t["sentence"]}</p></div>\n\n'
            f'<h2>{t["boiler_h"]}</h2>\n<p>{t["boiler"]}</p>\n\n'
            f'<h2>{t["facts_h"]}</h2>\n<ul>\n{facts}\n</ul>\n\n'
            f'<h2>{t["assets_h"]}</h2>\n<ul>\n{assets}\n</ul>\n<p>{t["no_alter"]}</p>\n<p>{t["trademark"]}</p>\n\n'
            f'<h2>{where}</h2>\n<ul>\n{social}  <li>{t["contact"]}: <a href="mailto:{EMAIL}">{EMAIL}</a></li>\n</ul>\n</div>\n')


def press_ld(t, code):
    return {"@type": "WebPage", "name": t["title"], "inLanguage": code, "publisher": ORG}


LOCAL["press.html"] = family_pages("press.html")

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

WEEKLY_T = {
 "de": {
  "title": "Die Sicherheitsliste diese Woche",
  "desc": "Wöchentliche Zahlen aus Verdettos öffentlicher Warnliste: Meldungen, Fälle, Neueinträge nach Prüfung, Entfernungen, Gesamtstände. Nur öffentliche Daten.",
  "fallback": "Die Zahlen der ersten Woche kommen am Montag.",
  "meta": "{span}. Aktualisiert am {generated} aus dem öffentlichen Repository; das nächste Update kommt am kommenden Montag.",
  "intro": "Das sind die Zahlen hinter Verdettos eigenem Teil der Warnliste: was Menschen gemeldet haben, was ein Mensch geprüft hat und was sich auf der Liste geändert hat. Sie stammen aus den öffentlichen Fall-Issues und den Listendateien im Repository, sonst nirgendwoher. Keine Telemetrie, keine Daten pro Scan, nichts von irgendjemandes Telefon; die App meldet nie, was sie gescannt hat, und diese Seite könnte es nicht zeigen, selbst wenn sie es täte.",
  "th": [
   "Zahl",
   "Diese Woche",
   "Was sie zählt"
  ],
  "rows": [
   [
    "Eingegangene Meldungen",
    "Meldungen, die über das Formular oder die App die Liste erreicht haben, je einmal gezählt."
   ],
   [
    "Eröffnete Fälle",
    "Meldungen, die ein Mensch als öffentlichen Fall zur Prüfung aufgenommen hat."
   ],
   [
    "Abgeschlossene Fälle",
    "Diese Woche entschiedene Fälle: gelistet, aus Versehen gelistet oder kein Phishing."
   ],
   [
    "Aufgenommene Einträge",
    "Adressen oder Hosts, die nach der Prüfung einer Meldung durch einen Menschen in die Liste kamen."
   ],
   [
    "Nach Prüfung entfernt",
    "Einträge, die von der Liste genommen wurden, nachdem sich eine Meldung über einen versehentlichen Eintrag bestätigt hat."
   ],
   [
    "Jetzt auf der Liste",
    "Verdettos eigene Einträge, von Menschen gemeldet und von einem Menschen bestätigt; die öffentlichen Quellen, die die Liste zusätzlich führt, werden im Repository gezählt."
   ]
  ],
  "added": "{u} Links, {h} Hosts, {a} Wallet-Adressen",
  "totals": "{u} Links, {h} Hosts, {a} Wallet-Adressen; {al} erlaubt",
  "closing": "Jeder Fall ist ein öffentliches Issue, jeder Eintrag trägt den Fall, der ihn ausgelöst hat, und jeder Eintrag läuft ab, wenn ihn kein Mensch erneuert: <a href=\"https://github.com/verdettoqr/link-safety-list\">github.com/verdettoqr/link-safety-list</a>. Du glaubst, etwas ist aus Versehen gelistet? <a href=\"{REPORT_HREF}?k=m\">Melde es</a>; ein Mensch prüft es erneut, und die Entfernung erscheint hier.",
  "note": "Die Wochenzahlen sind eine kleine Datei, die diese Seite selbst ausliefert, einmal pro Woche aus dem Repository kopiert; dein Browser stellt für diese Seite keine Anfrage an Dritte.",
  "months": [
   "Januar",
   "Februar",
   "März",
   "April",
   "Mai",
   "Juni",
   "Juli",
   "August",
   "September",
   "Oktober",
   "November",
   "Dezember"
  ],
  "span_same": "{d1}. bis {d2}. {M} {y}",
  "span_cross": "{d1}. {M1} bis {d2}. {M2} {y}",
  "ld_desc": "Wöchentliche Zahlen zu Meldungen, Fällen und Listeneinträgen für Verdettos eigenen Teil der Warnliste, aus öffentlichen Daten."
 },
 "es": {
  "title": "La lista de seguridad esta semana",
  "desc": "Cifras semanales de la lista pública de avisos de Verdetto: informes, casos, entradas añadidas tras revisión, retiradas y totales. Solo datos públicos.",
  "fallback": "Las cifras de la primera semana llegan el lunes.",
  "meta": "{span}. Actualizado el {generated} desde el repositorio público; la próxima actualización es el lunes que viene.",
  "intro": "Estas son las cifras detrás de la parte propia de Verdetto en la lista de avisos: lo que la gente informó, lo que revisó una persona y lo que cambió en la lista. Salen de los casos públicos y de los archivos de la lista en el repositorio, de nada más. Sin telemetría, sin datos por escaneo, nada del teléfono de nadie; la app nunca informa de lo que escaneó, y esta página no podría mostrarlo aunque lo hiciera.",
  "th": [
   "Cifra",
   "Esta semana",
   "Qué cuenta"
  ],
  "rows": [
   [
    "Informes recibidos",
    "Informes que llegaron a la lista por el formulario o la app, contados una vez cada uno."
   ],
   [
    "Casos abiertos",
    "Informes que una persona tomó para revisar como caso público."
   ],
   [
    "Casos cerrados",
    "Casos decididos esta semana: incluido, incluido por error o no es phishing."
   ],
   [
    "Entradas añadidas",
    "Direcciones o hosts añadidos a la lista después de que una persona revisara un informe."
   ],
   [
    "Retiradas tras revisión",
    "Entradas quitadas de la lista después de comprobarse un informe de inclusión por error."
   ],
   [
    "En la lista ahora",
    "Las entradas propias de Verdetto, las que la gente informó y una persona confirmó; las fuentes públicas que la lista también incluye se cuentan en el repositorio."
   ]
  ],
  "added": "{u} enlaces, {h} hosts, {a} direcciones de monedero",
  "totals": "{u} enlaces, {h} hosts, {a} direcciones de monedero; {al} permitidas",
  "closing": "Cada caso es un issue público, cada inclusión lleva el caso que la causó y cada entrada caduca si una persona no la renueva: <a href=\"https://github.com/verdettoqr/link-safety-list\">github.com/verdettoqr/link-safety-list</a>. ¿Crees que algo está incluido por error? <a href=\"{REPORT_HREF}?k=m\">Infórmalo</a>; una persona lo vuelve a comprobar y la retirada aparece aquí.",
  "note": "Las cifras semanales son un archivo pequeño que este sitio sirve por sí mismo, copiado del repositorio una vez por semana; tu navegador no hace ninguna petición a terceros para esta página.",
  "months": [
   "enero",
   "febrero",
   "marzo",
   "abril",
   "mayo",
   "junio",
   "julio",
   "agosto",
   "septiembre",
   "octubre",
   "noviembre",
   "diciembre"
  ],
  "span_same": "Del {d1} al {d2} de {M} de {y}",
  "span_cross": "Del {d1} de {M1} al {d2} de {M2} de {y}",
  "ld_desc": "Cifras semanales de informes, casos y entradas de la parte propia de Verdetto en la lista de avisos, a partir de datos públicos."
 },
 "fr": {
  "title": "La liste de sécurité cette semaine",
  "desc": "Chiffres de la semaine pour la liste d'alerte publique de Verdetto : signalements, dossiers, ajouts après examen, retraits, totaux. Données publiques seulement.",
  "fallback": "Les chiffres de la première semaine arrivent lundi.",
  "meta": "{span}. Mis à jour le {generated} depuis le dépôt public ; la prochaine mise à jour a lieu lundi prochain.",
  "intro": "Voici les chiffres derrière la part propre de Verdetto dans la liste d'alerte : ce que les gens ont signalé, ce qu'une personne a examiné et ce qui a changé sur la liste. Ils viennent des dossiers publics et des fichiers de la liste dans le dépôt, de rien d'autre. Pas de télémétrie, pas de données par scan, rien du téléphone de quiconque ; l'application ne rapporte jamais ce qu'elle a scanné, et cette page ne pourrait pas le montrer même si elle le faisait.",
  "th": [
   "Chiffre",
   "Cette semaine",
   "Ce qu'il compte"
  ],
  "rows": [
   [
    "Signalements reçus",
    "Signalements arrivés à la liste par le formulaire ou l'application, comptés une fois chacun."
   ],
   [
    "Dossiers ouverts",
    "Signalements qu'une personne a pris en examen comme dossier public."
   ],
   [
    "Dossiers clos",
    "Dossiers tranchés cette semaine : inscrit, inscrit par erreur, ou pas un phishing."
   ],
   [
    "Entrées ajoutées",
    "Adresses ou hôtes ajoutés à la liste après qu'une personne a examiné un signalement."
   ],
   [
    "Retirées après examen",
    "Entrées retirées de la liste après vérification d'un signalement d'inscription par erreur."
   ],
   [
    "Sur la liste aujourd'hui",
    "Les entrées propres de Verdetto, signalées par des gens et confirmées par une personne ; les flux publics que la liste reprend aussi sont comptés sur le dépôt."
   ]
  ],
  "added": "{u} liens, {h} hôtes, {a} adresses de portefeuille",
  "totals": "{u} liens, {h} hôtes, {a} adresses de portefeuille ; {al} autorisées",
  "closing": "Chaque dossier est un ticket public, chaque inscription porte le dossier qui l'a causée, et chaque entrée expire si personne ne la renouvelle : <a href=\"https://github.com/verdettoqr/link-safety-list\">github.com/verdettoqr/link-safety-list</a>. Vous pensez que quelque chose est inscrit par erreur ? <a href=\"{REPORT_HREF}?k=m\">Signalez-le</a> ; une personne revérifie et le retrait apparaît ici.",
  "note": "Les chiffres de la semaine sont un petit fichier que ce site sert lui-même, copié du dépôt une fois par semaine ; votre navigateur ne fait aucune requête à un tiers pour cette page.",
  "months": [
   "janvier",
   "février",
   "mars",
   "avril",
   "mai",
   "juin",
   "juillet",
   "août",
   "septembre",
   "octobre",
   "novembre",
   "décembre"
  ],
  "span_same": "Du {d1} au {d2} {M} {y}",
  "span_cross": "Du {d1} {M1} au {d2} {M2} {y}",
  "ld_desc": "Chiffres hebdomadaires des signalements, dossiers et entrées de la part propre de Verdetto dans la liste d'alerte, à partir de données publiques."
 },
 "pt-BR": {
  "title": "A lista de segurança nesta semana",
  "desc": "Números semanais da lista pública de alertas do Verdetto: relatos, casos, entradas adicionadas após análise, remoções e totais. Só dados públicos.",
  "fallback": "Os números da primeira semana chegam na segunda-feira.",
  "meta": "{span}. Atualizado em {generated} a partir do repositório público; a próxima atualização é na segunda-feira que vem.",
  "intro": "Estes são os números por trás da parte própria do Verdetto na lista de alertas: o que as pessoas relataram, o que uma pessoa analisou e o que mudou na lista. Eles vêm dos casos públicos e dos arquivos da lista no repositório, de mais nada. Sem telemetria, sem dados por leitura, nada do celular de ninguém; o app nunca informa o que leu, e esta página não poderia mostrar isso mesmo se ele informasse.",
  "th": [
   "Número",
   "Nesta semana",
   "O que conta"
  ],
  "rows": [
   [
    "Relatos recebidos",
    "Relatos que chegaram à lista pelo formulário ou pelo app, contados uma vez cada."
   ],
   [
    "Casos abertos",
    "Relatos que uma pessoa assumiu para análise como caso público."
   ],
   [
    "Casos encerrados",
    "Casos decididos nesta semana: listado, listado por engano ou não é phishing."
   ],
   [
    "Entradas adicionadas",
    "Endereços ou hosts adicionados à lista depois que uma pessoa analisou um relato."
   ],
   [
    "Removidas após análise",
    "Entradas tiradas da lista depois que um relato de inclusão por engano se confirmou."
   ],
   [
    "Na lista agora",
    "As entradas próprias do Verdetto, relatadas por pessoas e confirmadas por uma pessoa; as fontes públicas que a lista também traz são contadas no repositório."
   ]
  ],
  "added": "{u} links, {h} hosts, {a} endereços de carteira",
  "totals": "{u} links, {h} hosts, {a} endereços de carteira; {al} permitidas",
  "closing": "Cada caso é um issue público, cada inclusão traz o caso que a causou, e cada entrada expira se uma pessoa não a renovar: <a href=\"https://github.com/verdettoqr/link-safety-list\">github.com/verdettoqr/link-safety-list</a>. Acha que algo foi listado por engano? <a href=\"{REPORT_HREF}?k=m\">Relate</a>; uma pessoa confere de novo e a remoção aparece aqui.",
  "note": "Os números semanais são um arquivo pequeno que este site serve por conta própria, copiado do repositório uma vez por semana; seu navegador não faz nenhuma requisição a terceiros para esta página.",
  "months": [
   "janeiro",
   "fevereiro",
   "março",
   "abril",
   "maio",
   "junho",
   "julho",
   "agosto",
   "setembro",
   "outubro",
   "novembro",
   "dezembro"
  ],
  "span_same": "De {d1} a {d2} de {M} de {y}",
  "span_cross": "De {d1} de {M1} a {d2} de {M2} de {y}",
  "ld_desc": "Números semanais de relatos, casos e entradas da parte própria do Verdetto na lista de alertas, a partir de dados públicos."
 },
 "id": {
  "title": "Daftar keamanan minggu ini",
  "desc": "Angka mingguan dari daftar peringatan publik Verdetto: laporan, kasus, entri yang ditambahkan setelah tinjauan, penghapusan, total. Hanya data publik.",
  "fallback": "Angka minggu pertama tiba pada hari Senin.",
  "meta": "{span}. Diperbarui {generated} dari repositori publik; pembaruan berikutnya pada Senin mendatang.",
  "intro": "Inilah angka di balik bagian Verdetto sendiri dalam daftar peringatan: apa yang orang laporkan, apa yang ditinjau seorang manusia, dan apa yang berubah pada daftar. Semuanya berasal dari isu kasus publik dan berkas daftar di repositori, tidak dari yang lain. Tanpa telemetri, tanpa data per pindaian, tidak ada apa pun dari ponsel siapa pun; aplikasi tidak pernah melaporkan apa yang dipindainya, dan halaman ini tidak bisa menampilkannya bahkan jika ia melaporkan.",
  "th": [
   "Angka",
   "Minggu ini",
   "Apa yang dihitung"
  ],
  "rows": [
   [
    "Laporan diterima",
    "Laporan yang sampai ke daftar lewat formulir atau aplikasi, dihitung sekali masing-masing."
   ],
   [
    "Kasus dibuka",
    "Laporan yang diambil seorang manusia untuk ditinjau sebagai kasus publik."
   ],
   [
    "Kasus ditutup",
    "Kasus yang diputus minggu ini: didaftar, didaftar karena keliru, atau bukan phishing."
   ],
   [
    "Entri ditambahkan",
    "Alamat atau host yang ditambahkan ke daftar setelah seorang manusia meninjau laporan."
   ],
   [
    "Dihapus setelah tinjauan",
    "Entri yang dikeluarkan dari daftar setelah laporan salah daftar terbukti benar."
   ],
   [
    "Ada di daftar sekarang",
    "Entri Verdetto sendiri, yang dilaporkan orang dan dikonfirmasi seorang manusia; umpan publik yang juga dimuat daftar dihitung di repositori."
   ]
  ],
  "added": "{u} tautan, {h} host, {a} alamat dompet",
  "totals": "{u} tautan, {h} host, {a} alamat dompet; {al} diizinkan",
  "closing": "Setiap kasus adalah isu publik, setiap pendaftaran membawa kasus yang menyebabkannya, dan setiap entri kedaluwarsa kecuali seorang manusia memperbaruinya: <a href=\"https://github.com/verdettoqr/link-safety-list\">github.com/verdettoqr/link-safety-list</a>. Merasa ada yang terdaftar karena keliru? <a href=\"{REPORT_HREF}?k=m\">Laporkan</a>; seorang manusia memeriksanya lagi dan penghapusannya muncul di sini.",
  "note": "Angka mingguan adalah berkas kecil yang disajikan situs ini sendiri, disalin dari repositori sekali seminggu; peramban Anda tidak membuat permintaan ke pihak ketiga untuk halaman ini.",
  "months": [
   "Januari",
   "Februari",
   "Maret",
   "April",
   "Mei",
   "Juni",
   "Juli",
   "Agustus",
   "September",
   "Oktober",
   "November",
   "Desember"
  ],
  "span_same": "{d1} sampai {d2} {M} {y}",
  "span_cross": "{d1} {M1} sampai {d2} {M2} {y}",
  "ld_desc": "Angka mingguan laporan, kasus, dan entri untuk bagian Verdetto sendiri dalam daftar peringatan, dari data publik."
 },
 "ru": {
  "title": "Список безопасности за неделю",
  "desc": "Еженедельные цифры публичного списка предупреждений Verdetto: сообщения, дела, записи после проверки, удаления, итоги. Только публичные данные.",
  "fallback": "Цифры первой недели появятся в понедельник.",
  "meta": "{span}. Обновлено {generated} из публичного репозитория; следующее обновление в ближайший понедельник.",
  "intro": "Это цифры собственной части Verdetto в списке предупреждений: о чём сообщали люди, что проверил человек и что изменилось в списке. Они берутся из публичных дел и файлов списка в репозитории и больше ниоткуда. Никакой телеметрии, никаких данных по сканированиям, ничего с чьего-либо телефона; приложение никогда не сообщает, что оно отсканировало, и эта страница не смогла бы это показать, даже если бы сообщало.",
  "th": [
   "Показатель",
   "За неделю",
   "Что считается"
  ],
  "rows": [
   [
    "Получено сообщений",
    "Сообщения, дошедшие до списка через форму или приложение, каждое учтено один раз."
   ],
   [
    "Открыто дел",
    "Сообщения, которые человек взял на проверку как публичное дело."
   ],
   [
    "Закрыто дел",
    "Дела, решённые за неделю: внесено, внесено по ошибке или не фишинг."
   ],
   [
    "Добавлено записей",
    "Адреса или хосты, добавленные в список после того, как человек проверил сообщение."
   ],
   [
    "Удалено после проверки",
    "Записи, убранные из списка после подтверждения сообщения об ошибочном внесении."
   ],
   [
    "Сейчас в списке",
    "Собственные записи Verdetto, о которых сообщили люди и которые подтвердил человек; публичные источники, которые список тоже включает, считаются в репозитории."
   ]
  ],
  "added": "{u} ссылок, {h} хостов, {a} адресов кошельков",
  "totals": "{u} ссылок, {h} хостов, {a} адресов кошельков; {al} разрешено",
  "closing": "Каждое дело — публичный issue, каждое внесение несёт вызвавшее его дело, и каждая запись истекает, если человек её не продлит: <a href=\"https://github.com/verdettoqr/link-safety-list\">github.com/verdettoqr/link-safety-list</a>. Считаете, что что-то внесено по ошибке? <a href=\"{REPORT_HREF}?k=m\">Сообщите</a>; человек перепроверит, и удаление появится здесь.",
  "note": "Недельные цифры — небольшой файл, который этот сайт отдаёт сам, копируя его из репозитория раз в неделю; ваш браузер не делает запросов к третьим сторонам для этой страницы.",
  "months": [
   "января",
   "февраля",
   "марта",
   "апреля",
   "мая",
   "июня",
   "июля",
   "августа",
   "сентября",
   "октября",
   "ноября",
   "декабря"
  ],
  "span_same": "С {d1} по {d2} {M} {y} года",
  "span_cross": "С {d1} {M1} по {d2} {M2} {y} года",
  "ld_desc": "Еженедельные цифры сообщений, дел и записей собственной части Verdetto в списке предупреждений, из публичных данных."
 },
 "hi": {
  "title": "इस सप्ताह की सुरक्षा सूची",
  "desc": "Verdetto की सार्वजनिक चेतावनी सूची के साप्ताहिक आँकड़े: रिपोर्ट, केस, समीक्षा के बाद जोड़ी गई प्रविष्टियाँ, हटाई गई प्रविष्टियाँ, कुल। केवल सार्वजनिक डेटा।",
  "fallback": "पहले सप्ताह के आँकड़े सोमवार को आते हैं।",
  "meta": "{span}। सार्वजनिक रिपॉज़िटरी से {generated} को अपडेट किया गया; अगला अपडेट आने वाले सोमवार को।",
  "intro": "ये चेतावनी सूची में Verdetto के अपने हिस्से के पीछे के आँकड़े हैं: लोगों ने क्या रिपोर्ट किया, एक व्यक्ति ने क्या समीक्षा की, और सूची में क्या बदला। ये सार्वजनिक केस इश्यू और रिपॉज़िटरी की सूची फ़ाइलों से आते हैं, और कहीं से नहीं। कोई टेलीमेट्री नहीं, प्रति-स्कैन कोई डेटा नहीं, किसी के फ़ोन से कुछ नहीं; ऐप कभी नहीं बताता कि उसने क्या स्कैन किया, और अगर बताता भी, तो यह पेज उसे दिखा नहीं सकता।",
  "th": [
   "आँकड़ा",
   "इस सप्ताह",
   "यह क्या गिनता है"
  ],
  "rows": [
   [
    "प्राप्त रिपोर्ट",
    "रिपोर्ट फ़ॉर्म या ऐप से सूची तक पहुँची रिपोर्टें, हर एक एक बार गिनी गई।"
   ],
   [
    "खोले गए केस",
    "रिपोर्टें जिन्हें एक व्यक्ति ने सार्वजनिक केस के रूप में समीक्षा के लिए लिया।"
   ],
   [
    "बंद किए गए केस",
    "इस सप्ताह तय किए गए केस: सूचीबद्ध, गलती से सूचीबद्ध, या फ़िशिंग नहीं।"
   ],
   [
    "जोड़ी गई प्रविष्टियाँ",
    "एक व्यक्ति द्वारा रिपोर्ट की समीक्षा के बाद सूची में जोड़े गए पते या होस्ट।"
   ],
   [
    "समीक्षा के बाद हटाई गई",
    "गलती से सूचीबद्ध होने की रिपोर्ट सही निकलने पर सूची से हटाई गई प्रविष्टियाँ।"
   ],
   [
    "अब सूची में",
    "Verdetto की अपनी प्रविष्टियाँ, जिन्हें लोगों ने रिपोर्ट किया और एक व्यक्ति ने पुष्टि की; सूची में शामिल सार्वजनिक फ़ीड रिपॉज़िटरी में गिनी जाती हैं।"
   ]
  ],
  "added": "{u} लिंक, {h} होस्ट, {a} वॉलेट पते",
  "totals": "{u} लिंक, {h} होस्ट, {a} वॉलेट पते; {al} अनुमत",
  "closing": "हर केस एक सार्वजनिक इश्यू है, हर सूचीबद्धता उस केस को साथ रखती है जिसने उसे बनाया, और हर प्रविष्टि समाप्त हो जाती है जब तक कोई व्यक्ति उसे नवीनीकृत न करे: <a href=\"https://github.com/verdettoqr/link-safety-list\">github.com/verdettoqr/link-safety-list</a>। लगता है कुछ गलती से सूचीबद्ध है? <a href=\"{REPORT_HREF}?k=m\">रिपोर्ट करें</a>; एक व्यक्ति उसे फिर जाँचता है और हटाना यहाँ दिखता है।",
  "note": "साप्ताहिक आँकड़े एक छोटी फ़ाइल हैं जो यह साइट खुद परोसती है, सप्ताह में एक बार रिपॉज़िटरी से कॉपी की गई; इस पेज के लिए आपका ब्राउज़र किसी तीसरे पक्ष से कोई अनुरोध नहीं करता।",
  "months": [
   "जनवरी",
   "फ़रवरी",
   "मार्च",
   "अप्रैल",
   "मई",
   "जून",
   "जुलाई",
   "अगस्त",
   "सितंबर",
   "अक्टूबर",
   "नवंबर",
   "दिसंबर"
  ],
  "span_same": "{d1} से {d2} {M} {y}",
  "span_cross": "{d1} {M1} से {d2} {M2} {y}",
  "ld_desc": "चेतावनी सूची में Verdetto के अपने हिस्से की रिपोर्ट, केस और प्रविष्टियों के साप्ताहिक आँकड़े, सार्वजनिक डेटा से।"
 },
 "ja": {
  "title": "今週の安全リスト",
  "desc": "Verdetto の公開警告リストの週間の数字: 報告、案件、確認後に追加された項目、削除、合計。公開データのみで、誰かの端末からの情報はありません。",
  "fallback": "最初の週の数字は月曜日に届きます。",
  "meta": "{span}。{generated} に公開リポジトリから更新。次の更新は次の月曜日です。",
  "intro": "これは警告リストのうち Verdetto 自身の部分の数字です。人々が何を報告し、人が何を確認し、リストで何が変わったか。出典は公開の案件と、リポジトリ内のリストのファイルだけです。テレメトリーも、読み取りごとのデータも、誰かの端末からの情報もありません。アプリは何を読み取ったかを決して報告せず、仮に報告したとしてもこのページには表示できません。",
  "th": [
   "項目",
   "今週",
   "数えているもの"
  ],
  "rows": [
   [
    "受け取った報告",
    "報告フォームまたはアプリからリストに届いた報告。それぞれ一回だけ数えます。"
   ],
   [
    "開いた案件",
    "人が公開の案件として確認に取り上げた報告。"
   ],
   [
    "閉じた案件",
    "今週判断された案件: 登録、誤登録、またはフィッシングではない。"
   ],
   [
    "追加した項目",
    "人が報告を確認したあとにリストへ追加したアドレスやホスト。"
   ],
   [
    "確認後に削除",
    "誤登録の報告が正しいと分かり、リストから外した項目。"
   ],
   [
    "現在リストにあるもの",
    "人々が報告し人が確認した Verdetto 自身の項目。リストが併載する公開フィードはリポジトリ側で数えています。"
   ]
  ],
  "added": "リンク {u}、ホスト {h}、ウォレットアドレス {a}",
  "totals": "リンク {u}、ホスト {h}、ウォレットアドレス {a}。許可 {al}",
  "closing": "すべての案件は公開の issue で、すべての登録はその原因となった案件を伴い、すべての項目は人が更新しなければ失効します: <a href=\"https://github.com/verdettoqr/link-safety-list\">github.com/verdettoqr/link-safety-list</a>。誤登録だと思われるものがありますか? <a href=\"{REPORT_HREF}?k=m\">報告してください</a>。人が再確認し、削除はここに表れます。",
  "note": "週間の数字は、このサイト自身が配信する小さなファイルで、週に一度リポジトリからコピーされます。このページのためにブラウザが第三者へ要求を送ることはありません。",
  "months": None,
  "span_same": "{y}年{m}月{d1}日～{d2}日",
  "span_cross": "{y}年{m1}月{d1}日～{m2}月{d2}日",
  "ld_desc": "警告リストのうち Verdetto 自身の部分について、報告、案件、リスト項目の週間の数。公開データから。"
 },
 "zh-Hans": {
  "title": "本周的安全列表",
  "desc": "Verdetto 公开警告列表的每周数字：报告、案例、审核后新增的条目、移除、总数。仅公开数据，不含任何来自手机的信息。",
  "fallback": "第一周的数字将于周一到来。",
  "meta": "{span}。于 {generated} 从公开仓库更新；下次更新在下周一。",
  "intro": "这些是警告列表中 Verdetto 自有部分背后的数字：人们报告了什么、由人审核了什么、列表发生了什么变化。它们只来自公开的案例议题和仓库中的列表文件，别无其他。没有遥测，没有逐次扫描的数据，没有任何来自任何人手机的信息；应用从不报告它扫描了什么，即使报告，这个页面也无法显示。",
  "th": [
   "数字",
   "本周",
   "它统计什么"
  ],
  "rows": [
   [
    "收到的报告",
    "通过报告表单或应用到达列表的报告，每份只计一次。"
   ],
   [
    "开启的案例",
    "由人接手、作为公开案例审核的报告。"
   ],
   [
    "结束的案例",
    "本周裁定的案例：已列入、误列，或并非钓鱼。"
   ],
   [
    "新增的条目",
    "由人审核报告后加入列表的地址或主机。"
   ],
   [
    "审核后移除",
    "误列报告核实后从列表中移除的条目。"
   ],
   [
    "当前在列表中",
    "Verdetto 自有的条目，由人们报告并经人确认；列表同时收录的公开源在仓库中统计。"
   ]
  ],
  "added": "{u} 个链接、{h} 个主机、{a} 个钱包地址",
  "totals": "{u} 个链接、{h} 个主机、{a} 个钱包地址；{al} 个放行",
  "closing": "每个案例都是公开议题，每条列入都附带导致它的案例，每个条目如无人续期都会过期：<a href=\"https://github.com/verdettoqr/link-safety-list\">github.com/verdettoqr/link-safety-list</a>。觉得有什么被误列了？<a href=\"{REPORT_HREF}?k=m\">报告它</a>；由人重新核查，移除结果会显示在这里。",
  "note": "每周数字是本站自行提供的一个小文件，每周从仓库复制一次；浏览器不会为此页面向任何第三方发出请求。",
  "months": None,
  "span_same": "{y}年{m}月{d1}日至{d2}日",
  "span_cross": "{y}年{m1}月{d1}日至{m2}月{d2}日",
  "ld_desc": "警告列表中 Verdetto 自有部分的报告、案例和列表条目的每周计数，来自公开数据。"
 },
 "ar": {
  "title": "قائمة الأمان هذا الأسبوع",
  "desc": "أرقام أسبوعية من قائمة التحذير العامة لـ Verdetto: البلاغات، والحالات، والمدخلات المضافة بعد المراجعة، والمحذوفات، والمجاميع. بيانات عامة فقط.",
  "fallback": "أرقام الأسبوع الأول تصل يوم الاثنين.",
  "meta": "{span}. حُدِّث في {generated} من المستودع العام؛ التحديث التالي يوم الاثنين المقبل.",
  "intro": "هذه هي الأرقام خلف جزء Verdetto الخاص من قائمة التحذير: ما أبلغ عنه الناس، وما راجعه شخص، وما تغيّر في القائمة. تأتي من قضايا الحالات العامة وملفات القائمة في المستودع، لا من شيء آخر. لا قياس عن بُعد، ولا بيانات لكل مسح، ولا شيء من هاتف أحد؛ فالتطبيق لا يبلّغ أبدًا عمّا مسحه، ولا تستطيع هذه الصفحة إظهاره حتى لو فعل.",
  "th": [
   "الرقم",
   "هذا الأسبوع",
   "ما الذي يعدّه"
  ],
  "rows": [
   [
    "البلاغات الواردة",
    "البلاغات التي وصلت إلى القائمة عبر نموذج البلاغ أو التطبيق، ويُعدّ كل منها مرة واحدة."
   ],
   [
    "الحالات المفتوحة",
    "بلاغات تولّى شخصٌ مراجعتها كحالة عامة."
   ],
   [
    "الحالات المغلقة",
    "حالات قُرِّرت هذا الأسبوع: مُدرَج، أو مُدرَج خطأً، أو ليس تصيّدًا."
   ],
   [
    "المدخلات المضافة",
    "عناوين أو مضيفات أُضيفت إلى القائمة بعد أن راجع شخصٌ بلاغًا."
   ],
   [
    "المحذوفة بعد المراجعة",
    "مدخلات أُزيلت من القائمة بعد أن ثبتت صحة بلاغ عن إدراج خاطئ."
   ],
   [
    "في القائمة الآن",
    "مدخلات Verdetto الخاصة، التي أبلغ عنها الناس وأكّدها شخص؛ أما المصادر العامة التي تحملها القائمة أيضًا فتُعدّ في المستودع."
   ]
  ],
  "added": "{u} روابط، {h} مضيفات، {a} عناوين محافظ",
  "totals": "{u} روابط، {h} مضيفات، {a} عناوين محافظ؛ {al} مسموح بها",
  "closing": "كل حالة قضية عامة، وكل إدراج يحمل الحالة التي سبّبته، وكل مدخل ينتهي ما لم يجدّده شخص: <a href=\"https://github.com/verdettoqr/link-safety-list\">github.com/verdettoqr/link-safety-list</a>. تظن أن شيئًا أُدرج خطأً؟ <a href=\"{REPORT_HREF}?k=m\">أبلغ عنه</a>؛ يعيد شخصٌ التحقق منه ويظهر الحذف هنا.",
  "note": "الأرقام الأسبوعية ملف صغير يقدّمه هذا الموقع بنفسه، يُنسَخ من المستودع مرة في الأسبوع؛ ولا يرسل متصفحك أي طلب إلى طرف ثالث من أجل هذه الصفحة.",
  "months": [
   "يناير",
   "فبراير",
   "مارس",
   "أبريل",
   "مايو",
   "يونيو",
   "يوليو",
   "أغسطس",
   "سبتمبر",
   "أكتوبر",
   "نوفمبر",
   "ديسمبر"
  ],
  "span_same": "من {d1} إلى {d2} {M} {y}",
  "span_cross": "من {d1} {M1} إلى {d2} {M2} {y}",
  "ld_desc": "أعداد أسبوعية للبلاغات والحالات ومدخلات القائمة لجزء Verdetto الخاص من قائمة التحذير، من بيانات عامة."
 }
}


def weekly_body(t, code):
    """The safety-list page from its strings table, same numbers as the English page (stats/weekly.json), dates in the
    language's own form; thousands separators stay the site's until a count needs one."""
    path = HERE / "stats" / "weekly.json"
    if not path.exists():
        return f"<h1>{t['title']}</h1>\n<p>{t['fallback']}</p>\n"
    s = json.loads(path.read_text(encoding="utf-8"))
    def ymd(iso):
        y, m, d = (int(x) for x in iso.split("-"))
        return y, m, d
    y1, m1, d1 = ymd(s["week_start"])
    y2, m2, d2 = ymd(s["week_end"])
    names = t["months"]
    vals = dict(d1=d1, d2=d2, y=y2, m=m1, m1=m1, m2=m2, M=names[m1 - 1] if names else "", M1=names[m1 - 1] if names else "", M2=names[m2 - 1] if names else "")
    span = (t["span_same"] if m1 == m2 else t["span_cross"]).format(**vals)
    n = lambda v: f"{int(v):,}"  # noqa: E731
    added = s.get("entries_added", {})
    totals = s.get("totals", {})
    generated = s.get("generated_at", "")[:10]
    values = [n(s.get("reports_received", 0)), n(s.get("cases_opened", 0)), n(s.get("cases_closed", 0)),
              t["added"].format(u=n(added.get("urls", 0)), h=n(added.get("hosts", 0)), a=n(added.get("addresses", 0))),
              n(s.get("unlisted", 0)),
              t["totals"].format(u=n(totals.get("urls", 0)), h=n(totals.get("hosts", 0)), a=n(totals.get("addresses", 0)), al=n(totals.get("allow", 0)))]
    table = "".join(f"<tr><td>{k}</td><td>{v}</td><td>{d}</td></tr>\n" for (k, d), v in zip(t["rows"], values))
    th = "".join(f"<th>{x}</th>" for x in t["th"])
    return (f'\n<h1>{t["title"]}</h1>\n<p class="meta">{t["meta"].format(span=span, generated=generated)}</p>\n<p>{t["intro"]}</p>\n'
            f'<div class="tablewrap"><table><thead><tr>{th}</tr></thead><tbody>\n{table}</tbody></table></div>\n'
            f'<p>{t["closing"].replace("{REPORT_HREF}", href(localized("report.html", code)))}</p>\n<p class="meta">{t["note"]}</p>\n')


def weekly_ld(t, code):
    return {**WEEKLY_LD, "name": t["title"], "description": t["ld_desc"], "inLanguage": code}


LOCAL["safety-list.html"] = family_pages("safety-list.html")


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

// the store page
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
<tr><td><code>app.scanner.action.CARD</code></td><td>No filter: an explicit intent with the package <code>com.verdettoqr.scanner</code> only.</td><td>Opens the person's own contact card editor, the code they show to share their details. Meant for the app's own widgets and shortcuts; another app may call it, but nothing comes back.</td><td>None</td></tr>
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
<p>Code written for the ZXing Barcode Scanner keeps working: send <code>com.google.zxing.client.android.SCAN</code> the same way and read the same two extras. If more than one scanner on the phone answers it, the system asks the person which to use; sending the intent to the package <code>com.verdettoqr.scanner</code> skips that.</p>

<h2>What the person sees</h2>
<p>The scanner opens as it always does, with its own checks. When a code locks, the app hands it back and closes; nothing of yours appears on the screen, and nothing of theirs (history, settings, the safety list) is touched by the call.</p>

<div class="card"><p><strong>Testing on a phone without the app.</strong> The store page, the same address the fallback in the samples opens: <a href="{play}">Get it on Google Play</a>. The source of this page is the app's own INTENT.md; when the two differ, the app repository is right and this page is behind.</p></div>
</div>
"""


DEV_T = {
 "de": {
  "title": "Für Entwickler",
  "desc": "Wie eine andere Android-App Verdetto zum Scannen öffnet und den Code zurückerhält: die Intents, die Ergebnis-Extras, Kotlin und Java, und was die Person sieht.",
  "h1": "Scannen aus einer anderen App",
  "meta": "Verdetto beantwortet drei Intents und ein Teilen. Nichts davon braucht eine Berechtigung, eine Bibliothek oder einen Schlüssel. Die Person behält jede Sicherheitsprüfung und jede Einstellung der App; deine App erhält den Text des Codes in dem Moment, in dem sie ihn bestätigt.",
  "intents_h": "Die Intents",
  "th": [
   "Action",
   "Filter im Manifest",
   "Was passiert",
   "Ergebnis"
  ],
  "rows": [
   [
    "<code>com.google.zxing.client.android.SCAN</code>",
    "Ja, implizite Intents funktionieren.",
    "Öffnet den Scanner. Der erste Code, den die Person erfasst, wird zurückgegeben, so wie es der ZXing Barcode Scanner tat.",
    "<code>RESULT_OK</code> mit <code>SCAN_RESULT</code> und <code>SCAN_RESULT_FORMAT</code>"
   ],
   [
    "<code>app.scanner.action.SCAN</code>",
    "Ja.",
    "Öffnet den Scanner. Für ein Ergebnis gestartet (ein Result-Launcher oder <code>startActivityForResult</code>) gibt er den Code auf demselben Weg zurück; einfach gestartet öffnet er nur die App auf dem Scanner.",
    "<code>RESULT_OK</code> mit den beiden Extras, wenn für ein Ergebnis gestartet"
   ],
   [
    "<code>app.scanner.action.CARD</code>",
    "Kein Filter: nur ein expliziter Intent mit dem Paket <code>com.verdettoqr.scanner</code>.",
    "Öffnet den Editor der eigenen Kontaktkarte der Person, den Code, den sie zum Teilen ihrer Daten zeigt. Gedacht für die Widgets und Verknüpfungen der App selbst; eine andere App darf ihn aufrufen, aber es kommt nichts zurück.",
    "Keins"
   ],
   [
    "<code>android.intent.action.SEND</code> mit <code>image/*</code>",
    "Ja.",
    "Decodiert ein Bild: Die App zeigt das Ergebnisblatt für die Codes darin.",
    "Keins"
   ]
  ],
  "p_handback": "Die Person kann die Rückgabe in den Einstellungen unter „Ergebnisse an andere Apps übergeben“ („Wenn eine App einen Scan anfordert, geht der Code an sie zurück“) abschalten; sie ist standardmäßig an. Ist sie aus, öffnet jede Scan-Action den Scanner wie einen normalen Start, und dein Launcher erhält <code>RESULT_CANCELED</code>, wenn die Person ihn verlässt. Zurück aus dem Scanner ist ebenfalls <code>RESULT_CANCELED</code>.",
  "p_extras": "Derzeit werden keine Request-Extras gelesen: weder <code>SCAN_MODE</code>, <code>SCAN_FORMATS</code>, <code>PROMPT_MESSAGE</code>, <code>SAVE_HISTORY</code> noch andere. Der Scanner liest bei jedem Aufruf jede Symbologie, die er kennt. Ein Code, den die Prüfungen der App markieren, wird trotzdem zurückgegeben; die Person sieht zuerst die Warnung und entscheidet.",
  "result_h": "Das Ergebnis",
  "li_text": "<code>SCAN_RESULT</code> (String): der Inhalt des Codes, genau die Bytes, die der Code trug, als Text decodiert (UTF-8, wo die Symbologie es erlaubt, sonst der eigene Zeichensatz der Symbologie).",
  "li_format": "<code>SCAN_RESULT_FORMAT</code> (String): die Symbologie in Großbuchstaben mit Unterstrichen, die ZXing-Namen, wo es sie gibt. Derzeit geliefert: {formats}, und die weiteren Symbologien, die die eigenen Decoder der App hinzufügen, in derselben Schreibweise (der Name auf dem Ergebnisblatt, großgeschrieben, Leerzeichen und Bindestriche als Unterstriche).",
  "p_nothing": "Sonst reist nichts mit: kein Bild, kein Standort, keine Historie.",
  "p_query": "Ab Android 11 nimm die Query in dein Manifest auf, damit <code>resolveActivity</code> die App sehen kann:",
  "zxing_h": "Die ZXing-Action",
  "zxing_p": "Code, der für den ZXing Barcode Scanner geschrieben wurde, funktioniert weiter: Sende <code>com.google.zxing.client.android.SCAN</code> auf demselben Weg und lies dieselben zwei Extras. Antworten mehrere Scanner auf dem Telefon darauf, fragt das System die Person, welchen sie nutzen möchte; den Intent an das Paket <code>com.verdettoqr.scanner</code> zu senden, überspringt das.",
  "sees_h": "Was die Person sieht",
  "sees_p": "Der Scanner öffnet sich wie immer, mit seinen eigenen Prüfungen. Rastet ein Code ein, gibt die App ihn zurück und schließt sich; nichts von dir erscheint auf dem Bildschirm, und nichts von der Person (Historie, Einstellungen, Sicherheitsliste) wird durch den Aufruf berührt.",
  "card_lead": "Testen auf einem Telefon ohne die App.",
  "card": "Die Store-Seite, dieselbe Adresse, die der Fallback in den Beispielen öffnet: <a href=\"{play}\">Bei Google Play holen</a>. Die Quelle dieser Seite ist die INTENT.md der App selbst; weichen beide voneinander ab, hat das App-Repository recht und diese Seite hinkt hinterher."
 },
 "es": {
  "title": "Para desarrolladores",
  "desc": "Cómo otra app de Android abre Verdetto para escanear y recibe el código: los intents, los extras del resultado, Kotlin y Java, y lo que ve la persona.",
  "h1": "Escanear desde otra app",
  "meta": "Verdetto responde a tres intents y a un envío compartido. Nada de esto necesita un permiso, una biblioteca ni una clave. La persona conserva todas las comprobaciones de seguridad y todos los ajustes de la app; tu app recibe el texto del código en el momento en que ella lo confirma.",
  "intents_h": "Los intents",
  "th": [
   "Acción",
   "Filtro en el manifiesto",
   "Qué ocurre",
   "Resultado"
  ],
  "rows": [
   [
    "<code>com.google.zxing.client.android.SCAN</code>",
    "Sí, los intents implícitos funcionan.",
    "Abre el escáner. El primer código que la persona fija se devuelve, como lo hacía el ZXing Barcode Scanner.",
    "<code>RESULT_OK</code> con <code>SCAN_RESULT</code> y <code>SCAN_RESULT_FORMAT</code>"
   ],
   [
    "<code>app.scanner.action.SCAN</code>",
    "Sí.",
    "Abre el escáner. Iniciado para obtener un resultado (un result launcher o <code>startActivityForResult</code>) devuelve el código de la misma manera; iniciado sin más, solo abre la app en el escáner.",
    "<code>RESULT_OK</code> con los dos extras cuando se inicia para obtener un resultado"
   ],
   [
    "<code>app.scanner.action.CARD</code>",
    "Sin filtro: solo un intent explícito con el paquete <code>com.verdettoqr.scanner</code>.",
    "Abre el editor de la tarjeta de contacto de la persona, el código que muestra para compartir sus datos. Pensado para los widgets y accesos directos de la propia app; otra app puede llamarlo, pero no devuelve nada.",
    "Ninguno"
   ],
   [
    "<code>android.intent.action.SEND</code> con <code>image/*</code>",
    "Sí.",
    "Decodifica una imagen: la app muestra la hoja de resultados con los códigos que contiene.",
    "Ninguno"
   ]
  ],
  "p_handback": "La persona puede desactivar la devolución en Ajustes, en «Entregar resultados a otras apps» («Cuando una app pide un escaneo, el código vuelve a esa app»), que está activada por defecto. Desactivada, cualquiera de las dos acciones de escaneo abre el escáner como un inicio normal y tu launcher recibe <code>RESULT_CANCELED</code> cuando la persona sale. Volver atrás desde el escáner también es <code>RESULT_CANCELED</code>.",
  "p_extras": "Hoy no se lee ningún extra de la petición: ni <code>SCAN_MODE</code>, <code>SCAN_FORMATS</code>, <code>PROMPT_MESSAGE</code>, <code>SAVE_HISTORY</code> ni ningún otro. El escáner lee todas las simbologías que conoce en cada llamada. Un código que las comprobaciones de la app señalan se devuelve de todos modos; la persona ve primero el aviso y decide.",
  "result_h": "El resultado",
  "li_text": "<code>SCAN_RESULT</code> (String): el contenido del código, exactamente los bytes que llevaba el código, decodificados como texto (UTF-8 donde la simbología lo permite, y si no, el juego de caracteres propio de la simbología).",
  "li_format": "<code>SCAN_RESULT_FORMAT</code> (String): la simbología en mayúsculas con guiones bajos, con los nombres de ZXing donde existen. Se entregan hoy: {formats}, y las demás simbologías que añaden los decodificadores propios de la app, con la misma grafía (el nombre que muestra la hoja de resultados, en mayúsculas, con espacios y guiones como guiones bajos).",
  "p_nothing": "Nada más viaja: ni imagen, ni ubicación, ni historial.",
  "p_query": "En Android 11 y posteriores, añade la consulta a tu manifiesto para que <code>resolveActivity</code> pueda ver la app:",
  "zxing_h": "La acción de ZXing",
  "zxing_p": "El código escrito para el ZXing Barcode Scanner sigue funcionando: envía <code>com.google.zxing.client.android.SCAN</code> de la misma manera y lee los mismos dos extras. Si más de un escáner del teléfono responde, el sistema pregunta a la persona cuál usar; enviar el intent al paquete <code>com.verdettoqr.scanner</code> se lo ahorra.",
  "sees_h": "Lo que ve la persona",
  "sees_p": "El escáner se abre como siempre, con sus propias comprobaciones. Cuando un código se fija, la app lo devuelve y se cierra; nada tuyo aparece en la pantalla, y nada suyo (historial, ajustes, lista de seguridad) se toca con la llamada.",
  "card_lead": "Probar en un teléfono sin la app.",
  "card": "La página de la tienda, la misma dirección que abre el fallback de los ejemplos: <a href=\"{play}\">Descárgala en Google Play</a>. La fuente de esta página es el INTENT.md de la propia app; cuando los dos difieren, el repositorio de la app tiene razón y esta página va por detrás."
 },
 "fr": {
  "title": "Pour les développeurs",
  "desc": "Comment une autre app Android ouvre Verdetto pour scanner et récupère le code : intents, extras du résultat, Kotlin et Java, et ce que voit la personne.",
  "h1": "Scanner depuis une autre application",
  "meta": "Verdetto répond à trois intents et à un partage. Rien ici ne demande une permission, une bibliothèque ou une clé. La personne garde chaque vérification de sécurité et chaque réglage de l'application ; votre application reçoit le texte du code à l'instant où elle le confirme.",
  "intents_h": "Les intents",
  "th": [
   "Action",
   "Filtre dans le manifeste",
   "Ce qui se passe",
   "Résultat"
  ],
  "rows": [
   [
    "<code>com.google.zxing.client.android.SCAN</code>",
    "Oui, les intents implicites fonctionnent.",
    "Ouvre le scanner. Le premier code que la personne verrouille est renvoyé, comme le faisait le ZXing Barcode Scanner.",
    "<code>RESULT_OK</code> avec <code>SCAN_RESULT</code> et <code>SCAN_RESULT_FORMAT</code>"
   ],
   [
    "<code>app.scanner.action.SCAN</code>",
    "Oui.",
    "Ouvre le scanner. Lancé pour un résultat (un result launcher ou <code>startActivityForResult</code>), il renvoie le code de la même façon ; lancé simplement, il ouvre juste l'application sur le scanner.",
    "<code>RESULT_OK</code> avec les deux extras quand il est lancé pour un résultat"
   ],
   [
    "<code>app.scanner.action.CARD</code>",
    "Pas de filtre : un intent explicite avec le paquet <code>com.verdettoqr.scanner</code> seulement.",
    "Ouvre l'éditeur de la carte de contact de la personne, le code qu'elle montre pour partager ses coordonnées. Prévu pour les widgets et raccourcis de l'application elle-même ; une autre application peut l'appeler, mais rien ne revient.",
    "Aucun"
   ],
   [
    "<code>android.intent.action.SEND</code> avec <code>image/*</code>",
    "Oui.",
    "Décode une image : l'application affiche la feuille de résultat pour les codes qu'elle contient.",
    "Aucun"
   ]
  ],
  "p_handback": "La personne peut désactiver le renvoi dans les Réglages, sous « Transmettre les résultats à d'autres applications » (« Quand une application demande un scan, le code lui est renvoyé »), activé par défaut. Désactivé, chacune des deux actions de scan ouvre le scanner comme un lancement normal et votre launcher reçoit <code>RESULT_CANCELED</code> quand la personne quitte. Le retour depuis le scanner donne aussi <code>RESULT_CANCELED</code>.",
  "p_extras": "Aucun extra de requête n'est lu aujourd'hui : ni <code>SCAN_MODE</code>, <code>SCAN_FORMATS</code>, <code>PROMPT_MESSAGE</code>, <code>SAVE_HISTORY</code>, ni aucun autre. Le scanner lit toutes les symbologies qu'il connaît à chaque appel. Un code signalé par les vérifications de l'application est quand même renvoyé ; la personne voit d'abord l'alerte et décide.",
  "result_h": "Le résultat",
  "li_text": "<code>SCAN_RESULT</code> (String) : le contenu du code, exactement les octets qu'il portait, décodés en texte (UTF-8 quand la symbologie le permet, sinon le jeu de caractères propre à la symbologie).",
  "li_format": "<code>SCAN_RESULT_FORMAT</code> (String) : la symbologie en majuscules avec des tirets bas, avec les noms ZXing quand ils existent. Livrés aujourd'hui : {formats}, et les autres symbologies qu'ajoutent les décodeurs propres à l'application, dans la même graphie (le nom affiché sur la feuille de résultat, en majuscules, espaces et traits d'union en tirets bas).",
  "p_nothing": "Rien d'autre ne voyage : ni image, ni position, ni historique.",
  "p_query": "Sur Android 11 et suivants, ajoutez la requête à votre manifeste pour que <code>resolveActivity</code> puisse voir l'application :",
  "zxing_h": "L'action ZXing",
  "zxing_p": "Le code écrit pour le ZXing Barcode Scanner continue de fonctionner : envoyez <code>com.google.zxing.client.android.SCAN</code> de la même façon et lisez les deux mêmes extras. Si plusieurs scanners du téléphone y répondent, le système demande à la personne lequel utiliser ; envoyer l'intent au paquet <code>com.verdettoqr.scanner</code> évite cette étape.",
  "sees_h": "Ce que voit la personne",
  "sees_p": "Le scanner s'ouvre comme toujours, avec ses propres vérifications. Quand un code se verrouille, l'application le renvoie et se ferme ; rien de vous n'apparaît à l'écran, et rien d'elle (historique, réglages, liste de sécurité) n'est touché par l'appel.",
  "card_lead": "Tester sur un téléphone sans l'application.",
  "card": "La page du magasin, la même adresse que le repli des exemples ouvre : <a href=\"{play}\">Disponible sur Google Play</a>. La source de cette page est le fichier INTENT.md de l'application ; quand les deux divergent, le dépôt de l'application a raison et cette page est en retard."
 },
 "pt-BR": {
  "title": "Para desenvolvedores",
  "desc": "Como outro app Android abre o Verdetto para escanear e recebe o código de volta: os intents, os extras do resultado, Kotlin e Java, e o que a pessoa vê.",
  "h1": "Escanear a partir de outro app",
  "meta": "O Verdetto responde a três intents e a um compartilhamento. Nada aqui precisa de permissão, biblioteca ou chave. A pessoa mantém todas as verificações de segurança e todas as configurações do app; seu app recebe o texto do código no momento em que ela o confirma.",
  "intents_h": "Os intents",
  "th": [
   "Ação",
   "Filtro no manifesto",
   "O que acontece",
   "Resultado"
  ],
  "rows": [
   [
    "<code>com.google.zxing.client.android.SCAN</code>",
    "Sim, intents implícitos funcionam.",
    "Abre o leitor. O primeiro código que a pessoa fixa é devolvido, como o ZXing Barcode Scanner fazia.",
    "<code>RESULT_OK</code> com <code>SCAN_RESULT</code> e <code>SCAN_RESULT_FORMAT</code>"
   ],
   [
    "<code>app.scanner.action.SCAN</code>",
    "Sim.",
    "Abre o leitor. Iniciado para um resultado (um result launcher ou <code>startActivityForResult</code>), devolve o código do mesmo jeito; iniciado sem mais, só abre o app no leitor.",
    "<code>RESULT_OK</code> com os dois extras quando iniciado para um resultado"
   ],
   [
    "<code>app.scanner.action.CARD</code>",
    "Sem filtro: apenas um intent explícito com o pacote <code>com.verdettoqr.scanner</code>.",
    "Abre o editor do cartão de contato da própria pessoa, o código que ela mostra para compartilhar seus dados. Feito para os widgets e atalhos do próprio app; outro app pode chamá-lo, mas nada volta.",
    "Nenhum"
   ],
   [
    "<code>android.intent.action.SEND</code> com <code>image/*</code>",
    "Sim.",
    "Decodifica uma imagem: o app mostra a folha de resultado com os códigos que ela contém.",
    "Nenhum"
   ]
  ],
  "p_handback": "A pessoa pode desligar a devolução em Configurações, em \"Entregar resultados a outros apps\" (\"Quando um app pede um escaneamento, o código volta para ele\"), que vem ligada. Desligada, qualquer das duas ações de leitura abre o leitor como uma abertura normal e seu launcher recebe <code>RESULT_CANCELED</code> quando a pessoa sai. Voltar do leitor também é <code>RESULT_CANCELED</code>.",
  "p_extras": "Nenhum extra da requisição é lido hoje: nem <code>SCAN_MODE</code>, <code>SCAN_FORMATS</code>, <code>PROMPT_MESSAGE</code>, <code>SAVE_HISTORY</code>, nem qualquer outro. O leitor lê todas as simbologias que conhece em toda chamada. Um código que as verificações do app sinalizam ainda é devolvido; a pessoa vê o alerta primeiro e decide.",
  "result_h": "O resultado",
  "li_text": "<code>SCAN_RESULT</code> (String): o conteúdo do código, exatamente os bytes que ele carregava, decodificados como texto (UTF-8 onde a simbologia permite, e o conjunto de caracteres da própria simbologia nos outros casos).",
  "li_format": "<code>SCAN_RESULT_FORMAT</code> (String): a simbologia em maiúsculas com sublinhados, com os nomes do ZXing onde existem. Entregues hoje: {formats}, e as outras simbologias que os decodificadores próprios do app acrescentam, na mesma grafia (o nome mostrado na folha de resultado, em maiúsculas, com espaços e hifens como sublinhados).",
  "p_nothing": "Nada mais viaja: nenhuma imagem, nenhuma localização, nenhum histórico.",
  "p_query": "No Android 11 e posteriores, adicione a consulta ao seu manifesto para que <code>resolveActivity</code> consiga ver o app:",
  "zxing_h": "A ação do ZXing",
  "zxing_p": "Código escrito para o ZXing Barcode Scanner continua funcionando: envie <code>com.google.zxing.client.android.SCAN</code> do mesmo jeito e leia os mesmos dois extras. Se mais de um leitor no celular responder, o sistema pergunta à pessoa qual usar; enviar o intent para o pacote <code>com.verdettoqr.scanner</code> pula isso.",
  "sees_h": "O que a pessoa vê",
  "sees_p": "O leitor abre como sempre, com suas próprias verificações. Quando um código é fixado, o app o devolve e fecha; nada seu aparece na tela, e nada dela (histórico, configurações, lista de segurança) é tocado pela chamada.",
  "card_lead": "Testar em um celular sem o app.",
  "card": "A página da loja, o mesmo endereço que o fallback dos exemplos abre: <a href=\"{play}\">Disponível no Google Play</a>. A fonte desta página é o INTENT.md do próprio app; quando os dois divergem, o repositório do app está certo e esta página está atrasada."
 },
 "id": {
  "title": "Untuk pengembang",
  "desc": "Cara aplikasi Android lain membuka Verdetto untuk memindai dan menerima kodenya kembali: intent, ekstra hasil, Kotlin dan Java, serta apa yang dilihat pengguna.",
  "h1": "Memindai dari aplikasi lain",
  "meta": "Verdetto menjawab tiga intent dan satu berbagi. Tidak ada yang memerlukan izin, pustaka, atau kunci. Orang itu tetap mendapat setiap pemeriksaan keamanan dan setiap pengaturan aplikasi; aplikasi Anda menerima teks kode pada saat ia mengonfirmasinya.",
  "intents_h": "Intent-nya",
  "th": [
   "Action",
   "Filter di manifes",
   "Yang terjadi",
   "Hasil"
  ],
  "rows": [
   [
    "<code>com.google.zxing.client.android.SCAN</code>",
    "Ya, intent implisit berfungsi.",
    "Membuka pemindai. Kode pertama yang dikunci orang itu dikembalikan, seperti yang dilakukan ZXing Barcode Scanner.",
    "<code>RESULT_OK</code> dengan <code>SCAN_RESULT</code> dan <code>SCAN_RESULT_FORMAT</code>"
   ],
   [
    "<code>app.scanner.action.SCAN</code>",
    "Ya.",
    "Membuka pemindai. Dimulai untuk hasil (result launcher atau <code>startActivityForResult</code>) ia mengembalikan kode dengan cara yang sama; dimulai biasa, ia hanya membuka aplikasi di pemindai.",
    "<code>RESULT_OK</code> dengan dua ekstra itu bila dimulai untuk hasil"
   ],
   [
    "<code>app.scanner.action.CARD</code>",
    "Tanpa filter: hanya intent eksplisit dengan paket <code>com.verdettoqr.scanner</code>.",
    "Membuka editor kartu kontak milik orang itu, kode yang ia tunjukkan untuk berbagi datanya. Dimaksudkan untuk widget dan pintasan aplikasi sendiri; aplikasi lain boleh memanggilnya, tetapi tidak ada yang kembali.",
    "Tidak ada"
   ],
   [
    "<code>android.intent.action.SEND</code> dengan <code>image/*</code>",
    "Ya.",
    "Mendekode gambar: aplikasi menampilkan lembar hasil untuk kode di dalamnya.",
    "Tidak ada"
   ]
  ],
  "p_handback": "Orang itu bisa mematikan pengembalian hasil di Pengaturan pada \"Serahkan hasil ke aplikasi lain\" (\"Saat aplikasi meminta pindaian, kodenya dikembalikan ke aplikasi itu\"), yang aktif secara bawaan. Bila dimatikan, kedua action pindai membuka pemindai sebagai peluncuran biasa dan launcher Anda menerima <code>RESULT_CANCELED</code> saat orang itu keluar. Kembali dari pemindai juga <code>RESULT_CANCELED</code>.",
  "p_extras": "Saat ini tidak ada ekstra permintaan yang dibaca: bukan <code>SCAN_MODE</code>, <code>SCAN_FORMATS</code>, <code>PROMPT_MESSAGE</code>, <code>SAVE_HISTORY</code>, atau yang lain. Pemindai membaca setiap simbologi yang dikenalnya pada setiap panggilan. Kode yang ditandai pemeriksaan aplikasi tetap dikembalikan; orang itu melihat peringatannya dulu dan memutuskan.",
  "result_h": "Hasilnya",
  "li_text": "<code>SCAN_RESULT</code> (String): isi kode, persis byte yang dibawa kode, didekode sebagai teks (UTF-8 bila simbologinya mengizinkan, selain itu set karakter simbologi itu sendiri).",
  "li_format": "<code>SCAN_RESULT_FORMAT</code> (String): simbologi dalam huruf besar dengan garis bawah, memakai nama ZXing bila ada. Dikirim saat ini: {formats}, dan simbologi lain yang ditambahkan dekoder aplikasi sendiri, dengan ejaan yang sama (nama yang tampil di lembar hasil, dihurufbesarkan, spasi dan tanda hubung menjadi garis bawah).",
  "p_nothing": "Tidak ada yang lain ikut: tidak ada gambar, lokasi, atau riwayat.",
  "p_query": "Pada Android 11 ke atas, tambahkan query ke manifes Anda agar <code>resolveActivity</code> bisa melihat aplikasinya:",
  "zxing_h": "Action ZXing",
  "zxing_p": "Kode yang ditulis untuk ZXing Barcode Scanner tetap berfungsi: kirim <code>com.google.zxing.client.android.SCAN</code> dengan cara yang sama dan baca dua ekstra yang sama. Jika lebih dari satu pemindai di ponsel menjawabnya, sistem menanyakan kepada orang itu mana yang dipakai; mengirim intent ke paket <code>com.verdettoqr.scanner</code> melewati langkah itu.",
  "sees_h": "Yang dilihat pengguna",
  "sees_p": "Pemindai terbuka seperti biasa, dengan pemeriksaannya sendiri. Saat kode terkunci, aplikasi mengembalikannya dan menutup; tidak ada milik Anda yang muncul di layar, dan tidak ada milik orang itu (riwayat, pengaturan, daftar keamanan) yang tersentuh panggilan tersebut.",
  "card_lead": "Menguji di ponsel tanpa aplikasi.",
  "card": "Halaman toko, alamat yang sama yang dibuka fallback dalam contoh: <a href=\"{play}\">Dapatkan di Google Play</a>. Sumber halaman ini adalah INTENT.md aplikasi sendiri; bila keduanya berbeda, repositori aplikasi yang benar dan halaman ini yang tertinggal."
 },
 "ru": {
  "title": "Разработчикам",
  "desc": "Как другое Android-приложение открывает Verdetto для сканирования и получает код обратно: интенты, экстры результата, Kotlin и Java, и что видит человек.",
  "h1": "Сканирование из другого приложения",
  "meta": "Verdetto отвечает на три интента и одно действие «Поделиться». Ничему из этого не нужны разрешение, библиотека или ключ. Человек сохраняет все проверки безопасности и все настройки приложения; ваше приложение получает текст кода в момент, когда он его подтверждает.",
  "intents_h": "Интенты",
  "th": [
   "Action",
   "Фильтр в манифесте",
   "Что происходит",
   "Результат"
  ],
  "rows": [
   [
    "<code>com.google.zxing.client.android.SCAN</code>",
    "Да, неявные интенты работают.",
    "Открывает сканер. Первый код, который человек фиксирует, возвращается, как это делал ZXing Barcode Scanner.",
    "<code>RESULT_OK</code> с <code>SCAN_RESULT</code> и <code>SCAN_RESULT_FORMAT</code>"
   ],
   [
    "<code>app.scanner.action.SCAN</code>",
    "Да.",
    "Открывает сканер. Запущенный ради результата (result launcher или <code>startActivityForResult</code>), он возвращает код тем же способом; запущенный просто так, он лишь открывает приложение на сканере.",
    "<code>RESULT_OK</code> с двумя экстрами, если запущен ради результата"
   ],
   [
    "<code>app.scanner.action.CARD</code>",
    "Без фильтра: только явный интент с пакетом <code>com.verdettoqr.scanner</code>.",
    "Открывает редактор собственной контактной карточки человека, кода, который он показывает, чтобы поделиться данными. Предназначен для виджетов и ярлыков самого приложения; другое приложение может его вызвать, но назад ничего не приходит.",
    "Нет"
   ],
   [
    "<code>android.intent.action.SEND</code> с <code>image/*</code>",
    "Да.",
    "Декодирует изображение: приложение показывает лист результата для кодов в нём.",
    "Нет"
   ]
  ],
  "p_handback": "Человек может отключить возврат в Настройках, пункт «Передавать результаты другим приложениям» («Когда приложение запрашивает сканирование, код возвращается ему»), включённый по умолчанию. Если он выключен, любое из двух действий сканирования открывает сканер как обычный запуск, и ваш launcher получает <code>RESULT_CANCELED</code>, когда человек выходит. Возврат назад из сканера — тоже <code>RESULT_CANCELED</code>.",
  "p_extras": "Экстры запроса сейчас не читаются: ни <code>SCAN_MODE</code>, <code>SCAN_FORMATS</code>, <code>PROMPT_MESSAGE</code>, <code>SAVE_HISTORY</code>, ни какие-либо другие. Сканер читает все известные ему символики при каждом вызове. Код, который отметили проверки приложения, всё равно возвращается; человек сначала видит предупреждение и решает.",
  "result_h": "Результат",
  "li_text": "<code>SCAN_RESULT</code> (String): содержимое кода, ровно те байты, которые нёс код, декодированные как текст (UTF-8, где символика это позволяет, иначе собственный набор символов символики).",
  "li_format": "<code>SCAN_RESULT_FORMAT</code> (String): символика в верхнем регистре с подчёркиваниями, имена ZXing там, где они есть. Сейчас передаются: {formats}, и остальные символики, которые добавляют собственные декодеры приложения, в том же написании (имя, показанное на листе результата, в верхнем регистре, пробелы и дефисы как подчёркивания).",
  "p_nothing": "Больше ничего не передаётся: ни изображение, ни местоположение, ни история.",
  "p_query": "На Android 11 и новее добавьте запрос в манифест, чтобы <code>resolveActivity</code> мог увидеть приложение:",
  "zxing_h": "Действие ZXing",
  "zxing_p": "Код, написанный для ZXing Barcode Scanner, продолжает работать: отправьте <code>com.google.zxing.client.android.SCAN</code> тем же способом и читайте те же два экстра. Если на телефоне на него отвечают несколько сканеров, система спрашивает человека, какой использовать; отправка интента пакету <code>com.verdettoqr.scanner</code> пропускает это.",
  "sees_h": "Что видит человек",
  "sees_p": "Сканер открывается как всегда, со своими проверками. Когда код фиксируется, приложение возвращает его и закрывается; ничего вашего на экране не появляется, и ничего его (история, настройки, список безопасности) вызов не затрагивает.",
  "card_lead": "Проверка на телефоне без приложения.",
  "card": "Страница магазина, тот же адрес, который открывает запасной вариант в примерах: <a href=\"{play}\">Скачать в Google Play</a>. Источник этой страницы — собственный INTENT.md приложения; если они расходятся, прав репозиторий приложения, а эта страница отстаёт."
 },
 "hi": {
  "title": "डेवलपरों के लिए",
  "desc": "दूसरा Android ऐप स्कैन करने के लिए Verdetto को कैसे खोलता है और कोड वापस कैसे पाता है: इंटेंट, परिणाम के एक्स्ट्रा, Kotlin और Java, और व्यक्ति क्या देखता है।",
  "h1": "दूसरे ऐप से स्कैन करना",
  "meta": "Verdetto तीन इंटेंट और एक शेयर का जवाब देता है। यहाँ किसी चीज़ को अनुमति, लाइब्रेरी या कुंजी की ज़रूरत नहीं। व्यक्ति के पास ऐप की हर सुरक्षा जाँच और हर सेटिंग बनी रहती है; आपके ऐप को कोड का टेक्स्ट उसी क्षण मिलता है जब वह उसकी पुष्टि करता है।",
  "intents_h": "इंटेंट",
  "th": [
   "Action",
   "मैनिफ़ेस्ट में फ़िल्टर",
   "क्या होता है",
   "परिणाम"
  ],
  "rows": [
   [
    "<code>com.google.zxing.client.android.SCAN</code>",
    "हाँ, इम्प्लिसिट इंटेंट काम करते हैं।",
    "स्कैनर खोलता है। व्यक्ति जो पहला कोड लॉक करता है वह वापस दिया जाता है, जैसा ZXing Barcode Scanner करता था।",
    "<code>RESULT_OK</code> के साथ <code>SCAN_RESULT</code> और <code>SCAN_RESULT_FORMAT</code>"
   ],
   [
    "<code>app.scanner.action.SCAN</code>",
    "हाँ।",
    "स्कैनर खोलता है। परिणाम के लिए शुरू किया गया (result launcher या <code>startActivityForResult</code>) तो कोड उसी तरह वापस देता है; सादे तौर पर शुरू किया गया तो बस ऐप को स्कैनर पर खोलता है।",
    "परिणाम के लिए शुरू होने पर दोनों एक्स्ट्रा के साथ <code>RESULT_OK</code>"
   ],
   [
    "<code>app.scanner.action.CARD</code>",
    "कोई फ़िल्टर नहीं: केवल पैकेज <code>com.verdettoqr.scanner</code> के साथ एक्सप्लिसिट इंटेंट।",
    "व्यक्ति के अपने संपर्क कार्ड का एडिटर खोलता है, वह कोड जो वह अपनी जानकारी साझा करने के लिए दिखाता है। ऐप के अपने विजेट और शॉर्टकट के लिए बना है; कोई दूसरा ऐप इसे कॉल कर सकता है, पर कुछ वापस नहीं आता।",
    "कुछ नहीं"
   ],
   [
    "<code>android.intent.action.SEND</code> के साथ <code>image/*</code>",
    "हाँ।",
    "एक चित्र को डिकोड करता है: ऐप उसमें मौजूद कोड के लिए परिणाम शीट दिखाता है।",
    "कुछ नहीं"
   ]
  ],
  "p_handback": "व्यक्ति सेटिंग में \"परिणाम दूसरे ऐप को सौंपें\" (\"जब कोई ऐप स्कैन माँगता है, तो कोड उसे वापस जाता है\") के तहत वापसी बंद कर सकता है, जो डिफ़ॉल्ट रूप से चालू है। बंद होने पर दोनों में से कोई भी स्कैन action स्कैनर को सामान्य लॉन्च की तरह खोलता है और व्यक्ति के बाहर निकलने पर आपके launcher को <code>RESULT_CANCELED</code> मिलता है। स्कैनर से पीछे जाना भी <code>RESULT_CANCELED</code> है।",
  "p_extras": "आज कोई अनुरोध एक्स्ट्रा नहीं पढ़ा जाता: न <code>SCAN_MODE</code>, <code>SCAN_FORMATS</code>, <code>PROMPT_MESSAGE</code>, <code>SAVE_HISTORY</code>, न कोई और। स्कैनर हर कॉल पर अपनी जानी हुई हर सिंबोलॉजी पढ़ता है। जिस कोड को ऐप की जाँचें चिह्नित करती हैं वह भी वापस दिया जाता है; व्यक्ति पहले चेतावनी देखता है और फ़ैसला करता है।",
  "result_h": "परिणाम",
  "li_text": "<code>SCAN_RESULT</code> (String): कोड की सामग्री, ठीक वही बाइट जो कोड में थे, टेक्स्ट के रूप में डिकोड किए गए (जहाँ सिंबोलॉजी अनुमति देती है वहाँ UTF-8, अन्यथा सिंबोलॉजी का अपना कैरेक्टर सेट)।",
  "li_format": "<code>SCAN_RESULT_FORMAT</code> (String): सिंबोलॉजी बड़े अक्षरों में अंडरस्कोर के साथ, जहाँ मौजूद हों वहाँ ZXing के नाम। आज दिए जाते हैं: {formats}, और वे अन्य सिंबोलॉजी जो ऐप के अपने डिकोडर जोड़ते हैं, उसी वर्तनी में (परिणाम शीट पर दिखने वाला नाम, बड़े अक्षरों में, स्पेस और हाइफ़न अंडरस्कोर के रूप में)।",
  "p_nothing": "और कुछ नहीं जाता: न चित्र, न स्थान, न इतिहास।",
  "p_query": "Android 11 और बाद के संस्करणों पर, अपने मैनिफ़ेस्ट में क्वेरी जोड़ें ताकि <code>resolveActivity</code> ऐप को देख सके:",
  "zxing_h": "ZXing action",
  "zxing_p": "ZXing Barcode Scanner के लिए लिखा गया कोड काम करता रहता है: <code>com.google.zxing.client.android.SCAN</code> उसी तरह भेजें और वही दो एक्स्ट्रा पढ़ें। अगर फ़ोन पर एक से ज़्यादा स्कैनर इसका जवाब देते हैं, तो सिस्टम व्यक्ति से पूछता है कि कौन सा इस्तेमाल करना है; इंटेंट को पैकेज <code>com.verdettoqr.scanner</code> पर भेजने से यह चरण छूट जाता है।",
  "sees_h": "व्यक्ति क्या देखता है",
  "sees_p": "स्कैनर हमेशा की तरह खुलता है, अपनी जाँचों के साथ। कोड लॉक होने पर ऐप उसे वापस देता है और बंद हो जाता है; स्क्रीन पर आपका कुछ नहीं दिखता, और उसका कुछ भी (इतिहास, सेटिंग, सुरक्षा सूची) इस कॉल से नहीं छुआ जाता।",
  "card_lead": "बिना ऐप वाले फ़ोन पर परीक्षण।",
  "card": "स्टोर पेज, वही पता जो उदाहरणों का फ़ॉलबैक खोलता है: <a href=\"{play}\">Google Play पर पाएँ</a>। इस पेज का स्रोत ऐप की अपनी INTENT.md है; दोनों में अंतर हो तो ऐप रिपॉज़िटरी सही है और यह पेज पीछे है।"
 },
 "ja": {
  "title": "開発者向け",
  "desc": "他の Android アプリが Verdetto を開いて読み取り、コードを受け取る方法: インテント、結果のエクストラ、Kotlin と Java、そして利用者に見えるもの。",
  "h1": "他のアプリから読み取る",
  "meta": "Verdetto は三つのインテントと一つの共有に応えます。権限もライブラリもキーも要りません。利用者はアプリのすべての安全確認と設定をそのまま保ち、あなたのアプリは利用者が確認した瞬間にコードのテキストを受け取ります。",
  "intents_h": "インテント",
  "th": [
   "Action",
   "マニフェストのフィルター",
   "何が起きるか",
   "結果"
  ],
  "rows": [
   [
    "<code>com.google.zxing.client.android.SCAN</code>",
    "はい。暗黙的インテントが使えます。",
    "スキャナーを開きます。利用者が最初にロックしたコードが、ZXing Barcode Scanner と同じように返されます。",
    "<code>RESULT_OK</code> と <code>SCAN_RESULT</code>、<code>SCAN_RESULT_FORMAT</code>"
   ],
   [
    "<code>app.scanner.action.SCAN</code>",
    "はい。",
    "スキャナーを開きます。結果を求めて起動した場合（result launcher または <code>startActivityForResult</code>）は同じ方法でコードを返し、そのまま起動した場合はアプリをスキャナー画面で開くだけです。",
    "結果を求めて起動した場合、二つのエクストラ付きの <code>RESULT_OK</code>"
   ],
   [
    "<code>app.scanner.action.CARD</code>",
    "フィルターなし: パッケージ <code>com.verdettoqr.scanner</code> を指定した明示的インテントのみ。",
    "利用者自身の連絡先カードの編集画面、つまり自分の連絡先を共有するために見せるコードを開きます。アプリ自身のウィジェットとショートカット向けで、他のアプリから呼べますが、何も返りません。",
    "なし"
   ],
   [
    "<code>android.intent.action.SEND</code> と <code>image/*</code>",
    "はい。",
    "画像を解読します。アプリはその中のコードについて結果シートを表示します。",
    "なし"
   ]
  ],
  "p_handback": "利用者は設定の「結果を他のアプリに渡す」（「アプリからスキャンを求められたとき、コードをそのアプリに返します」）で受け渡しをオフにできます（初期状態はオン）。オフのとき、どちらのスキャン action も通常起動としてスキャナーを開き、利用者が離れるとあなたのランチャーは <code>RESULT_CANCELED</code> を受け取ります。スキャナーからの戻る操作も <code>RESULT_CANCELED</code> です。",
  "p_extras": "現在、リクエストのエクストラは読みません。<code>SCAN_MODE</code>、<code>SCAN_FORMATS</code>、<code>PROMPT_MESSAGE</code>、<code>SAVE_HISTORY</code> もその他も同様です。スキャナーは呼び出しごとに知っているすべてのシンボロジーを読みます。アプリの確認が警告したコードもそのまま返されます。利用者が先に警告を見て判断します。",
  "result_h": "結果",
  "li_text": "<code>SCAN_RESULT</code>（String）: コードの内容。コードが運んでいたバイトそのものをテキストとして解読したもの（シンボロジーが許す場合は UTF-8、それ以外はそのシンボロジー固有の文字集合）。",
  "li_format": "<code>SCAN_RESULT_FORMAT</code>（String）: シンボロジーを大文字とアンダースコアで表したもの。ZXing の名前がある場合はそれを使います。現在返すもの: {formats}、およびアプリ独自のデコーダーが加えるその他のシンボロジーを同じ表記で（結果シートに表示される名前を大文字にし、スペースとハイフンをアンダースコアにしたもの）。",
  "p_nothing": "他には何も渡りません。画像も、位置情報も、履歴も。",
  "p_query": "Android 11 以降では、<code>resolveActivity</code> がアプリを見つけられるように、マニフェストにクエリを追加してください:",
  "zxing_h": "ZXing の action",
  "zxing_p": "ZXing Barcode Scanner 向けに書かれたコードはそのまま動きます。<code>com.google.zxing.client.android.SCAN</code> を同じ方法で送り、同じ二つのエクストラを読んでください。端末上の複数のスキャナーがこれに応える場合、システムがどれを使うか利用者に尋ねます。パッケージ <code>com.verdettoqr.scanner</code> にインテントを送ればその手順は省かれます。",
  "sees_h": "利用者に見えるもの",
  "sees_p": "スキャナーはいつも通り、自身の確認とともに開きます。コードがロックされるとアプリはそれを返して閉じます。あなたのものは画面に何も現れず、利用者のもの（履歴、設定、安全リスト）にこの呼び出しが触れることもありません。",
  "card_lead": "アプリのない端末での確認。",
  "card": "ストアページで、サンプルのフォールバックが開くのと同じアドレスです: <a href=\"{play}\">Google Play で手に入れよう</a>。このページの出典はアプリ自身の INTENT.md で、両者が異なる場合はアプリのリポジトリが正しく、このページが遅れています。"
 },
 "zh-Hans": {
  "title": "面向开发者",
  "desc": "另一个 Android 应用如何打开 Verdetto 进行扫描并取回码：意图、结果附加数据、Kotlin 与 Java，以及用户看到的内容。",
  "h1": "从另一个应用发起扫描",
  "meta": "Verdetto 响应三个意图和一个分享。这里不需要任何权限、库或密钥。用户保留应用的每一项安全检查和每一项设置；在用户确认的那一刻，你的应用就会收到码的文本。",
  "intents_h": "意图",
  "th": [
   "Action",
   "清单中的过滤器",
   "会发生什么",
   "结果"
  ],
  "rows": [
   [
    "<code>com.google.zxing.client.android.SCAN</code>",
    "是，隐式意图可用。",
    "打开扫描器。用户锁定的第一个码会被返回，与 ZXing Barcode Scanner 的做法相同。",
    "<code>RESULT_OK</code>，附带 <code>SCAN_RESULT</code> 和 <code>SCAN_RESULT_FORMAT</code>"
   ],
   [
    "<code>app.scanner.action.SCAN</code>",
    "是。",
    "打开扫描器。为获取结果而启动时（result launcher 或 <code>startActivityForResult</code>），以同样方式返回码；直接启动时只是在扫描器界面打开应用。",
    "为获取结果而启动时，<code>RESULT_OK</code> 附带这两个附加数据"
   ],
   [
    "<code>app.scanner.action.CARD</code>",
    "无过滤器：仅接受指定包名 <code>com.verdettoqr.scanner</code> 的显式意图。",
    "打开用户自己的联系人名片编辑器，也就是用户用来分享自己信息的码。面向应用自身的小组件和快捷方式；其他应用可以调用，但不会返回任何内容。",
    "无"
   ],
   [
    "<code>android.intent.action.SEND</code>，类型 <code>image/*</code>",
    "是。",
    "解码一张图片：应用为其中的码显示结果面板。",
    "无"
   ]
  ],
  "p_handback": "用户可以在“设置”中的“把结果交给其他应用”（“当其他应用请求扫描时，把码返回给该应用”）关闭返回功能，该项默认开启。关闭后，两个扫描 action 都会像普通启动一样打开扫描器，用户离开时你的 launcher 会收到 <code>RESULT_CANCELED</code>。从扫描器返回同样是 <code>RESULT_CANCELED</code>。",
  "p_extras": "目前不读取任何请求附加数据：<code>SCAN_MODE</code>、<code>SCAN_FORMATS</code>、<code>PROMPT_MESSAGE</code>、<code>SAVE_HISTORY</code> 或其他都不读取。扫描器在每次调用时读取它所知的所有码制。被应用检查标记的码仍会返回；用户先看到警告，再自行决定。",
  "result_h": "结果",
  "li_text": "<code>SCAN_RESULT</code>（String）：码的内容，即码所携带的原始字节，按文本解码（码制允许时为 UTF-8，否则为该码制自身的字符集）。",
  "li_format": "<code>SCAN_RESULT_FORMAT</code>（String）：码制名称，大写并以下划线连接，存在 ZXing 名称时沿用之。目前返回：{formats}，以及应用自有解码器新增的其他码制，拼写方式相同（结果面板上显示的名称转为大写，空格和连字符改为下划线）。",
  "p_nothing": "不会传递其他任何东西：没有图片、没有位置、没有历史记录。",
  "p_query": "在 Android 11 及更高版本上，把查询加入你的清单，这样 <code>resolveActivity</code> 才能看到该应用：",
  "zxing_h": "ZXing action",
  "zxing_p": "为 ZXing Barcode Scanner 编写的代码可以继续使用：以同样方式发送 <code>com.google.zxing.client.android.SCAN</code>，并读取同样的两个附加数据。如果手机上有多个扫描器响应它，系统会询问用户使用哪一个；把意图发送给包名 <code>com.verdettoqr.scanner</code> 可以跳过这一步。",
  "sees_h": "用户看到的内容",
  "sees_p": "扫描器照常打开，带着它自己的检查。码锁定后，应用把它返回并关闭；屏幕上不会出现任何属于你的内容，用户的任何内容（历史记录、设置、安全列表）也不会被这次调用触及。",
  "card_lead": "在没有安装应用的手机上测试。",
  "card": "商店页面，也就是示例中回退所打开的地址：<a href=\"{play}\">在 Google Play 获取</a>。本页面的来源是应用自身的 INTENT.md；两者不一致时，以应用仓库为准，本页面滞后。"
 },
 "ar": {
  "title": "للمطوّرين",
  "desc": "كيف يفتح تطبيق Android آخر Verdetto للمسح ويستلم الرمز: النوايا (intents)، وإضافات النتيجة، وKotlin وJava، وما يراه المستخدم.",
  "h1": "المسح من تطبيق آخر",
  "meta": "يستجيب Verdetto لثلاث نوايا ومشاركة واحدة. لا يحتاج شيء هنا إلى إذن أو مكتبة أو مفتاح. يحتفظ الشخص بكل فحص أمان وكل إعداد في التطبيق؛ ويستلم تطبيقك نص الرمز لحظة تأكيده.",
  "intents_h": "النوايا",
  "th": [
   "Action",
   "المرشِّح في الـ manifest",
   "ما الذي يحدث",
   "النتيجة"
  ],
  "rows": [
   [
    "<code>com.google.zxing.client.android.SCAN</code>",
    "نعم، النوايا الضمنية تعمل.",
    "يفتح الماسح. أول رمز يثبّته الشخص يُعاد، كما كان يفعل ZXing Barcode Scanner.",
    "<code>RESULT_OK</code> مع <code>SCAN_RESULT</code> و<code>SCAN_RESULT_FORMAT</code>"
   ],
   [
    "<code>app.scanner.action.SCAN</code>",
    "نعم.",
    "يفتح الماسح. إذا بُدئ من أجل نتيجة (result launcher أو <code>startActivityForResult</code>) فإنه يعيد الرمز بالطريقة نفسها؛ وإذا بُدئ عاديًا فإنه يفتح التطبيق على الماسح فقط.",
    "<code>RESULT_OK</code> مع الإضافتين عند البدء من أجل نتيجة"
   ],
   [
    "<code>app.scanner.action.CARD</code>",
    "بلا مرشِّح: نية صريحة بالحزمة <code>com.verdettoqr.scanner</code> فقط.",
    "يفتح محرّر بطاقة الاتصال الخاصة بالشخص، أي الرمز الذي يعرضه لمشاركة بياناته. مخصص لأدوات التطبيق واختصاراته؛ ويمكن لتطبيق آخر استدعاؤه، لكن لا يعود شيء.",
    "لا شيء"
   ],
   [
    "<code>android.intent.action.SEND</code> مع <code>image/*</code>",
    "نعم.",
    "يفكّ صورة: يعرض التطبيق ورقة النتيجة للرموز الموجودة فيها.",
    "لا شيء"
   ]
  ],
  "p_handback": "يمكن للشخص إيقاف إعادة النتائج في الإعدادات ضمن «تسليم النتائج إلى تطبيقات أخرى» («عندما يطلب تطبيق ما مسحًا، يعود الرمز إليه»)، وهو مفعّل افتراضيًا. وعند إيقافه، يفتح أيٌّ من إجراءي المسح الماسح كتشغيل عادي ويستلم مشغّلك <code>RESULT_CANCELED</code> عندما يخرج الشخص. والرجوع من الماسح يعطي <code>RESULT_CANCELED</code> أيضًا.",
  "p_extras": "لا تُقرأ حاليًا أي إضافات في الطلب: لا <code>SCAN_MODE</code> ولا <code>SCAN_FORMATS</code> ولا <code>PROMPT_MESSAGE</code> ولا <code>SAVE_HISTORY</code> ولا غيرها. يقرأ الماسح كل ترميز يعرفه في كل استدعاء. والرمز الذي تعلّمه فحوص التطبيق يُعاد مع ذلك؛ يرى الشخص التحذير أولًا ثم يقرر.",
  "result_h": "النتيجة",
  "li_text": "<code>SCAN_RESULT</code> (String): محتوى الرمز، أي البايتات التي حملها الرمز بالضبط، مفكوكة كنص (UTF-8 حيث يسمح الترميز، وإلا فمجموعة محارف الترميز نفسه).",
  "li_format": "<code>SCAN_RESULT_FORMAT</code> (String): الترميز بأحرف كبيرة مع شرطات سفلية، بأسماء ZXing حيث توجد. يُسلَّم حاليًا: {formats}، إلى جانب الترميزات الأخرى التي تضيفها مفكّكات التطبيق الخاصة، بالكتابة نفسها (الاسم المعروض في ورقة النتيجة بأحرف كبيرة، مع تحويل المسافات والشرطات إلى شرطات سفلية).",
  "p_nothing": "لا ينتقل شيء آخر: لا صورة ولا موقع ولا سجل.",
  "p_query": "على Android 11 وما بعده، أضف الاستعلام إلى الـ manifest كي يتمكن <code>resolveActivity</code> من رؤية التطبيق:",
  "zxing_h": "إجراء ZXing",
  "zxing_p": "الكود المكتوب لـ ZXing Barcode Scanner يستمر في العمل: أرسل <code>com.google.zxing.client.android.SCAN</code> بالطريقة نفسها واقرأ الإضافتين نفسيهما. وإذا استجاب له أكثر من ماسح على الهاتف، يسأل النظام الشخص أيّها يستخدم؛ وإرسال النية إلى الحزمة <code>com.verdettoqr.scanner</code> يتجاوز ذلك.",
  "sees_h": "ما يراه الشخص",
  "sees_p": "يفتح الماسح كالمعتاد، بفحوصه الخاصة. وعندما يثبت رمز، يعيده التطبيق ويُغلَق؛ لا يظهر شيء من عندك على الشاشة، ولا يمسّ الاستدعاء شيئًا من عند الشخص (السجل، الإعدادات، قائمة الأمان).",
  "card_lead": "الاختبار على هاتف بلا التطبيق.",
  "card": "صفحة المتجر، وهي العنوان نفسه الذي يفتحه البديل في الأمثلة: <a href=\"{play}\">احصل عليه من Google Play</a>. مصدر هذه الصفحة هو ملف INTENT.md الخاص بالتطبيق؛ وعند اختلافهما فمستودع التطبيق هو الصحيح وهذه الصفحة متأخرة."
 }
}


def dev_body(t, code):
    """The developers page from its strings table: the same intents table, samples and formats list as the English page."""
    play = play_link("developers", "docs")
    kotlin = KOTLIN_SAMPLE.replace("PLAY_LINK", play)
    formats = ", ".join(f"<code>{f}</code>" for f in FORMATS_DELIVERED)
    th = "".join(f"<th>{x}</th>" for x in t["th"])
    rows = "\n".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in t["rows"])
    return (f'\n<div class="prose">\n<h1>{t["h1"]}</h1>\n<p class="meta">{t["meta"]}</p>\n\n'
            f'<h2>{t["intents_h"]}</h2>\n<table>\n<thead><tr>{th}</tr></thead>\n<tbody>\n{rows}\n</tbody>\n</table>\n\n'
            f'<p>{t["p_handback"]}</p>\n\n<p>{t["p_extras"]}</p>\n\n'
            f'<h2>{t["result_h"]}</h2>\n<ul>\n  <li>{t["li_text"]}</li>\n  <li>{t["li_format"].replace("{formats}", formats)}</li>\n</ul>\n<p>{t["p_nothing"]}</p>\n\n'
            f'<h2>Kotlin</h2>\n{code_block(kotlin)}\n<p>{t["p_query"]}</p>\n{code_block(QUERIES_SAMPLE)}\n\n'
            f'<h2>Java</h2>\n{code_block(JAVA_SAMPLE)}\n\n'
            f'<h2>{t["zxing_h"]}</h2>\n<p>{t["zxing_p"]}</p>\n\n'
            f'<h2>{t["sees_h"]}</h2>\n<p>{t["sees_p"]}</p>\n\n'
            f'<div class="card"><p><strong>{t["card_lead"]}</strong> {t["card"].replace("{play}", play)}</p></div>\n</div>\n')


def dev_ld(t, code):
    return {**DEVELOPERS_LD, "name": t["h1"], "inLanguage": code}


LOCAL["developers.html"] = family_pages("developers.html")


# ---- the features page: one page, the whole product, in the order people meet it (operator, 2026-09-05) -----
FEAT_T = {
 "en": {
  "title": "Everything it does",
  "desc": "Every feature of Verdetto, in the order people meet it: the link shown first, damaged codes, lookups you allow, codes you make, and no ads.",
  "lede": "Verdetto reads QR codes and barcodes and shows you what is in them before you act. Free, no ads, nothing collected. Here is all of it, in the order most people meet it.",
  "formats_line": "{N} kinds of codes, every one measured on the September 4, 2026 validation run:",
  "sections": [
   {
    "id": "see",
    "kicker": "Before it opens",
    "h2": "See the link before it opens",
    "shot": "result-sheet-warning.webp",
    "alt": "The Verdetto result sheet for a QR code that leads to paypa1.com: the address shown before anything opens, a Danger chip reading Imitates paypal.com, and an Open anyway button.",
    "ps": [
     "A QR code is a link you cannot read. Verdetto shows the address before anything opens, checks it on your phone, and leaves the decision to you: open, or not.",
     "The checks look for lookalike names (paypa1.com), shortened and affiliate links followed to where they lead, hidden sign-ins, raw IP addresses, unusual ports, unencrypted addresses, downloads, script addresses and tracking and affiliate parameters, and compare the address with a warning list of known phishing, scam and sanctions entries kept on the phone.",
     "The result is one line: Danger, Caution, or No warnings found. It is never a promise that something is safe; whether to open is your call. {GUIDE}."
    ],
    "guide": "How to check a link yourself"
   },
   {
    "id": "reads",
    "kicker": "Damaged codes",
    "h2": "Reads the codes other apps give up on",
    "shot": "batch.webp",
    "alt": "The batch sheet in Verdetto counting codes as they are scanned, with Done and Share list.",
    "ps": [
     "Faded, torn, badly printed, tilted or inverted: it reads while you aim and keeps trying across frames instead of asking you to hold still. Several codes in view? Each one is outlined and you tap the one you meant. Batch mode counts them all and exports the session as CSV."
    ],
    "formats": True
   },
   {
    "id": "knows",
    "kicker": "What a code is",
    "h2": "Knows what a code is, and does the one right thing",
    "shot": "wifi.webp",
    "alt": "A Wi-Fi network read by Verdetto: the network name, a caution that it is open with no password, and a Join button.",
    "ps": [
     "A Wi-Fi code joins the network in one tap. A contact card adds to your contacts. A boarding pass shows itself at the gate, big and bright. Calendar events, sign-in codes, locations, payment addresses, product and medicine numbers, GS1 packs, vehicle numbers: each opens with the one action that fits, and nothing opens by itself.",
     "Boarding passes, driver's licenses, and health certificates are read on the phone, shown once, and never kept. The app never looks a person up."
    ]
   },
   {
    "id": "lookups",
    "kicker": "Lookups",
    "h2": "Looks things up, only when you allow it",
    "shot": "vehicle-vin.webp",
    "alt": "A VIN read by Verdetto: the vehicle, model year, manufacturer, and a Look up vehicle button.",
    "ps": [
     "Scan a product and see what it is: books from Open Library and the German and French national libraries, food and cosmetics from Open Food Facts, medicines from openFDA, music from MusicBrainz, and the rest from Wikidata. Scan a vehicle's VIN: make, model, engine, recall campaigns, crash-test ratings and fuel economy from the US government's NHTSA and EPA databases.",
     "Each source receives the number and the app's name, nothing else. One switch turns online lookups off and product lookups have a switch of their own; with online off, nothing leaves the phone and every built-in check still works. {PRIVACY}."
    ],
    "privacy": "What the privacy policy says"
   },
   {
    "id": "create",
    "kicker": "Your own codes",
    "h2": "Make your own codes",
    "shot": "create.webp",
    "alt": "The Create screen in Verdetto: your card at the top, then Website, Text, Wi-Fi, Contact, Email, SMS, Phone, Location, Calendar and Clipboard.",
    "ps": [
     "Website, text, Wi-Fi, contact, email, SMS, phone, location, calendar, or whatever is on your clipboard: type it and the code appears as you go. Your own contact card comes first, with a live preview. Save it as an image, share it or print it; the app reads its own code back before it lets you, so what you hand out scans."
    ]
   },
   {
    "id": "hand",
    "kicker": "In the hand",
    "h2": "Made for the hand",
    "shot": "camera-left.webp",
    "alt": "The Verdetto camera screen in the left-handed layout, its controls on the left.",
    "ps": [
     "A Quick Settings tile opens the camera from the shade. Tap to focus, pinch to zoom, a torch when the light is low. A left-handed layout puts every control within reach. Results can be read aloud. Sound and vibration on read, if you want them. Eleven languages. Android 8 and later."
    ]
   },
   {
    "id": "history",
    "kicker": "Your history",
    "h2": "History that is yours",
    "shot": "history.webp",
    "alt": "Verdetto history with filter chips for Links, Wi-Fi, Batch and Starred, and a result sheet reopened from it.",
    "ps": [
     "Search it, star it, swipe to delete, export or import it as CSV. Scans older than 90 days clear on their own unless you star them. A private session keeps nothing at all. History rides in your phone's own backup unless you turn that off, and uninstalling removes it."
    ]
   },
   {
    "id": "apps",
    "kicker": "Other apps",
    "h2": "Works with other apps",
    "shot": None,
    "alt": "",
    "ps": [
     "Any app can ask Verdetto for a scan and get the code back, the way apps did with the ZXing scanner. Share a picture into it and it decodes the codes in the picture. {DEV}."
    ],
    "dev": "The details for developers"
   },
   {
    "id": "free",
    "kicker": "The deal",
    "h2": "Free, no ads, nothing collected",
    "shot": None,
    "alt": "",
    "ps": [
     "Every feature is free for everyone and stays free. No accounts, no analytics, no ads, so no fake buttons. Frames are scanned on the device and dropped. It is paid for and passed on by the people who use it: a one-time contribution from $0.99 keeps it going, and nothing is locked behind it. Share the app from inside it: a code any camera reads, carrying the store link and nothing else. {SUPPORT}."
    ],
    "support": "How that works",
    "cta": True
   }
  ]
 },
 "de": {
  "title": "Alles, was die App kann",
  "desc": "Jede Funktion von Verdetto in der Reihenfolge, in der man ihr begegnet: der Link zuerst, beschädigte Codes, erlaubte Abfragen, eigene Codes und keine Werbung.",
  "lede": "Verdetto liest QR-Codes und Barcodes und zeigt dir, was darin steckt, bevor du handelst. Kostenlos, ohne Werbung, ohne Datensammeln. Hier ist alles, in der Reihenfolge, in der die meisten es erleben.",
  "formats_line": "{N} Arten von Codes, jede gemessen im Validierungslauf vom 4. September 2026:",
  "sections": [
   {
    "id": "see",
    "shot": "result-sheet-warning.webp",
    "kicker": "Bevor er sich öffnet",
    "h2": "Sieh den Link, bevor er sich öffnet",
    "alt": "Das Verdetto-Ergebnisblatt für einen QR-Code, der zu paypa1.com führt: die Adresse, gezeigt bevor sich etwas öffnet, ein Gefahr-Chip „Imitiert paypal.com“ und ein Button „Trotzdem öffnen“.",
    "ps": [
     "Ein QR-Code ist ein Link, den du nicht lesen kannst. Verdetto zeigt die Adresse, bevor sich etwas öffnet, prüft sie auf deinem Telefon und lässt dir die Entscheidung: öffnen oder nicht.",
     "Die Prüfungen achten auf ähnlich aussehende Namen (paypa1.com), verfolgen Kurz- und Affiliate-Links bis zu ihrem Ziel, erkennen versteckte Anmeldedaten, nackte IP-Adressen, ungewöhnliche Ports, unverschlüsselte Adressen, Downloads, Skript-Adressen sowie Tracking- und Affiliate-Parameter und vergleichen die Adresse mit einer Warnliste bekannter Phishing-, Betrugs- und Sanktionseinträge, die auf dem Telefon liegt.",
     "Das Ergebnis ist eine Zeile: Gefahr, Vorsicht oder „Keine Warnungen gefunden“. Es ist nie ein Versprechen, dass etwas sicher ist; ob du öffnest, entscheidest du. {GUIDE}."
    ],
    "guide": "Wie du einen Link selbst prüfst"
   },
   {
    "id": "reads",
    "shot": "batch.webp",
    "formats": True,
    "kicker": "Beschädigte Codes",
    "h2": "Liest die Codes, bei denen andere Apps aufgeben",
    "alt": "Das Stapel-Blatt in Verdetto zählt Codes beim Scannen, mit „Fertig“ und „Liste teilen“.",
    "ps": [
     "Verblasst, zerrissen, schlecht gedruckt, schräg oder invertiert: Verdetto liest, während du zielst, und versucht es über mehrere Bilder hinweg weiter, statt dich stillhalten zu lassen. Mehrere Codes im Bild? Jeder wird umrandet, und du tippst auf den, den du meinst. Der Stapelmodus zählt sie alle und exportiert die Sitzung als CSV."
    ]
   },
   {
    "id": "knows",
    "shot": "wifi.webp",
    "kicker": "Was ein Code ist",
    "h2": "Weiß, was ein Code ist, und tut das eine Richtige",
    "alt": "Ein von Verdetto gelesenes WLAN: der Netzwerkname, ein Hinweis, dass es offen und ohne Passwort ist, und ein Button „Verbinden“.",
    "ps": [
     "Ein WLAN-Code verbindet mit einem Tipp. Eine Kontaktkarte landet in deinen Kontakten. Eine Bordkarte zeigt sich am Gate, groß und hell. Kalendereinträge, Anmeldecodes, Orte, Zahlungsadressen, Produkt- und Arzneimittelnummern, GS1-Packungen, Fahrzeugnummern: Jeder öffnet sich mit der einen passenden Aktion, und nichts öffnet sich von selbst.",
     "Bordkarten, Führerscheine und Gesundheitszertifikate werden auf dem Telefon gelesen, einmal gezeigt und nie aufbewahrt. Die App schlägt nie eine Person nach."
    ]
   },
   {
    "id": "lookups",
    "shot": "vehicle-vin.webp",
    "kicker": "Abfragen",
    "h2": "Schlägt Dinge nach, nur wenn du es erlaubst",
    "alt": "Eine von Verdetto gelesene Fahrgestellnummer: das Fahrzeug, das Modelljahr, der Hersteller und ein Button „Fahrzeug nachschlagen“.",
    "ps": [
     "Scanne ein Produkt und sieh, was es ist: Bücher aus der Open Library und den deutschen und französischen Nationalbibliotheken, Lebensmittel und Kosmetik aus Open Food Facts, Arzneimittel aus openFDA, Musik aus MusicBrainz und den Rest aus Wikidata. Scanne die Fahrgestellnummer eines Fahrzeugs: Marke, Modell, Motor, Rückrufaktionen, Crashtest-Bewertungen und Verbrauch aus den Datenbanken der US-Behörden NHTSA und EPA.",
     "Jede Quelle erhält die Nummer und den Namen der App, sonst nichts. Ein Schalter stellt Online-Abfragen ab, Produktabfragen haben einen eigenen; ist Online aus, verlässt nichts das Telefon, und jede eingebaute Prüfung funktioniert weiter. {PRIVACY}."
    ],
    "privacy": "Was die Datenschutzerklärung sagt"
   },
   {
    "id": "create",
    "shot": "create.webp",
    "kicker": "Eigene Codes",
    "h2": "Erstelle eigene Codes",
    "alt": "Der Erstellen-Bildschirm in Verdetto: deine Karte oben, dann Website, Text, WLAN, Kontakt, E-Mail, SMS, Telefon, Ort, Kalender und Zwischenablage.",
    "ps": [
     "Website, Text, WLAN, Kontakt, E-Mail, SMS, Telefon, Ort, Kalender oder was gerade in deiner Zwischenablage liegt: Tipp es ein, und der Code entsteht beim Schreiben. Deine eigene Kontaktkarte kommt zuerst, mit Live-Vorschau. Speichere ihn als Bild, teile oder drucke ihn; die App liest ihren eigenen Code zurück, bevor sie dich lässt, damit alles, was du weitergibst, auch gelesen wird."
    ]
   },
   {
    "id": "hand",
    "shot": "camera-left.webp",
    "kicker": "In der Hand",
    "h2": "Für die Hand gemacht",
    "alt": "Der Verdetto-Kamerabildschirm im Linkshänder-Layout, die Bedienelemente links.",
    "ps": [
     "Eine Schnelleinstellungen-Kachel öffnet die Kamera aus der Leiste. Tippen zum Fokussieren, Ziehen zum Zoomen, eine Taschenlampe bei wenig Licht. Ein Linkshänder-Layout bringt jedes Bedienelement in Reichweite. Ergebnisse können vorgelesen werden. Ton und Vibration beim Lesen, wenn du willst. Elf Sprachen. Android 8 und neuer."
    ]
   },
   {
    "id": "history",
    "shot": "history.webp",
    "kicker": "Deine Historie",
    "h2": "Eine Historie, die dir gehört",
    "alt": "Die Verdetto-Historie mit Filter-Chips für Links, WLAN, Stapel und Markiert und ein daraus erneut geöffnetes Ergebnisblatt.",
    "ps": [
     "Durchsuche sie, markiere Einträge, wische zum Löschen, exportiere oder importiere sie als CSV. Scans, die älter als 90 Tage sind, löschen sich selbst, außer du markierst sie. Eine private Sitzung behält gar nichts. Die Historie wandert mit dem Backup deines Telefons, außer du stellst das ab, und die Deinstallation entfernt sie."
    ]
   },
   {
    "id": "apps",
    "shot": None,
    "kicker": "Andere Apps",
    "h2": "Arbeitet mit anderen Apps",
    "alt": "",
    "ps": [
     "Jede App kann Verdetto um einen Scan bitten und den Code zurückbekommen, so wie Apps es beim ZXing-Scanner taten. Teile ein Bild hinein, und es decodiert die Codes im Bild. {DEV}."
    ],
    "dev": "Die Details für Entwickler"
   },
   {
    "id": "free",
    "shot": None,
    "cta": True,
    "kicker": "Der Deal",
    "h2": "Kostenlos, ohne Werbung, ohne Datensammeln",
    "alt": "",
    "ps": [
     "Jede Funktion ist für alle kostenlos und bleibt es. Keine Konten, keine Analysen, keine Werbung, also keine falschen Buttons. Bilder werden auf dem Gerät gescannt und verworfen. Bezahlt und weitergegeben von den Menschen, die die App nutzen: Ein einmaliger Beitrag ab 0,99 $ hält sie am Laufen, und nichts ist dahinter gesperrt. Teile die App aus ihr heraus: ein Code, den jede Kamera liest, mit dem Store-Link und sonst nichts. {SUPPORT}."
    ],
    "support": "Wie das funktioniert"
   }
  ]
 },
 "es": {
  "title": "Todo lo que hace",
  "desc": "Cada función de Verdetto, en el orden en que la gente la encuentra: el enlace primero, códigos dañados, consultas que permites, códigos propios y sin anuncios.",
  "lede": "Verdetto lee códigos QR y de barras y te muestra qué contienen antes de que actúes. Gratis, sin anuncios, sin recopilar nada. Aquí está todo, en el orden en que la mayoría lo encuentra.",
  "formats_line": "{N} tipos de códigos, cada uno medido en la ejecución de validación del 4 de septiembre de 2026:",
  "sections": [
   {
    "id": "see",
    "shot": "result-sheet-warning.webp",
    "kicker": "Antes de que se abra",
    "h2": "Mira el enlace antes de que se abra",
    "alt": "La hoja de resultados de Verdetto para un código QR que lleva a paypa1.com: la dirección mostrada antes de que se abra nada, un chip de peligro «Imita a paypal.com» y un botón «Abrir de todos modos».",
    "ps": [
     "Un código QR es un enlace que no puedes leer. Verdetto muestra la dirección antes de que se abra nada, la comprueba en tu teléfono y te deja la decisión a ti: abrir, o no.",
     "Las comprobaciones buscan nombres parecidos (paypa1.com), siguen los enlaces cortos y de afiliado hasta su destino, y detectan datos de acceso ocultos, direcciones IP en bruto, puertos inusuales, direcciones sin cifrar, descargas, direcciones de script y parámetros de rastreo y de afiliado; además comparan la dirección con una lista de avisos de entradas conocidas de phishing, estafa y sanciones guardada en el teléfono.",
     "El resultado es una línea: Peligro, Precaución o «No se encontraron avisos». Nunca es una promesa de que algo sea seguro; abrir o no es tu decisión. {GUIDE}."
    ],
    "guide": "Cómo comprobar un enlace tú mismo"
   },
   {
    "id": "reads",
    "shot": "batch.webp",
    "formats": True,
    "kicker": "Códigos dañados",
    "h2": "Lee los códigos que otras apps abandonan",
    "alt": "La hoja de lote de Verdetto contando códigos mientras se escanean, con «Listo» y «Compartir lista».",
    "ps": [
     "Descoloridos, rotos, mal impresos, inclinados o invertidos: lee mientras apuntas y sigue intentándolo fotograma tras fotograma en vez de pedirte que te quedes quieto. ¿Varios códigos a la vista? Cada uno se enmarca y tocas el que querías. El modo lote los cuenta todos y exporta la sesión como CSV."
    ]
   },
   {
    "id": "knows",
    "shot": "wifi.webp",
    "kicker": "Qué es un código",
    "h2": "Sabe qué es un código, y hace lo único correcto",
    "alt": "Una red Wi-Fi leída por Verdetto: el nombre de la red, un aviso de que es abierta y sin contraseña, y un botón «Conectar».",
    "ps": [
     "Un código Wi-Fi conecta a la red con un toque. Una tarjeta de contacto se añade a tus contactos. Una tarjeta de embarque se muestra en la puerta, grande y brillante. Eventos de calendario, códigos de acceso, ubicaciones, direcciones de pago, números de productos y medicamentos, paquetes GS1, números de vehículo: cada uno se abre con la única acción que corresponde, y nada se abre solo.",
     "Las tarjetas de embarque, los permisos de conducir y los certificados sanitarios se leen en el teléfono, se muestran una vez y nunca se guardan. La app nunca busca a una persona."
    ]
   },
   {
    "id": "lookups",
    "shot": "vehicle-vin.webp",
    "kicker": "Consultas",
    "h2": "Busca información, solo cuando lo permites",
    "alt": "Un VIN leído por Verdetto: el vehículo, el año del modelo, el fabricante y un botón «Consultar vehículo».",
    "ps": [
     "Escanea un producto y descubre qué es: libros de Open Library y de las bibliotecas nacionales de Alemania y Francia, alimentos y cosméticos de Open Food Facts, medicamentos de openFDA, música de MusicBrainz y el resto de Wikidata. Escanea el VIN de un vehículo: marca, modelo, motor, campañas de retirada, calificaciones de pruebas de choque y consumo de las bases de datos de la NHTSA y la EPA del gobierno de Estados Unidos.",
     "Cada fuente recibe el número y el nombre de la app, nada más. Un interruptor apaga las consultas en línea y las consultas de productos tienen el suyo propio; con la conexión apagada nada sale del teléfono y todas las comprobaciones integradas siguen funcionando. {PRIVACY}."
    ],
    "privacy": "Qué dice la política de privacidad"
   },
   {
    "id": "create",
    "shot": "create.webp",
    "kicker": "Tus propios códigos",
    "h2": "Crea tus propios códigos",
    "alt": "La pantalla Crear de Verdetto: tu tarjeta arriba y después Sitio web, Texto, Wi-Fi, Contacto, Correo, SMS, Teléfono, Ubicación, Calendario y Portapapeles.",
    "ps": [
     "Sitio web, texto, Wi-Fi, contacto, correo, SMS, teléfono, ubicación, calendario o lo que tengas en el portapapeles: escríbelo y el código aparece mientras tecleas. Tu propia tarjeta de contacto va primero, con vista previa en vivo. Guárdalo como imagen, compártelo o imprímelo; la app lee su propio código antes de dejarte, para que lo que entregues se escanee."
    ]
   },
   {
    "id": "hand",
    "shot": "camera-left.webp",
    "kicker": "En la mano",
    "h2": "Hecho para la mano",
    "alt": "La pantalla de cámara de Verdetto con el diseño para zurdos, con los controles a la izquierda.",
    "ps": [
     "Un mosaico de ajustes rápidos abre la cámara desde el panel. Toca para enfocar, pellizca para acercar, linterna cuando hay poca luz. Un diseño para zurdos pone cada control al alcance. Los resultados se pueden leer en voz alta. Sonido y vibración al leer, si los quieres. Once idiomas. Android 8 y posteriores."
    ]
   },
   {
    "id": "history",
    "shot": "history.webp",
    "kicker": "Tu historial",
    "h2": "Un historial que es tuyo",
    "alt": "El historial de Verdetto con chips de filtro para Enlaces, Wi-Fi, Lote y Destacados, y una hoja de resultados reabierta desde él.",
    "ps": [
     "Búscalo, destácalo, desliza para borrar, expórtalo o impórtalo como CSV. Los escaneos con más de 90 días se borran solos a menos que los destaques. Una sesión privada no guarda nada. El historial viaja en la copia de seguridad de tu propio teléfono a menos que lo desactives, y desinstalar lo elimina."
    ]
   },
   {
    "id": "apps",
    "shot": None,
    "kicker": "Otras apps",
    "h2": "Funciona con otras apps",
    "alt": "",
    "ps": [
     "Cualquier app puede pedirle a Verdetto un escaneo y recibir el código, como hacían las apps con el escáner ZXing. Comparte una imagen con ella y decodifica los códigos de la imagen. {DEV}."
    ],
    "dev": "Los detalles para desarrolladores"
   },
   {
    "id": "free",
    "shot": None,
    "cta": True,
    "kicker": "El trato",
    "h2": "Gratis, sin anuncios, sin recopilar nada",
    "alt": "",
    "ps": [
     "Todas las funciones son gratis para todos y lo seguirán siendo. Sin cuentas, sin analíticas, sin anuncios, así que sin botones falsos. Los fotogramas se escanean en el dispositivo y se descartan. Lo pagan y lo pasan a otros las personas que lo usan: una contribución única desde 0,99 $ lo mantiene en marcha, y nada queda bloqueado tras ella. Comparte la app desde dentro: un código que cualquier cámara lee, con el enlace de la tienda y nada más. {SUPPORT}."
    ],
    "support": "Cómo funciona"
   }
  ]
 },
 "fr": {
  "title": "Tout ce qu'elle fait",
  "desc": "Chaque fonction de Verdetto, dans l'ordre où on la rencontre : le lien d'abord, les codes abîmés, les recherches autorisées, vos codes, et pas de publicité.",
  "lede": "Verdetto lit les codes QR et les codes-barres et vous montre ce qu'ils contiennent avant que vous n'agissiez. Gratuit, sans publicité, sans rien collecter. Voici tout, dans l'ordre où la plupart des gens le rencontrent.",
  "formats_line": "{N} sortes de codes, chacune mesurée lors de la validation du 4 septembre 2026 :",
  "sections": [
   {
    "id": "see",
    "shot": "result-sheet-warning.webp",
    "kicker": "Avant l'ouverture",
    "h2": "Voyez le lien avant qu'il ne s'ouvre",
    "alt": "La feuille de résultat Verdetto pour un code QR menant à paypa1.com : l'adresse affichée avant toute ouverture, une puce Danger « Imite paypal.com » et un bouton « Ouvrir quand même ».",
    "ps": [
     "Un code QR est un lien que vous ne pouvez pas lire. Verdetto affiche l'adresse avant que quoi que ce soit ne s'ouvre, la vérifie sur votre téléphone et vous laisse la décision : ouvrir, ou non.",
     "Les vérifications cherchent les noms imités (paypa1.com), suivent les liens courts et d'affiliation jusqu'à leur destination, repèrent les identifiants cachés, les adresses IP brutes, les ports inhabituels, les adresses non chiffrées, les téléchargements, les adresses de scripts et les paramètres de pistage et d'affiliation, et comparent l'adresse à une liste d'alerte d'entrées connues de phishing, d'arnaque et de sanctions conservée sur le téléphone.",
     "Le résultat tient en une ligne : Danger, Prudence ou « Aucune alerte trouvée ». Ce n'est jamais une promesse que quelque chose est sûr ; ouvrir ou non, c'est votre choix. {GUIDE}."
    ],
    "guide": "Comment vérifier un lien vous-même"
   },
   {
    "id": "reads",
    "shot": "batch.webp",
    "formats": True,
    "kicker": "Codes abîmés",
    "h2": "Lit les codes que les autres applications abandonnent",
    "alt": "La feuille de lot de Verdetto comptant les codes au fil du scan, avec « Terminé » et « Partager la liste ».",
    "ps": [
     "Délavés, déchirés, mal imprimés, inclinés ou inversés : elle lit pendant que vous visez et continue d'essayer image après image au lieu de vous demander de ne pas bouger. Plusieurs codes dans le champ ? Chacun est entouré et vous touchez celui que vous vouliez. Le mode lot les compte tous et exporte la session en CSV."
    ]
   },
   {
    "id": "knows",
    "shot": "wifi.webp",
    "kicker": "Ce qu'est un code",
    "h2": "Sait ce qu'est un code, et fait la seule bonne action",
    "alt": "Un réseau Wi-Fi lu par Verdetto : le nom du réseau, un avertissement qu'il est ouvert sans mot de passe, et un bouton « Rejoindre ».",
    "ps": [
     "Un code Wi-Fi rejoint le réseau d'un toucher. Une carte de contact s'ajoute à vos contacts. Une carte d'embarquement s'affiche à la porte, grande et lumineuse. Événements d'agenda, codes de connexion, lieux, adresses de paiement, numéros de produits et de médicaments, colis GS1, numéros de véhicule : chacun s'ouvre avec la seule action qui convient, et rien ne s'ouvre tout seul.",
     "Les cartes d'embarquement, les permis de conduire et les certificats sanitaires sont lus sur le téléphone, affichés une fois et jamais conservés. L'application ne recherche jamais une personne."
    ]
   },
   {
    "id": "lookups",
    "shot": "vehicle-vin.webp",
    "kicker": "Recherches",
    "h2": "Cherche des informations, seulement si vous l'autorisez",
    "alt": "Un VIN lu par Verdetto : le véhicule, l'année du modèle, le constructeur et un bouton « Rechercher le véhicule ».",
    "ps": [
     "Scannez un produit et voyez ce que c'est : des livres via Open Library et les bibliothèques nationales allemande et française, l'alimentation et les cosmétiques via Open Food Facts, les médicaments via openFDA, la musique via MusicBrainz, et le reste via Wikidata. Scannez le VIN d'un véhicule : marque, modèle, moteur, campagnes de rappel, notes aux tests de choc et consommation, depuis les bases de données de la NHTSA et de l'EPA du gouvernement des États-Unis.",
     "Chaque source reçoit le numéro et le nom de l'application, rien d'autre. Un interrupteur coupe les recherches en ligne et les recherches de produits ont le leur ; hors ligne, rien ne quitte le téléphone et chaque vérification intégrée continue de fonctionner. {PRIVACY}."
    ],
    "privacy": "Ce que dit la politique de confidentialité"
   },
   {
    "id": "create",
    "shot": "create.webp",
    "kicker": "Vos propres codes",
    "h2": "Créez vos propres codes",
    "alt": "L'écran Créer de Verdetto : votre carte en haut, puis Site web, Texte, Wi-Fi, Contact, E-mail, SMS, Téléphone, Lieu, Agenda et Presse-papiers.",
    "ps": [
     "Site web, texte, Wi-Fi, contact, e-mail, SMS, téléphone, lieu, agenda ou ce qui se trouve dans votre presse-papiers : tapez-le et le code apparaît au fil de la saisie. Votre propre carte de contact vient en premier, avec un aperçu en direct. Enregistrez-le en image, partagez-le ou imprimez-le ; l'application relit son propre code avant de vous laisser faire, pour que ce que vous distribuez se lise."
    ]
   },
   {
    "id": "hand",
    "shot": "camera-left.webp",
    "kicker": "Dans la main",
    "h2": "Fait pour la main",
    "alt": "L'écran caméra de Verdetto en disposition pour gauchers, les commandes à gauche.",
    "ps": [
     "Une tuile de réglages rapides ouvre la caméra depuis le volet. Touchez pour faire la mise au point, pincez pour zoomer, une lampe quand la lumière manque. Une disposition pour gauchers met chaque commande à portée. Les résultats peuvent être lus à voix haute. Son et vibration à la lecture, si vous le souhaitez. Onze langues. Android 8 et versions ultérieures."
    ]
   },
   {
    "id": "history",
    "shot": "history.webp",
    "kicker": "Votre historique",
    "h2": "Un historique qui vous appartient",
    "alt": "L'historique de Verdetto avec des puces de filtre Liens, Wi-Fi, Lot et Favoris, et une feuille de résultat rouverte depuis celui-ci.",
    "ps": [
     "Cherchez, mettez en favori, balayez pour supprimer, exportez ou importez en CSV. Les scans de plus de 90 jours s'effacent d'eux-mêmes sauf si vous les mettez en favori. Une session privée ne garde rien du tout. L'historique voyage dans la sauvegarde de votre téléphone sauf si vous la désactivez, et la désinstallation le supprime."
    ]
   },
   {
    "id": "apps",
    "shot": None,
    "kicker": "Autres applications",
    "h2": "Fonctionne avec d'autres applications",
    "alt": "",
    "ps": [
     "N'importe quelle application peut demander un scan à Verdetto et récupérer le code, comme les applications le faisaient avec le lecteur ZXing. Partagez-lui une image et elle décode les codes qu'elle contient. {DEV}."
    ],
    "dev": "Les détails pour les développeurs"
   },
   {
    "id": "free",
    "shot": None,
    "cta": True,
    "kicker": "Le marché",
    "h2": "Gratuit, sans publicité, sans rien collecter",
    "alt": "",
    "ps": [
     "Chaque fonction est gratuite pour tous et le reste. Pas de comptes, pas d'analyse d'audience, pas de publicité, donc pas de faux boutons. Les images sont analysées sur l'appareil puis jetées. Financée et transmise par les personnes qui l'utilisent : une contribution unique dès 0,99 $ la fait vivre, et rien n'est verrouillé derrière. Partage l'application depuis l'application : un code que n'importe quel appareil photo lit, avec le lien de la boutique et rien d'autre. {SUPPORT}."
    ],
    "support": "Comment ça marche"
   }
  ]
 },
 "pt-BR": {
  "title": "Tudo o que ele faz",
  "desc": "Cada recurso do Verdetto, na ordem em que as pessoas o encontram: o link primeiro, códigos danificados, consultas permitidas, códigos seus e sem anúncios.",
  "lede": "O Verdetto lê códigos QR e de barras e mostra o que há neles antes que você aja. Grátis, sem anúncios, sem coletar nada. Aqui está tudo, na ordem em que a maioria encontra.",
  "formats_line": "{N} tipos de código, cada um medido na rodada de validação de 4 de setembro de 2026:",
  "sections": [
   {
    "id": "see",
    "shot": "result-sheet-warning.webp",
    "kicker": "Antes de abrir",
    "h2": "Veja o link antes que ele abra",
    "alt": "A folha de resultado do Verdetto para um código QR que leva a paypa1.com: o endereço mostrado antes de qualquer coisa abrir, um chip de Perigo \"Imita paypal.com\" e um botão \"Abrir mesmo assim\".",
    "ps": [
     "Um código QR é um link que você não consegue ler. O Verdetto mostra o endereço antes que qualquer coisa abra, verifica no seu celular e deixa a decisão com você: abrir, ou não.",
     "As verificações procuram nomes parecidos (paypa1.com), seguem links curtos e de afiliado até o destino, detectam credenciais ocultas, endereços IP puros, portas incomuns, endereços sem criptografia, downloads, endereços de script e parâmetros de rastreamento e de afiliado, e comparam o endereço com uma lista de alertas de entradas conhecidas de phishing, golpes e sanções guardada no celular.",
     "O resultado é uma linha: Perigo, Cuidado ou \"Nenhum alerta encontrado\". Nunca é uma promessa de que algo é seguro; abrir ou não é decisão sua. {GUIDE}."
    ],
    "guide": "Como verificar um link você mesmo"
   },
   {
    "id": "reads",
    "shot": "batch.webp",
    "formats": True,
    "kicker": "Códigos danificados",
    "h2": "Lê os códigos que outros apps desistem de ler",
    "alt": "A folha de lote do Verdetto contando códigos conforme são lidos, com \"Concluir\" e \"Compartilhar lista\".",
    "ps": [
     "Desbotados, rasgados, mal impressos, inclinados ou invertidos: ele lê enquanto você aponta e continua tentando quadro a quadro em vez de pedir que você fique parado. Vários códigos à vista? Cada um recebe um contorno e você toca no que queria. O modo lote conta todos e exporta a sessão como CSV."
    ]
   },
   {
    "id": "knows",
    "shot": "wifi.webp",
    "kicker": "O que é um código",
    "h2": "Sabe o que é um código, e faz a única coisa certa",
    "alt": "Uma rede Wi-Fi lida pelo Verdetto: o nome da rede, um aviso de que ela é aberta e sem senha, e um botão \"Conectar\".",
    "ps": [
     "Um código Wi-Fi conecta à rede em um toque. Um cartão de contato entra nos seus contatos. Um cartão de embarque se mostra no portão, grande e brilhante. Eventos de agenda, códigos de login, locais, endereços de pagamento, números de produtos e medicamentos, embalagens GS1, números de veículo: cada um abre com a única ação que cabe, e nada abre sozinho.",
     "Cartões de embarque, carteiras de motorista e certificados de saúde são lidos no celular, mostrados uma vez e nunca guardados. O app nunca procura uma pessoa."
    ]
   },
   {
    "id": "lookups",
    "shot": "vehicle-vin.webp",
    "kicker": "Consultas",
    "h2": "Busca informações, só quando você permite",
    "alt": "Um VIN lido pelo Verdetto: o veículo, o ano do modelo, o fabricante e um botão \"Consultar veículo\".",
    "ps": [
     "Escaneie um produto e veja o que ele é: livros da Open Library e das bibliotecas nacionais da Alemanha e da França, alimentos e cosméticos do Open Food Facts, medicamentos do openFDA, música do MusicBrainz e o resto do Wikidata. Escaneie o VIN de um veículo: marca, modelo, motor, campanhas de recall, notas de testes de colisão e consumo de combustível dos bancos de dados da NHTSA e da EPA do governo dos EUA.",
     "Cada fonte recebe o número e o nome do app, nada mais. Um botão desliga as consultas online e as consultas de produtos têm um botão próprio; com o online desligado, nada sai do celular e todas as verificações embutidas continuam funcionando. {PRIVACY}."
    ],
    "privacy": "O que diz a política de privacidade"
   },
   {
    "id": "create",
    "shot": "create.webp",
    "kicker": "Seus próprios códigos",
    "h2": "Crie seus próprios códigos",
    "alt": "A tela Criar do Verdetto: seu cartão no topo, depois Site, Texto, Wi-Fi, Contato, E-mail, SMS, Telefone, Local, Agenda e Área de transferência.",
    "ps": [
     "Site, texto, Wi-Fi, contato, e-mail, SMS, telefone, local, agenda ou o que estiver na sua área de transferência: digite e o código aparece enquanto você escreve. Seu próprio cartão de contato vem primeiro, com prévia ao vivo. Salve como imagem, compartilhe ou imprima; o app lê o próprio código de volta antes de deixar, para que o que você entregar seja lido."
    ]
   },
   {
    "id": "hand",
    "shot": "camera-left.webp",
    "kicker": "Na mão",
    "h2": "Feito para a mão",
    "alt": "A tela da câmera do Verdetto no layout para canhotos, com os controles à esquerda.",
    "ps": [
     "Um bloco de Configurações rápidas abre a câmera pela barra. Toque para focar, belisque para aproximar, lanterna quando a luz é pouca. Um layout para canhotos põe cada controle ao alcance. Os resultados podem ser lidos em voz alta. Som e vibração na leitura, se você quiser. Onze idiomas. Android 8 ou mais recente."
    ]
   },
   {
    "id": "history",
    "shot": "history.webp",
    "kicker": "Seu histórico",
    "h2": "Um histórico que é seu",
    "alt": "O histórico do Verdetto com chips de filtro Links, Wi-Fi, Lote e Favoritos, e uma folha de resultado reaberta a partir dele.",
    "ps": [
     "Pesquise, favorite, deslize para apagar, exporte ou importe como CSV. Leituras com mais de 90 dias somem sozinhas, a menos que você as favorite. Uma sessão privada não guarda nada. O histórico vai no backup do seu próprio celular a menos que você desligue isso, e desinstalar o remove."
    ]
   },
   {
    "id": "apps",
    "shot": None,
    "kicker": "Outros apps",
    "h2": "Funciona com outros apps",
    "alt": "",
    "ps": [
     "Qualquer app pode pedir uma leitura ao Verdetto e receber o código de volta, como os apps faziam com o leitor ZXing. Compartilhe uma imagem com ele e ele decodifica os códigos da imagem. {DEV}."
    ],
    "dev": "Os detalhes para desenvolvedores"
   },
   {
    "id": "free",
    "shot": None,
    "cta": True,
    "kicker": "O acordo",
    "h2": "Grátis, sem anúncios, sem coletar nada",
    "alt": "",
    "ps": [
     "Todo recurso é gratuito para todos e continua assim. Sem contas, sem análises de uso, sem anúncios, portanto sem botões falsos. Os quadros são lidos no aparelho e descartados. Pago e passado adiante pelas pessoas que o usam: uma contribuição única a partir de US$ 0,99 o mantém, e nada fica trancado atrás dela. Compartilhe o app de dentro dele: um código que qualquer câmera lê, com o link da loja e nada mais. {SUPPORT}."
    ],
    "support": "Como isso funciona"
   }
  ]
 },
 "id": {
  "title": "Semua yang bisa dilakukannya",
  "desc": "Setiap fitur Verdetto, dalam urutan orang menemuinya: tautan ditampilkan dulu, kode rusak, pencarian yang Anda izinkan, kode buatan Anda, dan tanpa iklan.",
  "lede": "Verdetto membaca kode QR dan barcode dan menunjukkan isinya sebelum Anda bertindak. Gratis, tanpa iklan, tidak mengumpulkan apa pun. Inilah semuanya, dalam urutan kebanyakan orang menemuinya.",
  "formats_line": "{N} jenis kode, masing-masing diukur pada uji validasi 4 September 2026:",
  "sections": [
   {
    "id": "see",
    "shot": "result-sheet-warning.webp",
    "kicker": "Sebelum terbuka",
    "h2": "Lihat tautannya sebelum terbuka",
    "alt": "Lembar hasil Verdetto untuk kode QR yang menuju paypa1.com: alamat ditampilkan sebelum apa pun terbuka, chip Bahaya \"Meniru paypal.com\", dan tombol \"Buka saja\".",
    "ps": [
     "Kode QR adalah tautan yang tidak bisa Anda baca. Verdetto menampilkan alamatnya sebelum apa pun terbuka, memeriksanya di ponsel Anda, dan menyerahkan keputusan kepada Anda: buka, atau tidak.",
     "Pemeriksaannya mencari nama yang mirip (paypa1.com), mengikuti tautan pendek dan afiliasi sampai tujuannya, mengenali data masuk tersembunyi, alamat IP mentah, port yang tidak biasa, alamat tanpa enkripsi, unduhan, alamat skrip serta parameter pelacakan dan afiliasi, lalu membandingkan alamat itu dengan daftar peringatan entri phishing, penipuan, dan sanksi yang dikenal, yang disimpan di ponsel.",
     "Hasilnya satu baris: Bahaya, Hati-hati, atau \"Tidak ada peringatan ditemukan\". Itu tidak pernah menjadi janji bahwa sesuatu aman; membuka atau tidak adalah keputusan Anda. {GUIDE}."
    ],
    "guide": "Cara memeriksa tautan sendiri"
   },
   {
    "id": "reads",
    "shot": "batch.webp",
    "formats": True,
    "kicker": "Kode rusak",
    "h2": "Membaca kode yang menyerah dibaca aplikasi lain",
    "alt": "Lembar batch Verdetto menghitung kode saat dipindai, dengan \"Selesai\" dan \"Bagikan daftar\".",
    "ps": [
     "Pudar, sobek, buruk cetakannya, miring, atau terbalik warnanya: ia membaca sambil Anda mengarahkan dan terus mencoba dari bingkai ke bingkai, bukan meminta Anda diam. Beberapa kode terlihat sekaligus? Masing-masing diberi garis tepi dan Anda mengetuk yang Anda maksud. Mode batch menghitung semuanya dan mengekspor sesi sebagai CSV."
    ]
   },
   {
    "id": "knows",
    "shot": "wifi.webp",
    "kicker": "Apa itu sebuah kode",
    "h2": "Tahu apa sebuah kode itu, dan melakukan satu hal yang tepat",
    "alt": "Jaringan Wi-Fi yang dibaca Verdetto: nama jaringan, peringatan bahwa jaringan terbuka tanpa kata sandi, dan tombol \"Gabung\".",
    "ps": [
     "Kode Wi-Fi menyambungkan ke jaringan dengan satu ketukan. Kartu kontak masuk ke kontak Anda. Boarding pass menampilkan dirinya di gerbang, besar dan terang. Acara kalender, kode masuk, lokasi, alamat pembayaran, nomor produk dan obat, kemasan GS1, nomor kendaraan: masing-masing terbuka dengan satu tindakan yang sesuai, dan tidak ada yang terbuka sendiri.",
     "Boarding pass, SIM, dan sertifikat kesehatan dibaca di ponsel, ditampilkan sekali, dan tidak pernah disimpan. Aplikasi tidak pernah mencari data seseorang."
    ]
   },
   {
    "id": "lookups",
    "shot": "vehicle-vin.webp",
    "kicker": "Pencarian",
    "h2": "Mencari informasi, hanya jika Anda mengizinkan",
    "alt": "VIN yang dibaca Verdetto: kendaraan, tahun model, pabrikan, dan tombol \"Cari kendaraan\".",
    "ps": [
     "Pindai sebuah produk dan lihat apa itu: buku dari Open Library dan perpustakaan nasional Jerman dan Prancis, makanan dan kosmetik dari Open Food Facts, obat dari openFDA, musik dari MusicBrainz, dan selebihnya dari Wikidata. Pindai VIN kendaraan: merek, model, mesin, kampanye penarikan, peringkat uji tabrak, dan konsumsi bahan bakar dari basis data NHTSA dan EPA milik pemerintah AS.",
     "Setiap sumber menerima nomornya dan nama aplikasi, tidak lebih. Satu sakelar mematikan pencarian online dan pencarian produk punya sakelar sendiri; dengan online mati, tidak ada yang meninggalkan ponsel dan setiap pemeriksaan bawaan tetap bekerja. {PRIVACY}."
    ],
    "privacy": "Apa kata kebijakan privasi"
   },
   {
    "id": "create",
    "shot": "create.webp",
    "kicker": "Kode Anda sendiri",
    "h2": "Buat kode Anda sendiri",
    "alt": "Layar Buat di Verdetto: kartu Anda di atas, lalu Situs web, Teks, Wi-Fi, Kontak, Email, SMS, Telepon, Lokasi, Kalender, dan Papan klip.",
    "ps": [
     "Situs web, teks, Wi-Fi, kontak, email, SMS, telepon, lokasi, kalender, atau apa pun yang ada di papan klip Anda: ketik saja dan kodenya muncul sambil Anda mengetik. Kartu kontak Anda sendiri ada di urutan pertama, dengan pratinjau langsung. Simpan sebagai gambar, bagikan, atau cetak; aplikasi membaca kembali kodenya sendiri sebelum mengizinkan Anda, sehingga yang Anda bagikan pasti terbaca."
    ]
   },
   {
    "id": "hand",
    "shot": "camera-left.webp",
    "kicker": "Di tangan",
    "h2": "Dibuat untuk tangan",
    "alt": "Layar kamera Verdetto dalam tata letak kidal, kontrolnya di sebelah kiri.",
    "ps": [
     "Ubin Setelan Cepat membuka kamera dari panel. Ketuk untuk fokus, cubit untuk memperbesar, senter saat cahaya redup. Tata letak kidal menaruh setiap kontrol dalam jangkauan. Hasil bisa dibacakan. Suara dan getaran saat membaca, jika Anda mau. Sebelas bahasa. Android 8 ke atas."
    ]
   },
   {
    "id": "history",
    "shot": "history.webp",
    "kicker": "Riwayat Anda",
    "h2": "Riwayat yang menjadi milik Anda",
    "alt": "Riwayat Verdetto dengan chip filter Tautan, Wi-Fi, Batch, dan Berbintang, dan lembar hasil yang dibuka lagi dari sana.",
    "ps": [
     "Cari, beri bintang, geser untuk menghapus, ekspor atau impor sebagai CSV. Pindaian yang lebih tua dari 90 hari terhapus sendiri kecuali Anda beri bintang. Sesi privat tidak menyimpan apa pun. Riwayat ikut dalam cadangan ponsel Anda kecuali Anda mematikannya, dan mencopot aplikasi menghapusnya."
    ]
   },
   {
    "id": "apps",
    "shot": None,
    "kicker": "Aplikasi lain",
    "h2": "Bekerja dengan aplikasi lain",
    "alt": "",
    "ps": [
     "Aplikasi mana pun bisa meminta pindaian kepada Verdetto dan menerima kodenya kembali, seperti yang dilakukan aplikasi dengan pemindai ZXing. Bagikan gambar ke dalamnya dan ia mendekode kode di gambar itu. {DEV}."
    ],
    "dev": "Rincian untuk pengembang"
   },
   {
    "id": "free",
    "shot": None,
    "cta": True,
    "kicker": "Kesepakatannya",
    "h2": "Gratis, tanpa iklan, tidak mengumpulkan apa pun",
    "alt": "",
    "ps": [
     "Setiap fitur gratis untuk semua orang dan tetap gratis. Tanpa akun, tanpa analitik, tanpa iklan, jadi tanpa tombol palsu. Bingkai dipindai di perangkat lalu dibuang. Dibayar dan diteruskan oleh orang-orang yang memakainya: kontribusi sekali bayar mulai $0,99 menjaganya berjalan, dan tidak ada yang dikunci di baliknya. Bagikan aplikasi dari dalam aplikasi: kode yang dibaca kamera apa pun, berisi tautan toko dan tidak ada yang lain. {SUPPORT}."
    ],
    "support": "Bagaimana caranya"
   }
  ]
 },
 "ru": {
  "title": "Всё, что оно умеет",
  "desc": "Каждая возможность Verdetto по порядку: сначала ссылка, повреждённые коды, разрешённые вами запросы, ваши собственные коды и никакой рекламы.",
  "lede": "Verdetto читает QR-коды и штрихкоды и показывает, что в них, прежде чем вы что-то сделаете. Бесплатно, без рекламы, ничего не собирает. Вот всё, в том порядке, в каком с этим встречается большинство.",
  "formats_line": "{N} вид кодов, каждый измерен в проверочном прогоне 4 сентября 2026 года:",
  "sections": [
   {
    "id": "see",
    "shot": "result-sheet-warning.webp",
    "kicker": "До открытия",
    "h2": "Увидьте ссылку до того, как она откроется",
    "alt": "Лист результата Verdetto для QR-кода, ведущего на paypa1.com: адрес показан до того, как что-либо откроется, чип «Опасность» с текстом «Имитирует paypal.com» и кнопка «Открыть всё равно».",
    "ps": [
     "QR-код — это ссылка, которую вы не можете прочитать. Verdetto показывает адрес до того, как что-либо откроется, проверяет его на вашем телефоне и оставляет решение вам: открывать или нет.",
     "Проверки ищут похожие имена (paypa1.com), проходят по коротким и партнёрским ссылкам до места назначения, замечают скрытые данные входа, голые IP-адреса, необычные порты, незашифрованные адреса, загрузки, адреса скриптов и параметры отслеживания и партнёрских программ, а также сверяют адрес со списком предупреждений об известных фишинговых, мошеннических и санкционных записях, который хранится на телефоне.",
     "Результат — одна строка: «Опасность», «Осторожно» или «Предупреждений не найдено». Это никогда не обещание, что что-то безопасно; открывать или нет, решаете вы. {GUIDE}."
    ],
    "guide": "Как проверить ссылку самому"
   },
   {
    "id": "reads",
    "shot": "batch.webp",
    "formats": True,
    "kicker": "Повреждённые коды",
    "h2": "Читает коды, на которых другие приложения сдаются",
    "alt": "Лист пакетного режима Verdetto считает коды по мере сканирования, с кнопками «Готово» и «Поделиться списком».",
    "ps": [
     "Выцветшие, надорванные, плохо напечатанные, наклонённые или инвертированные: оно читает, пока вы наводите камеру, и пробует кадр за кадром, а не просит вас замереть. В кадре несколько кодов? Каждый обведён, и вы касаетесь того, который имели в виду. Пакетный режим считает их все и экспортирует сессию в CSV."
    ]
   },
   {
    "id": "knows",
    "shot": "wifi.webp",
    "kicker": "Что такое код",
    "h2": "Понимает, что перед ним, и делает одно верное действие",
    "alt": "Сеть Wi-Fi, прочитанная Verdetto: имя сети, предупреждение, что она открытая и без пароля, и кнопка «Подключиться».",
    "ps": [
     "Код Wi-Fi подключает к сети одним касанием. Визитка добавляется в контакты. Посадочный талон показывает себя у выхода на посадку, крупно и ярко. События календаря, коды входа, места, платёжные адреса, номера товаров и лекарств, упаковки GS1, номера автомобилей: каждый открывается одним подходящим действием, и ничто не открывается само.",
     "Посадочные талоны, водительские права и медицинские сертификаты читаются на телефоне, показываются один раз и никогда не сохраняются. Приложение никогда не ищет сведения о человеке."
    ]
   },
   {
    "id": "lookups",
    "shot": "vehicle-vin.webp",
    "kicker": "Запросы",
    "h2": "Ищет информацию, только если вы разрешили",
    "alt": "VIN, прочитанный Verdetto: автомобиль, модельный год, производитель и кнопка «Найти автомобиль».",
    "ps": [
     "Отсканируйте товар и узнайте, что это: книги из Open Library и национальных библиотек Германии и Франции, еда и косметика из Open Food Facts, лекарства из openFDA, музыка из MusicBrainz, остальное из Wikidata. Отсканируйте VIN автомобиля: марка, модель, двигатель, отзывные кампании, оценки краш-тестов и расход топлива из баз данных NHTSA и EPA правительства США.",
     "Каждый источник получает номер и имя приложения, ничего больше. Один переключатель отключает онлайн-запросы, у запросов о товарах свой переключатель; при выключенном онлайне ничто не покидает телефон, и все встроенные проверки продолжают работать. {PRIVACY}."
    ],
    "privacy": "Что говорит политика конфиденциальности"
   },
   {
    "id": "create",
    "shot": "create.webp",
    "kicker": "Свои коды",
    "h2": "Создавайте свои коды",
    "alt": "Экран «Создать» в Verdetto: ваша карточка сверху, затем Сайт, Текст, Wi-Fi, Контакт, Почта, SMS, Телефон, Место, Календарь и Буфер обмена.",
    "ps": [
     "Сайт, текст, Wi-Fi, контакт, почта, SMS, телефон, место, календарь или то, что сейчас в буфере обмена: набирайте, и код появляется по мере ввода. Ваша собственная визитка идёт первой, с живым предпросмотром. Сохраните как изображение, поделитесь или распечатайте; приложение само считывает свой код, прежде чем разрешить это, чтобы то, что вы раздаёте, читалось."
    ]
   },
   {
    "id": "hand",
    "shot": "camera-left.webp",
    "kicker": "В руке",
    "h2": "Сделано для руки",
    "alt": "Экран камеры Verdetto в раскладке для левой руки, элементы управления слева.",
    "ps": [
     "Плитка быстрых настроек открывает камеру из шторки. Касание для фокуса, щипок для зума, фонарик при слабом свете. Раскладка для левой руки держит каждый элемент управления под рукой. Результаты можно озвучить. Звук и вибрация при чтении, если хотите. Одиннадцать языков. Android 8 и новее."
    ]
   },
   {
    "id": "history",
    "shot": "history.webp",
    "kicker": "Ваша история",
    "h2": "История, которая принадлежит вам",
    "alt": "История Verdetto с чипами фильтров «Ссылки», «Wi-Fi», «Пакеты» и «Избранное» и открытый из неё лист результата.",
    "ps": [
     "Ищите, отмечайте звёздочкой, смахивайте для удаления, экспортируйте или импортируйте в CSV. Сканы старше 90 дней стираются сами, если вы их не отметили. Приватная сессия не хранит ничего. История попадает в резервную копию телефона, если вы это не отключите, а удаление приложения стирает её."
    ]
   },
   {
    "id": "apps",
    "shot": None,
    "kicker": "Другие приложения",
    "h2": "Работает с другими приложениями",
    "alt": "",
    "ps": [
     "Любое приложение может попросить Verdetto отсканировать код и получить его обратно, как приложения делали со сканером ZXing. Поделитесь с ним изображением, и оно декодирует коды на изображении. {DEV}."
    ],
    "dev": "Подробности для разработчиков"
   },
   {
    "id": "free",
    "shot": None,
    "cta": True,
    "kicker": "Условия",
    "h2": "Бесплатно, без рекламы, ничего не собирает",
    "alt": "",
    "ps": [
     "Каждая возможность бесплатна для всех и такой останется. Никаких учётных записей, аналитики и рекламы, а значит, никаких ложных кнопок. Кадры обрабатываются на устройстве и отбрасываются. За него платят и его передают дальше те, кто им пользуется: разовый взнос от 0,99 $ поддерживает его, и ничто за ним не заперто. Делитесь приложением прямо из него: код, который читает любая камера, со ссылкой на магазин и ничем больше. {SUPPORT}."
    ],
    "support": "Как это устроено"
   }
  ]
 },
 "hi": {
  "title": "यह जो कुछ करता है",
  "desc": "Verdetto की हर सुविधा, उसी क्रम में जिसमें लोग उससे मिलते हैं: पहले लिंक, क्षतिग्रस्त कोड, आपकी अनुमति से खोज, आपके अपने कोड, और कोई विज्ञापन नहीं।",
  "lede": "Verdetto QR कोड और बारकोड पढ़ता है और आपके कुछ करने से पहले दिखाता है कि उनमें क्या है। मुफ़्त, बिना विज्ञापन, कुछ भी एकत्र नहीं। यहाँ सब कुछ है, उसी क्रम में जिसमें अधिकतर लोग इसे पाते हैं।",
  "formats_line": "{N} तरह के कोड, हर एक 4 सितंबर 2026 के सत्यापन रन में मापा गया:",
  "sections": [
   {
    "id": "see",
    "shot": "result-sheet-warning.webp",
    "kicker": "खुलने से पहले",
    "h2": "लिंक खुलने से पहले उसे देखें",
    "alt": "paypa1.com पर ले जाने वाले QR कोड के लिए Verdetto की परिणाम शीट: कुछ भी खुलने से पहले दिखाया गया पता, एक ख़तरा चिप \"paypal.com की नक़ल\", और एक \"फिर भी खोलें\" बटन।",
    "ps": [
     "QR कोड एक ऐसा लिंक है जिसे आप पढ़ नहीं सकते। Verdetto कुछ भी खुलने से पहले पता दिखाता है, उसे आपके फ़ोन पर जाँचता है, और फ़ैसला आप पर छोड़ता है: खोलें, या नहीं।",
     "जाँचें मिलते-जुलते नामों (paypa1.com) को खोजती हैं, छोटे और एफ़िलिएट लिंक को उनके गंतव्य तक फ़ॉलो करती हैं, छिपे लॉगिन, कच्चे IP पते, असामान्य पोर्ट, बिना एन्क्रिप्शन वाले पते, डाउनलोड, स्क्रिप्ट पते और ट्रैकिंग व एफ़िलिएट पैरामीटर पहचानती हैं, और पते की तुलना फ़ोन पर रखी ज्ञात फ़िशिंग, धोखाधड़ी और प्रतिबंध प्रविष्टियों की चेतावनी सूची से करती हैं।",
     "परिणाम एक पंक्ति है: ख़तरा, सावधान, या \"कोई चेतावनी नहीं मिली\"। यह कभी वादा नहीं है कि कुछ सुरक्षित है; खोलना है या नहीं, यह आपका फ़ैसला है। {GUIDE}।"
    ],
    "guide": "लिंक की जाँच खुद कैसे करें"
   },
   {
    "id": "reads",
    "shot": "batch.webp",
    "formats": True,
    "kicker": "क्षतिग्रस्त कोड",
    "h2": "वे कोड पढ़ता है जिन्हें दूसरे ऐप छोड़ देते हैं",
    "alt": "Verdetto की बैच शीट स्कैन होते कोड गिनती हुई, \"पूर्ण\" और \"सूची साझा करें\" के साथ।",
    "ps": [
     "फीके, फटे, ख़राब छपे, तिरछे या उलटे रंग वाले: यह निशाना लगाते हुए पढ़ता है और आपसे स्थिर रहने को कहे बिना फ़्रेम-दर-फ़्रेम कोशिश करता रहता है। एक साथ कई कोड दिख रहे हैं? हर एक की रूपरेखा बनती है और आप उस पर टैप करते हैं जो आपका मतलब था। बैच मोड सबको गिनता है और सत्र को CSV के रूप में निर्यात करता है।"
    ]
   },
   {
    "id": "knows",
    "shot": "wifi.webp",
    "kicker": "कोड क्या है",
    "h2": "जानता है कि कोड क्या है, और एक सही काम करता है",
    "alt": "Verdetto द्वारा पढ़ा गया Wi-Fi नेटवर्क: नेटवर्क का नाम, चेतावनी कि यह खुला और बिना पासवर्ड है, और एक \"जुड़ें\" बटन।",
    "ps": [
     "Wi-Fi कोड एक टैप में नेटवर्क से जोड़ता है। संपर्क कार्ड आपके संपर्कों में जुड़ता है। बोर्डिंग पास गेट पर बड़ा और चमकदार दिखता है। कैलेंडर इवेंट, साइन-इन कोड, स्थान, भुगतान पते, उत्पाद और दवा नंबर, GS1 पैक, वाहन नंबर: हर एक उसी एक कार्रवाई से खुलता है जो उस पर बैठती है, और कुछ भी अपने आप नहीं खुलता।",
     "बोर्डिंग पास, ड्राइविंग लाइसेंस और स्वास्थ्य प्रमाणपत्र फ़ोन पर पढ़े जाते हैं, एक बार दिखाए जाते हैं और कभी नहीं रखे जाते। ऐप कभी किसी व्यक्ति को खोजता नहीं।"
    ]
   },
   {
    "id": "lookups",
    "shot": "vehicle-vin.webp",
    "kicker": "खोज",
    "h2": "चीज़ें खोजता है, केवल तब जब आप अनुमति दें",
    "alt": "Verdetto द्वारा पढ़ा गया VIN: वाहन, मॉडल वर्ष, निर्माता, और एक \"वाहन खोजें\" बटन।",
    "ps": [
     "किसी उत्पाद को स्कैन करें और जानें कि वह क्या है: Open Library और जर्मनी व फ़्रांस की राष्ट्रीय लाइब्रेरियों से किताबें, Open Food Facts से खाद्य और सौंदर्य उत्पाद, openFDA से दवाएँ, MusicBrainz से संगीत, और बाक़ी Wikidata से। किसी वाहन का VIN स्कैन करें: मेक, मॉडल, इंजन, रिकॉल अभियान, क्रैश-टेस्ट रेटिंग और ईंधन दक्षता, अमेरिकी सरकार के NHTSA और EPA डेटाबेस से।",
     "हर स्रोत को केवल नंबर और ऐप का नाम मिलता है, और कुछ नहीं। एक स्विच ऑनलाइन खोज बंद करता है और उत्पाद खोज का अपना स्विच है; ऑनलाइन बंद होने पर फ़ोन से कुछ नहीं जाता और हर अंतर्निर्मित जाँच काम करती रहती है। {PRIVACY}।"
    ],
    "privacy": "गोपनीयता नीति क्या कहती है"
   },
   {
    "id": "create",
    "shot": "create.webp",
    "kicker": "आपके अपने कोड",
    "h2": "अपने कोड बनाएँ",
    "alt": "Verdetto की बनाएँ स्क्रीन: ऊपर आपका कार्ड, फिर वेबसाइट, टेक्स्ट, Wi-Fi, संपर्क, ईमेल, SMS, फ़ोन, स्थान, कैलेंडर और क्लिपबोर्ड।",
    "ps": [
     "वेबसाइट, टेक्स्ट, Wi-Fi, संपर्क, ईमेल, SMS, फ़ोन, स्थान, कैलेंडर, या जो कुछ आपके क्लिपबोर्ड में है: टाइप करें और कोड टाइप करते-करते बनता जाता है। आपका अपना संपर्क कार्ड पहले आता है, लाइव पूर्वावलोकन के साथ। इसे चित्र के रूप में सहेजें, साझा करें या छापें; ऐप अनुमति देने से पहले अपना ही कोड वापस पढ़ता है, ताकि जो आप दें वह स्कैन हो।"
    ]
   },
   {
    "id": "hand",
    "shot": "camera-left.webp",
    "kicker": "हाथ में",
    "h2": "हाथ के लिए बना",
    "alt": "बाएँ हाथ के लेआउट में Verdetto की कैमरा स्क्रीन, नियंत्रण बाईं ओर।",
    "ps": [
     "क्विक सेटिंग्स टाइल शेड से कैमरा खोलती है। फ़ोकस के लिए टैप, ज़ूम के लिए पिंच, कम रोशनी में टॉर्च। बाएँ हाथ का लेआउट हर नियंत्रण को पहुँच में रखता है। परिणाम ज़ोर से पढ़े जा सकते हैं। पढ़ने पर ध्वनि और कंपन, अगर आप चाहें। ग्यारह भाषाएँ। Android 8 और बाद के।"
    ]
   },
   {
    "id": "history",
    "shot": "history.webp",
    "kicker": "आपका इतिहास",
    "h2": "इतिहास जो आपका है",
    "alt": "लिंक, Wi-Fi, बैच और तारांकित फ़िल्टर चिप्स के साथ Verdetto का इतिहास, और उससे फिर खोली गई परिणाम शीट।",
    "ps": [
     "खोजें, तारांकित करें, हटाने के लिए स्वाइप करें, CSV के रूप में निर्यात या आयात करें। 90 दिन से पुराने स्कैन अपने आप हट जाते हैं, जब तक आप उन्हें तारांकित न करें। निजी सत्र कुछ भी नहीं रखता। इतिहास आपके फ़ोन के अपने बैकअप में जाता है, जब तक आप उसे बंद न करें, और अनइंस्टॉल उसे हटा देता है।"
    ]
   },
   {
    "id": "apps",
    "shot": None,
    "kicker": "दूसरे ऐप",
    "h2": "दूसरे ऐप के साथ काम करता है",
    "alt": "",
    "ps": [
     "कोई भी ऐप Verdetto से स्कैन माँग सकता है और कोड वापस पा सकता है, जैसे ऐप ZXing स्कैनर के साथ करते थे। इसमें कोई चित्र साझा करें और यह चित्र के कोड डिकोड कर देता है। {DEV}।"
    ],
    "dev": "डेवलपरों के लिए विवरण"
   },
   {
    "id": "free",
    "shot": None,
    "cta": True,
    "kicker": "सौदा",
    "h2": "मुफ़्त, बिना विज्ञापन, कुछ भी एकत्र नहीं",
    "alt": "",
    "ps": [
     "हर सुविधा सबके लिए मुफ़्त है और रहेगी। न खाते, न एनालिटिक्स, न विज्ञापन, इसलिए न नकली बटन। फ़्रेम डिवाइस पर स्कैन होकर हटा दिए जाते हैं। इसका खर्च वे लोग उठाते हैं जो इसे इस्तेमाल करते हैं और आगे बढ़ाते हैं: $0.99 से एक बार का योगदान इसे चलाए रखता है, और उसके पीछे कुछ भी बंद नहीं है। ऐप को ऐप के भीतर से ही साझा करें: एक कोड जिसे कोई भी कैमरा पढ़ लेता है, जिसमें स्टोर लिंक है और कुछ नहीं। {SUPPORT}।"
    ],
    "support": "यह कैसे काम करता है"
   }
  ]
 },
 "ja": {
  "title": "できることのすべて",
  "desc": "Verdetto のすべての機能を、人が出会う順に: まずリンクを表示、傷んだコード、許可した照会、自分で作るコード、そして広告なし。",
  "lede": "Verdetto は QR コードとバーコードを読み取り、行動する前に中身を見せます。無料、広告なし、何も収集しません。ほとんどの人が出会う順に、そのすべてを。",
  "formats_line": "{N} 種類のコード。いずれも 2026 年 9 月 4 日の検証で測定済み:",
  "sections": [
   {
    "id": "see",
    "shot": "result-sheet-warning.webp",
    "kicker": "開く前に",
    "h2": "開く前にリンクを見る",
    "alt": "paypa1.com へ導く QR コードの Verdetto 結果シート: 何かが開く前に表示されたアドレス、「paypal.com を模倣」と読める危険チップ、「それでも開く」ボタン。",
    "ps": [
     "QR コードは、あなたには読めないリンクです。Verdetto は何かが開く前にアドレスを表示し、端末上で確認し、開くか開かないかの判断をあなたに委ねます。",
     "確認では、見間違えやすい名前（paypa1.com）、行き先までたどる短縮リンクとアフィリエイトリンク、隠れたログイン情報、生の IP アドレス、珍しいポート、暗号化されていないアドレス、ダウンロード、スクリプトのアドレス、追跡とアフィリエイトのパラメーターを探し、端末に保存された既知のフィッシング、詐欺、制裁の警告リストと照らし合わせます。",
     "結果は一行です: 危険、注意、または「警告は見つかりませんでした」。何かが安全だという約束では決してなく、開くかどうかはあなたが決めます。{GUIDE}。"
    ],
    "guide": "リンクを自分で確認する方法"
   },
   {
    "id": "reads",
    "shot": "batch.webp",
    "formats": True,
    "kicker": "傷んだコード",
    "h2": "他のアプリがあきらめるコードを読む",
    "alt": "読み取りながらコードを数える Verdetto の一括シート。「完了」と「リストを共有」付き。",
    "ps": [
     "色あせ、破れ、印刷不良、傾き、色の反転。狙っている間に読み取り、じっとしていてと頼む代わりにフレームをまたいで試し続けます。複数のコードが見えている？ それぞれが枠で囲まれ、意図したものをタップします。一括モードはすべてを数え、セッションを CSV に書き出します。"
    ]
   },
   {
    "id": "knows",
    "shot": "wifi.webp",
    "kicker": "コードの中身",
    "h2": "コードが何かを知り、正しい一つの動作をする",
    "alt": "Verdetto が読み取った Wi-Fi ネットワーク: ネットワーク名、パスワードのない開放ネットワークという注意、「接続」ボタン。",
    "ps": [
     "Wi-Fi のコードは一回のタップでネットワークに接続します。連絡先カードは連絡先に追加されます。搭乗券は搭乗口で大きく明るく表示されます。カレンダーの予定、ログインコード、位置情報、支払い先アドレス、商品や医薬品の番号、GS1 パック、車両番号。それぞれが、ふさわしい一つの動作で開き、勝手に開くものはありません。",
     "搭乗券、運転免許証、健康証明書は端末上で読み取られ、一度表示されるだけで、決して保存されません。アプリが人物を照会することは決してありません。"
    ]
   },
   {
    "id": "lookups",
    "shot": "vehicle-vin.webp",
    "kicker": "照会",
    "h2": "調べるのは、あなたが許可したときだけ",
    "alt": "Verdetto が読み取った VIN: 車両、年式、メーカー、「車両を調べる」ボタン。",
    "ps": [
     "商品を読み取って、それが何かを見る: 本は Open Library とドイツ・フランスの国立図書館、食品と化粧品は Open Food Facts、医薬品は openFDA、音楽は MusicBrainz、その他は Wikidata から。車両の VIN を読み取る: メーカー、モデル、エンジン、リコール、衝突試験の評価、燃費を、米国政府の NHTSA と EPA のデータベースから。",
     "各ソースが受け取るのは番号とアプリ名だけです。スイッチ一つでオンライン照会をオフにでき、商品照会には専用のスイッチがあります。オンラインをオフにすると端末から何も出ず、内蔵の確認はすべて働き続けます。{PRIVACY}。"
    ],
    "privacy": "プライバシーポリシーの内容"
   },
   {
    "id": "create",
    "shot": "create.webp",
    "kicker": "自分のコード",
    "h2": "自分のコードを作る",
    "alt": "Verdetto の作成画面: 上にあなたのカード、続いてウェブサイト、テキスト、Wi-Fi、連絡先、メール、SMS、電話、位置情報、カレンダー、クリップボード。",
    "ps": [
     "ウェブサイト、テキスト、Wi-Fi、連絡先、メール、SMS、電話、位置情報、カレンダー、あるいはクリップボードにあるもの。入力するとコードがその場で現れます。自分の連絡先カードが最初で、ライブプレビュー付き。画像として保存、共有、印刷。アプリは許可する前に自分のコードを読み返すので、渡したものは必ず読み取れます。"
    ]
   },
   {
    "id": "hand",
    "shot": "camera-left.webp",
    "kicker": "手の中で",
    "h2": "手のために作られた",
    "alt": "左手用レイアウトの Verdetto カメラ画面。操作部は左側。",
    "ps": [
     "クイック設定タイルがシェードからカメラを開きます。タップでピント、ピンチでズーム、暗いときはライト。左手用レイアウトはすべての操作部を手の届く場所に置きます。結果は読み上げられます。読み取り時の音と振動は好みで。十一の言語。Android 8 以降。"
    ]
   },
   {
    "id": "history",
    "shot": "history.webp",
    "kicker": "あなたの履歴",
    "h2": "あなたのものである履歴",
    "alt": "リンク、Wi-Fi、一括、スター付きのフィルターチップを持つ Verdetto の履歴と、そこから開き直した結果シート。",
    "ps": [
     "検索し、スターを付け、スワイプで削除し、CSV で書き出し・読み込み。90 日より古い読み取りは、スターを付けなければ自動で消えます。プライベートセッションは何も残しません。履歴は端末自身のバックアップに含まれ（オフにもできます）、アンインストールで消えます。"
    ]
   },
   {
    "id": "apps",
    "shot": None,
    "kicker": "他のアプリ",
    "h2": "他のアプリと連携",
    "alt": "",
    "ps": [
     "どのアプリも Verdetto に読み取りを頼み、コードを受け取れます。ZXing スキャナーに対してアプリがしていたのと同じ方法です。画像を共有すれば、その中のコードを解読します。{DEV}。"
    ],
    "dev": "開発者向けの詳細"
   },
   {
    "id": "free",
    "shot": None,
    "cta": True,
    "kicker": "約束",
    "h2": "無料、広告なし、何も収集しない",
    "alt": "",
    "ps": [
     "すべての機能はすべての人に無料で、これからもそうです。アカウントも、解析も、広告もなく、だから偽のボタンもありません。フレームは端末上で読み取られ、捨てられます。使う人が支払い、伝えていく: 0.99 ドルからの一回限りの支援が続ける力になり、その先に何も隠されていません。アプリの中からアプリを共有できます。どのカメラでも読めるコードで、ストアのリンクだけを運びます。{SUPPORT}。"
    ],
    "support": "その仕組み"
   }
  ]
 },
 "zh-Hans": {
  "title": "它能做的一切",
  "desc": "Verdetto 的每一项功能，按人们遇到的顺序：先看到链接、受损的码、经您允许的查询、您自己制作的码，以及没有广告。",
  "lede": "Verdetto 读取二维码和条形码，并在您行动之前展示其中的内容。免费，无广告，不收集任何信息。这里是全部功能，按大多数人遇到的顺序排列。",
  "formats_line": "{N} 种码，每一种都在 2026 年 9 月 4 日的验证运行中测量过：",
  "sections": [
   {
    "id": "see",
    "shot": "result-sheet-warning.webp",
    "kicker": "打开之前",
    "h2": "在链接打开之前先看到它",
    "alt": "Verdetto 对一个指向 paypa1.com 的二维码的结果面板：在任何内容打开前显示的地址、写着“模仿 paypal.com”的危险标签，以及“仍然打开”按钮。",
    "ps": [
     "二维码是一条您读不出来的链接。Verdetto 在任何内容打开之前显示地址，在您的手机上检查它，并把决定权留给您：打开，或者不打开。",
     "检查会寻找仿冒名称（paypa1.com），跟随短链接和联盟链接直到其去向，识别隐藏的登录信息、裸 IP 地址、异常端口、未加密地址、下载、脚本地址以及追踪和联盟参数，并把地址与保存在手机上的已知钓鱼、诈骗和制裁条目警告列表比对。",
     "结果只有一行：危险、注意，或“未发现警告”。它从不承诺某样东西是安全的；是否打开由您决定。{GUIDE}。"
    ],
    "guide": "如何自己检查链接"
   },
   {
    "id": "reads",
    "shot": "batch.webp",
    "formats": True,
    "kicker": "受损的码",
    "h2": "读取其他应用放弃的码",
    "alt": "Verdetto 的批量面板在扫描时计数，带有“完成”和“分享列表”。",
    "ps": [
     "褪色、撕裂、印刷粗糙、倾斜或反色：它在您对准时就读取，并跨帧持续尝试，而不是要求您保持不动。视野里有多个码？每一个都被框出，您点选想要的那个。批量模式统计全部，并将本次会话导出为 CSV。"
    ]
   },
   {
    "id": "knows",
    "shot": "wifi.webp",
    "kicker": "码是什么",
    "h2": "知道码是什么，并做出唯一正确的动作",
    "alt": "Verdetto 读取的 Wi-Fi 网络：网络名称、提示该网络开放且无密码的注意标签，以及“加入”按钮。",
    "ps": [
     "Wi-Fi 码一键加入网络。联系人名片加入您的联系人。登机牌在登机口以大而亮的方式展示。日历事件、登录码、位置、付款地址、商品和药品编号、GS1 包装、车辆编号：每一种都以恰当的唯一动作打开，没有任何东西会自行打开。",
     "登机牌、驾照和健康证明在手机上读取，只显示一次，绝不保留。应用从不查询任何人。"
    ]
   },
   {
    "id": "lookups",
    "shot": "vehicle-vin.webp",
    "kicker": "查询",
    "h2": "只在您允许时才查询",
    "alt": "Verdetto 读取的 VIN：车辆、车型年份、制造商，以及“查询车辆”按钮。",
    "ps": [
     "扫描一件商品，看看它是什么：书籍来自 Open Library 以及德国和法国国家图书馆，食品和化妆品来自 Open Food Facts，药品来自 openFDA，音乐来自 MusicBrainz，其余来自 Wikidata。扫描车辆的 VIN：品牌、型号、发动机、召回、碰撞测试评级和油耗，来自美国政府的 NHTSA 和 EPA 数据库。",
     "每个来源只收到编号和应用名称，别无其他。一个开关关闭在线查询，商品查询有单独的开关；在线关闭后，没有任何东西离开手机，所有内置检查仍然有效。{PRIVACY}。"
    ],
    "privacy": "隐私政策怎么说"
   },
   {
    "id": "create",
    "shot": "create.webp",
    "kicker": "您自己的码",
    "h2": "制作您自己的码",
    "alt": "Verdetto 的创建界面：顶部是您的名片，然后是网站、文本、Wi-Fi、联系人、电子邮件、短信、电话、位置、日历和剪贴板。",
    "ps": [
     "网站、文本、Wi-Fi、联系人、电子邮件、短信、电话、位置、日历，或剪贴板里的任何内容：边输入，码边生成。您自己的联系人名片排在第一位，带实时预览。保存为图片、分享或打印；应用会先读回自己生成的码再放行，确保您递出去的码能被扫出来。"
    ]
   },
   {
    "id": "hand",
    "shot": "camera-left.webp",
    "kicker": "在手中",
    "h2": "为手而造",
    "alt": "左手布局下的 Verdetto 相机界面，控件在左侧。",
    "ps": [
     "快捷设置磁贴可从通知栏打开相机。点按对焦，双指缩放，光线不足时有手电。左手布局让每个控件都触手可及。结果可以朗读。读取时的声音和振动，随您选择。十一种语言。Android 8 及更高版本。"
    ]
   },
   {
    "id": "history",
    "shot": "history.webp",
    "kicker": "您的历史记录",
    "h2": "属于您的历史记录",
    "alt": "Verdetto 的历史记录，带有链接、Wi-Fi、批量和星标筛选标签，以及从中重新打开的结果面板。",
    "ps": [
     "搜索、加星、滑动删除、导出或导入为 CSV。超过 90 天的扫描记录自动清除，除非您加了星标。私密会话什么都不保留。历史记录随手机自身的备份一起保存，除非您关闭该项；卸载会将其移除。"
    ]
   },
   {
    "id": "apps",
    "shot": None,
    "kicker": "其他应用",
    "h2": "与其他应用协作",
    "alt": "",
    "ps": [
     "任何应用都可以向 Verdetto 请求扫描并取回码，就像应用过去对 ZXing 扫描器所做的那样。把一张图片分享给它，它会解码图片中的码。{DEV}。"
    ],
    "dev": "面向开发者的细节"
   },
   {
    "id": "free",
    "shot": None,
    "cta": True,
    "kicker": "约定",
    "h2": "免费、无广告、不收集任何信息",
    "alt": "",
    "ps": [
     "每一项功能对所有人免费，并将一直免费。没有账户，没有分析统计，没有广告，因此也没有假按钮。画面在设备上扫描后即丢弃。由使用它的人付费并口口相传：一次性支持从 0.99 美元起，让它持续下去，没有任何东西被锁在后面。从应用内分享应用：任何相机都能读的码，只带商店链接，别无其他。{SUPPORT}。"
    ],
    "support": "它是怎么运作的"
   }
  ]
 },
 "ar": {
  "title": "كل ما يفعله",
  "desc": "كل ميزة في Verdetto، بالترتيب الذي يلقاها الناس به: الرابط أولًا، والرموز المتضررة، والبحث الذي تسمح به، ورموزك التي تصنعها، وبلا إعلانات.",
  "lede": "يقرأ Verdetto رموز QR والباركود ويعرض لك ما فيها قبل أن تتصرف. مجاني، بلا إعلانات، لا يجمع شيئًا. هنا كل شيء، بالترتيب الذي يلقاه به معظم الناس.",
  "formats_line": "{N} نوعًا من الرموز، قِيس كل منها في جولة التحقق بتاريخ 4 سبتمبر 2026:",
  "sections": [
   {
    "id": "see",
    "shot": "result-sheet-warning.webp",
    "kicker": "قبل أن يُفتح",
    "h2": "شاهد الرابط قبل أن يُفتح",
    "alt": "ورقة نتيجة Verdetto لرمز QR يقود إلى paypa1.com: العنوان معروض قبل أن يُفتح أي شيء، وشارة خطر بنص «يقلّد paypal.com»، وزر «افتح على أي حال».",
    "ps": [
     "رمز QR رابطٌ لا تستطيع قراءته. يعرض Verdetto العنوان قبل أن يُفتح أي شيء، ويفحصه على هاتفك، ويترك لك القرار: أن تفتح أو لا.",
     "تبحث الفحوص عن الأسماء المشابهة (paypa1.com)، وتتبع الروابط المختصرة وروابط الشركاء إلى وجهتها، وتلتقط بيانات الدخول المخفية، وعناوين IP الخام، والمنافذ غير المعتادة، والعناوين غير المشفّرة، والتنزيلات، وعناوين السكربتات، ومعاملات التعقّب والشراكة، وتقارن العنوان بقائمة تحذير بمدخلات التصيّد والاحتيال والعقوبات المعروفة المحفوظة على الهاتف.",
     "النتيجة سطر واحد: خطر، أو حذر، أو «لم يُعثر على تحذيرات». وهي ليست أبدًا وعدًا بأن شيئًا ما آمن؛ فتح الرابط أو لا قرارك أنت. {GUIDE}."
    ],
    "guide": "كيف تفحص رابطًا بنفسك"
   },
   {
    "id": "reads",
    "shot": "batch.webp",
    "formats": True,
    "kicker": "الرموز المتضررة",
    "h2": "يقرأ الرموز التي تستسلم أمامها التطبيقات الأخرى",
    "alt": "ورقة الدُفعة في Verdetto تعدّ الرموز أثناء مسحها، مع «تم» و«مشاركة القائمة».",
    "ps": [
     "باهتة أو ممزقة أو سيئة الطباعة أو مائلة أو معكوسة الألوان: يقرأ وأنت توجّه الكاميرا ويواصل المحاولة عبر الإطارات بدل أن يطلب منك الثبات. عدة رموز في المشهد؟ يُحاط كلٌّ منها بإطار وتنقر على ما قصدته. ويعدّ وضع الدُفعة كلها ويصدّر الجلسة بصيغة CSV."
    ]
   },
   {
    "id": "knows",
    "shot": "wifi.webp",
    "kicker": "ما هو الرمز",
    "h2": "يعرف ما هو الرمز، ويقوم بالفعل الصحيح الوحيد",
    "alt": "شبكة Wi-Fi قرأها Verdetto: اسم الشبكة، وتحذير من أنها مفتوحة بلا كلمة مرور، وزر «انضم».",
    "ps": [
     "رمز Wi-Fi ينضم إلى الشبكة بنقرة واحدة. بطاقة الاتصال تُضاف إلى جهات اتصالك. بطاقة الصعود تعرض نفسها عند البوابة كبيرة ومضيئة. أحداث التقويم، ورموز الدخول، والمواقع، وعناوين الدفع، وأرقام المنتجات والأدوية، وعبوات GS1، وأرقام المركبات: يُفتح كلٌّ منها بالفعل الوحيد المناسب، ولا يُفتح شيء من تلقاء نفسه.",
     "تُقرأ بطاقات الصعود ورخص القيادة والشهادات الصحية على الهاتف، وتُعرض مرة واحدة، ولا تُحفظ أبدًا. ولا يبحث التطبيق عن شخص أبدًا."
    ]
   },
   {
    "id": "lookups",
    "shot": "vehicle-vin.webp",
    "kicker": "البحث",
    "h2": "يبحث عن المعلومات، فقط حين تسمح",
    "alt": "رقم VIN قرأه Verdetto: المركبة وسنة الطراز والمصنّع وزر «ابحث عن المركبة».",
    "ps": [
     "امسح منتجًا وشاهد ما هو: الكتب من Open Library والمكتبتين الوطنيتين الألمانية والفرنسية، والأغذية ومستحضرات التجميل من Open Food Facts، والأدوية من openFDA، والموسيقى من MusicBrainz، وما تبقّى من Wikidata. امسح رقم VIN لمركبة: الصانع والطراز والمحرك وحملات الاستدعاء وتقييمات اختبارات التصادم واستهلاك الوقود من قاعدتي بيانات NHTSA وEPA التابعتين لحكومة الولايات المتحدة.",
     "يتلقى كل مصدر الرقم واسم التطبيق، لا أكثر. مفتاح واحد يوقف البحث عبر الإنترنت، ولبحث المنتجات مفتاح خاص؛ ومع إيقاف الاتصال لا يخرج شيء من الهاتف وتستمر كل الفحوص المدمجة في العمل. {PRIVACY}."
    ],
    "privacy": "ما تقوله سياسة الخصوصية"
   },
   {
    "id": "create",
    "shot": "create.webp",
    "kicker": "رموزك أنت",
    "h2": "اصنع رموزك أنت",
    "alt": "شاشة الإنشاء في Verdetto: بطاقتك في الأعلى، ثم موقع ويب، ونص، وWi-Fi، وجهة اتصال، وبريد إلكتروني، ورسالة نصية، وهاتف، وموقع، وتقويم، وحافظة.",
    "ps": [
     "موقع ويب، أو نص، أو Wi-Fi، أو جهة اتصال، أو بريد إلكتروني، أو رسالة نصية، أو هاتف، أو موقع، أو تقويم، أو ما في حافظتك: اكتبه ويظهر الرمز وأنت تكتب. بطاقة اتصالك أولًا، مع معاينة حيّة. احفظه صورةً أو شاركه أو اطبعه؛ يقرأ التطبيق رمزه بنفسه قبل أن يسمح لك، كي يُقرأ ما توزّعه."
    ]
   },
   {
    "id": "hand",
    "shot": "camera-left.webp",
    "kicker": "في اليد",
    "h2": "مصنوع لليد",
    "alt": "شاشة كاميرا Verdetto في تخطيط اليد اليسرى، وعناصر التحكم على اليسار.",
    "ps": [
     "بلاطة في الإعدادات السريعة تفتح الكاميرا من الظِّل. انقر للتركيز، وقرّب بإصبعين، ومصباح حين يخفت الضوء. تخطيط لليد اليسرى يضع كل عنصر تحكم في المتناول. يمكن قراءة النتائج بصوت عالٍ. صوت واهتزاز عند القراءة إن أردت. إحدى عشرة لغة. Android 8 وما بعده."
    ]
   },
   {
    "id": "history",
    "shot": "history.webp",
    "kicker": "سجلّك",
    "h2": "سجلٌّ يخصّك",
    "alt": "سجل Verdetto مع شارات تصفية للروابط وWi-Fi والدُفعات والمميّز بنجمة، وورقة نتيجة أُعيد فتحها منه.",
    "ps": [
     "ابحث فيه، وميّز بنجمة، واسحب للحذف، وصدّره أو استورده بصيغة CSV. عمليات المسح الأقدم من 90 يومًا تُمحى من تلقاء نفسها ما لم تميّزها بنجمة. الجلسة الخاصة لا تحفظ شيئًا على الإطلاق. ينتقل السجل مع النسخة الاحتياطية لهاتفك ما لم توقف ذلك، وإزالة التطبيق تحذفه."
    ]
   },
   {
    "id": "apps",
    "shot": None,
    "kicker": "التطبيقات الأخرى",
    "h2": "يعمل مع التطبيقات الأخرى",
    "alt": "",
    "ps": [
     "يمكن لأي تطبيق أن يطلب من Verdetto مسحًا ويستلم الرمز، كما كانت التطبيقات تفعل مع ماسح ZXing. شارك معه صورة فيفكّ الرموز التي فيها. {DEV}."
    ],
    "dev": "التفاصيل للمطوّرين"
   },
   {
    "id": "free",
    "shot": None,
    "cta": True,
    "kicker": "الاتفاق",
    "h2": "مجاني، بلا إعلانات، لا يجمع شيئًا",
    "alt": "",
    "ps": [
     "كل ميزة مجانية للجميع وستبقى كذلك. لا حسابات ولا تحليلات ولا إعلانات، وبالتالي لا أزرار زائفة. تُمسح الإطارات على الجهاز ثم تُهمَل. يدفع ثمنه ويمرّره من يستخدمونه: مساهمة لمرة واحدة من 0.99 دولار تُبقيه مستمرًا، ولا شيء مقفل خلفها. شارك التطبيق من داخله: رمز تقرأه أي كاميرا، يحمل رابط المتجر ولا شيء غيره. {SUPPORT}."
    ],
    "support": "كيف يعمل ذلك"
   }
  ]
 }
}


def features_body(t, code):
    """The features page from its strings table: a hero line, then one section per job with an overline kicker, a
    title-large heading, the claim, optional format chips, and one screenshot in the site's phone frame."""
    def link(page, label):
        return f'<a href="{href(localized(page, code))}">{label}</a>'
    out = [f'<div class="hero"><div><h1>{t["title"]}</h1><p>{t["lede"]}</p></div></div>']
    for sec in t["sections"]:
        ps = []
        for x in sec["ps"]:
            x = (x.replace("{GUIDE}", link("check-qr-code-link.html", sec.get("guide", "")))
                  .replace("{PRIVACY}", link("privacy.html", sec.get("privacy", "")))
                  .replace("{DEV}", link("developers.html", sec.get("dev", "")))
                  .replace("{SUPPORT}", link("support-the-work.html", sec.get("support", ""))))
            ps.append(f'<p>{x}</p>')
        if sec.get("formats"):
            ps.append(f'<p>{t["formats_line"].replace("{N}", str(len(FORMATS_READ)))}</p>')
            ps.append('<ul class="tags">' + ''.join(f'<li>{f}</li>' for f in FORMATS_READ) + '</ul>')
        if sec.get("cta"):
            ps.append(f'<span class="label">{ic("clock")}{HOME_T[code]["coming"]}</span>')
        shot = (f'<img class="shot" src="screens/{sec["shot"]}" width="540" height="1140" alt="{sec["alt"]}" loading="lazy">' if sec["shot"] else '')
        cls = 'feature' if sec["shot"] else 'feature text'
        out.append(f'<section class="{cls}" id="{sec["id"]}"><div><p class="kicker">{sec["kicker"]}</p><h2>{sec["h2"]}</h2>{"".join(ps)}</div>{shot}</section>')
    return "\n" + "\n".join(out) + "\n"


LOCAL["features.html"] = {code: page for code, page in family_pages("features.html").items() if code in FEAT_T}


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
LOCAL["index.html"] = {code: page for code, _, page in HOME_LANGS}
for _t in HOME_T.values():
    assert len(_t["desc"]) <= 160, _t["desc"]


def home_body(t, code):
    """The home page from one strings table; links to the policies in the same language, the rest of the site in English."""
    privacy_page = next(p for c, _, p in PRIVACY_LANGS if c == code)
    link = lambda page, label: f'<a href="{href(localized(page, code))}">{label}</a>'
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
<p class="meta"><a href="{href(localized("features.html", code))}">{chrome(code)["features"]}: {FEAT_T[code]["title"]}</a></p>
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
    "support-the-work.html": (SUPPORT_WORK_T["en"]["title"], support_work_desc(SUPPORT_WORK_T["en"]), SUPPORT_WORK, SUPPORT_WORK_LD),
    "check-qr-code-link.html": (GUIDE_TITLE + " - Verdetto", GUIDE_DESC, GUIDE, GUIDE_LD),
    "report.html": ("Report to Verdetto", "Report a scam-looking link, a code the app read wrong, or anything else that isn't right in Verdetto: QR & Barcode Scanner. A person reviews every report.", REPORT, {"@type": "WebPage", "name": "Report to Verdetto", "publisher": ORG}),
    "press.html": ("Press kit - Verdetto", "The one-sentence description, boilerplate, checkable facts, and image assets for writing about Verdetto: QR & Barcode Scanner.", PRESS, {"@type": "WebPage", "name": "Press kit", "publisher": ORG}),
    "safety-list.html": ("The safety list this week - Verdetto", "Weekly numbers from Verdetto's public warning list: reports, cases, entries added after review, removals, totals. Public data only, nothing from anyone's phone.", weekly_page(), WEEKLY_LD),
    "developers.html": ("For developers - Verdetto", "How another Android app opens Verdetto to scan and gets the code back: the intents, the result extras, Kotlin and Java, and what the person sees.", developers_page(), DEVELOPERS_LD),
    "community-license.html": (COMMUNITY_TITLE, COMMUNITY_DESC, COMMUNITY, {"@type": "WebPage", "name": "Verdetto Community License", "publisher": ORG}),
    "404.html": ("Page not found - Verdetto", "That page is not here.", not_found(), None),
}
PAGE_LANG = {}  # name -> (lang, rtl, alternates) for pages that are not plain English
PAGE_LANG["privacy.html"] = ("en", False, PRIVACY_ALTERNATES)
PAGE_LANG["terms.html"] = ("en", False, TERMS_ALTERNATES)
PAGE_LANG["community-license.html"] = ("en", False, COMMUNITY_ALTERNATES)
for _langs, _alternates, _translate in ((PRIVACY_LANGS, PRIVACY_ALTERNATES, privacy_translation), (TERMS_LANGS, TERMS_ALTERNATES, terms_translation),
                                        (COMMUNITY_LANGS, COMMUNITY_ALTERNATES, community_translation)):
    for _code, _label, _page_name in _langs[1:]:
        _title, _desc, _body = _translate(_code)
        PAGES[_page_name] = (_title, _desc, _body, {"@type": "WebPage", "name": _title.split(" - ")[0], "publisher": ORG, "inLanguage": _code})
        PAGE_LANG[_page_name] = (_code, _code == "ar", _alternates)
PAGE_LANG["index.html"] = ("en", False, HOME_ALTERNATES)
for _code, _label, _page in HOME_LANGS[1:]:
    _t = HOME_T[_code]
    PAGES[_page] = (_t["title"], _t["desc"], home_body(_t, _code), {**APP, "inLanguage": _code})
    PAGE_LANG[_page] = (_code, _code == "ar", HOME_ALTERNATES)
PAGE_LANG["support.html"] = ("en", False, alternates_for("support.html"))
for _code in LANG_CODES[1:]:
    _t = SUPPORT_T[_code]
    _pg = LOCAL["support.html"][_code]
    PAGES[_pg] = (_t["title"], _t["desc"], support_body(_t, _code), faq_ld(_t, _code))
    PAGE_LANG[_pg] = (_code, _code == "ar", alternates_for("support.html"))
PAGE_LANG["support-the-work.html"] = ("en", False, alternates_for("support-the-work.html"))
for _code in LANG_CODES[1:]:
    _t = SUPPORT_WORK_T[_code]
    _pg = LOCAL["support-the-work.html"][_code]
    PAGES[_pg] = (_t["title"], support_work_desc(_t), support_work_body(_t, _code), support_work_ld(_t, _code))
    PAGE_LANG[_pg] = (_code, _code == "ar", alternates_for("support-the-work.html"))
PAGE_LANG["check-qr-code-link.html"] = ("en", False, alternates_for("check-qr-code-link.html"))
for _code in LANG_CODES[1:]:
    _t = GUIDE_T[_code]
    _pg = LOCAL["check-qr-code-link.html"][_code]
    PAGES[_pg] = (_t["title"] + " - Verdetto", _t["desc"], guide_body(_t, _code), guide_ld(_t, _code))
    PAGE_LANG[_pg] = (_code, _code == "ar", alternates_for("check-qr-code-link.html"))
PAGE_LANG["press.html"] = ("en", False, alternates_for("press.html"))
for _code in LANG_CODES[1:]:
    _t = PRESS_T[_code]
    _pg = LOCAL["press.html"][_code]
    PAGES[_pg] = (_t["title"] + " - Verdetto", _t["desc"], press_body(_t, _code), press_ld(_t, _code))
    PAGE_LANG[_pg] = (_code, _code == "ar", alternates_for("press.html"))
PAGE_LANG["report.html"] = ("en", False, alternates_for("report.html"))
PAGE_LANG["safety-list.html"] = ("en", False, alternates_for("safety-list.html"))
PAGE_LANG["developers.html"] = ("en", False, alternates_for("developers.html"))
for _code in LANG_CODES[1:]:
    _t, _pg = REPORT_T[_code], LOCAL["report.html"][_code]
    PAGES[_pg] = (_t["title"], _t["desc"], report_body(_t, _code), {"@type": "WebPage", "name": _t["title"], "publisher": ORG, "inLanguage": _code})
    PAGE_LANG[_pg] = (_code, _code == "ar", alternates_for("report.html"))
    _t, _pg = WEEKLY_T[_code], LOCAL["safety-list.html"][_code]
    PAGES[_pg] = (_t["title"] + " - Verdetto", _t["desc"], weekly_body(_t, _code), weekly_ld(_t, _code))
    PAGE_LANG[_pg] = (_code, _code == "ar", alternates_for("safety-list.html"))
    _t, _pg = DEV_T[_code], LOCAL["developers.html"][_code]
    PAGES[_pg] = (_t["title"] + " - Verdetto", _t["desc"], dev_body(_t, _code), dev_ld(_t, _code))
    PAGE_LANG[_pg] = (_code, _code == "ar", alternates_for("developers.html"))
PAGES["features.html"] = (FEAT_T["en"]["title"] + " - Verdetto", FEAT_T["en"]["desc"], features_body(FEAT_T["en"], "en"),
                          {"@type": "WebPage", "name": FEAT_T["en"]["title"], "publisher": ORG})
for _code in LANG_CODES[1:]:
    if _code in FEAT_T:
        _t, _pg = FEAT_T[_code], LOCAL["features.html"][_code]
        PAGES[_pg] = (_t["title"] + " - Verdetto", _t["desc"], features_body(_t, _code), {"@type": "WebPage", "name": _t["title"], "publisher": ORG, "inLanguage": _code})
        PAGE_LANG[_pg] = (_code, _code == "ar", alternates_for("features.html"))
if len(FEAT_T) > 1:
    PAGE_LANG["features.html"] = ("en", False, alternates_for("features.html"))
BENCH_PUBLISHED = False  # True once the benchmark page is cleared for the live site


def main():
    if BENCH_PUBLISHED:
        import bench
        PAGES["how-we-test.html"] = bench.page_entry()
        NAV.append(("how-we-test.html", "tests"))
    for name, (title, desc, body, ld) in PAGES.items():
        lang, rtl, alternates = PAGE_LANG.get(name, ("en", False, None))
        html = page(name, title.replace("&", "&amp;"), desc.replace("&", "&amp;"), body, ld, "article" if name.startswith("check") else "website",
                    lang=lang, rtl=rtl, alternates=alternates)
        (HERE / name).write_text(html, encoding="utf-8", newline="\n")
        print("wrote", name)
        if name.startswith(("privacy", "terms")):
            dated_copy(name, html)

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
