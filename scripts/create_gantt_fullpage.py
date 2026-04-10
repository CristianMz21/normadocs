"""
Create a full-page Gantt chart using PIL
"""

from PIL import Image, ImageDraw, ImageFont


def load_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    """Load a font"""
    try:
        if bold:
            return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", size)
        return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", size)
    except Exception:
        return ImageFont.load_default()


def create_gantt_fullpage():
    """Create a full-page Gantt chart"""
    # A4 dimensions at 150 DPI
    width, height = 1240, 1754
    img = Image.new("RGB", (width, height), (255, 255, 255))
    draw = ImageDraw.Draw(img)

    # Colors
    dark_blue = (30, 41, 64)
    phase1 = (52, 152, 219)  # Blue - Analysis
    phase2 = (46, 204, 113)  # Green - Planning
    phase3 = (230, 126, 34)  # Orange - Execution
    phase4 = (155, 89, 182)  # Purple - Evaluation
    light_gray = (240, 240, 240)
    white = (255, 255, 255)
    grid_color = (200, 200, 200)

    # Fonts
    title_font = load_font(28, True)
    subtitle_font = load_font(16)
    phase_font = load_font(14, True)
    activity_font = load_font(12)
    week_font = load_font(11, True)
    legend_font = load_font(11)

    # Title - CENTERED
    draw.text((width // 2, 50), "DIAGRAMA DE GANTT", fill=dark_blue, anchor="mm", font=title_font)
    draw.text(
        (width // 2, 85),
        "PROYECTO SHOPPIPAI - Duración: 16 Semanas",
        fill=dark_blue,
        anchor="mm",
        font=subtitle_font,
    )

    # Layout constants
    left_margin = 200
    right_margin = 50
    top_margin = 130
    bottom_margin = 80

    # Timeline spans from left_margin to width - right_margin
    timeline_width = width - left_margin - right_margin  # Total width for 16 weeks
    week_width = timeline_width / 16  # Width per week

    # Week headers row
    week_header_y = top_margin
    week_header_h = 35

    # Draw week header background
    draw.rectangle(
        [(left_margin, week_header_y), (width - right_margin, week_header_y + week_header_h)],
        fill=light_gray,
        outline=dark_blue,
        width=2,
    )

    # Draw week labels S1-S16 centered in each column
    for i in range(16):
        x = left_margin + i * week_width + week_width // 2
        draw.text(
            (x, week_header_y + week_header_h // 2),
            f"S{i + 1}",
            fill=dark_blue,
            anchor="mm",
            font=week_font,
        )

    # Vertical grid lines
    for i in range(17):  # 0 to 16 inclusive
        x = left_margin + i * week_width
        draw.line(
            [(x, week_header_y + week_header_h), (x, height - bottom_margin)],
            fill=grid_color,
            width=1,
        )

    # Phase colors map
    phase_colors = {1: phase1, 2: phase2, 3: phase3, 4: phase4}

    # Phase data: (name, start_week, duration, activities)
    phases = [
        (
            "FASE 1: ANÁLISIS",
            1,
            4,
            [
                "Levantamiento de requisitos",
                "Diseño de arquitectura",
                "Modelado de base de datos",
                "Prototipos Figma",
            ],
        ),
        (
            "FASE 2: PLANEACIÓN",
            5,
            4,
            [
                "Diseño de API REST",
                "Configuración Docker",
                "Definición de modelos Django",
                "Planificación de Sprints",
            ],
        ),
        (
            "FASE 3: EJECUCIÓN",
            9,
            4,
            [
                "Módulo Usuarios",
                "Módulo Productos/Catálogo",
                "Módulo Carrito/Checkout",
                "Integración Wompi/PayU",
                "Configuración WhatsApp API",
            ],
        ),
        (
            "FASE 4: EVALUACIÓN",
            13,
            4,
            [
                "Pruebas unitarias",
                "Pruebas de integración",
                "UAT con cliente",
                "Despliegue en producción",
                "Capacitación y documentación",
            ],
        ),
    ]

    current_y = week_header_y + week_header_h + 10
    row_height = 50
    phase_spacing = 15

    phase_num = 1
    for phase_name, start_week, duration, activities in phases:
        phase_color = phase_colors[phase_num]
        phase_num += 1

        # Phase header - spans the full duration
        phase_start_x = left_margin + (start_week - 1) * week_width
        phase_end_x = left_margin + (start_week + duration - 1) * week_width + week_width

        header_height = 30
        draw.rectangle(
            [(left_margin, current_y), (phase_end_x, current_y + header_height)],
            fill=phase_color,
            outline=dark_blue,
            width=2,
        )
        draw.text(
            (left_margin + 10, current_y + header_height // 2),
            phase_name,
            fill=white,
            anchor="lm",
            font=phase_font,
        )
        current_y += header_height + 5

        # Draw activities for this phase
        for activity in activities:
            # Activity label on the left
            draw.text(
                (left_margin - 10, current_y + row_height // 2),
                activity,
                fill=dark_blue,
                anchor="rm",
                font=activity_font,
            )

            # Activity bar spans the same weeks as the phase
            bar_y = current_y + 5
            bar_height = row_height - 10
            bar_x = phase_start_x
            bar_width = duration * week_width

            draw.rectangle(
                [(bar_x, bar_y), (bar_x + bar_width, bar_y + bar_height)],
                fill=phase_color,
                outline=dark_blue,
                width=1,
            )

            # Horizontal separator
            draw.line(
                [
                    (left_margin, current_y + row_height),
                    (width - right_margin, current_y + row_height),
                ],
                fill=grid_color,
                width=1,
            )

            current_y += row_height

        current_y += phase_spacing

    # Legend at bottom
    legend_y = height - 60
    draw.rectangle(
        [(left_margin, legend_y), (width - right_margin, legend_y + 40)],
        fill=light_gray,
        outline=dark_blue,
        width=1,
    )

    legend_items = [
        (phase1, "Fase 1: Análisis"),
        (phase2, "Fase 2: Planeación"),
        (phase3, "Fase 3: Ejecución"),
        (phase4, "Fase 4: Evaluación"),
    ]

    x = left_margin + 30
    for color, label in legend_items:
        draw.rectangle(
            [(x, legend_y + 12), (x + 25, legend_y + 30)], fill=color, outline=dark_blue, width=1
        )
        draw.text((x + 35, legend_y + 21), label, fill=dark_blue, anchor="lm", font=legend_font)
        x += 250

    # Save
    output_path = "/home/mackroph/Projectos/Learning/APAScript/IDocs/image/gantt_chart.png"
    img.save(output_path, "PNG", dpi=(150, 150))
    print(f"Gantt chart saved: {output_path}")
    print(f"Dimensions: {width}x{height}")


if __name__ == "__main__":
    create_gantt_fullpage()
