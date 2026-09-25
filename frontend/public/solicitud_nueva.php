<?php
declare(strict_types=1);
require __DIR__ . '/../includes/bootstrap.php';

exigir_sesion(['SOLICITANTE']);
$respuestaProductos = api('GET', '/api/productos');
$productos = $respuestaProductos['estado'] === 200 ? $respuestaProductos['datos'] : [];

$errorGeneral = null;
$detalles = [];

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $respuesta = api('POST', '/api/solicitudes', [
        'producto_codigo' => valor_post('producto_codigo'),
        'monto' => valor_post('monto'),
        'plazo_meses' => valor_post('plazo_meses'),
        'ingreso_mensual' => valor_post('ingreso_mensual'),
        'deudas_mensuales' => valor_post('deudas_mensuales', '0'),
        'antiguedad_meses' => valor_post('antiguedad_meses'),
        'tipo_empleo' => valor_post('tipo_empleo', 'ASALARIADO'),
    ]);
    if ($respuesta['estado'] === 201) {
        flash('exito', 'Solicitud guardada como borrador. Revise los datos y envíela a evaluación.');
        redirigir('solicitud.php?id=' . (int)$respuesta['datos']['id']);
    }
    [$errorGeneral, $detalles] = errores_de($respuesta);
}

$seleccionado = valor_post('producto_codigo', 'PERSONAL');
$tipoSeleccionado = valor_post('tipo_empleo', 'ASALARIADO');
encabezado('Nueva solicitud');
?>
<section class="panel">
    <h1>Nueva solicitud de precalificación</h1>
    <p class="nota">La solicitud se guarda como borrador. La evaluación se realiza cuando usted la envía.</p>
    <?= $errorGeneral ? aviso_error($errorGeneral) : '' ?>
    <form method="post" class="formulario formulario--columnas">
        <fieldset>
            <legend>Crédito solicitado</legend>
            <div class="campo">
                <label for="producto_codigo">Producto</label>
                <select id="producto_codigo" name="producto_codigo" required>
                    <?php foreach ($productos as $producto): ?>
                        <option value="<?= e($producto['codigo']) ?>"<?= $producto['codigo'] === $seleccionado ? ' selected' : '' ?>>
                            <?= e($producto['nombre']) ?> (<?= e(quetzales($producto['monto_min'])) ?> a <?= e(quetzales($producto['monto_max'])) ?>, <?= e($producto['plazo_min']) ?> a <?= e($producto['plazo_max']) ?> meses)
                        </option>
                    <?php endforeach; ?>
                </select>
                <?= error_campo($detalles, 'producto_codigo') ?>
            </div>
            <div class="campo">
                <label for="monto">Monto (Q)</label>
                <input id="monto" name="monto" type="number" step="0.01" required value="<?= e(valor_post('monto')) ?>">
                <?= error_campo($detalles, 'monto') ?>
            </div>
            <div class="campo">
                <label for="plazo_meses">Plazo (meses)</label>
                <input id="plazo_meses" name="plazo_meses" type="number" step="1" required value="<?= e(valor_post('plazo_meses')) ?>">
                <?= error_campo($detalles, 'plazo_meses') ?>
            </div>
        </fieldset>
        <fieldset>
            <legend>Situación laboral y financiera</legend>
            <div class="campo">
                <label for="tipo_empleo">Tipo de empleo</label>
                <select id="tipo_empleo" name="tipo_empleo" required>
                    <?php foreach (TIPOS_EMPLEO as $valor => $texto): ?>
                        <option value="<?= e($valor) ?>"<?= $valor === $tipoSeleccionado ? ' selected' : '' ?>><?= e($texto) ?></option>
                    <?php endforeach; ?>
                </select>
                <?= error_campo($detalles, 'tipo_empleo') ?>
            </div>
            <div class="campo">
                <label for="antiguedad_meses">Antigüedad laboral (meses)</label>
                <input id="antiguedad_meses" name="antiguedad_meses" type="number" step="1" required value="<?= e(valor_post('antiguedad_meses')) ?>">
                <?= error_campo($detalles, 'antiguedad_meses') ?>
            </div>
            <div class="campo">
                <label for="ingreso_mensual">Ingreso mensual (Q)</label>
                <input id="ingreso_mensual" name="ingreso_mensual" type="number" step="0.01" required value="<?= e(valor_post('ingreso_mensual')) ?>">
                <?= error_campo($detalles, 'ingreso_mensual') ?>
            </div>
            <div class="campo">
                <label for="deudas_mensuales">Pago mensual de otras deudas (Q)</label>
                <input id="deudas_mensuales" name="deudas_mensuales" type="number" step="0.01" required value="<?= e(valor_post('deudas_mensuales', '0')) ?>">
                <?= error_campo($detalles, 'deudas_mensuales') ?>
            </div>
        </fieldset>
        <div class="formulario__acciones">
            <button class="boton" type="submit">Guardar borrador</button>
            <a class="boton boton--secundario" href="panel.php">Volver</a>
        </div>
    </form>
</section>
<?php pie(); ?>
