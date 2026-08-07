import datetime
from airflow.sdk import dag, task
from extract.open_meteo import extract_open_meteo, build_rows, ingest_data

cities = [("Ribeirão Preto", -21.1775, -47.8103), ("Maringá", -23.4253, -51.9386), ("Marabá" ,-5.3815, -49.1323)]

@dag(start_date=datetime.datetime(2021, 1, 1), schedule="@daily")
def pipeline():

    @task
    def extract_task(cities, logical_date=None):
        return extract_open_meteo(cities=cities, run_date=logical_date.date())

    @task
    def build_rows_task(data, response):
        return build_rows(data=data, response_key=response)

    @task
    def ingest_task(rows, table_name, columns):
        return ingest_data(rows=rows, table_name=table_name, columns=columns)

    data = extract_task(cities)

    air_quality_rows = build_rows_task(data, "air_quality")
    forecast_rows = build_rows_task(data, "forecast")

    ingest_task(air_quality_rows, "raw.air_quality_open_meteo", ["city", "extracted_at", "air_quality_response"])
    ingest_task(forecast_rows, "raw.forecast_open_meteo", ["city", "extracted_at", "forecast_response"])


pipeline()