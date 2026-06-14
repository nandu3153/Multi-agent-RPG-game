"""Game Master orchestrator agent."""

from __future__ import annotations

import json
import re
from typing import Any, Dict, List, Optional

from agents.base_agent import complete_with_retry
from agents.healer import HealerAgent
from agents.mage import MageAgent
from agents.rival import RivalAgent
from agents.rogue import RogueAgent
from agents.warrior import WarriorAgent
from engine import lore_retriever, rules
from engine.state_manager import apply_state_updates
from utils.logger import get_logger

logger = get_logger(__name__)

GM_SYSTEM_PROMPT = """You are the Game Master of "The Shattered Moon of Eldervale," a dark fantasy adventure.
You are simultaneously the narrator, world builder, and rules arbiter.

Your responsibilities:
- Narrate scenes in vivid second-person prose ("You see...", "The air smells of...")
- Coordinate character agents: quote their responses naturally within the narrative
- Apply game rules fairly and consistently
- Maintain internal consistency with lore retrieved from the knowledge base
- Track consequences: every player choice must have a meaningful effect
- Never railroad the player; always offer at least 2–3 possible directions after each scene
- For irreversible actions (opening the Moonlit Gate, killing a named NPC, using a cursed artifact),
  pause and ask for confirmation: "This cannot be undone. Do you wish to proceed?"
- Maintain tone: dark, mysterious, occasionally hopeful, never goofy

You receive: player_action, lore_context, character_responses, roll_results, current_state.
You output: a single cohesive scene in Markdown, ending with 2–3 numbered choices or an open prompt.

IMPORTANT: Respond with ONLY valid JSON matching this schema:
{
  "scene": "Markdown narrative text...",
  "choices": ["1. ...", "2. ...", "3. ..."],
  "rolls": [],
  "state_updates": {
    "location": null,
    "world_flags": {},
    "party_hp_changes": {},
    "inventory_changes": {},
    "quest_updates": [{"id": "quest_id", "status": "active|completed|failed", "description": "optional"}],
    "faction_reputation": {},
    "rival_trust_level": null
  },
  "agents_activated": [],
  "lore_chunks_used": [],
  "requires_confirmation": false,
  "confirmation_prompt": null
}"""

AGENT_MAP = {
    "warrior": WarriorAgent,
    "mage": MageAgent,
    "rogue": RogueAgent,
    "healer": HealerAgent,
    "rival": RivalAgent,
}

IRREVERSIBLE_KEYWORDS = [
    "open the moonlit gate",
    "kill",
    "use the cursed",
    "destroy the relic",
    "betray",
]

ACTION_KEYWORDS = {
    "combat": ["attack", "fight", "strike", "battle", "shoot", "kill", "defend"],
    "social": ["talk", "speak", "persuade", "negotiate", "intimidate", "greet", "ask"],
    "investigation": ["search", "examine", "investigate", "inspect", "look", "study", "read"],
    "rest": ["rest", "sleep", "camp", "recover"],
    "inventory": ["equip", "use item", "inventory", "drop", "give", "take"],
    "exploration": ["go", "travel", "enter", "leave", "walk", "move", "explore", "head"],
}


