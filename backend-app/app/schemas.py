from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    password: str
    is_admin: bool = False
    is_staff: bool = False  # <-- ДОБАВЛЕНО: чтобы при создании можно было назначить сотрудника

class UserResponse(UserBase):
    id: int
    is_admin: bool
    is_staff: bool          # <-- ДОБАВЛЕНО: чтобы фронтенд знал роль пользователя
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

# ДОБАВЛЕНО: Новая схема для редактирования заявки
class TicketUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None  # Именно это поле будет менять сотрудник

class TicketResponse(BaseModel):
    id: int
    title: str
    description: str
    status: str
    creator_id: int
    assignee_id: Optional[int]
    created_at: datetime     # Это поле у тебя уже было, оно будет отдавать дату и время
    class Config:
        from_attributes = True