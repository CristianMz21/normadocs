"""
Cotización Realista - Análisis COMPLETO de los 3 proyectos
"""

from PIL import Image, ImageDraw, ImageFont


def load_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    try:
        if bold:
            return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", size)
        return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", size)
    except Exception:
        return ImageFont.load_default()


def create_cotizacion():
    width, height = 1240, 1754
    img = Image.new("RGB", (width, height), (255, 255, 255))
    draw = ImageDraw.Draw(img)

    dark_blue = (30, 41, 64)
    accent = (230, 126, 34)
    light_gray = (240, 240, 240)
    white = (255, 255, 255)
    green = (46, 204, 113)
    red = (231, 76, 60)

    title_font = load_font(20, True)
    header_font = load_font(11, True)
    item_font = load_font(8)
    price_font = load_font(8, True)
    total_font = load_font(14, True)
    note_font = load_font(8)
    small_font = load_font(7)

    # Title
    draw.text(
        (width // 2, 25),
        "COTIZACIÓN REALISTA - ANÁLISIS COMPLETO",
        fill=dark_blue,
        anchor="mm",
        font=title_font,
    )
    draw.text(
        (width // 2, 45),
        "Proyecto Shoppipai - 3 Proyectos con Diferentes Tecnologías",
        fill=dark_blue,
        anchor="mm",
        font=item_font,
    )

    # Info
    info_y = 60
    draw.rectangle(
        [(40, info_y), (width - 40, info_y + 50)], fill=light_gray, outline=dark_blue, width=2
    )

    info_items = [
        ("Cliente:", "Sra. Luisa Delgado - Tienda de Calzado"),
        ("Proyectos:", "1) Backend Django  2) Dashboard Next.js  3) Storefront React"),
        ("Fecha:", "26 de marzo de 2026 | Validez: 30 días"),
    ]
    y = info_y + 8
    for label, value in info_items:
        draw.text((50, y), label, fill=dark_blue, anchor="lm", font=header_font)
        draw.text((155, y), value, fill=dark_blue, anchor="lm", font=item_font)
        y += 14

    # Status summary
    status_y = info_y + 58
    draw.rectangle(
        [(40, status_y), (width - 40, status_y + 40)], fill=(255, 240, 240), outline=red, width=2
    )
    draw.text(
        (50, status_y + 10), "ANÁLISIS DE ESTADO ACTUAL:", fill=red, anchor="lm", font=header_font
    )
    draw.text(
        (50, status_y + 25),
        "Backend Django: 95% | Dashboard Next.js: 85% | Storefront React: 60-65% (INCOMPLETO)",
        fill=dark_blue,
        anchor="lm",
        font=note_font,
    )
    draw.text(
        (50, status_y + 36),
        "⚠ El STOREFRONT es el más incompleto - Falta checkout, pagos, búsqueda y más",
        fill=red,
        anchor="lm",
        font=small_font,
    )

    # Table header
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
        [(40, table_start_y), (width - 40, table_start_y + header_height)], fill=dark_blue
    )

    x = 50
    for i, header in enumerate(headers):
        draw.text((x, table_start_y + 12), header, fill=white, anchor="lm", font=header_font)
        x += col_widths[i]

    row_height = 20
    y = table_start_y + header_height + 2

    # COMPLETE breakdown based on actual analysis
    items = [
        # Project 1: Backend Django (95% complete - small adaptations)
        ("PROYECTO 1: BACKEND DJANGO (95% completo)", "", "", "", "", ""),
        (
            "Análisis de requisitos y ajustes de atributos",
            "1",
            "Global",
            "$200.000",
            "$200.000",
            "2 días",
        ),
        (
            "Personalización de modelos (tallas, anchos)",
            "1",
            "Global",
            "$250.000",
            "$250.000",
            "2 días",
        ),
        ("Integración WhatsApp (NO existe)", "1", "Global", "$1.500.000", "$1.500.000", "2 sem"),
        ("Ajustes de API para shoe store", "1", "Global", "$150.000", "$150.000", "1 día"),
        ("", "", "", "", "", ""),
        # Project 2: Dashboard Next.js (85% complete - some stubs)
        ("PROYECTO 2: DASHBOARD NEXT.JS (85% completo)", "", "", "", "", ""),
        (
            "Completar páginas stub (reviews, settings)",
            "1",
            "Global",
            "$300.000",
            "$300.000",
            "3 días",
        ),
        ("Métricas específicas para calzado", "1", "Global", "$200.000", "$200.000", "2 días"),
        ("Reportes personalizados de ventas", "1", "Global", "$250.000", "$250.000", "2 días"),
        ("Integración con WhatsApp (frontend)", "1", "Global", "$200.000", "$200.000", "2 días"),
        ("", "", "", "", "", ""),
        # Project 3: Storefront React (60% COMPLETE - MOST WORK NEEDED)
        ("PROYECTO 3: STOREFRONT REACT (60% - MUCHO POR HACER)", "", "", "", "", ""),
        ("Completar CHECKOUT flow completo", "1", "Global", "$1.200.000", "$1.200.000", "2 sem"),
        ("Integrar UI de pagos (Stripe/Wompi)", "1", "Global", "$800.000", "$800.000", "1.5 sem"),
        ("Implementar página de búsqueda", "1", "Global", "$400.000", "$400.000", "4 días"),
        (
            "Completar detalle producto (galería, tallas)",
            "1",
            "Global",
            "$500.000",
            "$500.000",
            "4 días",
        ),
        ("Carrito persistencia y sincronización", "1", "Global", "$300.000", "$300.000", "2 días"),
        ("Sistema de cupones/descuentos", "1", "Global", "$250.000", "$250.000", "2 días"),
        ("Rastreo de pedidos para cliente", "1", "Global", "$350.000", "$350.000", "3 días"),
        ("Políticas de envío configurables", "1", "Global", "$150.000", "$150.000", "1 día"),
        ("Responsive mobile optimizations", "1", "Global", "$400.000", "$400.000", "3 días"),
        ("", "", "", "", "", ""),
        # Integration & Deploy
        ("INTEGRACIÓN DE LOS 3 PROYECTOS", "", "", "", "", ""),
        ("Configurar CORS y API connections", "1", "Global", "$150.000", "$150.000", "1 día"),
        ("Integrar frontend con backend APIs", "1", "Global", "$300.000", "$300.000", "3 días"),
        ("Despliegue producción (3 ambientes)", "1", "Global", "$400.000", "$400.000", "2 días"),
        ("SSL + Dominio + CDN Cloudflare", "1", "Global", "$150.000", "$150.000", "1 día"),
        ("", "", "", "", "", ""),
        # QA & Docs
        ("QA, PRUEBAS Y DOCUMENTACIÓN", "", "", "", "", ""),
        ("Pruebas de integración completas", "1", "Global", "$500.000", "$500.000", "4 días"),
        ("Manuales de usuario (3 docs)", "1", "Global", "$250.000", "$250.000", "2 días"),
        ("Documentación técnica de cambios", "1", "Global", "$150.000", "$150.000", "1 día"),
        ("Capacitación (4 sesiones 2h)", "4", "Sesión", "$150.000", "$600.000", "2 días"),
        ("", "", "", "", "", ""),
        # Support
        ("SOPORTE POST-LANZAMIENTO", "", "", "", "", ""),
        ("Soporte 90 días (ajustes, debugging)", "3", "Mes", "$400.000", "$1.200.000", "3 mes"),
    ]

    section_headers = [
        "PROYECTO 1: BACKEND DJANGO (95% completo)",
        "PROYECTO 2: DASHBOARD NEXT.JS (85% completo)",
        "PROYECTO 3: STOREFRONT REACT (60% - MUCHO POR HACER)",
        "INTEGRACIÓN DE LOS 3 PROYECTOS",
        "QA, PRUEBAS Y DOCUMENTACIÓN",
        "SOPORTE POST-LANZAMIENTO",
    ]

    for i, item in enumerate(items):
        if item[0] in section_headers:
            # Different colors for different projects
            if "BACKEND" in item[0]:
                bg_color = (52, 152, 219)  # Blue
            elif "DASHBOARD" in item[0]:
                bg_color = (46, 204, 113)  # Green
            elif "STOREFRONT" in item[0]:
                bg_color = (230, 126, 34)  # Orange
            elif "INTEGRACIÓN" in item[0]:
                bg_color = (155, 89, 182)  # Purple
            else:
                bg_color = dark_blue

            draw.rectangle([(40, y), (width - 40, y + row_height)], fill=bg_color)
            draw.text((50, y + row_height // 2), item[0], fill=white, anchor="lm", font=header_font)
            y += row_height
        elif item[0] == "":
            y += 4
        else:
            bg_color = light_gray if i % 2 == 0 else white
            draw.rectangle([(40, y), (width - 40, y + row_height)], fill=bg_color)

            x = 50
            for j, cell in enumerate(item):
                text_color = green if j == 4 else dark_blue
                font = price_font if j in [3, 4] else item_font
                draw.text(
                    (x, y + row_height // 2 - 2), cell, fill=text_color, anchor="lm", font=font
                )
                x += col_widths[j]

            draw.line(
                [(40, y + row_height), (width - 40, y + row_height)], fill=(200, 200, 200), width=1
            )
            y += row_height

    # Total
    y += 5
    draw.rectangle([(40, y), (width - 40, y + 30)], fill=dark_blue)
    draw.text(
        (50, y + 15),
        "VALOR TOTAL REALISTA (3 PROYECTOS):",
        fill=white,
        anchor="lm",
        font=total_font,
    )
    draw.text((700, y + 15), "$10.800.000 COP", fill=green, anchor="lm", font=total_font)
    draw.text((950, y + 15), "~14 semanas", fill=white, anchor="lm", font=header_font)

    # Timeline
    timeline_y = y + 40
    draw.rectangle(
        [(40, timeline_y), (width - 40, timeline_y + 32)],
        fill=light_gray,
        outline=dark_blue,
        width=1,
    )
    draw.text(
        (50, timeline_y + 8),
        "DESGLOSE POR PROYECTO:",
        fill=dark_blue,
        anchor="lm",
        font=header_font,
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
        draw.text((px, timeline_y + 20), f"• {phase}", fill=dark_blue, anchor="lm", font=note_font)
        px += 220

    # Payment
    pay_y = timeline_y + 45
    draw.text((width // 2, pay_y), "FORMA DE PAGO", fill=dark_blue, anchor="mm", font=header_font)

    pay_y += 20
    pay_items = [
        ("ANTICIPO", "30%", "$3.240.000", "Al firma del contrato", "Inicio del proyecto"),
        ("SEGUNDA", "30%", "$3.240.000", "Al entregar storefront", "Checkout y pagos operativos"),
        ("TERCERA", "25%", "$2.700.000", "Al entregar dashboard", "Admin completo"),
        ("FINAL", "15%", "$1.620.000", "Tras capacitación", "Sistema en producción"),
    ]

    pay_box_width = 280
    x = 50
    for title, pct, amount, moment, _deliverable in pay_items:
        draw.rectangle(
            [(x, pay_y), (x + pay_box_width, pay_y + 58)],
            fill=light_gray,
            outline=dark_blue,
            width=2,
        )
        draw.rectangle([(x, pay_y), (x + pay_box_width, pay_y + 16)], fill=dark_blue)
        draw.text((x + 10, pay_y + 9), title, fill=white, anchor="lm", font=header_font)
        draw.text((x + 10, pay_y + 22), pct, fill=accent, anchor="lm", font=price_font)
        draw.text((x + 10, pay_y + 34), amount, fill=green, anchor="lm", font=price_font)
        draw.text((x + 10, pay_y + 46), moment, fill=dark_blue, anchor="lm", font=note_font)
        x += pay_box_width + 15

    # Footer
    footer_y = height - 35
    draw.line([(40, footer_y), (width - 40, footer_y)], fill=dark_blue, width=2)
    draw.text(
        (width // 2, footer_y + 12),
        "Mackroph Solutions | Soluciones Tecnológicas | NIT: 1234567890",
        fill=dark_blue,
        anchor="mm",
        font=note_font,
    )

    output_path = "/home/mackroph/Projectos/Learning/APAScript/IDocs/image/diagrama_cotizacion.png"
    img.save(output_path, "PNG", dpi=(150, 150))
    print(f"Cotización saved: {output_path}")
    print("Total: $10.800.000 COP | ~14 semanas")


if __name__ == "__main__":
    create_cotizacion()
