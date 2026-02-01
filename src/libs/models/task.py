from pydantic import BaseModel


class Task(BaseModel):
    task_id: str
    task_name: str
    priority: float
    assignee: str
    deadline_date: str
    estimated_hours: float
    predecessor_task_ids: str | None = ""
    start_date: str | None = None
    end_date: str | None = None
