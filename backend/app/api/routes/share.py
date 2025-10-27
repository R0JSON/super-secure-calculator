from typing import Any, List, Optional
from pydantic import BaseModel
from fastapi import APIRouter, Depends
from sqlmodel import select
from app.api.deps import CurrentUser, SessionDep
from app.models import SharedCalculation
from uuid import UUID
from sqlmodel import SQLModel, Field
from datetime import datetime
from app.core.db import get_db              
from sqlmodel import Session
from app.core.db import engine
from app.api.deps import get_current_user, get_db

router = APIRouter(prefix="/share", tags=["Share"])


class SharedCalculationCreate(BaseModel):
    expression: str
    result: str


class SharedCalculationRead(SQLModel):
    id: int
    expression: str
    result: str
    created_at: datetime
    user_id: UUID


# GET dla wszystkich – nie wymaga logowania
@router.get("/", response_model=List[SharedCalculationRead])
def get_shared_calculations(session: Session = Depends(get_db)):
    statement = select(SharedCalculation)
    results = session.exec(statement).all()
    return [
        SharedCalculationRead(
            id=item.id,
            expression=item.expression,
            result=item.result,
            created_at=item.created_at,
            user_id=item.user_id
	)
        for item in results
    ]


# POST – nadal wymaga zalogowanego użytkownika
@router.post("/", response_model=SharedCalculationRead)
def create_shared_calculation(
    shared_in: SharedCalculationCreate,
    session: Session = Depends(get_db),
    current_user = Depends(get_current_user)
) -> Any:
    new_shared = SharedCalculation(
        expression=shared_in.expression,
        result=shared_in.result,
        user_id=current_user.id
    )
    session.add(new_shared)
    session.commit()
    session.refresh(new_shared)
    return new_shared
