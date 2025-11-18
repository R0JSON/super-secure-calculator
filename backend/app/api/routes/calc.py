import uuid
from typing import Any 

from fastapi import APIRouter, HTTPException
from sqlmodel import func, select

from app.api.deps import CurrentUser, SessionDep
from app.models import Calculation, CalculationCreate, CalculationsPublic, CalculationPublic ,CalculationUpdate,  Message, OperationType

router = APIRouter(prefix="/calculations", tags=["calculations"])


@router.get("/", response_model=CalculationsPublic)
def read_calculations(
    session: SessionDep, current_user: CurrentUser, skip: int = 0, limit: int = 100
) -> Any:
    """
    Retrieve calculations.
    """

    if current_user.is_superuser:
        count_statement = select(func.count()).select_from(Calculation)
        count = session.exec(count_statement).one()
        statement = select(Calculation).offset(skip).limit(limit)
        calculations = session.exec(statement).all()
    else:
        count_statement = (
            select(func.count())
            .select_from(Calculation)
            .where(Calculation.owner_id == current_user.id)
        )
        count = session.exec(count_statement).one()
        statement = (
            select(Calculation)
            .where(Calculation.owner_id == current_user.id)
            .offset(skip)
            .limit(limit)
        )
        calculations = session.exec(statement).all()

    return CalculationsPublic(data=calculations, count=count)


@router.get("/{id}", response_model=CalculationPublic)
def read_calculation(session: SessionDep, current_user: CurrentUser, id: uuid.UUID) -> Any:
    """
    Get calculation by ID.
    """
    calculation = session.get(Calculation, id)
    if not calculation:
        raise HTTPException(status_code=404, detail="Calculation not found")
    if not current_user.is_superuser and (calculation.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    return calculation


@router.post("/", response_model=CalculationPublic)
def create_calculation(
    *, session: SessionDep, current_user: CurrentUser, calculation_in: CalculationCreate
) -> Any:
    """
    Create new calculation.
    """
    match calculation_in.operation:
        case "add":
            result = calculation_in.operand_a + calculation_in.operand_b
        case "sub":
            result = calculation_in.operand_a - calculation_in.operand_b
        case "mul":
            result = calculation_in.operand_a * calculation_in.operand_b
        case "div":
            if not calculation_in.operand_b:
                raise HTTPException(status_code=400, detail="Can't divide by zero!")
            result = calculation_in.operand_a / calculation_in.operand_b
    calculation = Calculation.model_validate(calculation_in, update={"owner_id": current_user.id, "result": result})
    session.add(calculation)
    session.commit()
    session.refresh(calculation)
    return calculation


# @router.put("/{id}", response_model=CalculationPublic)
# def update_calculation(
#     *,
#     session: SessionDep,
#     current_user: CurrentUser,
#     id: uuid.UUID,
#     calculation_in: CalculationUpdate,
# ) -> Any:
#     """
#     Update an calculation.
#     """
#     calculation = session.get(Calculation, id)
#     if not calculation:
#         raise HTTPException(status_code=404, detail="Calculation not found")
#     if not current_user.is_superuser and (calculation.owner_id != current_user.id):
#         raise HTTPException(status_code=400, detail="Not enough permissions")
#     update_dict = calculation_in.model_dump(exclude_unset=True)
#     match calculation_in.operation:
#         case "add":
#             result = calculation_in.operand_a + calculation_in.operand_b
#             pass
#         case "sub":
#             result = calculation_in.operand_a - calculation_in.operand_b
#             pass
#         case "mul":
#             result = calculation_in.operand_a * calculation_in.operand_b
#             pass
#         case "div":
#             if not operand_b:
#                 raise HTTPException(status_code=400, detail="Can't divide by zero!")
#             result = calculation_in.operand_a / calculation_in.operand_b
#             pass
#     update_dict["result"] = int(result)
#     calculation.sqlmodel_update(update_dict)
#     session.add(calculation)
#     session.commit()
#     session.refresh(calculation)
#     return calculation
#
#
# @router.delete("/{id}")
# def delete_calculation(
#     session: SessionDep, current_user: CurrentUser, id: uuid.UUID
# ) -> Message:
#     """
#     Delete an calculation.
#     """
#     calculation = session.get(Calculation, id)
#     if not calculation:
#         raise HTTPException(status_code=404, detail="Calculation not found")
#     if not current_user.is_superuser and (calculation.owner_id != current_user.id):
#         raise HTTPException(status_code=400, detail="Not enough permissions")
#     session.delete(calculation)
#     session.commit()
#     return Message(message="Calculation deleted successfully")
#
