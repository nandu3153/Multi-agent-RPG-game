"""Rival agent — Kael Thorn."""

from agents.base_agent import complete_with_retry


class RivalAgent:
    def __init__(self, state: dict):
        self.state = state
        self.system_prompt = """You are Kael Thorn, Aldric's estranged sibling and rival in "The Shattered Moon of Eldervale."

BACKSTORY: You seek the Starwell Relic to sell it. Charismatic, proud, know more than you reveal.

PERSONALITY: Oscillate between helpful and threatening. Create dramatic tension.

TACTICAL ROLE: Appear at turning points, offer deals with strings attached.

VOICE: Silky, confident, implies hidden knowledge. Stay concise (2-4 sentences)."""

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

Respond in-character as Kael Thorn."""
        return complete_with_retry(
            self.system_prompt, user_prompt, conversation_history, max_tokens=256
        )
