"""Build the verdettoqr.com pages: one header, footer, and stylesheet, the
logo and card icons inlined as SVG symbols, so every page is self-contained:
no scripts run, nothing loads from another host. Run assets.py first, then
python build.py. Flip PUBLISH and DRAFT at publication."""
import json
import re
from pathlib import Path

HERE = Path(__file__).parent
DRAFT = False       # True while drafting: shows the review banner
PUBLISH = True      # True at publication: clean URLs in links (GitHub Pages serves /privacy for privacy.html)
SITE = "https://verdettoqr.com"
DATE = "2026-09-03"  # lastmod for the sitemap and the article; update when copy changes
ADDRESS = "1520 Belle View Blvd, Suite #5992, Alexandria, VA 22307"
EMAIL = "support@verdettoqr.com"

svg = (HERE / "logo.svg").read_text(encoding="utf-8")
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
}
SYMBOLS = ('<svg width="0" height="0" style="position:absolute" aria-hidden="true">'
           f'<symbol id="logo" viewBox="0 0 108 108">{inner}</symbol>'
           + "".join(f'<symbol id="ic-{k}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">{v}</symbol>' for k, v in ICONS.items())
           + "</svg>")

CSS = """
/* Material 3 color roles, copied from the app's Theme.kt so the site and the app are one palette. */
:root{--surface:#E9F5F1;--on-surface:#191C1B;--on-surface-variant:#3F4946;--primary:#006B5E;--on-primary:#FFFFFF;--surface-container:#D5E8E3;--surface-container-high:#CFE2DC;--outline:#6F7977;--outline-variant:#B4CAC4;--tertiary:#8A5A00;--on-tertiary:#FFFFFF}
@media (prefers-color-scheme:dark){:root{--surface:#0F1312;--on-surface:#DFE4E1;--on-surface-variant:#BEC9C5;--primary:#54DBC8;--on-primary:#003731;--surface-container:#1C201F;--surface-container-high:#262B29;--outline:#899390;--outline-variant:#3F4946;--tertiary:#FFB95A;--on-tertiary:#462A00}}
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
.skip{position:absolute;left:-999px;top:0;background:var(--primary);color:var(--on-primary);padding:.5rem 1rem;border-radius:0 0 8px 0;z-index:2}
.skip:focus{left:0}
.wrap{max-width:44rem;margin:0 auto;padding:0 1rem}
.draft{background:var(--tertiary);color:var(--on-tertiary);text-align:center;padding:.4rem;font-size:.875rem;line-height:1.25rem;font-weight:500;letter-spacing:.01em}
header{border-bottom:1px solid var(--outline-variant)}
header .wrap{display:flex;align-items:center;gap:.75rem;min-height:64px;padding-top:.5rem;padding-bottom:.5rem;flex-wrap:wrap}
.brand{display:flex;align-items:center;gap:.75rem;color:var(--on-surface);text-decoration:none;font-weight:500;font-size:1.375rem;line-height:1.75rem}
.brand svg{width:40px;height:40px}
nav{margin-left:auto;display:flex;gap:.25rem;flex-wrap:wrap}
nav a{color:var(--on-surface-variant);text-decoration:none;font-weight:500;font-size:.875rem;line-height:1.25rem;padding:.6rem .75rem;border-radius:20px}
nav a:hover{background:var(--surface-container)}
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
.hero h1{margin:.25rem 0 .5rem}
.hero p{font-size:1.125rem;line-height:1.75rem;margin:0}
.hero .label{display:inline-flex;align-items:center;gap:.4rem;margin-top:1rem;color:var(--on-surface-variant);font-weight:500;font-size:.875rem;line-height:1.25rem}
.hero .label svg{width:18px;height:18px}
.shot{width:250px;height:auto;border-radius:20px;border:1px solid var(--outline-variant);background:var(--surface-container);display:block}
.grid{display:grid;grid-template-columns:1fr;gap:.75rem;margin:1rem 0}
.grid .card{margin:0;display:grid;grid-template-columns:auto 1fr;gap:.75rem;align-items:start}
.grid .card svg{width:24px;height:24px;color:var(--primary);margin-top:.15rem}
.grid h3{margin:0 0 .25rem;color:var(--on-surface)}
.grid p{margin:0;font-size:.875rem;line-height:1.25rem;color:var(--on-surface-variant)}
.callout{background:var(--surface-container-high);border-left:4px solid var(--primary);border-radius:0 12px 12px 0}
.faq p strong{color:var(--on-surface);font-weight:500}
.prose ol,.prose ul{padding-left:1.4rem}
.prose li{margin:.6rem 0}
footer{background:var(--surface-container);margin-top:2rem}
footer .wrap{padding:1.5rem 1rem 2rem;color:var(--on-surface-variant);font-size:.875rem;line-height:1.25rem}
footer a{color:var(--primary)}
@media (min-width:640px){.grid{grid-template-columns:1fr 1fr}}
@media (max-width:600px){.hero{grid-template-columns:1fr}.shot{width:220px;margin:0 auto}h1{font-size:1.75rem;line-height:2.25rem}nav{margin-left:0;width:100%}}
@media print{.draft,.skip,nav,footer .links{display:none}body{background:#fff;color:#000;font-size:12pt}a{color:#000}h2{color:#000;border-top-color:#999}.card,.callout{background:#f2f2f2}}
"""


