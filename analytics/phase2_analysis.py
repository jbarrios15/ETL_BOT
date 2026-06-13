import polars as pl

from analysis_helpers import (
    build_metrics
)


def daily_setup_hour_analysis(
    df,
    report_folder
):
    
    

    print()
    print("=" * 60)
    print(
        "DAILY SETUP HOUR ANALYSIS"
    )
    print("=" * 60)

    results = []

    grouped = (

        df

        .group_by(
            [
                "trade_date",
                "setup_type",
                "trade_hour"
            ]
        )

        .agg(

            pl.len()
            .alias("trades"),

            pl.sum(
                "is_win"
            )
            .alias("wins"),

            pl.sum(
                "profit"
            )
            .alias("profit")
        )

        .sort(
            [
                "trade_date",
                "setup_type",
                "trade_hour"
            ]
        )
    )

    for row in grouped.iter_rows(
        named=True
    ):

        date = row[
            "trade_date"
        ]

        setup = row[
            "setup_type"
        ]

        hour = row[
            "trade_hour"
        ]

        subset = (

            df.filter(

                (pl.col("trade_date") == date)

                &

                (pl.col("setup_type") == setup)

                &

                (pl.col("trade_hour") == hour)
            )
        )

        metrics = (
            build_metrics(
                subset
            )
        )

        results.append(

            {
                "trade_date": date,

                "setup_type": setup,

                "trade_hour": hour,

                **metrics
            }
        )

    result_df = pl.DataFrame(
        results
    )

    result_df.write_csv(

        report_folder /

        "daily_setup_hour.csv"
    )

    print(
        f"Filas generadas: "
        f"{len(result_df)}"
    )