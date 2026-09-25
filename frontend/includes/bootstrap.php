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
    session_start();
}

require __DIR__ . '/helpers.php';
require __DIR__ . '/api.php';
require __DIR__ . '/layout.php';
