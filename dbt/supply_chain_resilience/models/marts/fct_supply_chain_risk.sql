select
    z.zone_id,
    z.zone_full_name,
    z.state_fips,
    s.shipment_lane_count,
    s.total_tons,
    s.total_value_usd,
    r.climate_risk_score,
    r.climate_risk_tier,
    r.risk_intensity_score,
    r.risk_intensity_tier,
    r.event_count as state_storm_event_count,
    r.total_damage_usd as state_storm_damage_usd,
    v.ndvi_anomaly,
    v.vegetation_stress_tier,
    c.latitude,
    c.longitude
from {{ ref('dim_zone') }} z
left join {{ ref('fct_shipments') }} s on z.zone_id = s.zone_id
left join {{ ref('int_climate_risk_by_state') }} r on z.state_fips = r.state_fips
left join {{ ref('stg_modis_ndvi') }} v on z.state_fips = v.state_fips
left join {{ ref('state_centroids') }} c on z.state_fips = c.state_fips