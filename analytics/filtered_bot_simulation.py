import polars as pl


# ============================================================
# METRICAS
# ============================================================

def calculate_metrics(
    df
):

    trades = len(df)

    if trades == 0:

        return {
            "trades": 0,
            "wins": 0,
            "losses": 0,
            "winrate": 0,
            "profit": 0,
            "roi": 0,
            "profit_factor": 0,
            "positive_days": 0,
            "negative_days": 0,
            "daily_avg_profit": 0
        }


    wins = df["is_win"].sum()

    losses = trades - wins


    profit = df["profit"].sum()


    win_profit = (

        df.filter(
            pl.col("profit") > 0
        )
        ["profit"]
        .sum()

    )


    loss_profit = abs(

        df.filter(
            pl.col("profit") < 0
        )
        ["profit"]
        .sum()

    )


    pf = (
        win_profit / loss_profit
        if loss_profit != 0
        else 999
    )


    daily = (

        df

        .group_by(
            "trade_date"
        )

        .agg(

            pl.sum("profit")
            .alias("daily_profit")

        )

    )


    return {

        "trades": trades,

        "wins": int(wins),

        "losses": int(losses),

        "winrate": round(
            wins / trades * 100,
            2
        ),

        "profit": round(
            profit,
            2
        ),

        "roi": round(
            profit / trades * 100,
            2
        ),

        "profit_factor": round(
            pf,
            2
        ),

        "daily_avg_profit": round(
            daily["daily_profit"]
            .mean(),
            2
        ),

        "positive_days": len(
            daily.filter(
                pl.col("daily_profit") > 0
            )
        ),

        "negative_days": len(
            daily.filter(
                pl.col("daily_profit") < 0
            )
        )

    }



# ============================================================
# SIMULACIONES
# ============================================================

def apply_simulation(
    df,
    simulation
):


    # ------------------------------------
    # SIM 1
    # ------------------------------------

    if simulation == "FILTER_BAD_HOURS":


        return df.filter(

            ~(
                (
                    (pl.col("setup_type") == "extreme_reversion")
                    &
                    (pl.col("trade_hour").is_in([9,20]))
                )

                |

                (
                    (pl.col("setup_type") == "balanced_rebound")
                    &
                    (pl.col("trade_hour").is_in([20,21]))
                )

            )

        )


    # ------------------------------------
    # SIM 2
    # ------------------------------------

    if simulation == "FILTER_EXTENDED_HOURS":


        return df.filter(

            ~(
                (
                    (pl.col("setup_type") == "extreme_reversion")
                    &
                    (pl.col("trade_hour").is_in([9,14,20]))
                )

                |

                (
                    (pl.col("setup_type") == "balanced_rebound")
                    &
                    (pl.col("trade_hour").is_in([20,21]))
                )

            )

        )



    # ------------------------------------
    # SIM 3
    # ------------------------------------

    if simulation == "FILTER_VOLATILITY":


        return df.filter(

            ~(

                (
                    pl.col("setup_type")
                    ==
                    "balanced_rebound"
                )

                &

                (
                    pl.col("volatility_bucket")
                    ==
                    "Baja"
                )

            )

        )



    # ------------------------------------
    # SIM 4
    # ------------------------------------

    if simulation == "FILTER_COMBINED":


        return df.filter(

            ~(
                (
                    (pl.col("setup_type") == "extreme_reversion")
                    &
                    (pl.col("trade_hour").is_in([9,14,20]))
                )

                |

                (
                    (pl.col("setup_type") == "balanced_rebound")
                    &
                    (
                        (pl.col("trade_hour").is_in([20,21]))
                        |
                        (pl.col("volatility_bucket") == "Baja")
                    )
                )

            )

        )


    return df



# ============================================================
# MAIN
# ============================================================

def run_filtered_bot_simulation(
    df,
    report_folder
):

    print()
    print("=" * 60)
    print("FILTERED BOT SIMULATION")
    print("=" * 60)

    # ==================================================
    # CREATE VOLATILITY BUCKET
    # ==================================================

    if "volatility_bucket" not in df.columns:

        df = (

            df.with_columns(

                pl.col("volatility_pct")

                .qcut(
                    3,
                    labels=[
                        "Baja",
                        "Media",
                        "Alta"
                    ]
                )

                .alias(
                    "volatility_bucket"
                )

            )

        )

    sim_folder = (

        report_folder
        /
        "simulation"

    )


    sim_folder.mkdir(

        parents=True,

        exist_ok=True

    )


    simulations = [

        "ORIGINAL",

        "FILTER_BAD_HOURS",

        "FILTER_EXTENDED_HOURS",

        "FILTER_VOLATILITY",

        "FILTER_COMBINED"

    ]


    results = []


    for sim in simulations:


        if sim == "ORIGINAL":

            sim_df = df

        else:

            sim_df = apply_simulation(
                df,
                sim
            )


        versions = (

            sim_df

            .select(
                "strategy_version"
            )

            .drop_nulls()

            .unique()

            .to_series()

            .to_list()

        )


        for version in versions:


            version_df = (

                sim_df.filter(

                    pl.col("strategy_version")
                    ==
                    version

                )

            )


            metrics = calculate_metrics(
                version_df
            )


            results.append(

                {

                    "simulation": sim,

                    "strategy_version": version,

                    **metrics

                }

            )


    summary = (

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


    summary.write_csv(

        sim_folder
        /
        "filtered_bot_summary.csv"

    )


    print(summary)


    print(
        "Archivo generado:",
        sim_folder
        /
        "filtered_bot_summary.csv"
    )