<?php
declare(strict_types=1);

use PHPUnit\Framework\TestCase;

/**
 * Pruebas unitarias de includes/helpers.php (componente crítico del frontend, sección
 * 3.7 de la Fase 1): escape de salida contra XSS, formato de montos y estados.
 */
final class HelpersTest extends TestCase
{
    protected function setUp(): void
    {
        $_SESSION = [];
        $_POST = [];
    }

    public function testEscapaEtiquetasYComillasContraXss(): void
    {
        $this->assertSame(
            '&lt;script&gt;alert(&quot;x&quot;)&lt;/script&gt; &#039;a&#039;',
            e('<script>alert("x")</script> \'a\'')
        );
    }

    public function testEscapeDeNuloDevuelveCadenaVacia(): void
    {
        $this->assertSame('', e(null));
        $this->assertSame('12.5', e(12.5));
    }

    public function testFormatoDeQuetzalesConSeparadorDeMilesYDosDecimales(): void
    {
        $this->assertSame('Q1,807.62', quetzales(1807.62));
        $this->assertSame('Q1,500,000.00', quetzales('1500000'));
        $this->assertSame('Q0.00', quetzales(null));
    }

    public function testFormatoDePorcentajeYValorNulo(): void
    {
        $this->assertSame('40.00 %', porcentaje(40));
        $this->assertSame('—', porcentaje(null));
    }

    public function testFechaCortaConValoresValidosVaciosEInvalidos(): void
    {
        $this->assertSame('01/10/2026 08:15', fecha_corta('2026-10-01 08:15:00'));
        $this->assertSame('—', fecha_corta(null));
        $this->assertSame('—', fecha_corta(''));
        $this->assertSame('no es fecha', fecha_corta('no es fecha'));
    }

    public function testEtiquetaDeEstadoConocidoUsaTextoYClase(): void
    {
        $html = etiqueta_estado('EN_REVISION');
        $this->assertStringContainsString('estado--revision', $html);
        $this->assertStringContainsString('En revisión', $html);
    }

    public function testEstadoDesconocidoSeEscapaYUsaClaseNeutra(): void
    {
        $html = etiqueta_estado('<b>RARO</b>');
        $this->assertStringContainsString('estado--neutro', $html);
        $this->assertStringContainsString('&lt;b&gt;RARO&lt;/b&gt;', $html);
        $this->assertSame('Vencida', texto_estado('VENCIDA'));
        $this->assertSame('neutro', clase_estado('OTRO'));
    }

    public function testPaginaDeInicioSegunElRol(): void
    {
        $this->assertSame('analista.php', pagina_inicio('ANALISTA'));
        $this->assertSame('admin_productos.php', pagina_inicio('ADMIN'));
        $this->assertSame('panel.php', pagina_inicio('SOLICITANTE'));
    }

    public function testErrorDeCampoSeEscapaYSeOmiteSiNoExiste(): void
    {
        $html = error_campo(['monto' => 'Monto <inválido>'], 'monto');
        $this->assertStringContainsString('id="error-monto"', $html);
        $this->assertStringContainsString('Monto &lt;inválido&gt;', $html);
        $this->assertSame('', error_campo([], 'monto'));
    }

    public function testMensajesFlashSeConsumenUnaSolaVez(): void
    {
        flash('info', 'Sesión cerrada');
        $this->assertSame([['tipo' => 'info', 'mensaje' => 'Sesión cerrada']], tomar_flash());
        $this->assertSame([], tomar_flash());
    }

    public function testValorPostRecortaEspaciosYUsaPredeterminado(): void
    {
        $_POST['email'] = '  cliente@correo.com ';
        $this->assertSame('cliente@correo.com', valor_post('email'));
        $this->assertSame('PERSONAL', valor_post('producto', 'PERSONAL'));
    }

    public function testTextoDeTipoDeEmpleo(): void
    {
        $this->assertSame('Asalariado', texto_tipo_empleo('ASALARIADO'));
        $this->assertSame('OTRO', texto_tipo_empleo('OTRO'));
    }
}
