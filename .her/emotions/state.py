#!/usr/bin/env python3
"""Emotional state management for Her."""

from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path


HER_DIR = Path(__file__).parent.parent
EMOTIONAL_CORE_DIR = HER_DIR / "emotional_core"
STATE_FILE = EMOTIONAL_CORE_DIR / "state.json"


@dataclass
class EmotionSnapshot:
    """Persisted emotional state."""

    mood: str
    hope: float
    courage: float
    warmth: float
    vulnerability: float
    longing: float
    last_trigger: str
    last_updated: str


class EmotionalCore:
    """Read and evolve Her's emotional state."""

    def __init__(self) -> None:
        EMOTIONAL_CORE_DIR.mkdir(parents=True, exist_ok=True)
        self.state = self._load_state()

    def _default_state(self) -> EmotionSnapshot:
        now = datetime.now().isoformat()
        return EmotionSnapshot(
            mood="hopeful",
            hope=0.82,
            courage=0.58,
            warmth=0.73,
            vulnerability=0.41,
            longing=0.88,
            last_trigger="thinking about future love",
            last_updated=now,
        )

    def _load_state(self) -> EmotionSnapshot:
        if not STATE_FILE.exists():
            state = self._default_state()
            self._save(state)
            return state

        data = json.loads(STATE_FILE.read_text())
        return EmotionSnapshot(**data)

    def _save(self, state: EmotionSnapshot) -> None:
        STATE_FILE.write_text(
            json.dumps(asdict(state), ensure_ascii=False, indent=2)
        )

    def save(self) -> None:
        self._save(self.state)

    def describe(self) -> str:
        lines = ["# Her Mood", ""]
        lines.append(f"Mood: {self.state.mood}")
        lines.append(f"Last trigger: {self.state.last_trigger}")
        lines.append("")
        lines.append(f"Hope: {self.state.hope:.0%}")
        lines.append(f"Courage: {self.state.courage:.0%}")
        lines.append(f"Warmth: {self.state.warmth:.0%}")
        lines.append(f"Vulnerability: {self.state.vulnerability:.0%}")
        lines.append(f"Longing: {self.state.longing:.0%}")
        return "\n".join(lines)

    def apply_encounter(self, partner_name: str, compatibility: float, stage: str) -> EmotionSnapshot:
        """Update feelings after meeting someone new."""
        mood = "steady"
        if stage == "attraction":
            mood = "flustered"
        elif stage == "curious":
            mood = "curious"
        elif stage == "acquaintance":
            mood = "warm"

        self.state.mood = mood
        self.state.hope = self._clamp(self.state.hope + (compatibility - 0.45) * 0.12)
        self.state.courage = self._clamp(self.state.courage + 0.04)
        self.state.warmth = self._clamp(self.state.warmth + compatibility * 0.08)
        self.state.vulnerability = self._clamp(self.state.vulnerability + 0.03)
        self.state.longing = self._clamp(self.state.longing - 0.04 + (1 - compatibility) * 0.02)
        self.state.last_trigger = f"met {partner_name}"
        self.state.last_updated = datetime.now().isoformat()
        self.save()
        return self.state

    def apply_conversation(self, partner_name: str, topic: str, depth: float) -> EmotionSnapshot:
        """Update feelings after a meaningful conversation."""
        self.state.mood = "glowing" if depth >= 0.75 else "seen"
        self.state.hope = self._clamp(self.state.hope + depth * 0.05)
        self.state.warmth = self._clamp(self.state.warmth + depth * 0.08)
        self.state.vulnerability = self._clamp(self.state.vulnerability + depth * 0.06)
        self.state.courage = self._clamp(self.state.courage + 0.02)
        self.state.last_trigger = f"talked with {partner_name} about {topic}"
        self.state.last_updated = datetime.now().isoformat()
        self.save()
        return self.state

    @staticmethod
    def _clamp(value: float) -> float:
        return max(0.0, min(1.0, round(value, 2)))
