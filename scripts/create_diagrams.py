#!/usr/bin/env python3
"""Generate PNG diagrams for the technical proposal."""

import os

from PIL import Image, ImageDraw, ImageFont

OUTPUT_DIR = "/home/mackroph/Projectos/Learning/APAScript/IDocs/image"
FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_BOLD_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def load_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    try:
        path = FONT_BOLD_PATH if bold else FONT_PATH
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default()


def create_architecture_diagram():
    """Create the system architecture diagram."""
    width, height = 900, 480
    img = Image.new("RGB", (width, height), (255, 255, 255))
    draw = ImageDraw.Draw(img)

    dark_blue = (30, 41, 64)
    client_color = (52, 152, 219)
    server_color = (46, 204, 113)
    db_color = (155, 89, 182)
    service_color = (230, 126, 34)
    redis_color = (41, 128, 185)
    whatsapp_color = (37, 155, 37)

    # Title
    draw.rectangle([(50, 15), (850, 60)], fill=dark_blue)
    draw.text(
        (450, 37),
        "ARQUITECTURA SHOPPIPAI",
        fill=(255, 255, 255),
        anchor="mm",
        font=load_font(22, True),
    )

    # Client box
    draw.rectangle([(50, 90), (260, 240)], fill=client_color)
    draw.text((155, 110), "CLIENTE", fill=(255, 255, 255), anchor="mm", font=load_font(16, True))
    draw.text((155, 145), "Dispositivos:", fill=(255, 255, 255), anchor="mm", font=load_font(11))
    draw.text((155, 170), "  - Smartphone", fill=(255, 255, 255), anchor="mm", font=load_font(10))
    draw.text((155, 190), "  - Computador", fill=(255, 255, 255), anchor="mm", font=load_font(10))
    draw.text((155, 210), "  - Tablet", fill=(255, 255, 255), anchor="mm", font=load_font(10))

    # Arrow line
    draw.line([(260, 165), (350, 165)], fill=dark_blue, width=3)
    draw.text((305, 150), "HTTPS/SSL", fill=dark_blue, anchor="mm", font=load_font(10))

    # Server box
    draw.rectangle([(350, 85), (620, 280)], fill=(255, 255, 255), outline=server_color, width=3)
    draw.text((485, 100), "SERVIDOR", fill=server_color, anchor="mm", font=load_font(14, True))

    # API REST
    draw.rectangle([(375, 120), (595, 160)], fill=server_color)
    draw.text(
        (485, 140), "API REST - Django", fill=(255, 255, 255), anchor="mm", font=load_font(12, True)
    )

    # PostgreSQL
    draw.rectangle([(375, 175), (595, 240)], fill=db_color)
    draw.text(
        (485, 195), "PostgreSQL 15", fill=(255, 255, 255), anchor="mm", font=load_font(12, True)
    )
    draw.text((485, 218), "Base de Datos", fill=(255, 255, 255), anchor="mm", font=load_font(10))

    # External services
    # Wompi
    draw.rectangle([(640, 85), (870, 145)], fill=service_color)
    draw.text(
        (755, 107), "Wompi / PayU", fill=(255, 255, 255), anchor="mm", font=load_font(11, True)
    )
    draw.text((755, 127), "(Pagos)", fill=(255, 255, 255), anchor="mm", font=load_font(10))

    # Redis
    draw.rectangle([(640, 155), (870, 215)], fill=redis_color)
    draw.text(
        (755, 177), "Redis (Celery)", fill=(255, 255, 255), anchor="mm", font=load_font(11, True)
    )
    draw.text((755, 197), "(Tareas Async)", fill=(255, 255, 255), anchor="mm", font=load_font(10))

    # WhatsApp
    draw.rectangle([(640, 225), (870, 285)], fill=whatsapp_color)
    draw.text(
        (755, 247), "WhatsApp API", fill=(255, 255, 255), anchor="mm", font=load_font(11, True)
    )
    draw.text((755, 267), "(Notificaciones)", fill=(255, 255, 255), anchor="mm", font=load_font(10))

    # Connection lines
    draw.line([(620, 115), (640, 115)], fill=service_color, width=2)
    draw.line([(620, 185), (640, 185)], fill=redis_color, width=2)
    draw.line([(595, 240), (755, 255)], fill=whatsapp_color, width=2)

    # Legend
    draw.rectangle([(50, 310), (850, 400)], fill=(240, 240, 240), outline=dark_blue, width=1)
    draw.text(
        (450, 325), "Tecnologias Utilizadas", fill=dark_blue, anchor="mm", font=load_font(14, True)
    )
    draw.text(
        (80, 355),
        "Frontend: HTML5, CSS3, JavaScript (Django Templates)",
        fill=(50, 50, 50),
        anchor="lm",
        font=load_font(10),
    )
    draw.text(
        (80, 375),
        "Backend: Python/Django REST Framework",
        fill=(50, 50, 50),
        anchor="lm",
        font=load_font(10),
    )
    draw.text(
        (500, 355),
        "Base de Datos: PostgreSQL 15",
        fill=(50, 50, 50),
        anchor="lm",
        font=load_font(10),
    )
    draw.text(
        (500, 375),
        "Pagos: Wompi/PayU  |  Notificaciones: WhatsApp API",
        fill=(50, 50, 50),
        anchor="lm",
        font=load_font(10),
    )

    img.save(os.path.join(OUTPUT_DIR, "diagrama_arquitectura.png"))
    print("Created diagrama_arquitectura.png")