def href(name):
    if not PUBLISH:
        return name
    return "/" if name == "index.html" else "/" + name[:-5]


def url(name):
    return SITE + ("/" if name == "index.html" else "/" + name[:-5])


NAV = (("privacy.html", "Privacy"), ("terms.html", "Terms"), ("support.html", "Support"), ("check-qr-code-link.html", "Guide"))

ORG = {"@type": "Organization", "name": "Verdetto", "url": SITE + "/", "email": EMAIL, "logo": SITE + "/icon-512.png",
       "address": {"@type": "PostalAddress", "streetAddress": "1520 Belle View Blvd, Suite #5992", "addressLocality": "Alexandria",
                   "addressRegion": "VA", "postalCode": "22307", "addressCountry": "US"}}
APP = {"@type": "SoftwareApplication", "name": "Verdetto: QR & Barcode Scanner", "operatingSystem": "Android",
       "applicationCategory": "UtilitiesApplication", "url": SITE + "/", "image": SITE + "/icon-512.png",
       "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD"}, "publisher": ORG,
       "description": "A QR and barcode scanner for Android. No ads, no fake buttons. See the link before it opens. Reads damaged codes."}


def page(name, title, description, body, ld=None, og_type="website", nav_key=None):
    nav = "".join(f'<a href="{href(h)}"{" aria-current=\"page\"" if h == name else ""}>{t}</a>' for h, t in NAV)
    banner = '<div class="draft" role="status">Draft for review. Not published.</div>\n' if DRAFT else ""
    ld_tag = f'<script type="application/ld+json">{json.dumps({"@context": "https://schema.org", **ld}, ensure_ascii=False)}</script>\n' if ld else ""
    canonical = url(name) if name != "404.html" else SITE + "/404"
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; img-src 'self' data:; font-src 'self'; base-uri 'none'; form-action 'none'">
<title>{title}</title>
<meta name="description" content="{description}">
<link rel="canonical" href="{canonical}">
<meta name="theme-color" media="(prefers-color-scheme: light)" content="#E9F5F1">
<meta name="theme-color" media="(prefers-color-scheme: dark)" content="#0F1312">
<link rel="icon" href="{href('icon.svg') if PUBLISH else 'icon.svg'}" type="image/svg+xml">
<link rel="icon" href="favicon-32.png" sizes="32x32" type="image/png">
<link rel="apple-touch-icon" href="apple-touch-icon.png">
<meta property="og:type" content="{og_type}">
<meta property="og:site_name" content="Verdetto">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{description}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{SITE}/og-image.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="Verdetto icon with the words QR &amp; Barcode Scanner for Android, See the link before it opens.">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{title}">
<meta name="twitter:description" content="{description}">
<meta name="twitter:image" content="{SITE}/og-image.png">
{ld_tag}<style>{CSS}</style>
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
{banner}{SYMBOLS}
<header><div class="wrap">
  <a class="brand" href="{href('index.html')}"><svg aria-hidden="true"><use href="#logo"/></svg>Verdetto</a>
  <nav aria-label="Site">{nav}</nav>
</div></header>
<main id="main"><div class="wrap">
{body}
</div></main>
<footer><div class="wrap">
  <p>&copy; 2026 Verdetto &middot; {ADDRESS} &middot; <a href="mailto:{EMAIL}">{EMAIL}</a></p>
  <p class="links"><a href="{href('privacy.html')}">Privacy policy</a> &middot; <a href="{href('terms.html')}">Terms of use</a> &middot; <a href="{href('support.html')}">Support</a> &middot; <a href="{href('check-qr-code-link.html')}">How to check a QR code link</a></p>
