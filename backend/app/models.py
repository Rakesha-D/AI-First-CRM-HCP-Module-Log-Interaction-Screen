"""
AI-First CRM HCP Module - Database Models
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum, Float
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.database import Base


class InteractionType(str, enum.Enum):
    CALL = "Call"
    VISIT = "Visit"
    EMAIL = "Email"
    MEETING = "Meeting"
    WEBINAR = "Webinar"
    PHONE = "Phone"
    VIRTUAL = "Virtual"


class InteractionStatus(str, enum.Enum):
    DRAFT = "Draft"
    SUBMITTED = "Submitted"
    APPROVED = "Approved"
    REJECTED = "Rejected"


class ProductInterest(str, enum.Enum):
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"
    NONE = "None"


class HCP(Base):
    """Healthcare Professional model"""
    __tablename__ = "hcps"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    full_name = Column(String(200), index=True)
    npi = Column(String(20), unique=True, index=True)
    specialty = Column(String(100))
    license_number = Column(String(50))
    email = Column(String(200))
    phone = Column(String(20))
    organization = Column(String(200))
    address = Column(Text)
    city = Column(String(100))
    state = Column(String(50))
    zip_code = Column(String(20))
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    interactions = relationship("Interaction", back_populates="hcp", cascade="all, delete-orphan")
    accounts = relationship("Account", back_populates="hcp", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<HCP({self.first_name} {self.last_name})>"


class Interaction(Base):
    """Interaction/Encounter model"""
    __tablename__ = "interactions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    hcp_id = Column(Integer, ForeignKey("hcps.id"), nullable=False, index=True)
    rep_id = Column(Integer, nullable=False)
    rep_name = Column(String(200), nullable=False)

    # Interaction details
    interaction_type = Column(Enum(InteractionType), nullable=False)
    date = Column(DateTime, nullable=False)
    duration_minutes = Column(Integer)
    status = Column(Enum(InteractionStatus), default=InteractionStatus.DRAFT)

    # Content
    summary = Column(Text)
    details = Column(Text)
    key_topics = Column(Text)  # JSON string of topics
    products_discussed = Column(Text)  # JSON string of products
    next_steps = Column(Text)
    follow_up_date = Column(DateTime)

    # AI-generated fields
    ai_summary = Column(Text)
    ai_entities = Column(Text)  # JSON string of extracted entities
    ai_sentiment = Column(String(50))
    ai_confidence = Column(Float)

    # Metadata
    source = Column(String(50), default="manual")  # manual, chat, ai
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    hcp = relationship("HCP", back_populates="interactions")
    accounts = relationship("Account", back_populates="interaction", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Interaction(id={self.id}, type={self.interaction_type})>"


class Account(Base):
    """Account/Opportunity model linked to interactions"""
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    hcp_id = Column(Integer, ForeignKey("hcps.id"), nullable=False)
    interaction_id = Column(Integer, ForeignKey("interactions.id"), nullable=True)

    name = Column(String(200), nullable=False)
    description = Column(Text)
    product_name = Column(String(200))
    estimated_value = Column(Float)
    interest_level = Column(Enum(ProductInterest), default=ProductInterest.MEDIUM)
    expected_close_date = Column(DateTime)
    status = Column(String(50), default="Open")  # Open, Won, Lost, On Hold

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    hcp = relationship("HCP", back_populates="accounts")
    interaction = relationship("Interaction", back_populates="accounts")

    def __repr__(self):
        return f"<Account({self.name})>"


class ChatSession(Base):
    """Chat session for conversational logging"""
    __tablename__ = "chat_sessions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, nullable=False)
    session_token = Column(String(100), unique=True, index=True)
    status = Column(String(50), default="active")  # active, completed, archived
    interaction_id = Column(Integer, ForeignKey("interactions.id"), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<ChatSession(token={self.session_token})>"


class ChatMessage(Base):
    """Individual chat messages"""
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    session_id = Column(Integer, ForeignKey("chat_sessions.id"), nullable=False)
    role = Column(String(50), nullable=False)  # user, assistant, system
    content = Column(Text, nullable=False)
    metadata_json = Column(Text)  # Additional metadata as JSON

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    session = relationship("ChatSession", back_populates="messages")

    def __repr__(self):
        return f"<ChatMessage(role={self.role})>"
