"""
Database Schemas for Atomik (Teen-to-Teen EdTech)

Each Pydantic model represents a collection in MongoDB.
The collection name is the lowercase of the class name.
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List

class Tutorprofile(BaseModel):
    """
    Peer tutor profiles available for booking.
    Collection: "tutorprofile"
    """
    name: str = Field(..., description="Tutor full name")
    grade_levels: List[int] = Field(..., description="Grades the tutor can teach (8-12)")
    subjects: List[str] = Field(..., description="Subjects the tutor teaches")
    bio: Optional[str] = Field(None, description="Short introduction")
    availability: Optional[str] = Field(None, description="General availability notes")
    rating: Optional[float] = Field(None, ge=0, le=5, description="Average rating out of 5")

class Teachercandidate(BaseModel):
    """
    Candidates applying to become tutors via aptitude test.
    Collection: "teachercandidate"
    """
    name: str = Field(...)
    email: EmailStr = Field(...)
    grade: int = Field(..., ge=8, le=12)
    subjects: List[str] = Field(...)
    motivation: Optional[str] = Field(None, description="Why they want to teach")
    score: Optional[int] = Field(None, ge=0)
    status: Optional[str] = Field(None, description="pending | passed | needs-review | rejected")

# Note: You can extend with more collections such as Session, Booking, Feedback, etc.
