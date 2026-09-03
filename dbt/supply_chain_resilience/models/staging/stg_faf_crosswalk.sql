select
    FAF6 as zone_id,
    FAF6_SHORT as zone_short_name,
    FAF6_NAME as zone_full_name,
    CFS_AREA as cfs_area_code,
    cast(split_part(CFS_AREA, '-', 1) as integer) as state_fips,
    CFS22_NAME as cfs_area_name
from {{ source('raw', 'raw_faf_crosswalk') }}