import duckdb
import pandas as pd

DB_PATH = "supply_chain_resilience.duckdb"

con = duckdb.connect(DB_PATH)

# FAF6 regional freight data
con.execute("""
    CREATE OR REPLACE TABLE raw_faf6_regional AS
    SELECT * FROM read_csv_auto('raw/faf6/FAF6.0.csv', header=True)
""")
print("raw_faf6_regional:", con.execute("SELECT COUNT(*) FROM raw_faf6_regional").fetchone()[0], "rows")

# FAF6 zone crosswalk (xlsx, needs pandas)
crosswalk_df = pd.read_excel("raw/faf6/FAF6_Zone_ID_crosswalk.xlsx")
con.execute("CREATE OR REPLACE TABLE raw_faf_crosswalk AS SELECT * FROM crosswalk_df")
print("raw_faf_crosswalk:", con.execute("SELECT COUNT(*) FROM raw_faf_crosswalk").fetchone()[0], "rows")

# NOAA storm events: all 10 years at once via glob pattern
con.execute("""
    CREATE OR REPLACE TABLE raw_noaa_details AS
    SELECT * FROM read_csv_auto('raw/noaa_storm_events/StormEvents_details-*.csv', union_by_name=True)
""")
print("raw_noaa_details:", con.execute("SELECT COUNT(*) FROM raw_noaa_details").fetchone()[0], "rows")

con.execute("""
    CREATE OR REPLACE TABLE raw_noaa_locations AS
    SELECT * FROM read_csv_auto('raw/noaa_storm_events/StormEvents_locations-*.csv', union_by_name=True)
""")
print("raw_noaa_locations:", con.execute("SELECT COUNT(*) FROM raw_noaa_locations").fetchone()[0], "rows")

# MODIS NDVI anomaly by state
con.execute("""
    CREATE OR REPLACE TABLE raw_modis_ndvi_by_state AS
    SELECT * FROM read_csv_auto('raw/modis_ndvi_by_state.csv', header=True)
""")
print("raw_modis_ndvi_by_state:", con.execute("SELECT COUNT(*) FROM raw_modis_ndvi_by_state").fetchone()[0], "rows")



con.close()
print("Done —", DB_PATH, "created.")