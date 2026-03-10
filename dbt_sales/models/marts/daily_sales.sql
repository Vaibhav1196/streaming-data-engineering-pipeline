select
    cast(order_timestamp as date) as order_date,
    region,
    category,
    count(*) as total_orders,
    sum(quantity) as total_units,
    round(sum(price * quantity), 2) as gross_revenue
from {{ ref('stg_sales') }}
group by 1, 2, 3
order by 1, 2, 3
