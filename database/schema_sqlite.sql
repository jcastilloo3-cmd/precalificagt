-- =====================================================================
-- PrecalificaGT - Sistema de precalificación de créditos
-- Esquema de base de datos para SQLite (desarrollo local y pruebas)
-- =====================================================================

CREATE TABLE usuarios (
    id                 INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre             TEXT NOT NULL,
    dpi                TEXT UNIQUE,
    email              TEXT NOT NULL UNIQUE,
    telefono           TEXT,
    fecha_nacimiento   TEXT,
    password_hash      TEXT NOT NULL,
    rol                TEXT NOT NULL DEFAULT 'SOLICITANTE'
                       CHECK (rol IN ('SOLICITANTE', 'ANALISTA', 'ADMIN')),
    estado             TEXT NOT NULL DEFAULT 'ACTIVO'
                       CHECK (estado IN ('ACTIVO', 'BLOQUEADO', 'INACTIVO')),
    intentos_fallidos  INTEGER NOT NULL DEFAULT 0,
    bloqueado_hasta    TEXT,
    creado_en          TEXT NOT NULL
);

CREATE TABLE productos (
    codigo      TEXT PRIMARY KEY,
    nombre      TEXT NOT NULL,
    tasa_anual  REAL NOT NULL,
    monto_min   REAL NOT NULL,
    monto_max   REAL NOT NULL,
    plazo_min   INTEGER NOT NULL,
    plazo_max   INTEGER NOT NULL,
    activo      INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE parametros (
    clave        TEXT PRIMARY KEY,
    valor        TEXT NOT NULL,
    descripcion  TEXT
);

-- Central de riesgo simulada (equivalente a la consulta a un buró de crédito).
CREATE TABLE buro_credito (
    dpi             TEXT PRIMARY KEY,
    calificacion    TEXT NOT NULL CHECK (calificacion IN ('A', 'B', 'C', 'D', 'E')),
    entidad         TEXT NOT NULL,
    actualizado_en  TEXT NOT NULL
);

CREATE TABLE solicitudes (
    id                      INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id              INTEGER NOT NULL REFERENCES usuarios(id),
    producto_codigo         TEXT NOT NULL REFERENCES productos(codigo),
    monto                   REAL NOT NULL,
    plazo_meses             INTEGER NOT NULL,
    ingreso_mensual         REAL NOT NULL,
    deudas_mensuales        REAL NOT NULL DEFAULT 0,
    antiguedad_meses        INTEGER NOT NULL,
    tipo_empleo             TEXT NOT NULL
                            CHECK (tipo_empleo IN ('ASALARIADO', 'INDEPENDIENTE')),
    tasa_anual              REAL,
    cuota_estimada          REAL,
    relacion_deuda_ingreso  REAL,
    calificacion_buro       TEXT,
    estado                  TEXT NOT NULL DEFAULT 'BORRADOR'
                            CHECK (estado IN ('BORRADOR', 'EN_REVISION', 'PREAPROBADA', 'RECHAZADA',
                                              'ACEPTADA', 'DECLINADA', 'CANCELADA', 'VENCIDA')),
    regla_aplicada          TEXT,
    motivo                  TEXT,
    fecha_creacion          TEXT NOT NULL,
    fecha_evaluacion        TEXT,
    fecha_vencimiento       TEXT
);

CREATE TABLE historial_estados (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    solicitud_id     INTEGER NOT NULL REFERENCES solicitudes(id),
    estado_anterior  TEXT,
    estado_nuevo     TEXT NOT NULL,
    usuario_id       INTEGER REFERENCES usuarios(id),
    comentario       TEXT,
    fecha            TEXT NOT NULL
);

CREATE INDEX idx_solicitudes_usuario ON solicitudes(usuario_id);
CREATE INDEX idx_solicitudes_estado ON solicitudes(estado);
CREATE INDEX idx_historial_solicitud ON historial_estados(solicitud_id);
