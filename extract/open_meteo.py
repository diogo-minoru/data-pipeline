import requests
import logging
import psycopg2
from psycopg2.extras import execute_values, Json
from datetime import datetime
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

def extract_open_meteo(cities, run_date):

    result = []
    for city_name, latitude, longitude in cities:
        air_quality_response = requests.get(url=f'https://air-quality-api.open-meteo.com/v1/air-quality?latitude={latitude}&longitude={longitude}&hourly=dust,uv_index,carbon_dioxide,methane,ozone')
        forecast_response = requests.get(url=f'https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&hourly=temperature_2m,rain')

        data = {
            "city": city_name,
            "extracted_at": run_date,
            "air_quality": air_quality_response.json(),
            "forecast": forecast_response.json(),
        }

        result.append(data)

    return result


def build_rows(data, response_key):
    return [(d["city"], d["extracted_at"], Json(d[response_key])) for d in data]


def ingest_data(rows, table_name, columns):

    conn = connect_warehouse_db()

    try:
        with conn.cursor() as cur:
            cols = ", ".join(columns)
            query = f"INSERT INTO {table_name} ({cols}) VALUES %s ON CONFLICT (city, extracted_at) DO UPDATE SET {columns[-1]} = EXCLUDED.{columns[-1]};"
            execute_values(cur, query, rows)
        conn.commit()
        return logging.info("Data ingested successfully.")
    except Exception as e:
        return logging.error(f"Error while ingesting: {e}")
    finally:
        conn.close()
    

cities = [("Ribeirão Preto", -21.1775, -47.8103), ("Maringá", -23.4253, -51.9386), ("Marabá" ,-5.3815, -49.1323)]

query1 = """CREATE SCHEMA IF NOT EXISTS raw;
        CREATE TABLE IF NOT EXISTS raw.air_quality_open_meteo
        (city TEXT NOT NULL,
        extracted_at DATE NOT NULL,
        air_quality_response JSONB NOT NULL,
        CONSTRAINT air_quality_city_extracted_at UNIQUE (city, extracted_at));"""

query2 = """CREATE SCHEMA IF NOT EXISTS raw;
        CREATE TABLE IF NOT EXISTS raw.forecast_open_meteo
        (city TEXT NOT NULL,
        extracted_at DATE NOT NULL,
        forecast_response JSONB NOT NULL,
        CONSTRAINT forecast_city_extracted_at UNIQUE (city, extracted_at));"""

create_new_table(query=query1)
create_new_table(query=query2)
data = extract_open_meteo(cities=cities, run_date=datetime.strptime('2026-07-29', "%Y-%m-%d").date())

air_quality_rows = build_rows(data, "air_quality")
forecast_rows = build_rows(data, "forecast")

ingest_data(air_quality_rows, "raw.air_quality_open_meteo", ["city", "extracted_at", "air_quality_response"])
ingest_data(forecast_rows, "raw.forecast_open_meteo", ["city", "extracted_at", "forecast_response"])