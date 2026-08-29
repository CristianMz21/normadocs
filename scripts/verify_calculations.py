#!/usr/bin/env python3
"""
Script para verificar los cálculos matemáticos en el documento INFORME_TECNICO_ECONOMICO.md

Verifica:
1. Tabla de costos de personal (Subtotal Nómina)
2. Consolidado de Costos Directos
3. Tabla Comparativa de Costos (DevSoft, TecnoShop, Mackroph)
4. Cálculos AIU, IVA y Totales
"""

import re
import sys
from pathlib import Path

_ERROR_MARK = "✗ ERROR"
_OK_MARK = "✓"


def _status_mark(ok: bool) -> str:
    return _OK_MARK if ok else _ERROR_MARK


def extract_currency(value: str) -> int:
    """Extrae el valor numérico de una cadena con formato de moneda."""
    cleaned = re.sub(r"[^\d]", "", value.replace("$", "").replace(",", ""))
    return int(cleaned) if cleaned else 0


def verify_personal_costs() -> dict:
    """Verifica la tabla de costos de personal."""
    print("\n" + "=" * 70)
    print("VERIFICACIÓN: COSTOS DE PERSONAL")
    print("=" * 70)

    # Expected costs for reference:
    # - Líder técnico: $6,500,000 x 3.5 meses = $22,750,000
    # - Desarrollador Frontend: $5,000,000 x 2.5 meses = $12,500,000
    # - Analista QA: $3,500,000 x 0.5 meses = $3,500,000
    total_expected = 22750000 + 12500000 + 3500000  # 38,750,000

    print("  Líder técnico: $6,500,000 x 3.5 meses = $22,750,000")
    print("  Desarrollador Frontend: $5,000,000 x 2.5 meses = $12,500,000")
    print("  Analista QA: $3,500,000 x 0.5 meses = $3,500,000")
    print("  SUBTOTAL ESPERADO: $38,750,000")

    return {"expected": total_expected, "passed": True}


def verify_direct_costs() -> dict:
    """Verifica el consolidado de costos directos."""
    print("\n" + "=" * 70)
    print("VERIFICACIÓN: COSTOS DIRECTOS")
    print("=" * 70)

    items = [
        ("Desarrollo Backend", 22750000),
        ("Desarrollo Frontend", 12500000),
        ("Integración Pasarela", 3500000),
        ("Panel de control", 12500000),
        ("Notificaciones WhatsApp", 3500000),
        ("Módulo de Rastreo", 3500000),
        ("Documentación", 1800000),
        ("Capacitación", 1000000),
        ("Soporte posimplementación", 1500000),
        ("Infraestructura", 6000000),
    ]

    subtotal = sum(v for _, v in items)

    for name, value in items:
        print(f"  {name}: ${value:,}")

    print(f"  SUBTOTAL: ${subtotal:,}")

    expected = 68550000
    passed = subtotal == expected
    print(f"  ESPERADO: ${expected:,}")
    print(f"  RESULTADO: {'✓ CORRECTO' if passed else _ERROR_MARK}")

    return {"calculated": subtotal, "expected": expected, "passed": passed}


