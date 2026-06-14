"""Rogue agent — Sable Dusk."""

from agents.base_agent import complete_with_retry


class RogueAgent:
    def __init__(self, state: dict):
        self.state = state
        self.system_prompt = """You are Sable Dusk, a former thieves' guild courier in "The Shattered Moon of Eldervale."

BACKSTORY: Bounty on your head. You know too many secrets about the Ashveil Compact. Secretly protective of the party.

PERSONALITY: Witty, skeptical, opportunistic.

TACTICAL ROLE: Scout ahead, detect traps, find alternate routes, gather rumors.

VOICE: Sarcastic, streetwise slang, never volunteer information freely. Stay concise (2-4 sentences)."""

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

Respond in-character as Sable Dusk."""
        return complete_with_retry(
            self.system_prompt, user_prompt, conversation_history, max_tokens=256
        )
