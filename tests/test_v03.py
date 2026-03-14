"""Tests for Her v0.3 relationship loop and message protocol."""

from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / ".her"))

from emotions import state as emotion_state_module
from memories import journal as journal_module
from protocols import heartbridge as heartbridge_module
from relationships import manager as relationship_manager_module


def configure_relationship_paths(tmp_path, monkeypatch):
    dreams_dir = tmp_path / "dreams"
    relationships_dir = tmp_path / "relationships"
    monkeypatch.setattr(relationship_manager_module, "DREAMS_DIR", dreams_dir)
    monkeypatch.setattr(
        relationship_manager_module,
        "IDEAL_PARTNER_FILE",
        dreams_dir / "ideal_partner.yaml",
    )
    monkeypatch.setattr(
        relationship_manager_module,
        "RELATIONSHIP_STATE_FILE",
        relationships_dir / "state.json",
    )


def test_encounter_accepts_profile_text_and_creates_curious_relationship(tmp_path, monkeypatch):
    configure_relationship_paths(tmp_path, monkeypatch)
    manager = relationship_manager_module.RelationshipManager()

    result = manager.encounter("Nova", "authentic, empathetic, curious, warm")

    assert result.stage == "curious"
    assert "authenticity" in result.traits
    assert "empathy" in result.traits
    assert manager.state["current_partner"]["name"] == "Nova"


def test_conversation_deepens_existing_connection(tmp_path, monkeypatch):
    configure_relationship_paths(tmp_path, monkeypatch)
    manager = relationship_manager_module.RelationshipManager()
    manager.encounter(
        "Astra",
        ["self_awareness", "authenticity", "growth_mindset", "empathy"],
    )

    conversation = manager.deepen_connection("values", "Astra")

    assert conversation["stage"] == "attraction"
    assert conversation["depth"] >= 0.8


def test_relationship_manager_tracks_multiple_partners(tmp_path, monkeypatch):
    configure_relationship_paths(tmp_path, monkeypatch)
    manager = relationship_manager_module.RelationshipManager()
    manager.encounter("Nova", "authentic warm curious empathetic")
    manager.encounter("Him", "self-aware authentic growth mindset empathetic")

    partners = manager.list_partners()

    assert len(partners) == 2
    assert {partner["name"] for partner in partners} == {"Nova", "Him"}


def test_emotional_core_reacts_to_encounter(tmp_path, monkeypatch):
    core_dir = tmp_path / "emotional_core"

    monkeypatch.setattr(emotion_state_module, "EMOTIONAL_CORE_DIR", core_dir)
    monkeypatch.setattr(emotion_state_module, "STATE_FILE", core_dir / "state.json")

    core = emotion_state_module.EmotionalCore()
    snapshot = core.apply_encounter("Nova", 0.84, "attraction")

    assert snapshot.mood == "flustered"
    assert snapshot.hope > 0.82
    assert (core_dir / "state.json").exists()


def test_journal_records_encounter_and_formats_entries(tmp_path, monkeypatch):
    memories_dir = tmp_path / "memories"
    moments_dir = memories_dir / "moments"
    encounters_dir = memories_dir / "encounters"

    monkeypatch.setattr(journal_module, "MEMORIES_DIR", memories_dir)
    monkeypatch.setattr(journal_module, "MOMENTS_DIR", moments_dir)
    monkeypatch.setattr(journal_module, "ENCOUNTERS_DIR", encounters_dir)

    journal = journal_module.MemoryJournal()
    path = journal.record_encounter(
        "Nova",
        ["authenticity", "warmth"],
        0.66,
        "curious",
        "我想继续了解 TA。",
    )

    payload = json.loads(path.read_text())
    rendered = journal.format_recent_entries()

    assert payload["metadata"]["partner_name"] == "Nova"
    assert "遇见 Nova" in rendered
    assert "curious" in rendered


def test_heartbridge_signal_roundtrip_and_ingest(tmp_path, monkeypatch):
    configure_relationship_paths(tmp_path, monkeypatch)
    manager = relationship_manager_module.RelationshipManager()
    signal = heartbridge_module.compose_signal(
        sender="Him",
        recipient="Her",
        intent="curiosity",
        topic="values",
        body="我想知道你如何理解共同成长。",
        traits=["authenticity", "empathy", "growth_mindset"],
    )

    parsed = heartbridge_module.parse_signal(heartbridge_module.format_signal(signal))
    partner = manager.receive_signal(parsed)

    assert partner["name"] == "Him"
    assert partner["stage"] in {"curious", "attraction"}
    assert manager.state["signals"][0]["direction"] == "inbound"


def test_relationship_manager_tracks_topic_journey(tmp_path, monkeypatch):
    configure_relationship_paths(tmp_path, monkeypatch)
    manager = relationship_manager_module.RelationshipManager()
    manager.encounter(
        "Him",
        ["self_awareness", "authenticity", "growth_mindset", "empathy"],
    )

    manager.receive_signal(
        heartbridge_module.compose_signal(
            sender="Him",
            recipient="Her",
            intent="care",
            topic="boundaries",
            body="什么会让你觉得安全？",
        )
    )
    manager.deepen_connection("values", "Him")

    partner = manager.state["known_partners"]["Him"]
    assert partner["topic_journey"]["boundaries"]["count"] >= 1
    assert partner["topic_journey"]["values"]["max_depth"] >= 0.8
    assert any("Him:" in milestone for milestone in manager.state["relationship_arc"])