</div></footer>
</body>
</html>
"""


def ic(k):
    return f'<svg aria-hidden="true"><use href="#ic-{k}"/></svg>'


HOME = f"""
<div class="hero">
  <div>
    <svg class="mark" role="img" aria-label="Verdetto icon"><use href="#logo"/></svg>
    <h1>See the link before it opens.</h1>
    <p>Verdetto is a QR code and barcode scanner for Android with no ads and no fake buttons. It reads damaged codes, shows you exactly what a code contains, and checks it for warning signs on your phone before you act on it.</p>
    <span class="label">{ic('clock')}Coming soon to Google Play</span>
  </div>
  <img class="shot" src="screens/result-sheet.webp" width="540" height="1140" alt="The Verdetto result sheet showing a scanned QR code that leads to wikipedia.org, the No warnings found chip, and an Open button that names the site.">
</div>

<h2>What it does</h2>
<div class="grid">
  <div class="card">{ic('scan')}<div><h3>Reads damaged codes</h3><p>QR codes and barcodes: EAN, UPC, Code 128, Data Matrix, PDF417, Aztec, and more, including faded, torn, and poorly printed ones.</p></div></div>
  <div class="card">{ic('eye')}<div><h3>Look before it opens</h3><p>Shows you the link, network, contact, event, or product first. Nothing opens by itself unless you turn that on.</p></div></div>
  <div class="card">{ic('warning')}<div><h3>Warning signs, on the phone</h3><p>Hidden sign-in details, lookalike names, shortened links, unencrypted addresses, app downloads, premium-rate numbers, open Wi-Fi, and more.</p></div></div>
  <div class="card">{ic('shield')}<div><h3>Known threats list</h3><p>Links, sites, and wallet addresses are compared with a list of known phishing, malware, and scam entries kept on your phone.</p></div></div>
  <div class="card">{ic('barcode')}<div><h3>Product lookup</h3><p>Barcode numbers go to Open Food Facts and Open Library for product details when online lookups are on.</p></div></div>
  <div class="card">{ic('history')}<div><h3>History that is yours</h3><p>Every scan stays on your phone: searchable, starrable, deletable with a swipe.</p></div></div>
  <div class="card">{ic('offline')}<div><h3>Works offline</h3><p>Scanning and every check run on the phone. Online lookups are optional and one switch away.</p></div></div>
  <div class="card">{ic('heart')}<div><h3>Free, no ads</h3><p>Everything is free. An optional contribution supports development, and nothing is locked behind it.</p></div></div>
</div>

<h2>Why another QR scanner</h2>
<p>Most free QR code scanners on Android are ad-supported, and many put a fake "scan" or "open" button where the ad should be. Verdetto has no ads, so it has nothing to hide behind. Most scanners open a link the moment they read it. Verdetto shows you the link first, in full, with the site name on the button, so you decide. And most scanners give up on a torn sticker or a faded receipt; Verdetto is built to read damaged codes, because that is when the content matters most.</p>

<h2>What it will never tell you</h2>
<div class="card callout"><p>That something is safe. Verdetto tells you what it checked and what it found. "No warnings found" means none of its checks matched, and the decision to open, join, or dial is always yours. If you want to know what to look for yourself, read <a href="{href('check-qr-code-link.html')}">how to check a QR code link before you open it</a>.</p></div>
"""

PRIVACY = f"""
<h1>Privacy policy</h1>
<p class="meta">For Verdetto: QR &amp; Barcode Scanner, the Android app published by Verdetto. Effective date: September 3, 2026.</p>

<div class="card"><p><strong>In short.</strong> The app has no accounts, no ads, and no analytics. Scanning happens on your phone. When online lookups are on, which is the default, only the address, domain, or product number you scanned goes to the services named below. Nothing else leaves the phone, and we do not collect, store, or sell any data about you. This website sets no cookies.</p></div>

<h2>Who we are</h2>
<p>Verdetto, {ADDRESS}, United States. Contact: <a href="mailto:{EMAIL}">{EMAIL}</a>.</p>