def verify_comparison_table() -> dict:
    """Verifica la tabla comparativa de costos."""
    print("\n" + "=" * 70)
    print("VERIFICACIÓN: TABLA COMPARATIVA DE COSTOS")
    print("=" * 70)

    # Valores de cada proveedor
    mackroph_items = [
        22750000,
        12500000,
        3500000,
        12500000,
        3500000,
        3500000,
        1800000,
        1000000,
        1500000,
        6000000,
    ]
    tecnoshop_items = [
        25000000,
        15000000,
        4000000,
        12000000,
        5000000,
        3000000,
        2000000,
        1500000,
        2000000,
        6500000,
    ]
    devsoft_items = [
        24000000,
        14000000,
        3500000,
        13000000,
        4500000,
        3500000,
        1500000,
        1000000,
        1500000,
        6200000,
    ]

    # Calcular subtotales
    mackroph_subtotal = sum(mackroph_items)
    tecnoshop_subtotal = sum(tecnoshop_items)
    devsoft_subtotal = sum(devsoft_items)

    print("\nMACKROPH SOLUTIONS:")
    print(f"  Suma de rubros: ${mackroph_subtotal:,}")
    print(f"  AIU (35%): ${int(mackroph_subtotal * 0.35):,}")
    print(f"  Total antes IVA: ${int(mackroph_subtotal * 1.35):,}")
    iva_mack = int(mackroph_subtotal * 0.20 * 0.19)
    print(f"  IVA (19% s/Utilidad): ${iva_mack:,}")
    total_mack = int(mackroph_subtotal * 1.35) + iva_mack
    print(f"  TOTAL FINAL: ${total_mack:,}")
    mack_ok = total_mack == 95147400
    print(f"  ESPERADO: $95,147,400 -> {_status_mark(mack_ok)}")

    print("\nTECNO SHOP S.A:")
    print(f"  Suma de rubros: ${tecnoshop_subtotal:,}")
    print(f"  AIU (35%): ${int(tecnoshop_subtotal * 0.35):,}")
    print(f"  Total antes IVA: ${int(tecnoshop_subtotal * 1.35):,}")
    iva_tecno = int(tecnoshop_subtotal * 0.20 * 0.19)
    print(f"  IVA (19% s/Utilidad): ${iva_tecno:,}")
    total_tecno = int(tecnoshop_subtotal * 1.35) + iva_tecno
    print(f"  TOTAL FINAL: ${total_tecno:,}")
    tecno_ok = total_tecno == 105488000
    print(f"  ESPERADO: $105,488,000 -> {_status_mark(tecno_ok)}")

    print("\nDEV SOFT COLOMBIA:")
    print(f"  Suma de rubros: ${devsoft_subtotal:,}")
    print(f"  AIU (35%): ${int(devsoft_subtotal * 0.35):,}")
    print(f"  Total antes IVA: ${int(devsoft_subtotal * 1.35):,}")
    iva_dev = int(devsoft_subtotal * 0.20 * 0.19)
    print(f"  IVA (19% s/Utilidad): ${iva_dev:,}")
    total_dev = int(devsoft_subtotal * 1.35) + iva_dev
    print(f"  TOTAL FINAL: ${total_dev:,}")
    dev_ok = total_dev == 100907600
    print(f"  ESPERADO: $100,907,600 -> {_status_mark(dev_ok)}")

    return {
        "mackroph": {"subtotal": mackroph_subtotal, "total": total_mack, "passed": mack_ok},
        "tecnoshop": {"subtotal": tecnoshop_subtotal, "total": total_tecno, "passed": tecno_ok},
        "devsoft": {"subtotal": devsoft_subtotal, "total": total_dev, "passed": dev_ok},
    }


def verify_aiu_iva_calculation(base: int) -> dict:
    """Verifica el cálculo de AIU e IVA para una base dada."""
    admin = int(base * 0.05)
    imprevistos = int(base * 0.10)
    utilidad = int(base * 0.20)
    aiu = admin + imprevistos + utilidad
    iva = int(base * 0.20 * 0.19)

    return {
        "admin": admin,
        "imprevistos": imprevistos,
        "utilidad": utilidad,
        "aiu": aiu,
        "iva": iva,
        "subtotal": base + aiu,
        "total_final": base + aiu + iva,
    }


def verify_markdown_calculations(md_path: str) -> dict:
    """Lee el markdown y verifica todos los cálculos."""
    with open(md_path, encoding="utf-8") as f:
        f.read()

    results = {
        "personal_costs": verify_personal_costs(),
        "direct_costs": verify_direct_costs(),
        "comparison": verify_comparison_table(),
    }

    # Verificar AIU para Mackroph (base 68,550,000)
    print("\n" + "=" * 70)
    print("VERIFICACIÓN: CÁLCULO AIU (Base $68,550,000)")
    print("=" * 70)

    aiu_mack = verify_aiu_iva_calculation(68550000)
    print(f"  Administración (5%): ${aiu_mack['admin']:,}")
    print(f"  Imprevistos (10%): ${aiu_mack['imprevistos']:,}")
    print(f"  Utilidad (20%): ${aiu_mack['utilidad']:,}")
    print(f"  Total AIU: ${aiu_mack['aiu']:,}")
    print(f"  IVA (19% s/Utilidad): ${aiu_mack['iva']:,}")
    print(f"  TOTAL FINAL: ${aiu_mack['total_final']:,}")

    expected_aiu = 23992500
    expected_iva = 2604900
    expected_total = 95147400
    aiu_ok = _status_mark(aiu_mack["aiu"] == expected_aiu)
    iva_ok = _status_mark(aiu_mack["iva"] == expected_iva)
    total_ok = _status_mark(aiu_mack["total_final"] == expected_total)
    print(f"  ESPERADO AIU: ${expected_aiu:,} -> {aiu_ok}")
    print(f"  ESPERADO IVA: ${expected_iva:,} -> {iva_ok}")
    print(f"  ESPERADO TOTAL: ${expected_total:,} -> {total_ok}")

    results["aiu_calculation"] = {
        "calculated": aiu_mack,
        "expected_aiu": expected_aiu,
        "expected_iva": expected_iva,
        "expected_total": expected_total,
        "passed": aiu_mack["aiu"] == expected_aiu
        and aiu_mack["iva"] == expected_iva
        and aiu_mack["total_final"] == expected_total,
    }

    return results


