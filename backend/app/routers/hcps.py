"""
AI-First CRM HCP Module - HCP CRUD Routes
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from app.database import get_db
from app.models import HCP
from app.schemas import HCPCreate, HCPUpdate, HCP

router = APIRouter(prefix="/api/hcps", tags=["HCPs"])


@router.get("/", response_model=List[HCP])
def list_hcps(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    search: str = Query(None),
    specialty: str = Query(None),
    db: Session = Depends(get_db),
):
    """List all HCPs with optional filtering."""
    query = db.query(HCP)

    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (HCP.first_name.ilike(search_term)) |
            (HCP.last_name.ilike(search_term)) |
            (HCP.full_name.ilike(search_term)) |
            (HCP.npi.ilike(search_term)) |
            (HCP.organization.ilike(search_term))
        )

    if specialty:
        query = query.filter(HCP.specialty.ilike(f"%{specialty}%"))

    return query.offset(skip).limit(limit).all()


@router.get("/{hcp_id}", response_model=HCP)
def get_hcp(hcp_id: int, db: Session = Depends(get_db)):
    """Get a specific HCP by ID."""
    hcp = db.query(HCP).filter(HCP.id == hcp_id).first()
    if not hcp:
        raise HTTPException(status_code=404, detail="HCP not found")
    return hcp


@router.post("/", response_model=HCP)
def create_hcp(hcp_data: HCPCreate, db: Session = Depends(get_db)):
    """Create a new HCP record."""
    # Generate full_name
    full_name = f"{hcp_data.first_name} {hcp_data.last_name}"

    hcp = HCP(
        **hcp_data.model_dump(),
        full_name=full_name,
    )
    db.add(hcp)
    db.commit()
    db.refresh(hcp)
    return hcp


@router.put("/{hcp_id}", response_model=HCP)
def update_hcp(hcp_id: int, hcp_data: HCPUpdate, db: Session = Depends(get_db)):
    """Update an existing HCP record."""
    hcp = db.query(HCP).filter(HCP.id == hcp_id).first()
    if not hcp:
        raise HTTPException(status_code=404, detail="HCP not found")

    update_data = hcp_data.model_dump(exclude_unset=True)

    # Regenerate full_name if name fields changed
    if "first_name" in update_data or "last_name" in update_data:
        first = update_data.get("first_name", hcp.first_name)
        last = update_data.get("last_name", hcp.last_name)
        update_data["full_name"] = f"{first} {last}"

    for key, value in update_data.items():
        setattr(hcp, key, value)

    db.commit()
    db.refresh(hcp)
    return hcp


@router.delete("/{hcp_id}")
def delete_hcp(hcp_id: int, db: Session = Depends(get_db)):
    """Delete an HCP record."""
    hcp = db.query(HCP).filter(HCP.id == hcp_id).first()
    if not hcp:
        raise HTTPException(status_code=404, detail="HCP not found")

    db.delete(hcp)
    db.commit()
    return {"message": "HCP deleted successfully"}
