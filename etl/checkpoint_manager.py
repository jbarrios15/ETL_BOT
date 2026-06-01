from pathlib import Path
import json


class CheckpointManager:

    def __init__(self, checkpoint_path: str):
        self.checkpoint_path = Path(checkpoint_path)

    def load(self) -> int:

        if not self.checkpoint_path.exists():
            return 0

        with open(
            self.checkpoint_path,
            "r",
            encoding="utf-8"
        ) as f:

            data = json.load(f)

        return data.get(
            "last_processed_line",
            0
        )

    def save(self, line_number: int):

        data = {
            "last_processed_line": line_number
        }

        with open(
            self.checkpoint_path,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                data,
                f,
                indent=4
            )