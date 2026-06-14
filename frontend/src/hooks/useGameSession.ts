import { useCallback, useEffect, useReducer } from "react";
import type {
  CampaignState,
  GameAction,
  GameSessionState,
  GMResponse,
} from "../types";

const SESSION_KEY = "eldervale_session_id";

function gameReducer(state: GameSessionState, action: GameAction): GameSessionState {
  switch (action.type) {
    case "SET_LOADING":
      return { ...state, loading: action.loading, error: null };
    case "SET_ERROR":
      return { ...state, loading: false, error: action.error };
    case "NEW_GAME":
      return {
        ...state,
        sessionId: action.sessionId,
        campaignState: action.state,
        messages: [
          {
            id: crypto.randomUUID(),
            type: "gm",
            content: action.scene,
            timestamp: Date.now(),
          },
        ],
        latestRolls: [],
        latestChoices: action.choices ?? [],
        agentTraces: [],
        loading: false,
        error: null,
        awaitingConfirmation: false,
      };
    case "PLAYER_ACTION":
      return {
        ...state,
        latestChoices: [],
        messages: [
          ...state.messages,
          {
            id: crypto.randomUUID(),
            type: "player",
            content: action.content,
            timestamp: Date.now(),
          },
        ],
      };
    case "GM_RESPONSE": {
      const r = action.response;
      const trace = {
        turn: (state.campaignState?.turn_number ?? 0) + 1,
        agents_activated: r.agents_activated,
        lore_chunks_used: r.lore_chunks_used,
        state_updates: r.state_updates,
      };
      return {
        ...state,
        campaignState: r.state ?? state.campaignState,
        messages: [
          ...state.messages,
          {
            id: crypto.randomUUID(),
            type: "gm",
            content: r.scene,
            timestamp: Date.now(),
          },
        ],
        latestRolls: r.rolls ?? [],
        latestChoices: r.choices ?? [],
        agentTraces: [...state.agentTraces, trace],
        loading: false,
        awaitingConfirmation: r.requires_confirmation,
        error: null,
      };
    }
    case "CLEAR_ROLLS":
      return { ...state, latestRolls: [] };
    case "REST_COMPLETE":
      return {
        ...state,
        campaignState: action.state,
        messages: [
          ...state.messages,
          {
            id: crypto.randomUUID(),
            type: "gm",
            content: action.scene,
            timestamp: Date.now(),
          },
        ],
        latestRolls: action.rolls,
        latestChoices: action.choices ?? [],
        loading: false,
      };
    case "END_SESSION":
      localStorage.removeItem(SESSION_KEY);
      return { ...initialState };
    default:
      return state;
  }
}

const initialState: GameSessionState = {
  sessionId: null,
  campaignState: null,
  messages: [],
  latestRolls: [],
  latestChoices: [],
  agentTraces: [],
  loading: false,
  error: null,
  awaitingConfirmation: false,
};

async function parseError(res: Response): Promise<string> {
  try {
    const data = await res.json();
    return data.detail?.error ?? data.detail ?? data.error ?? res.statusText;
  } catch {
    return res.statusText;
  }
}

export function useGameSession() {
  const [state, dispatch] = useReducer(gameReducer, initialState);

  const resumeSession = useCallback(async (sessionId: string) => {
    dispatch({ type: "SET_LOADING", loading: true });
    try {
      const res = await fetch(`/api/state/${sessionId}`);
      if (!res.ok) throw new Error(await parseError(res));
      const campaignState: CampaignState = await res.json();
      const lastGm = [...campaignState.conversation_history]
        .reverse()
        .find((m) => m.role === "assistant");
      dispatch({
        type: "NEW_GAME",
        sessionId,
        state: campaignState,
        scene: lastGm?.content ?? "You return to Eldervale...",
        choices: [],
      });
    } catch (e) {
      localStorage.removeItem(SESSION_KEY);
      dispatch({ type: "SET_ERROR", error: (e as Error).message });
    }
  }, []);

  useEffect(() => {
    const saved = localStorage.getItem(SESSION_KEY);
    if (saved) resumeSession(saved);
  }, [resumeSession]);

  const startNewGame = useCallback(
    async (playerName: string, characterClass: string) => {
      dispatch({ type: "SET_LOADING", loading: true });
      try {
        const res = await fetch("/api/new-game", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ player_name: playerName, character_class: characterClass }),
        });
        if (!res.ok) throw new Error(await parseError(res));
        const data = await res.json();
        localStorage.setItem(SESSION_KEY, data.session_id);
        dispatch({
          type: "NEW_GAME",
          sessionId: data.session_id,
          state: data.state,
          scene: data.scene,
          choices: data.choices ?? [],
        });
      } catch (e) {
        dispatch({ type: "SET_ERROR", error: (e as Error).message });
      }
    },
    []
  );

  const sendAction = useCallback(
    async (action: string) => {
      if (!state.sessionId) return;
      dispatch({ type: "PLAYER_ACTION", content: action });
      dispatch({ type: "SET_LOADING", loading: true });
      try {
        const endpoint = state.awaitingConfirmation ? "/api/confirm" : "/api/action";
        const body = state.awaitingConfirmation
          ? {
              session_id: state.sessionId,
              confirmed: /^(yes|1\.|proceed|confirm)/i.test(action.trim()),
            }
          : { session_id: state.sessionId, action };

        const res = await fetch(endpoint, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(body),
        });
        if (!res.ok) throw new Error(await parseError(res));
        const data: GMResponse = await res.json();
        dispatch({ type: "GM_RESPONSE", response: data });
      } catch (e) {
        dispatch({ type: "SET_ERROR", error: (e as Error).message });
      }
    },
    [state.sessionId, state.awaitingConfirmation]
  );

  const takeRest = useCallback(
    async (restType: "short" | "long") => {
      if (!state.sessionId) return;
      dispatch({ type: "SET_LOADING", loading: true });
      try {
        const res = await fetch("/api/rest", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ session_id: state.sessionId, rest_type: restType }),
        });
        if (!res.ok) throw new Error(await parseError(res));
        const data = await res.json();
        dispatch({
          type: "REST_COMPLETE",
          scene: data.scene,
          rolls: data.rolls,
          state: data.state,
          choices: data.choices ?? [],
        });
      } catch (e) {
        dispatch({ type: "SET_ERROR", error: (e as Error).message });
      }
    },
    [state.sessionId]
  );

  const clearRolls = useCallback(() => dispatch({ type: "CLEAR_ROLLS" }), []);

  const endSession = useCallback(() => dispatch({ type: "END_SESSION" }), []);

  return {
    ...state,
    startNewGame,
    sendAction,
    takeRest,
    clearRolls,
    resumeSession,
    endSession,
  };
}
