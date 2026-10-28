<?php
declare(strict_types=1);

/*
 * Arranque de las pruebas unitarias del frontend (PHPUnit).
 * Carga solo las funciones bajo prueba (helpers.php y api.php) sin iniciar la sesión
 * HTTP ni el layout. API_URL apunta a un puerto local cerrado: así api() se prueba
 * sin depender del backend real.
 */
date_default_timezone_set('America/Guatemala');
define('APP_NOMBRE', 'PrecalificaGT');
define('API_URL', 'http://127.0.0.1:9');

$_SESSION = [];

require __DIR__ . '/../includes/helpers.php';
require __DIR__ . '/../includes/api.php';
