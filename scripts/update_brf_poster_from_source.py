from pathlib import Path
from PIL import Image, ImageOps

SRC = Path('/root/.hermes/image_cache/img_f3c474aa71d5.png')
ASSETS = Path('/root/workspace/sait/assets')

DESKTOP_ORIGINAL = ASSETS / 'brf-poster.png'
DESKTOP_OUTPUTS = [
    (ASSETS / 'brf-poster.jpg', 1280),
    (ASSETS / 'brf-poster-1920.jpg', 1920),
    (ASSETS / 'brf-poster-3840.jpg', 3840),
]
MOBILE_ORIGINAL = ASSETS / 'brf-poster-mobile.png'
MOBILE_OUTPUTS = [
    (ASSETS / 'brf-poster-mobile.jpg', 960),
    (ASSETS / 'brf-poster-mobile-828.jpg', 828),
]
JPEG_QUALITY = 91


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


def save_jpeg(im: Image.Image, path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    im.save(path, 'JPEG', quality=JPEG_QUALITY, optimize=True, progressive=True, subsampling=1)
    print(f'{path.relative_to(ASSETS.parent)} {im.size} {path.stat().st_size // 1024}KB')


def main():
    src = Image.open(SRC)
    src.save(DESKTOP_ORIGINAL)
    src.save(MOBILE_ORIGINAL)
    print(f'{DESKTOP_ORIGINAL.relative_to(ASSETS.parent)} {src.size} {DESKTOP_ORIGINAL.stat().st_size // 1024}KB')
    print(f'{MOBILE_ORIGINAL.relative_to(ASSETS.parent)} {src.size} {MOBILE_ORIGINAL.stat().st_size // 1024}KB')

    rgb = flatten_rgba(src)
    for path, width in DESKTOP_OUTPUTS + MOBILE_OUTPUTS:
        save_jpeg(resize_width(rgb, width), path)


if __name__ == '__main__':
    main()
