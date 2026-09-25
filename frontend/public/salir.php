<?php
declare(strict_types=1);
require __DIR__ . '/../includes/bootstrap.php';

$_SESSION = [];
session_regenerate_id(true);
flash('info', 'Sesión cerrada.');
redirigir('login.php');
