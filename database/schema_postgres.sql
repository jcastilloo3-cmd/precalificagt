-- =====================================================================
-- PrecalificaGT - Sistema de precalificación de créditos
-- Esquema de base de datos para PostgreSQL (ambiente cloud)
-- =====================================================================

CREATE TABLE usuarios (
    id                 SERIAL PRIMARY KEY,
    nombre             VARCHAR(100) NOT NULL,
    dpi                VARCHAR(13) UNIQUE,
    email              VARCHAR(120) NOT NULL UNIQUE,
    telefono           VARCHAR(8),
    fecha_nacimiento   DATE,
    password_hash      VARCHAR(255) NOT NULL,
    rol                VARCHAR(12) NOT NULL DEFAULT 'SOLICITANTE'
                       CHECK (rol IN ('SOLICITANTE', 'ANALISTA', 'ADMIN')),
    estado             VARCHAR(10) NOT NULL DEFAULT 'ACTIVO'
                       CHECK (estado IN ('ACTIVO', 'BLOQUEADO', 'INACTIVO')),
    intentos_fallidos  INTEGER NOT NULL DEFAULT 0,
    bloqueado_hasta    TIMESTAMP,
    creado_en          TIMESTAMP NOT NULL
);

CREATE TABLE productos (
    codigo      VARCHAR(20) PRIMARY KEY,
    nombre      VARCHAR(60) NOT NULL,
    tasa_anual  NUMERIC(5,2) NOT NULL,
    monto_min   NUMERIC(12,2) NOT NULL,
    monto_max   NUMERIC(12,2) NOT NULL,
    plazo_min   INTEGER NOT NULL,
    plazo_max   INTEGER NOT NULL,
    activo      INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE parametros (
    clave        VARCHAR(40) PRIMARY KEY,
    valor        VARCHAR(40) NOT NULL,
    descripcion  VARCHAR(200)
);

-- Central de riesgo simulada (equivalente a la consulta a un buró de crédito).
CREATE TABLE buro_credito (
    dpi             VARCHAR(13) PRIMARY KEY,
    calificacion    CHAR(1) NOT NULL CHECK (calificacion IN ('A', 'B', 'C', 'D', 'E')),
    entidad         VARCHAR(60) NOT NULL,
    actualizado_en  DATE NOT NULL
);

CREATE TABLE solicitudes (
    id                      SERIAL PRIMARY KEY,
    usuario_id              INTEGER NOT NULL REFERENCES usuarios(id),
    producto_codigo         VARCHAR(20) NOT NULL REFERENCES productos(codigo),
    monto                   NUMERIC(12,2) NOT NULL,
    plazo_meses             INTEGER NOT NULL,
    ingreso_mensual         NUMERIC(12,2) NOT NULL,
    deudas_mensuales        NUMERIC(12,2) NOT NULL DEFAULT 0,
    antiguedad_meses        INTEGER NOT NULL,
    tipo_empleo             VARCHAR(15) NOT NULL
                            CHECK (tipo_empleo IN ('ASALARIADO', 'INDEPENDIENTE')),
    tasa_anual              NUMERIC(5,2),
    cuota_estimada          NUMERIC(12,2),
    relacion_deuda_ingreso  NUMERIC(7,2),
    calificacion_buro       VARCHAR(15),
    estado                  VARCHAR(12) NOT NULL DEFAULT 'BORRADOR'
                            CHECK (estado IN ('BORRADOR', 'EN_REVISION', 'PREAPROBADA', 'RECHAZADA',
                                              'ACEPTADA', 'DECLINADA', 'CANCELADA', 'VENCIDA')),
    regla_aplicada          VARCHAR(5),
    motivo                  VARCHAR(250),
    fecha_creacion          TIMESTAMP NOT NULL,
    fecha_evaluacion        TIMESTAMP,
    fecha_vencimiento       TIMESTAMP
);

CREATE TABLE historial_estados (
    id               SERIAL PRIMARY KEY,
    solicitud_id     INTEGER NOT NULL REFERENCES solicitudes(id),
    estado_anterior  VARCHAR(12),
    estado_nuevo     VARCHAR(12) NOT NULL,
    usuario_id       INTEGER REFERENCES usuarios(id),
    comentario       VARCHAR(250),
    fecha            TIMESTAMP NOT NULL
);

CREATE INDEX idx_solicitudes_usuario ON solicitudes(usuario_id);
CREATE INDEX idx_solicitudes_estado ON solicitudes(estado);
CREATE INDEX idx_historial_solicitud ON historial_estados(solicitud_id);
