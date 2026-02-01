from pydantic import BaseModel


class Calender(BaseModel):
    employee_id: str
    date: str
    day_of_week: str
    available_hours: float
