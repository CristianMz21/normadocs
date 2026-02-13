# APAScript: Conversor de Markdown a APA 7

Este proyecto es una herramienta automatizada para convertir documentos escritos en **Markdown** a documentos **Microsoft Word (.docx)** que cumplen estrictamente con las normas **APA 7ª edición**.

Es ideal para aprendices SENA, estudiantes y profesionales que prefieren escribir en Markdown pero necesitan entregar documentos en formato APA.

## 🚀 Características

*   **Automatización Total:** Convierte estructura, fuentes y márgenes automáticamente.
*   **Gestión de Portada:** Genera una portada APA profesional a partir de metadatos simples.
*   **Formato de Texto:** Aplica Times New Roman 12pt, doble espaciado y sangrías correctas.
*   **Tablas APA:** Convierte tablas Markdown a tablas con estilo APA (sin bordes verticales).
*   **Referencias:** Formatea la lista de referencias con sangría francesa.
*   **Ecuaciones y Citas:** Manejo básico de citas parentéticas (convierte "y" a "&" en citas).

---

## 📋 Requisitos Previos

Antes de empezar, necesitas instalar las siguientes herramientas en tu sistema.

### 1. Pandoc (Obligatorio)
Motor principal de conversión.
*   **Linux (Debian/Ubuntu):**
    ```bash
    sudo apt-get update
    sudo apt-get install pandoc
    ```
*   **Windows/Mac:** Descargar desde [pandoc.org](https://pandoc.org/installing.html).

### 2. UV (Gestor de Python Recomendado)
Usamos `uv` para manejar Python y las dependencias sin ensuciar tu sistema.
*   **Instalación (Linux/Mac/Windows):**
    ```bash
    curl -LsSf https://astral.sh/uv/install.sh | sh
    ```

---

## 🛠️ Instalación y Configuración del Proyecto

1.  **Clonar el repositorio:**
    ```bash
    git clone https://github.com/TU_USUARIO/APAScript.git
    cd APAScript
    ```

2.  **Verificar instalación:**
    No es necesario instalar nada más manualmente si usas `uv`. El proyecto ya tiene configurado `python-docx` como dependencia.

---

## 📖 Guía de Uso

### Paso 1: Prepara tu Documento
Crea un archivo Markdown en la carpeta del proyecto. Puedes usar **`example.md`** como plantilla.

Tu archivo debe tener este encabezado (metadatos) en las primeras líneas para que la portada se genere bien:

```markdown
**Título de tu Trabajo**

Tu Nombre Completo

Nombre de tu Programa
Número de Ficha
Nombre de la Institución (SENA)
Nombre del Centro
Fecha
```

### Paso 2: Configurar el Script (Opcional)
Por defecto, el script busca un archivo llamado `ERS_Shoppipai_SENA_COMPLETO.md`. Si tu archivo tiene otro nombre (ej. `Mi_Ensayo.md`), tienes dos opciones:

**Opción A (Recomendada):** Renombra tu archivo a `ERS_Shoppipai_SENA_COMPLETO.md`.

**Opción B:** Edita el archivo `convert_to_apa.py` y cambia la línea 43:
```python
# Cambia esto por el nombre de tu archivo
INPUT_FILE = "Mi_Ensayo.md"
```

### Paso 3: Ejecutar la Conversión

El script ahora admite argumentos para personalizar la ejecución.

#### Uso Básico (DOCX por defecto)
```bash
uv run convert_to_apa.py [ARCHIVO_ENTRADA]
```
Ejemplo:
```bash
uv run convert_to_apa.py mi_ensayo.md
```

#### Opciones Avanzadas

| Argumento | Descripción | Ejemplo |
| :--- | :--- | :--- |
| `archivo` | Archivo Markdown de entrada (Posicional). | `tesis.md` |
| `-o`, `--output-dir` | Carpeta donde se guardarán los archivos. | `-o Entregables` |
| `-f`, `--format` | Formato de salida: `docx`, `pdf` o `all`. | `-f all` |

**Ejemplos:**

1.  **Generar PDF y DOCX:**
    ```bash
    uv run convert_to_apa.py ejemplo.md -f all
    ```

2.  **Guardar en otra carpeta:**
    ```bash
    uv run convert_to_apa.py -o ./dist
    ```

### Paso 4: Obtener el Resultado
El documento final aparecerá en la carpeta especificada (por defecto `DOCS/`).

### Ejecución con Docker

Si prefieres no instalar nada en tu máquina, puedes usar Docker:

1.  **Construir la imagen:**
    ```bash
    docker build -t apascript .
    ```

2.  **Ejecutar el contenedor:**
    Para obtener el archivo generado en tu carpeta `DOCS/` local, montamos un volumen:
    ```bash
    docker run --rm -v $(pwd)/DOCS:/app/DOCS apascript
    ```


---

## 📂 Estructura del Proyecto

*   `convert_to_apa.py`: **Script principal.** Aquí ocurre la magia.
*   `example.md`: **Plantilla.** Úsala de base para tus documentos.
*   `pyproject.toml`: **Configuración.** Define las dependencias para `uv`.
*   `.gitignore`: **Seguridad.** Evita que subas tus documentos privados a GitHub.
*   `DOCS/`: **Salida.** Aquí se guardan los archivos .docx generados.

## ⚠️ Solución de Problemas

*   **Error "pandoc not found":** Asegúrate de haber instalado Pandoc (`sudo apt install pandoc`) y que funcionen en tu terminal (`pandoc --version`).
*   **Error de dependencias:** Si usas `pip` en lugar de `uv`, recuerda instalar manual: `pip install python-docx`.
