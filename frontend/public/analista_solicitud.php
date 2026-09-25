<?php
declare(strict_types=1);
require __DIR__ . '/../includes/bootstrap.php';

$usuario = exigir_sesion(['ANALISTA', 'ADMIN']);
$id = (int)($_GET['id'] ?? 0);
$errorGeneral = null;
$detalles = [];

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $respuesta = api('POST', '/api/analista/solicitudes/' . $id . '/resolver', [
        'decision' => valor_post('decision'),
        'comentario' => valor_post('comentario'),
    ]);
    if ($respuesta['estado'] === 200) {
        flash('exito', 'Solicitud N.º ' . $id . ' resuelta.');
        redirigir('analista.php');
    }
    [$errorGeneral, $detalles] = errores_de($respuesta);
}

$respuesta = api('GET', '/api/analista/solicitudes/' . $id);
if ($respuesta['estado'] !== 200) {
    flash('error', errores_de($respuesta)[0]);
    redirigir('analista.php');
}
$solicitud = $respuesta['datos'];
$puedeResolver = $usuario['rol'] === 'ANALISTA' && $solicitud['estado'] === 'EN_REVISION';

encabezado('Revisión de solicitud ' . $id);
?>
<section class="panel">
    <div class="panel__cabecera">
        <h1>Solicitud N.º <?= e($id) ?></h1>
        <?= etiqueta_estado($solicitud['estado']) ?>
    </div>
    <?php if ($solicitud['motivo']): ?>
        <p class="resultado resultado--<?= e(clase_estado($solicitud['estado'])) ?>"><?= e($solicitud['motivo']) ?></p>
    <?php endif; ?>
    <div class="columnas">
        <dl class="ficha">
            <div><dt>Solicitante</dt><dd><?= e($solicitud['solicitante_nombre']) ?></dd></div>
            <div><dt>DPI</dt><dd><?= e($solicitud['solicitante_dpi']) ?></dd></div>
            <div><dt>Fecha de nacimiento</dt><dd><?= e($solicitud['solicitante_fecha_nacimiento']) ?></dd></div>
            <div><dt>Tipo de empleo</dt><dd><?= e(texto_tipo_empleo((string)$solicitud['tipo_empleo'])) ?></dd></div>
            <div><dt>Antigüedad laboral</dt><dd><?= e($solicitud['antiguedad_meses']) ?> meses</dd></div>
            <div><dt>Ingreso mensual</dt><dd><?= e(quetzales($solicitud['ingreso_mensual'])) ?></dd></div>
            <div><dt>Otras deudas mensuales</dt><dd><?= e(quetzales($solicitud['deudas_mensuales'])) ?></dd></div>
        </dl>
        <dl class="ficha">
            <div><dt>Producto</dt><dd><?= e($solicitud['producto_nombre']) ?></dd></div>
            <div><dt>Monto</dt><dd><?= e(quetzales($solicitud['monto'])) ?></dd></div>
            <div><dt>Plazo</dt><dd><?= e($solicitud['plazo_meses']) ?> meses</dd></div>
            <div><dt>Cuota estimada</dt><dd><?= $solicitud['cuota_estimada'] === null ? '—' : e(quetzales($solicitud['cuota_estimada'])) ?></dd></div>
            <div><dt>Relación deuda-ingreso</dt><dd><?= e(porcentaje($solicitud['relacion_deuda_ingreso'])) ?></dd></div>
            <div><dt>Central de riesgo</dt><dd><?= e($solicitud['calificacion_buro'] ?? '—') ?></dd></div>
            <div><dt>Regla aplicada</dt><dd><?= e($solicitud['regla_aplicada'] ?? '—') ?></dd></div>
        </dl>
    </div>
</section>

<?php if ($puedeResolver): ?>
<section class="panel">
    <h2>Resolver solicitud</h2>
    <?= $errorGeneral ? aviso_error($errorGeneral) : '' ?>
    <form method="post" class="formulario">
        <fieldset class="opciones">
            <legend>Decisión</legend>
            <label><input type="radio" name="decision" value="PREAPROBAR" required> Preaprobar</label>
            <label><input type="radio" name="decision" value="RECHAZAR"> Rechazar</label>
            <?= error_campo($detalles, 'decision') ?>
        </fieldset>
        <div class="campo">
            <label for="comentario">Comentario de la resolución</label>
            <textarea id="comentario" name="comentario" rows="4" required><?= e(valor_post('comentario')) ?></textarea>
            <p class="campo__ayuda">Mínimo 10 caracteres. El comentario queda en el historial de la solicitud.</p>
            <?= error_campo($detalles, 'comentario') ?>
        </div>
        <button class="boton" type="submit">Guardar resolución</button>
    </form>
</section>
<?php endif; ?>

<section class="panel">
    <h2>Historial</h2>
    <ol class="linea-tiempo">
        <?php foreach ($solicitud['historial'] as $evento): ?>
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
    <p><a class="boton boton--secundario" href="analista.php">Volver a la bandeja</a></p>
</section>
<?php pie(); ?>
