"""Generate the site's binary assets from the icon master and the screen walk:
favicons, the Apple touch icon, the SVG favicon, the Open Graph image, and
the hero screenshot. Run once, then build.py. Requires Pillow only."""
import re
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).parent
ARCHIVE = Path(r"D:\OneDrive\OneDrive - Atlast\Alexandria Moving Records\New folder\optical-page-archive")
MASTER = ARCHIVE / "build/optical-page/app-design/icon/final/verdict-icon-1024.png"
SHOT = ARCHIVE / "build/optical-page/app-design/2026-09-03-screens/bundle/light-f01-scan-sheet-star.png"
MINT, DEEP, TEAL, INK, VARIANT = (0xE9, 0xF5, 0xF1), (0x00, 0x3D, 0x35), (0x00, 0x6B, 0x5E), (0x19, 0x1C, 0x1B), (0x3F, 0x49, 0x46)


def rounded(img, frac=0.22):
    s = img.size[0]
    m = Image.new("L", (s, s), 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, s - 1, s - 1), radius=int(s * frac), fill=255)
    out = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    out.paste(img.convert("RGBA"), (0, 0), m)
    return out


master = Image.open(MASTER).convert("RGB")
# favicons: rounded so the tab icon matches the launcher; 32 stays crisp from the 1024 master
for size, name in ((32, "favicon-32.png"), (180, "apple-touch-icon.png"), (512, "icon-512.png")):
    img = master.resize((size, size), Image.LANCZOS)
    (rounded(img) if size != 512 else img).save(HERE / name)
    print("wrote", name)

# svg favicon: the logo with rounded corners (same transform build.py applies)
svg = (HERE / "logo.svg").read_text(encoding="utf-8")
svg = re.sub(r'<rect width="108" height="108" fill="#D5E8E3"/>', '<rect width="108" height="108" rx="24" fill="#D5E8E3"/>', svg)
svg = re.sub(r' width="1024" height="1024"', "", svg)
(HERE / "icon.svg").write_text(svg, encoding="utf-8", newline="\n")
print("wrote icon.svg")


def font(name, size):
    for candidate in (name, "segoeui.ttf"):
        try:
            return ImageFont.truetype(str(Path(r"C:\Windows\Fonts") / candidate), size)
        except OSError:
            continue
    return ImageFont.load_default()




def transparent_mark(color, height, accent_rgb=(0xB8, 0x65, 0x0A)):
    """The QR mark alone on a transparent ground: the body in the given color (teal on light grounds, white on dark),
    the accent square always the signal amber, as on the splash. Built once from the master: pixels that are not the
    mint tile, their distance from the tile as alpha; the accent pixels found by their orange hue."""
    global _MARK_ALPHA, _MARK_ACCENT
    if "_MARK_ALPHA" not in globals():
        from PIL import ImageChops
        src = master.convert("RGB")
        diff = ImageChops.difference(src, Image.new("RGB", src.size, (0xD5, 0xE8, 0xE3))).convert("L")
        full = diff.point(lambda v: 255 if v > 30 else (0 if v < 4 else int(255 * (v - 4) / 26)))
        box = full.getbbox(); _MARK_ALPHA = full.crop(box)
        r, g, b = src.crop(box).split()
        # amber accent: red well above blue
        _MARK_ACCENT = ImageChops.subtract(r, b).point(lambda v: 255 if v > 60 else 0)
    alpha = _MARK_ALPHA; accent = _MARK_ACCENT
    scale = height / alpha.height; size = (max(1, round(alpha.width * scale)), height)
    alpha_s = alpha.resize(size, Image.LANCZOS); accent_s = accent.resize(size, Image.LANCZOS)
    body = Image.new("RGBA", size, color + (255,))
    amber = Image.new("RGBA", size, accent_rgb + (255,))
    out = Image.composite(amber, body, accent_s)
    out.putalpha(alpha_s)
    return out


def lockup(draw_target, x, y, text, fnt, color, body):
    """Mark (body color plus the amber accent), then the name in the text color; the mark at the cap height of the
    text; returns the right edge."""
    d = ImageDraw.Draw(draw_target)
    cap_top = y + fnt.getbbox("V")[1]; cap_bottom = y + fnt.getbbox("V")[3]
    # on a dark ground (white body) the accent is the dark theme's lighter amber, as in the site header
    m = transparent_mark(body, cap_bottom - cap_top, (0xFF, 0xB9, 0x5A) if body == (0xFF, 0xFF, 0xFF) else (0xB8, 0x65, 0x0A))
    draw_target.paste(m, (x, cap_top), m)
    tx = x + m.width + round(0.3 * fnt.size)
    d.text((tx, y), text, font=fnt, fill=color)
    return tx + round(d.textlength(text, font=fnt))


