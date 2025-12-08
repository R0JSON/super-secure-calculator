import html
import re
import uuid
from typing import Any

from fastapi import APIRouter, HTTPException
from sqlmodel import func, select

from app.api.deps import CurrentUser, SessionDep
from app.models import (
    Calculation,
    Comment,
    Message,
    Post,
    PostCreate,
    PostPublic,
    PostPublicWithOwner,
    PostsPublic,
    PostsPublicWithOwners,
    PostUpdate,
    PostWithCalculation,
    PostWithDetails,
    User,
    UserPublicLimited,
)

router = APIRouter(prefix="/posts", tags=["posts"])


def sanitize_description_content(content: str) -> str:
    """
    Sanitize description content to prevent XSS and other attacks.
    """
    if not content:
        return content

    # Remove leading/trailing whitespace
    content = content.strip()

    # Basic HTML escaping - ONLY ONCE
    content = html.escape(content)

    # Remove potentially dangerous patterns
    dangerous_patterns = [
        r"<script.*?>.*?</script>",
        r"on\w+\s*=",
        r"javascript:",
        r"vbscript:",
        r"expression\s*\(",
        r"url\s*\(",
    ]

    for pattern in dangerous_patterns:
        content = re.sub(pattern, "", content, flags=re.IGNORECASE)

    # Limit consecutive spaces
    content = re.sub(r" {2,}", " ", content)

    # Limit consecutive newlines (keep max 2)
    content = re.sub(r"\n{3,}", "\n\n", content)

    return content


@router.get("/public/", response_model=PostsPublicWithOwners)
def read_public_posts(session: SessionDep, skip: int = 0, limit: int = 100) -> Any:
    """
    Retrieve public posts with limited owner information.
    """
    count_statement = select(func.count()).select_from(Post)
    count = session.exec(count_statement).one()

    statement = select(Post).join(User).where(User.is_active).offset(skip).limit(limit)
    posts = session.exec(statement).all()

    posts_with_owners = []
    for post in posts:
        post_with_owner = PostPublicWithOwner(
            id=post.id,
            title=post.title,
            description=post.description,
            created_at=post.created_at,
            owner_id=post.owner_id,
            calculation_id=post.calculation_id,
            owner=UserPublicLimited(
                id=post.owner.id,
                full_name=post.owner.full_name,
                # Don't include email, is_active, is_superuser
            ),
        )
        posts_with_owners.append(post_with_owner)

    return PostsPublicWithOwners(data=posts_with_owners, count=count)


@router.get("/{id}", response_model=PostWithDetails)
def read_post(session: SessionDep, current_user: CurrentUser, id: uuid.UUID) -> Any:
    """
    Get post by ID with calculation and comments details.
    """
    # Get post with calculation and owner
    statement = select(Post).where(Post.id == id).join(Calculation).join(User)
    post = session.exec(statement).first()

    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    if not current_user.is_superuser and post.owner_id != current_user.id:
        raise HTTPException(status_code=400, detail="Not enough permissions")

    # Get comments for this post
    comments_statement = select(Comment).where(Comment.post_id == id).join(User)
    comments = session.exec(comments_statement).all()

    # Convert to response model with nested data
    post_details = PostWithDetails(
        id=post.id,
        title=post.title,
        description=post.description,
        created_at=post.created_at,
        owner_id=post.owner_id,
        calculation_id=post.calculation_id,
        calculation=post.calculation,
        comments=comments,
        owner=post.owner,
    )

    return post_details


@router.get("/public/{id}", response_model=PostWithCalculation)
def read_public_post(session: SessionDep, id: uuid.UUID) -> Any:
    """
    Get public post by ID with calculation details.
    """
    statement = (
        select(Post)
        .where(Post.id == id)
        .join(Calculation)
        .join(User)
        .where(User.is_active)
    )
    post = session.exec(statement).first()

    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    post_with_calc = PostWithCalculation(
        id=post.id,
        title=post.title,
        description=post.description,
        created_at=post.created_at,
        owner_id=post.owner_id,
        calculation_id=post.calculation_id,
        calculation=post.calculation,
    )

    return post_with_calc


@router.post("/", response_model=PostWithCalculation)
def create_post(
    session: SessionDep, current_user: CurrentUser, post_in: PostCreate
) -> Any:
    """
    Create a new post associated with a calculation.
    """
    # Verify the calculation exists and belongs to the user
    calculation = session.get(Calculation, post_in.calculation_id)
    if not calculation:
        raise HTTPException(status_code=404, detail="Calculation not found")
    if not current_user.is_superuser and calculation.owner_id != current_user.id:
        raise HTTPException(
            status_code=400, detail="Not enough permissions to use this calculation"
        )

    # Sanitize title and description
    sanitized_title = sanitize_description_content(post_in.title)
    sanitized_description = (
        sanitize_description_content(post_in.description)
        if post_in.description
        else None
    )

    # Create the post with sanitized data
    post_data = {
        "title": sanitized_title,
        "description": sanitized_description,
        "calculation_id": post_in.calculation_id,
    }

    post = Post.model_validate(post_data, update={"owner_id": current_user.id})
    session.add(post)
    session.commit()
    session.refresh(post)

    # Refresh to get the calculation relationship loaded
    session.refresh(post.calculation)

    return PostWithCalculation(
        id=post.id,
        title=post.title,
        description=post.description,
        created_at=post.created_at,
        owner_id=post.owner_id,
        calculation_id=post.calculation_id,
        calculation=post.calculation,
    )


@router.put("/{id}", response_model=PostPublic)
def update_post(
    session: SessionDep, current_user: CurrentUser, id: uuid.UUID, post_in: PostUpdate
) -> Any:
    """
    Update a post.
    """
    post = session.get(Post, id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    if not current_user.is_superuser and post.owner_id != current_user.id:
        raise HTTPException(status_code=400, detail="Not enough permissions")

    # Don't allow changing calculation_id through update
    update_data = post_in.model_dump(exclude_unset=True, exclude={"calculation_id"})

    post.sqlmodel_update(update_data)
    session.add(post)
    session.commit()
    session.refresh(post)
    return post


@router.delete("/{id}", response_model=Message)
def delete_post(session: SessionDep, current_user: CurrentUser, id: uuid.UUID) -> Any:
    """
    Delete a post.
    """
    post = session.get(Post, id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    if not current_user.is_superuser and post.owner_id != current_user.id:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    session.delete(post)
    session.commit()
    return Message(message="Post deleted successfully")


@router.get("/user/{user_id}", response_model=PostsPublic)
def read_user_posts(
    session: SessionDep,
    current_user: CurrentUser,
    user_id: uuid.UUID,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve posts by a specific user.
    """
    # For non-superusers, only allow accessing their own posts
    if not current_user.is_superuser and user_id != current_user.id:
        raise HTTPException(status_code=400, detail="Not enough permissions")

    count_statement = (
        select(func.count()).select_from(Post).where(Post.owner_id == user_id)
    )
    count = session.exec(count_statement).one()

    statement = select(Post).where(Post.owner_id == user_id).offset(skip).limit(limit)
    posts = session.exec(statement).all()

    return PostsPublic(data=posts, count=count)
