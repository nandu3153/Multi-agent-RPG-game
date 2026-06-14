export interface AbilityScores {
  STR: number;
  DEX: number;
  INT: number;
  WIS: number;
  CON: number;
  CHA: number;
}

export interface PartyMember {
  agent: string;
  name: string;
  hp_current: number;
  hp_max: number;
  ac: number;
  scores: AbilityScores;
  inventory: string[];
  conditions: string[];
  short_rest_used: boolean;
}

export interface QuestEntry {
  id: string;
  title: string;
  status: string;
  description: string;
}

export interface CampaignState {
  campaign: string;
  session_id: string;
  player_name: string;
  player_class: string;
  location: string;
  active_quest: string;
  turn_number: number;
  party: PartyMember[];
  rival?: PartyMember;
  world_flags: Record<string, boolean | string>;
  quest_log: QuestEntry[];
  conversation_history: { role: string; content: string }[];
  rival_trust_level: string;
  faction_reputation: Record<string, number>;
  pending_confirmation?: { action: string; prompt: string } | null;
}

export interface RollResult {
  actor: string;
  check: string;
  roll: number;
  modifier: number;
  total: number;
  difficulty: number;
  result: string;
  consequence: string;
}

export interface StateUpdates {
  location?: string;
  world_flags?: Record<string, boolean | string>;
  party_hp_changes?: Record<string, number>;
  inventory_changes?: Record<string, { add?: string[]; remove?: string[] }>;
  quest_updates?: QuestEntry[];
  faction_reputation?: Record<string, number>;
  rival_trust_level?: string;
}

export interface GMResponse {
  scene: string;
  choices?: string[];
  rolls: RollResult[];
  state_updates?: StateUpdates;
  agents_activated: string[];
  lore_chunks_used: string[];
  requires_confirmation: boolean;
  confirmation_prompt?: string | null;
  state?: CampaignState;
}

export interface ChatMessage {
  id: string;
  type: "player" | "gm";
  content: string;
  timestamp: number;
}

export interface AgentTrace {
  turn: number;
  agents_activated: string[];
  lore_chunks_used: string[];
  state_updates?: StateUpdates;
}

export interface GameSessionState {
  sessionId: string | null;
  campaignState: CampaignState | null;
  messages: ChatMessage[];
  latestRolls: RollResult[];
  latestChoices: string[];
  agentTraces: AgentTrace[];
  loading: boolean;
  error: string | null;
  awaitingConfirmation: boolean;
}

export type GameAction =
  | { type: "SET_LOADING"; loading: boolean }
  | { type: "SET_ERROR"; error: string | null }
  | { type: "NEW_GAME"; sessionId: string; state: CampaignState; scene: string; choices?: string[] }
  | { type: "PLAYER_ACTION"; content: string }
  | { type: "GM_RESPONSE"; response: GMResponse }
  | { type: "CLEAR_ROLLS" }
  | { type: "REST_COMPLETE"; scene: string; rolls: RollResult[]; state: CampaignState; choices?: string[] }
  | { type: "END_SESSION" };
