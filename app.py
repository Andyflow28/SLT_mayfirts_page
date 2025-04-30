from flask import Flask, render_template, jsonify
from pymongo import MongoClient, errors
import datetime
import os
from dotenv import load_dotenv

load_dotenv()

def create_app():
    # --- Configuración de MongoDB (DEBEN SER CORRECTOS) ---
    MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
    DB_NAME = os.getenv('DB_NAME', 'weatherdb')
    COLLECTION_NAME = os.getenv('COLLECTION_NAME', 'readings')
    # --------------------------------

    app = Flask(__name__)

    # --- Conexión a MongoDB ---
    try:
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        db = client[DB_NAME]
        collection = db[COLLECTION_NAME]
        client.admin.command('ping')
        print("¡Conexión a MongoDB exitosa!")
    except errors.ConnectionFailure as e:
        print(f"Error: No se pudo conectar a MongoDB. Detalle: {e}")
        client = None
        collection = None
    except Exception as e:
        print(f"Error inesperado al conectar a MongoDB: {e}")
        client = None
        collection = None
    # ------------------------

    # Función para obtener icono (basado en temperatura ahora)
    def get_weather_icon(temperature):
        if not isinstance(temperature, (int, float)):
            return "fas fa-question-circle" # Icono de interrogación si no hay temp

        if temperature > 28:
            return "fas fa-sun" # Caluroso
        elif temperature > 22:
            return "fas fa-cloud-sun" # Templado / Parcialmente Nublado
        elif temperature < 18:
             return "fas fa-snowflake" # Fresco (ejemplo, podría ser nube)
        else:
            return "fas fa-cloud" # Nublado / Normal

    # --- Ruta Principal (Carga Inicial) ---
    @app.route('/')
    def index():
        latest_reading = None
        temperature = "N/A"
        humidity = "N/A"
        pressure = "N/A" # Variable para presión
        wind_speed = "N/A" # Mantenemos viento estático si no está en BD
        reading_timestamp_str = "No disponible"
        icon_class = "fas fa-question-circle" # Icono por defecto

        if collection is not None:
            try:
                latest_reading = collection.find_one(
                    filter={},
                    sort=[('PC_Timestamp', -1)]
                )
            except Exception as e:
                print(f"Error al consultar MongoDB en index: {e}")

        if latest_reading:
            temperature = latest_reading.get('Temperature_C', 'Error')
            humidity = latest_reading.get('Humidity_rH', 'N/A')
            pressure = latest_reading.get('Pressure_hPa', 'N/A') # *** Lee Presión ***
            reading_timestamp_str = latest_reading.get('PC_Timestamp', "Inválido")
            icon_class = get_weather_icon(temperature) # Icono basado en temp

        weather_data = {
            'location': 'Mérida, Venezuela - Café La Rama Dorada',
            'temperature': temperature,
            'humidity': humidity,
            'pressure': pressure, # *** Pasa Presión a la plantilla ***
            'wind_speed': wind_speed, # Se mantiene pero no se mostrará prominentemente
            'timestamp': reading_timestamp_str,
            'icon_class': icon_class
            # 'description' ya no se usa prominentemente
        }

        return render_template('index.html', weather=weather_data)

    # --- Ruta API para obtener la última lectura ---
    @app.route('/api/latest_reading')
    def get_latest_reading_api():
        latest_reading_data = {
            'temperature': None,
            'humidity': None,
            'pressure': None, # *** Añadido campo para presión ***
            'timestamp': None,
            'icon_class': "fas fa-question-circle", # Icono por defecto API
            'error': None
            }

        if collection is not None:
            try:
                latest_doc = collection.find_one(sort=[('PC_Timestamp', -1)])
                if latest_doc:
                    temp = latest_doc.get('Temperature_C')
                    latest_reading_data['temperature'] = temp
                    latest_reading_data['humidity'] = latest_doc.get('Humidity_rH')
                    latest_reading_data['pressure'] = latest_doc.get('Pressure_hPa') # *** Devuelve Presión ***
                    latest_reading_data['timestamp'] = latest_doc.get('PC_Timestamp')
                    latest_reading_data['icon_class'] = get_weather_icon(temp) # *** Devuelve Icono ***
                else:
                    latest_reading_data['error'] = "No se encontraron lecturas."
            except Exception as e:
                print(f"Error al consultar MongoDB en API: {e}")
                latest_reading_data['error'] = f"Error de servidor: {e}"
        else:
            latest_reading_data['error'] = "Conexión a BD no disponible."

        return jsonify(latest_reading_data)

    return app

# --- Modificación para ejecutar con create_app ---
# Elimina las líneas app.create_app() y app.run() si usas un runner como Gunicorn/Waitress
# Si ejecutas directamente con 'python app.py', necesitas crear la app y correrla:
if __name__ == '__main__':
    app_instance = create_app()
    # host='0.0.0.0' permite acceso desde otros dispositivos en la red local
    app_instance.run(debug=True)
# --------------------------------------------------