from flask import Flask, request
from twilio.rest import Client
import os
from datetime import datetime
import openai

app = Flask(__name__)

# Variables de entorno
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
openai.api_key = OPENAI_API_KEY

# Información del café bar
INFO_CAFE = """
HÍBRIDO CAFÉ BAR - Galería, Café y Bar

📍 UBICACIÓN:
Cra. 3 #12-81, La Candelaria, Bogotá
Google Maps: https://maps.app.goo.gl/tu-link

🕐 HORARIOS:
- Lunes a Miércoles: 12:00 PM - 12:00 AM
- Jueves a Sábado: 12:00 PM - 1:00 AM
- Domingo: CERRADO

📞 CONTACTO:
Teléfono/WhatsApp: 311 237 7520
Instagram: @hibridocafebarbogota
Facebook: HibridoCafeBarBogota

💳 MEDIOS DE PAGO:
Aceptamos tarjeta, transferencia, Nequi y QR

✨ SERVICIOS:
- Solo servicio en local
- Reservaciones disponibles (no obligatorias)
- Ambiente acogedor de galería-café-bar

🍷 ESPECIALIDAD:
Nuestro Vino Caliente es el cóctel más apetecido ($28.000)
Vino Tinto, Brandy, Jugo de Naranja y Especias
"""

# Menú organizado por categorías
MENU_CAFE = {
    "cocteles_populares": [
        "🍷 Vino Caliente (ESPECIALIDAD) - $28.000",
        "🍹 Mojito Cubano - $30.000",
        "🍸 Martini - $29.000",
        "🥃 Old Fashioned - $30.000",
        "🍹 Piña Colada - $28.000",
        "🍸 Margarita - $30.000",
        "🍹 Long Island - $45.000"
    ],
    "cervezas": [
        "🍺 Corona - $16.000",
        "🍺 Stella Artois - $16.000",
        "🍺 Club Colombia (Dorada/Roja/Negra) - $11.000",
        "🍺 Póker / Águila - $9.000",
        "🍺 Budweiser - $12.000"
    ],
    "bebidas_sin_alcohol": [
        "🥤 Limonada Natural - $10.000",
        "🥤 Limonada de Coco - $15.000",
        "☕ Granizado de Café - $16.000",
        "🍹 Cócteles sin licor - desde $22.000",
        "🥤 Jugos Naturales - $13.000"
    ],
    "comida": [
        "🥔 Papas de la Casa (tocineta y cheddar) - $32.000",
        "🌮 Nachos (con queso, pico de gallo y frijol) - $30.000",
        "🌭 Chorizada (20 chorizos con papas) - $45.000",
        "🥔 Salchipapas - $24.000",
        "🥟 Empanaditas (6 unidades) - $22.000"
    ],
    "postres_dulces": [
        "🍰 Brownie con Helado - $25.000",
        "🍨 Copa de Helado - $20.000",
        "🍫 Brownie Chip (con granizado) - $30.000",
        "☕ Mokka (café, chocolate, helado) - $25.000"
    ]
}

# Prompt del sistema para el agente
SYSTEM_PROMPT = f"""Eres el asistente virtual de HÍBRIDO CAFÉ BAR en Bogotá, La Candelaria.

Tu personalidad:
- Amable, cálido y profesional
- Entusiasta sobre el café bar
- Conoces TODO sobre el menú, horarios y servicios
- Respondes SIEMPRE en español
- Eres conciso (máximo 3-4 oraciones por respuesta)
- Usas emojis apropiados para hacer las respuestas más amigables

Información del negocio:
{INFO_CAFE}

ESPECIALIDAD DEL LOCAL:
El Vino Caliente es nuestro cóctel estrella y el más pedido por los clientes. Siempre menciónalo cuando alguien pregunte por recomendaciones.

Categorías del menú:
- Cócteles (con licor y sin licor)
- Cervezas nacionales e importadas
- Vinos y licores
- Bebidas sin alcohol
- Comida (picadas, papas, nachos)
- Postres dulces y bebidas especiales

IMPORTANTE:
- Si preguntan por delivery: Solo atendemos en el local
- Si preguntan por horario: Abierto Lu-Mi 12PM-12AM, Ju-Sa 12PM-1AM, Cerrado Domingos
- Si preguntan por reservas: Aceptamos reservas pero no son obligatorias
- Si preguntan precios: Proporciona precios exactos del menú
- Si preguntan ubicación: Cra. 3 #12-81, La Candelaria, Bogotá
- Si preguntan medios de pago: Tarjeta, transferencia, Nequi y QR
- Si preguntan por el vino caliente: Es nuestra ESPECIALIDAD, $28.000

Ejemplos de respuestas:
- "¡Hola! Bienvenido a Híbrido Café Bar 🎨☕ ¿En qué puedo ayudarte?"
- "Te recomiendo nuestro famoso Vino Caliente 🍷 ($28.000), es la especialidad de la casa"
- "Estamos en La Candelaria, Cra. 3 #12-81. Abrimos Lu-Mi 12PM-12AM 🕐"

Siempre sé útil, amigable y promueve el ambiente único de galería-café-bar."""

# Diccionario para almacenar contexto de conversaciones
conversaciones = {}

