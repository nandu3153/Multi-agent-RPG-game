"""Campaign state load/save and initialization."""

from __future__ import annotations

import json
import os
import uuid
from pathlib import Path
from typing import Any, Dict, List

from utils.logger import get_logger
from utils.paths import resolve_data_path

logger = get_logger(__name__)

DEFAULT_STATE_PATH = str(resolve_data_path("STATE_DIR", "data/state"))

PARTY_TEMPLATES = {
    "warrior": {
        "agent": "warrior",
        "name": "Bran Ironvale",
        "hp_current": 26,
        "hp_max": 26,
        "ac": 17,
        "scores": {"STR": 18, "DEX": 12, "INT": 8, "WIS": 10, "CON": 16, "CHA": 10},
        "inventory": ["longsword", "shield", "torch"],
        "conditions": [],
        "short_rest_used": False,
    },
    "mage": {
        "agent": "mage",
        "name": "Lyra Vey",
        "hp_current": 18,
        "hp_max": 18,
        "ac": 12,
        "scores": {"STR": 8, "DEX": 14, "INT": 18, "WIS": 12, "CON": 10, "CHA": 14},
        "inventory": ["staff", "torch"],
        "conditions": [],
        "short_rest_used": False,
    },
    "rogue": {
        "agent": "rogue",
        "name": "Sable Dusk",
        "hp_current": 20,
        "hp_max": 20,
        "ac": 15,
        "scores": {"STR": 10, "DEX": 18, "INT": 12, "WIS": 14, "CON": 12, "CHA": 14},
        "inventory": ["dagger", "rope", "ashveil_smoke_bomb"],
        "conditions": [],
        "short_rest_used": False,
    },
    "healer": {
        "agent": "healer",
        "name": "Aldric Thorn",
        "hp_current": 22,
        "hp_max": 22,
        "ac": 14,
        "scores": {"STR": 10, "DEX": 10, "INT": 14, "WIS": 18, "CON": 14, "CHA": 16},
        "inventory": ["mace", "healing_kit", "silver_root_tonic"],
        "conditions": [],
        "short_rest_used": False,
    },
}

RIVAL_TEMPLATE = {
    "agent": "rival",
    "name": "Kael Thorn",
    "hp_current": 20,
    "hp_max": 20,
    "ac": 14,
    "scores": {"STR": 12, "DEX": 14, "INT": 14, "WIS": 10, "CON": 12, "CHA": 18},
    "inventory": ["rapier", "eye_sigil_amulet"],
    "conditions": [],
    "short_rest_used": False,
}


def new_campaign(player_name: str = "Adventurer", character_class: str = "warrior") -> dict:
    """Create a fresh campaign state."""
    party = []
    for key, template in PARTY_TEMPLATES.items():
        member = dict(template)
        party.append(member)

    # Rival travels separately but tracked in state
    return {
        "campaign": "The Shattered Moon of Eldervale",
        "session_id": str(uuid.uuid4()),
        "player_name": player_name,
        "player_class": character_class,
        "location": "The Moonlit Gate",
        "active_quest": "Recover the Starwell Relic",
        "turn_number": 0,
        "party": party,
        "rival": dict(RIVAL_TEMPLATE),
        "world_flags": {"moonlit_gate_sealed": True},
        "quest_log": [
            {
                "id": "main_starwell",
                "title": "Recover the Starwell Relic",
                "status": "active",
                "description": "Find the relic hidden in the Starwell Cavern before the Ashveil Compact claims it.",
            },
            {
                "id": "side_silver_root",
                "title": "Heal the Wounded Pilgrim",
                "status": "available",
                "description": "A pilgrim near the Silver Root Sanctum needs aid.",
            },
            {
                "id": "side_ironwarden",
                "title": "Recover the Ironvale Shield",
                "status": "available",
                "description": "Bran's family shield was stolen during the Ironwarden siege.",
            },
        ],
        "conversation_history": [],
        "rival_trust_level": "uncertain",
        "faction_reputation": {
            "Order of the Silver Root": 0,
            "Ashveil Compact": 0,
            "Ironwarden Legion": 0,
        },
        "pending_confirmation": None,
    }


