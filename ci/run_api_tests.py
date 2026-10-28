"""Ejecuta la colección Postman con Newman (etapa 4 del pipeline).

Sin --base-url: levanta la API en un ambiente de integración efímero (SQLite nueva en
una carpeta temporal y puerto local), espera a /api/health, ejecuta Newman y apaga la
API. Con --base-url: ejecuta la colección contra un ambiente ya desplegado (QA).

Funciona igual en Windows y en Linux. Uso desde la raíz del repositorio:
    python ci/run_api_tests.py
    python ci/run_api_tests.py --base-url https://precalificagt-api-qa.onrender.com
"""
import argparse
import os
import secrets
import shlex
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request

RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
COLECCION = os.path.join(RAIZ, "tests", "api", "PrecalificaGT.postman_collection.json")
REPORTES = os.path.join(RAIZ, "reports")
NEWMAN_VERSION = "6.2.1"


def esperar_salud(url, segundos):
    limite = time.time() + segundos
    while time.time() < limite:
        try:
            with urllib.request.urlopen(url + "/api/health", timeout=10) as respuesta:
                if respuesta.status == 200:
                    return True
        except (urllib.error.URLError, OSError):
            pass
        time.sleep(2)
    return False


def comando_newman():
    """Usa NEWMAN_CMD si está definido; si no, newman global o npx con versión fija."""
    personalizado = os.environ.get("NEWMAN_CMD")
    if personalizado:
        return shlex.split(personalizado, posix=os.name != "nt")
    newman = shutil.which("newman")
    if newman:
        return [newman]
    npx = shutil.which("npx")
    if not npx and os.name == "nt":
        # Jenkins (servicio de Windows) no ve el PATH nuevo hasta reiniciarse: rutas típicas
        for carpeta in (os.environ.get("ProgramFiles", r"C:\Program Files"), r"C:\Program Files"):
            candidato = os.path.join(carpeta, "nodejs", "npx.cmd")
            if os.path.exists(candidato):
                npx = candidato
                os.environ["PATH"] = os.path.dirname(candidato) + os.pathsep + os.environ.get("PATH", "")
                break
    if not npx:
        sys.exit("No se encontró newman ni npx. Instale Node.js LTS y reinicie Jenkins.")
    return [npx, "--yes", f"newman@{NEWMAN_VERSION}"]


def ejecutar_newman(base_url):
    os.makedirs(REPORTES, exist_ok=True)
    comando = comando_newman() + [
        "run", COLECCION,
        "--env-var", f"baseUrl={base_url}",
        "--reporters", "cli,junit",
        "--reporter-junit-export", os.path.join(REPORTES, "newman.xml"),
        "--timeout-request", "90000",
        "--color", "off",
    ]
    print("Ejecutando:", " ".join(comando), flush=True)
    return subprocess.call(comando)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", help="URL de un ambiente desplegado (omitir para usar uno local)")
    parser.add_argument("--puerto", type=int, default=5055)
    args = parser.parse_args()

    if args.base_url:
        url = args.base_url.rstrip("/")
        print(f"Esperando a {url} (la capa gratuita puede tardar ~1 minuto en despertar)...")
        if not esperar_salud(url, 180):
            sys.exit(f"La API en {url} no respondió a /api/health")
        sys.exit(ejecutar_newman(url))

    carpeta = tempfile.mkdtemp(prefix="precalifica-ci-")
    entorno = dict(
        os.environ,
        DATABASE_URL="sqlite:///" + os.path.join(carpeta, "integracion.db").replace("\\", "/"),
        PORT=str(args.puerto),
        SECRET_KEY=os.environ.get("CI_SECRET_KEY") or secrets.token_hex(32),
    )
    registro = open(os.path.join(carpeta, "api.log"), "w", encoding="utf-8")
    servidor = subprocess.Popen(
        [sys.executable, "wsgi.py"], cwd=os.path.join(RAIZ, "backend"), env=entorno,
        stdout=registro, stderr=subprocess.STDOUT,
    )
    url = f"http://127.0.0.1:{args.puerto}"
    try:
        if not esperar_salud(url, 60):
            registro.flush()
            with open(registro.name, encoding="utf-8") as f:
                print(f.read())
            sys.exit("La API local no arrancó")
        print(f"API de integración lista en {url}", flush=True)
        codigo = ejecutar_newman(url)
    finally:
        servidor.terminate()
        try:
            servidor.wait(timeout=10)
        except subprocess.TimeoutExpired:
            servidor.kill()
        registro.close()
        shutil.rmtree(carpeta, ignore_errors=True)
    sys.exit(codigo)


if __name__ == "__main__":
    main()
