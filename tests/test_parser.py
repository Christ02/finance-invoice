"""Tests del parser FEL contra fixtures reales en tests/fixtures/*.html.

Los fixtures son correos FEL reales (decodificados del cuerpo del mensaje), que
NO se versionan por contener datos personales. Si no existen, los tests se omiten.
"""

import datetime as dt
import glob
import os
from decimal import Decimal

import pytest

from src.fel_parser import parse_factura

FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "fixtures")
FIXTURES = sorted(glob.glob(os.path.join(FIXTURES_DIR, "fel*.html")))

requires_fixtures = pytest.mark.skipif(
    not FIXTURES, reason="No hay fixtures FEL en tests/fixtures/ (datos personales)."
)


def _load(name: str) -> str:
    with open(os.path.join(FIXTURES_DIR, name), encoding="utf-8") as fh:
        return fh.read()


@requires_fixtures
@pytest.mark.parametrize("path", FIXTURES, ids=lambda p: os.path.basename(p))
def test_campos_basicos(path):
    """Cada fixture parsea con los campos esperados y tipos correctos."""
    with open(path, encoding="utf-8") as fh:
        f = parse_factura(fh.read())

    assert f["numero_autorizacion"]            # PK / dedup
    assert f["tipo"] == "FACT"                 # los 6 fixtures son facturas
    assert f["moneda"] == "GTQ"
    assert isinstance(f["monto"], Decimal) and f["monto"] > 0
    assert f["emisor_nit"] and f["emisor_nombre"]
    assert f["establecimiento"]
    assert isinstance(f["fecha_emision"], dt.datetime)


@requires_fixtures
def test_valores_exactos_fel1():
    """Valores conocidos de fel1.html (Pan-American Life)."""
    f = parse_factura(_load("fel1.html"))
    assert f["numero_autorizacion"] == "FFF67974-5521-4266-B111-D5A4DF6DEADE"
    assert f["tipo"] == "FACT"
    assert f["serie"] == "FFF67974"
    assert f["numero"] == "1428243046"
    assert f["emisor_nit"] == "725269"
    assert f["emisor_nombre"].startswith("PAN-AMERICAN")  # el guion del nombre se preserva
    assert f["monto"] == Decimal("716.46")
    assert f["moneda"] == "GTQ"


@requires_fixtures
def test_monto_con_separador_de_miles():
    """fel4.html trae 'GTQ - 1,199.00' → Decimal sin coma."""
    f = parse_factura(_load("fel4.html"))
    assert f["monto"] == Decimal("1199.00")


def test_ncre_monto_negativo():
    """NCRE (nota de crédito) → monto negativo. Caso sintético (sin fixture real)."""
    html = """
    <table>
      <tr><td>Tipo</td><td>NCRE - Nota de Crédito</td></tr>
      <tr><td>Número Autorización</td><td>ABC-123</td></tr>
      <tr><td>Serie</td><td>S1</td></tr>
      <tr><td>Número</td><td>999</td></tr>
      <tr><td>Emisor</td><td>123456 - TIENDA EJEMPLO, S.A.</td></tr>
      <tr><td>Establecimiento</td><td>1 - SUCURSAL CENTRO</td></tr>
      <tr><td>Fecha de emisión</td><td>2026-06-01T10:00:00-06:00</td></tr>
      <tr><td>Monto</td><td>GTQ - 50.00</td></tr>
    </table>
    """
    f = parse_factura(html)
    assert f["tipo"] == "NCRE"
    assert f["monto"] == Decimal("-50.00")
    assert f["emisor_nit"] == "123456"
    assert f["emisor_nombre"] == "TIENDA EJEMPLO, S.A."
    assert f["establecimiento"] == "SUCURSAL CENTRO"


def test_html_invalido_sin_autorizacion():
    """HTML que no es una notificación FEL → ValueError."""
    with pytest.raises(ValueError):
        parse_factura("<table><tr><td>Hola</td><td>Mundo</td></tr></table>")