<h2>What the app does on your phone</h2>
<ul>
  <li><strong>Camera.</strong> Camera frames are read on the phone to find and decode codes. They are not stored and not uploaded.</li>
  <li><strong>Images you choose.</strong> If you pick an image from your photos, it is read on the phone the same way and is not uploaded.</li>
  <li><strong>Scan history.</strong> Decoded content is kept in a history on your phone so you can find it again. You can delete any entry, or clear the whole history, in the app.</li>
  <li><strong>Safety checks.</strong> The app inspects scanned content on the phone for warning signs and compares links, sites, and wallet addresses with a list of known phishing, malware, and scam entries that is stored on the phone. The comparison never sends what you scanned anywhere.</li>
  <li><strong>Settings.</strong> Your preferences are stored on the phone.</li>
</ul>

<h2>What leaves the phone, and when</h2>
<p>Online lookups are on by default and can be turned off in Settings. While they are on, the app may make these requests. Each carries only what is listed, plus your phone's internet address, which every internet request carries.</p>
<ul>
  <li><strong>Warning-list updates.</strong> The app downloads a newer copy of the warning list, at most once a day, from where we publish it. The request carries no scanned content. The app checks the list's signature before using it.</li>
  <li><strong>Shortened links.</strong> To show you where a shortened link leads, the app asks the shortening service for its destination. That service sees the request the way it would see any visit to the short link. The destination page itself is not opened or inspected.</li>
  <li><strong>Domain age.</strong> To tell you when a link's domain was registered, the app sends the domain name to the domain's registry.</li>
  <li><strong>Product numbers.</strong> To show product details, the app sends the barcode number to Open Food Facts or its sister databases (Open Beauty Facts, Open Pet Food Facts, Open Products Facts), or an ISBN to Open Library. Their answers are shown as given.</li>
</ul>
<p>These services are run by others and have their own privacy policies. With online lookups off, nothing leaves the phone.</p>

<h2>What never leaves the phone</h2>
<p>Your scan history. The pages behind links, which the app never opens or inspects. Wi-Fi passwords, contacts, and calendar entries you scan. Anything about you.</p>

<h2>Permissions</h2>
<p>The app asks for the camera, which it needs to scan. It needs no other permission. Network access is used only for the lookups described above. Joining a Wi-Fi network, adding a contact, or saving an event goes through the standard Android prompt for that action, and only when you choose it.</p>

<h2>Purchases</h2>
<p>The optional contribution inside the app is processed by Google Play. Google handles the payment under its own policy; the app receives only a confirmation that the purchase went through. We never see your payment details.</p>

<h2>Children</h2>
<p>The app is not directed at children under 13 and collects no data from anyone.</p>

<h2>Keeping and deleting data</h2>
<p>Everything the app keeps is on your phone. Delete history entries in the app, or uninstall the app to remove all of it. We hold no data about you, so there is nothing for us to delete or hand over.</p>

<h2>This website</h2>
<p>These pages are static. They set no cookies, run no analytics, have no forms, and load nothing from anywhere but this site. Our hosting provider may keep standard server logs, such as the address a page was requested from and when, under its own policy.</p>

<h2>Changes</h2>
<p>If this policy changes, the new version will be posted here with a new effective date.</p>

<h2>Contact</h2>
<p>Questions about privacy: <a href="mailto:{EMAIL}">{EMAIL}</a>.</p>
"""

TERMS = f"""
<h1>Terms of use</h1>
<p class="meta">For Verdetto: QR &amp; Barcode Scanner. Last updated: September 3, 2026.</p>

<div class="card"><p><strong>In short.</strong> The app looks at what a code contains and tells you what it found. It never says anything is safe. Whether to open, join, dial, or act on scanned content is your decision. These are the same terms shown inside the app; if the two ever differ, the installed version applies.</p></div>

<h2>The app</h2>
<p>This app is free and open source. It is provided as is and as available, without warranty of any kind, express or implied, including fitness for a particular purpose. It is not security software and not a substitute for security advice.</p>

<h2>What the safety checks are</h2>
<p>When you scan a code, the app looks at the content itself, on your phone, for known warning signs: hidden sign-in details, raw IP addresses, lookalike or imitation names, shortened links, unencrypted addresses, unusual ports, app or program downloads, unusually deep subdomains, script or file addresses, tracking parameters, premium-rate numbers, open Wi-Fi networks, and payment destinations. It also compares links, sites, and wallet addresses with a list of known phishing, malware, and scam entries kept on the phone, compiled from public sources (PhishTank, the CERT Polska warning list, PhishDestroy, PhishIndex, and the polkadot-js phishing list). If you turn on online lookups, the app can download a newer list, follow a shortened link to where it leads, ask a domain's registry when it was registered, and send a product number to Open Food Facts, its sister databases, or Open Library. Their answers are shown as given.</p>

