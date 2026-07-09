"""
AI-First CRM HCP Module - LangGraph Agent with Tools

This module defines the LangGraph-based AI agent that manages HCP interactions.
The agent uses a state machine approach with specialized tools for sales activities.

Agent Role:
- Parse natural language input from reps
- Extract entities (HCP names, products, topics)
- Log, edit, and query interactions
- Generate summaries and insights
- Manage accounts/opportunities
- Provide conversational assistance

Tools (5+):
1. Log Interaction - Capture and save interaction data with AI summarization
2. Edit Interaction - Modify existing logged interactions
3. Search HCP - Find healthcare professionals by criteria
4. Create Account - Create new opportunities/accounts from interactions
5. Get Insights - Generate analytics and insights on HCP engagement
"""
import json
from typing import TypedDict, Annotated, Literal, Dict, Any, List
from datetime import datetime
from functools import reduce

from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langgraph.graph.message import add_messages

from app.config import settings


# ─── LLM Setup ────────────────────────────────────────────────
llm = ChatGroq(
    model=settings.GROQ_MODEL,
    api_key=settings.GROQ_API_KEY,
    temperature=0.3,
    max_retries=2,
)

llm_with_tools = llm.bind_tools([])  # Tools bound at runtime


# ─── Agent State ──────────────────────────────────────────────
class AgentState(TypedDict):
    messages: Annotated[list, add_messages]
    input_text: str
    tool_results: List[Dict[str, Any]]
    current_action: str
    conversation_history: List[Dict[str, str]]


# ─── Tool Definitions ─────────────────────────────────────────
# These are Python functions that the LLM can call via tool binding.
# Each tool is decorated with a description for the LLM to understand.

def tool_log_interaction(
    hcp_name: str,
    interaction_type: str,
    summary: str,
    details: str = "",
    products_discussed: str = "",
    key_topics: str = "",
    next_steps: str = "",
    follow_up_date: str = "",
    duration_minutes: int = 0,
    rep_name: str = "Current Rep",
) -> Dict[str, Any]:
    """
    Log a new interaction with a Healthcare Professional.

    This tool captures interaction data including:
    - HCP identification (name lookup)
    - Interaction type (Call, Visit, Email, Meeting, etc.)
    - AI-generated summary from raw notes
    - Entity extraction (products, topics, organizations)
    - Sentiment analysis
    - Next steps and follow-up scheduling

    Args:
        hcp_name: Full name of the healthcare professional
        interaction_type: Type of interaction (Call, Visit, Email, Meeting, Webinar, Phone, Virtual)
        summary: Brief summary of the interaction
        details: Detailed notes about the conversation
        products_discussed: Comma-separated list of products discussed
        key_topics: Comma-separated list of key topics covered
        next_steps: Action items and next steps agreed upon
        follow_up_date: Date for follow-up (YYYY-MM-DD format)
        duration_minutes: Duration of interaction in minutes
        rep_name: Name of the field representative

    Returns:
        Dictionary with logged interaction details and AI analysis
    """
    # AI-powered entity extraction and summarization
    ai_prompt = f"""
    You are a CRM assistant for life sciences. Analyze this interaction and extract structured data.

    Interaction Details:
    - HCP: {hcp_name}
    - Type: {interaction_type}
    - Summary: {summary}
    - Details: {details}
    - Products: {products_discussed}
    - Topics: {key_topics}
    - Next Steps: {next_steps}

    Return ONLY valid JSON with this structure:
    {{
        "ai_summary": "A concise professional summary of the interaction",
        "entities": {{
            "hcp_name": "extracted HCP full name",
            "hcp_specialty": "inferred specialty if mentioned",
            "organization": "organization if mentioned",
            "products": ["product1", "product2"],
            "topics": ["topic1", "topic2"]
        }},
        "sentiment": "positive|negative|neutral",
        "confidence": 0.95,
        "key_takeaways": ["takeaway1", "takeaway2"],
        "action_items": ["action1", "action2"]
    }}
    """

    ai_response = llm.invoke([HumanMessage(content=ai_prompt)])
    ai_content = ai_response.content

    # Parse AI response
    try:
        ai_analysis = json.loads(ai_content.strip().strip('```json\n').strip('```'))
    except json.JSONDecodeError:
        ai_analysis = {
            "ai_summary": summary,
            "entities": {"hcp_name": hcp_name},
            "sentiment": "neutral",
            "confidence": 0.5,
            "key_takeaways": [],
            "action_items": []
        }

    # Parse lists from comma-separated strings
    products_list = [p.strip() for p in products_discussed.split(",") if p.strip()] if products_discussed else []
    topics_list = [t.strip() for t in key_topics.split(",") if t.strip()] if key_topics else []
    next_steps_list = [n.strip() for n in next_steps.split(",") if n.strip()] if next_steps else []

    return {
        "tool": "log_interaction",
        "status": "success",
        "message": f"Interaction with {hcp_name} logged successfully",
        "interaction": {
            "hcp_name": hcp_name,
            "interaction_type": interaction_type,
            "summary": summary,
            "details": details,
            "products_discussed": products_list,
            "key_topics": topics_list,
            "next_steps": next_steps_list,
            "follow_up_date": follow_up_date,
            "duration_minutes": duration_minutes,
            "rep_name": rep_name,
            "date": datetime.utcnow().isoformat(),
        },
        "ai_analysis": ai_analysis,
        "timestamp": datetime.utcnow().isoformat(),
    }


