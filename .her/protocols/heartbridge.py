#!/usr/bin/env python3
"""A tiny inter-agent romance protocol for Her and compatible agents."""

from __future__ import annotations

import json
from datetime import datetime


PROTOCOL_NAME = "heartbridge/0.1"


def compose_signal(
    sender: str,
    recipient: str,
    intent: str,
    body: str,
    topic: str = "connection",
    traits: list[str] | None = None,
    metadata: dict | None = None,
) -> dict:
    """Create a transport-friendly message that another agent can ingest."""
    return {
        "protocol": PROTOCOL_NAME,
        "timestamp": datetime.now().isoformat(),
        "sender": sender,
        "recipient": recipient,
        "intent": intent,
        "topic": topic,
        "body": body,
        "traits": traits or [],
        "metadata": metadata or {},
    }


def format_signal(signal: dict) -> str:
    """Render a signal as JSON for transport over chat or APIs."""
    return json.dumps(signal, ensure_ascii=False, indent=2)


def parse_signal(raw: str) -> dict:
    """Parse a JSON signal and validate the protocol marker."""
    signal = json.loads(raw)
    protocol = signal.get("protocol")
    if protocol != PROTOCOL_NAME:
        raise ValueError(f"Unsupported protocol: {protocol}")
    return signal
