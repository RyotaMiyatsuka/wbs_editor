from pydantic import BaseModel


class Employee(BaseModel):
    employee_id: str
    name: str
    available_hours_per_day: float
