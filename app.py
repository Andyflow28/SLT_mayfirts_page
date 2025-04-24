from flask import Flask, render_template, jsonify
from pymongo import MongoClient, errors # Importa errors para mejor manejo
import datetime
import os
from dotenv import load_dotenv

load_dotenv()


def create_app():    

    # --- Configuración de MongoDB (Asegúrate que sean correctos) ---
    MONGO_URI = os.getenv('MONGO_URI') # Usa variable de entorno o tu URI
    DB_NAME = os.getenv('DB_NAME')         # Nombre de tu base de datos
    COLLECTION_NAME = os.getenv('COLLECTION_NAME')  # Nombre de tu colección
    # --------------------------------

    app = Flask(__name__)

    # --- Conexión a MongoDB ---
    try:
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000) # Timeout corto
        db = client[DB_NAME]
        collection = db[COLLECTION_NAME]
        # Prueba la conexión
        client.admin.command('ping')
        print("¡Conexión a MongoDB exitosa!")
    except errors.ConnectionFailure as e:
        print(f"Error: No se pudo conectar a MongoDB en {MONGO_URI}. Verifica que esté corriendo. Detalle: {e}")
        client = None
        collection = None
    except Exception as e:
        print(f"Error inesperado al conectar a MongoDB: {e}")
        client = None
        collection = None
    # ------------------------

    # Función para obtener icono (sin cambios)
    def get_weather_icon(description="Parcialmente Nublado"):
        description_lower = description.lower()
        if "soleado" in description_lower or "despejado" in description_lower:
            return "fas fa-sun"
        elif "nublado" in description_lower or "nubes" in description_lower:
            if "parcialmente" in description_lower:
                return "fas fa-cloud-sun"
            else:
                return "fas fa-cloud"
        elif "lluvia" in description_lower or "llovizna" in description_lower:
            return "fas fa-cloud-showers-heavy"
        elif "tormenta" in description_lower:
            return "fas fa-bolt"
        elif "nieve" in description_lower:
            return "fas fa-snowflake"
        else:
            return "fas fa-smog"

    # --- Ruta Principal (Carga Inicial) ---
    @app.route('/')
    def index():
        latest_reading = None
        temperature = "N/A"
        humidity = "N/A"
        wind_speed = "N/A" # Mantenemos viento estático si no está en BD
        reading_timestamp_str = "No disponible"
        description = "Condición Actual" # Descripción por defecto

        if collection is not None:
            try:
                # Busca el documento más reciente usando el campo 'PC_Timestamp'
                # Asume que el formato string permite ordenamiento correcto (YYYY-MM-DD HH:MM:SS)
                latest_reading = collection.find_one(
                    filter={},
                    sort=[('PC_Timestamp', -1)] # Ordenar por PC_Timestamp descendente
                )
            except Exception as e:
                print(f"Error al consultar MongoDB en index: {e}")

        if latest_reading:
            # --- Usa los nombres de campo EXACTOS de tu BD ---
            temperature = latest_reading.get('Temperature_C', 'Error')
            humidity = latest_reading.get('Humidity_rH', 'N/A') # Lee humedad de la BD
            # Presión (si la quieres mostrar, añádela al HTML)
            # pressure = latest_reading.get('Pressure_hPa', 'N/A')

            # Obtiene el timestamp como string directamente
            reading_timestamp_str = latest_reading.get('PC_Timestamp', "Timestamp inválido")

            # Puedes intentar una descripción basada en la temperatura (ejemplo simple)
            if isinstance(temperature, (int, float)):
                if temperature > 26:
                    description = "Caluroso"
                elif temperature < 20:
                    description = "Fresco"
                else:
                    description = "Templado"
            else:
                description = "Condición Desconocida"


        # Prepara los datos para la plantilla
        weather_data = {
            'location': 'Ejido, Mérida, Venezuela',
            'temperature': temperature,       # Dato de BD
            'description': description,       # Descripción (puede ser de BD o calculada)
            'humidity': humidity,             # Dato de BD
            'wind_speed': wind_speed,         # Dato estático (o de BD si lo tuvieras)
            'timestamp': reading_timestamp_str, # Timestamp (string) de BD
            'icon_class': get_weather_icon(description) # Icono basado en descripción
        }

        return render_template('index.html', weather=weather_data)

    # --- Ruta API para obtener la última lectura ---
    @app.route('/api/latest_reading')
    def get_latest_reading_api():
        latest_reading_data = {
            'temperature': None,
            'humidity': None,
            'timestamp': None,
            'error': None
            }
        
        while True:

            if collection is not None:
                try:
                    # Busca el documento más reciente por PC_Timestamp
                    latest_doc = collection.find_one(sort=[('PC_Timestamp', -1)])
                    if latest_doc:
                        # --- Usa los nombres de campo EXACTOS ---
                        latest_reading_data['temperature'] = latest_doc.get('Temperature_C')
                        latest_reading_data['humidity'] = latest_doc.get('Humidity_rH') # Devuelve también humedad
                        latest_reading_data['timestamp'] = latest_doc.get('PC_Timestamp') # Devuelve el string
                    else:
                        latest_reading_data['error'] = "No se encontraron lecturas."
                except Exception as e:
                    print(f"Error al consultar MongoDB en API: {e}")
                    latest_reading_data['error'] = f"Error de servidor al consultar datos: {e}"
            else:
                latest_reading_data['error'] = "Conexión a base de datos no disponible."

            return jsonify(latest_reading_data)
        
            time.sleep(2)
    return app
# -------------------------------------------------------

if __name__ == '__main__':
    app.create_app()
    app.run(debug=True)