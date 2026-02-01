from datetime import datetime

from libs.defines.constants import DATE_FORMAT
from libs.models.calender import Calender
from libs.models.task import Task


class WbsService:
    """WBS編集機."""

    def build_schedule(
        self,
        task_list: list[Task],
        calender_list: list[Calender],
        start_date: str,
    ) -> list[Task]:
        """情報から予定日を埋める.

        Args:
            task_list: タスク一覧
            calender_list: カレンダー一覧
            start_date: スケジューリング開始日

        Returns:
            開始日・終了日が設定されたタスク一覧

        """
        employee_calendar = self._build_employee_calendar(calender_list)
        employee_next_date_index = self._init_employee_next_date_index(
            employee_calendar, start_date
        )

        completed_tasks: set[str] = set()
        result_tasks: list[Task] = []

        while len(completed_tasks) < len(task_list):
            available_tasks = self._get_available_tasks(task_list, completed_tasks)

            if not available_tasks:
                break

            available_tasks.sort(key=lambda t: t.priority)

            for task in available_tasks:
                if task.task_id in completed_tasks:
                    continue

                earliest_start = self._get_earliest_start_date(
                    task, result_tasks, start_date
                )

                scheduled_task = self._schedule_task(
                    task,
                    earliest_start,
                    employee_calendar,
                    employee_next_date_index,
                )

                if scheduled_task:
                    result_tasks.append(scheduled_task)
                    completed_tasks.add(task.task_id)

        return result_tasks

    def _build_employee_calendar(
        self, calender_list: list[Calender]
    ) -> dict[str, list[Calender]]:
        """担当者ごとのカレンダー情報を整理する."""
        employee_calendar: dict[str, list[Calender]] = {}
        for cal in calender_list:
            if cal.employee_id not in employee_calendar:
                employee_calendar[cal.employee_id] = []
            employee_calendar[cal.employee_id].append(cal)

        for emp_id, calendars in employee_calendar.items():
            calendars.sort(key=lambda c: datetime.strptime(c.date, DATE_FORMAT))

        return employee_calendar

    def _init_employee_next_date_index(
        self,
        employee_calendar: dict[str, list[Calender]],
        start_date: str,
    ) -> dict[str, int]:
        """担当者ごとの次の作業可能日インデックスを初期化する."""
        employee_next_date_index: dict[str, int] = {}
        start_dt = datetime.strptime(start_date, DATE_FORMAT)

        for emp_id, calendars in employee_calendar.items():
            for i, cal in enumerate(calendars):
                cal_dt = datetime.strptime(cal.date, DATE_FORMAT)
                if cal_dt >= start_dt and cal.available_hours > 0:
                    employee_next_date_index[emp_id] = i
                    break
            else:
                employee_next_date_index[emp_id] = len(calendars)

        return employee_next_date_index

    def _get_available_tasks(
        self,
        task_list: list[Task],
        completed_tasks: set[str],
    ) -> list[Task]:
        """処理可能なタスク(先行タスクがすべて完了)を取得."""
        available = []
        for task in task_list:
            if task.task_id in completed_tasks:
                continue

            predecessor_ids = self._parse_predecessor_ids(task.predecessor_task_ids)
            all_predecessors_done = all(
                pid in completed_tasks for pid in predecessor_ids
            )

            if all_predecessors_done:
                available.append(task)

        return available

    def _parse_predecessor_ids(self, predecessor_task_ids: str) -> list[str]:
        """カンマ区切りの先行タスクIDをパースする."""
        if not predecessor_task_ids or predecessor_task_ids.strip() == "":
            return []
        return [pid.strip() for pid in predecessor_task_ids.split(",") if pid.strip()]

    def _get_earliest_start_date(
        self,
        task: Task,
        scheduled_tasks: list[Task],
        default_start: str,
    ) -> str:
        """先行タスクの終了日から最も早い開始可能日を取得する."""
        predecessor_ids = self._parse_predecessor_ids(task.predecessor_task_ids)

        if not predecessor_ids:
            return default_start

        scheduled_map = {t.task_id: t for t in scheduled_tasks}
        latest_end_date = default_start

        for pid in predecessor_ids:
            if pid in scheduled_map and scheduled_map[pid].end_date:
                end_date = scheduled_map[pid].end_date
                if end_date is None:
                    msg = f"Invalid end_date: {end_date}"
                    raise ValueError(msg)
                if datetime.strptime(end_date, DATE_FORMAT) > datetime.strptime(  # noqa: DTZ007
                    latest_end_date, DATE_FORMAT
                ):
                    latest_end_date = end_date

        return latest_end_date

    def _schedule_task(
        self,
        task: Task,
        earliest_start: str,
        employee_calendar: dict[str, list[Calender]],
        employee_next_date_index: dict[str, int],
    ) -> Task | None:
        """タスクをスケジュールし、開始日・終了日を設定する."""
        assignee = task.assignee

        if assignee not in employee_calendar:
            return None

        calendars = employee_calendar[assignee]
        current_index = employee_next_date_index.get(assignee, 0)
        earliest_dt = datetime.strptime(earliest_start, DATE_FORMAT)

        while current_index < len(calendars):
            cal = calendars[current_index]
            cal_dt = datetime.strptime(cal.date, DATE_FORMAT)
            if cal_dt >= earliest_dt and cal.available_hours > 0:
                break
            current_index += 1

        if current_index >= len(calendars):
            return None

        task_start_date = calendars[current_index].date
        remaining_hours = task.estimated_hours
        end_date = task_start_date

        while remaining_hours > 0 and current_index < len(calendars):
            cal = calendars[current_index]
            if cal.available_hours > 0:
                remaining_hours -= cal.available_hours
                end_date = cal.date
            current_index += 1

        employee_next_date_index[assignee] = current_index

        return Task(
            task_id=task.task_id,
            task_name=task.task_name,
            priority=task.priority,
            assignee=task.assignee,
            deadline_date=task.deadline_date,
            estimated_hours=task.estimated_hours,
            predecessor_task_ids=task.predecessor_task_ids,
            start_date=task_start_date,
            end_date=end_date,
        )
