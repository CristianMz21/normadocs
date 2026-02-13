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

## Instalación

1.  Clona este repositorio.
2.  Instala las dependencias de Python:

    ```bash
    pip install -r requirements.txt
    # O si usas pip directamente:
    pip install python-docx
    ```

## Uso

1.  Coloca tu archivo Markdown en la raíz del proyecto (por defecto busca `ERS_Shoppipai_SENA_COMPLETO.md`).
2.  Ejecuta el script:

    ```bash
    python3 convert_to_apa.py
    ```

3.  El documento generado se guardará en la carpeta `DOCS/` con el nombre `ERS_Shoppipai_SENA_COMPLETO_APA.docx`.

## Estructura del Proyecto

-   `convert_to_apa.py`: Script principal de conversión.
-   `DOCS/`: Carpeta de salida para los documentos generados.
-   `pyproject.toml`: Configuración del proyecto y dependencias.
