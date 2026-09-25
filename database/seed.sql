-- =====================================================================
-- PrecalificaGT - Datos semilla (compatibles con PostgreSQL y SQLite)
-- Credenciales de demostración:
--   admin@precalifica.gt      / Admin#2026     (ADMIN)
--   analista@precalifica.gt   / Analista#2026  (ANALISTA)
--   cliente.demo@correo.com   / Cliente#2026   (SOLICITANTE, buró A)
-- =====================================================================

-- Productos de crédito
INSERT INTO productos (codigo, nombre, tasa_anual, monto_min, monto_max, plazo_min, plazo_max, activo) VALUES
  ('PERSONAL',    'Crédito personal',     18.00,   2000.00,  150000.00,  6,  60, 1),
  ('VEHICULAR',   'Crédito vehicular',    12.50,  25000.00,  400000.00, 12,  72, 1),
  ('HIPOTECARIO', 'Crédito hipotecario',   8.50, 100000.00, 1500000.00, 60, 300, 1);

-- Parámetros de la política de crédito
INSERT INTO parametros (clave, valor, descripcion) VALUES
  ('EDAD_MIN', '18', 'Edad mínima en años cumplidos'),
  ('EDAD_MAX', '65', 'Edad máxima en años cumplidos al solicitar'),
  ('EDAD_MAX_FIN_PLAZO', '75', 'Edad máxima al finalizar el plazo del crédito'),
  ('INGRESO_MIN', '3500.00', 'Ingreso mensual mínimo en quetzales'),
  ('ANTIGUEDAD_MIN_MESES', '6', 'Antigüedad laboral mínima en meses'),
  ('DTI_PREAPROBACION', '40.00', 'Relación deuda-ingreso máxima (%) para preaprobación automática'),
  ('DTI_MAX_REVISION', '50.00', 'Relación deuda-ingreso máxima (%) para revisión manual'),
  ('VIGENCIA_OFERTA_DIAS', '30', 'Días de vigencia de una oferta preaprobada'),
  ('MAX_INTENTOS_LOGIN', '3', 'Intentos fallidos consecutivos antes del bloqueo'),
  ('BLOQUEO_MINUTOS', '15', 'Minutos de bloqueo temporal de la cuenta');

