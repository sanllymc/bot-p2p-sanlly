import telebot
import gspread
import requests
import threading
import time
from datetime import datetime
from oauth2client.service_account import ServiceAccountCredentials

TOKEN = "7264007059:AAE9xOJjxwU0DonrGoRpGOO6w5Px5NWKo5w"
CHAT_ID = "1188735274"
SPREADSHEET_ID = "15euGYYB9YE45VJDYnkzNVnTPBb3WsbSfwRKQvuz-wWk"

bot = telebot.TeleBot(TOKEN)

scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
import os
with open("credentials.json", "w") as f:
    f.write(os.environ["GOOGLE_APPLICATION_CREDENTIALS_CONTENT"])
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)
sheet = client.open_by_key(SPREADSHEET_ID).sheet1

alertas_menor = []
alertas_mayor = []
CHECK_INTERVAL = 300

def registrar_operacion(tipo, precio, cantidad):
    total = round(float(precio) * float(cantidad), 2)
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    historial = sheet.get_all_values()
    ultima_fila = historial[-1] if len(historial) > 1 else []
    balance_actual = float(ultima_fila[6].replace(",", "")) if len(ultima_fila) >= 7 and ultima_fila[6] else 0.0
    ganancia = 0
    if tipo.lower() == "venta":
        for fila in reversed(historial[1:]):
            if fila[1].lower() == "compra":
                precio_compra = float(fila[2].replace(",", ""))
                ganancia = round((float(precio) - precio_compra) * float(cantidad), 2)
                break
        balance_actual += ganancia
    sheet.append_row([fecha, tipo, precio, cantidad, total, ganancia, balance_actual, ""])

@bot.message_handler(commands=["start", "help"])
def ayuda(message):
    texto = ("📌 *Bot P2P Sanlly* - Comandos disponibles:\n"
             "/compra <precio> <cantidad>\n"
             "/venta <precio> <cantidad>\n"
             "/resumen\n"
             "/balance\n"
             "/borrar_ultima\n"
             "/alerta_menor <precio>\n"
             "/alerta_mayor <precio>\n"
             "/cancelar_alertas")
    bot.send_message(message.chat.id, texto, parse_mode="Markdown")

@bot.message_handler(commands=["compra"])
def compra(message):
    try:
        _, precio, cantidad = message.text.split()
        registrar_operacion("Compra", precio, cantidad)
        bot.send_message(message.chat.id, f"✅ Compra registrada: {cantidad} USDT a RD${precio}")
    except:
        bot.send_message(message.chat.id, "⚠️ Formato incorrecto. Usa: /compra <precio> <cantidad>")

@bot.message_handler(commands=["venta"])
def venta(message):
    try:
        _, precio, cantidad = message.text.split()
        registrar_operacion("Venta", precio, cantidad)
        bot.send_message(message.chat.id, f"✅ Venta registrada: {cantidad} USDT a RD${precio}")
    except:
        bot.send_message(message.chat.id, "⚠️ Formato incorrecto. Usa: /venta <precio> <cantidad>")

@bot.message_handler(commands=["resumen"])
def resumen(message):
    datos = sheet.get_all_values()[1:]
    ganancia_total = sum(float(f[5]) for f in datos if f[5])
    bot.send_message(message.chat.id, f"📈 Ganancia total: RD${ganancia_total:.2f}")

@bot.message_handler(commands=["balance"])
def balance(message):
    datos = sheet.get_all_values()[1:]
    if datos and datos[-1][6]:
        balance = datos[-1][6]
        bot.send_message(message.chat.id, f"💰 Balance acumulado: RD${balance}")
    else:
        bot.send_message(message.chat.id, "No hay balance aún.")

@bot.message_handler(commands=["borrar_ultima"])
def borrar_ultima(message):
    filas = len(sheet.get_all_values())
    if filas > 1:
        sheet.delete_rows(filas)
        bot.send_message(message.chat.id, "🗑 Última fila eliminada.")
    else:
        bot.send_message(message.chat.id, "No hay filas para borrar.")

@bot.message_handler(commands=["alerta_menor"])
def establecer_alerta_menor(message):
    try:
        _, valor = message.text.split()
        alertas_menor.append(float(valor))
        bot.send_message(message.chat.id, f"🔔 Alerta baja configurada: USDT ≤ RD${valor}")
    except:
        bot.send_message(message.chat.id, "⚠️ Usa: /alerta_menor <precio>")

@bot.message_handler(commands=["alerta_mayor"])
def establecer_alerta_mayor(message):
    try:
        _, valor = message.text.split()
        alertas_mayor.append(float(valor))
        bot.send_message(message.chat.id, f"🔔 Alerta alta configurada: USDT ≥ RD${valor}")
    except:
        bot.send_message(message.chat.id, "⚠️ Usa: /alerta_mayor <precio>")

@bot.message_handler(commands=["cancelar_alertas"])
def cancelar_alertas(message):
    alertas_menor.clear()
    alertas_mayor.clear()
    bot.send_message(message.chat.id, "❌ Todas las alertas eliminadas.")

def obtener_precio_usdt_en_dop():
    try:
        binance_response = requests.get("https://api.binance.com/api/v3/ticker/price?symbol=USDTBRL")
        binance_price = float(binance_response.json()["price"])
        fx_response = requests.get("https://open.er-api.com/v6/latest/BRL")
        tasa_brl_dop = float(fx_response.json()["rates"]["DOP"])
        return round(binance_price * tasa_brl_dop, 2)
    except Exception as e:
        print("Error al obtener precio:", e)
        return None

def revisar_precio():
    while True:
        precio_dop = obtener_precio_usdt_en_dop()
        if precio_dop:
            for obj in alertas_menor:
                if precio_dop <= obj:
                    bot.send_message(CHAT_ID, f"⚠️ USDT bajó a RD${precio_dop} (≤ {obj})")
            for obj in alertas_mayor:
                if precio_dop >= obj:
                    bot.send_message(CHAT_ID, f"🚀 USDT subió a RD${precio_dop} (≥ {obj})")
        time.sleep(CHECK_INTERVAL)

hilo_alerta = threading.Thread(target=revisar_precio)
hilo_alerta.daemon = True
hilo_alerta.start()

bot.infinity_polling()
