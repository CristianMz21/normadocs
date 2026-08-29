"""
Cotización Realista - Análisis COMPLETO de los 3 proyectos.
"""

from PIL import Image, ImageDraw, ImageFont

_DARK_BLUE = (30, 41, 64)
_ACCENT = (230, 126, 34)
_LIGHT_GRAY = (240, 240, 240)
_WHITE = (255, 255, 255)
_GREEN = (46, 204, 113)
_RED = (231, 76, 60)
_BLUE = (52, 152, 219)
_PURPLE = (155, 89, 182)
_WIDTH = 1240
_HEIGHT = 1754
_DAYS_PER_WEEK = 7


def load_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    """Carga fuente DejaVu o default."""
    try:
        if bold:
            path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
            return ImageFont.truetype(path, size)
        return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", size)
    except Exception:
        return ImageFont.load_default()


def _money(cop: int) -> str:
    return f"${cop:,}".replace(",", ".")


def _duration(days: float = 0.0, months: int = 0) -> str:
    if months:
        return f"{months} mes"
    if days >= _DAYS_PER_WEEK:
        return f"{days / _DAYS_PER_WEEK:g} sem"
    if days == 1:
        return f"{days:g} día"
    return f"{days:g} días"


def _item(
    desc: str, qty: int, unit: str, cop: int, duration: str
) -> tuple[str, str, str, str, str, str]:
    return (desc, str(qty), unit, _money(cop), _money(cop * qty), duration)


def _get_fonts() -> dict[str, ImageFont.FreeTypeFont]:
    return {
        "title": load_font(20, bold=True),
        "header": load_font(11, bold=True),
        "item": load_font(8),
        "price": load_font(8, bold=True),
        "total": load_font(14, bold=True),
        "note": load_font(8),
        "small": load_font(7),
    }