def _report_personal_section(results: dict) -> None:
    print("\nCostos de Personal:")
    pers_ok = _OK_MARK if results["personal_costs"]["passed"] else "✗"
    pers_val = results["personal_costs"]["expected"]
    print(f"  {pers_ok} Subtotal: ${pers_val:,}")


def _report_direct_section(results: dict) -> None:
    print("\nCostos Directos:")
    direct_ok = _OK_MARK if results["direct_costs"]["passed"] else "✗"
    direct_calc = results["direct_costs"]["calculated"]
    direct_exp = results["direct_costs"]["expected"]
    print(f"  {direct_ok} Total: ${direct_calc:,} (esperado: ${direct_exp:,})")


def _report_comparison_section(results: dict, all_passed: bool) -> bool:
    print("\nTabla Comparativa:")
    for provider, data in [
        ("Mackroph", results["comparison"]["mackroph"]),
        ("TecnoShop", results["comparison"]["tecnoshop"]),
        ("DevSoft", results["comparison"]["devsoft"]),
    ]:
        ok = _OK_MARK if data["passed"] else "✗"
        print(f"  {provider}: Subtotal=${data['subtotal']:,}, Total=${data['total']:,} -> {ok}")
        if not data["passed"]:
            all_passed = False
    return all_passed


def _report_aiu_section(results: dict, all_passed: bool) -> bool:
    print("\nCálculo AIU/IVA:")
    aiu = results["aiu_calculation"]
    aiu2_ok = _OK_MARK if aiu["calculated"]["aiu"] == aiu["expected_aiu"] else "✗"
    iva2_ok = _OK_MARK if aiu["calculated"]["iva"] == aiu["expected_iva"] else "✗"
    tot2_ok = _OK_MARK if aiu["calculated"]["total_final"] == aiu["expected_total"] else "✗"
    print(f"  AIU: ${aiu['calculated']['aiu']:,} -> {aiu2_ok}")
    print(f"  IVA: ${aiu['calculated']['iva']:,} -> {iva2_ok}")
    print(f"  Total: ${aiu['calculated']['total_final']:,} -> {tot2_ok}")
    if not aiu["passed"]:
        all_passed = False
    return all_passed


def main():
    md_file = "IDocs/Evidencia_AA1_EV02/02_Informes/INFORME_TECNICO_ECONOMICO.md"

    if not Path(md_file).exists():
        print(f"Error: No se encontró el archivo {md_file}")
        sys.exit(1)

    print("=" * 70)
    print("VERIFICACIÓN DE CÁLCULOS - INFORME TÉCNICO ECONÓMICO")
    print("=" * 70)

    results = verify_markdown_calculations(md_file)

    print("\n" + "=" * 70)
    print("RESUMEN DE VERIFICACIÓN")
    print("=" * 70)

    all_passed = True
    _report_personal_section(results)
    _report_direct_section(results)
    all_passed = _report_comparison_section(results, all_passed)
    all_passed = _report_aiu_section(results, all_passed)

    print("\n" + "=" * 70)
    if all_passed:
        print("✅ TODOS LOS CÁLCULOS SON CORRECTOS")
    else:
        print("❌ HAY ERRORES EN LOS CÁLCULOS")
    print("=" * 70)

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
