import datetime
from airflow.sdk import dag, task
from extract.open_meteo import extract_open_meteo, build_rows, ingest_data
from cosmos import DbtTaskGroup, ProjectConfig, ProfileConfig, ExecutionConfig, ExecutionMode
from cosmos.profiles import PostgresUserPasswordProfileMapping


cities = [("Ribeirão Preto", -21.1775, -47.8103), ("Maringá", -23.4253, -51.9386), ("Marabá" ,-5.3815, -49.1323)]

@dag(start_date=datetime.datetime(2021, 1, 1), schedule="@daily")
def pipeline():

    @task(retries=3, retry_delay=datetime.timedelta(minutes=2))
    def extract_task(city, logical_date=None):
        return extract_open_meteo(cities=city, run_date=logical_date.date())

    @task
    def build_rows_task(data, response):
        return build_rows(data=data, response_key=response)

    @task
    def ingest_task(rows, table_name, columns):
        return ingest_data(rows=rows, table_name=table_name, columns=columns)

    dbt_tg = DbtTaskGroup(
        group_id="dbt_task_group",
        project_config=ProjectConfig("/opt/airflow/dbt/datapipeline/"),
        profile_config=ProfileConfig(
            profile_name="datapipeline",
            target_name="dev",
            profile_mapping=PostgresUserPasswordProfileMapping(
                conn_id="warehousedb",
                profile_args={"schema": "public"},
            )
        ),
        execution_config=ExecutionConfig(
            execution_mode=ExecutionMode.LOCAL,
        ),
    )

    data = extract_task.expand(city=cities)

    air_quality_rows = build_rows_task(data, "air_quality")
    forecast_rows = build_rows_task(data, "forecast")

    air_quality_ingest = ingest_task(air_quality_rows, "raw.air_quality_open_meteo", ["city", "extracted_at", "air_quality_response"])
    forecast_ingest = ingest_task(forecast_rows, "raw.forecast_open_meteo", ["city", "extracted_at", "forecast_response"])

    [air_quality_ingest, forecast_ingest] >> dbt_tg

pipeline()