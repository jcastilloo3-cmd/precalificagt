"""Descarga PHPUnit 10.5 (compatible con PHP 8.1+) en tools/phpunit.phar si no existe.

Se usa el PHAR oficial para no exigir Composer en el agente de Jenkins.
"""
import os
import sys
import urllib.request

RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DESTINO = os.path.join(RAIZ, "tools", "phpunit.phar")
URL = os.environ.get("PHPUNIT_URL", "https://phar.phpunit.de/phpunit-10.5.phar")

if os.path.exists(DESTINO) and os.path.getsize(DESTINO) > 1_000_000:
    print(f"PHPUnit ya disponible en {DESTINO}")
    sys.exit(0)
os.makedirs(os.path.dirname(DESTINO), exist_ok=True)
print(f"Descargando {URL} ...")
# phar.phpunit.de rechaza (HTTP 403) el agente por defecto "Python-urllib"
peticion = urllib.request.Request(URL, headers={"User-Agent": "Mozilla/5.0 (PrecalificaGT CI)"})
with urllib.request.urlopen(peticion, timeout=120) as respuesta, open(DESTINO, "wb") as salida:
    salida.write(respuesta.read())
print(f"PHPUnit guardado en {DESTINO} ({os.path.getsize(DESTINO) // 1024} KB)")
