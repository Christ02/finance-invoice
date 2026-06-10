"""Cliente de Gmail en modo solo-lectura (gmail.readonly).

Auth con refresh token, búsqueda de notificaciones FEL por fecha, y fetch del
cuerpo HTML de cada mensaje. Nunca escribe ni borra correo.

El token se genera una vez con `python -m src.auth_setup` (ver ese módulo) y se
guarda en la variable de entorno GMAIL_TOKEN_JSON (o en token.json para dev local).
"""

from __future__ import annotations

import base64
import json
from datetime import date

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

from . import config

# Solo lectura. Nunca escribir/borrar correo.
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

TOKEN_FILE = "token.json"


def _load_credentials() -> Credentials:
    """Carga las credenciales OAuth desde GMAIL_TOKEN_JSON o token.json."""
    if config.GMAIL_TOKEN_JSON:
        info = json.loads(config.GMAIL_TOKEN_JSON)
    else:
        try:
            with open(TOKEN_FILE, encoding="utf-8") as fh:
                info = json.load(fh)
        except FileNotFoundError as exc:
            raise RuntimeError(
                "No hay credenciales de Gmail. Define GMAIL_TOKEN_JSON o genera "
                "token.json con `python -m src.auth_setup`."
            ) from exc
    return Credentials.from_authorized_user_info(info, SCOPES)


def auth():
    """Autentica y devuelve el servicio de Gmail (solo lectura).

    Refresca el access token con el refresh token si está vencido.
    """
    creds = _load_credentials()
    if not creds.valid:
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            raise RuntimeError(
                "Credenciales de Gmail inválidas y sin refresh_token. "
                "Regenera el token con `python -m src.auth_setup`."
            )
    return build("gmail", "v1", credentials=creds, cache_discovery=False)


def _build_query(desde: date) -> str:
    """Arma la query de Gmail para las notificaciones FEL desde una fecha."""
    after = desde.strftime("%Y/%m/%d")
    return (
        f'from:{config.FEL_SENDER} '
        f'subject:"Notificación Factura Electrónica" '
        f'after:{after}'
    )


def buscar_facturas(desde: date, service=None) -> list[str]:
    """Devuelve los message_id de las notificaciones FEL desde `desde`.

    Pagina todos los resultados.
    """
    service = service or auth()
    query = _build_query(desde)
    ids: list[str] = []
    page_token = None
    while True:
        resp = (
            service.users()
            .messages()
            .list(userId="me", q=query, pageToken=page_token)
            .execute()
        )
        ids.extend(m["id"] for m in resp.get("messages", []))
        page_token = resp.get("nextPageToken")
        if not page_token:
            break
    return ids


def _extract_html(payload: dict) -> str | None:
    """Recorre el árbol de partes MIME y devuelve el primer cuerpo text/html."""
    if payload.get("mimeType") == "text/html":
        data = payload.get("body", {}).get("data")
        if data:
            return base64.urlsafe_b64decode(data).decode("utf-8", "replace")
    for part in payload.get("parts", []) or []:
        html = _extract_html(part)
        if html:
            return html
    return None


def get_html(message_id: str, service=None) -> str:
    """Devuelve el cuerpo HTML decodificado de un mensaje."""
    service = service or auth()
    msg = (
        service.users()
        .messages()
        .get(userId="me", id=message_id, format="full")
        .execute()
    )
    html = _extract_html(msg.get("payload", {}))
    if html is None:
        raise ValueError(f"El mensaje {message_id} no tiene parte text/html.")
    return html
