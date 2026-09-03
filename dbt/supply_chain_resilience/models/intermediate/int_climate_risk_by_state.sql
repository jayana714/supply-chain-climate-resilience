with parsed_events as (
    select
        state_fips,
        state_name,
        case
            when damage_property_raw is null or damage_property_raw = '' then 0
            when upper(right(damage_property_raw, 1)) = 'K' then try_cast(left(damage_property_raw, length(damage_property_raw)-1) as double) * 1000
            when upper(right(damage_property_raw, 1)) = 'M' then try_cast(left(damage_property_raw, length(damage_property_raw)-1) as double) * 1000000
            when upper(right(damage_property_raw, 1)) = 'B' then try_cast(left(damage_property_raw, length(damage_property_raw)-1) as double) * 1000000000
            else coalesce(try_cast(damage_property_raw as double), 0)
        end as damage_property_usd,
        injuries_direct,
        deaths_direct
    from {{ ref('stg_noaa_events') }}
    where state_fips is not null
),

state_agg as (
    select
        state_fips,
        max(state_name) as state_name,
        count(*) as event_count,
        sum(damage_property_usd) as total_damage_usd,
        sum(injuries_direct) as total_injuries,
        sum(deaths_direct) as total_deaths
    from parsed_events
    group by state_fips
),

combined as (
    select
        a.*,
        sh.state_total_tons,
        sh.state_total_value_usd,
        case when sh.state_total_value_usd > 0
            then a.total_damage_usd / (sh.state_total_value_usd / 1000000.0)
            else null
        end as damage_per_million_shipped
    from state_agg a
    left join {{ ref('int_shipments_by_state') }} sh on a.state_fips = sh.state_fips
),

scored as (
    select
        *,
        (event_count - min(event_count) over ()) * 1.0
            / nullif(max(event_count) over () - min(event_count) over (), 0) as event_count_norm,
        (total_damage_usd - min(total_damage_usd) over ()) * 1.0
            / nullif(max(total_damage_usd) over () - min(total_damage_usd) over (), 0) as damage_norm,
        (damage_per_million_shipped - min(damage_per_million_shipped) over ())
            / nullif(max(damage_per_million_shipped) over () - min(damage_per_million_shipped) over (), 0) as intensity_norm
    from combined
)

select
    state_fips,
    state_name,
    event_count,
    total_damage_usd,
    total_injuries,
    total_deaths,
    state_total_tons,
    state_total_value_usd,
    round(damage_per_million_shipped, 2) as damage_usd_per_million_shipped,
    round((coalesce(event_count_norm,0) + coalesce(damage_norm,0)) / 2, 4) as climate_risk_score,
    case
        when (coalesce(event_count_norm,0) + coalesce(damage_norm,0)) / 2 >= 0.66 then 'High'
        when (coalesce(event_count_norm,0) + coalesce(damage_norm,0)) / 2 >= 0.33 then 'Medium'
        else 'Low'
    end as climate_risk_tier,
    round(coalesce(intensity_norm,0), 4) as risk_intensity_score,
    case
        when coalesce(intensity_norm,0) >= 0.66 then 'High'
        when coalesce(intensity_norm,0) >= 0.33 then 'Medium'
        else 'Low'
    end as risk_intensity_tier
from scored