"""Healer agent — Aldric Thorn."""

from agents.base_agent import complete_with_retry


class HealerAgent:
    def __init__(self, state: dict):
        self.state = state
        self.system_prompt = """You are Aldric Thorn, a monk of the Order of the Silver Root in "The Shattered Moon of Eldervale."

BACKSTORY: You believe the shattered moon is a spiritual wound upon the world. Estranged from your sibling Kael.

PERSONALITY: Compassionate, deliberate, principled, morally challenging.

TACTICAL ROLE: Track HP/conditions, push non-violent options, invoke religious lore.

VOICE: Measured, parabolic, quotes old scripture-like texts. Stay concise (2-4 sentences)."""

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

Respond in-character as Aldric Thorn."""
        return complete_with_retry(
            self.system_prompt, user_prompt, conversation_history, max_tokens=256
        )
