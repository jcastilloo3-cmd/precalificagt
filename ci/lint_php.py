"""Etapa 1 (compilación) del frontend: verifica la sintaxis de todos los .php con `php -l`.

Uso: python ci/lint_php.py [ruta_a_php]   (por defecto PHP_EXE o "php")
"""
import os
import subprocess
import sys

RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
php = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("PHP_EXE", "php")

archivos = []
for carpeta, _, nombres in os.walk(os.path.join(RAIZ, "frontend")):
    archivos += [os.path.join(carpeta, n) for n in nombres if n.endswith(".php")]

errores = 0
for archivo in sorted(archivos):
    resultado = subprocess.run([php, "-l", archivo], capture_output=True, text=True)
    if resultado.returncode != 0:
        errores += 1
        print(resultado.stdout + resultado.stderr)
print(f"php -l: {len(archivos)} archivos revisados, {errores} con errores de sintaxis")
sys.exit(1 if errores else 0)
