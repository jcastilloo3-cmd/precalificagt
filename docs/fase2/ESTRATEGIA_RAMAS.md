# Estrategia de ramas y control de cambios (E9)

PrecalificaGT usa tres ramas permanentes, una por ambiente, y ramas de trabajo de vida corta.

| Rama | Ambiente | Quién escribe | Despliegue |
|---|---|---|---|
| `DEV` | Integración | Solo merge de PR desde `feature/*` o `fix/*` | Ambiente efímero en Jenkins (API + SQLite) donde corren las pruebas de API |
| `QA` | Pruebas | Solo merge de PR desde `DEV` | Render: `precalificagt-api-qa` y `precalificagt-web-qa` (Neon, rama `qa`), creados desde el panel con Branch = QA y Auto-Deploy = Off |
| `main` | Producción (PROD) | Solo merge de PR desde `QA` | Render: `precalificagt-api` y `precalificagt-web` (Neon, rama principal) |

Ramas de trabajo: `feature/<tema>` para funcionalidad o infraestructura y `fix/<módulo>-<tema>` para correcciones (por ejemplo `fix/aut-val-adm-seguridad`). Nacen de `DEV` y se eliminan después del merge.

## Política de promoción

1. Todo cambio entra a `DEV` por Pull Request. No se permite push directo a `DEV`, `QA` ni `main`.
2. Cada PR debe:
   - pasar el pipeline completo de Jenkins (`continuous-integration/jenkins/pr-merge`): compilación, pruebas unitarias con la meta de cobertura, análisis de SonarCloud con quality gate aprobado y pruebas de API con Newman;
   - tener una revisión escrita con la lista de verificación de la plantilla de PR (`.github/pull_request_template.md`) y comentarios sobre líneas concretas del diff;
   - tener todas las conversaciones resueltas.
3. `DEV → QA`: cuando `DEV` está en verde y contiene un conjunto de cambios listo para probar. Al hacer merge, Jenkins construye `QA`, despliega en Render QA y ejecuta la colección de Postman contra QA desplegado (prueba de humo).
4. `QA → main`: cuando QA desplegado pasó la prueba de humo y la revisión. Al hacer merge, Jenkins construye `main` y despliega en PROD. Render tiene el despliegue automático apagado (`autoDeploy: false`): **solo** el pipeline despliega.
5. Corrección urgente en producción (hotfix): rama `fix/*` desde `main`, PR a `main` con el mismo pipeline, y luego PR de `main` a `QA` y a `DEV` para no perder el cambio.

## Bloqueo del merge si el pipeline falla

En GitHub → Settings → Branches se configura una regla para `DEV`, `QA` y `main`:

- Require a pull request before merging.
- Require status checks to pass before merging → `continuous-integration/jenkins/pr-merge`.
- Require conversation resolution before merging.
- Do not allow bypassing the above settings (aplica también al administrador del repositorio).

Jenkins (Multibranch Pipeline con GitHub Branch Source) publica el estado de cada build en el PR. Si cualquier etapa falla, el estado es rojo y GitHub deshabilita el botón de merge.

## Revisión de código en un proyecto individual

El enunciado pide revisión de otro integrante. Como el proyecto es individual (sección 1.3 de la Fase 1), el autor hace una revisión diferida y documentada: deja pasar al menos unas horas entre el último commit y la revisión, recorre la lista de verificación de la plantilla, comenta las líneas del diff con hallazgos concretos (riesgos, casos límite, pruebas faltantes) y corrige en nuevos commits antes de aprobar. GitHub no permite aprobar un PR propio, por eso la regla no exige aprobaciones: el control efectivo es el pipeline en verde más la revisión escrita.
