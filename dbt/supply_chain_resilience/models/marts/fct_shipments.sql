select
    origin_zone_id as zone_id,
    count(*) as shipment_lane_count,
    sum(tons) as total_tons,
    sum(value_usd) as total_value_usd
from {{ ref('stg_faf_shipments') }}
group by origin_zone_id