from __future__ import annotations

import enum
import html
import uuid
from datetime import datetime
from typing import Optional, List

from pydantic import EmailStr, field_validator
from sqlmodel import SQLModel, Field, Relationship


# ========================
# Enums
# ========================


class Role(str, enum.Enum):
    ADMIN = "admin"
    USER = "user"


# ========================
# User
# ========================


class UserBase(SQLModel):
    username: str
    email: EmailStr
    role: Role = Role.USER


class User(UserBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # reverse relationships
    calculations: List["Calculation"] = Relationship(back_populates="user")
    posts: List["Post"] = Relationship(back_populates="user")
    comments: List["Comment"] = Relationship(back_populates="user")


class UserPublic(SQLModel):
    id: uuid.UUID
    username: str
    role: Role


class UserPublicLimited(SQLModel):
    id: uuid.UUID
    username: str


# ========================
# Calculation
# ========================


class CalculationBase(SQLModel):
    expression: str
    result: str


class Calculation(CalculationBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    user_id: uuid.UUID = Field(foreign_key="user.id")
    user: Optional[User] = Relationship(back_populates="calculations")


class CalculationPublic(SQLModel):
    id: uuid.UUID
    expression: str
    result: str
    created_at: datetime
    user: UserPublicLimited


# ========================
# Posts
# ========================


class PostBase(SQLModel):
    title: str
    content: str

    @field_validator("content")
    def sanitize_content(cls, v: str) -> str:
        return html.escape(v)


class Post(PostBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    user_id: uuid.UUID = Field(foreign_key="user.id")
    user: Optional[User] = Relationship(back_populates="posts")

    comments: List["Comment"] = Relationship(back_populates="post")


class PostPublic(SQLModel):
    id: uuid.UUID
    title: str
    content: str
    created_at: datetime
    user: UserPublicLimited


# ========================
# Comments
# ========================


class CommentBase(SQLModel):
    content: str

    @field_validator("content")
    def sanitize_content(cls, v: str) -> str:
        return html.escape(v)


class Comment(CommentBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    user_id: uuid.UUID = Field(foreign_key="user.id")
    post_id: uuid.UUID = Field(foreign_key="post.id")

    user: Optional[User] = Relationship(back_populates="comments")
    post: Optional[Post] = Relationship(back_populates="comments")


class CommentPublic(SQLModel):
    id: uuid.UUID
    content: str
    created_at: datetime
    user: UserPublicLimited
