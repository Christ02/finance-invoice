# FEL Gastos

Sistema personal que lee facturas electrónicas (FEL) del SAT desde Gmail, las categoriza
(híbrido reglas + IA) y las guarda en Supabase. Dashboard en Next.js (Fase 7).

Corre solo vía **GitHub Actions cron** (Fase 6). Ver `CLAUDE.md` para las reglas del proyecto.

## Requisitos

- Python 3.11+
- Cuentas/credenciales: Gmail API (OAuth installed-app), Supabase, Anthropic API.

## Setup local

```bash
pip install -e .            # instala el paquete y dependencias
cp .env.example .env        # luego rellena los valores
```

Variables de entorno (ver `.env.example`):

| Variable | Descripción |
|---|---|
| `GMAIL_TOKEN_JSON` | Contenido del `token.json` con `refresh_token` (se genera una vez localmente). |
| `SUPABASE_URL` | URL del proyecto Supabase. |
| `SUPABASE_SERVICE_KEY` | Key `service_role` (solo backend/cron). |
| `ANTHROPIC_API_KEY` | API key de Claude (categorización). |
| `FEL_SENDER` | Remitente FEL. Default `notificacionesfel@sat.gob.gt`. |
| `BACKFILL_MONTHS` | Meses de histórico en la primera corrida. Default `12` (`0` = solo nuevas). |
| `IA_MODEL` | Modelo de IA para categorizar. Default `claude-haiku-4-5-20251001`. |

Validar que la config esté completa:

```bash
python -c "import src.config as c; c.validate()"
```

## Fases

| Fase | Estado | Entregable |
|---|---|---|
| 0 — Scaffold | ✅ | estructura, config, stubs |
| 1 — Gmail client | ⬜ | `src/gmail_client.py` (solo lectura) |
| 2 — Parser FEL | ⬜ | `src/fel_parser.py` + tests con correos reales en `tests/fixtures/` |
| 3 — Capa Supabase | ⬜ | `sql/schema.sql`, `src/db.py`, `src/seed_reglas.py` |
| 4 — Categorizador | ⬜ | `src/categorizer.py` (reglas + IA) |
| 5 — Pipeline | ⬜ | `src/pipeline.py` (`python -m src.pipeline`) |
| 6 — Scheduler | ⬜ | `.github/workflows/sync.yml` (cron 6h) |
| 7 — Dashboard | ⬜ | `dashboard/` (Next.js, requiere diseños en `designs/`) |
| 8 — Pulido | ⬜ | Muni Antigua, NCRE, recategorización manual, vista pendientes |

## Tests

```bash
pytest
```
