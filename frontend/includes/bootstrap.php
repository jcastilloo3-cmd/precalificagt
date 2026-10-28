<?php
declare(strict_types=1);

/*
 * Arranque común de todas las páginas del frontend.
 * API_URL apunta al backend Python (por ejemplo https://precalificagt-api.onrender.com).
 */
define('APP_NOMBRE', 'PrecalificaGT');
date_default_timezone_set('America/Guatemala');
define('API_URL', rtrim((string)(getenv('API_URL') ?: ($_SERVER['API_URL'] ?? 'http://localhost:5000')), '/'));

if (session_status() !== PHP_SESSION_ACTIVE) {
    // Cookie de sesión inaccesible desde JavaScript y no enviada en peticiones de otros sitios
    $https = ($_SERVER['HTTPS'] ?? '') === 'on' || ($_SERVER['HTTP_X_FORWARDED_PROTO'] ?? '') === 'https';
    session_set_cookie_params(['httponly' => true, 'samesite' => 'Lax', 'secure' => $https]);
    session_start();
}

require __DIR__ . '/helpers.php';
require __DIR__ . '/api.php';
require __DIR__ . '/layout.php';

// Todo POST debe traer el token CSRF de la sesión; si no, no se procesa
if (($_SERVER['REQUEST_METHOD'] ?? 'GET') === 'POST' && !csrf_valido($_POST[CAMPO_CSRF] ?? null)) {
    http_response_code(400);
    encabezado('Solicitud no válida');
    echo '<section class="panel"><h1>Solicitud no válida</h1>'
        . '<p>El formulario expiró o no proviene de PrecalificaGT. Vuelva a la página e inténtelo de nuevo.</p>'
        . '<p><a class="boton" href="index.php">Ir al inicio</a></p></section>';
    pie();
    exit;
}
