from flask import Flask, request
from twilio.rest import Client
import os
from datetime import datetime
import re

app = Flask(__name__)

# Variables de entorno
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER")

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# Información del café bar
INFO_BASICA = {
    "nombre": "Híbrido Café Bar",
    "direccion": "Cra. 3 #12-81, La Candelaria, Bogotá",
    "telefono": "311 237 7520",
    "instagram": "@hibridocafebarbogota",
    "facebook": "HibridoCafeBarBogota",
}

HORARIOS = """🕐 HORARIOS DE HÍBRIDO CAFÉ BAR:

📅 Lunes a Miércoles: 12:00 PM - 12:00 AM
📅 Jueves a Sábado: 12:00 PM - 1:00 AM
📅 Domingo: CERRADO

¡Te esperamos! 🎨☕"""

UBICACION = """📍 UBICACIÓN:
Cra. 3 #12-81, La Candelaria, Bogotá

🗺️ Estamos en pleno corazón de La Candelaria

📞 WhatsApp: 311 237 7520
📱 Instagram: @hibridocafebarbogota"""

MENU_PRINCIPAL = """📋 MENÚ HÍBRIDO CAFÉ BAR:

🍷 CÓCTELES CON LICOR
🍹 CÓCTELES SIN LICOR
🍺 CERVEZAS
🥃 LICORES Y VINOS
🍔 COMIDA Y PICADAS
🍰 POSTRES Y DULCES

🌟 ESPECIALIDAD: Vino Caliente $28.000

Escribe el número o nombre de la categoría que te interesa. Ejemplo: "cócteles" o "comida" 😊"""

# Menú detallado por categorías
COCTELES_POPULARES = """🍷 CÓCTELES POPULARES:

⭐ Vino Caliente (ESPECIALIDAD) - $28.000
   Vino Tinto, Brandy, Jugo de Naranja, Especias
   
🍹 Mojito Cubano - $30.000
🍸 Martini Clásico - $29.000
🍹 Piña Colada - $28.000
🍸 Margarita - $30.000
🥃 Old Fashioned - $30.000
🍹 Daiquirí - $28.000
🍸 Cosmopolitan - $30.000
🍹 Cuba Libre - $32.000
🍹 Long Island - $45.000

💡 Te recomendamos nuestro Vino Caliente, ¡es el favorito de nuestros clientes!"""

COCTELES_SIN_LICOR = """🍹 CÓCTELES SIN LICOR:

🍓 Primavera - $22.000
   Leche Helada, Chocolate, Granadina
   
🍋 Limonana - $22.000
   Limón, Hierbabuena, Hielo Frappé
   
☕ Dálmata - $22.000
   Café Helado, Leche, Chocolate
   
🥭 Híbrido - $25.000
   Naranja, Mango, Helado, Granadina
   
🍊 Amanecer - $22.000
   Naranja, Fresa, Manzana
   
🍏 Clorofila - $22.000
   Manzana, Kiwi, Granadina

¡Perfectos para cualquier momento del día! 😊"""

CERVEZAS = """🍺 CERVEZAS:

🍺 Corona - $16.000
🍺 Stella Artois - $16.000
🍺 Club Colombia (Dorada/Roja/Negra) - $11.000
🍺 Budweiser - $12.000
🍺 Póker - $9.000
🍺 Águila - $9.000
🍺 Smirnoff Ice - $19.000

🍻 Todas nuestras cervezas vienen bien frías!"""

COMIDA = """🍔 COMIDA Y PICADAS:

🥔 Papas de la Casa - $32.000
   Con tocineta y queso cheddar
   
🌮 Nachos - $30.000
   Con queso cheddar, pico de gallo y frijol
   
🌭 Chorizada - $45.000
   20 Chorizos con papas y ají
   
🥔 Salchipapas - $24.000
   
🥟 Empanaditas - $22.000
   6 unidades papa/carne con ají
   
🥔 Papas a la Francesa - $15.000

🥜 Porción de Maní - $8.000
   Salado o picante

¡Perfecto para compartir! 🎉"""

POSTRES = """🍰 POSTRES Y DULCES:

🍫 Brownie con Helado - $25.000

🍨 Copa de Helado - $20.000
   Helado de vainilla con chocolate
   
🍫 Brownie Chip - $30.000
   Granizado de café, brownie, whisky, helado
   
☕ Mokka - $25.000
   Café granizado, chocolate, helado, brandy
   
🍦 Malteada - $17.000
   Vainilla, chocolate o café

😋 ¡El final perfecto para tu visita!"""

