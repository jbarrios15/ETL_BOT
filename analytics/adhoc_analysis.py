import polars as pl
from datetime import date

def balanced_hour17_deep_analysis(
    df,
    report_folder
):

    print()
    print("=" * 60)
    print(
        "BALANCED REBOUND HOUR 17 DEEP ANALYSIS"
    )
    print("=" * 60)

    target_dates = [

        date(2026, 6, 6),
        date(2026, 6, 7),
        date(2026, 6, 10),
        date(2026, 6, 11),
        date(2026, 6, 12)

    ]

    analysis_df = (

        df

        .filter(

            (pl.col("setup_type") == "balanced_rebound")

            &

            (pl.col("trade_hour") == 17)

            &

            (
                pl.col("trade_date")
                .is_in(target_dates)
            )

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

        .select(

            [
                "trade_date",

                "symbol",

                "direction",

                "strategy_version",

                "result",

                "profit",

                "is_win",

                "rsi",

                "volatility_pct",

                "ema_distance",

                "call_score",

                "put_score",

                "max_score"
            ]

        )

        .sort(
            [
                "trade_date"
            ]
        )

    )

    analysis_df.write_csv(

        report_folder /

        "balanced17_raw.csv"

    )

    print(analysis_df)

    print(
        f"Trades encontrados: "
        f"{len(analysis_df)}"
    )

    print(
        "Archivo generado:"
    )

    print(
        report_folder /
        "balanced17_raw.csv"
    )