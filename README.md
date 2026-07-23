# Data Pipeline

An end-to-end pipeline that ingests weather and air quality data, transforms it, and surfaces it in a BI dashboard, built to demonstrate orchestration, data modeling, and containerized deployment.

## What it does

1. **Extract**: pulls forecast and air-quality data from the [Open-Meteo](https://open-meteo.com/) API for a configurable list of cities.
2. **Load**: lands raw data in a `raw` schema in Postgres, idempotently per run date so backfills are safe.
3. **Orchestrate**: an Airflow DAG dynamically fans the extract step out over the city list, then hands off to dbt.
4. **Transform**: dbt models move data through staging → intermediate → marts layers (daily weather/air-quality summaries per city, a combined comfort index), with tests enforcing data quality. dbt runs as individual Airflow tasks via [Astronomer Cosmos](https://astronomer.github.io/astronomer-cosmos/).
5. **Report** :[Metabase](https://www.metabase.com/) connects to the marts schema for dashboards.

## Stack

- **Docker Compose** — runs every service (Airflow, warehouse Postgres, Metabase) locally
- **Python** — extraction/load scripts
- **Airflow** — scheduling, retries, dynamic task mapping, backfills
- **dbt** — data modeling and testing
- **Postgres** — analytics warehouse
- **Metabase** — dashboards

## Status

Work in progress, built incrementally milestone by milestone:

- [ ] Docker Compose base (Airflow + warehouse Postgres)
- [ ] Extraction script (raw layer)
- [ ] Airflow DAG — extract & load
- [ ] dbt staging layer
- [ ] dbt marts + tests
- [ ] Cosmos integration
- [ ] Metabase reporting
- [ ] End-to-end verification

## Running locally

```bash
docker compose up
```

Airflow UI: `localhost:8080`
Metabase: `localhost:3000` (once added)