BEBIDAS = """🥤 BEBIDAS SIN ALCOHOL:

🍋 Limonada Natural - $10.000
🥥 Limonada de Coco - $15.000
🌿 Limonada de Hierbabuena - $12.000
🍒 Limonada Cerezada - $14.000
🍊 Naranjada - $12.000

☕ Granizado de Café - $16.000
🍹 Granizados de Frutas - $20.000
🧃 Jugos Naturales en Agua - $13.000
🥛 Jugos Naturales en Leche - $17.000

🥤 Gaseosas - desde $6.000"""

LICORES = """🥃 LICORES Y VINOS:

WHISKY:
🥃 Buchanan's 12 años - Copa $38.000
🥃 Chivas 12 años - Copa $33.000
🥃 Old Parr - Copa $36.000
🥃 Jack Daniel's - Copa $32.000

RON:
🍹 Bacardi - Trago $22.000
🍹 Habana Club - Trago $28.000

VINOS:
🍷 Casillero del Diablo - Copa $26.000
🍷 Santa Rita - Copa $26.000
🍷 Gato Negro - Copa $25.000

OTROS:
🍸 Baileys - Copa $28.000
🍸 Tequila José Cuervo - Trago $26.000
🍸 Vodka Absolut - Trago $30.000

También vendemos botellas! 🍾"""

RESERVAS = """📱 RESERVAS:

✅ Aceptamos reservas
✅ NO son obligatorias para ingresar

Para reservar:
📞 Llama o escribe al: 311 237 7520

Horarios disponibles:
• Lunes a Miércoles: 12PM - 12AM
• Jueves a Sábado: 12PM - 1AM

💡 Tip: Los fines de semana hay más gente, ¡reserva con anticipación!"""

MEDIOS_PAGO = """💳 MEDIOS DE PAGO:

✅ Tarjeta débito/crédito
✅ Transferencia bancaria
✅ Nequi
✅ Pago por QR

¡Elige el que prefieras! 😊"""

# Almacena el contexto de cada usuario
contexto_usuarios = {}

def normalizar_texto(texto):
    """Normaliza el texto para buscar coincidencias"""
    texto = texto.lower().strip()
    # Reemplaza acentos
    reemplazos = {'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u', 'ñ': 'n'}
    for a, b in reemplazos.items():
        texto = texto.replace(a, b)
    return texto

