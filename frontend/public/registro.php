<?php
declare(strict_types=1);
require __DIR__ . '/../includes/bootstrap.php';

if (usuario_actual() !== null) {
    redirigir(pagina_inicio(usuario_actual()['rol']));
}

$errorGeneral = null;
$detalles = [];

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $respuesta = api('POST', '/api/auth/registro', [
        'nombre' => valor_post('nombre'),
        'dpi' => valor_post('dpi'),
        'email' => valor_post('email'),
        'telefono' => valor_post('telefono'),
        'fecha_nacimiento' => valor_post('fecha_nacimiento'),
        'password' => (string)($_POST['password'] ?? ''),
    ]);
    if ($respuesta['estado'] === 201) {
        flash('exito', 'Cuenta creada. Inicie sesión con su correo y contraseña.');
        redirigir('login.php');
    }
    [$errorGeneral, $detalles] = errores_de($respuesta);
}

encabezado('Crear cuenta');
?>
<section class="panel panel--angosto">
    <h1>Crear cuenta</h1>
    <p class="nota">Necesita una cuenta para enviar solicitudes de precalificación.</p>
    <?= $errorGeneral ? aviso_error($errorGeneral) : '' ?>
    <form method="post" class="formulario">
        <div class="campo">
            <label for="nombre">Nombre completo</label>
            <input id="nombre" name="nombre" type="text" autocomplete="name" required value="<?= e(valor_post('nombre')) ?>">
            <?= error_campo($detalles, 'nombre') ?>
        </div>
        <div class="campo">
            <label for="dpi">DPI (13 dígitos)</label>
            <input id="dpi" name="dpi" type="text" inputmode="numeric" required value="<?= e(valor_post('dpi')) ?>">
            <?= error_campo($detalles, 'dpi') ?>
        </div>
        <div class="campo">
            <label for="email">Correo electrónico</label>
            <input id="email" name="email" type="email" autocomplete="email" required value="<?= e(valor_post('email')) ?>">
            <?= error_campo($detalles, 'email') ?>
        </div>
        <div class="campo">
            <label for="telefono">Teléfono (8 dígitos)</label>
            <input id="telefono" name="telefono" type="tel" inputmode="numeric" required value="<?= e(valor_post('telefono')) ?>">
            <?= error_campo($detalles, 'telefono') ?>
        </div>
        <div class="campo">
            <label for="fecha_nacimiento">Fecha de nacimiento</label>
            <input id="fecha_nacimiento" name="fecha_nacimiento" type="date" required value="<?= e(valor_post('fecha_nacimiento')) ?>">
            <?= error_campo($detalles, 'fecha_nacimiento') ?>
        </div>
        <div class="campo">
            <label for="password">Contraseña</label>
            <input id="password" name="password" type="password" autocomplete="new-password" required>
            <p class="campo__ayuda">Mínimo 8 caracteres, con al menos una mayúscula y un número.</p>
            <?= error_campo($detalles, 'password') ?>
        </div>
        <button class="boton" type="submit">Crear cuenta</button>
    </form>
    <p class="nota">¿Ya tiene cuenta? <a href="login.php">Inicie sesión</a>.</p>
</section>
<?php pie(); ?>
