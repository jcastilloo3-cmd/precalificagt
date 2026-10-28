## Qué cambia

<!-- Resumen en 2 o 3 líneas. Indique los defectos (DEF-xx) y requerimientos (RF/RNF) relacionados. -->

## Rama de origen → destino

- [ ] `feature/*` o `fix/*` → `DEV`
- [ ] `DEV` → `QA`
- [ ] `QA` → `main`

## Lista de verificación de la revisión

**Correctitud**
- [ ] El cambio cumple el requerimiento y el resultado esperado del defecto en el registro de la Fase 1.
- [ ] Se revisaron los valores límite (por ejemplo 40.00 %, 18 años, 65 años, plazo mínimo y máximo).
- [ ] Las entradas inválidas responden 4xx en JSON, nunca 500 ni HTML (RNF-02).

**Seguridad**
- [ ] La regla de negocio se valida en la API, no solo en la interfaz.
- [ ] Los endpoints nuevos o modificados exigen el rol correcto (RNF-05).
- [ ] No hay secretos, contraseñas ni tokens en el código.

**Pruebas**
- [ ] Cada defecto corregido tiene al menos una prueba de regresión (unitaria o de integración).
- [ ] Las pruebas unitarias aíslan la base de datos y el reloj cuando la unidad depende de ellos.
- [ ] Si cambió el contrato de la API, se actualizó la colección de Postman.

**Pipeline**
- [ ] Jenkins en verde: compilación, pruebas unitarias, quality gate de SonarCloud y Newman.
- [ ] Sin hallazgos nuevos Blocker o Critical en SonarCloud.

## Evidencia

<!-- Enlace al build de Jenkins, al análisis del PR en SonarCloud y capturas si aplica. -->
