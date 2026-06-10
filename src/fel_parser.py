"""Parser FEL: HTML del correo → dict limpio de factura.

Sigue el mapa label→campo de CLAUDE.md. Maneja Emisor "NIT - NOMBRE",
Establecimiento "N - NOMBRE", Monto "GTQ - 716.46", fecha con dateutil, y
NCRE → monto negativo. Test-driven contra fixtures reales en tests/fixtures.

# TODO: Fase 2
"""
