import json
from json import JSONDecoder
from pathlib import Path

import polars as pl

from checkpoint_manager import CheckpointManager
from datetime import datetime

class BronzeToSilverETL:

    def __init__(self):

        self.bronze_file = (
            "data/bronze/trades.jsonl"
        )

        self.silver_file = (
            "data/silver/trades.parquet"
        )

        self.checkpoint = CheckpointManager(
            "data/metadata/checkpoint.json"
        )

        self.records = []
        self.trades = []

        self.last_read_line = 0

        self.max_processed_line = 0

    def extract(self):

        decoder = JSONDecoder()

        last_line = self.checkpoint.load()

        print(
            f"Checkpoint encontrado: {last_line}"
        )

        current_line = 0

        with open(
            self.bronze_file,
            "r",
            encoding="utf-8"
        ) as f:

            for current_line, line in enumerate(
                f,
                start=1
            ):

                if current_line <= last_line:
                    continue

                line = line.strip()

                if not line:
                    continue

                try:

                    while line:

                        obj, idx = decoder.raw_decode(
                            line
                        )

                        obj["_line_number"] = current_line

                        self.records.append(
                            obj
                        )

                        line = line[idx:].strip()

                except Exception as e:

                    print(
                        f"\nError procesando línea {current_line}"
                    )

                    print(
                        line[:500]
                    )

                    raise e

        self.last_read_line = current_line

        print(
            f"Registros nuevos: {len(self.records)}"
        )

    def transform(self):

        open_trades = {}

        completed_trades = []

        for record in self.records:

            event = record.get(
                "event"
            )

            trade_id = record.get(
                "trade_id"
            )

            if not trade_id:
                continue

            if event == "OPEN":

                open_trades[
                    trade_id
                ] = record

            elif event == "CLOSE":

                open_record = (
                    open_trades.get(
                        trade_id
                    )
                )

                if not open_record:
                    continue

                trade = (
                    open_record.copy()
                )

                trade["result"] = record.get("result")
                trade["profit"] = record.get("profit")
                trade["close_time"] = record.get("close_time")

                # ==========================
                # FECHAS
                # ==========================

                open_dt = datetime.fromisoformat(
                    trade["open_time"]
                )

                close_dt = datetime.fromisoformat(
                    trade["close_time"]
                )

                trade["trade_date"] = (
                    open_dt.date()
                )

                trade["trade_date_key"] = int(
                    open_dt.strftime("%Y%m%d")
                )

                trade["trade_hour"] = (
                    open_dt.hour
                )

                trade["trade_weekday"] = (
                    open_dt.weekday()
                )

                trade["trade_month"] = (
                    open_dt.month
                )

                trade["trade_year"] = (
                    open_dt.year
                )

                trade["duration_seconds"] = int(
                    (close_dt - open_dt).total_seconds()
                )

                # ==========================
                # ELIMINAR COLUMNAS
                # ==========================

                trade.pop("event", None)
                trade.pop("event_time", None)
                trade.pop("status", None)

                close_line = record.get(
                    "_line_number",
                    0
                )

                if close_line > self.max_processed_line:
                    self.max_processed_line = close_line    

                completed_trades.append(
                    trade
                )

        self.trades = (
            completed_trades
        )

        print(
            f"Trades completos: {len(self.trades)}"
        )

    def load(self):

        if not self.trades:

            print(
                "No hay trades para guardar."
            )
            return

        df = pl.DataFrame(
            self.trades
        )

        df = df.with_columns([
            pl.col("amount").cast(pl.Float64),
            pl.col("profit").cast(pl.Float64),
            pl.col("entry_price").cast(pl.Float64),
            pl.col("rsi").cast(pl.Float64),
            pl.col("ema").cast(pl.Float64),
            pl.col("atr").cast(pl.Float64),
            pl.col("bb_upper").cast(pl.Float64),
            pl.col("bb_lower").cast(pl.Float64),
            pl.col("volatility_pct").cast(pl.Float64),
            pl.col("ema_distance").cast(pl.Float64),
        ])

        df = df.with_columns(
            [
                pl.col("open_time")
                .str.to_datetime(),

                pl.col("close_time")
                .str.to_datetime()
            ]
        )

        df = df.with_columns(
            (
                pl.col("result") == "win"
            )
            .cast(pl.Int8)
            .alias("is_win")
        )

        silver_path = Path(
            self.silver_file
        )

        silver_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        if silver_path.exists():

            existing_df = (
                pl.read_parquet(
                    self.silver_file
                )
            )

            df = pl.concat(
                [
                    existing_df,
                    df
                ],
                how="diagonal"
            )

            df = df.unique(
                subset=["trade_id"]
            )

        df.write_parquet(
            self.silver_file
        )

        print(
            f"Nuevo checkpoint: {self.max_processed_line}"
        )

        self.checkpoint.save(
            self.max_processed_line
        )

        print(
            f"Silver actualizado."
        )

    def run(self):

        self.extract()
        self.transform()
        self.load()