<?php
declare(strict_types=1);

const ESTADOS_SOLICITUD = [
    'BORRADOR' => ['Borrador', 'neutro'],
    'EN_REVISION' => ['En revisión', 'revision'],
    'PREAPROBADA' => ['Preaprobada', 'exito'],
    'RECHAZADA' => ['Rechazada', 'rechazo'],
    'ACEPTADA' => ['Aceptada', 'exito'],
    'DECLINADA' => ['Declinada', 'neutro'],
    'CANCELADA' => ['Cancelada', 'neutro'],
    'VENCIDA' => ['Vencida', 'neutro'],
];

const TIPOS_EMPLEO = [
    'ASALARIADO' => 'Asalariado',
    'INDEPENDIENTE' => 'Independiente',
];

function e(mixed $valor): string
{
    return htmlspecialchars((string)($valor ?? ''), ENT_QUOTES, 'UTF-8');
}

function quetzales(mixed $monto): string
{
    return 'Q' . number_format((float)$monto, 2, '.', ',');
}

function porcentaje(mixed $valor): string
{
    return $valor === null ? '—' : number_format((float)$valor, 2, '.', ',') . ' %';
}

function fecha_corta(?string $texto): string
{
    if ($texto === null || $texto === '') {
        return '—';
    }
    $marca = strtotime($texto);
    return $marca === false ? $texto : date('d/m/Y H:i', $marca);
}

function etiqueta_estado(string $estado): string
{
    $estados = ESTADOS_SOLICITUD;
    [$texto, $clase] = $estados[$estado] ?? [$estado, 'neutro'];
    return '<span class="estado estado--' . $clase . '">' . e($texto) . '</span>';
}

function flash(string $tipo, string $mensaje): void
{
    $_SESSION['flash'][] = ['tipo' => $tipo, 'mensaje' => $mensaje];
}

function tomar_flash(): array
{
    $mensajes = $_SESSION['flash'] ?? [];
    unset($_SESSION['flash']);
    return $mensajes;
}

function redirigir(string $url): never
{
    header('Location: ' . $url);
    exit;
}

function usuario_actual(): ?array
{
    return $_SESSION['usuario'] ?? null;
}

function pagina_inicio(string $rol): string
{
    return match ($rol) {
        'ANALISTA' => 'analista.php',
        'ADMIN' => 'admin_productos.php',
        default => 'panel.php',
    };
}

/** Exige sesión iniciada y, si se indican, uno de los roles permitidos. */
function exigir_sesion(array $roles = []): array
{
    $usuario = usuario_actual();
    if ($usuario === null) {
        flash('info', 'Inicie sesión para continuar.');
        redirigir('login.php');
    }
    if ($roles !== [] && !in_array($usuario['rol'], $roles, true)) {
        http_response_code(403);
        encabezado('Acceso restringido');
        echo '<section class="panel"><h1>Acceso restringido</h1>'
            . '<p>Su usuario no tiene permiso para ver esta página.</p>'
            . '<p><a class="boton" href="' . e(pagina_inicio($usuario['rol'])) . '">Ir a mi inicio</a></p></section>';
        pie();
        exit;
    }
    return $usuario;
}

function valor_post(string $campo, string $predeterminado = ''): string
{
    return isset($_POST[$campo]) ? trim((string)$_POST[$campo]) : $predeterminado;
}

function texto_estado(string $estado): string
{
    $estados = ESTADOS_SOLICITUD;
    return isset($estados[$estado]) ? $estados[$estado][0] : $estado;
}

function clase_estado(string $estado): string
{
    $estados = ESTADOS_SOLICITUD;
    return isset($estados[$estado]) ? $estados[$estado][1] : 'neutro';
}

function texto_tipo_empleo(string $tipo): string
{
    $tipos = TIPOS_EMPLEO;
    return $tipos[$tipo] ?? $tipo;
}

function error_campo(array $detalles, string $campo): string
{
    if (!isset($detalles[$campo])) {
        return '';
    }
    return '<p class="campo__error" id="error-' . e($campo) . '">' . e($detalles[$campo]) . '</p>';
}
