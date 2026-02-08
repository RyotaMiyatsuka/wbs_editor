from pydantic import BaseModel, model_validator

from libs.defines.constants import HOURS_PER_DAY


class Calender(BaseModel):
    employee_id: str
    date: str
    day_of_week: str
    available_days: float
    available_hours: float | None = None

    @model_validator(mode="after")
    def compute_available_hours(self) -> "Calender":
        if self.available_hours is None:
            self.available_hours = self.available_days * HOURS_PER_DAY
        return self
