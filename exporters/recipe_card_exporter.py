# ──────────────────────────────────────────────
# RECIPE CARD EXPORTER
# ──────────────────────────────────────────────
import os
import math
from PIL import Image, ImageDraw, ImageFilter, ImageFont


# ── Helpers ────────────────────────────────────

def _dominant_color(img: Image.Image) -> tuple[int, int, int]:
    """Return the average color of the image (used for background tint)."""
    small = img.copy().convert("RGB")
    small.thumbnail((50, 50))
    pixels = list(small.getdata())
    r = sum(p[0] for p in pixels) // len(pixels)
    g = sum(p[1] for p in pixels) // len(pixels)
    b = sum(p[2] for p in pixels) // len(pixels)
    return (r, g, b)


def _darken(color: tuple[int, int, int], factor: float = 0.35) -> tuple[int, int, int]:
    return tuple(int(c * factor) for c in color)


def _blend(color: tuple[int, int, int], factor: float = 0.55) -> tuple[int, int, int]:
    """Blend color toward dark gray."""
    target = (30, 30, 30)
    return tuple(int(color[i] * factor + target[i] * (1 - factor)) for i in range(3))


def _rounded_rect_mask(size: tuple[int, int], radius: int) -> Image.Image:
    mask = Image.new("L", size, 0)
    d = ImageDraw.Draw(mask)
    d.rounded_rectangle([(0, 0), (size[0] - 1, size[1] - 1)], radius=radius, fill=255)
    return mask


def _paste_rounded(base: Image.Image, img: Image.Image, pos: tuple[int, int], radius: int):
    mask = _rounded_rect_mask(img.size, radius)
    base.paste(img, pos, mask)


def _draw_pill(draw: ImageDraw.ImageDraw, xy, fill, radius=18, alpha=160):
    """Draw a rounded rectangle pill."""
    draw.rounded_rectangle(xy, radius=radius, fill=fill)


def _try_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = (
        ["arialbd.ttf", "Arial Bold.ttf", "DejaVuSans-Bold.ttf", "LiberationSans-Bold.ttf"]
        if bold else
        ["arial.ttf", "Arial.ttf", "DejaVuSans.ttf", "LiberationSans-Regular.ttf"]
    )
    for name in candidates:
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            pass
    return ImageFont.load_default()


# ── Layout constants ────────────────────────────

CARD_W = 900
# Aspect ratio 4 (width) : 5 (height)  →  portrait format
CARD_H = int(CARD_W * 5 / 4)   # = 1125 px

PADDING = 36
PHOTO_RADIUS = 22
PILL_RADIUS = 16
PILL_ALPHA = 180   # 0-255


# ── Main export function ────────────────────────

