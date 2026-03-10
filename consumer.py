import json
import os

import psycopg2
from kafka import KafkaConsumer
from psycopg2.extensions import connection as PgConnection


TOPIC_NAME = os.getenv("KAFKA_TOPIC", "sales_topic")
BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")

DB_HOST = os.getenv("POSTGRES_HOST", "localhost")
DB_PORT = int(os.getenv("POSTGRES_PORT", "5433"))
DB_NAME = os.getenv("POSTGRES_DB", "sales_db")
DB_USER = os.getenv("POSTGRES_USER", "data_eng")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "data_eng")

INSERT_QUERY = """
INSERT INTO raw_sales (
    event_id,
    order_id,
    customer_id,
    product_name,
    category,
    price,
    quantity,
    region,
    order_timestamp
)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
ON CONFLICT (event_id) DO NOTHING;
"""


def build_consumer() -> KafkaConsumer:
    return KafkaConsumer(
        TOPIC_NAME,
        bootstrap_servers=BOOTSTRAP_SERVERS,
        auto_offset_reset="earliest",
        enable_auto_commit=True,
        value_deserializer=lambda value: json.loads(value.decode("utf-8")),
    )


def build_connection() -> PgConnection:
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
    )


def main() -> None:
    consumer = build_consumer()
    connection = build_connection()
    cursor = connection.cursor()

    print(f"Consuming topic '{TOPIC_NAME}' and writing into {DB_NAME}.raw_sales")

    try:
        for message in consumer:
            event = message.value
            cursor.execute(
                INSERT_QUERY,
                (
                    event["event_id"],
                    event["order_id"],
                    event["customer_id"],
                    event["product_name"],
                    event["category"],
                    event["price"],
                    event["quantity"],
                    event["region"],
                    event["order_timestamp"],
                ),
            )
            connection.commit()
            print("Inserted", event["event_id"])
    except KeyboardInterrupt:
        print("\nConsumer stopped.")
    finally:
        cursor.close()
        connection.close()
        consumer.close()


if __name__ == "__main__":
    main()
