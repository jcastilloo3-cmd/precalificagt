<?php
declare(strict_types=1);

function enlaces_navegacion(?array $usuario): array
{
    if ($usuario === null) {
        return ['index.php' => 'Simulador', 'registro.php' => 'Crear cuenta', 'login.php' => 'Iniciar sesión'];
    }
    return match ($usuario['rol']) {
        'ANALISTA' => ['analista.php' => 'Bandeja de revisión', 'reportes.php' => 'Reportes'],
        'ADMIN' => [
            'admin_productos.php' => 'Productos',
            'admin_usuarios.php' => 'Usuarios',
            'analista.php' => 'Solicitudes',
            'reportes.php' => 'Reportes',
        ],
        default => [
            'index.php' => 'Simulador',
            'panel.php' => 'Mis solicitudes',
            'solicitud_nueva.php' => 'Nueva solicitud',
        ],
    };
}

function encabezado(string $titulo): void
{
    $usuario = usuario_actual();
    $actual = basename($_SERVER['SCRIPT_NAME'] ?? '');
    $mensajes = tomar_flash();
    ?>
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title><?= e($titulo) ?> | <?= e(APP_NOMBRE) ?></title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Public+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="assets/styles.css">
</head>
<body>
<a class="saltar" href="#contenido">Ir al contenido</a>
<header class="barra">
    <div class="barra__interior">
        <a class="marca" href="<?= e($usuario ? pagina_inicio($usuario['rol']) : 'index.php') ?>">
            <span class="marca__sello" aria-hidden="true">Q</span>
            <span class="marca__nombre"><?= e(APP_NOMBRE) ?></span>
        </a>
        <nav class="navegacion" aria-label="Principal">
            <?php foreach (enlaces_navegacion($usuario) as $destino => $texto): ?>
                <a href="<?= e($destino) ?>"<?= $destino === $actual ? ' aria-current="page"' : '' ?>><?= e($texto) ?></a>
            <?php endforeach; ?>
            <?php if ($usuario !== null): ?>
                <span class="navegacion__usuario"><?= e($usuario['nombre']) ?></span>
                <a href="salir.php">Cerrar sesión</a>
            <?php endif; ?>
        </nav>
    </div>
</header>
<main id="contenido" class="contenido">
    <?php foreach ($mensajes as $mensaje): ?>
        <div class="aviso aviso--<?= e($mensaje['tipo']) ?>" role="status"><?= e($mensaje['mensaje']) ?></div>
    <?php endforeach; ?>
    <?php
}

function pie(): void
{
    ?>
</main>
<footer class="pie">
    <p><?= e(APP_NOMBRE) ?> es un sistema académico de precalificación. Los resultados son estimaciones y no constituyen una aprobación de crédito.</p>
</footer>
</body>
</html>
    <?php
}

function aviso_error(string $mensaje): string
{
    return '<div class="aviso aviso--error" role="alert">' . e($mensaje) . '</div>';
}
