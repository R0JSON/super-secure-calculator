import uuid
import enum
from typing import Literal
from pydantic import EmailStr
from sqlmodel import Field, Relationship, SQLModel


# Shared properties
class UserBase(SQLModel):
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    is_active: bool = True
    is_superuser: bool = False
    full_name: str | None = Field(default=None, max_length=255)


# Properties to receive via API on creation
class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=40)


class UserRegister(SQLModel):
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8, max_length=40)
    full_name: str | None = Field(default=None, max_length=255)


# Properties to receive via API on update, all are optional
class UserUpdate(UserBase):
    email: EmailStr | None = Field(default=None, max_length=255)  # type: ignore
    password: str | None = Field(default=None, min_length=8, max_length=40)


class UserUpdateMe(SQLModel):
    full_name: str | None = Field(default=None, max_length=255)
    email: EmailStr | None = Field(default=None, max_length=255)


class UpdatePassword(SQLModel):
    current_password: str = Field(min_length=8, max_length=40)
    new_password: str = Field(min_length=8, max_length=40)


# Database model, database table inferred from class name
class User(UserBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: str
    calculations: list["Calculation"] = Relationship(back_populates="owner", cascade_delete=True)
    posts: list["Post"] = Relationship(back_populates="owner", cascade_delete=True)
    comments: list["Comment"] = Relationship(back_populates="owner", cascade_delete=True)

# Properties to return via API, id is always required
class UserPublic(UserBase):
    id: uuid.UUID


class UsersPublic(SQLModel):
    data: list[UserPublic]
    count: int

class OperationType(str, enum.Enum):
    add = "add"
    sub = "sub"
    mul = "mul"
    div = "div"

# Shared properties
class CalculationBase(SQLModel):
    result: int | None = Field(default=None)
    operand_a: int | None = Field(default=None)
    operand_b: int | None = Field(default=None)
    operation: OperationType | None = Field(default=None)

# Properties to receive on item creation
class CalculationCreate(SQLModel):
    operand_a: int
    operand_b: int
    operation: OperationType

# Properties to receive on item update
class CalculationUpdate(SQLModel):
    operand_a: int | None = None
    operand_b: int | None = None
    operation: OperationType | None = None

# Database model, database table inferred from class name
class Calculation(CalculationBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    owner_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE"
    )
    owner: User | None = Relationship(back_populates="calculations")
    posts: list["Post"] = Relationship(back_populates="calculation", cascade_delete=True)


# Properties to return via API, id is always required
class CalculationPublic(CalculationBase):
    id: uuid.UUID
    owner_id: uuid.UUID


class CalculationWithPosts(CalculationPublic):
    posts: list["PostPublic"] = []


class CalculationsPublic(SQLModel):
    data: list[CalculationPublic]
    count: int


# Generic message
class Message(SQLModel):
    message: str


# JSON payload containing access token
class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"


# Contents of JWT token
class TokenPayload(SQLModel):
    sub: str | None = None


class NewPassword(SQLModel):
    token: str
    new_password: str = Field(min_length=8, max_length=40)

from datetime import datetime

class PostBase(SQLModel):
    title: str = Field(max_length=255)
    description: str | None = Field(default=None, max_length=500)  # Optional description about the calculation
    created_at: datetime | None = Field(default_factory=datetime.utcnow)


class PostCreate(PostBase):
    calculation_id: uuid.UUID  # Post must be associated with a calculation


class PostUpdate(SQLModel):
    title: str | None = Field(default=None, max_length=255)
    description: str | None = Field(default=None, max_length=500)


class Post(PostBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    owner_id: uuid.UUID = Field(foreign_key="user.id", nullable=False, ondelete="CASCADE")
    calculation_id: uuid.UUID = Field(foreign_key="calculation.id", nullable=False, ondelete="CASCADE")

    owner: User | None = Relationship(back_populates="posts")
    calculation: Calculation | None = Relationship(back_populates="posts")
    comments: list["Comment"] = Relationship(back_populates="post", cascade_delete=True)


class PostPublic(PostBase):
    id: uuid.UUID
    owner_id: uuid.UUID
    calculation_id: uuid.UUID


class PostWithCalculation(PostPublic):
    calculation: CalculationPublic | None = None


class PostWithDetails(PostWithCalculation):
    comments: list["CommentPublic"] = []
    owner: UserPublic | None = None


class PostsPublic(SQLModel):
    data: list[PostPublic]
    count: int


# --- Comment Models ---

class CommentBase(SQLModel):
    content: str = Field(max_length=1000)
    created_at: datetime | None = Field(default_factory=datetime.utcnow)


class CommentCreate(CommentBase):
    post_id: uuid.UUID


class Comment(CommentBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    post_id: uuid.UUID = Field(foreign_key="post.id", nullable=False, ondelete="CASCADE")
    owner_id: uuid.UUID = Field(foreign_key="user.id", nullable=False, ondelete="CASCADE")

    post: Post | None = Relationship(back_populates="comments")
    owner: User | None = Relationship(back_populates="comments")


class CommentPublic(CommentBase):
    id: uuid.UUID
    post_id: uuid.UUID
    owner_id: uuid.UUID


class CommentWithOwner(CommentPublic):
    owner: UserPublic | None = None


class CommentsPublic(SQLModel):
    data: list[CommentPublic]
    count: int