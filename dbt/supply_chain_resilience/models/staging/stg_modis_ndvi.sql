select
    state_fips,
    ndvi_current,
    ndvi_baseline_2020,
    ndvi_anomaly,
    case
        when ndvi_anomaly is null then 'No Data'
        when ndvi_anomaly < -0.03 then 'Elevated Stress'
        when ndvi_anomaly > 0.03 then 'Above Normal'
        else 'Normal'
    end as vegetation_stress_tier
from {{ source('raw', 'raw_modis_ndvi_by_state') }}