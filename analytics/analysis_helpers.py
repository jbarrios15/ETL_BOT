import polars as pl


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


def build_metrics(
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
            "profit_factor": 0
        }

    wins = (
        df["is_win"]
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
        df["profit"]
        .sum(),
        2
    )

    amount = (
        df["amount"]
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
            df
        )
    )

    return {

        "trades": trades,

        "wins": wins,

        "losses": losses,

        "winrate": winrate,

        "profit": profit,

        "roi": roi,

        "profit_factor": profit_factor
    }


def print_metrics(
    name,
    metrics
):

    print()

    print(
        name
    )

    print(
        f"Trades: {metrics['trades']}"
    )

    print(
        f"Wins: {metrics['wins']}"
    )

    print(
        f"Losses: {metrics['losses']}"
    )

    print(
        f"Winrate: {metrics['winrate']}%"
    )

    print(
        f"Profit: {metrics['profit']}"
    )

    print(
        f"ROI: {metrics['roi']}%"
    )

    print(
        f"Profit Factor: "
        f"{metrics['profit_factor']}"
    )


def analyze_group(
    df,
    group_column,
    report_folder,
    report_name,
    title
):

    print()
    print("=" * 60)
    print(title)
    print("=" * 60)

    results = []

    values = (
        df
        .select(group_column)
        .unique()
        .sort(group_column)
        .to_series()
        .to_list()
    )

    for value in values:

        subset = (
            df.filter(
                pl.col(group_column)
                == value
            )
        )

        metrics = (
            build_metrics(
                subset
            )
        )

        print(
            f"{value} | "
            f"Trades={metrics['trades']} | "
            f"WR={metrics['winrate']}% | "
            f"Profit={metrics['profit']} | "
            f"PF={metrics['profit_factor']}"
        )

        row = {
            group_column: value
        }

        row.update(
            metrics
        )

        results.append(
            row
        )

    pl.DataFrame(
        results
    ).write_csv(
        report_folder /
        report_name
    )