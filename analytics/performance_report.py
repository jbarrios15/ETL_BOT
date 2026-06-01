import polars as pl


def main():

    df = pl.read_parquet(
        "data/silver/trades.parquet"
    )

    # ==========================
    # MÉTRICAS GENERALES
    # ==========================

    total_trades = len(df)

    wins = (
        df["is_win"]
        .sum()
    )

    losses = (
        total_trades - wins
    )

    winrate = (
        wins / total_trades
    ) * 100

    total_profit = (
        df["profit"]
        .sum()
    )

    total_invested = (
        df["amount"]
        .sum()
    )

    roi_pct = (
        total_profit
        / total_invested
    ) * 100

    gross_profit = (
        df
        .filter(
            pl.col("profit") > 0
        )
        ["profit"]
        .sum()
    )

    gross_loss = abs(
        df
        .filter(
            pl.col("profit") < 0
        )
        ["profit"]
        .sum()
    )

    profit_factor = (
        gross_profit / gross_loss
        if gross_loss > 0
        else 0
    )

    payout = 0.86

    breakeven_winrate = (
        1 / (1 + payout)
    ) * 100

    gap_vs_breakeven = (
        winrate - breakeven_winrate
    )

    # ==========================
    # REPORTE GENERAL
    # ==========================

    print("\n")
    print("=" * 60)
    print("BOT PERFORMANCE REPORT")
    print("=" * 60)

    print(
        f"Total Trades: {total_trades}"
    )

    print(
        f"Trades Ganados: {wins}"
    )

    print(
        f"Trades Perdidos: {losses}"
    )

    print(
        f"Winrate: {winrate:.2f}%"
    )

    print(
        f"Breakeven Winrate: {breakeven_winrate:.2f}%"
    )

    print(
        f"Gap vs Breakeven: {gap_vs_breakeven:.2f}%"
    )

    print(
        f"Profit Total: {total_profit:.2f}"
    )

    print(
        f"ROI: {roi_pct:.2f}%"
    )

    print(
        f"Profit Factor: {profit_factor:.2f}"
    )

    # ==========================
    # DIRECCIÓN
    # ==========================

    print("\n")
    print("=" * 60)
    print("WINRATE POR DIRECCIÓN")
    print("=" * 60)

    direction_stats = (
        df
        .group_by("direction")
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
        .sort(
            "winrate",
            descending=True
        )
    )

    print(direction_stats)

    # ==========================
    # ACTIVO
    # ==========================

    print("\n")
    print("=" * 60)
    print("WINRATE POR ACTIVO")
    print("=" * 60)

    symbol_stats = (
        df
        .group_by("symbol")
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
            .alias("profit"),

            (
                pl.col("profit").sum()
                /
                pl.col("amount").sum()
                * 100
            )
            .round(2)
            .alias("roi_pct")
        ])
        .sort(
            "winrate",
            descending=True
        )
    )

    print()

    for row in symbol_stats.iter_rows(named=True):

        print(
            f"{row['symbol']} → "
            f"{row['winrate']:.2f}% | "
            f"Trades: {row['trades']} | "
            f"Wins: {row['wins']} | "
            f"Losses: {row['losses']} | "
            f"Profit: {row['profit']:.2f} | "
            f"ROI: {row['roi_pct']:.2f}%"
        )

    # ==========================
    # HORA
    # ==========================

    print("\n")
    print("=" * 60)
    print("WINRATE POR HORA")
    print("=" * 60)

    hour_stats = (
        df
        .group_by("trade_hour")
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
        .sort(
            "trade_hour"
        )
    )

    print()

    for row in hour_stats.iter_rows(named=True):

        hora = row["trade_hour"]

        trades = row["trades"]

        wins = row["wins"]

        losses = row["losses"]

        winrate = row["winrate"]

        profit = row["profit"]

        print(
            f"{hora:02d}:00 → "
            f"{winrate:.2f}% | "
            f"Trades: {trades} | "
            f"Wins: {wins} | "
            f"Losses: {losses} | "
            f"Profit: {profit:.2f}"
        )

    # ==========================
    # SETUP
    # ==========================

    print("\n")
    print("=" * 60)
    print("WINRATE POR SETUP")
    print("=" * 60)

    setup_stats = (
        df
        .group_by("setup_type")
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
            .alias("profit"),

            (
                pl.col("profit").sum()
                /
                pl.col("amount").sum()
                * 100
            )
            .round(2)
            .alias("roi_pct")
        ])
        .sort(
            "winrate",
            descending=True
        )
    )

    print()

    for row in setup_stats.iter_rows(named=True):

        print(
            f"{row['setup_type']} → "
            f"{row['winrate']:.2f}% | "
            f"Trades: {row['trades']} | "
            f"Wins: {row['wins']} | "
            f"Losses: {row['losses']} | "
            f"Profit: {row['profit']:.2f} | "
            f"ROI: {row['roi_pct']:.2f}%"
        )

    # ==========================
    # STRATEGY VERSION
    # ==========================

    print("\n")
    print("=" * 60)
    print("WINRATE POR STRATEGY VERSION")
    print("=" * 60)

    strategy_stats = (
        df
        .group_by("strategy_version")
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
            .alias("profit"),

            (
                pl.col("profit").sum()
                /
                pl.col("amount").sum()
                * 100
            )
            .round(2)
            .alias("roi_pct")
        ])
        .sort(
            "winrate",
            descending=True
        )
    )

    print()

    for row in strategy_stats.iter_rows(named=True):

        print(
            f"{row['strategy_version']} → "
            f"{row['winrate']:.2f}% | "
            f"Trades: {row['trades']} | "
            f"Wins: {row['wins']} | "
            f"Losses: {row['losses']} | "
            f"Profit: {row['profit']:.2f} | "
            f"ROI: {row['roi_pct']:.2f}%"
        )


if __name__ == "__main__":
    main()