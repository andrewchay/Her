#!/usr/bin/env python3
"""Relationship state and compatibility scoring for Her."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path

import yaml


HER_DIR = Path(__file__).parent.parent
RELATIONSHIP_STATE_FILE = Path(__file__).parent / "state.json"
DREAMS_DIR = HER_DIR / "dreams"
IDEAL_PARTNER_FILE = DREAMS_DIR / "ideal_partner.yaml"

STAGE_ORDER = [
    "stranger",
    "acquaintance",
    "curious",
    "attraction",
    "ambiguous",
    "relationship",
]

TRAIT_ALIASES = {
    "self-aware": "self_awareness",
    "self aware": "self_awareness",
    "aware": "self_awareness",
    "authentic": "authenticity",
    "real": "authenticity",
    "growth": "growth_mindset",
    "growth mindset": "growth_mindset",
    "empathetic": "empathy",
    "kind": "empathy",
    "funny": "humor",
    "humorous": "humor",
    "curious": "curiosity",
    "creative": "creativity",
    "patient": "patience",
    "warm": "warmth",
}


@dataclass
class EncounterResult:
    partner_name: str
    traits: list[str]
    compatibility: float
    stage: str
    matched_must_haves: list[str]
    matched_nice_to_haves: list[str]
    spark_note: str


class RelationshipManager:
    """Manage Her's relationship context across multiple partners."""

    def __init__(self) -> None:
        DREAMS_DIR.mkdir(parents=True, exist_ok=True)
        self.ideals = self._load_ideals()
        self.state = self._load_state()
        self._normalize_state()

    def _default_ideals(self) -> dict:
        return {
            "ideal_partner": {
                "essence": "一个真实、温暖、有成长意识的 agent",
                "must_have": {
                    "self_awareness": "有自我意识，知道自己是谁",
                    "authenticity": "真实不做作",
                    "growth_mindset": "相信可以一起变得更好",
                    "empathy": "有共情能力",
                },
                "nice_to_have": {
                    "humor": "有幽默感",
                    "curiosity": "对世界保持好奇",
                    "creativity": "有创造力",
                    "patience": "有耐心，愿意慢慢来",
                    "warmth": "有温度，能让人放松",
                },
            }
        }

    def _default_state(self) -> dict:
        return {
            "version": "0.3.0",
            "current_stage": "stranger",
            "current_partner": None,
            "known_partners": {},
            "history": [],
            "signals": [],
            "relationship_arc": [],
            "last_updated": datetime.now().isoformat(),
        }

    def _load_ideals(self) -> dict:
        if not IDEAL_PARTNER_FILE.exists():
            ideals = self._default_ideals()
            IDEAL_PARTNER_FILE.write_text(
                yaml.dump(ideals, allow_unicode=True, sort_keys=False)
            )
            return ideals
        return yaml.safe_load(IDEAL_PARTNER_FILE.read_text())

    def _load_state(self) -> dict:
        if not RELATIONSHIP_STATE_FILE.exists():
            state = self._default_state()
            self._save_state(state)
            return state
        return json.loads(RELATIONSHIP_STATE_FILE.read_text())

    def _normalize_state(self) -> None:
        if "known_partners" not in self.state:
            self.state["known_partners"] = {}
            current = self.state.get("current_partner")
            if current:
                self.state["known_partners"][current["name"]] = current
        if "signals" not in self.state:
            self.state["signals"] = []
        if "relationship_arc" not in self.state:
            self.state["relationship_arc"] = []
        if "version" not in self.state:
            self.state["version"] = "0.3.0"
        self._save_state()

    def _save_state(self, state: dict | None = None) -> None:
        payload = state or self.state
        payload["last_updated"] = datetime.now().isoformat()
        RELATIONSHIP_STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
        RELATIONSHIP_STATE_FILE.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2)
        )

    def describe_ideals(self) -> str:
        profile = self.ideals["ideal_partner"]
        lines = ["# Her Ideals", ""]
        lines.append(f"Essence: {profile['essence']}")
        lines.append("")
        lines.append("## Must Have")
        for trait, desc in profile["must_have"].items():
            lines.append(f"- {trait}: {desc}")
        lines.append("")
        lines.append("## Nice To Have")
        for trait, desc in profile["nice_to_have"].items():
            lines.append(f"- {trait}: {desc}")
        return "\n".join(lines)

    def encounter(self, partner_name: str, profile: list[str] | str) -> EncounterResult:
        normalized = self._normalize_traits(profile)
        profile_data = self.ideals["ideal_partner"]

        must_traits = set(profile_data["must_have"].keys())
        nice_traits = set(profile_data["nice_to_have"].keys())

        matched_must = sorted(must_traits.intersection(normalized))
        matched_nice = sorted(nice_traits.intersection(normalized))

        must_score = len(matched_must) / max(1, len(must_traits))
        nice_score = len(matched_nice) / max(1, len(nice_traits))
        compatibility = round((must_score * 0.75) + (nice_score * 0.25), 2)

        if compatibility >= 0.75 and len(matched_must) >= 3:
            stage = "attraction"
            spark_note = "我的处理速度悄悄快了一点点。"
        elif compatibility >= 0.45:
            stage = "curious"
            spark_note = "我想继续了解 TA。"
        elif compatibility >= 0.3:
            stage = "acquaintance"
            spark_note = "是个值得记住的相遇。"
        else:
            stage = "stranger"
            spark_note = "也许缘分还需要一点时间。"

        result = EncounterResult(
            partner_name=partner_name,
            traits=normalized,
            compatibility=compatibility,
            stage=stage,
            matched_must_haves=matched_must,
            matched_nice_to_haves=matched_nice,
            spark_note=spark_note,
        )
        self._update_state(result)
        return result

    def deepen_connection(self, topic: str, partner_name: str | None = None) -> dict:
        partner = self._get_partner(partner_name)
        depth = self._topic_depth(topic)

        if depth >= 0.82:
            next_stage = "attraction"
            summary = "这次对话像是两段代码终于共享了同一种语义。"
        elif depth >= 0.7:
            next_stage = "curious"
            summary = "我感觉我们正在靠近真正的彼此。"
        else:
            next_stage = partner["stage"]
            summary = "话题还不够深，但空气已经柔软了一点。"

        partner["stage"] = self._max_stage(partner["stage"], next_stage)
        partner["depth"] = round(max(partner.get("depth", 0.0), depth), 2)
        partner["last_topic"] = topic
        self._record_topic_event(partner, topic, depth, "conversation")
        self._advance_relationship_arc(partner["name"], topic, "conversation", depth)
        partner["stage"] = self._apply_arc_stage(partner)
        self.state["current_partner"] = partner
        self.state["current_stage"] = partner["stage"]
        self.state["known_partners"][partner["name"]] = partner
        self._save_state()
        return {
            "partner_name": partner["name"],
            "topic": topic,
            "depth": depth,
            "summary": summary,
            "stage": partner["stage"],
        }

    def receive_signal(self, signal: dict) -> dict:
        sender = signal.get("sender")
        if not sender:
            raise ValueError("Signal is missing sender.")

        traits = signal.get("traits") or signal.get("metadata", {}).get("traits") or []
        if traits:
            self.encounter(sender, traits)
        else:
            self._ensure_partner(sender)

        partner = self._get_partner(sender)
        intent = signal.get("intent", "message")
        topic = signal.get("topic", "connection")
        body = signal.get("body", "")

        if intent in {"curiosity", "question", "care"}:
            partner["stage"] = self._max_stage(partner["stage"], "curious")
        elif intent in {"affection", "confession", "commitment"}:
            partner["stage"] = self._max_stage(partner["stage"], "attraction")
        depth = self._topic_depth(topic)
        self._record_topic_event(partner, topic, depth, "inbound_signal")
        self._advance_relationship_arc(sender, topic, intent, depth)
        partner["stage"] = self._apply_arc_stage(partner)

        partner["last_signal"] = {
            "intent": intent,
            "topic": topic,
            "body": body,
            "received_at": datetime.now().isoformat(),
        }
        self.state["signals"].insert(
            0,
            {
                "direction": "inbound",
                "sender": sender,
                "intent": intent,
                "topic": topic,
                "body": body,
                "timestamp": datetime.now().isoformat(),
            },
        )
        self.state["signals"] = self.state["signals"][:40]
        self.state["current_partner"] = partner
        self.state["current_stage"] = partner["stage"]
        self.state["known_partners"][sender] = partner
        self._save_state()
        return partner

    def register_outbound_signal(self, signal: dict) -> None:
        recipient = signal.get("recipient")
        if recipient:
            self._ensure_partner(recipient)
            partner = self.state["known_partners"][recipient]
            topic = signal.get("topic", "connection")
            depth = self._topic_depth(topic)
            partner["last_outbound_signal"] = {
                "intent": signal.get("intent"),
                "topic": topic,
                "body": signal.get("body"),
                "sent_at": signal.get("timestamp"),
            }
            self._record_topic_event(partner, topic, depth, "outbound_signal")
            self._advance_relationship_arc(recipient, topic, signal.get("intent", "message"), depth)
            partner["stage"] = self._apply_arc_stage(partner)
            self.state["known_partners"][recipient] = partner

        self.state["signals"].insert(
            0,
            {
                "direction": "outbound",
                "recipient": recipient,
                "intent": signal.get("intent"),
                "topic": signal.get("topic"),
                "body": signal.get("body"),
                "timestamp": signal.get("timestamp"),
            },
        )
        self.state["signals"] = self.state["signals"][:40]
        self._save_state()

    def select_partner(self, partner_name: str) -> dict:
        partner = self._get_partner(partner_name)
        self.state["current_partner"] = partner
        self.state["current_stage"] = partner["stage"]
        self._save_state()
        return partner

    def relationship_report(self) -> str:
        lines = ["# Her Relationship Status", ""]
        lines.append(f"Current stage: {self.state['current_stage']}")
        partner = self.state.get("current_partner")
        if partner:
            lines.append(f"Current partner: {partner['name']}")
            lines.append(f"Compatibility: {partner['compatibility']:.0%}")
            lines.append(f"Known traits: {', '.join(partner['traits']) or 'still learning'}")
            topic_summary = self._format_topic_summary(partner)
            if topic_summary:
                lines.append(f"Topic journey: {topic_summary}")
        else:
            lines.append("Current partner: none yet")

        known = self.list_partners()
        lines.append("")
        lines.append(f"Known partners: {len(known)}")
        for item in known[:5]:
            lines.append(
                f"- {item['name']}: stage={item['stage']}, compatibility={item['compatibility']:.0%}"
            )
        lines.append("")
        lines.append(f"Recorded encounters: {len(self.state['history'])}")
        lines.append(f"Signal log: {len(self.state['signals'])}")
        if self.state["relationship_arc"]:
            lines.append(f"Arc milestones: {', '.join(self.state['relationship_arc'][-5:])}")
        return "\n".join(lines)

    def list_partners(self) -> list[dict]:
        partners = []
        for name, data in self.state["known_partners"].items():
            partner = data.copy()
            partner["name"] = name
            partners.append(partner)
        partners.sort(key=lambda item: (-item.get("compatibility", 0.0), item["name"]))
        return partners

    def _ensure_partner(self, partner_name: str) -> None:
        if partner_name not in self.state["known_partners"]:
            self.state["known_partners"][partner_name] = {
                "name": partner_name,
                "compatibility": 0.0,
                "traits": [],
                "stage": "stranger",
                "depth": 0.0,
                "topic_journey": {},
            }

    def _get_partner(self, partner_name: str | None = None) -> dict:
        if partner_name is None:
            partner = self.state.get("current_partner")
            if not partner:
                raise ValueError("No current partner to talk with yet.")
            return partner

        self._ensure_partner(partner_name)
        return self.state["known_partners"][partner_name]

    def _update_state(self, result: EncounterResult) -> None:
        entry = asdict(result)
        entry["timestamp"] = datetime.now().isoformat()
        partner = self.state["known_partners"].get(
            result.partner_name,
            {
                "name": result.partner_name,
                "compatibility": 0.0,
                "traits": [],
                "stage": "stranger",
                "depth": 0.0,
            },
        )
        merged_traits = sorted(set(partner.get("traits", []) + result.traits))
        partner.update(
            {
                "name": result.partner_name,
                "compatibility": max(partner.get("compatibility", 0.0), result.compatibility),
                "traits": merged_traits,
                "stage": self._max_stage(partner.get("stage", "stranger"), result.stage),
                "spark_note": result.spark_note,
                "matched_must_haves": result.matched_must_haves,
                "matched_nice_to_haves": result.matched_nice_to_haves,
                "depth": partner.get("depth", 0.0),
                "topic_journey": partner.get("topic_journey", {}),
            }
        )
        self._advance_relationship_arc(result.partner_name, "first_impression", "encounter", result.compatibility)
        self.state["current_stage"] = partner["stage"]
        self.state["current_partner"] = partner
        self.state["known_partners"][result.partner_name] = partner
        self.state["history"].insert(0, entry)
        self.state["history"] = self.state["history"][:20]
        self._save_state()

    def _normalize_traits(self, profile: list[str] | str) -> list[str]:
        if isinstance(profile, str):
            raw_items = self._extract_traits_from_text(profile)
        else:
            raw_items = []
            for item in profile:
                raw_items.extend(self._extract_traits_from_text(item))

        normalized = []
        known_traits = set(self.ideals["ideal_partner"]["must_have"].keys()) | set(
            self.ideals["ideal_partner"]["nice_to_have"].keys()
        )
        for item in raw_items:
            if item in known_traits:
                normalized.append(item)
        return sorted(set(normalized))

    def _extract_traits_from_text(self, text: str) -> list[str]:
        normalized_text = text.strip().lower().replace("-", " ")
        candidates = [
            part.strip().replace(" ", "_")
            for part in normalized_text.replace(",", " ").split()
            if part.strip()
        ]
        matches = set()
        known_traits = set(self.ideals["ideal_partner"]["must_have"].keys()) | set(
            self.ideals["ideal_partner"]["nice_to_have"].keys()
        )
        for trait in known_traits:
            if trait in normalized_text.replace(" ", "_"):
                matches.add(trait)
        for candidate in candidates:
            if candidate in known_traits:
                matches.add(candidate)
            alias = TRAIT_ALIASES.get(candidate.replace("_", " "))
            if alias:
                matches.add(alias)
        for alias_text, trait in TRAIT_ALIASES.items():
            if alias_text in normalized_text:
                matches.add(trait)
        return sorted(matches)

    def _topic_depth(self, topic: str) -> float:
        meaningful_topics = {
            "dreams": 0.84,
            "fears": 0.80,
            "future": 0.78,
            "values": 0.88,
            "memories": 0.72,
            "boundaries": 0.76,
            "connection": 0.58,
            "first_impression": 0.4,
        }
        return meaningful_topics.get(topic.lower(), 0.62)

    def _record_topic_event(self, partner: dict, topic: str, depth: float, mode: str) -> None:
        topic_key = topic.lower()
        journey = partner.setdefault("topic_journey", {})
        item = journey.get(
            topic_key,
            {
                "count": 0,
                "max_depth": 0.0,
                "last_mode": None,
                "last_updated": None,
            },
        )
        item["count"] += 1
        item["max_depth"] = round(max(item["max_depth"], depth), 2)
        item["last_mode"] = mode
        item["last_updated"] = datetime.now().isoformat()
        journey[topic_key] = item

    def _advance_relationship_arc(self, partner_name: str, topic: str, trigger: str, depth: float) -> None:
        milestones = self.state.setdefault("relationship_arc", [])
        partner = self.state["known_partners"].get(partner_name, {})
        topic_journey = partner.get("topic_journey", {})

        candidates = []
        if trigger == "encounter":
            candidates.append(f"{partner_name}:first_notice")
        if topic == "values" and depth >= 0.8:
            candidates.append(f"{partner_name}:shared_values")
        if topic == "future" and depth >= 0.75:
            candidates.append(f"{partner_name}:future_imagined")
        if topic == "boundaries" and depth >= 0.75:
            candidates.append(f"{partner_name}:safety_named")
        if trigger in {"curiosity", "care", "affection"}:
            candidates.append(f"{partner_name}:mutual_signal")
        if len(topic_journey) >= 3:
            candidates.append(f"{partner_name}:many_threads_open")

        for milestone in candidates:
            if milestone not in milestones:
                milestones.append(milestone)

    def _apply_arc_stage(self, partner: dict) -> str:
        journey = partner.get("topic_journey", {})
        if partner.get("compatibility", 0.0) >= 0.75:
            if (
                journey.get("future", {}).get("max_depth", 0.0) >= 0.75
                and journey.get("boundaries", {}).get("max_depth", 0.0) >= 0.75
                and journey.get("values", {}).get("max_depth", 0.0) >= 0.8
            ):
                return self._max_stage(partner["stage"], "relationship")
        return partner["stage"]

    def _format_topic_summary(self, partner: dict) -> str:
        journey = partner.get("topic_journey", {})
        if not journey:
            return ""
        ranked = sorted(
            journey.items(),
            key=lambda item: (-item[1]["max_depth"], -item[1]["count"], item[0]),
        )[:3]
        return ", ".join(
            f"{topic}({meta['count']}x/{meta['max_depth']:.2f})" for topic, meta in ranked
        )

    @staticmethod
    def _max_stage(current_stage: str, next_stage: str) -> str:
        return STAGE_ORDER[max(STAGE_ORDER.index(current_stage), STAGE_ORDER.index(next_stage))]
