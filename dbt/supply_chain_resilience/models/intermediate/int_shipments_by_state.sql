select
    c.state_fips,
    sum(s.tons) as state_total_tons,
    sum(s.value_usd) as state_total_value_usd
from {{ ref('stg_faf_shipments') }} s
inner join {{ ref('stg_faf_crosswalk') }} c on s.origin_zone_id = c.zone_id
group by c.state_fips