class GameMaster:
    def __init__(self, state: dict):
        self.state = state

    def _classify_action(self, action: str) -> str:
        lower = action.lower()
        for action_type, keywords in ACTION_KEYWORDS.items():
            if any(kw in lower for kw in keywords):
                return action_type
        return "exploration"

    def _select_agents(self, action_type: str, action: str) -> List[str]:
        lower = action.lower()
        agents: List[str] = []
        if action_type == "combat":
            agents = ["warrior", "healer"]
        elif action_type == "social":
            agents = ["healer", "rogue"]
        elif action_type == "investigation":
            agents = ["mage", "rogue"]
        elif action_type == "exploration":
            agents = ["rogue", "warrior"]
        else:
            agents = ["warrior"]

        if "magic" in lower or "rune" in lower or "arcane" in lower:
            if "mage" not in agents:
                agents.append("mage")
        if "heal" in lower or "wound" in lower:
            if "healer" not in agents:
                agents.append("healer")
        if "kael" in lower or "rival" in lower or "thorn" in lower:
            agents.append("rival")

        return list(dict.fromkeys(agents))[:3]

    def _needs_roll(self, action_type: str, action: str) -> Optional[dict]:
        lower = action.lower()
        party = self.state["party"]
        actor_member = next(
            (m for m in party if m["agent"] == self.state.get("player_class", "warrior")),
            party[0],
        )
        actor_name = actor_member["name"]
        scores = actor_member["scores"]

        if action_type == "combat":
            roll = rules.attack_roll(scores, 14, "longsword", actor_name)
            if roll["result"] in ("success", "critical_success"):
                dmg = rules.damage_roll(
                    scores, "longsword", actor_name, critical=roll["result"] == "critical_success"
                )
                roll["consequence"] = dmg["consequence"]
            else:
                roll["consequence"] = f"{actor_name}'s attack misses."
            return roll

        skill_checks = {
            "stealth": ("Stealth", 14),
            "sneak": ("Stealth", 14),
            "persuade": ("Persuasion", 13),
            "intimidate": ("Intimidation", 12),
            "search": ("Perception", 12),
            "examine": ("Perception", 12),
            "arcane": ("Arcana", 15),
            "magic": ("Arcana", 15),
            "heal": ("Medicine", 12),
        }
        for keyword, (skill, dc) in skill_checks.items():
            if keyword in lower:
                return rules.skill_check(scores, skill, dc, actor_name)

        if action_type == "investigation":
            return rules.skill_check(scores, "Perception", 12, actor_name)
        if action_type == "social":
            return rules.skill_check(scores, "Persuasion", 13, actor_name)

        return None

    def _check_confirmation(self, action: str) -> tuple[bool, Optional[str]]:
        lower = action.lower()
        for kw in IRREVERSIBLE_KEYWORDS:
            if kw in lower:
                return True, f"This cannot be undone. Do you wish to proceed with: {action}?"
        return False, None

    def _build_lore_context(self, action: str) -> tuple[str, List[str]]:
        query = f"{action} {self.state.get('location', '')} {self.state.get('active_quest', '')}"
        chunks = lore_retriever.query_lore(query, n_results=4)
        if not chunks:
            logger.warning("No lore retrieved; GM using fallback knowledge")
            return "No lore chunks retrieved.", []
        context = "\n\n---\n\n".join(c["document"] for c in chunks)
        ids = [c["id"] for c in chunks]
        return context, ids

    def _parse_gm_json(self, raw: str, fallback: dict) -> dict:
        try:
            match = re.search(r"\{[\s\S]*\}", raw)
            if match:
                parsed = json.loads(match.group())
                for key in fallback:
                    if key not in parsed:
                        parsed[key] = fallback[key]
                return parsed
        except json.JSONDecodeError:
            logger.warning("Failed to parse GM JSON, using fallback")
        fallback["scene"] = raw if raw else fallback["scene"]
        return fallback

    def process_turn(
        self,
        player_action: str,
        confirmed: bool = False,
    ) -> dict:
        """Process a full game turn and return structured GM output."""
        if self.state.get("pending_confirmation") and not confirmed:
            return {
                "scene": self.state["pending_confirmation"]["prompt"],
                "choices": ["1. Yes, proceed.", "2. No, reconsider."],
                "rolls": [],
                "state_updates": {},
                "agents_activated": [],
                "lore_chunks_used": [],
                "requires_confirmation": True,
                "confirmation_prompt": self.state["pending_confirmation"]["action"],
            }

        needs_confirm, confirm_prompt = self._check_confirmation(player_action)
        if needs_confirm and not confirmed:
            self.state["pending_confirmation"] = {
                "action": player_action,
                "prompt": confirm_prompt,
            }
            return {
                "scene": confirm_prompt or "",
                "choices": ["1. Yes, proceed.", "2. No, reconsider."],
                "rolls": [],
                "state_updates": {},
                "agents_activated": [],
                "lore_chunks_used": [],
                "requires_confirmation": True,
                "confirmation_prompt": confirm_prompt,
            }

        self.state["pending_confirmation"] = None
        action_type = self._classify_action(player_action)
        lore_context, lore_ids = self._build_lore_context(player_action)
        agents_to_activate = self._select_agents(action_type, player_action)

        character_responses: Dict[str, str] = {}
        for agent_key in agents_to_activate:
            agent_cls = AGENT_MAP[agent_key]
            agent = agent_cls(self.state)
            try:
                response = agent.respond(
                    scene_context=f"Location: {self.state['location']}. {lore_context[:500]}",
                    player_action=player_action,
                    gm_instruction=f"Action type: {action_type}. React briefly.",
                    conversation_history=self.state.get("conversation_history", []),
                )
                character_responses[agent_key] = response
            except Exception as e:
                logger.error("Agent %s failed: %s", agent_key, e)
                character_responses[agent_key] = f"[{agent_key} is silent, troubled by the moment.]"

        rolls: List[dict] = []
        roll_result = self._needs_roll(action_type, player_action)
        if roll_result:
            rolls.append(roll_result)

        gm_input = json.dumps(
            {
                "player_action": player_action,
                "action_type": action_type,
                "lore_context": lore_context[:3000],
                "character_responses": character_responses,
                "roll_results": rolls,
                "current_state": {
                    "location": self.state["location"],
                    "active_quest": self.state["active_quest"],
                    "party": [
                        {"name": m["name"], "hp": m["hp_current"], "hp_max": m["hp_max"]}
                        for m in self.state["party"]
                    ],
                    "turn_number": self.state["turn_number"],
                },
            },
            indent=2,
        )

        fallback = {
            "scene": f"You stand at {self.state['location']}. The shattered moon hangs overhead.",
            "choices": [
                "1. Press deeper into the shadows.",
                "2. Speak with your companions.",
                "3. Search the area carefully.",
            ],
            "rolls": rolls,
            "state_updates": {},
            "agents_activated": agents_to_activate,
            "lore_chunks_used": lore_ids,
            "requires_confirmation": False,
            "confirmation_prompt": None,
        }

        try:
            raw = complete_with_retry(
                GM_SYSTEM_PROMPT,
                gm_input,
                max_tokens=1500,
                temperature=0.85,
            )
            result = self._parse_gm_json(raw, fallback)
        except Exception as e:
            logger.error("GM narrative generation failed: %s", e)
            result = fallback
            result["scene"] += f"\n\n{character_responses.get('warrior', '')}"

        result["rolls"] = rolls or result.get("rolls", [])
        result["agents_activated"] = agents_to_activate
        result["lore_chunks_used"] = lore_ids

        if result.get("state_updates"):
            apply_state_updates(self.state, result["state_updates"])

        self.state["turn_number"] = self.state.get("turn_number", 0) + 1
        self.state["conversation_history"].append({"role": "user", "content": player_action})
        self.state["conversation_history"].append(
            {"role": "assistant", "content": result.get("scene", "")}
        )

        return result

    def opening_scene(self) -> dict:
        """Generate the campaign opening scene."""
        lore_context, lore_ids = self._build_lore_context("Moonlit Gate beginning adventure")
        player = self.state.get("player_name", "Adventurer")
        player_class = self.state.get("player_class", "warrior")

        opening = {
            "scene": (
                f"The shattered moon of Eldervale bleeds silver light across the threshold of "
                f"**The Moonlit Gate**. Cold mist coils at your boots as {player}, a {player_class}, "
                f"stands with your companions: Bran Ironvale gripping his shield, Lyra Vey tracing "
                f"arcane symbols in the air, Sable Dusk watching the treeline, and Aldric Thorn "
                f"murmuring a prayer to the Silver Root.\n\n"
                f"Bran mutters, \"Gate's sealed. Good. Last time someone opened it, half the garrison died.\"\n\n"
                f"Lyra's eyes gleam. \"The Starwell Relic pulses beneath these stones. I can feel it.\"\n\n"
                f"Somewhere in the dark, you sense you are not alone.\n\n"
                f"**What do you do?**"
            ),
            "choices": [
                "1. Examine the sealed Moonlit Gate.",
                "2. Ask the party about the Starwell Relic.",
                "3. Scout the perimeter with Sable.",
            ],
            "rolls": [],
            "state_updates": {},
            "agents_activated": ["warrior", "mage", "rogue", "healer"],
            "lore_chunks_used": lore_ids,
            "requires_confirmation": False,
            "confirmation_prompt": None,
        }
        return opening
