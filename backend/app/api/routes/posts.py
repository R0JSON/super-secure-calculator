import uuid
from typing import Any

from fastapi import APIRouter, HTTPException
from sqlmodel import select, func

from app.api.deps import SessionDep, CurrentUser
from app.models import (
    Post,
    PostCreate,
    PostUpdate,
    PostPublic,
    PostWithCalculation,
    PostWithDetails,
    PostsPublic,
    Message,
    Calculation,
    User,
    Comment,
    UserPublic,
    PostPublicWithOwner,
    PostsPublicWithOwners,
    UserPublicLimited,
)

router = APIRouter(prefix="/posts", tags=["posts"])


@router.get("/public/", response_model=PostsPublicWithOwners)
def read_public_posts(session: SessionDep, skip: int = 0, limit: int = 100) -> Any:
    """
    Retrieve public posts with limited owner information.
    """
    count_statement = select(func.count()).select_from(Post)
    count = session.exec(count_statement).one()

    statement = (
        select(Post)
        .join(User, Post.owner_id == User.id)
        .where(User.is_active == True)
        .offset(skip)
        .limit(limit)
    )
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
                full_name=post.owner.full_name
                # Don't include email, is_active, is_superuser
            )
        )
        posts_with_owners.append(post_with_owner)

    return PostsPublicWithOwners(data=posts_with_owners, count=count)


@router.get("/{id}", response_model=PostWithDetails)
def read_post(session: SessionDep, current_user: CurrentUser, id: uuid.UUID) -> Any:
    """
    Get post by ID with calculation and comments details.
    """
    # Get post with calculation and owner
    statement = (
        select(Post)
        .where(Post.id == id)
        .join(Calculation, Post.calculation_id == Calculation.id)
        .join(User, Post.owner_id == User.id)
    )
    post = session.exec(statement).first()

    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    if not current_user.is_superuser and post.owner_id != current_user.id:
        raise HTTPException(status_code=400, detail="Not enough permissions")

    # Get comments for this post
    comments_statement = (
        select(Comment)
        .where(Comment.post_id == id)
        .join(User, Comment.owner_id == User.id)
    )
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
        owner=post.owner
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
        .join(Calculation, Post.calculation_id == Calculation.id)
        .join(User, Post.owner_id == User.id)
        .where(User.is_active == True)
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
        calculation=post.calculation
    )

    return post_with_calc


@router.post("/", response_model=PostWithCalculation)
def create_post(session: SessionDep, current_user: CurrentUser, post_in: PostCreate) -> Any:
    """
    Create a new post associated with a calculation.
    """
    # Verify the calculation exists and belongs to the user
    calculation = session.get(Calculation, post_in.calculation_id)
    if not calculation:
        raise HTTPException(status_code=404, detail="Calculation not found")
    if not current_user.is_superuser and calculation.owner_id != current_user.id:
        raise HTTPException(status_code=400, detail="Not enough permissions to use this calculation")

    # Create the post
    post = Post.model_validate(
        post_in,
        update={"owner_id": current_user.id}
    )
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
        calculation=post.calculation
    )


@router.put("/{id}", response_model=PostPublic)
def update_post(session: SessionDep, current_user: CurrentUser, id: uuid.UUID, post_in: PostUpdate) -> Any:
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
def read_user_posts(session: SessionDep, current_user: CurrentUser, user_id: uuid.UUID, skip: int = 0,
                    limit: int = 100) -> Any:
    """
    Retrieve posts by a specific user.
    """
    # For non-superusers, only allow accessing their own posts
    if not current_user.is_superuser and user_id != current_user.id:
        raise HTTPException(status_code=400, detail="Not enough permissions")

    count_statement = (
        select(func.count())
        .select_from(Post)
        .where(Post.owner_id == user_id)
    )
    count = session.exec(count_statement).one()

    statement = (
        select(Post)
        .where(Post.owner_id == user_id)
        .offset(skip)
        .limit(limit)
    )
    posts = session.exec(statement).all()

    return PostsPublic(data=posts, count=count)