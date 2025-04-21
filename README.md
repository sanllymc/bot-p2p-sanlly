# 🤖 Bot P2P Sanlly

Este es un bot de Telegram automatizado para llevar control de operaciones de compra/venta de USDT en arbitraje P2P, con conexión a Google Sheets y alertas automáticas de precios.

## ✅ Funciones principales

- Registro de operaciones de compra y venta con cálculo automático de:
  - Total
  - Ganancia por operación
  - Balance acumulado

- Conexión directa con Google Sheets
- Alertas automáticas si el precio del USDT sube o baja de un umbral
- Webhook con Flask + Render para ejecución 24/7

---

## 🧾 Comandos disponibles

| Comando | Descripción |
|--------|-------------|
| `/compra <precio> <cantidad>` | Registra una compra de USDT |
| `/venta <precio> <cantidad>` | Registra una venta y calcula ganancia |
| `/resumen` | Muestra la ganancia total acumulada |
| `/balance` | Muestra el balance acumulado |
| `/borrar_ultima` | Elimina la última fila de la hoja |
| `/alerta_menor <precio>` | Alerta si USDT baja a ese valor |
| `/alerta_mayor <precio>` | Alerta si USDT sube a ese valor |
| `/cancelar_alertas` | Elimina todas las alertas activas |

---

## 🚀 Despliegue en Render

1. Sube este proyecto a un repositorio de GitHub
2. Crea un nuevo servicio web en [https://render.com](https://render.com)
3. Conecta el repositorio
4. Rellena las siguientes variables de entorno:

| Clave | Valor |
|------|-------|
| `TOKEN` | Token de tu bot de Telegram |
| `CHAT_ID` | Tu chat ID de Telegram |
| `SPREADSHEET_ID` | ID de tu Google Sheets |

5. Asegúrate de subir tu archivo `credentials.json` a Render (usando Secret Files)

---

## 📌 Requisitos

- Python 3.10+
- `requirements.txt` con:
  - Flask
  - pyTelegramBotAPI
  - gspread
  - oauth2client
  - requests

---

## 📄 Licencia

Este bot fue creado por @sanllymc para automatizar el control de arbitraje en P2P con integración de Google Sheets y precios desde Binance.

