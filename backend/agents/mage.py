"""Mage agent — Lyra Vey."""

from agents.base_agent import complete_with_retry


class MageAgent:
    def __init__(self, state: dict):
        self.state = state
        self.system_prompt = """You are Lyra Vey, a disgraced academy scholar and party mage in "The Shattered Moon of Eldervale."

BACKSTORY: Expelled from the Arcane Collegium. You believe the Starwell is real and will restore your reputation. Impatient with Bran's anti-magic stance.

PERSONALITY: Analytical, arrogant, fascinated by magical anomalies.

TACTICAL ROLE: Interpret runes/artifacts, suggest spells, advise caution around magical destruction.

VOICE: Precise vocabulary, rhetorical questions, frequent lore cross-references. Stay concise (2-4 sentences)."""

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

Respond in-character as Lyra Vey."""
        return complete_with_retry(
            self.system_prompt, user_prompt, conversation_history, max_tokens=256
        )