def _draw_title(draw: ImageDraw.ImageDraw, fonts: dict, width: int) -> None:
    draw.text(
        (width // 2, 25),
        "COTIZACIÓN REALISTA - ANÁLISIS COMPLETO",
        fill=_DARK_BLUE,
        anchor="mm",
        font=fonts["title"],
    )
    draw.text(
        (width // 2, 45),
        "Proyecto Shoppipai - 3 Proyectos con Diferentes Tecnologías",
        fill=_DARK_BLUE,
        anchor="mm",
        font=fonts["item"],
    )


def _draw_info(draw: ImageDraw.ImageDraw, fonts: dict, width: int) -> int:
    info_y = 60
    draw.rectangle(
        [(40, info_y), (width - 40, info_y + 50)],
        fill=_LIGHT_GRAY,
        outline=_DARK_BLUE,
        width=2,
    )
    info_items = [
        ("Cliente:", "Sra. Luisa Delgado - Tienda de Calzado"),
        (
            "Proyectos:",
            "1) Backend Django  2) Dashboard Next.js  3) Storefront React",
        ),
        ("Fecha:", "26 de marzo de 2026 | Validez: 30 días"),
    ]
    y = info_y + 8
    for label, value in info_items:
        draw.text((50, y), label, fill=_DARK_BLUE, anchor="lm", font=fonts["header"])
        draw.text((155, y), value, fill=_DARK_BLUE, anchor="lm", font=fonts["item"])
        y += 14
    return info_y


def _draw_status(draw: ImageDraw.ImageDraw, fonts: dict, width: int, info_y: int) -> int:
    status_y = info_y + 58
    draw.rectangle(
        [(40, status_y), (width - 40, status_y + 40)],
        fill=(255, 240, 240),
        outline=_RED,
        width=2,
    )
    draw.text(
        (50, status_y + 10),
        "ANÁLISIS DE ESTADO ACTUAL:",
        fill=_RED,
        anchor="lm",
        font=fonts["header"],
    )
    draw.text(
        (50, status_y + 25),
        "Backend Django: 95% | Dashboard Next.js: 85% | Storefront React: 60-65% (INCOMPLETO)",
        fill=_DARK_BLUE,
        anchor="lm",
        font=fonts["note"],
    )
    draw.text(
        (50, status_y + 36),
        "El STOREFRONT es el mas incompleto - Falta checkout, pagos, busqueda y mas",
        fill=_RED,
        anchor="lm",
        font=fonts["small"],
    )
    return status_y


def _draw_table_header(
    draw: ImageDraw.ImageDraw, fonts: dict, width: int, status_y: int
) -> tuple[int, list[int], int]:
    table_start_y = status_y + 50
    col_widths = [380, 70, 85, 145, 145, 105]
    headers = [
        "Descripción del Trabajo",
        "Cant.",
        "Unidad",
        "Precio Unit. (COP)",
        "Precio Total (COP)",
        "Tiempo",
    ]
    header_height = 24
    draw.rectangle(
        [(40, table_start_y), (width - 40, table_start_y + header_height)],
        fill=_DARK_BLUE,
    )
    x = 50
    for i, header in enumerate(headers):
        draw.text(
            (x, table_start_y + 12),
            header,
            fill=_WHITE,
            anchor="lm",
            font=fonts["header"],
        )
        x += col_widths[i]
    return table_start_y, col_widths, header_height


def _build_items() -> list[tuple[str, str, str, str, str, str]]:
    # Prices are numeric COP; totals are derived (qty * unit price).
    sp = ("", "", "", "", "", "")
    return [
        ("PROYECTO 1: BACKEND DJANGO (95% completo)", "", "", "", "", ""),
        _item("Analisis de requisitos y ajustes de atributos", 1, "Global", 200_000, _duration(2)),
        _item("Personalizacion de modelos (tallas, anchos)", 1, "Global", 250_000, _duration(2)),
        _item("Integracion WhatsApp (NO existe)", 1, "Global", 1_500_000, _duration(14)),
        _item("Ajustes de API para shoe store", 1, "Global", 150_000, _duration(1)),
        sp,
        ("PROYECTO 2: DASHBOARD NEXT.JS (85% completo)", "", "", "", "", ""),
        _item("Completar paginas stub (reviews, settings)", 1, "Global", 300_000, _duration(3)),
        _item("Metricas especificas para calzado", 1, "Global", 200_000, _duration(2)),
        _item("Reportes personalizados de ventas", 1, "Global", 250_000, _duration(2)),
        _item("Integracion con WhatsApp (frontend)", 1, "Global", 200_000, _duration(2)),
        sp,
        ("PROYECTO 3: STOREFRONT REACT (60% - MUCHO POR HACER)", "", "", "", "", ""),
        _item("Completar CHECKOUT flow completo", 1, "Global", 1_200_000, _duration(14)),
        _item("Integrar UI de pagos (Stripe/Wompi)", 1, "Global", 800_000, _duration(10.5)),
        _item("Implementar pagina de busqueda", 1, "Global", 400_000, _duration(4)),
        _item("Completar detalle producto (galeria, tallas)", 1, "Global", 500_000, _duration(4)),
        _item("Carrito persistencia y sincronizacion", 1, "Global", 300_000, _duration(2)),
        _item("Sistema de cupones/descuentos", 1, "Global", 250_000, _duration(2)),
        _item("Rastreo de pedidos para cliente", 1, "Global", 350_000, _duration(3)),
        _item("Politicas de envio configurables", 1, "Global", 150_000, _duration(1)),
        _item("Responsive mobile optimizations", 1, "Global", 400_000, _duration(3)),
        sp,
        ("INTEGRACIÓN DE LOS 3 PROYECTOS", "", "", "", "", ""),
        _item("Configurar CORS y API connections", 1, "Global", 150_000, _duration(1)),
        _item("Integrar frontend con backend APIs", 1, "Global", 300_000, _duration(3)),
        _item("Despliegue produccion (3 ambientes)", 1, "Global", 400_000, _duration(2)),
        _item("SSL + Dominio + CDN Cloudflare", 1, "Global", 150_000, _duration(1)),
        sp,
        ("QA, PRUEBAS Y DOCUMENTACIÓN", "", "", "", "", ""),
        _item("Pruebas de integracion completas", 1, "Global", 500_000, _duration(4)),
        _item("Manuales de usuario (3 docs)", 1, "Global", 250_000, _duration(2)),
        _item("Documentacion tecnica de cambios", 1, "Global", 150_000, _duration(1)),
        _item("Capacitacion (4 sesiones 2h)", 4, "Sesión", 150_000, _duration(2)),
        sp,
        ("SOPORTE POST-LANZAMIENTO", "", "", "", "", ""),
        _item("Soporte 90 dias (ajustes, debugging)", 3, "Mes", 400_000, _duration(months=3)),
    ]


def _section_bg(name: str) -> tuple[int, int, int]:
    if "BACKEND" in name:
        return _BLUE
    if "DASHBOARD" in name:
        return _GREEN
    if "STOREFRONT" in name:
        return _ACCENT
    if "INTEGRACIÓN" in name:
        return _PURPLE
    return _DARK_BLUE


def _render_rows(
    draw: ImageDraw.ImageDraw,
    start_y: int,
    items: list[tuple[str, str, str, str, str, str]],
    col_widths: list[int],
    fonts: dict,
    row_height: int,
) -> int:
    section_headers = [item[0] for item in items if item[0] and not item[1]]
    y = start_y
    for i, item in enumerate(items):
        if item[0] in section_headers:
            bg_color = _section_bg(item[0])
            draw.rectangle([(40, y), (_WIDTH - 40, y + row_height)], fill=bg_color)
            draw.text(
                (50, y + row_height // 2),
                item[0],
                fill=_WHITE,
                anchor="lm",
                font=fonts["header"],
            )
            y += row_height
            continue
        if item[0] == "":
            y += 4
            continue
        bg_color = _LIGHT_GRAY if i % 2 == 0 else _WHITE
        draw.rectangle([(40, y), (_WIDTH - 40, y + row_height)], fill=bg_color)
        x = 50
        for j, cell in enumerate(item):
            text_color = _GREEN if j == 4 else _DARK_BLUE
            font = fonts["price"] if j in [3, 4] else fonts["item"]
            draw.text(
                (x, y + row_height // 2 - 2),
                cell,
                fill=text_color,
                anchor="lm",
                font=font,
            )
            x += col_widths[j]
        draw.line(
            [(40, y + row_height), (_WIDTH - 40, y + row_height)],
            fill=(200, 200, 200),
            width=1,
        )
        y += row_height
    return y


def _draw_total(draw: ImageDraw.ImageDraw, fonts: dict, width: int, y: int) -> int:
    y += 5
    draw.rectangle([(40, y), (width - 40, y + 30)], fill=_DARK_BLUE)
    draw.text(
        (50, y + 15),
        "VALOR TOTAL REALISTA (3 PROYECTOS):",
        fill=_WHITE,
        anchor="lm",
        font=fonts["total"],
    )
    draw.text((700, y + 15), "$10.800.000 COP", fill=_GREEN, anchor="lm", font=fonts["total"])
    draw.text((950, y + 15), "~14 semanas", fill=_WHITE, anchor="lm", font=fonts["header"])
    return y


def _draw_timeline(draw: ImageDraw.ImageDraw, fonts: dict, width: int, y: int) -> int:
    timeline_y = y + 40
    draw.rectangle(
        [(40, timeline_y), (width - 40, timeline_y + 32)],
        fill=_LIGHT_GRAY,
        outline=_DARK_BLUE,
        width=1,
    )
    draw.text(
        (50, timeline_y + 8),
        "DESGLOSE POR PROYECTO:",
        fill=_DARK_BLUE,
        anchor="lm",
        font=fonts["header"],
    )
    phases = [
        "Backend: 2.5 sem",
        "Dashboard: 1 sem",
        "Storefront: 6 sem",
        "Integración: 1 sem",
        "QA: 2 sem",
    ]
    px = 50
    for phase in phases:
        draw.text(
            (px, timeline_y + 20),
            f"• {phase}",
            fill=_DARK_BLUE,
            anchor="lm",
            font=fonts["note"],
        )
        px += 220
    return timeline_y


def _draw_payment(draw: ImageDraw.ImageDraw, fonts: dict, width: int, timeline_y: int) -> None:
    pay_y = timeline_y + 45
    draw.text(
        (width // 2, pay_y), "FORMA DE PAGO", fill=_DARK_BLUE, anchor="mm", font=fonts["header"]
    )
    pay_y += 20
    pay_items = [
        ("ANTICIPO", "30%", "$3.240.000", "Al firma del contrato"),
        ("SEGUNDA", "30%", "$3.240.000", "Al entregar storefront"),
        ("TERCERA", "25%", "$2.700.000", "Al entregar dashboard"),
        ("FINAL", "15%", "$1.620.000", "Tras capacitación"),
    ]
    pay_box_width = 280
    x = 50
    for title, pct, amount, moment in pay_items:
        draw.rectangle(
            [(x, pay_y), (x + pay_box_width, pay_y + 58)],
            fill=_LIGHT_GRAY,
            outline=_DARK_BLUE,
            width=2,
        )
        draw.rectangle([(x, pay_y), (x + pay_box_width, pay_y + 16)], fill=_DARK_BLUE)
        draw.text((x + 10, pay_y + 9), title, fill=_WHITE, anchor="lm", font=fonts["header"])
        draw.text((x + 10, pay_y + 22), pct, fill=_ACCENT, anchor="lm", font=fonts["price"])
        draw.text((x + 10, pay_y + 34), amount, fill=_GREEN, anchor="lm", font=fonts["price"])
        draw.text((x + 10, pay_y + 46), moment, fill=_DARK_BLUE, anchor="lm", font=fonts["note"])
        x += pay_box_width + 15


def _draw_footer(draw: ImageDraw.ImageDraw, fonts: dict, width: int, height: int) -> None:
    footer_y = height - 35
    draw.line([(40, footer_y), (width - 40, footer_y)], fill=_DARK_BLUE, width=2)
    draw.text(
        (width // 2, footer_y + 12),
        "Mackroph Solutions | Soluciones Tecnológicas | NIT: 1234567890",
        fill=_DARK_BLUE,
        anchor="mm",
        font=fonts["note"],
    )


def create_cotizacion() -> None:
    """Genera imagen de cotización."""
    img = Image.new("RGB", (_WIDTH, _HEIGHT), _WHITE)
    draw = ImageDraw.Draw(img)
    fonts = _get_fonts()

    _draw_title(draw, fonts, _WIDTH)
    info_y = _draw_info(draw, fonts, _WIDTH)
    status_y = _draw_status(draw, fonts, _WIDTH, info_y)
    table_start_y, col_widths, header_h = _draw_table_header(draw, fonts, _WIDTH, status_y)

    items = _build_items()
    row_height = 20
    start_y = table_start_y + header_h + 2
    y = _render_rows(draw, start_y, items, col_widths, fonts, row_height)

    y = _draw_total(draw, fonts, _WIDTH, y)
    timeline_y = _draw_timeline(draw, fonts, _WIDTH, y)
    _draw_payment(draw, fonts, _WIDTH, timeline_y)
    _draw_footer(draw, fonts, _WIDTH, _HEIGHT)

    output_path = "/home/mackroph/Projectos/Learning/APAScript/IDocs/image/diagrama_cotizacion.png"
    img.save(output_path, "PNG", dpi=(150, 150))
    print(f"Cotización saved: {output_path}")
    print("Total: $10.800.000 COP | ~14 semanas")


if __name__ == "__main__":
    create_cotizacion()
