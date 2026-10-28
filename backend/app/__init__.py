"""Fábrica de la aplicación Flask - API de PrecalificaGT."""
import os

from flask import Flask, jsonify

from .config import Config
from .db import close_db, inicializar_bd
from .validaciones import ErrorValidacion


def create_app(config=None):
    app = Flask(__name__)
    app.config.from_object(Config)
    if config:
        app.config.update(config)
    app.json.ensure_ascii = False
    app.json.sort_keys = False

    from .rutas import admin, analista, auth, reportes, simulador, solicitudes

    for modulo in (auth, simulador, solicitudes, analista, admin, reportes):
        app.register_blueprint(modulo.bp)

    app.teardown_appcontext(close_db)

    @app.get("/api/health")
    def salud():
        # version = commit desplegado (Render define RENDER_GIT_COMMIT); el pipeline la
        # compara con el commit construido para confirmar que el despliegue terminó.
        return jsonify(
            estado="ok",
            servicio="precalificagt-api",
            version=os.environ.get("RENDER_GIT_COMMIT", "local"),
        )

    @app.errorhandler(ErrorValidacion)
    def error_validacion(error):
        return jsonify(error="Revise los datos del formulario", detalles=error.detalles), 400

    @app.errorhandler(404)
    def no_encontrado(_error):
        return jsonify(error="Recurso no encontrado"), 404

    @app.errorhandler(500)
    def error_interno(_error):
        # Toda falla inesperada responde en JSON, nunca en HTML (RNF-02, DEF-10)
        return jsonify(error="Error interno del servidor. Intente de nuevo más tarde"), 500

    @app.errorhandler(405)
    def metodo_no_permitido(_error):
        return jsonify(error="Método no permitido"), 405

    inicializar_bd(app)
    return app
