"""Orquestador end-to-end: Gmail → parser → categorizer → Supabase.

Lee sync_state, calcula fecha de inicio (BACKFILL_MONTHS o last_processed_date),
procesa de forma idempotente, actualiza sync_state. Flag --backfill.
Punto de entrada: `python -m src.pipeline`.

# TODO: Fase 5
"""
