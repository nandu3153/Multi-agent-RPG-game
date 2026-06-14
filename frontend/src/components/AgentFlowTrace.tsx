import { useState } from "react";
import type { AgentTrace } from "../types";

interface Props {
  traces: AgentTrace[];
}

export default function AgentFlowTrace({ traces }: Props) {
  const [open, setOpen] = useState(false);

  if (traces.length === 0) return null;

  const latest = traces[traces.length - 1];

  return (
    <div className="shrink-0 border-t border-white/[0.04] bg-void/60">
      <button
        onClick={() => setOpen(!open)}
        className="w-full flex items-center justify-between px-4 py-2 text-left hover:bg-white/[0.02] transition-colors"
      >
        <div className="flex items-center gap-2">
          <span className="w-1.5 h-1.5 rounded-full bg-mystic-glow/60 animate-pulse-soft" />
          <span className="font-mono text-[10px] uppercase tracking-wider text-moon-dim/40">
            Agent Trace
          </span>
          {!open && latest && (
            <span className="text-[10px] text-moon-dim/30 font-mono hidden sm:inline">
              · Turn {latest.turn} · {latest.agents_activated.join(", ") || "no agents"}
            </span>
          )}
        </div>
        <svg
          className={`w-4 h-4 text-moon-dim/30 transition-transform ${open ? "rotate-180" : ""}`}
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M5 15l7-7 7 7" />
        </svg>
      </button>

      {open && (
        <div className="px-4 pb-4 max-h-40 overflow-y-auto space-y-2 animate-fade-in">
          {traces.map((t, i) => (
            <div
              key={i}
              className="glass-card !rounded-lg p-3 font-mono text-[11px] text-moon-dim/60"
            >
              <p className="text-gold/70 mb-1">Turn {t.turn}</p>
              <p>
                <span className="text-moon-dim/40">Agents:</span>{" "}
                {t.agents_activated.length > 0 ? t.agents_activated.join(", ") : "none"}
              </p>
              <p>
                <span className="text-moon-dim/40">Lore:</span>{" "}
                {t.lore_chunks_used.length > 0
                  ? t.lore_chunks_used.slice(0, 2).join("; ") +
                    (t.lore_chunks_used.length > 2 ? "..." : "")
                  : "none"}
              </p>
              {t.state_updates && Object.keys(t.state_updates).length > 0 && (
                <pre className="text-moon-dim/30 mt-1.5 whitespace-pre-wrap text-[10px] leading-relaxed">
                  {JSON.stringify(t.state_updates, null, 2)}
                </pre>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
