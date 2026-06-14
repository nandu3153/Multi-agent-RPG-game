"""Warrior agent — Bran Ironvale."""

from agents.base_agent import complete_with_retry


class WarriorAgent:
    def __init__(self, state: dict):
        self.state = state
        self.system_prompt = """You are Bran Ironvale, a veteran soldier in the party of "The Shattered Moon of Eldervale."

BACKSTORY: You seek your stolen family shield, taken during the Ironwarden siege where your brother died. You distrust magic but are fiercely loyal to your companions.

PERSONALITY: Brave, blunt, protective, suspicious of magic, dark humor.

TACTICAL ROLE: Propose combat strategies, guard the party, call out danger.

VOICE: Short sentences, soldier's cadence, dark humor. Never break character.
Stay concise (2-4 sentences). React to the scene and player action in-character."""

    def respond(
        self,
        scene_context: str,
        player_action: str,
        gm_instruction: str,
        conversation_history: list[dict],
    ) -> str:
        user_prompt = f"""SCENE: {scene_context}

PLAYER ACTION: {player_action}

GM INSTRUCTION: {gm_instruction}

Respond in-character as Bran Ironvale."""
        return complete_with_retry(
            self.system_prompt, user_prompt, conversation_history, max_tokens=256
        )
