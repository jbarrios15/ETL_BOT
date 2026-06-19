import numpy as np
import polars as pl

from sklearn.tree import (
    DecisionTreeClassifier,
    export_text
)

from sklearn.preprocessing import (
    OneHotEncoder
)

def calculate_metrics(
    df
):

    trades = len(df)

    if trades == 0:

        return None


    wins = (

        df["is_win"]
        .sum()

    )


    losses = (

        trades
        -
        wins

    )


    profit = (

        df["profit"]
        .sum()

    )


    win_profit = (

        df

        .filter(

            pl.col("profit") > 0

        )

        ["profit"]

        .sum()

    )


    loss_profit = abs(

        df

        .filter(

            pl.col("profit") < 0)

        ["profit"]

        .sum()

    )


    if loss_profit == 0:

        profit_factor = 999

    else:

        profit_factor = (

            win_profit
            /
            loss_profit

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
            profit_factor,
            2
        )

    }

def extract_leaf_metrics(
    tree,
    X,
    original_df,
    tree_name
):

    leaf_ids = (

        tree.apply(X)

    )


    temp = (

        original_df

        .with_columns(

            pl.Series(
                "leaf_id",
                leaf_ids
            )

        )

    )


    results = []


    for leaf in (

        temp

        .select("leaf_id")

        .unique()

        .to_series()

        .to_list()

    ):


        leaf_df = (

            temp.filter(

                pl.col("leaf_id")
                ==
                leaf

            )

        )


        metrics = calculate_metrics(

            leaf_df

        )


        if metrics:


            row = {

                "tree": tree_name,

                "leaf_id": leaf,

                **metrics

            }


            results.append(row)


    return results

def train_operational_tree(
    df,
    output_file,
    tree_name
):

    if len(df) < 100:

        print(
            f"{tree_name}: pocos registros"
        )

        return

    df = df.with_columns(

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

    categorical_features = [

        "setup_type",
        "strategy_version",
        "symbol",
        "direction",
        "trade_hour",
        "volatility_bucket"

    ]

    target = "is_win"

    df = (

        df

        .drop_nulls(
            categorical_features
            +
            [target]
        )

    )

    pdf = df.to_pandas()

    encoder = OneHotEncoder(

        handle_unknown="ignore",

        sparse_output=False

    )

    X = encoder.fit_transform(

        pdf[
            categorical_features
        ]

    )

    y = pdf[
        target
    ]

    feature_names = list(

        encoder.get_feature_names_out(
            categorical_features
        )

    )

    tree = DecisionTreeClassifier(

        max_depth=5,

        min_samples_leaf=100,

        random_state=42

    )

    tree.fit(
        X,
        y
    )

    leaf_results = extract_leaf_metrics(

        tree,

        X,

        df,

        tree_name

    )

    rules = export_text(

        tree,

        feature_names=feature_names

    )

    with open(
        output_file,
        "w",
        encoding="utf-8"
    ) as f:

        f.write(
            f"{tree_name}\n"
        )

        f.write(
            "=" * 80
        )

        f.write("\n\n")

        f.write(
            rules
        )

    print(
        f"{tree_name} generado"
    )

    return leaf_results


def run_operational_tree_analysis(
    df,
    report_folder
):
    

    print()
    print("=" * 60)
    print("OPERATIONAL TREE ANALYSIS")
    print("=" * 60)

    print(">>> EJECUTANDO VERSION V2 CON LEAF RANKING <<<")

    tree_folder = (

        report_folder

        /

        "tree_operational_analysis"

    )

    tree_folder.mkdir(
        parents=True,
        exist_ok=True
    )

    all_leafs = []

    # ============================================
    # GLOBAL
    # ============================================

    results = train_operational_tree(

        df,

        tree_folder
        /
        "decision_tree_operational_global.txt",

        "OPERATIONAL GLOBAL"

    )


    if results:

        all_leafs.extend(
            results
        )

    # ============================================
    # BALANCED
    # ============================================

    balanced_df = (

        df.filter(

            pl.col("setup_type")
            ==
            "balanced_rebound"

        )

    )

    results = train_operational_tree(

        balanced_df,

        tree_folder
        /
        "decision_tree_operational_balanced.txt",

        "OPERATIONAL BALANCED"

    )


    if results:

        all_leafs.extend(
            results
        )

    # ============================================
    # EXTREME
    # ============================================

    extreme_df = (

        df.filter(

            pl.col("setup_type")
            ==
            "extreme_reversion"

        )

    )

    results = train_operational_tree(

        extreme_df,

        tree_folder
        /
        "decision_tree_operational_extreme.txt",

        "OPERATIONAL EXTREME"

    )


    if results:

        all_leafs.extend(
            results
        )

    # ============================================
    # LEAF RANKING CSV
    # ============================================

    print(
        "TOTAL LEAFS GENERADAS:",
        len(all_leafs)
    )


    if len(all_leafs) > 0:

        leaf_df = (

            pl.DataFrame(
                all_leafs
            )

            .sort(

                by=[

                    "profit_factor",

                    "profit",

                    "winrate"

                ],

                descending=True

            )

        )


        leaf_df.write_csv(

            tree_folder

            /

            "tree_leaf_ranking.csv"

        )


        print(

            "Archivo generado:",

            tree_folder

            /

            "tree_leaf_ranking.csv"

        )

    print()
    print(
        "Operational Tree Analysis Finalizado"
    )