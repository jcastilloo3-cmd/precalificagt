<?php
declare(strict_types=1);
require __DIR__ . '/../includes/bootstrap.php';

exigir_sesion(['SOLICITANTE']);
$respuesta = api('GET', '/api/solicitudes');
$solicitudes = $respuesta['estado'] === 200 ? $respuesta['datos'] : [];
$errorGeneral = $respuesta['estado'] === 200 ? null : errores_de($respuesta)[0];

encabezado('Mis solicitudes');
?>
<section class="panel">
    <div class="panel__cabecera">
        <h1>Mis solicitudes</h1>
        <a class="boton" href="solicitud_nueva.php">Nueva solicitud</a>
    </div>
    <?= $errorGeneral ? aviso_error($errorGeneral) : '' ?>
    <?php if ($solicitudes === [] && $errorGeneral === null): ?>
        <p class="vacio">Aún no tiene solicitudes. Cree la primera para conocer su precalificación.</p>
    <?php else: ?>
        <div class="tabla-desplazable">
            <table class="tabla">
                <thead>
                <tr><th>N.º</th><th>Producto</th><th class="num">Monto</th><th class="num">Plazo</th><th>Estado</th><th>Creada</th><th></th></tr>
                </thead>
                <tbody>
                <?php foreach ($solicitudes as $solicitud): ?>
                    <tr>
                        <td><?= e($solicitud['id']) ?></td>
                        <td><?= e($solicitud['producto_nombre']) ?></td>
                        <td class="num"><?= e(quetzales($solicitud['monto'])) ?></td>
                        <td class="num"><?= e($solicitud['plazo_meses']) ?> meses</td>
                        <td><?= etiqueta_estado($solicitud['estado']) ?></td>
                        <td><?= e(fecha_corta($solicitud['fecha_creacion'])) ?></td>
                        <td><a href="solicitud.php?id=<?= e($solicitud['id']) ?>">Ver detalle</a></td>
                    </tr>
                <?php endforeach; ?>
                </tbody>
            </table>
        </div>
    <?php endif; ?>
</section>
<?php pie(); ?>
