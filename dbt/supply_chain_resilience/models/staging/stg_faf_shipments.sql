select
    cast(dms_orig as integer) as origin_zone_id,
    cast(dms_dest as integer) as dest_zone_id,
    dms_mode as mode_code,
    sctg2 as commodity_code,
    trade_type,
    tons_2022 as tons,
    value_2022 as value_usd
from {{ source('raw', 'raw_faf6_regional') }}