# Open Graph image 1200x630: the lockup, then the tagline
og = Image.new("RGB", (1200, 630), MINT)
lockup(og, 90, 120, "Verdetto", font("seguisb.ttf", 92), INK, DEEP)
d = ImageDraw.Draw(og)
d.text((90, 262), "QR & Barcode Scanner for Android", font=font("segoeui.ttf", 40), fill=TEAL)
for i, line in enumerate(("See the link before it opens.", "No ads. No fake buttons.", "Reads the codes other apps give up on.")):
    d.text((90, 350 + 46 * i), line, font=font("segoeui.ttf", 34), fill=VARIANT)
d.text((90, 548), "verdettoqr.com", font=font("segoeui.ttf", 28), fill=TEAL)
og.save(HERE / "og-image.png", optimize=True)
print("wrote og-image.png")

# hero screenshot: the result sheet at 2x for a 270 px wide slot, WebP
shot = Image.open(SHOT).convert("RGB")
w = 540
shot = shot.resize((w, round(shot.height * w / shot.width)), Image.LANCZOS)
(HERE / "screens").mkdir(exist_ok=True)
shot.save(HERE / "screens" / "result-sheet.webp", "WEBP", quality=84, method=6)
print("wrote screens/result-sheet.webp", shot.size)


# Per-page social images 1200x630 (word-of-mouth surface 4): the mark, the wordmark, the page's title and one line, on
# the mint ground. Localized privacy and terms pages carry their localized title. Each stays under 40 KB (PNG, palette).
import sys  # noqa: E402

sys.path.insert(0, str(HERE))
import build  # noqa: E402  (build.py runs nothing on import)

SCRATCH_LIB = Path(r"C:\Users\Sam\AppData\Local\Temp\claude\D--OneDrive-OneDrive---Atlast-Alexandria-Moving-Records-New-folder-optical-page-archive\f9f927c8-5f39-4ae7-968e-db5100e761f2\scratchpad\pylib")
sys.path.insert(0, str(SCRATCH_LIB))
try:
    import arabic_reshaper  # noqa: E402
    from bidi.algorithm import get_display  # noqa: E402
except ImportError:  # without the shaper the Arabic page keeps the English title on its image
    arabic_reshaper = None

FONTS = Path(r"C:\Windows\Fonts")
# Roboto is the bundled web font, but Pillow cannot read the .woff2; the Android SDK's Roboto TTF is used when present,
# else Segoe UI, which is what the shared og-image.png already uses. Per script: Yu Gothic (ja), Microsoft YaHei (zh), Nirmala (hi).
ROBOTO = next((p for p in Path(r"C:\Users\Sam\AppData\Local\Android\Sdk\platforms").glob("*/data/fonts/Roboto-Regular.ttf")), None) if Path(r"C:\Users\Sam\AppData\Local\Android\Sdk\platforms").exists() else None
ROBOTO_BOLD = next((p for p in Path(r"C:\Users\Sam\AppData\Local\Android\Sdk\platforms").glob("*/data/fonts/Roboto-Medium.ttf")), None) if ROBOTO else None
SCRIPT_FONT = {"ja": "YuGothM.ttc", "zh-Hans": "msyh.ttc", "hi": "Nirmala.ttc"}


def page_font(lang, size, bold=False):
    if lang in SCRIPT_FONT:
        try:
            return ImageFont.truetype(str(FONTS / SCRIPT_FONT[lang]), size)
        except OSError:
            pass
    if ROBOTO and lang not in ("ar", "ru"):
        return ImageFont.truetype(str(ROBOTO_BOLD if bold and ROBOTO_BOLD else ROBOTO), size)
    return font("seguisb.ttf" if bold else "segoeui.ttf", size)


def shape(text, lang):
    if lang == "ar" and arabic_reshaper is not None:
        return get_display(arabic_reshaper.reshape(text))
    return text


def wrap(draw, text, fnt, width, lang):
    """Greedy wrap by measured width; CJK wraps per character since there are no spaces."""
    units = list(text) if lang in ("ja", "zh-Hans") else text.split(" ")
    joiner = "" if lang in ("ja", "zh-Hans") else " "
    lines, cur = [], ""
    for u in units:
        cand = (cur + joiner + u) if cur else u
        if draw.textlength(shape(cand, lang), font=fnt) <= width or not cur:
            cur = cand
        else:
            lines.append(cur); cur = u
    if cur:
        lines.append(cur)
    return lines


