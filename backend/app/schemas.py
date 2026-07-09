"""
AI-First CRM HCP Module - Pydantic Schemas
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List, Dict, Any
from app.models import InteractionType, InteractionStatus, ProductInterest


# ─── HCP Schemas ──────────────────────────────────────────────
class HCPBase(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    npi: Optional[str] = Field(None, max_length=20)
    specialty: Optional[str] = Field(None, max_length=100)
    license_number: Optional[str] = Field(None, max_length=50)
    email: Optional[str] = Field(None, max_length=200)
    phone: Optional[str] = Field(None, max_length=20)
    organization: Optional[str] = Field(None, max_length=200)
    address: Optional[str] = None
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=50)
    zip_code: Optional[str] = Field(None, max_length=20)
    notes: Optional[str] = None


class HCPCreate(HCPBase):
    pass


class HCPUpdate(BaseModel):
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    npi: Optional[str] = Field(None, max_length=20)
    specialty: Optional[str] = Field(None, max_length=100)
    email: Optional[str] = Field(None, max_length=200)
    phone: Optional[str] = Field(None, max_length=20)
    organization: Optional[str] = Field(None, max_length=200)
    address: Optional[str] = None
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=50)
    zip_code: Optional[str] = Field(None, max_length=20)
    notes: Optional[str] = None


class HCP(HCPBase):
    id: int
    full_name: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ─── Interaction Schemas ──────────────────────────────────────
class InteractionBase(BaseModel):
    hcp_id: int
    rep_id: int
    rep_name: str = Field(..., min_length=1, max_length=200)
    interaction_type: InteractionType
    date: datetime
    duration_minutes: Optional[int] = Field(None, ge=0)
    summary: Optional[str] = None
    details: Optional[str] = None
    key_topics: Optional[List[str]] = None
    products_discussed: Optional[List[str]] = None
    next_steps: Optional[str] = None
    follow_up_date: Optional[datetime] = None


class InteractionCreate(InteractionBase):
    source: str = Field("manual", max_length=50)


class InteractionUpdate(BaseModel):
    interaction_type: Optional[InteractionType] = None
    date: Optional[datetime] = None
    duration_minutes: Optional[int] = Field(None, ge=0)
    status: Optional[InteractionStatus] = None
    summary: Optional[str] = None
    details: Optional[str] = None
    key_topics: Optional[List[str]] = None
    products_discussed: Optional[List[str]] = None
    next_steps: Optional[str] = None
    follow_up_date: Optional[datetime] = None


class Interaction(InteractionBase):
    id: int
    status: InteractionStatus = InteractionStatus.DRAFT
    ai_summary: Optional[str] = None
    ai_entities: Optional[str] = None
    ai_sentiment: Optional[str] = None
    ai_confidence: Optional[float] = None
    source: str = "manual"
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ─── Account Schemas ──────────────────────────────────────────
class AccountBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    product_name: Optional[str] = Field(None, max_length=200)
    estimated_value: Optional[float] = Field(None, ge=0)
    interest_level: ProductInterest = ProductInterest.MEDIUM
    expected_close_date: Optional[datetime] = None
    status: str = Field("Open", max_length=50)


class AccountCreate(AccountBase):
    hcp_id: int
    interaction_id: Optional[int] = None


class AccountUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    product_name: Optional[str] = Field(None, max_length=200)
    estimated_value: Optional[float] = Field(None, ge=0)
    interest_level: Optional[ProductInterest] = None
    expected_close_date: Optional[datetime] = None
    status: Optional[str] = Field(None, max_length=50)


class Account(AccountBase):
    id: int
    hcp_id: int
    interaction_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ─── Chat Schemas ─────────────────────────────────────────────
class ChatSessionCreate(BaseModel):
    user_id: int


class ChatMessageBase(BaseModel):
    role: str = Field(..., pattern="^(user|assistant|system)$")
    content: str


class ChatMessageCreate(ChatMessageBase):
    session_id: int
    metadata_json: Optional[str] = None


class ChatMessage(ChatMessageBase):
    id: int
    session_id: int
    metadata_json: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ChatSession(BaseModel):
    id: int
    user_id: int
    session_token: str
    status: str
    interaction_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    messages: List[ChatMessage] = []

    class Config:
        from_attributes = True


# ─── AI Response Schemas ──────────────────────────────────────
class AIExtractEntitiesResponse(BaseModel):
    hcp_name: Optional[str] = None
    hcp_specialty: Optional[str] = None
    organization: Optional[str] = None
    products: List[str] = []
    topics: List[str] = []
    sentiment: str = "neutral"
    confidence: float = 0.0
    summary: str = ""
    next_steps: List[str] = []
    follow_up_date: Optional[str] = None


class ChatResponse(BaseModel):
    message: str
    intent: Optional[str] = None
    entities: Optional[dict] = None
    action_taken: Optional[str] = None
    suggestions: Optional[List[str]] = None


class InteractionDraftUpdateRequest(BaseModel):
    message: str = Field(
        ...,
        min_length=1,
        description="Natural-language instruction, for example: update the date to 19-04-2025",
    )
    current_draft: Dict[str, Any] = Field(
        default_factory=dict,
        description="Current interaction draft from the UI. The API returns a merged updated draft.",
    )


class InteractionDraftUpdateResponse(BaseModel):
    message: str
    updated_draft: Dict[str, Any]
    updated_fields: List[str] = []
    confidence: float = 1.0


class HealthResponse(BaseModel):
    status: str
    app: str
    version: str
