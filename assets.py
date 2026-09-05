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


# Open Graph image 1200x630: mark on the left, name and tagline on the right
og = Image.new("RGB", (1200, 630), MINT)
mark = rounded(master.resize((360, 360), Image.LANCZOS))
og.paste(mark, (90, 135), mark)
d = ImageDraw.Draw(og)
d.text((520, 175), "Verdetto", font=font("seguisb.ttf", 92), fill=INK)
d.text((524, 290), "QR & Barcode Scanner for Android", font=font("segoeui.ttf", 40), fill=TEAL)
for i, line in enumerate(("See the link before it opens.", "No ads. No fake buttons.", "Made for damaged codes.")):
    d.text((524, 372 + 46 * i), line, font=font("segoeui.ttf", 34), fill=VARIANT)
d.text((524, 548), "verdettoqr.com", font=font("segoeui.ttf", 28), fill=TEAL)
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


(HERE / "og").mkdir(exist_ok=True)
small_mark = rounded(master.resize((150, 150), Image.LANCZOS))
for name, (title, desc, _body, _ld) in build.PAGES.items():
    if name == "404.html":
        continue
    lang, rtl, _alts = build.PAGE_LANG.get(name, ("en", False, None))
    stem = name[:-5]
    head = title.split(" - ")[0] if " - " in title else title
    line = desc.split(". ")[0].rstrip(".") + "."
    if lang == "ar" and arabic_reshaper is None:
        head, line = build.PAGES["privacy.html" if "privacy" in name else "terms.html"][0].split(" - ")[0], ""
    img = Image.new("RGB", (1200, 630), MINT)
    d = ImageDraw.Draw(img)
    img.paste(small_mark, (90, 80), small_mark)
    d.text((270, 118), "Verdetto", font=page_font("en", 60, bold=True), fill=INK)
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
