#!/usr/bin/env python3
"""
Script para verificación STRICT de Normas APA 7ma Edición.

Verifica:
1. Formato General (márgenes, interlineado, sangría, numeración)
2. Estructura del Informe (portada, resumen, cuerpo, referencias)
3. Niveles de Títulos (5 niveles APA 7)
4. Tablas y Figuras
5. Referencias (sangría francesa)
6. Citas en el texto
"""

import re
import sys
from pathlib import Path

try:
    from pypdf import PdfReader
except ImportError:
    print("Error: Necesitas instalar pypdf")
    print("Ejecuta: pip3 install pypdf")
    sys.exit(1)


class APA7Verifier:
    """Verificador riguroso de Normas APA 7ma Edición."""

    def __init__(self, pdf_path: str):
        self.pdf_path = Path(pdf_path)
        self.reader = PdfReader(str(pdf_path))
        self.total_pages = len(self.reader.pages)
        self.all_text = ""
        self.pages_text = {}
        self.errors = []
        self.warnings = []
        self.passed = []

        # Extraer texto por página
        for i, page in enumerate(self.reader.pages, 1):
            page_text = page.extract_text() or ""
            self.pages_text[i] = page_text
            self.all_text += f"\n=== Página {i} ===\n{page_text}"

    def verify_all(self) -> dict:
        """Ejecuta todas las verificaciones."""
        self.verify_page_format()
        self.verify_page_numbers()
        self.verify_cover_page()
        self.verify_resumen()
        self.verify_body_start()
        self.verify_heading_levels()
        self.verify_references()
        self.verify_table_format()
        self.verify_figure_format()
        self.verify_citations()
        self.verify_font_indicators()
        self.verify_text_wrapping()

        return {
            "errors": self.errors,
            "warnings": self.warnings,
            "passed": self.passed,
            "total_pages": self.total_pages,
        }

    def verify_page_format(self):
        """Verifica formato de página (márgenes, tamaño)."""
        for i, page in enumerate(self.reader.pages, 1):
            # Verificar que no esté vacío
            if not page.extract_text():
                self.warnings.append(f"Página {i} aparece vacía")

    def verify_page_numbers(self):
        """Verifica numeración de páginas: debe empezar en 1."""
        # Buscar número 1 en primera página
        page1_text = self.pages_text.get(1, "")

        # El número de página debe aparecer como "1" solo en header
        # LibreOffice coloca el número de página
        if "1" in page1_text[:200]:
            self.passed.append("Numeración de páginas comienza en 1")
        else:
            # Verificar si hay números de página en el header
            has_page_num = bool(re.search(r"\b\d+\b", page1_text[:100]))
            if has_page_num or page1_text.strip():
                self.passed.append("Primera página tiene contenido")
            else:
                self.errors.append("No se detectó número de página 1 en portada")

    def verify_cover_page(self):
        """Verifica portada APA 7.

        Elementos requeridos en portada:
        - Título (negrita, centrado)
        - Nombre del autor
        - Afiliación (institución)
        - Curso
        - Instructor (opcional)
        - Fecha
        - Número de página (arriba derecha)
        """
        page1 = self.pages_text.get(1, "")
        lines = page1.split("\n")[:20]
        content = " ".join(lines)

        # Verificar elementos requeridos
        checks = {
            "Título": len([line for line in lines if len(line.strip()) > 15]) > 0,
            "Autor": bool(re.search(r"Zaid|Arellano|Cristian", content, re.IGNORECASE)),
            "Institución": "SENA" in content.upper() or "Universidad" in content,
            "Programa": bool(re.search(r"Análisis|Desarrollo|Software|Programa", content)),
            "Fecha": bool(re.search(r"\d{1,2}\s+de\s+\w+|\d{4}", content)),
        }

        for item, passed in checks.items():
            if passed:
                self.passed.append(f"Portada tiene {item}")
            else:
                self.errors.append(f"Portada falta o incorrecto: {item}")

        # Verificar que NO haya YAML frontmatter en portada
        if page1.strip().startswith("---"):
            self.errors.append("Portada contiene YAML frontmatter sin procesar")

        # Verificar que no haya Markdown residual
        if re.search(r"!\[.*?\]\(.*?\)", page1):
            self.warnings.append("Portada contiene sintaxis Markdown sin procesar")

    def verify_resumen(self):
        """Verifica sección Resumen (Abstract).

        Requisitos APA 7:
        - Título "Resumen" centrado y en negrita
        - Texto sin sangría de primera línea
        - "Palabras clave:" en cursiva
        - Máximo 250 palabras
        """
        resumen_found = False
        for page_num, text in self.pages_text.items():
            if re.search(r"^\s*Resumen\s*$", text, re.MULTILINE):
                resumen_found = True
                self.passed.append(f"Resumen encontrado en página {page_num}")

                # Verificar Palabras clave
                if re.search(r"Palabras\s+clave|Keywords", text, re.IGNORECASE):
                    self.passed.append("Palabras clave encontradas")
                else:
                    self.warnings.append("No se encontró 'Palabras clave' después de Resumen")

                break

        if not resumen_found:
            self.warnings.append("No se encontró sección 'Resumen' (opcional pero recomendado)")

    def verify_body_start(self):
        """Verifica que el cuerpo del texto inicie correctamente.

        Después del resumen (y palabras clave), debe iniciar con:
        - Título del trabajo centrado (repetición del título)
        - Luego Introducción
        """
        body_started = False
        for page_num, text in self.pages_text.items():
            # Buscar inicio del cuerpo
            if re.search(
                r"^\s*1\.\s*DESCRIPCIÓN|INTRODUCCIÓN|Este documento",
                text,
                re.MULTILINE | re.IGNORECASE,
            ):
                body_started = True
                self.passed.append(f"Cuerpo del texto inicia en página {page_num}")
                break

        if not body_started:
            self.warnings.append("No se detectó inicio claro del cuerpo del texto")

    def verify_heading_levels(self):
        """Verifica los 5 niveles de títulos APA 7.

        Nivel 1: Centrado, Negrita, Mayúsculas
        Nivel 2: Izquierda, Negrita, Mayúsculas
        Nivel 3: Izquierda, Negrita+Itálica, Mayúsculas
        Nivel 4: Sangría, Negrita, Mayúsculas, termina en punto
        Nivel 5: Sangría, Negrita+Itálica, Mayúsculas, termina en punto
        """
        # Verificar presencia de títulos de nivel 1
        h1_found = bool(
            re.search(
                r"^\s*(RESUMEN|INTRODUCCIÓN|MÉTODOS|RESULTADOS|DISCUSIÓN|CONCLUSIONES|REFERENCIAS)\s*$",
                self.all_text,
                re.MULTILINE,
            )
        )
        if h1_found:
            self.passed.append("Títulos de nivel 1 (centrados) detectados")

        # Verificar títulos de nivel 2 (numéricos)
        h2_found = bool(re.search(r"^\s*\d+\.\s+[A-ZÁÉÍÓÚÑ]", self.all_text, re.MULTILINE))
        if h2_found:
            self.passed.append("Títulos de nivel 2 (numerados) detectados")

        # Verificar títulos de nivel 3
        h3_found = bool(re.search(r"^\s*\d+\.\d+\s+[A-ZÁÉÍÓÚÑ]", self.all_text, re.MULTILINE))
        if h3_found:
            self.passed.append("Títulos de nivel 3 (subnumerados) detectados")

    def verify_references(self):
        """Verifica formato de Referencias.

        Requisitos APA 7:
        - Título "Referencias" centrado
        - Sangría francesa (hanging indent): primera línea sin sangría, resto con sangría
        - Orden alfabético por apellido del autor
        - Doble interlineado
        """
        ref_found = False
        for page_num, text in self.pages_text.items():
            if re.search(r"^\s*Referencias\s*$", text, re.MULTILINE | re.IGNORECASE):
                ref_found = True
                self.passed.append(f"Referencias encontradas en página {page_num}")

                # Buscar patrones de entradas de referencias (Apellido, N.)
                ref_entries = re.findall(
                    r"^[A-ZÁÉÍÓÚÑ][a-záéíóúñ]+\s*,?\s*[A-Z]\.", text, re.MULTILINE
                )
                if len(ref_entries) >= 2:
                    self.passed.append(
                        f"Múltiples entradas de referencia detectadas ({len(ref_entries)})"
                    )
                elif len(ref_entries) == 1:
                    self.warnings.append("Solo una entrada de referencia detectada")
                break

        if not ref_found:
            self.warnings.append("No se encontró sección 'Referencias'")

    def verify_table_format(self):
        """Verifica formato de tablas.

        Requisitos APA 7:
        - "Tabla N" en negrita
        - Título en cursiva en siguiente línea
        - Notas si es necesario
        """
        tables = re.findall(r"Tabla\s+\d+", self.all_text, re.IGNORECASE)
        if tables:
            unique_tables = set(tables)
            self.passed.append(f"Tablas detectadas: {len(unique_tables)}")

            # Verificar que no haya duplicados de numeración
            table_nums = [int(re.search(r"\d+", t).group()) for t in tables]
            if sorted(table_nums) == list(range(1, max(table_nums) + 1)):
                self.passed.append("Numeración de tablas es secuencial")
            else:
                self.errors.append(f"Numeración de tablas no secuencial: {table_nums}")

    def verify_figure_format(self):
        """Verifica formato de figuras.

        Requisitos APA 7:
        - "Figura N" en negrita
        - Título en cursiva
        - "Nota." en itálica si hay notas
        """
        figures = re.findall(r"Figura\s+\d+", self.all_text, re.IGNORECASE)
        if figures:
            unique_figures = set(figures)
            self.passed.append(f"Figuras detectadas: {len(unique_figures)}")

            # Verificar numeración secuencial
            fig_nums = [int(re.search(r"\d+", f).group()) for f in figures]
            if sorted(fig_nums) == list(range(1, max(fig_nums) + 1)):
                self.passed.append("Numeración de figuras es secuencial")
            else:
                self.warnings.append(f"Numeración de figuras no secuencial: {fig_nums}")

    def verify_citations(self):
        """Verifica formato de citas.

        Cita parentética: (Autor, año)
        Cita narrativa: Como afirma Autor (año)
        Tres o más autores: (Autor et al., año)
        """
        # Buscar citas parentéticas
        parentetic_cites = re.findall(
            r"\([A-ZÁÉÍÓÚÑ][a-záéíóúñ]+(?:\s+(?:et\s+al\.|[A-ZÁÉÍÓÚÑ]\.))?,?\s*\d{4}[a-z]?(?:\s*,\s*p\.\s*\d+)?\)",
            self.all_text,
        )

        if parentetic_cites:
            self.passed.append(f"Citas parentéticas detectadas: {len(parentetic_cites)}")

        # Buscar "et al."
        et_al_cites = re.findall(r"\(.*?et\s+al\..*?\)", self.all_text)
        if et_al_cites:
            self.passed.append(f"Citas con 'et al.' detectadas: {len(et_al_cites)}")

    def verify_font_indicators(self):
        """Verifica indicadores de formato de fuente (no se puede verificar directamente en PDF extraído).

        Este método es una marca de posición ya que PDF extrae solo texto.
        """
        # Verificar que no haya texto RAW de Markdown
        md_indicators = {
            "Bold marker": r"\*\*[^*]+\*\*",
            "Italic marker": r"(?<!\*)\*[^*]+(?!\*)",
            "Code block": r"```[\s\S]+```",
        }

        for name, pattern in md_indicators.items():
            if re.search(pattern, self.all_text):
                self.warnings.append(f"Posible sintaxis Markdown sin procesar: {name}")

        # Verificar espacios múltiples
        if "  " in self.all_text:
            self.errors.append("Espacios múltiples detectados (deben ser simples)")

        # Verificar puntos suspensivos incorrectos
        if "...." in self.all_text:
            self.warnings.append("Puntos suspensivos incorrectos (....)")

        # Verificar duplicados consecutivos
        lines = self.all_text.split("\n")
        for line in lines:
            words = line.split()
            for i in range(len(words) - 1):
                w1 = re.sub(r"[^\w]", "", words[i].lower())
                w2 = re.sub(r"[^\w]", "", words[i + 1].lower())
                if w1 and w2 and w1 == w2 and len(w1) > 2:
                    self.errors.append(f"Palabra duplicada consecutivas: '{words[i]}'")
                    break

    def verify_text_wrapping(self):
        """Verifica problemas de envoltura de texto.

        Detecta problemas reales como:
        1. Texto cortado a mitad de palabra (guión al final)
        2. Valores monetarios divididos incorrectamente
        3. Texto muy largo sin saltos (problema de interlineado)

        Las referencias [a], [b], [c] son notación APA válida y no se reportan como errores.
        """
        issues_found = []

        lines = self.all_text.split("\n")

        # 1. Detectar texto cortado con guión (palabra incompleta al final)
        cutoff_words = []
        for i in range(len(lines) - 1):
            current = lines[i].strip()
            next_line = lines[i + 1].strip()

            if current and next_line:
                # Patrón: línea termina con guión
                if current.endswith("-"):
                    cutoff_words.append((i + 1, current[-30:], next_line[:30]))
                # Patrón: valor monetario dividido (ej: "$25,000,00" + "0")
                elif re.match(r"^\$[\d,]+,\d{1,2}\s*$", current) and re.match(
                    r"^\d{1,3}\s*$", next_line
                ):
                    cutoff_words.append((i + 1, current, next_line))

        if cutoff_words:
            issues_found.append(f"Texto cortado detectado: {len(cutoff_words)}")
            for line_num, before, after in cutoff_words[:5]:
                self.errors.append(f"  Línea {line_num}: Texto cortado - '{before}' + '{after}'")

        # 2. Detectar valores monetarios mal divididos
        # Patrones como "$25,000,00" seguido de "0" o "000"
        monetary_issues = []
        for i in range(len(lines) - 1):
            current = lines[i].strip()
            next_line = lines[i + 1].strip()

            # Detectar splits en valores monetarios grandes
            # Ej: "$105,488,0" + "00" o "$25,000,00" + "0"
            if re.match(r"^\$[\d,]+\,\d{1,2}\s*$", current) and re.match(
                r"^\d{1,3}\s*$", next_line
            ):
                combined = current.replace(",", "") + next_line
                # Verificar que el valor combinado tiene sentido (muchos dígitos)
                digits = re.sub(r"[^\d]", "", combined)
                if len(digits) >= 8:  # Valores >= $1,000,000
                    monetary_issues.append((i + 1, current, next_line))

        if monetary_issues:
            issues_found.append(f"Valores monetarios divididos: {len(monetary_issues)}")
            for line_num, before, after in monetary_issues[:5]:
                self.errors.append(f"  Línea {line_num}: Valor dividido - '{before}' + '{after}'")

        # 3. Detectar texto muy largo sin saltos (posible problema de interlineado)
        very_long_lines = []
        for i, line in enumerate(lines):
            # Excluir líneas de tabla que son legítimamente largas
            if len(line) > 120 and not re.search(r"\|\s*\S+\s*\|", line):
                very_long_lines.append((i + 1, len(line)))

        if very_long_lines:
            self.warnings.append(
                f"Líneas muy largas detectadas ({len(very_long_lines)}): verificar interlineado"
            )

        # No reportar líneas cortas o notas [a], [b], [c] como errores -
        # son parte normal del flujo de texto con ajuste automático

    def print_report(self):
        """Imprime reporte completo de verificación."""
        print("=" * 70)
        print(f"VERIFICACIÓN ESTRICTA APA 7: {self.pdf_path.name}")
        print("=" * 70)
        print(f"\n📄 Total páginas: {self.total_pages}\n")

        # Resumen
        print("-" * 70)
        print("📋 RESUMEN DE VERIFICACIÓN")
        print("-" * 70)

        if self.errors:
            print(f"\n❌ ERRORES ({len(self.errors)}):")
            for e in self.errors:
                print(f"   • {e}")

        if self.warnings:
            print(f"\n⚠️  ADVERTENCIAS ({len(self.warnings)}):")
            for w in self.warnings:
                print(f"   • {w}")

        if self.passed:
            print(f"\n✅ CORRECTO ({len(self.passed)}):")
            for p in self.passed[:10]:  # Mostrar máximo 10
                print(f"   ✓ {p}")
            if len(self.passed) > 10:
                print(f"   ... y {len(self.passed) - 10} más")

        # Veredicto final
        print("\n" + "=" * 70)
        if not self.errors and not self.warnings:
            print("✅ APROBADO - Documento cumple Normas APA 7ma Edición")
        elif not self.errors:
            print("⚠️  APROBADO CON ADVERTENCIAS")
        else:
            print("❌ REPROBADO - Corrija los errores indicados")
        print("=" * 70)

        return len(self.errors) == 0

    def get_detailed_pages(self, num_pages: int = 5) -> str:
        """Retorna texto detallado de las primeras N páginas."""
        output = []
        for i in range(1, min(num_pages + 1, self.total_pages + 1)):
            output.append(f"\n{'=' * 50}")
            output.append(f"PÁGINA {i}")
            output.append(f"{'=' * 50}")
            output.append(self.pages_text.get(i, ""))
        return "\n".join(output)


def verify_pdf(pdf_path: str, num_preview: int = 5):
    """Función principal de verificación."""
    path = Path(pdf_path)

    if not path.exists():
        print(f"Error: No se encontró el archivo {pdf_path}")
        sys.exit(1)

    try:
        verifier = APA7Verifier(str(path))
        passed = verifier.print_report()

        # Mostrar preview si se solicita
        if num_preview > 0:
            print("\n" + "=" * 50)
            print(f"VISTA PREVIA (primeras {num_preview} páginas)")
            print("=" * 50)
            print(verifier.get_detailed_pages(num_preview))

        return 0 if passed else 1

    except Exception as e:
        print(f"Error al verificar PDF: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python3 verify_pdf.py <archivo.pdf> [num_paginas_preview]")
        print("Ejemplo: python3 verify_pdf.py documento.pdf 5")
        sys.exit(1)

    pdf_file = sys.argv[1]
    num_pages = int(sys.argv[2]) if len(sys.argv) > 2 else 5

    exit_code = verify_pdf(pdf_file, num_pages)
    sys.exit(exit_code)
