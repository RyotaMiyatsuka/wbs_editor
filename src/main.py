from pathlib import Path

import polars as pl

from libs.models.calender import Calender
from libs.models.employee import Employee
from libs.models.task import Task
from libs.wbs_editor.wbs_service import WbsService


def main():
    print("Hello from wbs-editor!")


if __name__ == "__main__":
    sample_data_dirpath = Path("/home/ryotamiyatsuka/dev/wbs_editor/sample_data")
    calender_list = [
        Calender(**row)
        for row in pl.read_csv(sample_data_dirpath / "calendar.csv").iter_rows(
            named=True
        )
    ]
    employees = [
        Employee(**row)
        for row in pl.read_csv(sample_data_dirpath / "employees.csv").iter_rows(
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
    [print(row) for row in result]
