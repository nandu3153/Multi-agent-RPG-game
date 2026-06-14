import { useEffect } from "react";
import type { RollResult } from "../types";

interface Props {
  rolls: RollResult[];
  onFade: () => void;
}

const RESULT_CONFIG: Record<string, { bg: string; label: string; icon: string }> = {
  critical_success: {
    bg: "from-gold/30 to-gold-dim/10 border-gold/40",
    label: "Critical Success",
    icon: "★",
  },
  success: {
    bg: "from-emerald-900/40 to-emerald-950/20 border-emerald-600/30",
    label: "Success",
    icon: "✓",
  },
  partial_success: {
    bg: "from-amber-900/30 to-amber-950/15 border-amber-600/30",
    label: "Partial",
    icon: "~",
  },
  failure: {
    bg: "from-red-900/40 to-red-950/20 border-red-700/30",
    label: "Failure",
    icon: "✗",
  },
};

export default function DiceRollDisplay({ rolls, onFade }: Props) {
  useEffect(() => {
    if (rolls.length === 0) return;
    const timer = setTimeout(onFade, 5000);
    return () => clearTimeout(timer);
  }, [rolls, onFade]);

  if (rolls.length === 0) return null;

  return (
    <div className="fixed bottom-28 md:bottom-8 left-4 right-4 md:left-auto md:right-6 z-50 flex flex-col gap-3 md:items-end pointer-events-none">
      {rolls.map((roll, i) => {
        const config = RESULT_CONFIG[roll.result] ?? {
          bg: "from-void-100 to-void border-white/10",
          label: roll.result.replace(/_/g, " "),
          icon: "?",
        };

        return (
          <div
            key={`${roll.actor}-${roll.check}-${i}`}
            className={`pointer-events-auto w-full md:w-80 glass-panel rounded-2xl p-4 animate-dice-pop bg-gradient-to-br ${config.bg}`}
            style={{ animationDelay: `${i * 100}ms` }}
          >
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-2">
                <span className="text-xl">🎲</span>
                <div>
                  <p className="font-ui text-sm font-medium text-moon">{roll.actor}</p>
                  <p className="text-[11px] text-moon-dim/60">{roll.check}</p>
                </div>
              </div>
              <span className="flex items-center gap-1 text-xs font-ui font-medium px-2.5 py-1 rounded-full bg-void/50 border border-white/[0.08]">
                <span>{config.icon}</span>
                <span className="capitalize">{config.label}</span>
              </span>
            </div>

            <div className="grid grid-cols-4 gap-2 text-center">
              {[
                { label: "Roll", value: roll.roll, highlight: false },
                {
                  label: "Mod",
                  value: roll.modifier >= 0 ? `+${roll.modifier}` : roll.modifier,
                  highlight: false,
                },
                { label: "Total", value: roll.total, highlight: true },
                { label: "DC", value: roll.difficulty, highlight: false },
              ].map((stat) => (
                <div key={stat.label} className="glass-card !rounded-lg p-2">
                  <span className="text-[10px] text-moon-dim/50 font-ui uppercase tracking-wider block">
                    {stat.label}
                  </span>
                  <span
                    className={`font-mono text-lg ${stat.highlight ? "text-gold font-semibold" : "text-moon"}`}
                  >
                    {stat.value}
                  </span>
                </div>
              ))}
            </div>

            {roll.consequence && (
              <p className="mt-3 text-xs text-moon-dim/70 font-narrative italic leading-relaxed border-t border-white/[0.06] pt-3">
                {roll.consequence}
              </p>
            )}
          </div>
        );
      })}
    </div>
  );
}
