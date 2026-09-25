<?php
declare(strict_types=1);
require __DIR__ . '/../includes/bootstrap.php';

exigir_sesion(['ADMIN']);

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $codigo = valor_post('codigo');
    $respuesta = api('PUT', '/api/admin/productos/' . rawurlencode($codigo), [
        'tasa_anual' => valor_post('tasa_anual'),
        'monto_min' => valor_post('monto_min'),
        'monto_max' => valor_post('monto_max'),
        'plazo_min' => valor_post('plazo_min'),
        'plazo_max' => valor_post('plazo_max'),
    ]);
    if ($respuesta['estado'] === 200) {
        flash('exito', 'Producto ' . $codigo . ' actualizado.');
    } else {
        [$general, $detalles] = errores_de($respuesta);
        flash('error', trim($general . ' ' . implode(' ', array_map('strval', $detalles))));
    }
    redirigir('admin_productos.php');
}

$respuesta = api('GET', '/api/admin/productos');
$productos = $respuesta['estado'] === 200 ? $respuesta['datos'] : [];

encabezado('Productos de crédito');
?>
<section class="panel">
    <h1>Productos de crédito</h1>
    <p class="nota">Los cambios aplican a las simulaciones y solicitudes nuevas.</p>
    <?php foreach ($productos as $producto): ?>
        <form method="post" class="producto">
            <input type="hidden" name="codigo" value="<?= e($producto['codigo']) ?>">
            <h2><?= e($producto['nombre']) ?></h2>
            <div class="producto__campos">
                <div class="campo">
                    <label for="tasa-<?= e($producto['codigo']) ?>">Tasa anual (%)</label>
                    <input id="tasa-<?= e($producto['codigo']) ?>" name="tasa_anual" type="number" step="0.01" required value="<?= e($producto['tasa_anual']) ?>">
                </div>
                <div class="campo">
                    <label for="mmin-<?= e($producto['codigo']) ?>">Monto mínimo (Q)</label>
                    <input id="mmin-<?= e($producto['codigo']) ?>" name="monto_min" type="number" step="0.01" required value="<?= e($producto['monto_min']) ?>">
                </div>
                <div class="campo">
                    <label for="mmax-<?= e($producto['codigo']) ?>">Monto máximo (Q)</label>
                    <input id="mmax-<?= e($producto['codigo']) ?>" name="monto_max" type="number" step="0.01" required value="<?= e($producto['monto_max']) ?>">
                </div>
                <div class="campo">
                    <label for="pmin-<?= e($producto['codigo']) ?>">Plazo mínimo (meses)</label>
                    <input id="pmin-<?= e($producto['codigo']) ?>" name="plazo_min" type="number" step="1" required value="<?= e($producto['plazo_min']) ?>">
                </div>
                <div class="campo">
                    <label for="pmax-<?= e($producto['codigo']) ?>">Plazo máximo (meses)</label>
                    <input id="pmax-<?= e($producto['codigo']) ?>" name="plazo_max" type="number" step="1" required value="<?= e($producto['plazo_max']) ?>">
                </div>
            </div>
            <button class="boton" type="submit">Guardar cambios</button>
        </form>
    <?php endforeach; ?>
</section>
<?php pie(); ?>
