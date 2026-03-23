import os
import json
import logging
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
SPREADSHEET_ID = os.environ["GOOGLE_SHEET_ID"]
SHEET_NAME = os.environ.get("GOOGLE_SHEET_NAME", "Registros")

HEADERS = ["Nombre", "Categoría", "Producto", "Precio", "Fecha", "Hora"]


def get_service():
    creds_json = os.environ["GOOGLE_CREDENTIALS_JSON"]
    creds_dict = json.loads(creds_json)
    creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
    return build("sheets", "v4", credentials=creds)


def ensure_headers(service):
    """Crea la fila de encabezados si la hoja está vacía."""
    result = (
        service.spreadsheets()
        .values()
        .get(spreadsheetId=SPREADSHEET_ID, range=f"{SHEET_NAME}!A1:F1")
        .execute()
    )
    if not result.get("values"):
        service.spreadsheets().values().update(
            spreadsheetId=SPREADSHEET_ID,
            range=f"{SHEET_NAME}!A1",
            valueInputOption="USER_ENTERED",
            body={"values": [HEADERS]},
        ).execute()
        logger.info("Encabezados creados en Google Sheets.")


def append_row(data: dict):
    service = get_service()
    ensure_headers(service)

    row = [
        data["nombre"],
        data["categoria"],
        data["producto"],
        float(data["precio"]),   # ← número real
        data["fecha"],           # ← fecha válida
        data["hora"],            # ← hora válida
    ]

    service.spreadsheets().values().append(
        spreadsheetId=SPREADSHEET_ID,
        range=f"{SHEET_NAME}!A1",
        valueInputOption="USER_ENTERED",
        insertDataOption="INSERT_ROWS",
        body={"values": [row]},
    ).execute()

    logger.info(f"Fila agregada: {row}")
