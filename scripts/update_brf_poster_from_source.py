from pathlib import Path
from PIL import Image, ImageOps, ImageFilter, ImageEnhance

SRC = Path('/root/.hermes/image_cache/img_f3c474aa71d5.png')
ASSETS = Path('/root/workspace/sait/assets')

# Current hero HTML expects these exact filenames.
DESKTOP_ORIGINAL = ASSETS / 'brf-poster.png'
DESKTOP_OUTPUTS = [
    (ASSETS / 'brf-poster.jpg', 1280),
    (ASSETS / 'brf-poster-1920.jpg', 1920),
    # Source is 2280 wide; keep no-upscale 2280px payload behind the historical 3840 filename.
    (ASSETS / 'brf-poster-3840.jpg', 3840),
]
MOBILE_ORIGINAL = ASSETS / 'brf-poster-mobile.png'
MOBILE_OUTPUTS = [
    (ASSETS / 'brf-poster-mobile.jpg', 960),
    (ASSETS / 'brf-poster-mobile-828.jpg', 828),
]

JPEG_QUALITY = 91
MOBILE_SIZE = 960


def flatten_rgba(im: Image.Image, bg=(255, 255, 255)) -> Image.Image:
    im = ImageOps.exif_transpose(im)
    if im.mode in ('RGBA', 'LA'):
        base = Image.new('RGB', im.size, bg)
        base.paste(im, mask=im.split()[-1])
        return base
    return im.convert('RGB')


def resize_width(im: Image.Image, width: int) -> Image.Image:
    width = min(width, im.width)
    if width == im.width:
        return im.copy()
    height = round(im.height * width / im.width)
    return im.resize((width, height), Image.Resampling.LANCZOS)


def cover_resize(im: Image.Image, size: int) -> Image.Image:
    scale = max(size / im.width, size / im.height)
    resized = im.resize((round(im.width * scale), round(im.height * scale)), Image.Resampling.LANCZOS)
    left = (resized.width - size) // 2
    top = (resized.height - size) // 2
    return resized.crop((left, top, left + size, top + size))


def mobile_square_composite(im: Image.Image) -> Image.Image:
    """Square phone art from one wide poster, without destroying the logo.

    A hard square crop cuts the main logo and side artists too aggressively. Instead:
    - blurred/darkened full-poster background fills the square;
    - the complete wide poster sits centered as a sharp foreground strip.
    This preserves all event information while keeping the existing 1:1 mobile hero slot.
    """
    size = MOBILE_SIZE
    bg = cover_resize(im, size).filter(ImageFilter.GaussianBlur(18))
    bg = ImageEnhance.Contrast(bg).enhance(1.06)
    bg = ImageEnhance.Brightness(bg).enhance(0.82)

    fg = im.resize((size, round(size * im.height / im.width)), Image.Resampling.LANCZOS)
    # Slightly above center: artists + logo matter more than empty lower sponsor area.
    y = round((size - fg.height) * 0.46)
    bg.paste(fg, (0, y))
    return bg


def save_jpeg(im: Image.Image, path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    im.save(path, 'JPEG', quality=JPEG_QUALITY, optimize=True, progressive=True, subsampling=1)
    print(f'{path.relative_to(ASSETS.parent)} {im.size} {path.stat().st_size // 1024}KB')


def main():
    src = Image.open(SRC)
    # keep PNG originals for future reprocessing/source-of-truth
    src.save(DESKTOP_ORIGINAL)
    print(f'{DESKTOP_ORIGINAL.relative_to(ASSETS.parent)} {src.size} {DESKTOP_ORIGINAL.stat().st_size // 1024}KB')

    rgb = flatten_rgba(src)
    for path, width in DESKTOP_OUTPUTS:
        save_jpeg(resize_width(rgb, width), path)

    mob = mobile_square_composite(rgb)
    mob.save(MOBILE_ORIGINAL)
    print(f'{MOBILE_ORIGINAL.relative_to(ASSETS.parent)} {mob.size} {MOBILE_ORIGINAL.stat().st_size // 1024}KB')
    for path, width in MOBILE_OUTPUTS:
        save_jpeg(resize_width(mob, width), path)


if __name__ == '__main__':
    main()
