<?php
declare(strict_types=1);

use PHPUnit\Framework\TestCase;

/**
 * Pruebas unitarias de includes/api.php (cliente HTTP del frontend hacia la API).
 * No se usa el backend real: API_URL apunta a un puerto local cerrado (bootstrap).
 */
final class ApiTest extends TestCase
{
    protected function setUp(): void
    {
        $_SESSION = [];
    }

    public function testErroresDeExtraeMensajeGeneralYDetallesPorCampo(): void
    {
        $respuesta = ['estado' => 400, 'datos' => [
            'error' => 'Revise los datos del formulario',
            'detalles' => ['monto' => 'Fuera de rango'],
        ]];
        [$general, $detalles] = errores_de($respuesta);
        $this->assertSame('Revise los datos del formulario', $general);
        $this->assertSame(['monto' => 'Fuera de rango'], $detalles);
    }

    public function testErroresDeSinMensajeUsaTextoPredeterminado(): void
    {
        [$general, $detalles] = errores_de(['estado' => 500, 'datos' => []]);
        $this->assertSame('La operación no se pudo completar.', $general);
        $this->assertSame([], $detalles);
    }

    public function testApiSinConexionDevuelveEstadoCeroYMensajeAmigable(): void
    {
        $respuesta = api('GET', '/api/health');
        $this->assertSame(0, $respuesta['estado']);
        $this->assertStringContainsString('No fue posible conectar', $respuesta['datos']['error']);
    }
}
