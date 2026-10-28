"""Cobertura de los módulos críticos (E2, sección 3.7 de la Fase 1) contra la línea base.

Lee el reporte Cobertura de pytest-cov y calcula la cobertura de líneas de MOT, SOL,
AUT y VAL. La línea base registrada en la Fase 1 es 0 % (sin pruebas). El paso falla
si el incremento agregado es menor a 20 puntos porcentuales (exigencia de E10).

Uso: python ci/cobertura_criticos.py reports/coverage.xml
"""
import os
import sys
import xml.etree.ElementTree as ET

LINEA_BASE = 0.0
INCREMENTO_MINIMO = 20.0
MODULOS = {
    "AUT  Autenticación y seguridad": ["rutas/auth.py", "seguridad.py", "config.py"],
    "VAL  Validaciones": ["validaciones.py"],
    "MOT  Motor de precalificación": ["servicios/motor_reglas.py", "servicios/calculadora.py",
                                      "servicios/politica.py"],
    "SOL  Solicitudes y estados": ["rutas/solicitudes.py", "servicios/estados.py"],
}


def leer(ruta):
    lineas = {}
    for clase in ET.parse(ruta).getroot().iter("class"):
        nombre = clase.get("filename").replace("\\", "/")
        nombre = nombre.split("backend/app/")[-1]
        filas = clase.findall("./lines/line")
        cubiertas = sum(1 for f in filas if int(f.get("hits", "0")) > 0)
        lineas[nombre] = (cubiertas, len(filas))
    return lineas


def main():
    ruta = sys.argv[1] if len(sys.argv) > 1 else "reports/coverage.xml"
    datos = leer(ruta)
    filas, total_c, total_v = [], 0, 0
    for modulo, archivos in MODULOS.items():
        c = sum(datos.get(a, (0, 0))[0] for a in archivos)
        v = sum(datos.get(a, (0, 0))[1] for a in archivos)
        total_c, total_v = total_c + c, total_v + v
        filas.append((modulo, c, v, 100.0 * c / v if v else 0.0))
    agregado = 100.0 * total_c / total_v if total_v else 0.0
    incremento = agregado - LINEA_BASE

    salida = ["| Módulo crítico | Líneas cubiertas | Cobertura | Línea base | Incremento |",
              "|---|---|---|---|---|"]
    for modulo, c, v, pct in filas:
        salida.append(f"| {modulo} | {c}/{v} | {pct:.1f} % | {LINEA_BASE:.1f} % | +{pct - LINEA_BASE:.1f} pp |")
    salida.append(f"| **Total críticos** | {total_c}/{total_v} | **{agregado:.1f} %** | "
                  f"{LINEA_BASE:.1f} % | **+{incremento:.1f} pp** |")
    texto = "\n".join(salida)
    print(texto)
    os.makedirs("reports", exist_ok=True)
    with open(os.path.join("reports", "cobertura_criticos.md"), "w", encoding="utf-8") as f:
        f.write(texto + "\n")
    if incremento < INCREMENTO_MINIMO:
        sys.exit(f"Incremento de {incremento:.1f} pp menor al mínimo de {INCREMENTO_MINIMO} pp")
    print(f"OK: incremento de {incremento:.1f} pp sobre la línea base (mínimo {INCREMENTO_MINIMO} pp)")


if __name__ == "__main__":
    main()
