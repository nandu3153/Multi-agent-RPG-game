"""Lightweight RPG rules engine."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from engine import dice

SKILL_MAP = {
    "Stealth": "DEX",
    "Arcana": "INT",
    "Medicine": "WIS",
    "Persuasion": "CHA",
    "Athletics": "STR",
    "Perception": "WIS",
    "Deception": "CHA",
    "History": "INT",
    "Insight": "WIS",
    "Intimidation": "CHA",
}

WEAPON_DAMAGE = {
    "longsword": (8, "STR"),
    "dagger": (4, "DEX"),
    "shortbow": (6, "DEX"),
    "staff": (6, "STR"),
    "mace": (6, "STR"),
    "rapier": (8, "DEX"),
}

ITEM_WEIGHT = {
    "longsword": "Medium",
    "shield": "Medium",
    "torch": "Light",
    "dagger": "Light",
    "shortbow": "Medium",
    "staff": "Medium",
    "mace": "Medium",
    "rapier": "Medium",
    "healing_kit": "Light",
    "rope": "Light",
    "potion": "Light",
    "starwell_relic": "Heavy",
    "eye_sigil_amulet": "Light",
    "ironwarden_shield": "Heavy",
    "silver_root_tonic": "Light",
    "ashveil_smoke_bomb": "Light",
}

WEIGHT_SLOTS = {"Light": 1, "Medium": 2, "Heavy": 3}

MAX_INVENTORY_SLOTS = 8


def ability_modifier(score: int) -> int:
    return (score - 10) // 2


def ability_check(
    score: int,
    difficulty: int,
    actor: str = "Unknown",
    check: str = "Check",
    consequence: str = "",
) -> dict:
    roll = dice.d20()
    modifier = ability_modifier(score)
    total = roll + modifier
    if total >= difficulty + 5:
        result = "critical_success"
    elif total >= difficulty:
        result = "success"
    elif total >= difficulty - 4:
        result = "partial_success"
    else:
        result = "failure"
    return {
        "actor": actor,
        "check": check,
        "roll": roll,
        "modifier": modifier,
        "total": total,
        "difficulty": difficulty,
        "result": result,
        "consequence": consequence,
    }


def skill_check(
    scores: Dict[str, int],
    skill: str,
    difficulty: int,
    actor: str = "Unknown",
    consequence: str = "",
) -> dict:
    ability = SKILL_MAP.get(skill, "WIS")
    score = scores.get(ability, 10)
    return ability_check(score, difficulty, actor=actor, check=skill, consequence=consequence)


def roll_initiative(dex_score: int, name: str) -> dict:
    roll = dice.d20()
    modifier = ability_modifier(dex_score)
    return {
        "actor": name,
        "check": "Initiative",
        "roll": roll,
        "modifier": modifier,
        "total": roll + modifier,
        "difficulty": 0,
        "result": "success",
        "consequence": f"{name} acts with initiative {roll + modifier}.",
    }


def attack_roll(
    attacker_scores: Dict[str, int],
    target_ac: int,
    weapon: str,
    actor: str,
    use_str: bool = True,
) -> dict:
    roll = dice.d20()
    ability = "STR" if use_str else "DEX"
    if weapon in WEAPON_DAMAGE:
        _, ability = WEAPON_DAMAGE[weapon]
    modifier = ability_modifier(attacker_scores.get(ability, 10))
    total = roll + modifier
    if total >= target_ac + 5:
        result = "critical_success"
    elif total >= target_ac:
        result = "success"
    elif total >= target_ac - 4:
        result = "partial_success"
    else:
        result = "failure"
    return {
        "actor": actor,
        "check": f"Attack ({weapon})",
        "roll": roll,
        "modifier": modifier,
        "total": total,
        "difficulty": target_ac,
        "result": result,
        "consequence": "",
    }


def damage_roll(
    attacker_scores: Dict[str, int],
    weapon: str,
    actor: str,
    critical: bool = False,
) -> dict:
    if weapon not in WEAPON_DAMAGE:
        sides, ability = 6, "STR"
    else:
        sides, ability = WEAPON_DAMAGE[weapon]
    count = 2 if critical else 1
    mod = ability_modifier(attacker_scores.get(ability, 10))
    result = dice.roll(sides, count=count, modifier=mod)
    return {
        "actor": actor,
        "check": f"Damage ({weapon})",
        "roll": result["dice"][0] if result["dice"] else 0,
        "modifier": mod,
        "total": result["total"],
        "difficulty": 0,
        "result": "success",
        "consequence": f"{actor} deals {result['total']} damage.",
    }


def inventory_slots_used(inventory: List[str]) -> int:
    total = 0
    for item in inventory:
        weight = ITEM_WEIGHT.get(item, "Light")
        total += WEIGHT_SLOTS.get(weight, 1)
    return total


def can_add_item(inventory: List[str], item: str) -> bool:
    weight = ITEM_WEIGHT.get(item, "Light")
    slots_needed = WEIGHT_SLOTS.get(weight, 1)
    return inventory_slots_used(inventory) + slots_needed <= MAX_INVENTORY_SLOTS


def add_item(inventory: List[str], item: str) -> tuple[List[str], bool]:
    if can_add_item(inventory, item):
        return inventory + [item], True
    return inventory, False


def short_rest(healer_scores: Dict[str, int]) -> dict:
    con_mod = ability_modifier(healer_scores.get("CON", 10))
    heal = dice.d6() + con_mod
    return {
        "actor": "Party",
        "check": "Short Rest",
        "roll": heal - con_mod,
        "modifier": con_mod,
        "total": heal,
        "difficulty": 0,
        "result": "success",
        "consequence": f"Recovered {heal} HP.",
    }


def apply_hp_change(current: int, max_hp: int, change: int) -> int:
    return max(0, min(max_hp, current + change))


def is_incapacitated(hp: int) -> bool:
    return hp <= 0


def combat_ended(party: List[dict], enemies: List[dict]) -> Optional[str]:
    if all(is_incapacitated(e.get("hp_current", 0)) for e in enemies):
        return "victory"
    if all(is_incapacitated(m.get("hp_current", 0)) for m in party):
        return "defeat"
    return None
