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

## Run dbt Models

From the repository root:

```bash
cd dbt_sales
uv run dbt run --profiles-dir .
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
