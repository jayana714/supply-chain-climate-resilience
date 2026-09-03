import duckdb

con = duckdb.connect("/Users/jayanasarma/Desktop/supply-chain-climate-resilience/supply_chain_resilience.duckdb")

con.execute("""
    COPY (SELECT * FROM fct_supply_chain_risk)
    TO '/Users/jayanasarma/Desktop/supply-chain-climate-resilience/powerbi/fct_supply_chain_risk.csv'
    (HEADER, DELIMITER ',')
""")

print("Exported to powerbi/fct_supply_chain_risk.csv")
con.close()