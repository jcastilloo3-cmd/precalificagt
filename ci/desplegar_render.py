"""Etapa 5 del pipeline: despliegue en Render mediante deploy hooks.

Lee RENDER_DEPLOY_HOOKS (credencial de Jenkins: una o varias URL separadas por coma,
API y web del ambiente), dispara el despliegue y espera hasta que /api/health de la
API reporte la versión (commit) que se construyó. Así el pipeline solo termina en
verde cuando el ambiente ya ejecuta el código probado.

Uso: python ci/desplegar_render.py --ambiente QA --api-url https://... --commit <sha>
"""
import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request


def disparar(hook):
    peticion = urllib.request.Request(hook, method="POST", data=b"")
    with urllib.request.urlopen(peticion, timeout=30) as respuesta:
        cuerpo = respuesta.read().decode("utf-8", "replace")
    servicio = hook.split("/deploy/")[-1].split("?")[0]
    print(f"Despliegue solicitado para {servicio}: HTTP {respuesta.status} {cuerpo[:120]}")


def version_actual(api_url):
    try:
        with urllib.request.urlopen(api_url + "/api/health", timeout=30) as respuesta:
            return json.loads(respuesta.read()).get("version")
    except (urllib.error.URLError, OSError, ValueError):
        return None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--ambiente", required=True)
    parser.add_argument("--api-url", required=True)
    parser.add_argument("--commit", required=True)
    parser.add_argument("--minutos", type=int, default=15)
    args = parser.parse_args()

    hooks = [h.strip() for h in os.environ.get("RENDER_DEPLOY_HOOKS", "").split(",") if h.strip()]
    if not hooks:
        sys.exit("Falta la credencial RENDER_DEPLOY_HOOKS")
    api_url = args.api_url.rstrip("/")
    print(f"Ambiente {args.ambiente}: desplegando commit {args.commit[:7]} en {api_url}")
    for hook in hooks:
        disparar(hook)

    limite = time.time() + args.minutos * 60
    while time.time() < limite:
        version = version_actual(api_url)
        print(f"  versión en {args.ambiente}: {version}")
        if version and args.commit.startswith(version[:7]) and version != "local":
            print(f"Despliegue en {args.ambiente} verificado: la API ejecuta {version[:7]}")
            return
        time.sleep(20)
    sys.exit(f"Tiempo agotado: {args.ambiente} no llegó a la versión {args.commit[:7]}")


if __name__ == "__main__":
    main()
