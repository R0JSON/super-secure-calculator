import uuid
from typing import Any

from fastapi import APIRouter, HTTPException
from sqlmodel import select, func

from app.api.deps import SessionDep, CurrentUser
from app.models import (
    Comment,
    CommentCreate,
    CommentPublic,
    CommentsPublic,
    Message,
)

router = APIRouter(prefix="/comments", tags=["comments"])


@router.get("/", response_model=CommentsPublic)
def read_comments(session: SessionDep, current_user: CurrentUser, skip: int = 0, limit: int = 100) -> Any:
    """
    Retrieve comments.
    """
    if current_user.is_superuser:
        count_statement = select(func.count()).select_from(Comment)
        count = session.exec(count_statement).one()
        statement = select(Comment).offset(skip).limit(limit)
        comments = session.exec(statement).all()
    else:
        count_statement = (
            select(func.count())
            .select_from(Comment)
            .where(Comment.owner_id == current_user.id)
        )
        count = session.exec(count_statement).one()
        statement = (
            select(Comment)
            .where(Comment.owner_id == current_user.id)
            .offset(skip)
            .limit(limit)
        )
        comments = session.exec(statement).all()

    return CommentsPublic(data=comments, count=count)


@router.get("/{id}", response_model=CommentPublic)
def read_comment(session: SessionDep, current_user: CurrentUser, id: uuid.UUID) -> Any:
    """
    Get comment by ID.
    """
    comment = session.get(Comment, id)
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    if not current_user.is_superuser and comment.owner_id != current_user.id:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    return comment


@router.post("/", response_model=CommentPublic)
def create_comment(session: SessionDep, current_user: CurrentUser, comment_in: CommentCreate) -> Any:
    """
    Create a new comment for a post.
    """
    comment = Comment.model_validate(comment_in, update={"owner_id": current_user.id})
    session.add(comment)
    session.commit()
    session.refresh(comment)
    return comment


@router.delete("/{id}", response_model=Message)
def delete_comment(session: SessionDep, current_user: CurrentUser, id: uuid.UUID) -> Any:
    """
    Delete a comment.
    """
    comment = session.get(Comment, id)
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    if not current_user.is_superuser and comment.owner_id != current_user.id:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    session.delete(comment)
    session.commit()
    return Message(message="Comment deleted successfully")
