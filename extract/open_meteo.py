import requests
import logging
from datetime import datetime
import psycopg2
from psycopg2 import OperationalError
from psycopg2.extras import RealDictCursor
# from dotenv import load_dotenv

logger = logging.getLogger(__name__)

logging.basicConfig(
    level=logging.INFO
)

def connect_warehouse_db():

    db_params = {
        "database": "warehouse",
        "user": "admin",
        "password": "8e8p&L5V",
        "host": "localhost",
        "port": 5433
    }

    try:
        conn = psycopg2.connect(**db_params)

        with conn.cursor() as cur:
            cur.execute("SELECT current_database();")
            database = cur.fetchone()
            print(database)

        logging.info("Connected Successfully.")

        return conn
    
    except Exception as e:
        logging.info(f"Error Connecting to Database: {e}")

def create_new_table(query):

    conn = connect_warehouse_db()

    try:
        with conn.cursor() as cur:
            cur.execute(query)
            conn.commit()
            print("New Table created")

    except Exception as e:
        return print(f"Error while creating the table: {e}")

def extract_open_meteo(cities):

    result = []
    for city_name, latitude, longitude in cities:
        air_quality_response = requests.get(url=f'https://air-quality-api.open-meteo.com/v1/air-quality?latitude={latitude}&longitude={longitude}&hourly=dust,uv_index,carbon_dioxide,methane,ozone')
        forecast_response = requests.get(url=f'https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&hourly=temperature_2m,rain')

        data = {
            "city": city_name,
            "extracted_at": datetime.now(),
            "air_quality": air_quality_response.json(),
            "forecast": forecast_response.json(),
        }

        result.append(data)

    return result

cities = [("Ribeirão Preto", -21.1775, -47.8103), ("Maringá", -23.4253, -51.9386), ("Marabá" ,-5.3815, -49.1323)]

query = """CREATE SCHEMA IF NOT EXISTS raw;
        CREATE TABLE IF NOT EXISTS raw.air_quality_open_meteo
        (city TEXT NOT NULL,
        extracted_at DATE NOT NULL,
        air_quality_response JSONB NOT NULL,
        UNIQUE (city, extracted_at));"""

#create_new_table(query=query)
print(extract_open_meteo(cities=cities))