import os
import re
import json
import logging
from datetime import datetime
import pytz

logger = logging.getLogger(__name__)
BOLIVIA_TZ = pytz.timezone("America/La_Paz")


def get_current_datetime():
    """
    Devuelve fecha y hora en formato compatible con Google Sheets.
    Fecha: YYYY-MM-DD
    Hora: HH:MM:SS
    """
    now = datetime.now(BOLIVIA_TZ)

    fecha = now.strftime("%Y-%m-%d")   # ← FORMATO ISO (muy importante)
    hora = now.strftime("%H:%M:%S")

    return fecha, hora


def parse_message(text: str) -> dict | None:
    data = parse_simple(text)
    if data:
        return data

    data = parse_flexible(text)
    if data:
        return data

    return parse_with_gemini(text)


def parse_simple(text: str) -> dict | None:
    """Formato exacto: Nombre, Categoría, Producto, Precio"""
    parts = [p.strip() for p in text.split(",")]

    if len(parts) == 4 and all(parts):
        fecha, hora = get_current_datetime()

        return _build(
            parts[0],
            parts[1],
            parts[2],
            parts[3],
            fecha,
            hora
        )

    return None


def parse_flexible(text: str) -> dict | None:
    """
    Soporta frases como:
    Marcelo mercado banana 5Bs
    Marcelo mercado San-Gabriel 26.5
    """

    cleaned = re.sub(r"[,\.;]+", " ", text.strip())
    tokens = [t.strip() for t in cleaned.split() if t.strip()]

    if len(tokens) == 4:
        fecha, hora = get_current_datetime()

        return _build(
            tokens[0],
            tokens[1],
            tokens[2],
            tokens[3],
            fecha,
            hora
        )

    # Detectar precio al final
    precio_match = re.search(
        r"(\d+[\.,]?\d*\s*(?:bs|bolivianos?|\$|usd|us)?)",
        text,
        re.IGNORECASE
    )

    if precio_match:
        precio = precio_match.group(1).strip()

        resto = text[:precio_match.start()].strip()

        partes = [
            p.strip()
            for p in re.split(r"[,\s]+", resto)
            if p.strip()
        ]

        if len(partes) >= 3:
            fecha, hora = get_current_datetime()

            return _build(
                partes[0],
                partes[1],
                " ".join(partes[2:]),
                precio,
                fecha,
                hora
            )

    return None


def parse_with_gemini(text: str) -> dict | None:
    """Fallback usando Gemini si no pudo parsear localmente."""

    api_key = os.environ.get("GEMINI_API_KEY")

    if not api_key:
        logger.warning(
            "GEMINI_API_KEY no configurada, no se puede usar IA."
        )
        return None

    try:
        import google.generativeai as genai

        genai.configure(api_key=api_key)

        model = genai.GenerativeModel(
            "gemini-1.5-flash"
        )

        prompt = f"""
Extrae exactamente estos 4 campos del mensaje
y responde SOLO con JSON válido:

- nombre
- categoria
- producto
- precio

Mensaje: "{text}"

Formato exacto:
{{"nombre":"...","categoria":"...","producto":"...","precio":"..."}}
"""

        response = model.generate_content(prompt)

        raw = response.text.strip()

        raw = re.sub(
            r"```json|```",
            "",
            raw
        ).strip()

        parsed = json.loads(raw)

        if all(
            parsed.get(k)
            for k in ["nombre", "categoria", "producto", "precio"]
        ):
            fecha, hora = get_current_datetime()

            return _build(
                parsed["nombre"],
                parsed["categoria"],
                parsed["producto"],
                parsed["precio"],
                fecha,
                hora
            )

    except Exception as e:
        logger.error(f"Error en Gemini fallback: {e}")

    return None


def _build(nombre, categoria, producto, precio, fecha, hora):
    """
    Limpia el precio y lo convierte a número real.
    """

    # Quitar texto como Bs, $, etc.
    precio_limpio = re.sub(
        r"[^\d.,]",
        "",
        str(precio)
    )

    # Convertir coma a punto
    precio_limpio = precio_limpio.replace(",", ".")

    try:
        precio_limpio = float(precio_limpio)
    except:
        precio_limpio = None

    return {
        "nombre": nombre,
        "categoria": categoria,
        "producto": producto,
        "precio": precio_limpio,
        "fecha": fecha,
        "hora": hora,
    }