# Cambio de demostración (E15)

Este archivo se agregó durante la grabación del video de defensa para mostrar el flujo completo en vivo:

1. Pull Request desde una rama de trabajo hacia `DEV`, con el check de Jenkins obligatorio.
2. Promoción `DEV → QA` mediante Pull Request.
3. Al hacer merge en `QA`, Jenkins ejecuta las 5 etapas (compilación, pruebas unitarias, SonarCloud con quality gate, Newman y despliegue) y verifica en `/api/health` que Render QA ejecuta el commit nuevo.

No modifica código de la aplicación.
