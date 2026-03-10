select
    event_id,
    order_id,
    customer_id,
    product_name,
    category,
    price,
    quantity,
    region,
    order_timestamp,
    ingestion_timestamp
from public.raw_sales
