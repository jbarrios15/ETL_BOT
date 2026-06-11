import polars as pl

from pathlib import Path

import sys
from pathlib import Path

sys.path.append(
    str(
        Path(__file__)
        .resolve()
        .parent.parent
    )
)

from utils.report_manager import (
    get_report_folder
)


def calculate_profit_factor(df):

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

    if gross_loss == 0:
        return 0

    return round(
        gross_profit /
        gross_loss,
        2
    )


def setup_comparison(
    df,
    report_folder
):

    print()
    print("=" * 60)
    print(
        "SETUP COMPARISON"
    )
    print("=" * 60)

    results = []

    setups = (
        df
        .select("setup_type")
        .unique()
        .drop_nulls()
        .to_series()
        .to_list()
    )

    for setup in setups:

        setup_df = (
            df.filter(
                pl.col(
                    "setup_type"
                ) == setup
            )
        )

        trades = len(
            setup_df
        )

        wins = (
            setup_df["is_win"]
            .sum()
        )

        losses = (
            trades - wins
        )

        winrate = round(
            wins /
            trades *
            100,
            2
        )

        profit = round(
            setup_df["profit"]
            .sum(),
            2
        )

        amount = (
            setup_df["amount"]
            .sum()
        )

        roi = round(
            (
                profit /
                amount
            ) * 100,
            2
        )

        profit_factor = (
            calculate_profit_factor(
                setup_df
            )
        )

        print()
        print(
            f"{setup}"
        )

        print(
            f"Trades: {trades}"
        )

        print(
            f"Wins: {wins}"
        )

        print(
            f"Losses: {losses}"
        )

        print(
            f"Winrate: {winrate}%"
        )

        print(
            f"Profit: {profit}"
        )

        print(
            f"ROI: {roi}%"
        )

        print(
            f"Profit Factor: {profit_factor}"
        )

        results.append(
            {
                "setup": setup,
                "trades": trades,
                "wins": wins,
                "losses": losses,
                "winrate": winrate,
                "profit": profit,
                "roi": roi,
                "profit_factor": profit_factor
            }
        )

    result_df = (
        pl.DataFrame(
            results
        )
    )

    result_df.write_csv(
        report_folder /
        "setup_comparison.csv"
    )

def balanced_volatility_analysis(
    df,
    report_folder
):

    print()
    print("=" * 60)
    print(
        "BALANCED REBOUND - VOLATILITY ANALYSIS"
    )
    print("=" * 60)

    df = (
        df.filter(
            pl.col("setup_type")
            == "balanced_rebound"
        )
    )

    if len(df) == 0:

        print(
            "No hay registros de balanced_rebound."
        )

        return

    q20 = (
        df["volatility_pct"]
        .quantile(0.20)
    )

    q40 = (
        df["volatility_pct"]
        .quantile(0.40)
    )

    q60 = (
        df["volatility_pct"]
        .quantile(0.60)
    )

    q80 = (
        df["volatility_pct"]
        .quantile(0.80)
    )

    df = df.with_columns(

        pl.when(
            pl.col("volatility_pct")
            <= q20
        )
        .then(
            pl.lit("Muy Baja")
        )

        .when(
            pl.col("volatility_pct")
            <= q40
        )
        .then(
            pl.lit("Baja")
        )

        .when(
            pl.col("volatility_pct")
            <= q60
        )
        .then(
            pl.lit("Media")
        )

        .when(
            pl.col("volatility_pct")
            <= q80
        )
        .then(
            pl.lit("Alta")
        )

        .otherwise(
            pl.lit("Muy Alta")
        )

        .alias(
            "volatility_bucket"
        )
    )

    results = []

    buckets = [
        "Muy Baja",
        "Baja",
        "Media",
        "Alta",
        "Muy Alta"
    ]

    for bucket in buckets:

        bucket_df = (
            df.filter(
                pl.col(
                    "volatility_bucket"
                ) == bucket
            )
        )

        trades = len(
            bucket_df
        )

        if trades == 0:
            continue

        wins = (
            bucket_df["is_win"]
            .sum()
        )

        losses = (
            trades - wins
        )

        winrate = round(
            wins /
            trades * 100,
            2
        )

        profit = round(
            bucket_df["profit"]
            .sum(),
            2
        )

        amount = (
            bucket_df["amount"]
            .sum()
        )

        roi = round(
            (
                profit /
                amount
            ) * 100,
            2
        )

        profit_factor = (
            calculate_profit_factor(
                bucket_df
            )
        )

        print()

        print(
            f"{bucket}"
        )

        print(
            f"Trades: {trades}"
        )

        print(
            f"Wins: {wins}"
        )

        print(
            f"Losses: {losses}"
        )

        print(
            f"Winrate: {winrate}%"
        )

        print(
            f"Profit: {profit}"
        )

        print(
            f"ROI: {roi}%"
        )

        print(
            f"Profit Factor: {profit_factor}"
        )

        results.append(
            {
                "volatility_bucket": bucket,
                "trades": trades,
                "wins": wins,
                "losses": losses,
                "winrate": winrate,
                "profit": profit,
                "roi": roi,
                "profit_factor": profit_factor
            }
        )

    result_df = pl.DataFrame(
        results
    )

    result_df.write_csv(
        report_folder /
        "balanced_volatility.csv"
    )

def main():

    report_folder = (
        get_report_folder()
    )

    print(
        f"\nReport Folder: "
        f"{report_folder}"
    )

    df = pl.read_parquet(
        "data/silver/trades.parquet"
    )

    setup_comparison(
        df,
        report_folder
    )

    balanced_volatility_analysis(
        df,
        report_folder
    )

    print()
    print(
        "CSV generado correctamente."
    )


if __name__ == "__main__":
    main()