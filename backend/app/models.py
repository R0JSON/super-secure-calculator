import enum
import html
import uuid
from typing import Literal
from datetime import datetime
from pydantic import EmailStr, field_validator

from sqlmodel import Field, Relationship, SQLModel

# Public API for mypy
__all__ = [
    "UserBase",
    "UserCreate",
    "UserRegister",
    "UserUpdate",
    "UserUpdateMe",
    "UpdatePassword",
    "User",
    "UserPublic",
    "UserPublicLimited",
    "UsersPublic",
    "OperationType",
    "CalculationBase",
    "CalculationCreate",
    "CalculationUpdate",
    "Calculation",
    "CalculationPublic",
    "CalculationWithPosts",
    "CalculationsPublic",
    "Message",
    "Token",
    "TokenPayload",
    "NewPassword",
    "PostBase",
    "PostCreate",
    "PostUpdate",
    "Post",
    "PostPublic",
    "PostWithCalculation",
    "PostWithDetails",
    "PostsPublic",
    "PostPublicWithOwner",
    "PostsPublicWithOwners",
    "CommentBase",
    "CommentCreate",
    "Comment",
    "CommentPublic",
    "CommentWithOwner",
    "CommentsPublic",
    "CommentsPublicWithOwners",
]

# --- USER MODELS ---


class UserBase(SQLModel):
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    is_active: bool = True
    is_superuser: bool = False
    full_name: str | None = Field(default=None, max_length=255)


class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=40)


class UserRegister(SQLModel):
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8, max_length=40)
    full_name: str | None = Field(default=None, max_length=255)


class UserUpdate(UserBase):
    email: EmailStr | None = Field(default=None, max_length=255)  # type: ignore
    password: str | None = Field(default=None, min_length=8, max_length=40)


class UserUpdateMe(SQLModel):
    full_name: str | None = Field(default=None, max_length=255)
    email: EmailStr | None = Field(default=None, max_length=255)


class UpdatePassword(SQLModel):
    current_password: str = Field(min_length=8, max_length=40)
    new_password: str = Field(min_length=8, max_length=40)


class User(UserBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: str

    calculations: list["Calculation"] = Relationship(
        back_populates="owner", cascade_delete=True, default_factory=list
    )
    posts: list["Post"] = Relationship(
        back_populates="owner", cascade_delete=True, default_factory=list
    )
    comments: list["Comment"] = Relationship(
        back_populates="owner", cascade_delete=True, default_factory=list
    )


class UserPublic(UserBase):
    id: uuid.UUID


class UserPublicLimited(SQLModel):
    id: uuid.UUID
    full_name: str | None = None


class UsersPublic(SQLModel):
    data: list[UserPublic]
    count: int


# --- CALCULATION MODELS ---


class OperationType(str, enum.Enum):
    add = "add"
    sub = "sub"
    mul = "mul"
    div = "div"


class CalculationBase(SQLModel):
    result: int | None = None
    operand_a: int | None = None
    operand_b: int | None = None
    operation: OperationType | None = None


class CalculationCreate(SQLModel):
    operand_a: int
    operand_b: int
    operation: OperationType


class CalculationUpdate(SQLModel):
    operand_a: int | None = None
    operand_b: int | None = None
    operation: OperationType | None = None


class Calculation(CalculationBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    owner_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE"
    )

    owner: "User" = Relationship(back_populates="calculations")
    posts: list["Post"] = Relationship(
        back_populates="calculation", cascade_delete=True, default_factory=list
    )


class CalculationPublic(CalculationBase):
    id: uuid.UUID
    owner_id: uuid.UUID


class CalculationWithPosts(CalculationPublic):
    posts: list["PostPublic"] = Field(default_factory=list)


class CalculationsPublic(SQLModel):
    data: list[CalculationPublic]
    count: int


# --- MESSAGE TOKENS ---


class Message(SQLModel):
    message: str


class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"


class TokenPayload(SQLModel):
    sub: str | None = None


class NewPassword(SQLModel):
    token: str
    new_password: str = Field(min_length=8, max_length=40)


# --- POST MODELS ---


class PostBase(SQLModel):
    title: str = Field(max_length=255)
    description: str | None = Field(default=None, max_length=500)
    created_at: datetime | None = Field(default_factory=datetime.utcnow)


class PostCreate(PostBase):
    calculation_id: uuid.UUID


class PostUpdate(SQLModel):
    title: str | None = Field(default=None, max_length=255)
    description: str | None = Field(default=None, max_length=500)


class Post(PostBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    owner_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE"
    )
    calculation_id: uuid.UUID = Field(
        foreign_key="calculation.id", nullable=False, ondelete="CASCADE"
    )

    owner: "User" = Relationship(back_populates="posts")
    calculation: "Calculation" = Relationship(back_populates="posts")
    comments: list["Comment"] = Relationship(
        back_populates="post", cascade_delete=True, default_factory=list
    )


class PostPublic(PostBase):
    id: uuid.UUID
    owner_id: uuid.UUID
    calculation_id: uuid.UUID


class PostWithCalculation(PostPublic):
    calculation: "CalculationPublic | None" = None


class PostWithDetails(PostWithCalculation):
    comments: list["CommentPublic"] = Field(default_factory=list)
    owner: "UserPublic | None" = None


class PostsPublic(SQLModel):
    data: list[PostPublic]
    count: int


class PostPublicWithOwner(PostPublic):
    owner: "UserPublicLimited | None" = None


class PostsPublicWithOwners(SQLModel):
    data: list[PostPublicWithOwner]
    count: int


# --- COMMENT MODELS ---


class CommentBase(SQLModel):
    content: str = Field(max_length=1000)
    created_at: datetime | None = Field(default_factory=datetime.utcnow)


class CommentCreate(CommentBase):
    post_id: uuid.UUID

    @field_validator("content")
    @classmethod
    def validate_content_not_empty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Comment content cannot be empty")
        if len(v) > 1000:
            raise ValueError("Comment content cannot exceed 1000 characters")
        return v


class Comment(CommentBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    post_id: uuid.UUID = Field(
        foreign_key="post.id", nullable=False, ondelete="CASCADE"
    )
    owner_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE"
    )

    post: "Post" = Relationship(back_populates="comments")
    owner: "User" = Relationship(back_populates="comments")


class CommentPublic(CommentBase):
    id: uuid.UUID
    post_id: uuid.UUID
    owner_id: uuid.UUID


class CommentWithOwner(CommentPublic):
    owner: "UserPublicLimited | None" = None


class CommentsPublic(SQLModel):
    data: list[CommentPublic]
    count: int


class CommentsPublicWithOwners(SQLModel):
    data: list[CommentWithOwner]
    count: int
