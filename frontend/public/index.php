<?php
declare(strict_types=1);
require __DIR__ . '/../includes/bootstrap.php';

$respuestaProductos = api('GET', '/api/productos');
$productos = $respuestaProductos['estado'] === 200 ? $respuestaProductos['datos'] : [];

$entrada = ['producto_codigo' => 'PERSONAL', 'monto' => '50000', 'plazo_meses' => '36'];
$resultado = null;
$errorGeneral = null;
$detalles = [];

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $entrada = [
        'producto_codigo' => valor_post('producto_codigo'),
        'monto' => valor_post('monto'),
        'plazo_meses' => valor_post('plazo_meses'),
    ];
    $respuesta = api('POST', '/api/simulador', $entrada);
    if ($respuesta['estado'] === 200) {
        $resultado = $respuesta['datos'];
    } else {
        [$errorGeneral, $detalles] = errores_de($respuesta);
    }
}

$usuario = usuario_actual();
encabezado('Simulador de crédito');
?>
<section class="intro">
    <h1>Conozca su cuota antes de solicitar</h1>
    <p>Calcule la cuota mensual de un crédito personal, vehicular o hipotecario. Si le conviene, cree su cuenta y obtenga su precalificación en minutos.</p>
</section>

<div class="simulador">
    <form method="post" class="panel formulario">
        <h2>Datos del crédito</h2>
        <?= $errorGeneral ? aviso_error($errorGeneral) : '' ?>
        <div class="campo">
            <label for="producto_codigo">Producto</label>
            <select id="producto_codigo" name="producto_codigo" required>
                <?php foreach ($productos as $producto): ?>
                    <option value="<?= e($producto['codigo']) ?>"<?= $producto['codigo'] === $entrada['producto_codigo'] ? ' selected' : '' ?>><?= e($producto['nombre']) ?></option>
                <?php endforeach; ?>
            </select>
            <?= error_campo($detalles, 'producto_codigo') ?>
        </div>
        <div class="campo">
            <label for="monto">Monto (Q)</label>
            <input id="monto" name="monto" type="number" step="0.01" inputmode="decimal" required value="<?= e($entrada['monto']) ?>">
            <?= error_campo($detalles, 'monto') ?>
        </div>
        <div class="campo">
            <label for="plazo_meses">Plazo (meses)</label>
            <input id="plazo_meses" name="plazo_meses" type="number" step="1" inputmode="numeric" required value="<?= e($entrada['plazo_meses']) ?>">
            <?= error_campo($detalles, 'plazo_meses') ?>
        </div>
        <button class="boton" type="submit">Calcular cuota</button>
    </form>

    <aside class="comprobante" aria-live="polite">
        <?php if ($resultado): ?>
            <p class="comprobante__rotulo">Cuota mensual estimada</p>
            <p class="comprobante__cifra"><?= e(quetzales($resultado['cuota_mensual'])) ?></p>
            <dl class="comprobante__detalle">
                <div><dt>Monto</dt><dd><?= e(quetzales($resultado['monto'])) ?></dd></div>
                <div><dt>Plazo</dt><dd><?= e($resultado['plazo_meses']) ?> meses</dd></div>
                <div><dt>Tasa anual</dt><dd><?= e(porcentaje($resultado['tasa_anual'])) ?></dd></div>
                <div><dt>Total de intereses</dt><dd><?= e(quetzales($resultado['total_intereses'])) ?></dd></div>
                <div class="comprobante__total"><dt>Total a pagar</dt><dd><?= e(quetzales($resultado['total_a_pagar'])) ?></dd></div>
            </dl>
            <?php if ($usuario === null): ?>
                <a class="boton boton--claro" href="registro.php">Crear cuenta para solicitar</a>
            <?php elseif ($usuario['rol'] === 'SOLICITANTE'): ?>
                <a class="boton boton--claro" href="solicitud_nueva.php">Solicitar precalificación</a>
            <?php endif; ?>
        <?php else: ?>
            <p class="comprobante__rotulo">Cuota mensual estimada</p>
            <p class="comprobante__vacio">Complete los datos del crédito y presione «Calcular cuota».</p>
        <?php endif; ?>
    </aside>
</div>

<section class="panel">
    <h2>Condiciones por producto</h2>
    <div class="tabla-desplazable">
        <table class="tabla">
            <thead><tr><th>Producto</th><th class="num">Tasa anual</th><th class="num">Monto mínimo</th><th class="num">Monto máximo</th><th class="num">Plazo</th></tr></thead>
            <tbody>
            <?php foreach ($productos as $producto): ?>
                <tr>
                    <td><?= e($producto['nombre']) ?></td>
                    <td class="num"><?= e(porcentaje($producto['tasa_anual'])) ?></td>
                    <td class="num"><?= e(quetzales($producto['monto_min'])) ?></td>
                    <td class="num"><?= e(quetzales($producto['monto_max'])) ?></td>
                    <td class="num"><?= e($producto['plazo_min']) ?> a <?= e($producto['plazo_max']) ?> meses</td>
                </tr>
            <?php endforeach; ?>
            </tbody>
        </table>
    </div>
</section>
<?php pie(); ?>
