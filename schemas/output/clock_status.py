from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class ClockStatus(BaseModel):
    """
    Current clock-in state for an employee.

    Returned by the status endpoint to tell the frontend
    whether to show "Clock In" or "Clock Out" button.
    """
    is_clocked_in: bool
    clock_in_time: Optional[datetime] = None