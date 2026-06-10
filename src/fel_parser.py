"""Parser FEL: HTML del correo → dict limpio de factura.

Sigue el mapa label→campo de CLAUDE.md. La tabla del correo es de dos columnas
(label, valor). Maneja Emisor "NIT - NOMBRE", Establecimiento "N - NOMBRE",
Monto "GTQ - 716.46", fecha con dateutil (varios offsets) y NCRE → monto negativo.

Función pura: no toca red. Test-driven contra fixtures reales en tests/fixtures.
"""

from __future__ import annotations

import re
from decimal import Decimal

from bs4 import BeautifulSoup
from dateutil import parser as dateparser

# Delimitador real en el correo: espacio-guion-espacio. Tolerante a espaciado.
# Se usa con maxsplit=1 para no romper NITs con dígito verificador (1234567-8)
# ni nombres con guion (PAN-AMERICAN).
_DASH = re.compile(r"\s+-\s+")


def _split_dash(value: str) -> tuple[str, str]:
    """Parte 'IZQUIERDA - DERECHA' en el primer ' - '. Si no hay, derecha vacía."""
    parts = _DASH.split(value, maxsplit=1)
    if len(parts) == 2:
        return parts[0].strip(), parts[1].strip()
    return value.strip(), ""


def _tabla_a_dict(html: str) -> dict[str, str]:
    """Convierte la tabla de dos columnas del correo en {label: valor}."""
    soup = BeautifulSoup(html, "lxml")
    campos: dict[str, str] = {}
    for tr in soup.find_all("tr"):
        celdas = [c.get_text(" ", strip=True) for c in tr.find_all(["td", "th"])]
        if len(celdas) == 2 and celdas[0]:
            campos[celdas[0]] = celdas[1]
    return campos


def parse_factura(html: str) -> dict:
    """Parsea el HTML de una notificación FEL a un dict de factura.

    Devuelve las claves del esquema `facturas`. Lanza ValueError si falta el
    Número Autorización (clave de deduplicación).
    """
    campos = _tabla_a_dict(html)

    numero_autorizacion = campos.get("Número Autorización", "").strip()
    if not numero_autorizacion:
        raise ValueError("HTML sin 'Número Autorización' — no parece una notificación FEL.")

    tipo = _split_dash(campos.get("Tipo", ""))[0]  # 'FACT - Factura' -> 'FACT'

    emisor_nit, emisor_nombre = _split_dash(campos.get("Emisor", ""))

    # Establecimiento viene 'N - NOMBRE'; guardamos el nombre (lo útil para reglas).
    _, establecimiento = _split_dash(campos.get("Establecimiento", ""))
    establecimiento = establecimiento or campos.get("Establecimiento", "").strip()

    fecha_raw = campos.get("Fecha de emisión", "").strip()
    fecha_emision = dateparser.parse(fecha_raw) if fecha_raw else None

    moneda, monto_raw = _split_dash(campos.get("Monto", ""))
    monto = Decimal(monto_raw.replace(",", "")) if monto_raw else Decimal("0")
    # NCRE = nota de crédito (reembolso) → monto negativo.
    if tipo == "NCRE":
        monto = -abs(monto)

    return {
        "numero_autorizacion": numero_autorizacion,
        "tipo": tipo,
        "serie": campos.get("Serie", "").strip(),
        "numero": campos.get("Número", "").strip(),
        "emisor_nit": emisor_nit,
        "emisor_nombre": emisor_nombre,
        "establecimiento": establecimiento,
        "fecha_emision": fecha_emision,
        "monto": monto,
        "moneda": moneda or "GTQ",
    }
