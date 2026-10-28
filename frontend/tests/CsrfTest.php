<?php
declare(strict_types=1);

use PHPUnit\Framework\TestCase;

/**
 * Pruebas unitarias de la protección CSRF de includes/helpers.php (remediación del
 * hallazgo S4502 en la capa que sí autentica con cookie de sesión).
 */
final class CsrfTest extends TestCase
{
    protected function setUp(): void
    {
        $_SESSION = [];
    }

    public function testTokenEsAleatorioDe64HexadecimalesYEstableEnLaSesion(): void
    {
        $token = csrf_token();
        $this->assertSame(1, preg_match('/^[0-9a-f]{64}$/', $token));
        $this->assertSame($token, csrf_token());
        $_SESSION = [];
        $this->assertTrue($token !== csrf_token());
    }

    public function testTokenValidoSoloSiCoincideConElDeLaSesion(): void
    {
        $token = csrf_token();
        $this->assertTrue(csrf_valido($token));
        $this->assertSame(false, csrf_valido('otro-token'));
        $this->assertSame(false, csrf_valido(null));
        $this->assertSame(false, csrf_valido(['arreglo']));
        $_SESSION = [];
        $this->assertSame(false, csrf_valido($token));
    }

    public function testCampoOcultoIncluyeElTokenDeLaSesion(): void
    {
        $html = campo_csrf();
        $this->assertStringContainsString('type="hidden"', $html);
        $this->assertStringContainsString('name="csrf_token"', $html);
        $this->assertStringContainsString('value="' . $_SESSION['csrf'] . '"', $html);
    }
}
