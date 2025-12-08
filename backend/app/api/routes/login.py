import logging  # Added logging import
from datetime import timedelta
from typing import Annotated, Any

from fastapi import (  # Added Request
    APIRouter,
    Depends,
    HTTPException,
    Request,
    Response,
)
from fastapi.security import OAuth2PasswordRequestForm

from app import crud
from app.api.deps import CurrentUser, SessionDep
from app.core import security
from app.core.config import settings
from app.models import Token, UserPublic

router = APIRouter(tags=["login"])

logger = logging.getLogger(__name__)  # Added logger instance


@router.post("/login/access-token")
def login_access_token(
    session: SessionDep,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    response: Response,
    request: Request,
) -> Token:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    user = crud.authenticate(
        session=session, email=form_data.username, password=form_data.password
    )

    client_host = request.client.host if request.client else "unknown"  # Get client IP

    if not user:
        logger.warning(
            f"Failed login attempt for user: {form_data.username} from IP: {client_host}. Reason: Incorrect credentials."
        )
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    elif not user.is_active:
        logger.warning(
            f"Failed login attempt for user: {form_data.username} from IP: {client_host}. Reason: Inactive user."
        )
        raise HTTPException(status_code=400, detail="Inactive user")

    logger.info(
        f"Successful login for user: {user.email} (ID: {user.id}) from IP: {client_host}."
    )  # Log successful login

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        user.id, expires_delta=access_token_expires
    )
    response.set_cookie(
        key="access_token",
        value=f"Bearer {access_token}",
        httponly=True,
        secure=True,
        samesite="strict",
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )
    return Token(access_token=access_token)


@router.post("/login/test-token", response_model=UserPublic)
def test_token(current_user: CurrentUser) -> Any:
    """
    Test access token
    """
    return current_user
