from flask import Flask, render_template
import datetime
import random # Solo para variar el icono de ejemplo

# Inicializar la aplicación Flask
app = Flask(__name__)

# Función simple para obtener un icono basado en la descripción (Ejemplo)
def get_weather_icon(description):
    description_lower = description.lower()
    if "soleado" in description_lower or "despejado" in description_lower:
        return "fas fa-sun" # Icono de sol
    elif "nublado" in description_lower or "nubes" in description_lower:
        # Diferenciar entre parcialmente nublado y mayormente nublado
        if "parcialmente" in description_lower:
            return "fas fa-cloud-sun" # Nubes y sol
        else:
            return "fas fa-cloud" # Nube
    elif "lluvia" in description_lower or "llovizna" in description_lower:
        return "fas fa-cloud-showers-heavy" # Lluvia fuerte
    elif "tormenta" in description_lower:
        return "fas fa-poo-storm" # Tormenta (icono de ejemplo)
    elif "nieve" in description_lower:
        return "fas fa-snowflake" # Nieve
    else:
        # Icono por defecto si no coincide
        return "fas fa-smog" # Un icono genérico

# Ruta principal de la aplicación
@app.route('/')
def index():
    # --- DATOS DE EJEMPLO ---
    current_time = datetime.datetime.now()
    # Variedad de descripciones para probar iconos
    descriptions = ['Parcialmente Nublado', 'Soleado', 'Mayormente Nublado', 'Lluvioso']
    selected_description = random.choice(descriptions)

    weather_data = {
        'location': 'Ejido, Mérida, Venezuela',
        'temperature': random.randint(18, 28), # Temperatura aleatoria para ejemplo
        'description': selected_description,
        'humidity': random.randint(60, 90),     # Humedad aleatoria
        'wind_speed': random.randint(5, 20),   # Viento aleatorio
        'timestamp': current_time.strftime("%d de %B, %Y a las %I:%M %p"),
        # Obtenemos el icono basado en la descripción
        'icon_class': get_weather_icon(selected_description)
    }
    # ------------------------

    return render_template('index.html', weather=weather_data)

if __name__ == '__main__':
    app.run(debug=True)