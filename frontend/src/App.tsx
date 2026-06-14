import { useState } from "react";
import AgentFlowTrace from "./components/AgentFlowTrace";
import AtmosphereBackground from "./components/AtmosphereBackground";
import CharacterCreation from "./components/CharacterCreation";
import ChatWindow from "./components/ChatWindow";
import DiceRollDisplay from "./components/DiceRollDisplay";
import GameHeader from "./components/GameHeader";
import PartyPanel from "./components/PartyPanel";
import QuestJournal from "./components/QuestJournal";
import { useGameSession } from "./hooks/useGameSession";

export default function App() {
  const {
    sessionId,
    campaignState,
    messages,
    latestRolls,
    latestChoices,
    agentTraces,
    loading,
    error,
    awaitingConfirmation,
    startNewGame,
    sendAction,
    takeRest,
    clearRolls,
    endSession,
  } = useGameSession();

  const [playerName, setPlayerName] = useState("Adventurer");
  const [characterClass, setCharacterClass] = useState("warrior");
  const [partyOpen, setPartyOpen] = useState(false);
  const [questOpen, setQuestOpen] = useState(false);

  if (!sessionId || !campaignState) {
    return (
      <>
        <AtmosphereBackground />
        <CharacterCreation
          playerName={playerName}
          characterClass={characterClass}
          loading={loading}
          error={error}
          onNameChange={setPlayerName}
          onClassChange={setCharacterClass}
          onStart={() => startNewGame(playerName.trim(), characterClass)}
        />
      </>
    );
  }

  return (
    <div className="h-screen flex flex-col overflow-hidden">
      <AtmosphereBackground />

      <GameHeader
        campaignState={campaignState}
        loading={loading}
        onShortRest={() => takeRest("short")}
        onLongRest={() => takeRest("long")}
        onEndSession={endSession}
        onToggleParty={() => setPartyOpen((v) => !v)}
      />

      {error && (
        <div className="shrink-0 px-4 py-2.5 bg-red-950/50 border-b border-red-800/30 text-red-300 text-sm font-ui flex items-center gap-2 animate-fade-in">
          <span className="text-red-400">⚠</span>
          {error}
        </div>
      )}

      <div className="flex flex-1 min-h-0 relative">
        <PartyPanel
          party={campaignState.party}
          playerClass={campaignState.player_class}
          mobileOpen={partyOpen}
          onClose={() => setPartyOpen(false)}
        />

        <main className="flex-1 flex flex-col min-w-0 relative">
          {/* Mobile quest toggle */}
          <div className="lg:hidden shrink-0 px-4 py-2 border-b border-white/[0.04] flex items-center justify-between">
            <button
              onClick={() => setQuestOpen((v) => !v)}
              className="btn-ghost !text-xs flex items-center gap-2"
            >
              <span>📜</span>
              Quest Journal
              <svg
                className={`w-3 h-3 transition-transform ${questOpen ? "rotate-180" : ""}`}
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
              </svg>
            </button>
            <div className="flex gap-1.5 sm:hidden">
              <button
                onClick={() => takeRest("short")}
                disabled={loading}
                className="btn-ghost !text-xs !px-2"
              >
                ☕
              </button>
              <button
                onClick={() => takeRest("long")}
                disabled={loading}
                className="btn-ghost !text-xs !px-2"
              >
                🏕
              </button>
            </div>
          </div>

          {questOpen && (
            <div className="lg:hidden shrink-0 max-h-[40vh] overflow-hidden border-b border-white/[0.06] animate-fade-in">
              <QuestJournal
                questLog={campaignState.quest_log}
                location={campaignState.location}
                activeQuest={campaignState.active_quest}
              />
            </div>
          )}

          <div className="flex-1 min-h-0">
            <ChatWindow
              messages={messages}
              choices={latestChoices}
              onSend={sendAction}
              loading={loading}
              awaitingConfirmation={awaitingConfirmation}
            />
          </div>

          <AgentFlowTrace traces={agentTraces} />
        </main>

        {/* Desktop quest sidebar */}
        <div className="hidden lg:flex">
          <QuestJournal
            questLog={campaignState.quest_log}
            location={campaignState.location}
            activeQuest={campaignState.active_quest}
          />
        </div>
      </div>

      <DiceRollDisplay rolls={latestRolls} onFade={clearRolls} />
    </div>
  );
}
