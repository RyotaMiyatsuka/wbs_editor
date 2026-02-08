from pydantic import BaseModel, model_validator

from libs.defines.constants import HOURS_PER_DAY


class Task(BaseModel):
    task_id: str
    task_name: str
    priority: float
    assignee: str
    deadline_date: str
    estimated_days: float
    estimated_hours: float | None = None
    predecessor_task_ids: str | None = ""
    start_date: str | None = None
    end_date: str | None = None

    @model_validator(mode="after")
    def compute_estimated_hours(self) -> "Task":
        if self.estimated_hours is None:
            self.estimated_hours = self.estimated_days * HOURS_PER_DAY
        return self
