import type { CampaignState } from "../types";

interface Props {
  campaignState: CampaignState;
  loading: boolean;
  onShortRest: () => void;
  onLongRest: () => void;
  onEndSession: () => void;
  onToggleParty: () => void;
}

export default function GameHeader({
  campaignState,
  loading,
  onShortRest,
  onLongRest,
  onEndSession,
  onToggleParty,
}: Props) {
  return (
    <header className="glass-panel border-b border-white/[0.06] px-4 md:px-6 py-3 flex items-center justify-between gap-4 shrink-0 z-20">
      <div className="flex items-center gap-3 min-w-0">
        <button
          onClick={onToggleParty}
          className="lg:hidden btn-ghost !px-2.5 !py-2"
          aria-label="Toggle party panel"
        >
          <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z" />
          </svg>
        </button>

        <div className="min-w-0">
          <h1 className="font-display text-sm md:text-base text-gold truncate">
            The Shattered Moon
          </h1>
          <p className="text-xs text-moon-dim font-ui truncate">
            <span className="text-moon">{campaignState.player_name}</span>
            <span className="text-moon-dim/50 mx-1">·</span>
            <span className="capitalize">{campaignState.player_class}</span>
            <span className="text-moon-dim/50 mx-1">·</span>
            Turn {campaignState.turn_number}
          </p>
        </div>
      </div>

      <div className="flex items-center gap-1.5 md:gap-2 shrink-0">
        <div className="hidden sm:flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-void/60 border border-white/[0.06]">
          <span className="text-moon-dim/50 text-xs">📍</span>
          <span className="text-xs font-ui text-moon-dim truncate max-w-[140px] md:max-w-[200px]">
            {campaignState.location}
          </span>
        </div>

        <button
          onClick={onShortRest}
          disabled={loading}
          className="btn-ghost !text-xs hidden sm:inline-flex"
          title="Short Rest"
        >
          ☕ Short Rest
        </button>
        <button
          onClick={onLongRest}
          disabled={loading}
          className="btn-ghost !text-xs hidden sm:inline-flex"
          title="Long Rest"
        >
          🏕 Long Rest
        </button>

        <button
          onClick={onEndSession}
          className="btn-ghost !text-xs !text-moon-dim/60 hover:!text-red-400"
          title="End session"
        >
          Exit
        </button>
      </div>
    </header>
  );
}
