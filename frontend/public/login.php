<?php
declare(strict_types=1);
require __DIR__ . '/../includes/bootstrap.php';

if (usuario_actual() !== null) {
    redirigir(pagina_inicio(usuario_actual()['rol']));
}

$errorGeneral = null;

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $respuesta = api('POST', '/api/auth/login', [
        'email' => valor_post('email'),
        'password' => (string)($_POST['password'] ?? ''),
    ]);
    if ($respuesta['estado'] === 200) {
        session_regenerate_id(true);
        $_SESSION['token'] = $respuesta['datos']['token'];
        $_SESSION['usuario'] = $respuesta['datos']['usuario'];
        redirigir(pagina_inicio($respuesta['datos']['usuario']['rol']));
    }
    [$errorGeneral] = errores_de($respuesta);
}

encabezado('Iniciar sesión');
?>
<section class="panel panel--angosto">
    <h1>Iniciar sesión</h1>
    <?= $errorGeneral ? aviso_error($errorGeneral) : '' ?>
    <form method="post" class="formulario">
        <div class="campo">
            <label for="email">Correo electrónico</label>
            <input id="email" name="email" type="email" autocomplete="username" required value="<?= e(valor_post('email')) ?>">
        </div>
        <div class="campo">
            <label for="password">Contraseña</label>
            <input id="password" name="password" type="password" autocomplete="current-password" required>
        </div>
        <button class="boton" type="submit">Iniciar sesión</button>
    </form>
    <p class="nota">¿No tiene cuenta? <a href="registro.php">Cree una</a>.</p>
</section>
<?php pie(); ?>
