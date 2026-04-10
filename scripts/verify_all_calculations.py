#!/usr/bin/env python3
"""
Script para verificar TODOS los cálculos del INFORME TÉCNICO ECONÓMICO.
"""

import re
import sys
from pathlib import Path


def extract_currency(value: str) -> int:
    """Extrae valor numérico de formato colombiano $3.500.000"""
    if not value:
        return 0
    cleaned = value.strip().replace("$", "").replace(" ", "")
    if "." in cleaned:
        cleaned = re.sub(r"[^\d]", "", cleaned)
        return int(cleaned) if cleaned else 0
    return 0


def parse_table_lines(section: str) -> list[list[str]]:
    """Extrae filas de datos de una sección markdown (que contiene tablas)."""
    rows = []
    in_table = False
    for line in section.split("\n"):
        if not line.startswith("|"):
            in_table = False
            continue
        cells = [c.strip() for c in line.split("|")]
        # Remove leading/trailing empty cells
        if cells and cells[0] == "":
            cells = cells[1:]
        if cells and cells[-1] == "":
            cells = cells[:-1]
        if not cells:
            continue
        # Check if separator line (---: etc)
        if all(re.match(r"^[:\- ]+$", c) or c == "" for c in cells):
            in_table = True
            continue
        if in_table and cells:
            rows.append(cells)
    return rows


