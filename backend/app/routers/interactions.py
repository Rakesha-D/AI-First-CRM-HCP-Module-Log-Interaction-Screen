"""
AI-First CRM HCP Module - Interactions CRUD Routes
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.database import get_db
from app.models import Interaction, InteractionType, InteractionStatus
from app.schemas import InteractionCreate, InteractionUpdate, Interaction

router = APIRouter(prefix="/api/interactions", tags=["Interactions"])


@router.get("/", response_model=List[Interaction])
def list_interactions(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    hcp_id: Optional[int] = Query(None),
    interaction_type: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """List all interactions with optional filtering."""
    query = db.query(Interaction)

    if hcp_id:
        query = query.filter(Interaction.hcp_id == hcp_id)
    if interaction_type:
        query = query.filter(Interaction.interaction_type == interaction_type)
    if status:
        query = query.filter(Interaction.status == status)

    return query.order_by(Interaction.date.desc()).offset(skip).limit(limit).all()


@router.get("/{interaction_id}", response_model=Interaction)
def get_interaction(interaction_id: int, db: Session = Depends(get_db)):
    """Get a specific interaction by ID."""
    interaction = db.query(Interaction).filter(Interaction.id == interaction_id).first()
    if not interaction:
        raise HTTPException(status_code=404, detail="Interaction not found")
    return interaction


@router.post("/", response_model=Interaction)
def create_interaction(interaction_data: InteractionCreate, db: Session = Depends(get_db)):
    """Create a new interaction record."""
    interaction = Interaction(**interaction_data.model_dump())
    db.add(interaction)
    db.commit()
    db.refresh(interaction)
    return interaction


@router.put("/{interaction_id}", response_model=Interaction)
def update_interaction(
    interaction_id: int,
    interaction_data: InteractionUpdate,
    db: Session = Depends(get_db),
):
    """Update an existing interaction record."""
    interaction = db.query(Interaction).filter(Interaction.id == interaction_id).first()
    if not interaction:
        raise HTTPException(status_code=404, detail="Interaction not found")

    update_data = interaction_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(interaction, key, value)

    db.commit()
    db.refresh(interaction)
    return interaction


@router.delete("/{interaction_id}")
def delete_interaction(interaction_id: int, db: Session = Depends(get_db)):
    """Delete an interaction record."""
    interaction = db.query(Interaction).filter(Interaction.id == interaction_id).first()
    if not interaction:
        raise HTTPException(status_code=404, detail="Interaction not found")

    db.delete(interaction)
    db.commit()
    return {"message": "Interaction deleted successfully"}
