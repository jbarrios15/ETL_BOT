from pathlib import Path
from datetime import datetime


def get_report_folder():

    today = datetime.now().strftime(
        "%Y%m%d"
    )

    base_folder = Path(
        "reports"
    )

    report_folder = (
        base_folder / today
    )

    counter = 0

    while report_folder.exists():

        counter += 1

        report_folder = (
            base_folder /
            f"{today}_{counter}"
        )

    report_folder.mkdir(
        parents=True,
        exist_ok=True
    )

    return report_folder