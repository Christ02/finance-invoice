"""Carga y validación de configuración desde variables de entorno.

Lee `.env` (si existe) con python-dotenv y expone las constantes del proyecto.
La validación NO corre al importar — llamar a `validate()` explícitamente — para
que importar el módulo o correr tests no falle cuando aún no hay secrets.
"""

import os

from dotenv import load_dotenv

load_dotenv()

# --- Secrets requeridos (sin default; validate() los exige) ---
GMAIL_TOKEN_JSON = os.getenv("GMAIL_TOKEN_JSON")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

# --- Config con defaults ---
FEL_SENDER = os.getenv("FEL_SENDER", "notificacionesfel@sat.gob.gt")
BACKFILL_MONTHS = int(os.getenv("BACKFILL_MONTHS", "12"))
IA_MODEL = os.getenv("IA_MODEL", "claude-haiku-4-5-20251001")

# Variables que deben estar presentes para correr el pipeline.
REQUIRED = (
    "GMAIL_TOKEN_JSON",
    "SUPABASE_URL",
    "SUPABASE_SERVICE_KEY",
    "ANTHROPIC_API_KEY",
)


def validate() -> None:
    """Verifica que las variables requeridas estén presentes.

    Lanza RuntimeError con la lista de las que faltan.
    """
    faltantes = [name for name in REQUIRED if not globals().get(name)]
    if faltantes:
        raise RuntimeError(
            "Faltan variables de entorno requeridas: "
            + ", ".join(faltantes)
            + ". Copia .env.example a .env y rellena los valores."
        )
