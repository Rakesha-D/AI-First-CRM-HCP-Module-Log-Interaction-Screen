"""
AI-First CRM HCP Module - AI Agent Routes
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
import json
import re
from datetime import datetime, date

from app.database import get_db
from app.agent import run_agent, tool_log_interaction, tool_edit_interaction
from app.models import Interaction, HCP
from app.schemas import (
    ChatResponse, AIExtractEntitiesResponse, InteractionCreate, Interaction,
    InteractionDraftUpdateRequest, InteractionDraftUpdateResponse
)

router = APIRouter(prefix="/api/ai", tags=["AI Agent"])


def _clean_value(value: str) -> str:
    return value.strip().strip('"., ')


def _parse_date_value(value: str) -> Optional[str]:
    raw_value = _clean_value(value)
    today = date.today()
    lowered = raw_value.lower()

    if lowered == "today":
      return today.isoformat()
    if lowered == "tomorrow":
      from datetime import timedelta
      return (today + timedelta(days=1)).isoformat()
    if lowered == "yesterday":
      from datetime import timedelta
      return (today - timedelta(days=1)).isoformat()

    formats = [
        "%Y-%m-%d",
        "%d-%m-%Y",
        "%d/%m/%Y",
        "%m/%d/%Y",
        "%d.%m.%Y",
        "%B %d %Y",
        "%b %d %Y",
        "%d %B %Y",
        "%d %b %Y",
    ]
    for fmt in formats:
        try:
            return datetime.strptime(raw_value, fmt).date().isoformat()
        except ValueError:
            continue
    return None


def _parse_time_value(value: str) -> Optional[str]:
    raw_value = _clean_value(value).upper().replace(".", "")
    raw_value = re.sub(r"\s+", " ", raw_value)

    formats = ["%H:%M", "%H.%M", "%I:%M %p", "%I %p", "%I%p"]
    for fmt in formats:
        try:
            return datetime.strptime(raw_value, fmt).strftime("%H:%M")
        except ValueError:
            continue
    return None


def _split_list(value: str) -> List[str]:
    return [
        item.strip()
        for item in re.split(r",|;|\band\b", _clean_value(value), flags=re.IGNORECASE)
        if item.strip()
    ]


def _extract_after_label(message: str, labels: List[str]) -> Optional[str]:
    label_pattern = "|".join(re.escape(label) for label in labels)
    pattern = rf"(?:{label_pattern})\s*(?:to|as|is|:)?\s+(.+?)(?=$|(?:\s+(?:and|also)\s+(?:date|time|hcp|doctor|attendees|topics|outcomes|summary|follow[- ]?up|sentiment|products|materials|samples)\b))"
    match = re.search(pattern, message, flags=re.IGNORECASE)
    if match:
        return _clean_value(match.group(1))
    return None


def _extract_hcp_name(message: str) -> Optional[str]:
    stop_words = r"(?=$|[,.;]|\s+(?:and|also)\s+(?:interaction|type|mode|date|time|attendees|topics|products|summary|sentiment|materials|samples|next|follow))"
    patterns = [
        rf"\b(?:patient|hcp|doctor)\s+(?:name\s+)?(?:is|to|as|:)\s+(?:Dr\.?\s+)?([A-Za-z]+(?:\s+[A-Za-z]+){{0,3}}){stop_words}",
        rf"\b(?:met|visited|saw|called|spoke\s+with|spoke\s+to)\s+(?:Dr\.?\s+)?([A-Za-z]+(?:\s+[A-Za-z]+){{0,3}}){stop_words}",
        rf"\bDr\.?\s+([A-Za-z]+(?:\s+[A-Za-z]+){{0,3}}){stop_words}",
    ]
    for pattern in patterns:
        match = re.search(pattern, message, flags=re.IGNORECASE)
        if match:
            return _clean_value(match.group(1))
    return None


def _normalize_interaction_type(value: str) -> Optional[str]:
    normalized = _clean_value(value).lower().replace("-", " ")
    allowed_types = {
        "call": "Call",
        "phone": "Phone",
        "phone call": "Phone",
        "visit": "Visit",
        "in person": "Visit",
        "in person visit": "Visit",
        "face to face": "Visit",
        "meeting": "Meeting",
        "email": "Email",
        "webinar": "Webinar",
        "online": "Virtual",
        "virtual": "Virtual",
        "video": "Virtual",
        "zoom": "Virtual",
        "teams": "Virtual",
    }
    return allowed_types.get(normalized)


def _apply_draft_updates(message: str, current_draft: dict) -> tuple[dict, List[str]]:
    draft = dict(current_draft or {})
    updated_fields: List[str] = []

    hcp_name = _extract_hcp_name(message)
    if hcp_name:
        draft["hcp_name"] = hcp_name
        updated_fields.append("hcp_name")

    date_match = re.search(
        r"\b(?:date|meeting date|interaction date)\b\s*(?:to|as|is|:)?\s+"
        r"(today|tomorrow|yesterday|\d{1,4}[-/.]\d{1,2}[-/.]\d{2,4}|"
        r"[A-Za-z]{3,9}\s+\d{1,2},?\s+\d{4}|\d{1,2}\s+[A-Za-z]{3,9}\s+\d{4})",
        message,
        flags=re.IGNORECASE,
    )
    if date_match:
        parsed_date = _parse_date_value(date_match.group(1))
        if parsed_date:
            draft["date"] = parsed_date
            updated_fields.append("date")

    time_match = re.search(
        r"\b(?:time|meeting time|interaction time)\b\s*(?:to|as|is|:)?\s+"
        r"(\d{1,2}(?::\d{2}|\.\d{2})?\s*(?:am|pm|AM|PM)?)",
        message,
        flags=re.IGNORECASE,
    )
    if time_match:
        parsed_time = _parse_time_value(time_match.group(1))
        if parsed_time:
            draft["time"] = parsed_time
            updated_fields.append("time")

    interaction_type = _extract_after_label(message, ["interaction type", "type", "mode"])
    inline_type = re.search(r"\b(in[- ]person|online|virtual|meeting|call|phone|email|webinar|visit)\b", message, flags=re.IGNORECASE)
    normalized_type = _normalize_interaction_type(interaction_type or (inline_type.group(1) if inline_type else ""))
    if normalized_type:
        draft["interaction_type"] = normalized_type
        updated_fields.append("interaction_type")

    attendees = _extract_after_label(message, ["attendees", "attendee"])
    if attendees:
        draft["attendees"] = attendees
        updated_fields.append("attendees")

    topics = _extract_after_label(message, ["topics discussed", "topic discussed", "topics", "key topics"])
    if topics:
        draft["key_topics"] = _split_list(topics)
        updated_fields.append("key_topics")

    products = _extract_after_label(message, ["products discussed", "products", "product"])
    if products:
        draft["products_discussed"] = _split_list(products)
        updated_fields.append("products_discussed")

    outcomes = _extract_after_label(message, ["outcomes", "outcome", "summary"])
    if outcomes:
        draft["summary"] = outcomes
        updated_fields.append("summary")

    follow_up = _extract_after_label(message, ["follow-up actions", "follow up actions", "next steps", "follow-up", "follow up"])
    if follow_up:
        draft["next_steps"] = follow_up
        updated_fields.append("next_steps")

    sentiment = re.search(r"\b(positive|neutral|negative)\b", message, flags=re.IGNORECASE)
    if sentiment and re.search(r"\bsentiment|feeling|tone\b", message, flags=re.IGNORECASE):
        draft["sentiment"] = sentiment.group(1).capitalize()
        updated_fields.append("sentiment")

    materials = _extract_after_label(message, ["materials shared", "materials", "shared"])
    if materials:
        draft["materials_shared"] = materials
        updated_fields.append("materials_shared")

    samples = _extract_after_label(message, ["samples distributed", "samples", "sample"])
    if samples:
        draft["samples_distributed"] = samples
        updated_fields.append("samples_distributed")

    return draft, list(dict.fromkeys(updated_fields))


@router.post(
    "/interaction-draft/update",
    response_model=InteractionDraftUpdateResponse,
    summary="Update the Log HCP Interaction draft from an AI Assistant message",
)
def update_interaction_draft(request: InteractionDraftUpdateRequest):
    """
    Parse a natural-language AI Assistant message and return an updated interaction draft.

    The UI intentionally keeps Interaction Details read-only. Reps update the draft by
    sending messages such as "update the date to 19-04-2025" or
    "set sentiment to positive and next steps to send brochure".
    """
    updated_draft, updated_fields = _apply_draft_updates(
        request.message,
        request.current_draft,
    )

    if updated_fields:
        field_names = ", ".join(field.replace("_", " ") for field in updated_fields)
        assistant_message = f"Updated {field_names} in Interaction Details."
    else:
        assistant_message = (
            "I could not find a supported field to update. Try messages like "
            "'update the date to 19-04-2025' or 'set sentiment to positive'."
        )

    return InteractionDraftUpdateResponse(
        message=assistant_message,
        updated_draft=updated_draft,
        updated_fields=updated_fields,
        confidence=0.95 if updated_fields else 0.3,
    )


@router.post("/chat", response_model=ChatResponse)
def ai_chat(message: str, conversation_history: Optional[List[str]] = None):
    """
    Send a message to the AI agent for processing.
    The agent will use LangGraph to route to appropriate tools.
    """
    result = run_agent(message, conversation_history or [])

    return ChatResponse(
        message=result["response"],
        intent="general",
        suggestions=["Log a new interaction", "Search for an HCP", "Get insights"],
    )


@router.post("/extract", response_model=AIExtractEntitiesResponse)
def extract_entities(raw_text: str):
    """
    Extract structured entities from raw interaction text using LLM.
    """
    from langchain_core.messages import HumanMessage
    from langchain_groq import ChatGroq
    from app.config import settings
    import json

    llm = ChatGroq(
        model=settings.GROQ_MODEL,
        api_key=settings.GROQ_API_KEY,
        temperature=0.3,
    )

    prompt = f"""
    Extract structured data from this interaction note:

    {raw_text}

    Return ONLY valid JSON:
    {{
        "hcp_name": "name if mentioned",
        "hcp_specialty": "specialty if mentioned",
        "organization": "organization if mentioned",
        "products": ["product1"],
        "topics": ["topic1"],
        "sentiment": "positive|negative|neutral",
        "confidence": 0.95,
        "summary": "concise summary",
        "next_steps": ["step1"],
        "follow_up_date": "YYYY-MM-DD if mentioned"
    }}
    """

    response = llm.invoke([HumanMessage(content=prompt)])
    try:
        data = json.loads(response.content.strip().strip('```json\n').strip('```'))
    except json.JSONDecodeError:
        data = {"summary": raw_text, "sentiment": "neutral", "confidence": 0.5}

    return AIExtractEntitiesResponse(**data)


@router.post("/log-interaction")
def ai_log_interaction(interaction_data: InteractionCreate, db: Session = Depends(get_db)):
    """
    Log an interaction with AI-powered entity extraction and summarization.
    """
    # Find HCP by ID
    hcp = db.query(HCP).filter(HCP.id == interaction_data.hcp_id).first()
    if not hcp:
        raise HTTPException(status_code=404, detail="HCP not found")

    # Call the AI tool for logging
    tool_result = tool_log_interaction(
        hcp_name=f"{hcp.first_name} {hcp.last_name}",
        interaction_type=interaction_data.interaction_type.value,
        summary=interaction_data.summary or "",
        details=interaction_data.details or "",
        products_discussed=", ".join(interaction_data.products_discussed or []),
        key_topics=", ".join(interaction_data.key_topics or []),
        next_steps=interaction_data.next_steps or "",
        duration_minutes=interaction_data.duration_minutes or 0,
        rep_name=interaction_data.rep_name,
    )

    # Save to database
    interaction = Interaction(
        hcp_id=interaction_data.hcp_id,
        rep_id=interaction_data.rep_id,
        rep_name=interaction_data.rep_name,
        interaction_type=interaction_data.interaction_type,
        date=interaction_data.date,
        duration_minutes=interaction_data.duration_minutes,
        summary=interaction_data.summary,
        details=interaction_data.details,
        key_topics=json.dumps(interaction_data.key_topics or []),
        products_discussed=json.dumps(interaction_data.products_discussed or []),
        next_steps=interaction_data.next_steps,
        source=interaction_data.source,
        ai_summary=tool_result["ai_analysis"].get("ai_summary"),
        ai_entities=json.dumps(tool_result["ai_analysis"].get("entities", {})),
        ai_sentiment=tool_result["ai_analysis"].get("sentiment"),
        ai_confidence=tool_result["ai_analysis"].get("confidence"),
    )

    db.add(interaction)
    db.commit()
    db.refresh(interaction)

    return {
        "interaction": interaction,
        "ai_analysis": tool_result["ai_analysis"],
    }
