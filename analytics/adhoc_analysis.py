import polars as pl

from analysis_helpers import (
    build_metrics
)


def window_analysis(
    df,
    report_folder
):

    print()
    print("=" * 60)
    print("WINDOW ANALYSIS")
    print("=" * 60)

    windows = [

        # =====================================================
        # BALANCED REBOUND
        # =====================================================

        {
            "setup": "balanced_rebound",
            "window": "BR_16_17",
            "description": "16:00-17:00",
            "hours": [16, 17]
        },

        {
            "setup": "balanced_rebound",
            "window": "BR_16_18",
            "description": "16:00-18:00",
            "hours": [16, 17, 18]
        },

        {
            "setup": "balanced_rebound",
            "window": "BR_22_23",
            "description": "22:00-23:00",
            "hours": [22, 23]
        },

        {
            "setup": "balanced_rebound",
            "window": "BR_NEG_02_03",
            "description": "02:00-03:00",
            "hours": [2, 3]
        },

        {
            "setup": "balanced_rebound",
            "window": "BR_NEG_20_21",
            "description": "20:00-21:00",
            "hours": [20, 21]
        },

        # =====================================================
        # EXTREME REVERSION
        # =====================================================

        {
            "setup": "extreme_reversion",
            "window": "ER_07_08",
            "description": "07:00-08:00",
            "hours": [7, 8]
        },

        {
            "setup": "extreme_reversion",
            "window": "ER_17_18",
            "description": "17:00-18:00",
            "hours": [17, 18]
        },

        {
            "setup": "extreme_reversion",
            "window": "ER_21_23",
            "description": "21:00-23:00",
            "hours": [21, 22, 23]
        },

        {
            "setup": "extreme_reversion",
            "window": "ER_NEG_09",
            "description": "09:00",
            "hours": [9]
        },

        {
            "setup": "extreme_reversion",
            "window": "ER_NEG_14",
            "description": "14:00",
            "hours": [14]
        },

        {
            "setup": "extreme_reversion",
            "window": "ER_NEG_20",
            "description": "20:00",
            "hours": [20]
        }

    ]

    results = []

    versions = (

        df

        .select(
            "strategy_version"
        )

        .drop_nulls()

        .unique()

        .to_series()

        .to_list()

    )

    print()
    print("VERSIONES DETECTADAS:")
    print(versions)

    for w in windows:

        for version in versions:

            subset = (

                df.filter(

                    (pl.col("setup_type") == w["setup"])

                    &

                    (
                        pl.col("trade_hour")
                        .is_in(w["hours"])
                    )

                    &

                    (
                        pl.col("strategy_version")
                        == version
                    )

                )

            )

            if len(subset) == 0:
                continue

            metrics = build_metrics(
                subset
            )

            row = {

                "setup": w["setup"],

                "strategy_version": version,

                "window": w["window"],

                "hours": w["description"],

                **metrics

            }

            results.append(
                row
            )

    result_df = (

        pl.DataFrame(
            results
        )

        .sort(
            by=[
                "profit_factor",
                "profit"
            ],
            descending=True
        )

    )

    # ==========================================================
    # RESUMEN POR VERSION
    # ==========================================================

    version_summary = (

        result_df

        .group_by(
            "strategy_version"
        )

        .agg(

            pl.sum("trades")
            .alias("trades"),

            pl.mean("winrate")
            .alias("avg_winrate"),

            pl.sum("profit")
            .alias("profit"),

            pl.mean("profit_factor")
            .alias("avg_pf")

        )

        .sort(
            "avg_pf",
            descending=True
        )

    )

    version_summary.write_csv(

        report_folder /

        "window_analysis_by_version.csv"

    )

    # ==========================================================
    # CSV PRINCIPAL
    # ==========================================================

    result_df.write_csv(

        report_folder /

        "window_analysis.csv"

    )

    # ==========================================================
    # TOP 10
    # ==========================================================

    top10 = (

        result_df

        .sort(
            by=[
                "profit_factor",
                "profit"
            ],
            descending=True
        )

        .head(10)

    )

    top10.write_csv(

        report_folder /

        "top10_windows.csv"

    )

    # ==========================================================
    # WORST 10
    # ==========================================================

    worst10 = (

        result_df

        .sort(
            by=[
                "profit_factor",
                "profit"
            ],
            descending=False
        )

        .head(10)

    )

    worst10.write_csv(

        report_folder /

        "worst10_windows.csv"

    )

    print()
    print("WINDOW ANALYSIS")
    print(result_df)

    print()
    print("WINDOW ANALYSIS BY VERSION")
    print(version_summary)

    print()
    print("TOP 10 WINDOWS")
    print(top10)

    print()
    print("WORST 10 WINDOWS")
    print(worst10)

    print()
    print(
        f"Archivo generado: "
        f"{report_folder / 'window_analysis.csv'}"
    )