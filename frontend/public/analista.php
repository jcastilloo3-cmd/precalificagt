<?php
declare(strict_types=1);
require __DIR__ . '/../includes/bootstrap.php';

exigir_sesion(['ANALISTA', 'ADMIN']);
$filtros = ['EN_REVISION', 'PREAPROBADA', 'RECHAZADA', 'ACEPTADA', 'DECLINADA', 'CANCELADA', 'VENCIDA', 'BORRADOR'];
$estado = (string)($_GET['estado'] ?? 'EN_REVISION');
if (!in_array($estado, $filtros, true)) {
    $estado = 'EN_REVISION';
}
$respuesta = api('GET', '/api/analista/solicitudes?estado=' . urlencode($estado));
$solicitudes = $respuesta['estado'] === 200 ? $respuesta['datos'] : [];
$errorGeneral = $respuesta['estado'] === 200 ? null : errores_de($respuesta)[0];

encabezado('Bandeja de revisión');
?>
<section class="panel">
    <div class="panel__cabecera">
        <h1>Solicitudes: <?= e(texto_estado($estado)) ?></h1>
        <form method="get" class="filtro">
            <label for="estado">Estado</label>
            <select id="estado" name="estado" onchange="this.form.submit()">
                <?php foreach ($filtros as $opcion): ?>
                    <option value="<?= e($opcion) ?>"<?= $opcion === $estado ? ' selected' : '' ?>><?= e(texto_estado($opcion)) ?></option>
                <?php endforeach; ?>
            </select>
            <noscript><button class="boton boton--secundario" type="submit">Filtrar</button></noscript>
        </form>
    </div>
    <?= $errorGeneral ? aviso_error($errorGeneral) : '' ?>
    <?php if ($solicitudes === [] && $errorGeneral === null): ?>
        <p class="vacio">No hay solicitudes en este estado.</p>
    <?php else: ?>
        <div class="tabla-desplazable">
            <table class="tabla">
                <thead>
                <tr><th>N.º</th><th>Solicitante</th><th>DPI</th><th>Producto</th><th class="num">Monto</th><th class="num">Deuda-ingreso</th><th>Central de riesgo</th><th>Regla</th><th></th></tr>
                </thead>
                <tbody>
                <?php foreach ($solicitudes as $solicitud): ?>
                    <tr>
                        <td><?= e($solicitud['id']) ?></td>
                        <td><?= e($solicitud['solicitante_nombre']) ?></td>
                        <td><?= e($solicitud['solicitante_dpi']) ?></td>
                        <td><?= e($solicitud['producto_nombre']) ?></td>
                        <td class="num"><?= e(quetzales($solicitud['monto'])) ?></td>
                        <td class="num"><?= e(porcentaje($solicitud['relacion_deuda_ingreso'])) ?></td>
                        <td><?= e($solicitud['calificacion_buro'] ?? '—') ?></td>
                        <td><?= e($solicitud['regla_aplicada'] ?? '—') ?></td>
                        <td><a href="analista_solicitud.php?id=<?= e($solicitud['id']) ?>">Revisar</a></td>
                    </tr>
                <?php endforeach; ?>
                </tbody>
            </table>
        </div>
    <?php endif; ?>
</section>
<?php pie(); ?>