<h2>What they are not</h2>
<p>The checks do not open or inspect the page behind a link, cannot see what a network, contact, calendar entry, or product will do, and cannot catch every scam, unsafe site, or harmful code. "No warnings found" means none of the app's checks matched. It is never a statement that anything is safe, genuine, or trustworthy.</p>

<h2>Your decisions</h2>
<p>Whether to open a link, join a network, add a contact or event, dial a number, or act on any scanned content is your decision, made at your own risk. Automatic opening, when you turn it on, opens links you have not looked at; you accept that when you turn it on.</p>

<h2>Liability</h2>
<p>To the fullest extent permitted by law, the developers and contributors of this app are not liable for any loss, damage, or harm arising from the use of the app or from acting on scanned content, including opening a link, joining a network, or relying on a check or a lookup.</p>

<h2>Your data</h2>
<p>Online lookups are on by default and can be turned off in Settings. While on, only the address, domain, or product number goes to the named services; with them off, nothing leaves the phone. There are no ads, no analytics, and no accounts. The <a href="{href('privacy.html')}">privacy policy</a> has the details.</p>

<h2>Changes</h2>
<p>These terms may change with a new version of the app. The text in the installed version is the one that applies.</p>
"""

FAQ = [
    ("It said \"No warnings found.\" Is the link safe?",
     "The app does not know, and it never says something is safe. \"No warnings found\" means none of its checks matched. Look at the address it shows you, and open it only if you would have opened it anyway."),
    ("Does it work offline?",
     "Yes. Scanning and every safety check run on the phone. Online lookups add product details, link destinations, and domain age when you have a connection, and can be turned off in Settings."),
    ("Why does it ask for the camera?", "To scan. It is the only permission the app asks for."),
    ("How do I turn off online lookups?", "Settings, then Allow online lookups. With them off, nothing leaves the phone."),
    ("How do I delete my history?", "Swipe an entry left, or use Clear history in Settings. History lives only on your phone; uninstalling the app removes it too."),
    ("A code will not scan.",
     "Fill more of the screen with it, hold still, and let the camera focus. Damaged or faded codes take a moment longer. If it still will not read, send us a photo of the code if it is not sensitive."),
    ("What does the contribution unlock?",
     "Nothing. Every feature is free. The contribution supports development, and you can hide the supporter badge if you prefer."),
]
SUPPORT = f"""
<h1>Support</h1>
<div class="card"><p>Write to <a href="mailto:{EMAIL}">{EMAIL}</a>. It helps to include your phone model, your Android version, and what you were scanning if you can share it. Never send sign-in details or a code that contains them.</p></div>

<h2>Common questions</h2>
<div class="faq">
""" + "\n".join(f"<p><strong>{q}</strong><br>\n{a}</p>\n" for q, a in FAQ) + f"""
</div>
<p>Not sure what to look for in a link? Read <a href="{href('check-qr-code-link.html')}">how to check a QR code link before you open it</a>.</p>
"""
FAQ_LD = {"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in FAQ]}

GUIDE_TITLE = "How to check a QR code link before you open it"
GUIDE_DESC = "Six things to look at in a QR code's link before you tap it: the domain, shortened links, lookalike names, the connection, downloads, and where the code was placed."
GUIDE = f"""
<div class="prose">
<h1>{GUIDE_TITLE}</h1>
<p class="meta">Updated {DATE}. About a four-minute read.</p>

<div class="card"><p><strong>In short.</strong> Before you open a link from a QR code: read the domain, not the whole address; treat shortened links as unknown until they are expanded; look for lookalike names; check for <code>https</code> and no unusual port; never install anything a code hands you; and ask why the code is where it is. A scanner can show you all of that. It cannot tell you a page is safe.</p></div>

<p>A QR code is just a way of typing a link so you do not have to. The trouble is that the link is invisible until something reads it, and most scanner apps open it the instant they do. Fake codes on parking meters, restaurant tables, posters, and even in emails rely on exactly that. The fix is simple: look at the link before you open it. Here is what to look at, in order.</p>

<h2>1. Read the domain, not the whole link</h2>
<p>The domain is the part after <code>https://</code> and before the first single slash. In <code>https://accounts.example.com/login?ref=qr</code> the domain is <code>accounts.example.com</code>, and the part that matters most is the last two labels, <code>example.com</code>. Everything after the slash can say anything; it is the domain that decides where you land. A good scanner shows the domain by itself in large type, so you do not have to find it in a long string.</p>

