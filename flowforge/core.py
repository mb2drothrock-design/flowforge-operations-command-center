from __future__ import annotations

import re
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Iterable

EMAIL_RE = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
PHONE_RE = re.compile(r"(?<!\d)(?:\+?1[-.\s]?)?(?:\(\d{3}\)|\d{3})[-.\s]\d{3}[-.\s]\d{4}(?!\d)")
MONEY_RE = re.compile(r"\$\s?\d{1,3}(?:,\d{3})*(?:\.\d{2})?")
ORDER_RE = re.compile(r"\b(?:order|ticket|case|invoice|po)[\s:#-]*([A-Z0-9-]{4,})\b", re.I)

CATEGORY_RULES = {
    "billing": ("invoice", "billing", "refund", "charged", "payment", "credit card"),
    "sales": ("quote", "pricing", "demo", "purchase", "buy", "contract"),
    "support": ("broken", "error", "failed", "issue", "problem", "not working", "bug", "outage", "down", "blocked"),
    "operations": ("shipment", "delivery", "warehouse", "vendor", "inventory", "order"),
    "account": ("login", "password", "account", "access", "user"),
}

URGENT_TERMS = {
    "critical": 45,
    "outage": 45,
    "down": 35,
    "urgent": 30,
    "asap": 25,
    "immediately": 25,
    "today": 15,
    "blocked": 20,
    "cannot": 15,
    "can't": 15,
}

@dataclass(frozen=True)
class IntakeResult:
    source: str
    subject: str
    text: str
    category: str
    priority_score: int
    priority_label: str
    sentiment: str
    emails: list[str]
    phones: list[str]
    monetary_values: list[str]
    reference_ids: list[str]
    suggested_owner: str
    suggested_action: str
    created_at: str

    def to_dict(self) -> dict:
        return asdict(self)


def classify_category(text: str) -> str:
    lower = text.lower()
    best = ("general", 0)
    for category, terms in CATEGORY_RULES.items():
        score = sum(1 for term in terms if term in lower)
        if score > best[1]:
            best = (category, score)
    return best[0]


def score_priority(text: str, category: str) -> int:
    lower = text.lower()
    score = 15
    for term, weight in URGENT_TERMS.items():
        if term in lower:
            score += weight
    if category == "billing" and any(term in lower for term in ("duplicate", "fraud", "charged twice")):
        score += 20
    if "vip" in lower or "enterprise" in lower:
        score += 10
    return min(score, 100)


def priority_label(score: int) -> str:
    if score >= 80:
        return "P0 - Critical"
    if score >= 60:
        return "P1 - High"
    if score >= 35:
        return "P2 - Normal"
    return "P3 - Low"


def sentiment(text: str) -> str:
    lower = text.lower()
    negative = ("angry", "frustrated", "unacceptable", "terrible", "broken", "failed", "urgent", "refund")
    positive = ("thanks", "thank you", "great", "appreciate", "happy")
    neg_score = sum(term in lower for term in negative)
    pos_score = sum(term in lower for term in positive)
    if neg_score > pos_score:
        return "negative"
    if pos_score > neg_score:
        return "positive"
    return "neutral"


def route(category: str, score: int) -> tuple[str, str]:
    owners = {
        "billing": "Finance Operations",
        "sales": "Revenue Operations",
        "support": "Technical Support",
        "operations": "Fulfillment Operations",
        "account": "Customer Success",
        "general": "Operations Triage",
    }
    actions = {
        "billing": "Verify transaction details and resolve billing discrepancy.",
        "sales": "Review request, qualify opportunity, and prepare next-step response.",
        "support": "Reproduce issue, capture diagnostics, and provide remediation path.",
        "operations": "Check fulfillment status and coordinate the operational handoff.",
        "account": "Validate account state and restore or update access as needed.",
        "general": "Review request and route to the correct operational owner.",
    }
    action = actions[category]
    if score >= 80:
        action = "Escalate immediately. " + action
    elif score >= 60:
        action = "Prioritize for same-day action. " + action
    return owners[category], action


def analyze_intake(source: str, subject: str, text: str) -> IntakeResult:
    combined = f"{subject}\n{text}".strip()
    category = classify_category(combined)
    score = score_priority(combined, category)
    owner, action = route(category, score)
    return IntakeResult(
        source=source,
        subject=subject.strip() or "Untitled request",
        text=text.strip(),
        category=category,
        priority_score=score,
        priority_label=priority_label(score),
        sentiment=sentiment(combined),
        emails=sorted(set(EMAIL_RE.findall(combined))),
        phones=sorted(set(PHONE_RE.findall(combined))),
        monetary_values=sorted(set(MONEY_RE.findall(combined))),
        reference_ids=sorted(set(match.group(1) for match in ORDER_RE.finditer(combined))),
        suggested_owner=owner,
        suggested_action=action,
        created_at=datetime.now(timezone.utc).isoformat(timespec="seconds"),
    )
