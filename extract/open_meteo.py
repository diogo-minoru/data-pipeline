import requests
import logging
import psycopg2
from psycopg2.extras import execute_values, Json

logger = logging.getLogger(__name__)

logging.basicConfig(
    level=logging.INFO
)

def connect_warehouse_db():

    db_params = {
        "database": "warehouse",
        "user": "admin",
        "password": "8e8p&L5V",
        "host": "warehouse-db",
        "port": 5432
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
        raise e

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
    city_name, latitude, longitude = cities
    
    air_quality_response = requests.get(url=f'https://air-quality-api.open-meteo.com/v1/air-quality?latitude={latitude}&longitude={longitude}&hourly=dust,uv_index,carbon_dioxide,methane,ozone')
    forecast_response = requests.get(url=f'https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&hourly=temperature_2m,rain')

    data = {
        "city": city_name,
        "extracted_at": run_date,
        "air_quality": air_quality_response.json(),
        "forecast": forecast_response.json(),
    }

    return data


def build_rows(data, response_key):
    return [(d["city"], d["extracted_at"], d[response_key]) for d in data]


def ingest_data(rows, table_name, columns):

    conn = connect_warehouse_db()
    
    try:
        with conn.cursor() as cur:
            cols = ", ".join(columns)
            wrapped_rows = [(city, extracted_at, Json(response)) for city, extracted_at, response in rows]
            query = f"INSERT INTO {table_name} ({cols}) VALUES %s ON CONFLICT (city, extracted_at) DO UPDATE SET {columns[-1]} = EXCLUDED.{columns[-1]};"
            execute_values(cur, query, wrapped_rows)
        conn.commit()
        return logging.info("Data ingested successfully.")
    except Exception as e:
        return logging.error(f"Error while ingesting: {e}")
    finally:
        conn.close()