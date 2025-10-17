from flask import Flask, request
from twilio.rest import Client
import os
from datetime import datetime

app = Flask(__name__)

# Variables de entorno (las configuraremos en Render)
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER")

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# Base de datos de respuestas del bot
respuestas = {
    "hola": "¡Hola! 👋 ¿Cómo estás? Soy un bot automático.",
    "ayuda": "📋 Puedo ayudarte con: hola, ayuda, hora, chiste, quién eres, gracias",
    "hora": f"🕐 La hora actual es: {datetime.now().strftime('%H:%M:%S')}",
    "chiste": "😂 ¿Por qué los programadores prefieren el dark mode? ¡Porque la luz atrae bugs! 🐛",
    "quién eres": "🤖 Soy un bot de WhatsApp creado con Twilio y Python. Estoy disponible 24/7.",
    "gracias": "¡De nada! 😊 Si necesitas algo más, cuéntame.",
}

def procesar_mensaje(mensaje):
    """
    Procesa un mensaje y devuelve una respuesta
    Busca coincidencias exactas y parciales
    """
    mensaje_limpio = mensaje.lower().strip()
    
    # Busca coincidencias exactas primero
    if mensaje_limpio in respuestas:
        return respuestas[mensaje_limpio]
    
    # Busca coincidencias parciales
    for clave, respuesta in respuestas.items():
        if clave in mensaje_limpio:
            return respuesta
    
    # Respuesta por defecto si no entiende
    return "🤔 No entiendo eso. Escribe 'ayuda' para ver mis opciones disponibles."

@app.route("/webhook", methods=["POST"])
def webhook():
    """
    Esta función se ejecuta cada vez que recibe un mensaje por WhatsApp
    """
    try:
        print("=" * 50)
        print("🔔 WEBHOOK RECIBIDO")
        print(f"Todos los datos: {request.values}")
        print("=" * 50)
        
        # Obtiene el mensaje recibido
        incoming_msg = request.values.get("Body", "")
        # Obtiene el número de quien envía el mensaje
        sender = request.values.get("From")
        
        print(f"📥 Mensaje recibido de {sender}: {incoming_msg}")
        
        if not incoming_msg:
            print("⚠️ Mensaje vacío recibido")
            return "OK", 200
        
        # Procesa el mensaje y obtiene la respuesta
        respuesta = procesar_mensaje(incoming_msg)
        
        # Envía la respuesta por WhatsApp
        client.messages.create(
            body=respuesta,
            from_=TWILIO_WHATSAPP_NUMBER,
            to=sender
        )
        
        print(f"✅ Respuesta enviada: {respuesta}")
        
        return "OK", 200
    
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return "Error", 500

@app.route("/", methods=["GET"])
def home():
    """
    Página de prueba para verificar que el servidor está activo
    """
    return "✅ Bot de WhatsApp está activo y funcionando", 200

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)