import json
import os
import random
import time
import uuid
from datetime import datetime, timezone

from kafka import KafkaProducer


BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
TOPIC_NAME = os.getenv("KAFKA_TOPIC", "sales_topic")
POLL_INTERVAL_SECONDS = float(os.getenv("PRODUCER_INTERVAL_SECONDS", "2"))

PRODUCTS = [
    {"product_name": "Laptop", "category": "Electronics", "price_range": (800, 1500)},
    {"product_name": "Phone", "category": "Electronics", "price_range": (400, 1200)},
    {"product_name": "Headphones", "category": "Accessories", "price_range": (50, 300)},
]
REGIONS = ["Europe", "North America", "Asia", "Middle East"]


def build_producer() -> KafkaProducer:
    return KafkaProducer(
        bootstrap_servers=BOOTSTRAP_SERVERS,
        value_serializer=lambda value: json.dumps(value).encode("utf-8"),
    )


def generate_event() -> dict:
    product = random.choice(PRODUCTS)
    price = round(random.uniform(*product["price_range"]), 2)
    return {
        "event_id": str(uuid.uuid4()),
        "order_id": random.randint(10000, 99999),
        "customer_id": random.randint(1000, 9999),
        "product_name": product["product_name"],
        "category": product["category"],
        "price": price,
        "quantity": random.randint(1, 5),
        "region": random.choice(REGIONS),
        "order_timestamp": datetime.now(timezone.utc).isoformat(),
    }


def main() -> None:
    producer = build_producer()
    print(f"Producing events to topic '{TOPIC_NAME}' on {BOOTSTRAP_SERVERS}")

    try:
        while True:
            event = generate_event()
            producer.send(TOPIC_NAME, event)
            producer.flush()
            print("Sent:", event)
            time.sleep(POLL_INTERVAL_SECONDS)
    except KeyboardInterrupt:
        print("\nProducer stopped.")
    finally:
        producer.close()


if __name__ == "__main__":
    main()
