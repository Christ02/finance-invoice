# FEL Gastos — contexto del proyecto

Sistema personal que lee facturas electrónicas (FEL) del SAT desde Gmail,
las categoriza (híbrido reglas + IA) y las guarda en Supabase. Dashboard en Next.js.

## Reglas de oro
- Solo procesar correos de `notificacionesfel@sat.gob.gt`, asunto "Notificación Factura Electrónica".
- Toda la data sale del cuerpo HTML del correo. NO descargar PDF ni XML.
- `numero_autorizacion` es la PK y la clave de deduplicación. Todo upsert es idempotente.
- Gmail siempre en modo solo-lectura (`gmail.readonly`). Nunca escribir/borrar correo.
- Secrets solo por variables de entorno. Nunca commitear tokens ni llaves.

## Categorización
1. Buscar match en tabla `reglas` (nit > emisor > establecimiento).
2. Si no hay match, clasificar con Claude API (modelo Haiku) entre las categorías permitidas.
3. Guardar la decisión de IA como regla nueva (source='aprendida') para no repetir el costo.
4. Si la IA tiene baja confianza, dejar categoria='Sin categoría', origen='pendiente'.

## Estilo
- Funciones puras y testeables. Parser y categorizer no tocan red salvo lo necesario.
- Tests con pytest contra fixtures reales en tests/fixtures.
- Commits pequeños por fase.

## Diseños del dashboard
- La UI la define el dueño del proyecto. Los diseños/mockups llegan en /designs.
- NO inventar la interfaz: implementar el dashboard fiel a lo que esté en /designs.
- Si /designs está vacío, usar dashboard-gastos-fel.jsx como referencia provisional y NO avanzar la fase 7 hasta tener los diseños.

## Mapa de campos (tabla HTML del correo → factura)

| Label en el correo | Campo | Notas de parseo |
|---|---|---|
| `Tipo` | `tipo` | `FACT`, `NCRE`, etc. |
| `Número Autorización` | `numero_autorizacion` | **PK / dedup** |
| `Serie` | `serie` | |
| `Número` | `numero` | |
| `Emisor` | `emisor_nit`, `emisor_nombre` | viene `"NIT - NOMBRE"`, split en el primer `-` |
| `Establecimiento` | `establecimiento` | viene `"N - NOMBRE"` |
| `Fecha de emisión` | `fecha_emision` | ISO con offsets variados → usar `dateutil` |
| `Monto` | `moneda`, `monto` | viene `"GTQ - 716.46"` |

Casos especiales: `NCRE` = nota de crédito → monto negativo. Honorarios UFM
(`contabilidad@ufm.edu`) = ingreso, se excluye. Comprobante Muni Antigua
(`no-reply@muniantigua.gob.gt`) = otro formato, se maneja en Fase 8.

## Estado de fases
- Fase 0 (scaffold): hecho.
- Fases 1–8: pendientes (ver README).
