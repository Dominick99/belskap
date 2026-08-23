from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models import CreditWallet, User
from app.schemas import CreditBalanceResponse


router = APIRouter(prefix="/api/v1/credits", tags=["credits"])


@router.get("/balance", response_model=CreditBalanceResponse)
def read_credit_balance(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> CreditBalanceResponse:
    wallet = db.get(CreditWallet, user.id)
    return CreditBalanceResponse(balance=wallet.balance if wallet else 0)
