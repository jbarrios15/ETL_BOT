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

from adhoc_analysis import (
    window_analysis
)

from tree_operational_analysis import (
    run_operational_tree_analysis
)

from filtered_bot_simulation import (
    run_filtered_bot_simulation
)

from tree_pattern_analysis import (
    run_tree_pattern_analysis
)

from utils.report_manager import (
    get_report_folder
)


from analysis_helpers import (
    calculate_profit_factor,
    build_metrics,
    print_metrics,
    analyze_group
)

from phase2_analysis import (
    daily_setup_hour_analysis
)

#DICE QUE ANALISIS VAN A CORRER

RUN_PHASE1 = False
RUN_PHASE2 = False 
RUN_ADHOC = False
RUN_TREE_ANALYSIS = True
RUN_OPERATIONAL_TREE = True
RUN_FILTER_SIMULATION = True

def balanced_ema_analysis(
    df,
    report_folder
):

    df = (
        df
        .filter(
            pl.col("setup_type")
            == "balanced_rebound"
        )
        .with_columns(

            pl.when(
                pl.col("ema_distance") < 0.10
            )
            .then(pl.lit("0.00-0.10"))

            .when(
                pl.col("ema_distance") < 0.20
            )
            .then(pl.lit("0.10-0.20"))

            .when(
                pl.col("ema_distance") < 0.30
            )
            .then(pl.lit("0.20-0.30"))

            .otherwise(
                pl.lit("0.30+")
            )

            .alias("ema_bucket")
        )
    )

    analyze_group(
        df,
        "ema_bucket",
        report_folder,
        "balanced_ema.csv",
        "BALANCED REBOUND - EMA DISTANCE"
    )

def balanced_rsi_analysis(
    df,
    report_folder
):

    df = (
        df
        .filter(
            pl.col("setup_type")
            == "balanced_rebound"
        )
        .with_columns(

            pl.when(
                pl.col("rsi") < 40
            )
            .then(pl.lit("RSI < 40"))

            .when(
                pl.col("rsi") < 60
            )
            .then(pl.lit("RSI 40-60"))

            .when(
                pl.col("rsi") < 75
            )
            .then(pl.lit("RSI 60-75"))

            .otherwise(
                pl.lit("RSI > 75")
            )

            .alias("rsi_bucket")
        )
    )

    analyze_group(
        df,
        "rsi_bucket",
        report_folder,
        "balanced_rsi.csv",
        "BALANCED REBOUND - RSI"
    )

def balanced_hour_analysis(
    df,
    report_folder
):

    df = df.filter(
        pl.col("setup_type")
        == "balanced_rebound"
    )

    analyze_group(
        df,
        "trade_hour",
        report_folder,
        "balanced_hour.csv",
        "BALANCED REBOUND - HOUR"
    )

def balanced_symbol_analysis(
    df,
    report_folder
):

    df = df.filter(
        pl.col("setup_type")
        == "balanced_rebound"
    )

    analyze_group(
        df,
        "symbol",
        report_folder,
        "balanced_symbol.csv",
        "BALANCED REBOUND - SYMBOL"
    )

def balanced_weekday_analysis(
    df,
    report_folder
):

    df = df.filter(
        pl.col("setup_type")
        == "balanced_rebound"
    )

    analyze_group(
        df,
        "trade_weekday",
        report_folder,
        "balanced_weekday.csv",
        "BALANCED REBOUND - WEEKDAY"
    )

