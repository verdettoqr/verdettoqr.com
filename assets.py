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
