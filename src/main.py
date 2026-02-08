from pathlib import Path

import polars as pl

from libs.models.calender import Calender
from libs.models.task import Task
from libs.wbs_editor.wbs_service import WbsService

if __name__ == "__main__":
    sample_data_dirpath = Path("./sample_data")
    calender_list = [
        Calender(**row)
        for row in pl.read_csv(sample_data_dirpath / "calendar.csv").iter_rows(
            named=True
        )
    ]
    tasks = [
        Task(**row)
        for row in pl.read_csv(sample_data_dirpath / "tasks.csv").iter_rows(named=True)
    ]
    wbs_service = WbsService()
    result = wbs_service.build_schedule(
        task_list=tasks, calender_list=calender_list, start_date="2025-01-01"
    )
    df = pl.DataFrame([row.model_dump() for row in result])
    print(df)
    df.write_csv(".data/output.csv", include_bom=True)
