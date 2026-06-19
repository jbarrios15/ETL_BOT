import os
import numpy as np
import pandas as pd
import polars as pl

from pathlib import Path

from sklearn.tree import (
    DecisionTreeClassifier,
    export_text
)

from sklearn.preprocessing import (
    OneHotEncoder
)


def train_tree(
    df,
    output_file,
    tree_name
):

    if len(df) < 100:

        print(
            f"{tree_name}: muy pocos registros"
        )

        return

    numeric_features = [

        "rsi",
        "ema_distance",
        "volatility_pct",
        "atr",
        "call_score",
        "put_score",
        "trade_hour",
        "duration_seconds"

    ]

    categorical_features = [

        "setup_type",
        "strategy_version",
        "symbol",
        "direction"

    ]

    target = "is_win"

    df = (

        df

        .drop_nulls(
            numeric_features
            +
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

    X_cat = encoder.fit_transform(

        pdf[
            categorical_features
        ]

    )

    X_num = pdf[
        numeric_features
    ].values

    X = np.hstack(
        [
            X_num,
            X_cat
        ]
    )

    y = pdf[
        target
    ]

    feature_names = (

        numeric_features

        +

        list(

            encoder.get_feature_names_out(
                categorical_features
            )

        )

    )

    tree = DecisionTreeClassifier(

        max_depth=4,

        min_samples_leaf=50,

        random_state=42

    )

    tree.fit(
        X,
        y
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

    print()

    print(
        f"{tree_name} generado"
    )

    print(
        output_file
    )


def run_tree_pattern_analysis(
    df,
    report_folder
):

    print()
    print("=" * 60)
    print("TREE PATTERN ANALYSIS")
    print("=" * 60)

    tree_folder = (

        report_folder

        /

        "tree_pattern_analysis"

    )

    tree_folder.mkdir(
        parents=True,
        exist_ok=True
    )

    configs = [

        (
            "v3_cooldown",
            "balanced_rebound",
            "decision_tree_v3_balanced.txt"
        ),

        (
            "v3_cooldown",
            "extreme_reversion",
            "decision_tree_v3_extreme.txt"
        ),

        (
            "v4_ema20",
            "balanced_rebound",
            "decision_tree_v4_balanced.txt"
        ),

        (
            "v4_ema20",
            "extreme_reversion",
            "decision_tree_v4_extreme.txt"
        )

    ]

    for version, setup, filename in configs:

        subset = (

            df.filter(

                (pl.col("strategy_version") == version)

                &

                (pl.col("setup_type") == setup)

            )

        )

        print()

        print(
            f"Procesando: "
            f"{version} | {setup}"
        )

        print(
            f"Trades: {len(subset)}"
        )

        train_tree(

            subset,

            tree_folder
            /
            filename,

            f"{version} | {setup}"

        )

    print()
    print(
        "Tree Analysis Finalizado"
    )