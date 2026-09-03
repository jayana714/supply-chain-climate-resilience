select
    EVENT_ID as event_id,
    STATE as state_name,
    STATE_FIPS as state_fips,
    YEAR as event_year,
    EVENT_TYPE as event_type,
    BEGIN_DATE_TIME as begin_date_time,
    END_DATE_TIME as end_date_time,
    DAMAGE_PROPERTY as damage_property_raw,
    DAMAGE_CROPS as damage_crops_raw,
    INJURIES_DIRECT as injuries_direct,
    DEATHS_DIRECT as deaths_direct,
    BEGIN_LAT as begin_lat,
    BEGIN_LON as begin_lon
from {{ source('raw', 'raw_noaa_details') }}