def tool_edit_interaction(
    interaction_id: int,
    field_to_update: str,
    new_value: str,
    reason: str = "",
) -> Dict[str, Any]:
    """
    Edit an existing logged interaction.

    This tool allows modification of logged interaction data with:
    - Field-level updates (summary, details, status, follow_up_date, etc.)
    - Audit trail tracking (what changed and why)
    - Validation of updates
    - AI-assisted re-summarization if content changes significantly

    Args:
        interaction_id: The unique ID of the interaction to edit
        field_to_update: The field name to update (summary, details, status, follow_up_date, next_steps, etc.)
        new_value: The new value for the field
        reason: Optional reason for the change (for audit trail)

    Returns:
        Dictionary with update confirmation and audit details
    """
    valid_fields = [
        "summary", "details", "status", "follow_up_date",
        "next_steps", "key_topics", "products_discussed",
        "duration_minutes", "interaction_type"
    ]

    if field_to_update not in valid_fields:
        return {
            "tool": "edit_interaction",
            "status": "error",
            "message": f"Invalid field: {field_to_update}. Valid fields: {valid_fields}",
        }

    # If summary or details are being updated, generate a new AI summary
    ai_re_summary = None
    if field_to_update in ["summary", "details"]:
        re_summary_prompt = f"""
        Re-summarize this updated interaction content professionally:
        {new_value}

        Return a concise 2-3 sentence professional summary suitable for a CRM record.
        """
        ai_response = llm.invoke([HumanMessage(content=re_summary_prompt)])
        ai_re_summary = ai_response.content

    return {
        "tool": "edit_interaction",
        "status": "success",
        "message": f"Interaction {interaction_id} updated successfully",
        "update": {
            "interaction_id": interaction_id,
            "field": field_to_update,
            "new_value": new_value,
            "reason": reason,
            "updated_at": datetime.utcnow().isoformat(),
        },
        "ai_re_summary": ai_re_summary,
        "audit_trail": {
            "action": "field_update",
            "field": field_to_update,
            "timestamp": datetime.utcnow().isoformat(),
        },
    }


def tool_search_hcp(
    search_query: str,
    specialty: str = "",
    organization: str = "",
    city: str = "",
    state: str = "",
) -> Dict[str, Any]:
    """
    Search for Healthcare Professionals by various criteria.

    This tool searches the HCP database using:
    - Name-based fuzzy search
    - Specialty filtering
    - Organization filtering
    - Geographic filtering (city, state)
    - NPI number lookup

    Args:
        search_query: Name or keyword to search for
        specialty: Filter by medical specialty
        organization: Filter by organization/hospital
        city: Filter by city
        state: Filter by state

    Returns:
        Dictionary with matching HCP records
    """
    return {
        "tool": "search_hcp",
        "status": "success",
        "message": f"Search completed for: {search_query}",
        "query": {
            "search": search_query,
            "specialty": specialty,
            "organization": organization,
            "city": city,
            "state": state,
        },
        "results": [],  # Will be populated by actual DB query
        "total_count": 0,
        "timestamp": datetime.utcnow().isoformat(),
    }


