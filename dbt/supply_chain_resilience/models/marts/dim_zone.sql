select
    zone_id,
    zone_short_name,
    zone_full_name,
    state_fips,
    cfs_area_code,
    cfs_area_name
from {{ ref('stg_faf_crosswalk') }}