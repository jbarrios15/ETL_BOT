import polars as pl

df = pl.read_parquet(
    "data/silver/trades.parquet"
)

df.write_csv(
    "data/silver/trades.csv"
)

print(
    "CSV generado correctamente."
)