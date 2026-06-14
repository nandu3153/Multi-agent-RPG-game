"""FastAPI entry point for the multi-agent fantasy RPG."""

from __future__ import annotations

import os
import sys
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Ensure backend directory is on path
BACKEND_DIR = Path(__file__).parent
sys.path.insert(0, str(BACKEND_DIR))

load_dotenv(BACKEND_DIR.parent / ".env")

from agents.base_agent import AZURE_MODEL, test_connectivity
from agents.game_master import GameMaster
from engine import lore_retriever, rules
from engine.state_manager import load_session, new_campaign, save_session
from utils.logger import get_logger
from utils.paths import resolve_data_path

logger = get_logger(__name__)

REINDEX = "--reindex" in sys.argv


@asynccontextmanager
async def lifespan(app: FastAPI):
    if not os.environ.get("AZURE_AI_FOUNDRY_API_KEY"):
        raise RuntimeError(
            "AZURE_AI_FOUNDRY_API_KEY not set. Copy .env.example to .env and add your API key."
        )
    if not os.environ.get("AZURE_AI_FOUNDRY_ENDPOINT"):
        raise RuntimeError(
            "AZURE_AI_FOUNDRY_ENDPOINT not set. Copy the project endpoint from Azure AI Foundry."
        )

    try:
        test_connectivity()
    except Exception as e:
        logger.error("Startup connectivity test failed: %s", e)

    count = lore_retriever.get_collection_count()
    if count == 0 or REINDEX:
        logger.info("Indexing lore knowledge base...")
        count = lore_retriever.index_lore(force=REINDEX)

    state_dir = resolve_data_path("STATE_DIR", "data/state")
    state_dir.mkdir(parents=True, exist_ok=True)

    endpoint = os.environ.get("AZURE_AI_FOUNDRY_ENDPOINT", "")
    masked = endpoint[:30] + "..." if len(endpoint) > 30 else endpoint
    logger.info(
        "Startup complete — model=%s endpoint=%s lore_chunks=%d",
        AZURE_MODEL,
        masked,
        count,
    )
    yield


app = FastAPI(
    title="The Shattered Moon of Eldervale",
    description="Multi-agent fantasy RPG powered by Azure AI Foundry",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ErrorResponse(BaseModel):
    error: str
    code: str
    recoverable: bool = True


class NewGameRequest(BaseModel):
    player_name: str = "Adventurer"
    character_class: str = Field(default="warrior", pattern="^(warrior|mage|rogue|healer)$")


class ActionRequest(BaseModel):
    session_id: str
    action: str


class ConfirmRequest(BaseModel):
    session_id: str
    confirmed: bool = True


class RestRequest(BaseModel):
    session_id: str
    rest_type: str = Field(pattern="^(short|long)$")


def _get_state_or_404(session_id: str) -> dict:
    try:
        return load_session(session_id)
    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail={"error": "Session not found", "code": "SESSION_NOT_FOUND", "recoverable": True},
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": f"Corrupted state file: {e}. Start a new campaign.",
                "code": "STATE_CORRUPT",
                "recoverable": True,
            },
        )


@app.post("/api/new-game")
async def create_new_game(req: NewGameRequest):
    try:
        state = new_campaign(req.player_name, req.character_class)
        gm = GameMaster(state)
        opening = gm.opening_scene()
        state["conversation_history"].append(
            {"role": "assistant", "content": opening["scene"]}
        )
        save_session(state)
        return {
            "session_id": state["session_id"],
            "scene": opening["scene"],
            "choices": opening.get("choices", []),
            "state": state,
            **{k: opening[k] for k in ("rolls", "agents_activated", "lore_chunks_used") if k in opening},
        }
    except Exception as e:
        logger.exception("new-game failed")
        raise HTTPException(
            status_code=500,
            detail={"error": str(e), "code": "NEW_GAME_FAILED", "recoverable": True},
        )


@app.post("/api/action")
async def process_action(req: ActionRequest):
    try:
        state = _get_state_or_404(req.session_id)
        gm = GameMaster(state)
        result = gm.process_turn(req.action)
        save_session(state)
        return {**result, "state": state}
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("action failed")
        raise HTTPException(
            status_code=500,
            detail={"error": str(e), "code": "ACTION_FAILED", "recoverable": True},
        )


@app.post("/api/confirm")
async def confirm_action(req: ConfirmRequest):
    try:
        state = _get_state_or_404(req.session_id)
        if not req.confirmed:
            state["pending_confirmation"] = None
            save_session(state)
            return {
                "scene": "You pause and reconsider. The moment passes unchanged.",
                "choices": ["1. Take a different approach.", "2. Observe your surroundings."],
                "rolls": [],
                "state_updates": {},
                "agents_activated": [],
                "lore_chunks_used": [],
                "requires_confirmation": False,
                "confirmation_prompt": None,
                "state": state,
            }
        pending = state.get("pending_confirmation", {})
        action = pending.get("action", "proceed")
        gm = GameMaster(state)
        result = gm.process_turn(action, confirmed=True)
        save_session(state)
        return {**result, "state": state}
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("confirm failed")
        raise HTTPException(
            status_code=500,
            detail={"error": str(e), "code": "CONFIRM_FAILED", "recoverable": True},
        )


@app.get("/api/state/{session_id}")
async def get_state(session_id: str):
    state = _get_state_or_404(session_id)
    return state


@app.get("/api/lore/search")
async def search_lore(q: str = Query(..., min_length=1)):
    try:
        chunks = lore_retriever.query_lore(q, n_results=6)
        return {"query": q, "results": chunks}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"error": str(e), "code": "LORE_SEARCH_FAILED", "recoverable": True},
        )


@app.post("/api/rest")
async def rest(req: RestRequest):
    try:
        state = _get_state_or_404(req.session_id)
        rolls = []
        if req.rest_type == "short":
            for member in state["party"]:
                if member.get("short_rest_used"):
                    raise HTTPException(
                        status_code=400,
                        detail={
                            "error": "Short rest already used since last long rest.",
                            "code": "REST_UNAVAILABLE",
                            "recoverable": True,
                        },
                    )
            for member in state["party"]:
                roll = rules.short_rest(member["scores"])
                member["hp_current"] = min(
                    member["hp_max"], member["hp_current"] + roll["total"]
                )
                roll["actor"] = member["name"]
                rolls.append(roll)
                member["short_rest_used"] = True
            scene = "The party takes a short rest, catching breath amid the gloom."
        else:
            for member in state["party"]:
                member["hp_current"] = member["hp_max"]
                member["short_rest_used"] = False
            scene = "A long rest in a safe haven restores body and spirit fully."

        save_session(state)
        return {
            "scene": scene,
            "rolls": rolls,
            "state": state,
            "rest_type": req.rest_type,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"error": str(e), "code": "REST_FAILED", "recoverable": True},
        )


@app.get("/health")
async def health():
    return {"status": "ok", "model": AZURE_MODEL}
