# Data Engineering Sales Pipeline

This repository contains a local streaming sales pipeline built with Python, Kafka, PostgreSQL, and dbt.

## Architecture

```text
Python Producer -> Kafka Topic -> Python Consumer -> PostgreSQL raw_sales -> dbt models
```

## Repository Layout

```text
.
├── consumer.py
├── dbt_sales/
│   ├── dbt_project.yml
│   ├── models/
│   │   ├── marts/daily_sales.sql
│   │   └── staging/stg_sales.sql
│   └── profiles.yml
├── docker-compose.yml
├── init.sql
├── pyproject.toml
├── producer.py
└── .gitignore
```

## Components

- `producer.py` generates mock sales events and publishes them to Kafka.
- `consumer.py` reads Kafka events and upserts them into PostgreSQL.
- `init.sql` creates the raw ingestion table.
- `dbt_sales` transforms raw sales records into an analytics-ready daily sales mart.
- `docker-compose.yml` provisions Zookeeper, Kafka, and PostgreSQL locally.

## Prerequisites

- Docker Desktop
- `uv`
- Python 3.10+

## Local Ports

- Kafka: `9092`
- PostgreSQL (Docker): `5433`

This project maps PostgreSQL to `5433` on the host to avoid conflicts with a locally installed Postgres server on `5432`.

## Setup

1. Create the virtual environment and install dependencies:

   ```bash
   uv sync
   ```

2. Start infrastructure:

   ```bash
   docker compose up -d
   ```

3. Create the Kafka topic:

   ```bash
   docker exec -it sales-kafka kafka-topics --create --topic sales_topic --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1
   ```

## Run the Pipeline

Start the producer:

```bash
uv run producer.py
```

Start the consumer in a second terminal:

```bash
uv run consumer.py
```

## Verify Ingestion

Check that records are landing in PostgreSQL:

```bash
docker exec -it sales-postgres psql -U data_eng -d sales_db -c "SELECT count(*) FROM raw_sales;"
```

Inspect recent rows:

```bash
docker exec -it sales-postgres psql -U data_eng -d sales_db -c "SELECT event_id, product_name, price, quantity, region, ingestion_timestamp FROM raw_sales ORDER BY ingestion_timestamp DESC LIMIT 10;"
```

If you want to test the host-mapped PostgreSQL connection directly:

```bash
PGPASSWORD=data_eng psql -h 127.0.0.1 -p 5433 -U data_eng -d sales_db -c "SELECT current_user, current_database();"
```

## Run dbt Models

Run dbt after the consumer has inserted at least a few rows into `raw_sales`.

From the repository root:

```bash
uv run --directory dbt_sales dbt run --profiles-dir .
```

Validate the mart output:

```bash
docker exec -it sales-postgres psql -U data_eng -d sales_db -c "SELECT * FROM daily_sales ORDER BY order_date DESC, region, category LIMIT 20;"
```

## End-to-End Local Test Flow

From the repository root:

```bash
uv sync
docker compose down
docker compose up -d
docker exec -it sales-kafka kafka-topics --create --topic sales_topic --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1
uv run producer.py
```

In a second terminal:

```bash
uv run consumer.py
```

After a few rows have landed:

```bash
uv run --directory dbt_sales dbt run --profiles-dir .
```

## Data Model

### Raw table

`raw_sales`

- `event_id`: unique event identifier
- `order_id`: order identifier
- `customer_id`: customer identifier
- `product_name`: sold product name
- `category`: product category
- `price`: unit price
- `quantity`: purchased quantity
- `region`: sales region
- `order_timestamp`: event time
- `ingestion_timestamp`: database ingestion time

### dbt outputs

- `stg_sales`: cleaned staging model over `raw_sales`
- `daily_sales`: daily aggregated revenue, units, and order counts by region and category

## Notes

- The Python applications support environment variables for Kafka and PostgreSQL connection settings.
- Kafka topic auto-creation is disabled so topic provisioning stays explicit.
- `uv sync` creates a local `.venv`, which is already ignored by git.
