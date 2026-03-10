CREATE TABLE IF NOT EXISTS raw_sales (
    event_id VARCHAR(100) PRIMARY KEY,
    order_id INTEGER,
    customer_id INTEGER,
    product_name VARCHAR(100),
    category VARCHAR(100),
    price NUMERIC(10, 2),
    quantity INTEGER,
    region VARCHAR(50),
    order_timestamp TIMESTAMP,
    ingestion_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
