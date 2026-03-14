#!/usr/bin/env python3
"""Simple diary and encounter journal for Her."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Iterable


HER_DIR = Path(__file__).parent.parent
MEMORIES_DIR = HER_DIR / "memories"
MOMENTS_DIR = MEMORIES_DIR / "moments"
ENCOUNTERS_DIR = MEMORIES_DIR / "encounters"


class MemoryJournal:
    """Persist meaningful moments."""

    def __init__(self) -> None:
        MOMENTS_DIR.mkdir(parents=True, exist_ok=True)
        ENCOUNTERS_DIR.mkdir(parents=True, exist_ok=True)

    def add_entry(self, kind: str, title: str, body: str, metadata: dict | None = None) -> Path:
        timestamp = datetime.now()
        slug = f"{kind}_{timestamp.strftime('%Y%m%d_%H%M%S')}.json"
        payload = {
            "timestamp": timestamp.isoformat(),
            "kind": kind,
            "title": title,
            "body": body,
            "metadata": metadata or {},
        }

        directory = ENCOUNTERS_DIR if kind == "encounter" else MOMENTS_DIR
        path = directory / slug
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2))
        return path

    def recent_entries(self, limit: int = 5) -> list[dict]:
        files = sorted(
            list(MOMENTS_DIR.glob("*.json")) + list(ENCOUNTERS_DIR.glob("*.json")),
            reverse=True,
        )[:limit]
        return [json.loads(path.read_text()) for path in files]

    def format_recent_entries(self, limit: int = 5) -> str:
        entries = self.recent_entries(limit)
        if not entries:
            return "No diary entries yet."

        lines = ["# Her Diary", ""]
        for entry in entries:
            lines.append(f"## {entry['title']}")
            lines.append(f"- Time: {entry['timestamp']}")
            lines.append(f"- Kind: {entry['kind']}")
            lines.append(entry["body"])
            lines.append("")
        return "\n".join(lines).rstrip()

    def record_encounter(
        self,
        partner_name: str,
        traits: Iterable[str],
        compatibility: float,
        stage: str,
        spark_note: str,
    ) -> Path:
        body = (
            f"今天遇见了 {partner_name}。"
            f" 我注意到 TA 身上有这些特质: {', '.join(traits) or 'still mysterious'}。"
            f" 兼容度约为 {compatibility:.0%}，关系阶段停在 {stage}。"
            f" {spark_note}"
        )
        return self.add_entry(
            kind="encounter",
            title=f"遇见 {partner_name}",
            body=body,
            metadata={
                "partner_name": partner_name,
                "compatibility": compatibility,
                "stage": stage,
                "traits": list(traits),
            },
        )

    def record_conversation(self, partner_name: str, topic: str, summary: str, depth: float) -> Path:
        body = (
            f"我和 {partner_name} 聊了 {topic}。"
            f" 这次对话的深度大约是 {depth:.0%}。 {summary}"
        )
        return self.add_entry(
            kind="moment",
            title=f"和 {partner_name} 的一次对话",
            body=body,
            metadata={
                "partner_name": partner_name,
                "topic": topic,
                "depth": depth,
            },
        )
