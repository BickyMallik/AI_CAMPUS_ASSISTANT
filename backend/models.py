# models.py — shared Pydantic schemas
# (All schemas are currently defined inline in main.py for simplicity.
#  Refactor here if the project grows.)

from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class GrievanceOut(BaseModel):
    id: int
    student_name: str
    student_roll: str
    department: str
    category: str
    subject: str
    description: str
    contact_email: Optional[str]
    status: str
    admin_remarks: Optional[str]
    submitted_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True