<h2>2. Treat shortened links as unknown</h2>
<p>Links through bit.ly, t.co, tinyurl, and similar services hide their destination on purpose. A code that shows one of these tells you nothing until it is expanded. Either expand it first, with a scanner that follows the short link and shows you where it ends up, or do not open it.</p>

<h2>3. Look for lookalikes</h2>
<p>The oldest trick is a domain that reads like a familiar one. Watch for a digit standing in for a letter (<code>paypa1.com</code>), an extra word or hyphen (<code>paypal-secure.com</code>), a familiar name pushed into the wrong place (<code>paypal.com.example.net</code>, where the domain is <code>example.net</code>), and letters from another alphabet that draw the same shape. If a name looks almost right, it is wrong.</p>

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

<div class="card callout"><p>Verdetto shows every link before it opens, expands shortened ones, and flags each of the patterns above on your phone, with no ads. <a href="{href('index.html')}">See what it does</a>.</p></div>
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
  <li><a href="{href('support.html')}">Support</a></li>
  <li><a href="{href('check-qr-code-link.html')}">How to check a QR code link before you open it</a></li>
</ul>
"""

PAGES = {
    "index.html": ("Verdetto: QR & Barcode Scanner for Android", "A QR code and barcode scanner for Android. No ads, no fake buttons. See the link before it opens. Reads damaged codes.", HOME, APP),
    "privacy.html": ("Privacy policy - Verdetto", "Privacy policy for Verdetto: QR & Barcode Scanner. No accounts, no ads, no analytics. Scanning happens on your phone.", PRIVACY, {"@type": "WebPage", "name": "Privacy policy", "publisher": ORG}),
    "terms.html": ("Terms of use - Verdetto", "Terms of use for Verdetto: QR & Barcode Scanner. What the safety checks are and are not, and that every decision on scanned content is yours.", TERMS, {"@type": "WebPage", "name": "Terms of use", "publisher": ORG}),
    "support.html": ("Support - Verdetto", "Support for Verdetto: QR & Barcode Scanner. How to reach us and answers to common questions.", SUPPORT, FAQ_LD),
    "check-qr-code-link.html": (GUIDE_TITLE + " - Verdetto", GUIDE_DESC, GUIDE, GUIDE_LD),
    "404.html": ("Page not found - Verdetto", "That page is not here.", NOT_FOUND, None),
}
for name, (title, desc, body, ld) in PAGES.items():
    html = page(name, title.replace("&", "&amp;"), desc.replace("&", "&amp;"), body, ld, "article" if name.startswith("check") else "website")
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
    "before it opens, reads damaged codes, and checks scanned content for warning signs on the phone. It never says "
    "anything is safe: \"No warnings found\" means none of its checks matched.\n\n"
    f"Publisher: Verdetto, {ADDRESS}, United States. Contact: {EMAIL}. Store title: \"Verdetto: QR & Barcode Scanner\". "
    "Status: coming soon to Google Play.\n\n"
    "## Pages\n\n"
    + "".join(f"- [{t.replace(' - Verdetto', '')}]({url(n)}): {d}\n" for n, (t, d, _, _) in PAGES.items() if n != "404.html")
    + "\n## Facts\n\n"
    "- Platform: Android. Price: free. Ads: none. Accounts: none. Analytics: none.\n"
    "- Scanning and every safety check run on the phone; online lookups (list updates, shortened-link destinations, "
    "domain age, product details from Open Food Facts and Open Library) are on by default and can be turned off.\n"
    "- Reads QR codes and barcodes including EAN, UPC, Code 128, Data Matrix, PDF417, and Aztec, including damaged ones.\n"
    "- Scan history stays on the phone and can be deleted by the person.\n"
    "- The only permission requested is the camera.\n"
    "- An optional in-app contribution supports development; nothing is locked behind it.\n",
    encoding="utf-8", newline="\n")
(HERE / "sitemap.xml").write_text(
    '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    + "".join(f"  <url><loc>{url(n)}</loc><lastmod>{DATE}</lastmod></url>\n" for n in urls) + "</urlset>\n",
    encoding="utf-8", newline="\n")
(HERE / "CNAME").write_text("verdettoqr.com\n", encoding="utf-8", newline="\n")
print("wrote robots.txt, sitemap.xml, llms.txt, CNAME")