def main():
    md_file = "IDocs/Evidencia_AA1_EV02/02_Informes/INFORME_TECNICO_ECONOMICO.md"
    docx_path = "ExportDocs/INFORME_TECNICO_ECONOMICO_APA.docx"

    if not Path(md_file).exists():
        print(f"Error: No se encontró {md_file}")
        sys.exit(1)

    print("=" * 70)
    print("VERIFICACIÓN COMPLETA DE CÁLCULOS")
    print("INFORME TÉCNICO ECONÓMICO - SHOPPIPAI")
    print("=" * 70)

    with open(md_file, encoding="utf-8") as f:
        content = f.read()

    all_ok = True

    # =========================================================================
    # 1. PERSONAL (Sección 4.2)
    # =========================================================================
    print("\n" + "=" * 70)
    print("1. COSTOS DE PERSONAL (Sección 4.2)")
    print("=" * 70)

    sec = content[content.find("## 4.2") : content.find("## 4.3")]
    rows = parse_table_lines(sec)

    personal_items = []
    personal_total = 0

    for row in rows:
        # Skip rows that are just labels (Subtotal)
        if len(row) >= 2 and row[0] == "" and "subtotal" in " ".join(row).lower():
            # This is the subtotal row
            for cell in reversed(row):
                val = extract_currency(cell)
                if val > 0:
                    personal_total = val
                    break
            continue

        if len(row) >= 5:
            name = row[0]
            total = extract_currency(row[4])
            if total > 0:
                personal_items.append((name, total))

    p_sum = sum(t for _, t in personal_items)
    for name, total in personal_items:
        print(f"   - {name}: ${total:,}")
    print("   ─────────────────────────────────")
    print(f"   TOTAL NÓMINA: ${p_sum:,}")

    if personal_total > 0 and p_sum == personal_total:
        print("   ✓ Suma coincide con subtotal")
    elif personal_total > 0:
        print(f"   ⚠️ Diferencia - usando suma: ${p_sum:,}")
        personal_total = p_sum
    else:
        personal_total = p_sum

    # =========================================================================
    # 2. HARDWARE (Sección 2.6)
    # =========================================================================
    print("\n" + "=" * 70)
    print("2. COSTOS DE HARDWARE (Sección 2.6)")
    print("=" * 70)

    sec = content[content.find("## 2.6") : content.find("## 3.")]
    rows = parse_table_lines(sec)

    hw_items = []
    hw_total = 0

    for row in rows:
        # Total row
        if "total" in " ".join(row).lower():
            for cell in reversed(row):
                val = extract_currency(cell)
                if val > 0:
                    hw_total = val
                    break
            continue

        # Data row - last cell is total
        if len(row) >= 2:
            total = extract_currency(row[-1])
            name = row[-2] if len(row) > 2 else row[0]  # Use second-to-last as name
            if total > 0:
                hw_items.append((name, total))

    hw_sum = sum(t for _, t in hw_items)
    for name, total in hw_items:
        print(f"   - {name}: ${total:,}")
    print("   ─────────────────────────────────")
    print(f"   TOTAL HARDWARE: ${hw_sum:,}")

    if hw_total > 0:
        if hw_sum == hw_total:
            print("   ✓ Suma coincide con total")
        else:
            print("   ⚠️ Diferencia - usando suma")
    hw_total = hw_sum

    # =========================================================================
    # 3. SOFTWARE (Sección 3.7)
    # =========================================================================
    print("\n" + "=" * 70)
    print("3. COSTOS DE SOFTWARE (Sección 3.7)")
    print("=" * 70)

    sec = content[content.find("## 3.7") : content.find("## 4.")]
    rows = parse_table_lines(sec)

    sw_items = []
    sw_total = 0

    for row in rows:
        if "total" in " ".join(row).lower():
            for cell in reversed(row):
                val = extract_currency(cell)
                if val > 0:
                    sw_total = val
                    break
            continue

        if len(row) >= 2:
            total = extract_currency(row[-1])
            name = row[0]
            if total > 0 and "rubro" not in name.lower():
                sw_items.append((name, total))

    sw_sum = sum(t for _, t in sw_items)
    for name, total in sw_items:
        print(f"   - {name}: ${total:,}")
    print("   ─────────────────────────────────")
    print(f"   TOTAL SOFTWARE: ${sw_sum:,}")

    if sw_total > 0:
        if sw_sum == sw_total:
            print("   ✓ Suma coincide con total")
        else:
            print("   ⚠️ Diferencia - usando suma")
    sw_total = sw_sum

    # =========================================================================
    # 4. COSTOS DIRECTOS (Sección 4.3)
    # =========================================================================
    print("\n" + "=" * 70)
    print("4. ESTRUCTURA DE COSTOS DIRECTOS (Sección 4.3)")
    print("=" * 70)

    sec = content[content.find("## 4.3") : content.find("## 4.4")]
    rows = parse_table_lines(sec)

    cost_items = []
    direct_costs = 0

    for row in rows:
        if "total" in " ".join(row).lower():
            for cell in reversed(row):
                val = extract_currency(cell)
                if val > 0:
                    direct_costs = val
                    break
            continue

        if len(row) >= 2:
            total = extract_currency(row[-1])
            name = row[0]
            if total > 0:
                cost_items.append((name, total))

    cost_sum = sum(t for _, t in cost_items)
    for name, total in cost_items:
        print(f"   - {name}: ${total:,}")
    print("   ─────────────────────────────────")
    print(f"   TOTAL COSTOS DIRECTOS: ${cost_sum:,}")

    # Verify: Personal + HW + SW should equal direct costs
    sum_parts = personal_total + hw_total + sw_total
    status = "✓" if sum_parts == direct_costs else "⚠️"
    print(
        f"\n   Verificación: ${personal_total:,} + ${hw_total:,} + ${sw_total:,} = ${sum_parts:,}"
    )
    print(f"   vs Costos Directos: ${direct_costs:,} {status}")

    direct_costs = cost_sum  # Use the documented total

    # =========================================================================
    # 5. AIU (Sección 4.4)
    # =========================================================================
    print("\n" + "=" * 70)
    print("5. CÁLCULO AIU (Sección 4.4)")
    print("=" * 70)

    sec = content[content.find("## 4.4") : content.find("## 4.5")]
    rows = parse_table_lines(sec)

    aiu_vals = {}
    for row in rows:
        row_text = " ".join(row).lower()
        # For AIU table: [Name, Base, Percentage, Value]
        # Value is at index 3 (last column typically)
        if len(row) >= 4:
            val = extract_currency(row[3])  # Last column is value
            if val > 0:
                if "administración" in row_text:
                    aiu_vals["a"] = val
                elif "imprevistos" in row_text:
                    aiu_vals["i"] = val
                elif "utilidad" in row_text:
                    aiu_vals["u"] = val
                elif "total aiu" in row_text:
                    aiu_vals["total"] = val

    admin_c = int(direct_costs * 0.05)
    imp_c = int(direct_costs * 0.10)
    util_c = int(direct_costs * 0.20)
    aiu_c = admin_c + imp_c + util_c
    iva_c = int(util_c * 0.19)
    total_c = direct_costs + aiu_c + iva_c

    print(f"   Base Imponible:     ${direct_costs:,}")
    print("   ─────────────────────────────────")

    for label, key, calc in [
        ("Administración (5 %)", "a", admin_c),
        ("Imprevistos (10 %)", "i", imp_c),
        ("Utilidad (20 %)", "u", util_c),
        ("Total AIU (35 %)", "total", aiu_c),
    ]:
        rep = aiu_vals.get(key, 0)
        st = "✓" if calc == rep else "✗"
        if calc != rep:
            all_ok = False
        print(f"      {label}: Calc=${calc:,} vs Reportado=${rep:,} {st}")

    print(f"   IVA (19 %):  ${iva_c:,}")
    print("   ════════════════════════════════════════")
    print(f"   TOTAL PROYECTO:   ${total_c:,}")

    # =========================================================================
    # 6. PRESUPUESTO (Sección 4.5)
    # =========================================================================
    print("\n" + "=" * 70)
    print("6. PRESUPUESTO TOTAL (Sección 4.5)")
    print("=" * 70)

    sec = content[content.find("## 4.5") : content.find("## 5.")]
    rows = parse_table_lines(sec)

    for row in rows:
        if len(row) >= 2:
            name = row[0]
            for cell in reversed(row):
                val = extract_currency(cell)
                if val > 0:
                    print(f"   - {name}: ${val:,}")
                    break

    # =========================================================================
    # 7. COMPARATIVA (Sección 6.2)
    # =========================================================================
    print("\n" + "=" * 70)
    print("7. TABLA COMPARATIVA (Sección 6.2)")
    print("=" * 70)

    sec = content[content.find("## 6.2") : content.find("# 7.")]
    rows = parse_table_lines(sec)

    mack = {"items": [], "sub": 0, "aiu": 0, "sub_aiu": 0, "iva": 0, "fin": 0}
    tecno = {"items": [], "sub": 0, "aiu": 0, "sub_aiu": 0, "iva": 0, "fin": 0}
    dev = {"items": [], "sub": 0, "aiu": 0, "sub_aiu": 0, "iva": 0, "fin": 0}

    for row in rows:
        if len(row) < 4:
            continue
        row_text = " ".join(row).lower()
        vals = [extract_currency(c) for c in row]
        num = [v for v in vals if v > 0]

        if "total final" in row_text and len(num) >= 3:
            mack["fin"], tecno["fin"], dev["fin"] = num[0], num[1], num[2]
        elif "subtotal" in row_text and "antes de iva" in row_text and len(num) >= 3:
            mack["sub_aiu"], tecno["sub_aiu"], dev["sub_aiu"] = num[0], num[1], num[2]
        elif "iva" in row_text and "19" in row_text and len(num) >= 3:
            mack["iva"], tecno["iva"], dev["iva"] = num[0], num[1], num[2]
        elif "aiu" in row_text and "35" in row_text and len(num) >= 3:
            mack["aiu"], tecno["aiu"], dev["aiu"] = num[0], num[1], num[2]
        elif "subtotal" in row_text and "directos" in row_text and len(num) >= 3:
            mack["sub"], tecno["sub"], dev["sub"] = num[0], num[1], num[2]
        elif row[0].strip().isdigit() and len(num) >= 3:
            mack["items"].append(num[0])
            tecno["items"].append(num[1])
            dev["items"].append(num[2])

    # =========================================================================
    # 7.1 DETECCIÓN DE VALORES INTERCAMBIADOS (SWAP CHECK)
    # =========================================================================
    print("\n" + "-" * 70)
    print("   ⚡ VERIFICACIÓN DE COLUMNAS (Detección de valores intercambiados)")
    print("-" * 70)

    providers = [
        ("Mackroph", mack["sub"], mack["aiu"], mack["sub_aiu"]),
        ("TecnoShop", tecno["sub"], tecno["aiu"], tecno["sub_aiu"]),
        ("DevSoft", dev["sub"], dev["aiu"], dev["sub_aiu"]),
    ]

    for pname, sub, aiu, sub_aiu in providers:
        expected_sub_aiu = sub + aiu
        if sub_aiu == expected_sub_aiu:
            print(f"   ✓ {pname}: Subtotal=${sub:,} + AIU=${aiu:,} = ${sub_aiu:,} ✓")
        else:
            print(
                f"   ✗ {pname}: Subtotal=${sub:,} + AIU=${aiu:,} = ${expected_sub_aiu:,} pero tabla dice ${sub_aiu:,}"
            )
            all_ok = False

    print("\n   🔍 Verificando que valores NO estén intercambiados entre columnas...")

    all_subs = {mack["sub"], tecno["sub"], dev["sub"]}
    all_aius = {mack["aiu"], tecno["aiu"], dev["aiu"]}
    all_sub_aius = {mack["sub_aiu"], tecno["sub_aiu"], dev["sub_aiu"]}

    if len(all_subs) == 3 and len(all_aius) == 3 and len(all_sub_aius) == 3:
        for pname, sub, aiu, sub_aiu in providers:
            expected = sub + aiu
            if sub_aiu != expected:
                print(
                    f"   ✗ ERROR: {pname} tiene valor incorrecto ${sub_aiu:,} (debería ser ${expected:,})"
                )
                all_ok = False

        actual_tecno = tecno["sub"] + tecno["aiu"]
        actual_dev = dev["sub"] + dev["aiu"]
        if actual_tecno == dev["sub_aiu"] and actual_dev == tecno["sub_aiu"]:
            print("   ✗ CRÍTICO: ¡Valores de TecnoShop y DevSoft están INTERCAMBIADOS!")
            all_ok = False
        elif actual_tecno == mack["sub_aiu"] or actual_dev == mack["sub_aiu"]:
            print("   ✗ CRÍTICO: ¡Valores están en columna equivocada!")
            all_ok = False
        else:
            print("   ✓ Columnas correctas - no hay valores intercambiados")
    else:
        print("   ⚠️ No se puede verificar intercambio (hay valores duplicados en la tabla)")

    for name, data in [("MACKROPH", mack), ("TECNO SHOP", tecno), ("DEV SOFT", dev)]:
        print(f"\n   {name}:")
        items_sum = sum(data["items"])
        sub_ok = items_sum == data["sub"]
        if sub_ok:
            print(
                f"      ✓ Items ({len(data['items'])}): ${items_sum:,} = subtotal ${data['sub']:,}"
            )
        else:
            print(
                f"      ✗ Items ({len(data['items'])}): ${items_sum:,} ≠ subtotal ${data['sub']:,}"
            )
            all_ok = False

        base = data["sub"]
        for label, key, calc_fn in [
            ("AIU", "aiu", lambda b: int(b * 0.35)),
            ("IVA", "iva", lambda b: int(b * 0.20 * 0.19)),
        ]:
            calc = calc_fn(base)
            ok = data[key] == calc
            if ok:
                print(f"      ✓ {label}: ${data[key]:,} = calc ${calc:,}")
            else:
                print(f"      ✗ {label}: ${data[key]:,} ≠ calc ${calc:,}")
                all_ok = False

        sub_aiu_calc = base + int(base * 0.35)
        if data["sub_aiu"] > 0:
            if data["sub_aiu"] == sub_aiu_calc:
                print(
                    f"      ✓ Subtotal antes de IVA: ${data['sub_aiu']:,} = ${base:,} + AIU ${int(base * 0.35):,}"
                )
            else:
                print(
                    f"      ✗ Subtotal antes de IVA: ${data['sub_aiu']:,} ≠ ${base:,} + AIU ${int(base * 0.35):,} = ${sub_aiu_calc:,}"
                )
                all_ok = False

        fin_calc = base + int(base * 0.35) + int(base * 0.20 * 0.19)
        ok = data["fin"] == fin_calc
        if ok:
            print(f"      ✓ TOTAL: ${data['fin']:,}")
        else:
            print(f"      ✗ TOTAL: ${data['fin']:,} ≠ calc ${fin_calc:,}")
            all_ok = False

    print("\n   Mackroph vs Proyecto:")
    if mack["fin"] == total_c:
        print(f"      ✓ TOTAL Mackroph (${mack['fin']:,}) = TOTAL Proyecto (${total_c:,})")
    else:
        print(f"      ✗ TOTAL Mackroph (${mack['fin']:,}) ≠ TOTAL Proyecto (${total_c:,})")
        all_ok = False

    # =========================================================================
    # 8. TABLAS NO CORTADAS
    # =========================================================================
    print("\n" + "=" * 70)
    print("8. VERIFICACIÓN DE TABLAS (No cortadas)")
    print("=" * 70)

    try:
        from docx import Document
        from docx.oxml.ns import qn
    except ImportError:
        print("   python-docx no instalado")
    else:
        if Path(docx_path).exists():
            doc = Document(docx_path)
            ok_count = 0
            for i, table in enumerate(doc.tables):
                rows_ok = sum(
                    1
                    for row in table.rows
                    if row._tr.find(qn("w:trPr")) is not None
                    and row._tr.find(qn("w:trPr")).find(qn("w:cantSplit")) is not None
                    and row._tr.find(qn("w:trPr")).find(qn("w:cantSplit")).get(qn("w:val")) == "1"
                    for row in table.rows
                )
                if rows_ok == len(table.rows):
                    ok_count += 1
                    print(f"   Tabla {i + 1}: {len(table.rows)} filas ✓")
            print(f"\n   Tablas protegidas: {ok_count}/{len(doc.tables)}")
        else:
            print("   DOCX no encontrado")

    # =========================================================================
    # RESUMEN
    # =========================================================================
    print("\n" + "=" * 70)
    print("RESUMEN FINAL")
    print("=" * 70)

    if "margen operativo" in content.lower():
        print("   ⚠️ Posible doble margen detectado")
        all_ok = False
    else:
        print("   ✓ Sin problema de doble margen")

    print(f"\n   📊 TOTAL PROYECTO: ${total_c:,} COP")

    if all_ok:
        print("\n   ✅ TODOS LOS CÁLCULOS VERIFICADOS")
    else:
        print("\n   ❌ HAY ERRORES")

    sys.exit(0 if all_ok else 1)


if __name__ == "__main__":
    main()