-- Central de riesgo simulada. DPI = 8 dígitos correlativos + 1 verificador + 2 departamento + 2 municipio
INSERT INTO buro_credito (dpi, calificacion, entidad, actualizado_en) VALUES
  ('3000000110101', 'A', 'Entidad simulada 01', '2026-08-31'),
  ('3000000210101', 'A', 'Entidad simulada 01', '2026-08-31'),
  ('3000000310101', 'A', 'Entidad simulada 01', '2026-08-31'),
  ('3000000410101', 'A', 'Entidad simulada 01', '2026-08-31'),
  ('3000000510101', 'A', 'Entidad simulada 01', '2026-08-31'),
  ('3000000610101', 'A', 'Entidad simulada 01', '2026-08-31'),
  ('3000000710101', 'A', 'Entidad simulada 01', '2026-08-31'),
  ('3000000810101', 'A', 'Entidad simulada 01', '2026-08-31'),
  ('3000000910101', 'A', 'Entidad simulada 01', '2026-08-31'),
  ('3000001010101', 'A', 'Entidad simulada 01', '2026-08-31'),
  ('3000001110101', 'A', 'Entidad simulada 01', '2026-08-31'),
  ('3000001210101', 'A', 'Entidad simulada 01', '2026-08-31'),
  ('3000001310101', 'A', 'Entidad simulada 01', '2026-08-31'),
  ('3000001410101', 'A', 'Entidad simulada 01', '2026-08-31'),
  ('3000001510101', 'A', 'Entidad simulada 01', '2026-08-31'),
  ('3000001610101', 'A', 'Entidad simulada 01', '2026-08-31'),
  ('3000001710101', 'A', 'Entidad simulada 01', '2026-08-31'),
  ('3000001810101', 'A', 'Entidad simulada 01', '2026-08-31'),
  ('3000001910101', 'A', 'Entidad simulada 01', '2026-08-31'),
  ('3000002010101', 'A', 'Entidad simulada 01', '2026-08-31'),
  ('3000002110101', 'A', 'Entidad simulada 01', '2026-08-31'),
  ('3000002210101', 'A', 'Entidad simulada 01', '2026-08-31'),
  ('3000002310101', 'A', 'Entidad simulada 01', '2026-08-31'),
  ('3000002410101', 'A', 'Entidad simulada 01', '2026-08-31'),
  ('3000002510101', 'A', 'Entidad simulada 01', '2026-08-31'),
  ('3000002610101', 'A', 'Entidad simulada 01', '2026-08-31'),
  ('3000002710101', 'A', 'Entidad simulada 01', '2026-08-31'),
  ('3000002810101', 'A', 'Entidad simulada 01', '2026-08-31'),
  ('3000002910101', 'A', 'Entidad simulada 01', '2026-08-31'),
  ('3000003010101', 'A', 'Entidad simulada 01', '2026-08-31'),
  ('3000003110101', 'A', 'Entidad simulada 01', '2026-08-31'),
  ('3000003210101', 'A', 'Entidad simulada 01', '2026-08-31'),
  ('3000003310101', 'A', 'Entidad simulada 01', '2026-08-31'),
  ('3000003410101', 'A', 'Entidad simulada 01', '2026-08-31'),
  ('3000003510101', 'A', 'Entidad simulada 01', '2026-08-31'),
  ('3000003610101', 'A', 'Entidad simulada 01', '2026-08-31'),
  ('3000003710101', 'A', 'Entidad simulada 01', '2026-08-31'),
  ('3000003810101', 'A', 'Entidad simulada 01', '2026-08-31'),
  ('3000003910101', 'A', 'Entidad simulada 01', '2026-08-31'),
  ('3000004010101', 'A', 'Entidad simulada 01', '2026-08-31'),
  ('4000000110101', 'B', 'Entidad simulada 02', '2026-08-31'),
  ('4000000210101', 'B', 'Entidad simulada 02', '2026-08-31'),
  ('4000000310101', 'B', 'Entidad simulada 02', '2026-08-31'),
  ('4000000410101', 'B', 'Entidad simulada 02', '2026-08-31'),
  ('4000000510101', 'B', 'Entidad simulada 02', '2026-08-31'),
  ('4000000610101', 'B', 'Entidad simulada 02', '2026-08-31'),
  ('4000000710101', 'B', 'Entidad simulada 02', '2026-08-31'),
  ('4000000810101', 'B', 'Entidad simulada 02', '2026-08-31'),
  ('4000000910101', 'B', 'Entidad simulada 02', '2026-08-31'),
  ('4000001010101', 'B', 'Entidad simulada 02', '2026-08-31'),
  ('5000000110101', 'C', 'Entidad simulada 03', '2026-08-31'),
  ('5000000210101', 'C', 'Entidad simulada 03', '2026-08-31'),
  ('5000000310101', 'C', 'Entidad simulada 03', '2026-08-31'),
  ('5000000410101', 'C', 'Entidad simulada 03', '2026-08-31'),
  ('5000000510101', 'C', 'Entidad simulada 03', '2026-08-31'),
  ('6000000110101', 'D', 'Entidad simulada 04', '2026-08-31'),
  ('6000000210101', 'D', 'Entidad simulada 04', '2026-08-31'),
  ('6000000310101', 'D', 'Entidad simulada 04', '2026-08-31'),
  ('6000000410101', 'D', 'Entidad simulada 04', '2026-08-31'),
  ('6000000510101', 'D', 'Entidad simulada 04', '2026-08-31'),
  ('7000000110101', 'E', 'Entidad simulada 05', '2026-08-31'),
  ('7000000210101', 'E', 'Entidad simulada 05', '2026-08-31'),
  ('7000000310101', 'E', 'Entidad simulada 05', '2026-08-31'),
  ('7000000410101', 'E', 'Entidad simulada 05', '2026-08-31'),
  ('7000000510101', 'E', 'Entidad simulada 05', '2026-08-31');

-- Usuarios de demostración
INSERT INTO usuarios (nombre, dpi, email, telefono, fecha_nacimiento, password_hash, rol, estado, intentos_fallidos, creado_en) VALUES
  ('Administrador del sistema', NULL, 'admin@precalifica.gt', '22223333', NULL, 'scrypt:32768:8:1$C0LL5AyGxU4Q2lid$16ec795404262dfff0df195db4f6d4d65db7cffd7f7e61183d4205c0b1aabadb2d8a4bc3facadcd09edca724e3ab920b8bcd0e8842549e75b9046244fd680b73', 'ADMIN', 'ACTIVO', 0, '2026-09-01 08:00:00'),
  ('Analista de crédito', NULL, 'analista@precalifica.gt', '22224444', NULL, 'scrypt:32768:8:1$pWnuzWJrIts7v0HQ$f8e502da7120cbc5b594e3ac3e917cd584ebff4b334d02f2d58343c3c7d867df611bf8abc26c165aa57783489d4ce150623a8ce70662bfcb01f4d07536125873', 'ANALISTA', 'ACTIVO', 0, '2026-09-01 08:00:00'),
  ('Cliente Demostración', '3000000110101', 'cliente.demo@correo.com', '55556666', '1990-05-15', 'scrypt:32768:8:1$TcPbU9etu6rphv7U$034e41dbd63658103993047cc3b74abcbabc3619d2a8f3b26a8d7aea89992fd41996a249dbfd03f1dbdd08702eb049b958a83a9e024e64d5e6f2084d2a228371', 'SOLICITANTE', 'ACTIVO', 0, '2026-09-01 08:00:00');
