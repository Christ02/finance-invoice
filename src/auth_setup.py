"""Script one-shot para generar token.json vía OAuth installed-app.

Uso (una sola vez, localmente):

    python -m src.auth_setup

Abre el navegador, te pide login con tu Gmail y consentimiento (scope
gmail.readonly), y guarda las credenciales en token.json. Al final imprime el
valor listo para pegar en GMAIL_TOKEN_JSON (lo usa el cron sin archivo).

Requiere credentials.json (OAuth client tipo "Desktop app") en la raíz del repo.
La cuenta de Gmail debe estar como "Test user" en la pantalla de consentimiento
mientras la app esté en modo Testing.
"""

from __future__ import annotations

import json
import os

from google_auth_oauthlib.flow import InstalledAppFlow

from .gmail_client import SCOPES, TOKEN_FILE

CREDENTIALS_FILE = "credentials.json"


def main() -> None:
    if not os.path.exists(CREDENTIALS_FILE):
        raise SystemExit(
            f"Falta {CREDENTIALS_FILE} (OAuth client 'Desktop app') en la raíz del repo."
        )

    flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
    # access_type=offline + prompt=consent asegura que venga el refresh_token.
    creds = flow.run_local_server(
        port=0, access_type="offline", prompt="consent"
    )

    token_json = creds.to_json()
    with open(TOKEN_FILE, "w", encoding="utf-8") as fh:
        fh.write(token_json)

    print(f"\n✅ token guardado en {TOKEN_FILE}\n")
    if not creds.refresh_token:
        print(
            "⚠️  No vino refresh_token. Revoca el acceso en "
            "https://myaccount.google.com/permissions y vuelve a correr esto.\n"
        )
    print("Para el cron, pega esto como una sola línea en GMAIL_TOKEN_JSON:\n")
    print(json.dumps(json.loads(token_json)))


if __name__ == "__main__":
    main()
