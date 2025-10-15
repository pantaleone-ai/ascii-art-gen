from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import StreamingResponse, JSONResponse
from io import BytesIO
from typing import Optional
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
import numpy as np
import random, math, os

app = FastAPI()

# Try to find a default TTF font
DEFAULT_FONT = None
for candidate in [
    "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/Library/Fonts/Arial.ttf",
]:
    if os.path.exists(candidate):
        DEFAULT_FONT = candidate
        break

CHAR_PRESETS = {
    "standard": "@%#*+=-:. ",
    "dense": "$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\\|()1{}[]?-_+~<>i!lI;:,\"^`'. ",
    "blocks": "█▓▒░ ",
    "binary": "01",
    "letters": "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ",
}

def get_font(path, size):
    try:
        if path:
            return ImageFont.truetype(path, size=size)
    except Exception:
        pass
    return ImageFont.load_default()

def map_brightness_to_index(brightness, charset):
    idx = int((brightness / 255.0) * (len(charset) - 1))
    return max(0, min(len(charset) - 1, idx))

@app.post("/")
async def generate(
    file: UploadFile = File(...),
    scale: float = Form(0.08),
    char_width: int = Form(10),
    char_height: int = Form(18),
    font_size: int = Form(14),
    preset: str = Form("dense"),
    charset: Optional[str] = Form(None),
    diversity: float = Form(0.0),
    sample_method: str = Form("center"),
    dither: bool = Form(False),
    dither_strength: float = Form(0.25),
    color_mode: str = Form("rgb"),
    palette: Optional[str] = Form(None),
    invert: bool = Form(False),
    brightness: float = Form(1.0),
    contrast: float = Form(1.0),
    seed: Optional[int] = Form(None),
):
    content = await file.read()
    try:
        pil_img = Image.open(BytesIO(content)).convert("RGB")
    except Exception as e:
        return JSONResponse({"error": "invalid image", "detail": str(e)}, status_code=400)

    if seed is not None:
        random.seed(seed)
        np.random.seed(seed)

    if charset is None:
        charset = CHAR_PRESETS.get(preset, CHAR_PRESETS["dense"])

    enhancer = ImageEnhance.Brightness(pil_img)
    pil_img = enhancer.enhance(brightness)
    enhancer = ImageEnhance.Contrast(pil_img)
    pil_img = enhancer.enhance(contrast)

    original_w, original_h = pil_img.size
    target_w = max(1, int(original_w * scale))
    aspect = (char_width / char_height)
    target_h = max(1, int(original_h * scale * (1.0 / aspect)))
    img_small = pil_img.resize((target_w, target_h), resample=Image.BILINEAR)
    arr = np.array(img_small)
    lum = (0.299 * arr[..., 0] + 0.587 * arr[..., 1] + 0.114 * arr[..., 2]).astype(np.uint8)

    if invert:
        lum = 255 - lum

    rows = []
    for y in range(target_h):
        row = []
        for x in range(target_w):
            if sample_method == "random":
                nx = min(max(0, x + random.randint(-1,1)), target_w-1)
                ny = min(max(0, y + random.randint(-1,1)), target_h-1)
                sample_rgb = arr[ny, nx]
                b = lum[ny, nx]
            else:
                sample_rgb = arr[y, x]
                b = lum[y, x]

            base_idx = map_brightness_to_index(b, charset)
            chosen_idx = base_idx
            if diversity and diversity > 0:
                spread = max(1, int(len(charset) * diversity))
                low = max(0, base_idx - spread)
                high = min(len(charset)-1, base_idx + spread)
                candidates = list(range(low, high+1))
                sigma = max(0.5, spread/2.0)
                weights = [math.exp(-((c-base_idx)**2)/(2*(sigma**2))) for c in candidates]
                s = sum(weights)
                probs = [w/s for w in weights]
                chosen_idx = random.choices(candidates, weights=probs, k=1)[0]
            ch = charset[chosen_idx]
            row.append((ch, tuple(int(v) for v in sample_rgb)))
        rows.append(row)

    out_w = target_w * char_width
    out_h = target_h * char_height
    out_img = Image.new("RGB", (out_w, out_h), color=(0,0,0))
    draw = ImageDraw.Draw(out_img)
    font = get_font(DEFAULT_FONT, font_size)

    # simple ordered 4x4 Bayer for dithering if requested
    bayer = None
    if dither:
        bayer = np.array([[0,8,2,10],[12,4,14,6],[3,11,1,9],[15,7,13,5]], dtype=float)/16.0
        bh, bw = bayer.shape

    for y, row in enumerate(rows):
        for x, (ch, rgb) in enumerate(row):
            px = x * char_width
            py = y * char_height
            fill = tuple(int(c) for c in rgb)
            if dither and bayer is not None:
                v = bayer[y % bh, x % bw]
                if random.random() < v * float(dither_strength):
                    # flip a char index a bit
                    try:
                        idx = charset.index(ch)
                        if random.random() > 0.5:
                            idx = min(idx+1, len(charset)-1)
                        else:
                            idx = max(idx-1, 0)
                        ch = charset[idx]
                    except ValueError:
                        pass
            draw.text((px, py), ch, font=font, fill=fill)

    buf = BytesIO()
    out_img.save(buf, format="PNG")
    buf.seek(0)
    return StreamingResponse(buf, media_type="image/png")
