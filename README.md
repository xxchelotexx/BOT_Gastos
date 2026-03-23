# 🤖 Bot de Telegram — Registro de Precios (Stack 100% Gratuito)

Bot que recibe información por **texto o voz** y la guarda en Google Sheets.

## 💸 Costo operativo: $0

| Componente | Solución gratuita |
|---|---|
| 🎙️ Transcripción de voz | `faster-whisper` corriendo **local** en Railway |
| 🧠 Parseo con IA | **Gemini 1.5 Flash** (free tier: 15 req/min, 1M tokens/día) |
| 📊 Base de datos | Google Sheets (gratis) |
| ☁️ Hosting | Railway Hobby ($5 crédito incluido/mes, suficiente para un bot) |

---

## 📋 Formato de entrada

```
Nombre, Categoría, Producto, Precio
```

**Ejemplo texto:** `Marcelo, Mercado, Banana, 5Bs`
**Ejemplo voz:** *"Marcelo mercado banana cinco bolivianos"*

---

## ⚙️ Variables de entorno

| Variable | Descripción | Dónde obtenerla |
|---|---|---|
| `TELEGRAM_TOKEN` | Token del bot | @BotFather en Telegram |
| `GEMINI_API_KEY` | API Key gratuita de Gemini | [aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey) |
| `GOOGLE_SHEET_ID` | ID de tu hoja de Sheets | URL de la hoja |
| `GOOGLE_SHEET_NAME` | Nombre de la pestaña | Default: `Registros` |
| `GOOGLE_CREDENTIALS_JSON` | Credenciales cuenta de servicio | Google Cloud Console |
| `WHISPER_MODEL` | Tamaño del modelo de voz | `tiny` (recomendado) o `base` |

---

## 🚀 Pasos de configuración

### 1. Crear bot en Telegram
1. Habla con **@BotFather** → `/newbot`
2. Copia el token → `TELEGRAM_TOKEN`

### 2. Obtener Gemini API Key (gratis, sin tarjeta)
1. Ve a [aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)
2. Clic en *Create API Key*
3. Copia la clave → `GEMINI_API_KEY`

### 3. Configurar Google Sheets
1. Crea una hoja en [sheets.google.com](https://sheets.google.com)
2. Copia el ID desde la URL → `GOOGLE_SHEET_ID`
3. Ve a [Google Cloud Console](https://console.cloud.google.com/):
   - Activa la **Google Sheets API**
   - Crea una **cuenta de servicio** y descarga el JSON
4. Comparte tu hoja con el `client_email` del JSON (permisos de Editor)
5. Convierte el JSON a una línea:
   ```bash
   cat credentials.json | python3 -c "import json,sys; print(json.dumps(json.load(sys.stdin)))"
   ```
   → Ese valor es `GOOGLE_CREDENTIALS_JSON`

### 4. Desplegar en Railway
1. Sube el proyecto a GitHub
2. En [railway.app](https://railway.app): *New Project → Deploy from GitHub*
3. Agrega todas las variables en la pestaña **Variables**
4. Railway detecta el `railway.toml` y despliega automáticamente

> ℹ️ El primer deploy tardará unos minutos porque descarga el modelo Whisper `tiny` (~75MB).

---

## 🔧 Lógica de parseo (3 niveles, sin gastar créditos si no es necesario)

```
Mensaje recibido
      │
      ▼
① Regex simple (4 partes separadas por coma)  ──✅──▶ Guardar
      │ ✗
      ▼
② Regex flexible (tokens por espacio / precio al final)  ──✅──▶ Guardar
      │ ✗
      ▼
③ Gemini 1.5 Flash (IA gratuita)  ──✅──▶ Guardar
      │ ✗
      ▼
   ❌ Pedir al usuario que reformatee
```

---

## 📊 Resultado en Google Sheets

| Nombre | Categoría | Producto | Precio | Fecha | Hora |
|--------|-----------|----------|--------|-------|------|
| Marcelo | Mercado | Banana | 5Bs | 22/03/2026 | 14:35:22 |
