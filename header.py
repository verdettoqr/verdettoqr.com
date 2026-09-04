"""Play developer-page header (4096 x 2304, JPEG under 1 MB): the mark and the wordmark on the
mint ground, same layout family as the share image. Run after assets.py."""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).parent
MASTER = Path(r"D:\OneDrive\OneDrive - Atlast\Alexandria Moving Records\New folder\optical-page-archive"
              r"\build\optical-page\app-design\icon\final\verdict-icon-1024.png")
MINT, TEAL, INK, VARIANT = (0xE9, 0xF5, 0xF1), (0x00, 0x6B, 0x5E), (0x19, 0x1C, 0x1B), (0x3F, 0x49, 0x46)


def font(name, size):
    for candidate in (name, "segoeui.ttf"):
        try:
            return ImageFont.truetype(str(Path(r"C:\Windows\Fonts") / candidate), size)
        except OSError:
            continue
    return ImageFont.load_default()


def rounded(img, frac=0.22):
    s = img.size[0]
    m = Image.new("L", (s, s), 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, s - 1, s - 1), radius=int(s * frac), fill=255)
    out = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    out.paste(img.convert("RGBA"), (0, 0), m)
    return out


W, H = 4096, 2304
img = Image.new("RGB", (W, H), MINT)
mark = rounded(Image.open(MASTER).convert("RGB").resize((1000, 1000), Image.LANCZOS))
img.paste(mark, (420, (H - 1000) // 2), mark)
d = ImageDraw.Draw(img)
x = 1620
d.text((x, 640), "Verdetto", font=font("seguisb.ttf", 320), fill=INK)
d.text((x + 12, 1040), "QR & Barcode Scanner for Android", font=font("segoeui.ttf", 140), fill=TEAL)
for i, line in enumerate(("See the link before it opens.", "No ads. No fake buttons.")):
    d.text((x + 12, 1300 + 150 * i), line, font=font("segoeui.ttf", 118), fill=VARIANT)
d.text((x + 12, 1780), "verdettoqr.com", font=font("segoeui.ttf", 96), fill=TEAL)
out = HERE / "play-header-4096x2304.jpg"
for q in (92, 85, 75):
    img.save(out, "JPEG", quality=q, optimize=True, subsampling=0)
    if out.stat().st_size < 1_000_000:
        break
print("wrote", out.name, out.stat().st_size, "bytes at quality", q)
