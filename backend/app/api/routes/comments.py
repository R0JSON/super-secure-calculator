import uuid
from typing import Any

from fastapi import APIRouter, HTTPException
from sqlmodel import select, func
import re
import html
from fastapi import APIRouter, HTTPException
from sqlmodel import select, func
from app.api.deps import SessionDep, CurrentUser
from app.models import (
    Comment,
    CommentCreate,
    CommentPublic,
    CommentWithOwner,
    CommentsPublic,
    Message,
    Post,
    User,
    UserPublicLimited,
    CommentsPublicWithOwners,
)

router = APIRouter(prefix="/comments", tags=["comments"])


def sanitize_comment_content(content: str) -> str:
    """
    Sanitize comment content to prevent XSS and other attacks.
    """
    if not content:
        return content

    # Remove leading/trailing whitespace
    content = content.strip()

    # Basic HTML escaping
    content = html.escape(content)

    # Remove potentially dangerous patterns
    # Remove script tags and event handlers
    dangerous_patterns = [
        r'<script.*?>.*?</script>',
        r'on\w+\s*=',
        r'javascript:',
        r'vbscript:',
        r'expression\s*\(',
        r'url\s*\(',
    ]

    for pattern in dangerous_patterns:
        content = re.sub(pattern, '', content, flags=re.IGNORECASE)

    # Limit consecutive spaces
    content = re.sub(r' {2,}', ' ', content)

    # Limit consecutive newlines (keep max 2)
    content = re.sub(r'\n{3,}', '\n\n', content)

    return content

@router.get("/post/{post_id}", response_model=CommentsPublicWithOwners)  # Changed response model
def read_comments_for_post(
        session: SessionDep, post_id: uuid.UUID, skip: int = 0, limit: int = 100
) -> Any:
    """
    Retrieve comments for a specific post.
    """
    # Verify the post exists
    post = session.get(Post, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    count_statement = (
        select(func.count())
        .select_from(Comment)
        .where(Comment.post_id == post_id)
    )
    count = session.exec(count_statement).one()

    statement = (
        select(Comment)
        .where(Comment.post_id == post_id)
        .join(User, Comment.owner_id == User.id)
        .offset(skip)
        .limit(limit)
        .order_by(Comment.created_at.asc())
    )
    comments = session.exec(statement).all()

    # Convert to public response with limited owner info
    comments_public = []
    for comment in comments:
        comment_public = CommentWithOwner(
            id=comment.id,
            content=comment.content,
            created_at=comment.created_at,
            post_id=comment.post_id,
            owner_id=comment.owner_id,
            owner=UserPublicLimited(
                id=comment.owner.id,
                full_name=comment.owner.full_name
            )
        )
        comments_public.append(comment_public)

    return CommentsPublicWithOwners(data=comments_public, count=count)  # Use new model


@router.post("/", response_model=CommentWithOwner)
def create_comment(
        session: SessionDep, current_user: CurrentUser, comment_in: CommentCreate
) -> Any:
    """
    Create a new comment.
    """
    # Verify the post exists
    post = session.get(Post, comment_in.post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    # Sanitize content before creating comment
    sanitized_content = sanitize_comment_content(comment_in.content)

    # Create comment with sanitized content
    comment_data = {
        "content": sanitized_content,
        "post_id": comment_in.post_id
    }

    comment = Comment.model_validate(
        comment_data, update={"owner_id": current_user.id}
    )
    session.add(comment)
    session.commit()
    session.refresh(comment)

    # Refresh to get the owner relationship loaded
    session.refresh(comment.owner)

    return CommentWithOwner(
        id=comment.id,
        content=comment.content,
        created_at=comment.created_at,
        post_id=comment.post_id,
        owner_id=comment.owner_id,
        owner=UserPublicLimited(
            id=comment.owner.id,
            full_name=comment.owner.full_name
        )
    )


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