def procesar_mensaje(mensaje, numero_usuario):
    """
    Procesa el mensaje y devuelve una respuesta inteligente
    """
    mensaje_norm = normalizar_texto(mensaje)
    
    # Saludo inicial
    if any(palabra in mensaje_norm for palabra in ['hola', 'buenas', 'buenos dias', 'buenas tardes', 'buenas noches', 'hey', 'ola']):
        contexto_usuarios[numero_usuario] = 'saludado'
        return f"""¡Hola! Bienvenido a Híbrido Café Bar 🎨☕

Somos una galería-café-bar en La Candelaria, Bogotá.

¿En qué puedo ayudarte?
• Horarios
• Ubicación
• Menú / Carta
• Precios
• Reservas
• Medios de pago

O escribe tu pregunta libremente 😊"""

    # Horarios
    if any(palabra in mensaje_norm for palabra in ['horario', 'hora', 'abierto', 'abren', 'cierran', 'cerrado', 'cuando']):
        return HORARIOS

    # Ubicación
    if any(palabra in mensaje_norm for palabra in ['ubicacion', 'direccion', 'donde', 'queda', 'ubicado', 'como llegar', 'llego']):
        return UBICACION

    # Menú general
    if any(palabra in mensaje_norm for palabra in ['menu', 'carta', 'que tienen', 'que venden', 'que hay']):
        contexto_usuarios[numero_usuario] = 'menu'
        return MENU_PRINCIPAL

    # Cócteles con licor
    if any(palabra in mensaje_norm for palabra in ['coctel', 'cocteles', 'cocktail', 'tragos', 'bebidas alcoholicas']):
        return COCTELES_POPULARES

    # Vino caliente (especialidad)
    if any(palabra in mensaje_norm for palabra in ['vino caliente', 'especialidad', 'recomendacion', 'recomienda', 'mejor', 'famoso', 'popular']):
        return """🍷 ¡VINO CALIENTE - NUESTRA ESPECIALIDAD!

Precio: $28.000

Ingredientes:
• Vino Tinto
• Brandy
• Jugo de Naranja
• Especias secretas 🌟

Es nuestro cóctel MÁS APETECIDO y perfecto para el clima bogotano. Los clientes lo aman! 🔥

¿Te gustaría saber algo más del menú? 😊"""

    # Cócteles sin licor
    if any(palabra in mensaje_norm for palabra in ['sin licor', 'sin alcohol', 'mocktail', 'no alcoholico']):
        return COCTELES_SIN_LICOR

    # Cervezas
    if any(palabra in mensaje_norm for palabra in ['cerveza', 'birra', 'beer']):
        return CERVEZAS

    # Comida
    if any(palabra in mensaje_norm for palabra in ['comida', 'comer', 'papas', 'nachos', 'picada', 'hamburguesa', 'sandwich']):
        return COMIDA

    # Postres
    if any(palabra in mensaje_norm for palabra in ['postre', 'dulce', 'brownie', 'helado', 'malteada']):
        return POSTRES

    # Bebidas sin alcohol
    if any(palabra in mensaje_norm for palabra in ['limonada', 'jugo', 'bebida', 'refresco', 'gaseosa', 'granizado']):
        return BEBIDAS

    # Licores y vinos
    if any(palabra in mensaje_norm for palabra in ['whisky', 'whiskey', 'ron', 'vino', 'vodka', 'tequila', 'licor', 'botella']):
        return LICORES

    # Precios específicos
    if 'precio' in mensaje_norm or 'cuesta' in mensaje_norm or 'cuanto' in mensaje_norm or 'valor' in mensaje_norm:
        # Si menciona algo específico, busca en el menú
        if 'mojito' in mensaje_norm:
            return "🍹 Mojito Cubano: $30.000\n\n¿Algo más que quieras saber? 😊"
        elif 'cerveza' in mensaje_norm or 'beer' in mensaje_norm:
            return CERVEZAS
        else:
            return MENU_PRINCIPAL

    # Reservas
    if any(palabra in mensaje_norm for palabra in ['reserva', 'reservar', 'reservacion', 'mesa', 'apartar']):
        return RESERVAS

    # Medios de pago
    if any(palabra in mensaje_norm for palabra in ['pago', 'tarjeta', 'efectivo', 'nequi', 'transferencia', 'pagar', 'qr']):
        return MEDIOS_PAGO

    # Delivery
    if any(palabra in mensaje_norm for palabra in ['delivery', 'domicilio', 'llevar', 'envio', 'entregan']):
        return """🏠 SERVICIO:

Por el momento solo atendemos EN EL LOCAL.

Pero vale la pena visitarnos! Tenemos un ambiente único de galería-café-bar en pleno corazón de La Candelaria 🎨☕

📍 Cra. 3 #12-81, La Candelaria
📞 311 237 7520"""

    # Contacto / Teléfono
    if any(palabra in mensaje_norm for palabra in ['contacto', 'telefono', 'numero', 'llamar', 'whatsapp']):
        return f"""📞 CONTACTO:

Teléfono/WhatsApp: 311 237 7520

📱 Redes Sociales:
Instagram: @hibridocafebarbogota
Facebook: HibridoCafeBarBogota

¡Síguenos para estar al día con eventos especiales! 🎉"""

    # Gracias / Despedida
    if any(palabra in mensaje_norm for palabra in ['gracias', 'graciass', 'thanks', 'chao', 'adios', 'bye']):
        return """¡De nada! Fue un placer ayudarte 😊

Recuerda:
📍 Cra. 3 #12-81, La Candelaria
🕐 Lu-Mi: 12PM-12AM | Ju-Sa: 12PM-1AM
📞 311 237 7520

¡Te esperamos en Híbrido Café Bar! 🎨☕🍷"""

    # Respuesta por defecto
    return """No estoy seguro de entender. Puedo ayudarte con:

🕐 Horarios
📍 Ubicación
📋 Menú / Carta
💰 Precios
📱 Reservas
💳 Medios de pago
🍷 Nuestra especialidad (Vino Caliente)

Escribe lo que necesites saber 😊"""

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
        
        # Procesa el mensaje
        respuesta = procesar_mensaje(incoming_msg, sender)
        
        print(f"🤖 Respuesta: {respuesta[:100]}...")
        
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
    Página principal
    """
    return "✅ Bot de Híbrido Café Bar está activo 🎨☕", 200

@app.route("/stats", methods=["GET"])
def stats():
    """
    Estadísticas básicas
    """
    return f"📊 Usuarios únicos: {len(contexto_usuarios)}", 200

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