def export_recipe_card(
    photo_path: str,
    recipe: dict,
    output_path: str,
    app_name: str = "Film Recipe Finder",
) -> str:

    # ── 1. Load & orient source photo ──────────────
    src = Image.open(photo_path)
    from PIL import ExifTags
    try:
        exif = src.getexif()
        orientation = exif.get(ExifTags.Base.Orientation, 1)
        if orientation == 8:
            src = src.rotate(90, expand=True)
        elif orientation == 6:
            src = src.rotate(-90, expand=True)
        elif orientation == 3:
            src = src.rotate(180, expand=True)
    except Exception:
        pass
    src = src.convert("RGB")

    # ── 2. Fixed card dimensions (4:5 portrait) ────
    # CARD_W and CARD_H are defined as module-level constants above.
    # All layout sections below are distributed within CARD_H.

    # ── 3. Build blurred background ────────────────
    dom = _dominant_color(src)

    bg_photo = src.copy()
    bg_photo = bg_photo.resize((CARD_W, CARD_H), Image.LANCZOS)
    bg_photo = bg_photo.filter(ImageFilter.GaussianBlur(radius=40))
    overlay = Image.new("RGB", (CARD_W, CARD_H), _darken(dom, 0.25))
    bg = Image.blend(bg_photo, overlay, alpha=0.55)

    card = bg.copy()
    draw = ImageDraw.Draw(card, "RGBA")

    # ── 3. Fonts ────────────────────────────────────
    f_title   = _try_font(38, bold=True)
    f_sub     = _try_font(20)
    f_brand   = _try_font(22, bold=True)
    f_pill_lg = _try_font(26, bold=True)
    f_pill_sm = _try_font(18, bold=True)
    f_label   = _try_font(15)

    # ── 4. Header ───────────────────────────────────
    name = recipe.get("Name", "Unknown Recipe")
    film_mode = recipe.get("FilmMode", "")

    # Recipe name
    draw.text((PADDING, PADDING), name, font=f_title, fill=(255, 255, 255))
    title_h = f_title.size + 6
    sub_text = film_mode if film_mode and film_mode.strip() and film_mode != "None" else ""
    draw.text((PADDING, PADDING + title_h), sub_text, font=f_sub, fill=(200, 200, 200))

    # Branding top-right
    brand_bbox = draw.textbbox((0, 0), app_name, font=f_brand)
    brand_w = brand_bbox[2] - brand_bbox[0]
    draw.text((CARD_W - PADDING - brand_w, PADDING + 6), app_name, font=f_brand, fill=(150, 150, 150))

    # ── 5. Photo thumbnail ──────────────────────────
    # Header block height
    header_block_h = PADDING + title_h + 20 + 14   # top pad + title + sub + gap

    # Distribute remaining vertical space:
    #   big pills row  →  90 px
    #   gap after big  →  20 px
    #   small pills    →  2 rows × 72 px + 1 × 10 gap = 154 px
    #   bottom padding →  PADDING
    ROWS_SMALL = math.ceil(9 / 5)
    small_pill_h = 72
    small_gap = 10
    big_pill_h = 90
    bottom_reserved = big_pill_h + 20 + ROWS_SMALL * small_pill_h + (ROWS_SMALL - 1) * small_gap + PADDING

    photo_y = header_block_h
    photo_h = CARD_H - photo_y - bottom_reserved - 24   # 24 = gap between photo and big pills

    photo_w = CARD_W - 2 * PADDING

    thumb = src.copy()
    src_ratio = src.width / src.height
    target_ratio = photo_w / photo_h
    if src_ratio > target_ratio:
        new_w = int(src.height * target_ratio)
        offset = (src.width - new_w) // 2
        thumb = thumb.crop((offset, 0, offset + new_w, src.height))
    else:
        new_h = int(src.width / target_ratio)
        offset = (src.height - new_h) // 2
        thumb = thumb.crop((0, offset, src.width, offset + new_h))
    thumb = thumb.resize((photo_w, photo_h), Image.LANCZOS)

    _paste_rounded(card, thumb, (PADDING, photo_y), PHOTO_RADIUS)
    draw = ImageDraw.Draw(card, "RGBA")  # redraw after paste

    # ── 6. Big pills row (Film Sim · WB · Grain) ────
    big_pill_y = photo_y + photo_h + 24
    gap = 12

    wb_val = recipe.get("WhiteBalance", "Auto")
    ct = recipe.get("ColorTemperature", "")
    wb_display = f"{ct}K" if ct and ct.strip() else wb_val

    wb_fine = recipe.get("WhiteBalanceFineTune", "")
    wb_fine_short = ""
    if wb_fine and wb_fine != "Red +0, Blue +0":
        wb_fine_short = wb_fine

    grain_r = recipe.get("GrainEffectRoughness", "Off")
    grain_s = recipe.get("GrainEffectSize", "Off")
    grain_display = "Off" if grain_r == "Off" else f"{grain_r}\n{grain_s}"

    big_pills = [
        {"top": film_mode or "—",   "bot": "Film Simulation"},
        {"top": wb_display,          "bot": wb_fine_short or "White Balance"},
        {"top": grain_display,       "bot": "Grain Effect"},
    ]

    total_gap = gap * (len(big_pills) - 1)
    pill_w = (CARD_W - 2 * PADDING - total_gap) // len(big_pills)

    pill_bg = (*_darken(dom, 0.55), PILL_ALPHA)  # RGBA

    for i, p in enumerate(big_pills):
        x0 = PADDING + i * (pill_w + gap)
        y0 = big_pill_y
        x1 = x0 + pill_w
        y1 = y0 + big_pill_h
        draw.rounded_rectangle([(x0, y0), (x1, y1)], radius=PILL_RADIUS, fill=pill_bg)

        tb = draw.textbbox((0, 0), p["top"], font=f_pill_lg)
        tw = tb[2] - tb[0]
        cx = x0 + (pill_w - tw) // 2
        draw.text((cx, y0 + 10), p["top"], font=f_pill_lg, fill=(240, 240, 240))

        lb = draw.textbbox((0, 0), p["bot"], font=f_label)
        lw = lb[2] - lb[0]
        draw.text((x0 + (pill_w - lw) // 2, y1 - 26), p["bot"], font=f_label, fill=(170, 170, 170))

    # ── 7. Small pills grid ─────────────────────────
    small_fields = [
        ("ColorChromeEffect",  "Color Effect"),
        ("ColorChromeFXBlue",  "Color FX Blue"),
        ("DevelopmentDynamicRange", "Dynamic Range"),
        ("HighlightTone",      "Highlight"),
        ("ShadowTone",         "Shadow"),
        ("Saturation",         "Color"),
        ("Sharpness",          "Sharpness"),
        ("NoiseReduction",     "Noise Reduction"),
        ("Clarity",            "Clarity"),
    ]

    COLS = 5
    small_y = big_pill_y + big_pill_h + 20
    small_pill_w = (CARD_W - 2 * PADDING - small_gap * (COLS - 1)) // COLS

    for idx, (field, label) in enumerate(small_fields):
        col = idx % COLS
        row = idx // COLS
        x0 = PADDING + col * (small_pill_w + small_gap)
        y0 = small_y + row * (small_pill_h + small_gap)
        x1 = x0 + small_pill_w
        y1 = y0 + small_pill_h

        draw.rounded_rectangle([(x0, y0), (x1, y1)], radius=12, fill=pill_bg)

        val = recipe.get(field, "—") or "—"
        short_val = val.split(" ")[0] if " " in val else val

        vb = draw.textbbox((0, 0), short_val, font=f_pill_lg)
        vw = vb[2] - vb[0]
        draw.text((x0 + (small_pill_w - vw) // 2, y0 + 8), short_val, font=f_pill_lg, fill=(230, 230, 230))

        lb = draw.textbbox((0, 0), label, font=f_label)
        lw = lb[2] - lb[0]
        draw.text((x0 + (small_pill_w - lw) // 2, y1 - 22), label, font=f_label, fill=(160, 160, 160))

    # ── 8. Save ──────────────────────────────────────
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    card.convert("RGB").save(output_path, "PNG", quality=95)
    return output_path