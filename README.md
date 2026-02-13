# APAScript: Markdown to APA 7 Converter

Este proyecto contiene un script en Python que convierte documentos Markdown (siguiendo la estructura ERS) a documentos DOCX con formato APA 7ª edición.

## Características

-   **Conversión Markdown a DOCX:** Utiliza Pandoc para la conversión inicial.
-   **Formato APA 7 Automatizado:**
    -   Portada en página independiente.
    -   Saltos de página antes de cada título de nivel 1.
    -   Fuente Times New Roman 12pt.
    -   Doble espaciado.
    -   Márgenes de 1 pulgada (2.54 cm).
    -   Sangría de primera línea (0.5 pulgadas).
    -   Tablas con estilo APA (solo bordes horizontales).
    -   Referencias con sangría francesa.
    -   Numeración de páginas.

## Requisitos

-   Python 3.11 o superior.
-   [Pandoc](https://pandoc.org/installing.html) instalado y accesible en el PATH del sistema.

## Instalación y Uso con `uv` (Recomendado)

Este proyecto está configurado para usarse con [uv](https://github.com/astral-sh/uv), un gestor de paquetes de Python extremadamente rápido.

1.  Asegúrate de tener `uv` instalado.
2.  Ejecuta el script directamente:

    ```bash
    uv run convert_to_apa.py
    ```

    `uv` se encargará de instalar Python y las dependencias necesarias automáticamente en un entorno aislado y efímero.

## Instalación Manual (Pip)

Si prefieres usar `pip`:

1.  Instala las dependencias:
    ```bash
    pip install -r requirements.txt
    # O manualmente:
    pip install python-docx
    ```
2.  Ejecuta:
    ```bash
    python3 convert_to_apa.py
    ```

3.  El documento generado se guardará en la carpeta `DOCS/` con el nombre `ERS_Shoppipai_SENA_COMPLETO_APA.docx`.

## Estructura del Proyecto

-   `convert_to_apa.py`: Script principal de conversión.
-   `DOCS/`: Carpeta de salida para los documentos generados.
-   `pyproject.toml`: Configuración del proyecto y dependencias.
