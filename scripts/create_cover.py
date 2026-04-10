"""Cover image generator for proposals."""

from __future__ import annotations

import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


def load_font(path: str, size: int) -> ImageFont.FreeTypeFont:
    """Load a font from file, fallback to default on error."""
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default()


def create_cover(output_dir: str | None = None) -> None:
    """Create the cover image and convert to PDF."""
    if output_dir is None:
        output_dir = "/home/mackroph/Projectos/Learning/APAScript/IDocs/image"

    output_path = Path(output_dir)
    logo_path = output_path / "logo_mackroph.png"
    cover_png = output_path / "cover_cover.png"

    width, height = 800, 600
    img = Image.new("RGB", (width, height), (255, 255, 255))
    draw = ImageDraw.Draw(img)

    dark_blue = (30, 41, 64)
    cyan = (0, 180, 220)
    light_gray = (240, 240, 240)

    draw.rectangle([(0, 0), (250, height)], fill=light_gray)

    if logo_path.exists():
        logo_img = Image.open(logo_path)
        logo_img = logo_img.resize((220, 52))
        img.paste(logo_img, (15, 40))

    font_paths = (
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    )
    font_company = load_font(font_paths[0], 18)
    font_tagline = load_font(font_paths[1], 10)
    font_title = load_font(font_paths[0], 36)
    font_subtitle = load_font(font_paths[1], 22)
    font_small = load_font(font_paths[1], 12)
    font_label = load_font(font_paths[0], 12)

    draw.text((15, 105), "MACKROPH SOLUTIONS", font=font_company, fill=dark_blue)
    draw.text((15, 128), '"Transformamos ideas en', font=font_tagline, fill=(100, 100, 100))
    draw.text((15, 143), 'soluciones tecnologicas"', font=font_tagline, fill=(100, 100, 100))
    draw.line([(260, 50), (260, height - 50)], fill=cyan, width=3)
    draw.text((290, 120), "PROPUESTA", font=font_title, fill=dark_blue)
    draw.text((290, 170), "TECNICA Y", font=font_title, fill=dark_blue)
    draw.text((290, 220), "ECONOMICA", font=font_title, fill=cyan)
    draw.text((290, 290), "Sistema de Comercio Electronico", font=font_subtitle, fill=(80, 80, 80))
    draw.text((290, 320), '"Shoppipai"', font=font_subtitle, fill=dark_blue)

    info_y = 420
    draw.rectangle([(280, info_y), (780, info_y + 140)], outline=cyan, width=2)

    info_items = [
        ("Fecha:", "26 de marzo de 2026"),
        ("Para:", "Sra. Luisa Delgado - Propietaria del Negocio de Calzado"),
        ("De:", "Cristian Zaid Arellano Munoz - Mackroph Solutions"),
        ("Ref:", "Propuesta Tecnica y Economica - Proyecto Shoppipai"),
    ]

    y = info_y + 15
    for label, value in info_items:
        draw.text((290, y), label, font=font_label, fill=dark_blue)
        draw.text((380, y), value, font=font_small, fill=(60, 60, 60))
        y += 25

    draw.line([(0, height - 80), (width, height - 80)], fill=light_gray, width=1)
    draw.text(
        (15, height - 60), "EV01 - GA2-220501094-AA4-EV02", font=font_small, fill=(100, 100, 100)
    )
    draw.text(
        (15, height - 40),
        "Analisis y Desarrollo de Software - Ficha 3336101",
        font=font_small,
        fill=(100, 100, 100),
    )
    draw.text((700, height - 50), "Pagina 1", font=font_small, fill=(100, 100, 100))

    img.save(str(cover_png), "PNG")
    print(f"Cover PNG created: {cover_png}")
    print("Converting to PDF with LibreOffice...")

    result = subprocess.run(
        [
            "libreoffice",
            "--headless",
            "--convert-to",
            "pdf",
            "--outdir",
            str(output_path),
            str(cover_png),
        ],
        capture_output=True,
        text=True,
    )
    if result.returncode == 0:
        print("Cover PDF created successfully")
    else:
        print(f"Error: {result.stderr}")
    print("Cover created successfully")


if __name__ == "__main__":
    create_cover()