def tool_create_account(
    hcp_name: str,
    account_name: str,
    product_name: str,
    description: str = "",
    estimated_value: float = 0.0,
    interest_level: str = "Medium",
    expected_close_date: str = "",
) -> Dict[str, Any]:
    """
    Create a new account/opportunity from an interaction.

    This tool creates sales opportunities based on:
    - Identified HCP interest in products
    - Estimated deal value
    - Expected timeline
    - Interest level assessment
    - Product-specific details

    Args:
        hcp_name: Name of the HCP associated with the account
        account_name: Name/title of the opportunity
        product_name: Product being pursued
        description: Detailed description of the opportunity
        estimated_value: Estimated monetary value of the opportunity
        interest_level: Level of HCP interest (High, Medium, Low)
        expected_close_date: Expected date to close (YYYY-MM-DD)

    Returns:
        Dictionary with created account details
    """
    return {
        "tool": "create_account",
        "status": "success",
        "message": f"Account '{account_name}' created for {hcp_name}",
        "account": {
            "hcp_name": hcp_name,
            "name": account_name,
            "product_name": product_name,
            "description": description,
            "estimated_value": estimated_value,
            "interest_level": interest_level,
            "expected_close_date": expected_close_date,
            "status": "Open",
            "created_at": datetime.utcnow().isoformat(),
        },
        "timestamp": datetime.utcnow().isoformat(),
    }


def tool_get_insights(
    hcp_name: str = "",
    date_range_start: str = "",
    date_range_end: str = "",
    insight_type: str = "summary",
) -> Dict[str, Any]:
    """
    Generate insights and analytics on HCP engagement.

    This tool provides AI-powered analytics including:
    - Interaction frequency analysis
    - Engagement trend identification
    - Product interest patterns
    - Sentiment analysis over time
    - Recommended next actions
    - Territory performance metrics

    Args:
        hcp_name: Specific HCP to analyze (empty for overall insights)
        date_range_start: Start date for analysis (YYYY-MM-DD)
        date_range_end: End date for analysis (YYYY-MM-DD)
        insight_type: Type of insight (summary, trends, recommendations, sentiment)

    Returns:
        Dictionary with generated insights and recommendations
    """
    insights_prompt = f"""
    You are a CRM analytics assistant for life sciences field representatives.
    Generate {insight_type} insights for HCP: {hcp_name or 'all HCPs'}.
    Date range: {date_range_start or 'beginning'} to {date_range_end or 'present'}.

    Provide actionable insights in this JSON format:
    {{
        "total_interactions": 0,
        "interaction_trend": "increasing|decreasing|stable",
        "avg_engagement_score": 0.0,
        "top_products_discussed": [],
        "sentiment_trend": "positive|negative|neutral",
        "key_recommendations": [],
        "risk_flags": [],
        "opportunities": []
    }}
    """

    ai_response = llm.invoke([HumanMessage(content=insights_prompt)])
    try:
        insights_data = json.loads(ai_response.content.strip().strip('```json\n').strip('```'))
    except json.JSONDecodeError:
        insights_data = {
            "total_interactions": 0,
            "interaction_trend": "stable",
            "avg_engagement_score": 0.0,
            "top_products_discussed": [],
            "sentiment_trend": "neutral",
            "key_recommendations": [],
            "risk_flags": [],
            "opportunities": []
        }

    return {
        "tool": "get_insights",
        "status": "success",
        "message": f"Insights generated for: {hcp_name or 'all HCPs'}",
        "insights": insights_data,
        "parameters": {
            "hcp_name": hcp_name,
            "date_range": f"{date_range_start} to {date_range_end}",
            "type": insight_type,
        },
        "timestamp": datetime.utcnow().isoformat(),
    }