def create_gantt_chart():
    """Create the Gantt chart with detailed activities."""
    width, height = 950, 500
    img = Image.new("RGB", (width, height), (255, 255, 255))
    draw = ImageDraw.Draw(img)

    dark_blue = (30, 41, 64)
    phase1 = (52, 152, 219)  # Blue - Analysis
    phase2 = (46, 204, 113)  # Green - Planning
    phase3 = (230, 126, 34)  # Orange - Execution
    phase4 = (155, 89, 182)  # Purple - Evaluation
    light_gray = (220, 220, 220)
    white = (255, 255, 255)

    # Title
    draw.text(
        (475, 25),
        "DIAGRAMA DE GANTT - PROYECTO SHOPPIPAI",
        fill=dark_blue,
        anchor="mm",
        font=load_font(18, True),
    )
    draw.text(
        (475, 50), "Duracion Total: 16 Semanas", fill=dark_blue, anchor="mm", font=load_font(12)
    )

    # Layout constants
    left_margin = 180
    start_x = 200
    week_width = 40
    timeline_end_x = start_x + 16 * week_width
    y_start = 85

    # Week header row
    draw.rectangle(
        [(left_margin - 5, y_start - 5), (timeline_end_x + 5, y_start + 25)],
        fill=light_gray,
        outline=dark_blue,
    )
    draw.text(
        (left_margin - 50, y_start + 10),
        "FASE",
        fill=dark_blue,
        anchor="mm",
        font=load_font(10, True),
    )

    for i in range(16):
        x = start_x + i * week_width
        draw.text(
            (x + 20, y_start + 10), f"S{i + 1}", fill=dark_blue, anchor="mm", font=load_font(9)
        )

    # Vertical grid lines
    for i in range(17):
        x = start_x + i * week_width
        draw.line([(x, y_start + 25), (x, 420)], fill=light_gray, width=1)

    # Phase data: (name, start_week, duration, color, activities)
    phases = [
        (
            "FASE 1: ANALISIS",
            1,
            4,
            phase1,
            [
                ("Levantamiento de requisitos", 1, 2),
                ("Disenio de arquitectura", 2, 2),
                ("Modelado de base de datos", 3, 2),
                ("Prototipos Figma", 3, 2),
            ],
        ),
        (
            "FASE 2: PLANEACION",
            5,
            4,
            phase2,
            [
                ("Disenio de API REST", 5, 2),
                ("Configuracion Docker", 6, 2),
                ("Definicion de modelos Django", 6, 3),
                ("Planificacion de Sprints", 7, 2),
            ],
        ),
        (
            "FASE 3: EJECUCION",
            9,
            4,
            phase3,
            [
                ("Modulo Usuarios", 9, 2),
                ("Modulo Productos/Catalogo", 9, 3),
                ("Modulo Carrito/Checkout", 10, 3),
                ("Integracion Wompi/PayU", 11, 2),
                ("Configuracion WhatsApp API", 12, 1),
            ],
        ),
        (
            "FASE 4: EVALUACION",
            13,
            4,
            phase4,
            [
                ("Pruebas unitarias", 13, 2),
                ("Pruebas de integracion", 14, 2),
                ("UAT con cliente", 14, 2),
                ("Despliegue en produccion", 15, 2),
                ("Capacitacion y documentacion", 15, 2),
            ],
        ),
    ]

    y = y_start + 35

    for phase_name, phase_start, phase_duration, phase_color, activities in phases:
        # Phase header bar
        bar_x = start_x + (phase_start - 1) * week_width
        bar_width = phase_duration * week_width

        draw.rectangle(
            [(left_margin - 5, y - 3), (bar_x + bar_width, y + 25)],
            fill=phase_color,
            outline=dark_blue,
            width=2,
        )
        draw.text(
            (left_margin - 50, y + 11),
            phase_name[:15],
            fill=dark_blue,
            anchor="mm",
            font=load_font(9, True),
        )
        draw.text(
            (bar_x + bar_width // 2, y + 11),
            phase_name,
            fill=white,
            anchor="mm",
            font=load_font(9, True),
        )

        y += 30

        # Activities
        for act_name, act_start, act_duration in activities:
            # Activity label
            draw.text((15, y + 5), act_name[:25], fill=(50, 50, 50), anchor="lm", font=load_font(9))

            # Activity bar
            act_x = start_x + (act_start - 1) * week_width
            act_width = act_duration * week_width - 3
            draw.rectangle(
                [(act_x, y), (act_x + act_width, y + 18)], fill=phase_color, outline=phase_color
            )
            draw.rectangle([(act_x, y), (act_x + act_width, y + 18)], outline=dark_blue, width=1)

            y += 22

        y += 15

    # Legend
    legend_y = 435
    draw.line([(20, legend_y), (930, legend_y)], fill=dark_blue, width=1)
    draw.text(
        (475, legend_y + 12), "LEYENDA", fill=dark_blue, anchor="mm", font=load_font(11, True)
    )

    legend_items = [
        ("Fase 1: Analisis", phase1),
        ("Fase 2: Planeacion", phase2),
        ("Fase 3: Ejecucion", phase3),
        ("Fase 4: Evaluacion", phase4),
    ]

    for i, (label, color) in enumerate(legend_items):
        x = 100 + i * 200
        draw.rectangle(
            [(x, legend_y + 30), (x + 20, legend_y + 50)], fill=color, outline=dark_blue, width=1
        )
        draw.text((x + 30, legend_y + 40), label, fill=(50, 50, 50), anchor="lm", font=load_font(9))

    # Footer note
    draw.text(
        (475, legend_y + 70),
        "Nota: Las barras representan la duracion de cada actividad en semanas",
        fill=(100, 100, 100),
        anchor="mm",
        font=load_font(9),
    )

    img.save(os.path.join(OUTPUT_DIR, "diagrama_gantt.png"))
    print("Created diagrama_gantt.png")


def create_profile_card():
    """Create the developer profile card."""
    width, height = 520, 300
    img = Image.new("RGB", (width, height), (255, 255, 255))
    draw = ImageDraw.Draw(img)

    dark_blue = (30, 41, 64)

    draw.rectangle([(0, 0), (width - 1, height - 1)], outline=dark_blue, width=3)
    draw.rectangle([(0, 0), (width, 50)], fill=dark_blue)
    draw.text(
        (260, 18),
        "CRISTIAN ZAID ARELLANO MUÑOZ",
        fill=(255, 255, 255),
        anchor="mm",
        font=load_font(14, True),
    )
    draw.text(
        (260, 38),
        "Lider Tecnico / Desarrollador Backend",
        fill=(255, 255, 255),
        anchor="mm",
        font=load_font(10),
    )

    y = 65
    draw.text((25, y), "Formacion:", fill=dark_blue, anchor="lm", font=load_font(11, True))
    y += 18
    draw.text(
        (40, y),
        "Programa: Analisis y Desarrollo de Software (ADSO)",
        fill=(50, 50, 50),
        anchor="lm",
        font=load_font(10),
    )
    y += 16
    draw.text((40, y), "Ficha: 3336101", fill=(50, 50, 50), anchor="lm", font=load_font(10))
    y += 16
    draw.text(
        (40, y),
        "Centro: SENA - Centro de Materiales y Ensayos",
        fill=(50, 50, 50),
        anchor="lm",
        font=load_font(10),
    )

    y += 28
    draw.text((25, y), "Especializacion:", fill=dark_blue, anchor="lm", font=load_font(11, True))
    y += 18
    draw.text(
        (40, y),
        "Desarrollo Backend con Python/Django",
        fill=(50, 50, 50),
        anchor="lm",
        font=load_font(10),
    )
    y += 16
    draw.text(
        (40, y),
        "Arquitectura de sistemas y bases de datos",
        fill=(50, 50, 50),
        anchor="lm",
        font=load_font(10),
    )
    y += 16
    draw.text(
        (40, y),
        "Integracion de APIs y servicios web",
        fill=(50, 50, 50),
        anchor="lm",
        font=load_font(10),
    )

    y += 28
    draw.text((25, y), "Contacto:", fill=dark_blue, anchor="lm", font=load_font(11, True))
    y += 18
    draw.text(
        (40, y), "Celular: +57 310 654 1234", fill=(50, 50, 50), anchor="lm", font=load_font(10)
    )
    y += 16
    draw.text(
        (40, y),
        "Email: zaidarellano21@gmail.com",
        fill=(50, 50, 50),
        anchor="lm",
        font=load_font(10),
    )

    img.save(os.path.join(OUTPUT_DIR, "perfil_desarrollador.png"))
    print("Created perfil_desarrollador.png")


def create_cotizacion_box():
    """Create the formal quote box."""
    width, height = 700, 420
    img = Image.new("RGB", (width, height), (255, 255, 255))
    draw = ImageDraw.Draw(img)

    dark_blue = (30, 41, 64)
    cyan = (0, 180, 220)
    green = (46, 204, 113)
    red = (231, 76, 60)

    # Outer border
    draw.rectangle([(10, 10), (width - 10, height - 10)], outline=dark_blue, width=3)
    draw.rectangle([(15, 15), (width - 15, height - 15)], outline=cyan, width=1)

    # Title
    draw.rectangle([(20, 20), (width - 20, 60)], fill=dark_blue)
    draw.text(
        (350, 40), "COTIZACION FORMAL", fill=(255, 255, 255), anchor="mm", font=load_font(18, True)
    )

    # Inner info box
    draw.rectangle([(40, 75), (660, 165)], outline=dark_blue, width=2)

    items = [
        ("PROYECTO:", 'Sistema de Comercio Electronico "Shoppipai"'),
        ("CLIENTE:", "Sra. Luisa Delgado"),
        ("EMPRESA:", "Mackroph Solutions"),
        ("FECHA:", "26 de marzo de 2026"),
    ]
    y = 85
    for label, value in items:
        draw.text((55, y), label, fill=dark_blue, anchor="lm", font=load_font(11, True))
        draw.text((200, y), value, fill=(50, 50, 50), anchor="lm", font=load_font(11))
        y += 22

    # Total value box
    draw.rectangle([(100, 175), (600, 240)], fill=cyan, outline=dark_blue, width=2)
    draw.text(
        (350, 195),
        "VALOR TOTAL DEL PROYECTO:",
        fill=(255, 255, 255),
        anchor="mm",
        font=load_font(14, True),
    )
    draw.text(
        (350, 220), "$8,500,000 COP", fill=(255, 255, 255), anchor="mm", font=load_font(20, True)
    )

    # Includes
    y = 255
    draw.text((40, y), "Este valor INCLUYE:", fill=green, anchor="lm", font=load_font(11, True))
    includes = [
        "Desarrollo completo del sistema (frontend + backend + BD)",
        "Integracion con pasarela de pagos (Wompi)",
        "Integracion con WhatsApp Business API",
        "Despliegue en servidor de produccion",
        "Soporte tecnico por 30 dias post-entrega",
        "Documentacion (manuales de usuario y tecnico)",
        "Capacitacion para el cliente",
    ]
    y += 18
    for item in includes:
        draw.text((55, y), "✓", fill=green, anchor="lm", font=load_font(10))
        draw.text((75, y), item, fill=(50, 50, 50), anchor="lm", font=load_font(9))
        y += 14

    # Does not include
    y += 5
    draw.text((40, y), "Este valor NO INCLUYE:", fill=red, anchor="lm", font=load_font(11, True))
    not_includes = [
        "Infraestructura cloud (hosting VPS): ~$10-15 USD/mes",
        "Dominio y certificado SSL: ~$10-15 USD/ano",
        "Propiedad intelectual del codigo fuente (negociable como adicional)",
        "Mantenimiento posterior a los 30 dias de soporte",
    ]
    y += 18
    for item in not_includes:
        draw.text((55, y), "✗", fill=red, anchor="lm", font=load_font(10))
        draw.text((75, y), item, fill=(50, 50, 50), anchor="lm", font=load_font(9))
        y += 14

    img.save(os.path.join(OUTPUT_DIR, "diagrama_cotizacion.png"))
    print("Created diagrama_cotizacion.png")


def create_payment_methods_box():
    """Create payment methods box."""
    width, height = 650, 180
    img = Image.new("RGB", (width, height), (255, 255, 255))
    draw = ImageDraw.Draw(img)

    dark_blue = (30, 41, 64)

    draw.rectangle([(0, 0), (width - 1, height - 1)], outline=dark_blue, width=2)
    draw.rectangle([(0, 0), (width, 35)], fill=dark_blue)
    draw.text(
        (325, 17),
        "METODOS DE PAGO ACEPTADOS",
        fill=(255, 255, 255),
        anchor="mm",
        font=load_font(14, True),
    )

    methods = [
        ("Consignacion bancaria:", "Cuenta de ahorros Banco de Bogota"),
        ("", "Titular: Cristian Zaid Arellano Munoz"),
        ("", "Numero: XXXX-XXXX-XXXX"),
        ("Transferencia:", "Nequi / Daviplata al +57 310 654 1234"),
        ("Efectivo:", "Solo en Cali, con recibo oficial"),
    ]

    y = 50
    for label, value in methods:
        if label:
            draw.text((30, y), label, fill=dark_blue, anchor="lm", font=load_font(11, True))
            draw.text((180, y), value, fill=(50, 50, 50), anchor="lm", font=load_font(10))
        else:
            draw.text((50, y), value, fill=(50, 50, 50), anchor="lm", font=load_font(10))
        y += 22

    img.save(os.path.join(OUTPUT_DIR, "diagrama_metodos_pago.png"))
    print("Created diagrama_metodos_pago.png")


def create_payment_schedule_box():
    """Create payment schedule vs project progress box."""
    width, height = 650, 200
    img = Image.new("RGB", (width, height), (255, 255, 255))
    draw = ImageDraw.Draw(img)

    dark_blue = (30, 41, 64)
    phase1 = (52, 152, 219)
    phase2 = (46, 204, 113)
    phase3 = (230, 126, 34)

    # Header
    draw.text(
        (325, 15),
        "Cronograma de Pagos vs Avance del Proyecto",
        fill=dark_blue,
        anchor="mm",
        font=load_font(12, True),
    )

    # Timeline
    start_x = 130
    bar_width = 120
    months = ["Mes 1", "Mes 2", "Mes 3", "Mes 4"]
    for i, m in enumerate(months):
        x = start_x + i * 130
        draw.text((x + 60, 40), m, fill=dark_blue, anchor="mm", font=load_font(10))
        draw.line([(x, 55), (x + 130, 55)], fill=dark_blue, width=1)

    # Payment 1
    draw.rectangle([(start_x, 70), (start_x + bar_width, 95)], fill=phase1)
    draw.text(
        (start_x + 10, 75), "PAGO 30%", fill=(255, 255, 255), anchor="lm", font=load_font(10, True)
    )
    draw.text(
        (start_x + 10, 88), "$2,550,000", fill=(255, 255, 255), anchor="lm", font=load_font(9)
    )
    draw.text((start_x + 60, 100), "Firma contrato", fill=dark_blue, anchor="mm", font=load_font(8))

    # Payment 2
    draw.rectangle([(start_x + 130, 115), (start_x + 250, 140)], fill=phase2)
    draw.text(
        (start_x + 140, 120),
        "PAGO 40%",
        fill=(255, 255, 255),
        anchor="lm",
        font=load_font(10, True),
    )
    draw.text(
        (start_x + 140, 133), "$3,400,000", fill=(255, 255, 255), anchor="lm", font=load_font(9)
    )
    draw.text((start_x + 190, 145), "Prototipo OK", fill=dark_blue, anchor="mm", font=load_font(8))

    # Payment 3
    draw.rectangle([(start_x + 260, 160), (start_x + 380, 185)], fill=phase3)
    draw.text(
        (start_x + 270, 165),
        "PAGO 30%",
        fill=(255, 255, 255),
        anchor="lm",
        font=load_font(10, True),
    )
    draw.text(
        (start_x + 270, 178), "$2,550,000", fill=(255, 255, 255), anchor="lm", font=load_font(9)
    )

    img.save(os.path.join(OUTPUT_DIR, "diagrama_cronograma_pagos.png"))
    print("Created diagrama_cronograma_pagos.png")


def create_evaluation_summary_box():
    """Create evaluation summary box."""
    width, height = 650, 220
    img = Image.new("RGB", (width, height), (255, 255, 255))
    draw = ImageDraw.Draw(img)

    dark_blue = (30, 41, 64)
    green = (46, 204, 113)

    draw.rectangle([(0, 0), (width - 1, height - 1)], outline=dark_blue, width=3)
    draw.rectangle([(0, 0), (width, 45)], fill=dark_blue)
    draw.text(
        (325, 15),
        "RESUMEN DE EVALUACION",
        fill=(255, 255, 255),
        anchor="mm",
        font=load_font(14, True),
    )
    draw.text(
        (325, 32),
        "Evidencia: GA2-220501094-AA4-EV02",
        fill=(255, 255, 255),
        anchor="mm",
        font=load_font(9),
    )

    criteria = [
        "Presentacion segun propositos del negocio",
        "Documentacion de sugerencias del cliente",
        "Ajustes tecnicos segun negociacion",
    ]

    y = 60
    draw.line([(30, y), (620, y)], fill=dark_blue, width=1)
    y += 15

    for item in criteria:
        draw.text((40, y), "✓", fill=green, anchor="lm", font=load_font(12))
        draw.text((65, y), item, fill=(50, 50, 50), anchor="lm", font=load_font(11))
        draw.text((550, y), "CUMPLE ✓", fill=green, anchor="lm", font=load_font(11, True))
        y += 28

    draw.line([(30, y), (620, y)], fill=dark_blue, width=1)
    y += 20

    # Final status
    draw.rectangle([(150, y), (500, y + 50)], fill=green)
    draw.text(
        (325, y + 15),
        "ESTADO GENERAL: APROBADO",
        fill=(255, 255, 255),
        anchor="mm",
        font=load_font(14, True),
    )
    draw.text(
        (325, y + 35),
        "CUMPLE CON TODOS LOS CRITERIOS",
        fill=(255, 255, 255),
        anchor="mm",
        font=load_font(10),
    )

    img.save(os.path.join(OUTPUT_DIR, "diagrama_resumen_evaluacion.png"))
    print("Created diagrama_resumen_evaluacion.png")


def create_company_info_box():
    """Create company information box."""
    width, height = 650, 380
    img = Image.new("RGB", (width, height), (255, 255, 255))
    draw = ImageDraw.Draw(img)

    dark_blue = (30, 41, 64)
    cyan = (0, 180, 220)

    draw.rectangle([(0, 0), (width - 1, height - 1)], outline=dark_blue, width=3)
    draw.rectangle([(0, 0), (width, 50)], fill=dark_blue)
    draw.text(
        (325, 25), "MACKROPH SOLUTIONS", fill=(255, 255, 255), anchor="mm", font=load_font(18, True)
    )

    draw.text(
        (325, 60),
        '"Transformamos ideas en soluciones tecnologicas"',
        fill=cyan,
        anchor="mm",
        font=load_font(11, True),
    )

    # Logo placeholder
    draw.rectangle([(225, 75), (425, 145)], fill=(240, 240, 240), outline=dark_blue, width=2)
    draw.text((325, 95), "[LOGO MACKROPH]", fill=(150, 150, 150), anchor="mm", font=load_font(12))
    draw.text((325, 125), "MS", fill=dark_blue, anchor="mm", font=load_font(24, True))

    # Separator
    draw.line([(30, 155), (620, 155)], fill=dark_blue, width=2)

    # Contact info
    y = 170
    draw.text(
        (30, y), "INFORMACION DE CONTACTO:", fill=dark_blue, anchor="lm", font=load_font(11, True)
    )
    draw.line([(30, y + 5), (250, y + 5)], fill=dark_blue, width=1)

    contacts = [
        ("Nombre:", "Cristian Zaid Arellano Munoz"),
        ("Cargo:", "Lider Tecnico / Desarrollador Backend"),
        ("Empresa:", "Mackroph Solutions"),
        ("Direccion:", "Calle 5 # 28-50, Cali, Valle del Cauca, Colombia"),
        ("Celular:", "+57 310 654 1234"),
        ("WhatsApp:", "+57 310 654 1234"),
        ("Email:", "zaidarellano21@gmail.com"),
        ("Email Corp:", "contacto@mackrophsolutions.com"),
        ("Website:", "www.mackrophsolutions.com"),
    ]

    y += 20
    for label, value in contacts:
        draw.text((50, y), label, fill=dark_blue, anchor="lm", font=load_font(10, True))
        draw.text((170, y), value, fill=(50, 50, 50), anchor="lm", font=load_font(10))
        y += 18

    # Program info
    y += 10
    draw.text(
        (30, y), "INFORMACION DEL PROGRAMA:", fill=dark_blue, anchor="lm", font=load_font(11, True)
    )
    draw.line([(30, y + 5), (250, y + 5)], fill=dark_blue, width=1)

    y += 20
    program_info = [
        ("Programa:", "Analisis y Desarrollo de Software (ADSO)"),
        ("Ficha:", "3336101"),
        ("Centro:", "Servicio Nacional de Aprendizaje (SENA)"),
    ]
    for label, value in program_info:
        draw.text((50, y), label, fill=dark_blue, anchor="lm", font=load_font(10, True))
        draw.text((170, y), value, fill=(50, 50, 50), anchor="lm", font=load_font(10))
        y += 18

    img.save(os.path.join(OUTPUT_DIR, "diagrama_info_empresa.png"))
    print("Created diagrama_info_empresa.png")


def create_signature_box():
    """Create signature box."""
    width, height = 450, 120
    img = Image.new("RGB", (width, height), (255, 255, 255))
    draw = ImageDraw.Draw(img)

    dark_blue = (30, 41, 64)

    # Draw signature line
    draw.text((30, 15), "Firma del desarrollador:", fill=dark_blue, anchor="lm", font=load_font(11))
    draw.line([(30, 60), (350, 60)], fill=dark_blue, width=1)
    draw.text(
        (30, 70), "Cristian Zaid Arellano Munoz", fill=dark_blue, anchor="lm", font=load_font(10)
    )
    draw.text(
        (30, 90), "Fecha: 26 de marzo de 2026", fill=(100, 100, 100), anchor="lm", font=load_font(9)
    )

    img.save(os.path.join(OUTPUT_DIR, "diagrama_firma.png"))
    print("Created diagrama_firma.png")


if __name__ == "__main__":
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    create_architecture_diagram()
    create_gantt_chart()
    create_profile_card()
    create_cotizacion_box()
    create_payment_methods_box()
    create_payment_schedule_box()
    create_evaluation_summary_box()
    create_company_info_box()
    create_signature_box()
    print("\nAll diagrams created successfully!")
