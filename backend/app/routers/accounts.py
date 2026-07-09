"""
AI-First CRM HCP Module - Accounts Routes
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.models import Account
from app.schemas import AccountCreate, AccountUpdate, Account

router = APIRouter(prefix="/api/accounts", tags=["Accounts"])


@router.get("/", response_model=List[Account])
def list_accounts(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    hcp_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
):
    """List all accounts/opportunities."""
    query = db.query(Account)
    if hcp_id:
        query = query.filter(Account.hcp_id == hcp_id)
    return query.offset(skip).limit(limit).all()


@router.post("/", response_model=Account)
def create_account(account_data: AccountCreate, db: Session = Depends(get_db)):
    """Create a new account/opportunity."""
    account = Account(**account_data.model_dump())
    db.add(account)
    db.commit()
    db.refresh(account)
    return account
