"""
Generate Gantt chart using Mermaid.js
"""

MERMAID_HTML = """<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Diagrama de Gantt - Shoppipai</title>
    <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
    <style>
        body {{
            background: white;
            padding: 20px;
            font-family: Arial, sans-serif;
        }}
        .mermaid {{
            display: flex;
            justify-content: center;
        }}
    </style>
</head>
<body>
    <pre class="mermaid">
    gantt
        title DIAGRAMA DE GANTT - PROYECTO SHOPPIPAI
        dateFormat  YYYY-MM-DD
        axisFormat  %d/%m

        section FASE 1: ANALISIS
        Levantamiento de requisitos       :a1, 2024-01-08, 14d
        Diseño de arquitectura            :a2, after a1, 14d
        Modelado de base de datos         :a3, after a2, 14d
        Prototipos Figma                  :a4, after a2, 14d

        section FASE 2: PLANEACIÓN
        Diseño de API REST               :b1, 2024-02-19, 14d
        Configuración Docker             :b2, after b1, 14d
        Definición de modelos Django      :b3, after b1, 21d
        Planificación de Sprints         :b4, after b3, 14d

        section FASE 3: EJECUCIÓN
        Módulo Usuarios                  :c1, 2024-04-01, 14d
        Módulo Productos/Catálogo        :c2, 2024-04-01, 21d
        Módulo Carrito/Checkout          :c3, after c1, 21d
        Integración Wompi/PayU           :c4, after c2, 14d
        Configuración WhatsApp API       :c5, after c4, 7d

        section FASE 4: EVALUACIÓN
        Pruebas unitarias                :d1, 2024-05-06, 14d
        Pruebas de integración           :d2, after d1, 14d
        UAT con cliente                  :d3, after d1, 14d
        Despliegue en producción         :d4, after d3, 14d
        Capacitación y documentación     :d5, after d3, 14d
    </pre>
    <script>
        mermaid.initialize({{
            startOnLoad: true,
            theme: 'base',
            themeVariables: {{
                primaryColor: '#3498db',
                primaryTextColor: '#1a1a1a',
                primaryBorderColor: '#2c3e50',
                lineColor: '#95a5a6',
                sectionBkgColor: '#ecf0f1',
                altSectionBkgColor: '#ffffff',
                gridColor: '#bdc3c7',
                done: '#27ae60',
                active: '#e74c3c',
                crit: '#e74c3c',
                milestone: '#f39c12'
            }},
            gantt: {{
                titleTopMargin: 25,
                barHeight: 30,
                barGap: 6,
                topPadding: 50,
                leftPadding: 120,
                gridLineStartPadding: 35,
                fontSize: 14,
                sectionFontSize: 16,
                numberSectionStyles: 4,
                axisFormat: '%d/%m'
            }}
        }});
    </script>
</body>
</html>"""


def generate_mermaid_gantt():
    """Generate Mermaid Gantt chart as PNG using playwright."""
    import os

    from playwright.sync_api import sync_playwright

    html_path = "/home/mackroph/Projectos/Learning/APAScript/IDocs/image/gantt_mermaid.html"
    png_path = "/home/mackroph/Projectos/Learning/APAScript/IDocs/image/gantt_chart.png"

    # Ensure directory exists
    os.makedirs(os.path.dirname(html_path), exist_ok=True)

    # Write HTML file
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(MERMAID_HTML)

    print(f"HTML created: {html_path}")

    # Use playwright to render and screenshot
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1400, "height": 800})

        page.goto(f"file://{html_path}")

        # Wait for mermaid to render
        page.wait_for_selector(".mermaid svg", timeout=30000)

        # Get the SVG element
        svg = page.query_selector(".mermaid svg")
        if svg:
            bbox = svg.bounding_box()
            print(f"SVG bounding box: {bbox}")

        # Take screenshot
        page.screenshot(path=png_path, full_page=True)
        browser.close()

    print(f"Gantt chart PNG saved: {png_path}")
    return png_path


if __name__ == "__main__":
    generate_mermaid_gantt()
