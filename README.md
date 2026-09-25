# PrecalificaGT — Sistema de precalificación de créditos

Aplicación web cliente-servidor que permite a una persona simular un crédito, registrar una
solicitud y obtener una precalificación automática según la política de crédito de la entidad
(edad, ingreso, calificación en la central de riesgo y relación deuda-ingreso). Los analistas
resuelven las solicitudes que quedan en revisión manual y los administradores gestionan
productos y usuarios.

Proyecto del curso **Aseguramiento de la Calidad de Software** — Universidad Mariano Gálvez de
Guatemala, segundo semestre 2026. Autor: Jorge Otoniel Castillo Ortega (carné 0900-13-719), proyecto individual. Aplicación generada con IA (Claude, Anthropic); ver el anexo
de declaración de uso de IA en la documentación de la Fase 1.

## Arquitectura

| Capa | Tecnología | Carpeta |
|---|---|---|
| Frontend | PHP 8.2 (renderizado en servidor), HTML5, CSS3 | `frontend/` |
| Backend | Python 3.12, Flask 3.1 (API REST JSON), PyJWT, Gunicorn | `backend/` |
| Base de datos | PostgreSQL 16 (nube) / SQLite 3 (desarrollo local) | `database/` |

El navegador solo habla con el frontend PHP; el frontend consume la API REST del backend
mediante HTTP y el token JWT se guarda en la sesión PHP del servidor.

```
precalificagt/
├── backend/            API Flask (app/rutas, app/servicios, validaciones, seguridad)
├── frontend/           Páginas PHP (public/) e includes comunes (includes/)
├── database/           schema_postgres.sql, schema_sqlite.sql, seed.sql
├── docs/               Documentación de la Fase 1
├── docker-compose.yml  Ambiente local completo (PostgreSQL + API + Web)
└── render.yaml         Despliegue en Render (capa gratuita)
```

## Requisitos

- Python 3.12 o superior y `pip`
- PHP 8.1 o superior (con `allow_url_fopen` activo, que es el valor por defecto)
- Opcional: Docker y Docker Compose

## Instalación y ejecución local (sin Docker)

1. Backend (usa SQLite automáticamente y crea la base con datos de ejemplo al arrancar):

   ```bash
   cd backend
   python -m venv .venv
   source .venv/bin/activate          # Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   python wsgi.py                     # API en http://localhost:5000
   ```

   Comprobación: `curl http://localhost:5000/api/health`

2. Frontend (en otra terminal, desde la raíz del repositorio):

   ```bash
   # Linux / macOS
   API_URL=http://localhost:5000 php -S localhost:8080 -t frontend/public
   # Windows (PowerShell)
   $env:API_URL="http://localhost:5000"; php -S localhost:8080 -t frontend/public
   ```

   Abrir http://localhost:8080

Para reiniciar los datos locales basta con borrar `database/precalifica.db` y volver a
arrancar el backend.

## Ejecución con Docker

```bash
docker compose up --build
```

- Web: http://localhost:8080
- API: http://localhost:5000/api/health

## Usuarios de prueba (datos semilla)

| Rol | Correo | Contraseña |
|---|---|---|
| Administrador | admin@precalifica.gt | Admin#2026 |
| Analista de crédito | analista@precalifica.gt | Analista#2026 |
| Solicitante | cliente.demo@correo.com | Cliente#2026 |

La central de riesgo es **simulada** (tabla `buro_credito`). DPI de ejemplo por calificación:
A = `3000000110101`, B = `4000000110101`, C = `5000000110101`, D = `6000000110101`,
E = `7000000110101`. Un DPI que no está en la tabla se evalúa como *sin historial*.

## Configuración (variables de entorno)

| Variable | Servicio | Descripción |
|---|---|---|
| `DATABASE_URL` | API | `postgresql://usuario:clave@host:5432/bd?sslmode=require`. Si no se define se usa SQLite. |
| `SECRET_KEY` | API | Clave para firmar los tokens JWT. |
| `JWT_HORAS` | API | Duración del token en horas (valor actual de la versión 1.0: 8). |
| `PORT` | API y Web | Puerto de escucha (Render lo define automáticamente). |
| `API_URL` | Web | URL pública de la API, por ejemplo `https://precalificagt-api.onrender.com`. |

## Despliegue en la nube (Render, capa gratuita)

1. Crear una base PostgreSQL gratuita en Neon o Supabase y copiar su cadena de conexión.
   (La base PostgreSQL gratuita de Render vence a los 30 días, antes de que termine el ciclo.)
2. En Render: *New → Blueprint* y seleccionar este repositorio (usa `render.yaml`).
3. Asignar `DATABASE_URL` al servicio `precalificagt-api`. Las tablas y los datos semilla se
   crean solos en el primer arranque.
4. Copiar la URL pública de la API y asignarla a `API_URL` en `precalificagt-web`.
5. Verificar `https://<api>/api/health` y abrir la URL del servicio web.

Los servicios gratuitos de Render se suspenden tras 15 minutos sin tráfico; la primera
petición después de la pausa puede tardar cerca de un minuto. Abra la aplicación un par de
minutos antes de una demostración.

## Pruebas

**Línea base: 0 pruebas automatizadas, 0 % de cobertura.** La versión 1.0 no incluye pruebas
unitarias ni de API. Las pruebas de la Fase 1 son manuales/funcionales y se registran en
Azure DevOps Test Plans (ver `docs/`).

En la Fase 2 el equipo agregará:

- Pruebas unitarias con `pytest` y `pytest-cov` (backend) y PHPUnit (frontend):
  `pytest --cov=app` desde `backend/`.
- Colección Postman ejecutada con Newman.
- Análisis estático con SonarCloud y pruebas de carga con k6.

## Pipeline

Pendiente para la Fase 2 (ramas DEV, QA y PROD con GitHub Actions o Azure Pipelines).

## Licencia

MIT. Ver `LICENSE`.
