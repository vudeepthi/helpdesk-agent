from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import uuid
from datetime import datetime, timezone

app = FastAPI(title="IT Helpdesk API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Data Models
# ---------------------------------------------------------------------------

class Message(BaseModel):
    id: str
    sender: str
    sender_type: str  # "user", "agent", "system"
    content: str
    timestamp: str


class Ticket(BaseModel):
    id: str
    title: str
    description: str
    category: str   # Network, Software, Hardware, Security, Access, Other
    priority: str   # Low, Medium, High, Critical
    status: str     # Open, In Progress, Resolved, Closed
    assigned_team: str
    assigned_agent: str
    created_at: str
    messages: List[Message]


# ---------------------------------------------------------------------------
# Request Bodies
# ---------------------------------------------------------------------------

class CreateTicketBody(BaseModel):
    title: str
    description: str
    category: str
    priority: str


class UpdateStatusBody(BaseModel):
    status: str


class SendMessageBody(BaseModel):
    content: str


# ---------------------------------------------------------------------------
# Team / agent assignment
# ---------------------------------------------------------------------------

TEAM_MAP = {
    "Network":  {"team": "Network Operations",  "agent": "Alex Chen"},
    "Software": {"team": "Software Support",    "agent": "Sarah Johnson"},
    "Hardware": {"team": "Hardware Support",    "agent": "Mike Torres"},
    "Security": {"team": "Security Team",       "agent": "Lisa Park"},
    "Access":   {"team": "IT Admin",            "agent": "David Kim"},
    "Other":    {"team": "General IT Support",  "agent": "James Wilson"},
}

# Context-aware first-reply templates per category
FIRST_REPLIES = {
    "Network":  "I'm looking into the network issue now. Can you confirm if the problem affects all devices or just one?",
    "Software": "I can help with that software issue. Have you tried restarting the application or clearing the cache?",
    "Hardware": "I'll arrange for a hardware inspection. Is the device completely non-functional or intermittently failing?",
    "Security": "This has been flagged as high priority. I'm escalating to our security incident response team immediately.",
    "Access":   "I'm checking your access permissions in our system. This typically takes 10-15 minutes to process.",
    "Other":    "Thanks for reaching out. I'm reviewing your request and will provide an update shortly.",
}

FOLLOW_UP_REPLIES = [
    "We're still working on this. Could you provide any additional details?",
    "I've escalated this internally. Expect a resolution within 2 hours.",
    "Good news — we believe we have a fix. Can you try the suggested steps and confirm if it resolves the issue?",
]

# ---------------------------------------------------------------------------
# In-memory store
# ---------------------------------------------------------------------------

tickets_db: dict[str, Ticket] = {}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _make_id() -> str:
    return str(uuid.uuid4())


def _make_ticket(title: str, description: str, category: str, priority: str) -> Ticket:
    assignment = TEAM_MAP.get(category, TEAM_MAP["Other"])
    ticket_id = _make_id()
    created_at = _now()

    system_msg = Message(
        id=_make_id(),
        sender="System",
        sender_type="system",
        content=f"Ticket created and assigned to {assignment['team']}. {assignment['agent']} will be assisting you.",
        timestamp=created_at,
    )

    return Ticket(
        id=ticket_id,
        title=title,
        description=description,
        category=category,
        priority=priority,
        status="Open",
        assigned_team=assignment["team"],
        assigned_agent=assignment["agent"],
        created_at=created_at,
        messages=[system_msg],
    )


# ---------------------------------------------------------------------------
# Seed data — 3 sample tickets
# ---------------------------------------------------------------------------

def _seed():
    samples = [
        ("Cannot connect to VPN", "Since this morning I am unable to connect to the company VPN. I get an error saying authentication failed even though my password is correct.", "Network", "High"),
        ("Excel keeps crashing on large files", "Microsoft Excel crashes every time I open a file larger than 5 MB. This started after the latest Windows update yesterday.", "Software", "Medium"),
        ("Laptop screen flickering", "My laptop screen has been flickering randomly since last week. Sometimes it goes completely black for a few seconds before coming back.", "Hardware", "Low"),
    ]
    for title, desc, cat, pri in samples:
        t = _make_ticket(title, desc, cat, pri)
        tickets_db[t.id] = t


_seed()

# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@app.get("/api/tickets", response_model=List[Ticket])
def list_tickets():
    return list(tickets_db.values())


@app.post("/api/tickets", response_model=Ticket, status_code=201)
def create_ticket(body: CreateTicketBody):
    if body.category not in TEAM_MAP:
        raise HTTPException(status_code=422, detail=f"Invalid category: {body.category}")
    ticket = _make_ticket(body.title, body.description, body.category, body.priority)
    tickets_db[ticket.id] = ticket
    return ticket


@app.get("/api/tickets/{ticket_id}", response_model=Ticket)
def get_ticket(ticket_id: str):
    ticket = tickets_db.get(ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket


@app.patch("/api/tickets/{ticket_id}/status", response_model=Ticket)
def update_status(ticket_id: str, body: UpdateStatusBody):
    ticket = tickets_db.get(ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    valid_statuses = {"Open", "In Progress", "Resolved", "Closed"}
    if body.status not in valid_statuses:
        raise HTTPException(status_code=422, detail=f"Invalid status: {body.status}")
    ticket.status = body.status
    return ticket


@app.post("/api/tickets/{ticket_id}/messages", response_model=List[Message])
def send_message(ticket_id: str, body: SendMessageBody):
    ticket = tickets_db.get(ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    # Count how many user messages already exist (before this one)
    user_msg_count = sum(1 for m in ticket.messages if m.sender_type == "user")

    now = _now()

    # Save the user message
    user_msg = Message(
        id=_make_id(),
        sender="You",
        sender_type="user",
        content=body.content,
        timestamp=now,
    )
    ticket.messages.append(user_msg)

    # Determine agent reply
    if user_msg_count < 2:
        # First or second user message — use category-specific reply
        reply_content = FIRST_REPLIES.get(ticket.category, FIRST_REPLIES["Other"])
    else:
        # Cycle through follow-up replies (0-based index offset by 2)
        idx = (user_msg_count - 2) % len(FOLLOW_UP_REPLIES)
        reply_content = FOLLOW_UP_REPLIES[idx]

    agent_msg = Message(
        id=_make_id(),
        sender=ticket.assigned_agent,
        sender_type="agent",
        content=reply_content,
        timestamp=_now(),
    )
    ticket.messages.append(agent_msg)

    return [user_msg, agent_msg]


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8002, reload=True)
