import polars as pl
from datetime import datetime, timedelta


def main():

    days = int(
        input(
            "\n¿Cuántos días atrás deseas analizar? "
        )
    )

    df = pl.read_parquet(
        "data/silver/trades.parquet"
    )

    cutoff_date = (
        datetime.now()
        - timedelta(days=days)
    )

    df = df.filter(
        pl.col("open_time") >= cutoff_date
    )

    total_trades = len(df)

    wins = (
        df["is_win"]
        .sum()
    )

    losses = (
        total_trades - wins
    )

    winrate = (
        wins / total_trades * 100
        if total_trades > 0
        else 0
    )

    profit = (
        df["profit"]
        .sum()
    )

    print()
    print("=" * 60)
    print(
        f"PERFORMANCE ÚLTIMOS {days} DÍAS"
    )
    print("=" * 60)

    print(
        f"Trades: {total_trades}"
    )

    print(
        f"Ganadas: {wins}"
    )

    print(
        f"Perdidas: {losses}"
    )

    print(
        f"Winrate: {winrate:.2f}%"
    )

    print(
        f"Profit: {profit:.2f}"
    )

    print()
    print("=" * 60)
    print("AGRUPADO POR DÍA")
    print("=" * 60)

    daily_stats = (
        df
        .group_by("trade_date")
        .agg([
            pl.len()
            .alias("trades"),

            pl.col("is_win")
            .sum()
            .alias("wins"),

            (
                pl.len()
                - pl.col("is_win").sum()
            )
            .alias("losses"),

            pl.col("is_win")
            .mean()
            .mul(100)
            .round(2)
            .alias("winrate"),

            pl.col("profit")
            .sum()
            .round(2)
            .alias("profit")
        ])
        .sort("trade_date")
    )

    print()

    for row in daily_stats.iter_rows(named=True):

        print(
            f"{row['trade_date']} → "
            f"{row['winrate']:.2f}% | "
            f"Trades: {row['trades']} | "
            f"Wins: {row['wins']} | "
            f"Losses: {row['losses']} | "
            f"Profit: {row['profit']:.2f}"
        )


if __name__ == "__main__":
    main()