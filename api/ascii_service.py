from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import StreamingResponse, JSONResponse, PlainTextResponse
from io import BytesIO
from typing import Optional
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageOps
import numpy as np
import random
import math
import os

app = FastAPI()

# Expanded font candidates for better cross-platform support
DEFAULT_FONT = None
for candidate in [
    "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/Library/Fonts/Arial.ttf",
    "/System/Library/Fonts/Menlo.ttc",
    "/usr/share/fonts/liberation/LiberationMono-Regular.ttf",
    "arial.ttf",  # Windows fallback
]:
    if os.path.exists(candidate):
        DEFAULT_FONT = candidate
        break

# Expanded charset presets for finer control
CHAR_PRESETS = {
    "standard": "@%#*+=-:. ",
    "dense": "$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\\|()1{}[]?-_+~<>i!lI;:,\"^`'. ",
    "blocks": "█▓▒░ ",
    "binary": "01",
    "letters": "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ",
    "extended": " .'`^\",:;Il!i><~+_-?][}{1)(|\\/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$",
}

def get_font(path: Optional[str], size: int):
    try:
        if path:
            return ImageFont.truetype(path, size=size)
    except Exception:
        pass
    return ImageFont.load_default() if DEFAULT_FONT is None else ImageFont.truetype(DEFAULT_FONT, size=size)

def map_brightness_to_index(brightness: float, charset: str) -> int:
    # Normalized to 0-1, map to charset index (high brightness -> high index, assuming charset dark to light)
    idx = int(brightness * (len(charset) - 1))
    return max(0, min(len(charset) - 1, idx))

def apply_floyd_steinberg_dither(lum: np.ndarray) -> np.ndarray:
    # Improved dithering: Floyd-Steinberg on luminance for better gradients
    h, w = lum.shape
    for y in range(h):
        for x in range(w):
            old = lum[y, x]
            new = round(old / 255.0) * 255  # Quantize (simplified; adjust levels as needed)
            err = old - new
            lum[y, x] = new
            if x + 1 < w:
                lum[y, x + 1] += err * 7 / 16
            if y + 1 < h:
                if x > 0:
                    lum[y + 1, x - 1] += err * 3 / 16
                lum[y + 1, x] += err * 5 / 16
                if x + 1 < w:
                    lum[y + 1, x + 1] += err * 1 / 16
    return lum

def generate_procedural_array(target_w: int, target_h: int, style: str, seed: Optional[int]) -> tuple[np.ndarray, np.ndarray]:
    # New: Procedural generation of RGB and lum arrays
    if seed is not None:
        random.seed(seed)
        np.random.seed(seed)
    
    arr = np.zeros((target_h, target_w, 3), dtype=np.uint8)
    lum = np.zeros((target_h, target_w), dtype=np.uint8)
    
    for y in range(target_h):
        for x in range(target_w):
            if style == "waves":
                value = math.sin(x / (target_w / 10.0)) + math.cos(y / (target_h / 5.0))
                value = (value + 2) / 4  # Normalize 0-1
                lum[y, x] = int(value * 255)
                arr[y, x] = [int(255 * value), int(255 * (1 - value)), int(128 + 127 * math.sin(x / 5))]  # Colorful waves
            elif style == "radial":
                dx = x - target_w / 2
                dy = y - target_h / 2
                dist = math.sqrt(dx**2 + dy**2) / math.sqrt((target_w/2)**2 + (target_h/2)**2)
                value = (math.sin(dist * 10) + 1) / 2
                lum[y, x] = int(value * 255)
                arr[y, x] = [int(255 * dist), int(255 * value), int(255 * (1 - dist))]  # Radial gradient
            elif style == "noise":
                # Simple hash-based noise for organic abstract
                noise = (math.sin(x * 12.9898 + y * 78.233) * 43758.5453) % 1
                value = noise
                lum[y, x] = int(value * 255)
                arr[y, x] = [int(255 * noise), int(255 * (1 - noise)), int(128 + 127 * noise)]  # Noisy colors
            elif style == "terrain":
                # Simple Perlin-like for land masses (inspired by procedural gen examples)
                height = 0.5 + 0.5 * math.sin(x / 10) + 0.3 * math.cos(y / 5) + random.random() * 0.2
                value = min(1, max(0, height))
                lum[y, x] = int(value * 255)
                arr[y, x] = [0, int(255 * value) if value > 0.5 else 0, int(255 * (1 - value))]  # Green/blue terrain
            else:
                # Fallback random
                value = random.random()
                lum[y, x] = int(value * 255)
                arr[y, x] = [random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)]
    
    return arr, lum

@app.post("/")
async def generate(
    file: Optional[UploadFile] = File(None),
    scale: float = Form(0.08),
    char_width: int = Form(10),
    char_height: int = Form(18),
    font_size: int = Form(14),
    preset: str = Form("dense"),
    charset: Optional[str] = Form(None),
    diversity: float = Form(0.0),
    sample_method: str = Form("center"),
    dither: bool = Form(False),  # Now uses Floyd-Steinberg if True
    # dither_strength removed; integrated into algorithm
    color_mode: str = Form("rgb"),  # Unused currently; could expand to grayscale output
    palette: Optional[str] = Form(None),  # Now implemented
    invert: bool = Form(False),
    brightness: float = Form(1.0),
    contrast: float = Form(1.0),
    seed: Optional[int] = Form(None),
    style: Optional[str] = Form(None),  # New: procedural style (waves, radial, noise, terrain)
    target_width: int = Form(80),  # New: char grid width for procedural
    target_height: int = Form(20),  # New: char grid height for procedural
    output_mode: str = Form("image"),  # New: "image" for PNG, "text" for plain ASCII
    font_file: Optional[UploadFile] = File(None),  # New: optional custom font upload
):
    if seed is not None:
        random.seed(seed)
        np.random.seed(seed)

    if charset is None:
        charset = CHAR_PRESETS.get(preset, CHAR_PRESETS["dense"])

    arr:
