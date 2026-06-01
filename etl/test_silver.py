# test_silver.py

import polars as pl

df = pl.read_parquet(
    "data/silver/trades.parquet"
)

print(df.shape)

print(df.columns)

print(df.head(5))

print(df.schema)

print(
    df.select(
        [
            "result",
            "profit"
        ]
    ).head(20)
)