OG_HEAD = {"report.html": "Report a link or a wrong read", "community-license.html": "Community License",
           "community-license-es.html": "Community License",
           "community-license-fr.html": "Community License",
           "community-license-de.html": "Community License",
           "community-license-pt-br.html": "Community License",
           "community-license-ru.html": "Community License",
           "community-license-id.html": "Community License",
           "community-license-ja.html": "Community License",
           "community-license-zh-hans.html": "Community License",
           "community-license-hi.html": "Community License",
           "community-license-ar.html": "Community License",
           "report-de.html": "Einen Link oder eine Fehllesung melden",
           "report-es.html": "Informar de un enlace o de una lectura errónea",
           "report-fr.html": "Signaler un lien ou une mauvaise lecture",
           "report-pt-br.html": "Relatar um link ou uma leitura errada",
           "report-id.html": "Laporkan tautan atau pembacaan yang salah",
           "report-ru.html": "Сообщить о ссылке или неверном чтении",
           "report-hi.html": "किसी लिंक या गलत रीडिंग की रिपोर्ट करें",
           "report-ja.html": "リンクや誤読を報告する",
           "report-zh-hans.html": "报告链接或误读",
           "report-ar.html": "أبلغ عن رابط أو قراءة خاطئة",
           }  # the lockup carries the name; a head never repeats it
FULL_STOPS = ".。।"  # period, ideographic full stop, danda


def dename(text):
    text = re.sub(r"Verdetto: QR & Barcode Scanner( for Android)?", "the app", text)
    return text.replace("Verdetto's", "the app's").replace("Verdetto", "the app")


def og_line(desc):
    """The image's one line: the first sentence without the name when it says something (30+ characters), else the first
    sentence with the name replaced. A sentence ends at a full stop of its script followed by white space."""
    sentences = [x.strip() for x in re.split("(?<=[" + re.escape(FULL_STOPS) + r"])\s+", desc) if x.strip()]
    pick = next((x for x in sentences if "Verdetto" not in x and len(x) >= 30), None) or dename(sentences[0])
    stop = pick[-1] if pick[-1] in FULL_STOPS else "."
    return pick.rstrip(FULL_STOPS) + stop


(HERE / "og").mkdir(exist_ok=True)

for name, (title, desc, _body, _ld) in build.PAGES.items():
    if name == "404.html":
        continue
    lang, rtl, _alts = build.PAGE_LANG.get(name, ("en", False, None))
    stem = name[:-5]
    # The no-repetition rule (operator, 2026-09-05: "we can't be duplicative or repetitive in the same message"): the mark and
    # wordmark are the one mention of the name, the footer the one mention of the domain, so the title and the line carry
    # neither. A name-free sentence of the description is preferred; else the name becomes "the app".
    head = OG_HEAD.get(name) or re.sub(r"^Verdetto: ", "", title.split(" - ")[0] if " - " in title else title)
    line = og_line(desc)
    for shown in (head, line):
        assert "Verdetto" not in shown and "verdettoqr" not in shown.lower(), (name, shown)
    if lang == "ar" and arabic_reshaper is None:
        head, line = build.PAGES["privacy.html" if "privacy" in name else "terms.html"][0].split(" - ")[0], ""
    img = Image.new("RGB", (1200, 630), MINT)
    d = ImageDraw.Draw(img)
    lockup(img, 90, 96, "Verdetto", page_font("en", 60, bold=True), INK, DEEP)
    title_font = page_font(lang, 66, bold=True)
    title_lines = wrap(d, head, title_font, 1020, lang)[:2]
    y = 290
    for t in title_lines:
        t2 = shape(t, lang)
        x = 1110 - d.textlength(t2, font=title_font) if rtl else 90
        d.text((x, y), t2, font=title_font, fill=DEEP)
        y += 80
    line_font = page_font(lang, 34)
    line_lines = wrap(d, line, line_font, 1020, lang)
    if len(line_lines) > 2:  # the one line is at most two rows; a cut ends on an ellipsis, never on a comma
        line_lines = line_lines[:2]
        line_lines[1] = line_lines[1].rstrip(" ,;:、，；：") + "…"
    for t in line_lines:
        t2 = shape(t, lang)
        x = 1110 - d.textlength(t2, font=line_font) if rtl else 90
        d.text((x, y + 10), t2, font=line_font, fill=VARIANT)
        y += 44
    d.text((90, 556), "verdettoqr.com", font=page_font("en", 28), fill=TEAL)
    out = HERE / "og" / f"{stem}.png"
    img.quantize(colors=64, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE).save(out, optimize=True)
    size = out.stat().st_size
    if size > 40 * 1024:
        img.quantize(colors=16, dither=Image.Dither.NONE).save(out, optimize=True)
        size = out.stat().st_size
    assert size <= 40 * 1024, (name, size)
    print("wrote", out.relative_to(HERE), size // 1024, "KB", lang)


# Press kit lockups: mark and name on a transparent ground, ink for light grounds and white for dark grounds
for fname, color, body in (("lockup-teal-amber.png", INK, DEEP), ("lockup-white-amber.png", (0xFF, 0xFF, 0xFF), (0xFF, 0xFF, 0xFF))):
    canvas = Image.new("RGBA", (900, 200), (0, 0, 0, 0))
    right = lockup(canvas, 20, 40, "Verdetto", font("seguisb.ttf", 120), color, body)
    canvas = canvas.crop((0, 0, right + 20, 200))
    canvas.save(HERE / fname, optimize=True)
    print("wrote", fname, canvas.size)