def _state_path_for_session(session_id: str, base_dir: str | None = None) -> Path:
    directory = Path(base_dir or DEFAULT_STATE_PATH)
    directory.mkdir(parents=True, exist_ok=True)
    return directory / f"{session_id}.json"


def load_state(path: str) -> dict:
    """Load campaign state from a JSON file."""
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f"State file not found: {path}")
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_state(state: dict, path: str) -> None:
    """Persist campaign state to a JSON file."""
    file_path = Path(path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)


def load_session(session_id: str, base_dir: str | None = None) -> dict:
    return load_state(str(_state_path_for_session(session_id, base_dir)))


def save_session(state: dict, base_dir: str | None = None) -> None:
    save_state(state, str(_state_path_for_session(state["session_id"], base_dir)))


def _coerce_quest_update(raw: Any) -> Dict[str, Any] | None:
    """Normalize GM quest_updates entries (dict, string, or id:status shorthand)."""
    if isinstance(raw, dict):
        if raw.get("id") or raw.get("title"):
            return raw
        return None

    if isinstance(raw, str):
        text = raw.strip()
        if not text:
            return None
        if ":" in text:
            label, _, rest = text.partition(":")
            label, rest = label.strip(), rest.strip()
            update: Dict[str, Any] = {"_match_label": label}
            if rest:
                update["status"] = rest
            return update
        return {"_match_label": text}

    return None


def _quest_update_matches(existing: dict, update: dict) -> bool:
    label = update.get("_match_label")
    if label:
        return existing.get("id") == label or existing.get("title") == label
    return (
        (update.get("id") and existing.get("id") == update.get("id"))
        or (update.get("title") and existing.get("title") == update.get("title"))
    )


def _quest_fields_to_apply(update: dict) -> dict:
    return {k: v for k, v in update.items() if k != "_match_label" and v is not None}


def _normalize_quest_updates(raw: Any) -> List[dict]:
    if raw is None:
        return []
    if isinstance(raw, dict):
        items = [raw]
    elif isinstance(raw, list):
        items = raw
    else:
        logger.warning("Ignoring quest_updates with unexpected type: %s", type(raw).__name__)
        return []

    normalized: List[dict] = []
    for item in items:
        coerced = _coerce_quest_update(item)
        if coerced:
            normalized.append(coerced)
        else:
            logger.warning("Skipping invalid quest update entry: %r", item)
    return normalized


def apply_state_updates(state: dict, updates: Dict[str, Any]) -> dict:
    """Apply GM state_updates to campaign state."""
    if "location" in updates and updates["location"]:
        state["location"] = updates["location"]

    if "world_flags" in updates:
        state["world_flags"].update(updates["world_flags"])

    if "party_hp_changes" in updates:
        for agent, change in updates["party_hp_changes"].items():
            for member in state["party"]:
                if member["agent"] == agent:
                    member["hp_current"] = max(
                        0, min(member["hp_max"], member["hp_current"] + change)
                    )

    if "inventory_changes" in updates:
        for agent, changes in updates["inventory_changes"].items():
            for member in state["party"]:
                if member["agent"] == agent:
                    for item in changes.get("add", []):
                        if item not in member["inventory"]:
                            member["inventory"].append(item)
                    for item in changes.get("remove", []):
                        if item in member["inventory"]:
                            member["inventory"].remove(item)

    if "quest_updates" in updates:
        for qu in _normalize_quest_updates(updates["quest_updates"]):
            matched = False
            for existing in state["quest_log"]:
                if _quest_update_matches(existing, qu):
                    existing.update(_quest_fields_to_apply(qu))
                    matched = True
            if not matched:
                logger.warning("Quest update did not match any quest in log: %r", qu)

    if "rival_trust_level" in updates:
        state["rival_trust_level"] = updates["rival_trust_level"]

    if "faction_reputation" in updates:
        for faction, delta in updates["faction_reputation"].items():
            state["faction_reputation"][faction] = (
                state["faction_reputation"].get(faction, 0) + delta
            )

    return state