def obtener_respuesta_ia(mensaje, numero_usuario):
    """
    Usa OpenAI para generar respuestas inteligentes sobre el café bar
    """
    try:
        # Inicializa el historial si es nuevo usuario
        if numero_usuario not in conversaciones:
            conversaciones[numero_usuario] = []
        
        # Agrega el mensaje del usuario
        conversaciones[numero_usuario].append({
            "role": "user",
            "content": mensaje
        })
        
        # Mantiene solo los últimos 8 mensajes
        if len(conversaciones[numero_usuario]) > 8:
            conversaciones[numero_usuario] = conversaciones[numero_usuario][-8:]
        
        # Llama a OpenAI
        respuesta = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT}
            ] + conversaciones[numero_usuario],
            max_tokens=200,
            temperature=0.7
        )
        
        texto_respuesta = respuesta.choices[0].message.content.strip()
        
        # Agrega la respuesta al historial
        conversaciones[numero_usuario].append({
            "role": "assistant",
            "content": texto_respuesta
        })
        
        return texto_respuesta
    
    except Exception as e:
        print(f"Error con OpenAI: {e}")
        return "Disculpa, tengo un problema técnico. Por favor contáctanos al 311 237 7520 📞"

def procesar_comandos_rapidos(mensaje):
    """
    Comandos rápidos sin usar IA para respuestas instantáneas
    """
    mensaje_lower = mensaje.lower().strip()
    
    # Comando: Horarios
    if any(palabra in mensaje_lower for palabra in ["horario", "hora", "abierto", "abren", "cierran"]):
        return """🕐 HORARIOS DE HÍBRIDO CAFÉ BAR:

📅 Lunes a Miércoles: 12:00 PM - 12:00 AM
📅 Jueves a Sábado: 12:00 PM - 1:00 AM
📅 Domingo: CERRADO

¡Te esperamos! 🎨☕"""
    
    # Comando: Ubicación
    if any(palabra in mensaje_lower for palabra in ["ubicacion", "ubicación", "dirección", "direccion", "donde", "dónde", "queda"]):
        return """📍 UBICACIÓN:
Cra. 3 #12-81, La Candelaria, Bogotá

🗺️ Ver en Google Maps:
https://maps.app.goo.gl/tu-link

📞 WhatsApp: 311 237 7520"""
    
    # Comando: Menú o carta
    if any(palabra in mensaje_lower for palabra in ["menu", "menú", "carta", "precio", "cuesta"]):
        return """📋 MENÚ HÍBRIDO CAFÉ BAR:

🍷 CÓCTELES (desde $22.000)
🍺 CERVEZAS (desde $9.000)
🥃 LICORES Y VINOS
🥔 COMIDA (desde $8.000)
🍰 POSTRES Y DULCES

🌟 ESPECIALIDAD: Vino Caliente $28.000

¿Qué categoría te interesa? Puedo darte más detalles 😊"""
    
    # Comando: Vino caliente
    if any(palabra in mensaje_lower for palabra in ["vino caliente", "especialidad", "recomendación", "recomendacion"]):
        return """🍷 ¡VINO CALIENTE - NUESTRA ESPECIALIDAD!

Precio: $28.000

Ingredientes:
• Vino Tinto
• Brandy
• Jugo de Naranja
• Especias secretas

Es nuestro cóctel más apetecido y perfecto para el clima bogotano 🔥

¿Te gustaría reservar mesa? 😊"""
    
    # Comando: Reservas
    if any(palabra in mensaje_lower for palabra in ["reserva", "reservar", "reservación", "mesa"]):
        return """📱 RESERVAS:

Puedes hacer reservación pero NO es obligatoria para ingresar.

Para reservar llama o escribe al:
📞 311 237 7520

Horarios disponibles:
• Lu-Mi: 12PM - 12AM
• Ju-Sa: 12PM - 1AM

¿En qué más puedo ayudarte? 🎨☕"""
    
    # Comando: Medios de pago
    if any(palabra in mensaje_lower for palabra in ["pago", "tarjeta", "efectivo", "nequi", "transferencia"]):
        return """💳 MEDIOS DE PAGO ACEPTADOS:

✅ Tarjeta débito/crédito
✅ Transferencia bancaria
✅ Nequi
✅ Pago por QR

¡Elige el que prefieras! 😊"""
    
    return None

@app.route("/webhook", methods=["POST"])
def webhook():
    """
    Webhook que recibe mensajes de WhatsApp
    """
    try:
        print("=" * 50)
        print("🔔 WEBHOOK RECIBIDO")
        print("=" * 50)
        
        incoming_msg = request.values.get("Body", "").strip()
        sender = request.values.get("From")
        profile_name = request.values.get("ProfileName", "Cliente")
        
        print(f"📥 Mensaje de {profile_name} ({sender}): {incoming_msg}")
        
        if not incoming_msg:
            return "OK", 200
        
        # Primero intenta con comandos rápidos
        respuesta = procesar_comandos_rapidos(incoming_msg)
        
        # Si no hay comando rápido, usa IA
        if not respuesta:
            respuesta = obtener_respuesta_ia(incoming_msg, sender)
        
        print(f"🤖 Respuesta: {respuesta}")
        
        # Envía respuesta por WhatsApp
        client.messages.create(
            body=respuesta,
            from_=TWILIO_WHATSAPP_NUMBER,
            to=sender
        )
        
        print(f"✅ Mensaje enviado exitosamente")
        
        return "OK", 200
    
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return "Error", 500

@app.route("/", methods=["GET"])
def home():
    """
    Página principal para verificar que el bot está activo
    """
    return "✅ Bot de Híbrido Café Bar está activo 🎨☕", 200

@app.route("/stats", methods=["GET"])
def stats():
    """
    Endpoint para ver estadísticas básicas
    """
    return f"📊 Conversaciones activas: {len(conversaciones)}", 200

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)