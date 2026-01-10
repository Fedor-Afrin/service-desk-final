from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    password: str
    is_admin: bool = False

class UserResponse(UserBase):
    id: int
    is_admin: bool
    class Config:
        from_attributes = True

class ReportResponse(BaseModel):
    id: int
    comment: Optional[str]
    file_path: Optional[str]
    created_at: datetime
    class Config:
        from_attributes = True

class TicketCreate(BaseModel):
    title: str
    description: str
    creator_id: int

class TicketResponse(BaseModel):
    id: int
    title: str
    description: str
    status: str
    creator_id: int
    assignee_id: Optional[int]
    created_at: datetime
    class Config:
        from_attributes = True
