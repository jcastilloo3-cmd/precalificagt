<?php
declare(strict_types=1);
require __DIR__ . '/../includes/bootstrap.php';

exigir_sesion(['ANALISTA', 'ADMIN']);
$respuesta = api('GET', '/api/reportes/resumen');
$resumen = $respuesta['estado'] === 200 ? $respuesta['datos'] : null;
$errorGeneral = $resumen === null ? errores_de($respuesta)[0] : null;
$total = $resumen ? max(1, (int)$resumen['total_solicitudes']) : 1;

encabezado('Reportes');
?>
<section class="panel">
    <h1>Resumen de solicitudes</h1>
    <?= $errorGeneral ? aviso_error($errorGeneral) : '' ?>
    <?php if ($resumen): ?>
        <div class="cifras">
            <p><strong><?= e($resumen['total_solicitudes']) ?></strong> solicitudes registradas</p>
            <p><strong><?= e(quetzales($resumen['monto_preaprobado'])) ?></strong> en créditos preaprobados o aceptados</p>
        </div>
        <h2>Por estado</h2>
        <ul class="barras">
            <?php foreach ($resumen['por_estado'] as $fila): ?>
                <li>
                    <span class="barras__rotulo"><?= e(texto_estado((string)$fila['estado'])) ?></span>
                    <span class="barras__pista"><span class="barras__valor" style="width: <?= e(round($fila['cantidad'] * 100 / $total)) ?>%"></span></span>
                    <span class="barras__numero"><?= e($fila['cantidad']) ?></span>
                </li>
            <?php endforeach; ?>
        </ul>
        <h2>Por producto</h2>
        <div class="tabla-desplazable">
            <table class="tabla">
                <thead><tr><th>Producto</th><th class="num">Solicitudes</th><th class="num">Monto solicitado</th></tr></thead>
                <tbody>
                <?php foreach ($resumen['por_producto'] as $fila): ?>
                    <tr>
                        <td><?= e($fila['producto_codigo']) ?></td>
                        <td class="num"><?= e($fila['cantidad']) ?></td>
                        <td class="num"><?= e(quetzales($fila['monto_total'])) ?></td>
                    </tr>
                <?php endforeach; ?>
                </tbody>
            </table>
        </div>
    <?php endif; ?>
</section>
<?php pie(); ?>
