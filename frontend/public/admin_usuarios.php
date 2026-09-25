<?php
declare(strict_types=1);
require __DIR__ . '/../includes/bootstrap.php';

$actual = exigir_sesion(['ADMIN']);
$acciones = ['desbloquear' => 'desbloqueado', 'desactivar' => 'desactivado', 'activar' => 'activado'];

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $accion = valor_post('accion');
    $idUsuario = (int)valor_post('id');
    if (array_key_exists($accion, $acciones)) {
        $respuesta = api('POST', '/api/admin/usuarios/' . $idUsuario . '/' . $accion, []);
        if ($respuesta['estado'] === 200) {
            flash('exito', 'Usuario ' . $acciones[$accion] . '.');
        } else {
            flash('error', errores_de($respuesta)[0]);
        }
    }
    redirigir('admin_usuarios.php');
}

$respuesta = api('GET', '/api/admin/usuarios');
$usuarios = $respuesta['estado'] === 200 ? $respuesta['datos'] : [];
$roles = ['SOLICITANTE' => 'Solicitante', 'ANALISTA' => 'Analista', 'ADMIN' => 'Administrador'];
$estados = ['ACTIVO' => 'Activo', 'BLOQUEADO' => 'Bloqueado', 'INACTIVO' => 'Inactivo'];

encabezado('Usuarios');
?>
<section class="panel">
    <h1>Usuarios</h1>
    <div class="tabla-desplazable">
        <table class="tabla">
            <thead>
            <tr><th>Nombre</th><th>Correo</th><th>Rol</th><th>Estado</th><th class="num">Intentos fallidos</th><th>Bloqueado hasta</th><th>Acciones</th></tr>
            </thead>
            <tbody>
            <?php foreach ($usuarios as $fila): ?>
                <tr>
                    <td><?= e($fila['nombre']) ?></td>
                    <td><?= e($fila['email']) ?></td>
                    <td><?= e($roles[$fila['rol']] ?? $fila['rol']) ?></td>
                    <td><span class="cuenta cuenta--<?= e(strtolower((string)$fila['estado'])) ?>"><?= e($estados[$fila['estado']] ?? $fila['estado']) ?></span></td>
                    <td class="num"><?= e($fila['intentos_fallidos']) ?></td>
                    <td><?= e(fecha_corta($fila['bloqueado_hasta'])) ?></td>
                    <td>
                        <form method="post" class="acciones acciones--tabla">
                            <input type="hidden" name="id" value="<?= e($fila['id']) ?>">
                            <?php if ($fila['estado'] === 'BLOQUEADO'): ?>
                                <button class="boton boton--mini" name="accion" value="desbloquear">Desbloquear</button>
                            <?php endif; ?>
                            <?php if ($fila['estado'] === 'ACTIVO' && (int)$fila['id'] !== (int)$actual['id']): ?>
                                <button class="boton boton--mini boton--peligro" name="accion" value="desactivar">Desactivar</button>
                            <?php endif; ?>
                            <?php if ($fila['estado'] === 'INACTIVO'): ?>
                                <button class="boton boton--mini" name="accion" value="activar">Activar</button>
                            <?php endif; ?>
                        </form>
                    </td>
                </tr>
            <?php endforeach; ?>
            </tbody>
        </table>
    </div>
</section>
<?php pie(); ?>
