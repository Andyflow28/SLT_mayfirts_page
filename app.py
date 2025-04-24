from flask import Flask, render_template
import datetime
import random # Solo para variar el icono de ejemplo

app = Flask(__name__)

def get_weather_icon(description):
    description_lower = description.lower()
    if "soleado" in description_lower or "despejado" in description_lower:
        return "fas fa-sun" # Icono de sol
    elif "nublado" in description_lower or "nubes" in description_lower:
        if "parcialmente" in description_lower:
            return "fas fa-cloud-sun" # Nubes y sol
        else:
            return "fas fa-cloud" # Nube
    elif "lluvia" in description_lower or "llovizna" in description_lower:
        return "fas fa-cloud-showers-heavy" # Lluvia fuerte
    elif "tormenta" in description_lower:
        return "fas fa-bolt" # Tormenta (rayo)
    elif "nieve" in description_lower:
        return "fas fa-snowflake" # Nieve
    else:
        return "fas fa-smog" # Icono genérico (niebla/bruma)

@app.route('/')
def index():
    current_time = datetime.datetime.now()
    descriptions = ['Parcialmente Nublado', 'Soleado', 'Mayormente Nublado', 'Lluvioso', 'Tormenta Eléctrica']
    selected_description = random.choice(descriptions)
    weather_data = {
        'location': 'Ejido, Mérida, Venezuela',
        'temperature': random.randint(18, 28),
        'description': selected_description,
        'humidity': random.randint(60, 90),
        'wind_speed': random.randint(5, 20),
        'timestamp': current_time.strftime("%d de %B, %Y a las %I:%M %p"),
        'icon_class': get_weather_icon(selected_description)
    }
    return render_template('index.html', weather=weather_data)

if __name__ == '__main__':
    app.run(debug=True)