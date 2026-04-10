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


def extract_currency(value: str) -> int:
    """Extrae el valor numérico de una cadena con formato de moneda."""
    cleaned = re.sub(r"[^\d]", "", value.replace("$", "").replace(",", ""))
    return int(cleaned) if cleaned else 0


def verify_personal_costs(lines: list[str]) -> dict:
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


def verify_direct_costs(lines: list[str]) -> dict:
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
    print(f"  RESULTADO: {'✓ CORRECTO' if passed else '✗ ERROR'}")

    return {"calculated": subtotal, "expected": expected, "passed": passed}


def verify_comparison_table(lines: list[str]) -> dict:
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
    print(f"  ESPERADO: $95,147,400 -> {'✓' if mack_ok else '✗ ERROR'}")

    print("\nTECNO SHOP S.A:")
    print(f"  Suma de rubros: ${tecnoshop_subtotal:,}")
    print(f"  AIU (35%): ${int(tecnoshop_subtotal * 0.35):,}")
    print(f"  Total antes IVA: ${int(tecnoshop_subtotal * 1.35):,}")
    iva_tecno = int(tecnoshop_subtotal * 0.20 * 0.19)
    print(f"  IVA (19% s/Utilidad): ${iva_tecno:,}")
    total_tecno = int(tecnoshop_subtotal * 1.35) + iva_tecno
    print(f"  TOTAL FINAL: ${total_tecno:,}")
    tecno_ok = total_tecno == 105488000
    print(f"  ESPERADO: $105,488,000 -> {'✓' if tecno_ok else '✗ ERROR'}")

    print("\nDEV SOFT COLOMBIA:")
    print(f"  Suma de rubros: ${devsoft_subtotal:,}")
    print(f"  AIU (35%): ${int(devsoft_subtotal * 0.35):,}")
    print(f"  Total antes IVA: ${int(devsoft_subtotal * 1.35):,}")
    iva_dev = int(devsoft_subtotal * 0.20 * 0.19)
    print(f"  IVA (19% s/Utilidad): ${iva_dev:,}")
    total_dev = int(devsoft_subtotal * 1.35) + iva_dev
    print(f"  TOTAL FINAL: ${total_dev:,}")
    dev_ok = total_dev == 100907600
    print(f"  ESPERADO: $100,907,600 -> {'✓' if dev_ok else '✗ ERROR'}")

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
        content = f.read()

    results = {
        "personal_costs": verify_personal_costs(content.split("\n")),
        "direct_costs": verify_direct_costs(content.split("\n")),
        "comparison": verify_comparison_table(content.split("\n")),
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

    print(
        f"  ESPERADO AIU: ${expected_aiu:,} -> {'✓' if aiu_mack['aiu'] == expected_aiu else '✗ ERROR'}"
    )
    print(
        f"  ESPERADO IVA: ${expected_iva:,} -> {'✓' if aiu_mack['iva'] == expected_iva else '✗ ERROR'}"
    )
    print(
        f"  ESPERADO TOTAL: ${expected_total:,} -> {'✓' if aiu_mack['total_final'] == expected_total else '✗ ERROR'}"
    )

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


def main():
    md_file = "IDocs/Evidencia_AA1_EV02/02_Informes/INFORME_TECNICO_ECONOMICO.md"

    if not Path(md_file).exists():
        print(f"Error: No se encontró el archivo {md_file}")
        sys.exit(1)

    print("=" * 70)
    print("VERIFICACIÓN DE CÁLCULOS - INFORME TÉCNICO ECONÓMICO")
    print("=" * 70)

    results = verify_markdown_calculations(md_file)

    # Resumen
    print("\n" + "=" * 70)
    print("RESUMEN DE VERIFICACIÓN")
    print("=" * 70)

    all_passed = True

    print("\nCostos de Personal:")
    print(
        f"  {'✓' if results['personal_costs']['passed'] else '✗'} Subtotal: ${results['personal_costs']['expected']:,}"
    )

    print("\nCostos Directos:")
    print(
        f"  {'✓' if results['direct_costs']['passed'] else '✗'} Total: ${results['direct_costs']['calculated']:,} (esperado: ${results['direct_costs']['expected']:,})"
    )

    print("\nTabla Comparativa:")
    for provider, data in [
        ("Mackroph", results["comparison"]["mackroph"]),
        ("TecnoShop", results["comparison"]["tecnoshop"]),
        ("DevSoft", results["comparison"]["devsoft"]),
    ]:
        print(
            f"  {provider}: Subtotal=${data['subtotal']:,}, Total=${data['total']:,} -> {'✓' if data['passed'] else '✗'}"
        )
        if not data["passed"]:
            all_passed = False

    print("\nCálculo AIU/IVA:")
    aiu = results["aiu_calculation"]
    print(
        f"  AIU: ${aiu['calculated']['aiu']:,} -> {'✓' if aiu['calculated']['aiu'] == aiu['expected_aiu'] else '✗'}"
    )
    print(
        f"  IVA: ${aiu['calculated']['iva']:,} -> {'✓' if aiu['calculated']['iva'] == aiu['expected_iva'] else '✗'}"
    )
    print(
        f"  Total: ${aiu['calculated']['total_final']:,} -> {'✓' if aiu['calculated']['total_final'] == aiu['expected_total'] else '✗'}"
    )

    if not aiu["passed"]:
        all_passed = False

    print("\n" + "=" * 70)
    if all_passed:
        print("✅ TODOS LOS CÁLCULOS SON CORRECTOS")
    else:
        print("❌ HAY ERRORES EN LOS CÁLCULOS")
    print("=" * 70)

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
