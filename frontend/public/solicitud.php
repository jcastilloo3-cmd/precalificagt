<?php
declare(strict_types=1);
require __DIR__ . '/../includes/bootstrap.php';

exigir_sesion(['SOLICITANTE']);
$id = (int)($_GET['id'] ?? 0);

const ACCIONES = [
    'enviar' => 'La solicitud fue evaluada.',
    'cancelar' => 'La solicitud fue cancelada.',
    'aceptar' => 'Oferta aceptada. Un asesor le contactará para formalizar el crédito.',
    'declinar' => 'Oferta declinada.',
];

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $accion = valor_post('accion');
    if (array_key_exists($accion, ACCIONES)) {
        $respuesta = api('POST', '/api/solicitudes/' . $id . '/' . $accion, []);
        if ($respuesta['estado'] === 200) {
            flash('exito', ACCIONES[$accion]);
        } else {
            flash('error', errores_de($respuesta)[0]);
        }
    }
    redirigir('solicitud.php?id=' . $id);
}

$respuesta = api('GET', '/api/solicitudes/' . $id);
if ($respuesta['estado'] !== 200) {
    flash('error', errores_de($respuesta)[0]);
    redirigir('panel.php');
}
$solicitud = $respuesta['datos'];
$respuestaHistorial = api('GET', '/api/solicitudes/' . $id . '/historial');
$historial = $respuestaHistorial['estado'] === 200 ? $respuestaHistorial['datos'] : [];
$estado = $solicitud['estado'];

encabezado('Solicitud ' . $id);
?>
<section class="panel">
    <div class="panel__cabecera">
        <h1>Solicitud N.º <?= e($id) ?></h1>
        <?= etiqueta_estado($estado) ?>
    </div>

    <?php if ($solicitud['motivo']): ?>
        <p class="resultado resultado--<?= e(clase_estado($estado)) ?>"><?= e($solicitud['motivo']) ?></p>
    <?php endif; ?>

    <div class="columnas">
        <dl class="ficha">
            <div><dt>Producto</dt><dd><?= e($solicitud['producto_nombre']) ?></dd></div>
            <div><dt>Monto</dt><dd><?= e(quetzales($solicitud['monto'])) ?></dd></div>
            <div><dt>Plazo</dt><dd><?= e($solicitud['plazo_meses']) ?> meses</dd></div>
            <div><dt>Tipo de empleo</dt><dd><?= e(texto_tipo_empleo((string)$solicitud['tipo_empleo'])) ?></dd></div>
            <div><dt>Antigüedad laboral</dt><dd><?= e($solicitud['antiguedad_meses']) ?> meses</dd></div>
            <div><dt>Ingreso mensual</dt><dd><?= e(quetzales($solicitud['ingreso_mensual'])) ?></dd></div>
            <div><dt>Otras deudas mensuales</dt><dd><?= e(quetzales($solicitud['deudas_mensuales'])) ?></dd></div>
        </dl>
        <dl class="ficha">
            <div><dt>Tasa anual</dt><dd><?= e(porcentaje($solicitud['tasa_anual'])) ?></dd></div>
            <div><dt>Cuota estimada</dt><dd><?= $solicitud['cuota_estimada'] === null ? '—' : e(quetzales($solicitud['cuota_estimada'])) ?></dd></div>
            <div><dt>Relación deuda-ingreso</dt><dd><?= e(porcentaje($solicitud['relacion_deuda_ingreso'])) ?></dd></div>
            <div><dt>Calificación en central de riesgo</dt><dd><?= e($solicitud['calificacion_buro'] ?? '—') ?></dd></div>
            <div><dt>Regla aplicada</dt><dd><?= e($solicitud['regla_aplicada'] ?? '—') ?></dd></div>
            <div><dt>Fecha de evaluación</dt><dd><?= e(fecha_corta($solicitud['fecha_evaluacion'])) ?></dd></div>
            <div><dt>Oferta vigente hasta</dt><dd><?= e(fecha_corta($solicitud['fecha_vencimiento'])) ?></dd></div>
        </dl>
    </div>

    <form method="post" class="acciones">
        <?php if ($estado === 'BORRADOR'): ?>
            <button class="boton" name="accion" value="enviar">Enviar a evaluación</button>
        <?php endif; ?>
        <?php if ($estado === 'PREAPROBADA'): ?>
            <button class="boton" name="accion" value="aceptar">Aceptar oferta</button>
            <button class="boton boton--secundario" name="accion" value="declinar">Declinar oferta</button>
        <?php endif; ?>
        <?php if (in_array($estado, ['BORRADOR', 'EN_REVISION'], true)): ?>
            <button class="boton boton--peligro" name="accion" value="cancelar">Cancelar solicitud</button>
        <?php endif; ?>
        <a class="boton boton--secundario" href="panel.php">Volver a mis solicitudes</a>
    </form>
</section>

<section class="panel">
    <h2>Historial de la solicitud</h2>
    <ol class="linea-tiempo">
        <?php foreach ($historial as $evento): ?>
            <li class="linea-tiempo__evento">
                <div class="linea-tiempo__cabecera">
                    <?= etiqueta_estado($evento['estado_nuevo']) ?>
                    <time><?= e(fecha_corta($evento['fecha'])) ?></time>
                </div>
                <p><?= e($evento['comentario'] ?? '') ?></p>
                <p class="nota">Registrado por <?= e($evento['usuario_nombre'] ?? 'Sistema') ?></p>
            </li>
        <?php endforeach; ?>
    </ol>
</section>
<?php pie(); ?>
