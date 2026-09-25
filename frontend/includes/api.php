<?php
declare(strict_types=1);

/**
 * Cliente HTTP hacia la API REST del backend.
 * Devuelve ['estado' => código HTTP, 'datos' => arreglo decodificado del JSON].
 */
function api(string $metodo, string $ruta, ?array $cuerpo = null): array
{
    $cabeceras = ['Accept: application/json'];
    if (!empty($_SESSION['token'])) {
        $cabeceras[] = 'Authorization: Bearer ' . $_SESSION['token'];
    }

    $http = [
        'method' => $metodo,
        'ignore_errors' => true,
        'timeout' => 70,
    ];
    if ($cuerpo !== null) {
        $cabeceras[] = 'Content-Type: application/json';
        $http['content'] = json_encode($cuerpo, JSON_UNESCAPED_UNICODE);
    }
    $http['header'] = implode("\r\n", $cabeceras);

    $respuesta = @file_get_contents(API_URL . $ruta, false, stream_context_create(['http' => $http]));

    $estado = 0;
    if (isset($http_response_header[0])
        && preg_match('#^HTTP/\S+\s+(\d{3})#', $http_response_header[0], $coincidencia) === 1) {
        $estado = (int)$coincidencia[1];
    }

    if ($respuesta === false) {
        return [
            'estado' => 0,
            'datos' => ['error' => 'No fue posible conectar con el servicio de crédito. Intente de nuevo en unos segundos.'],
        ];
    }

    $datos = json_decode($respuesta, true);
    if (!is_array($datos)) {
        $datos = ['error' => 'El servicio respondió con un error inesperado (HTTP ' . $estado . ').'];
    }

    if ($estado === 401 && !empty($_SESSION['token'])) {
        $_SESSION = [];
        flash('info', 'Su sesión expiró. Inicie sesión de nuevo.');
        redirigir('login.php');
    }

    return ['estado' => $estado, 'datos' => $datos];
}

/** Mensajes de error de una respuesta: el mensaje general y los detalles por campo. */
function errores_de(array $respuesta): array
{
    $datos = $respuesta['datos'];
    $general = isset($datos['error']) ? (string)$datos['error'] : 'La operación no se pudo completar.';
    $detalles = isset($datos['detalles']) && is_array($datos['detalles']) ? $datos['detalles'] : [];
    return [$general, $detalles];
}