def balanced_score_analysis(
    df,
    report_folder
):

    df = (
        df
        .filter(
            pl.col("setup_type")
            == "balanced_rebound"
        )
        .with_columns(

            pl.max_horizontal(
                "call_score",
                "put_score"
            )
            .alias(
                "max_score"
            )
        )

        .with_columns(

            pl.when(
                pl.col("max_score") < 50
            )
            .then(pl.lit("0-50"))

            .when(
                pl.col("max_score") < 60
            )
            .then(pl.lit("50-60"))

            .when(
                pl.col("max_score") < 70
            )
            .then(pl.lit("60-70"))

            .when(
                pl.col("max_score") < 80
            )
            .then(pl.lit("70-80"))

            .otherwise(
                pl.lit("80+")
            )

            .alias(
                "score_bucket"
            )
        )
    )

    analyze_group(
        df,
        "score_bucket",
        report_folder,
        "balanced_score.csv",
        "BALANCED REBOUND - SCORE"
    )

def strategy_comparison_analysis(
    df,
    report_folder
):

    df = (
        df
        .filter(
            pl.col("strategy_version")
            .is_not_null()
        )
    )

    analyze_group(
        df,
        "strategy_version",
        report_folder,
        "strategy_comparison.csv",
        "STRATEGY COMPARISON"
    )

def balanced_duration_analysis(
    df,
    report_folder
):

    df = (
        df
        .filter(
            pl.col("setup_type")
            == "balanced_rebound"
        )
        .with_columns(

            pl.when(
                pl.col("duration_seconds") < 60
            )
            .then(
                pl.lit("0-60")
            )

            .when(
                pl.col("duration_seconds") < 70
            )
            .then(
                pl.lit("60-70")
            )

            .when(
                pl.col("duration_seconds") < 80
            )
            .then(
                pl.lit("70-80")
            )

            .otherwise(
                pl.lit("80+")
            )

            .alias(
                "duration_bucket"
            )
        )
    )

    analyze_group(
        df,
        "duration_bucket",
        report_folder,
        "balanced_duration.csv",
        "BALANCED REBOUND - DURATION"
    )

def setup_symbol_analysis(
    df,
    report_folder
):

    df = (
        df
        .with_columns(

            (
                pl.col("setup_type")
                + " | "
                + pl.col("symbol")
            )

            .alias(
                "setup_symbol"
            )
        )
    )

    analyze_group(
        df,
        "setup_symbol",
        report_folder,
        "setup_symbol.csv",
        "SETUP + SYMBOL"
    )

def setup_hour_analysis(
    df,
    report_folder
):

    df = (
        df
        .with_columns(

            (
                pl.col("setup_type")
                + " | H"
                + pl.col("trade_hour")
                .cast(pl.Utf8)
            )

            .alias(
                "setup_hour"
            )
        )
    )

    analyze_group(
        df,
        "setup_hour",
        report_folder,
        "setup_hour.csv",
        "SETUP + HOUR"
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

    if RUN_PHASE1:
         
        setup_comparison(
            df,
            report_folder
        )

        balanced_volatility_analysis(
            df,
            report_folder
        )

        balanced_ema_analysis(
        df,
        report_folder
        )

        balanced_rsi_analysis(
            df,
            report_folder
        )

        balanced_hour_analysis(
            df,
            report_folder
        )

        balanced_symbol_analysis(
            df,
            report_folder
        )

        balanced_weekday_analysis(
            df,
            report_folder
        )

        balanced_score_analysis(
            df,
            report_folder
        )

        strategy_comparison_analysis(
            df,
            report_folder
        )

        balanced_duration_analysis(
            df,
            report_folder
        )

        setup_symbol_analysis(
            df,
            report_folder
        )

        setup_hour_analysis(
            df,
            report_folder
        )

        daily_setup_hour_analysis(
            df,
            report_folder
        )

    if RUN_ADHOC:

       window_analysis(
            df,
            report_folder
        )

    if RUN_TREE_ANALYSIS:

        run_tree_pattern_analysis(
            df,
            report_folder
        )

    if RUN_OPERATIONAL_TREE:

        run_operational_tree_analysis(
            df,
            report_folder
        )

    if RUN_FILTER_SIMULATION:

        run_filtered_bot_simulation(
            df,
            report_folder
        )

    print()
    print(
        "CSV generado correctamente."
    )


if __name__ == "__main__":
    main()