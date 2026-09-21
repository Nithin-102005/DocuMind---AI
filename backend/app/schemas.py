from datetime import datetime

from pydantic import BaseModel, EmailStr


# -------------------------
# User Schemas
# -------------------------

class UserCreate(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime

    model_config = {
        "from_attributes": True
    }


# -------------------------
# Authentication Schemas
# -------------------------

class Token(BaseModel):
    access_token: str
    token_type: str


# -------------------------
# Document Schemas
# -------------------------

class DocumentCreate(BaseModel):
    filename: str
    content: str


class DocumentUpdate(BaseModel):
    filename: str
    content: str
class ChatRequest(BaseModel):
    question: str