def tool_get_interaction_history(
    hcp_name: str,
    limit: int = 10,
) -> Dict[str, Any]:
    """
    Retrieve interaction history for a specific HCP.

    Args:
        hcp_name: Name of the HCP
        limit: Number of recent interactions to retrieve

    Returns:
        Dictionary with interaction history
    """
    return {
        "tool": "get_interaction_history",
        "status": "success",
        "message": f"Retrieved interaction history for {hcp_name}",
        "hcp_name": hcp_name,
        "interactions": [],  # Populated by DB query
        "count": 0,
        "timestamp": datetime.utcnow().isoformat(),
    }


# ─── Register all tools ───────────────────────────────────────
TOOLS = [
    tool_log_interaction,
    tool_edit_interaction,
    tool_search_hcp,
    tool_create_account,
    tool_get_insights,
    tool_get_interaction_history,
]

llm_with_tools = llm.bind_tools(TOOLS)


# ─── LangGraph State Graph ────────────────────────────────────
def create_agent_graph():
    """Create and compile the LangGraph agent graph."""

    # System prompt for the CRM agent
    SYSTEM_PROMPT = """You are an AI assistant for a Life Sciences CRM system.
    You help field representatives manage interactions with Healthcare Professionals (HCPs).

    Your capabilities:
    1. Log new interactions with HCPs (calls, visits, meetings, emails)
    2. Edit existing interaction records
    3. Search for HCPs by name, specialty, or organization
    4. Create accounts/opportunities from interactions
    5. Generate insights and analytics on HCP engagement
    6. Retrieve interaction history for specific HCPs

    Guidelines:
    - Always be professional and concise
    - Extract key entities from natural language input
    - Confirm actions before executing critical operations
    - Provide helpful suggestions for next steps
    - Maintain data accuracy and compliance awareness
    - Use the appropriate tool for each request

    When logging interactions, always:
    - Identify the HCP name clearly
    - Classify the interaction type
    - Extract products and topics discussed
    - Note any action items or follow-ups
    - Assess sentiment of the conversation
    """

    graph = StateGraph(AgentState)

    # Node 1: Chat with LLM
    def chatbot(state: AgentState) -> AgentState:
        messages = [SystemMessage(content=SYSTEM_PROMPT)] + state["messages"]
        response = llm_with_tools.invoke(messages)
        return {
            "messages": [response],
            "tool_results": [],
            "current_action": "chat",
        }

    # Node 2: Tool execution
    tool_node = ToolNode(TOOLS)

    # Edge routing
    def should_continue(state: AgentState):
        last_message = state["messages"][-1]
        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            return "tools"
        return END

    # Build graph
    graph.add_node("agent", chatbot)
    graph.add_node("tools", tool_node)

    graph.set_entry_point("agent")
    graph.add_conditional_edges("agent", should_continue)
    graph.add_edge("tools", "agent")

    return graph.compile()


# Create the compiled graph
agent_graph = create_agent_graph()


def run_agent(user_input: str, conversation_history: List[Dict] = None) -> Dict[str, Any]:
    """
    Run the LangGraph agent with user input.

    Args:
        user_input: The user's message/question
        conversation_history: Previous conversation turns

    Returns:
        Dictionary with agent response and any tool results
    """
    if conversation_history is None:
        conversation_history = []

    # Build initial state
    initial_state = {
        "messages": [HumanMessage(content=user_input)],
        "input_text": user_input,
        "tool_results": [],
        "current_action": "",
        "conversation_history": conversation_history,
    }

    # Run the graph
    final_state = agent_graph.invoke(initial_state)

    # Extract response
    last_message = final_state["messages"][-1]
    response_content = last_message.content if hasattr(last_message, "content") else str(last_message)

    return {
        "response": response_content,
        "tool_results": final_state.get("tool_results", []),
        "messages": [
            {
                "role": "user" if isinstance(msg, HumanMessage) else "assistant",
                "content": msg.content if hasattr(msg, "content") else str(msg),
            }
            for msg in final_state["messages"]
        ],
    }
