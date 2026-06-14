import { useState } from "react";
import type { PartyMember } from "../types";

const CLASS_ICONS: Record<string, string> = {
  warrior: "⚔",
  mage: "✦",
  rogue: "◈",
  healer: "✿",
};

const CLASS_COLORS: Record<string, string> = {
  warrior: "from-ember/30 to-ember-dim/10 border-ember/20",
  mage: "from-mystic/30 to-mystic-dim/10 border-mystic/20",
  rogue: "from-emerald-800/30 to-emerald-950/10 border-emerald-700/20",
  healer: "from-gold/25 to-gold-dim/10 border-gold/20",
};

function hpColor(pct: number) {
  if (pct > 60) return "bg-gradient-to-r from-emerald-600 to-emerald-400";
  if (pct > 30) return "bg-gradient-to-r from-amber-600 to-amber-400";
  return "bg-gradient-to-r from-red-700 to-red-500";
}

function HpBar({ current, max }: { current: number; max: number }) {
  const pct = Math.max(0, Math.min(100, (current / max) * 100));
  return (
    <div className="hp-bar-track">
      <div className={`hp-bar-fill ${hpColor(pct)}`} style={{ width: `${pct}%` }} />
    </div>
  );
}

function StatModal({ member, onClose }: { member: PartyMember; onClose: () => void }) {
  const icon = CLASS_ICONS[member.agent] ?? "◆";
  const gradient = CLASS_COLORS[member.agent] ?? "from-void-100 to-void border-white/10";

  return (
    <div
      className="fixed inset-0 bg-void/80 backdrop-blur-sm flex items-center justify-center z-50 p-4 animate-fade-in"
      onClick={onClose}
    >
      <div
        className="glass-panel rounded-2xl p-6 max-w-sm w-full animate-dice-pop"
        onClick={(e) => e.stopPropagation()}
      >
        <div className={`flex items-center gap-4 mb-6 p-4 rounded-xl bg-gradient-to-br border ${gradient}`}>
          <span className="text-3xl">{icon}</span>
          <div>
            <h3 className="font-display text-xl text-gold">{member.name}</h3>
            <p className="text-sm text-moon-dim font-ui capitalize">{member.agent}</p>
          </div>
        </div>

        <div className="grid grid-cols-3 gap-2 mb-5">
          {Object.entries(member.scores).map(([k, v]) => (
            <div key={k} className="glass-card p-2 text-center">
              <span className="text-[10px] text-moon-dim/60 font-ui uppercase">{k}</span>
              <p className="font-mono text-lg text-moon">{v}</p>
            </div>
          ))}
        </div>

        <div className="space-y-3 text-sm font-ui">
          <div className="flex justify-between">
            <span className="text-moon-dim">Armor Class</span>
            <span className="font-mono text-moon">{member.ac}</span>
          </div>
          <div>
            <div className="flex justify-between mb-1">
              <span className="text-moon-dim">Health</span>
              <span className="font-mono text-moon">
                {member.hp_current} / {member.hp_max}
              </span>
            </div>
            <HpBar current={member.hp_current} max={member.hp_max} />
          </div>
          <div>
            <span className="text-moon-dim block mb-1">Inventory</span>
            <div className="flex flex-wrap gap-1.5">
              {member.inventory.length > 0 ? (
                member.inventory.map((item) => (
                  <span
                    key={item}
                    className="text-xs px-2 py-0.5 rounded-md bg-void/80 border border-white/[0.06] text-moon-dim"
                  >
                    {item.replace(/_/g, " ")}
                  </span>
                ))
              ) : (
                <span className="text-moon-dim/50 text-xs">Empty</span>
              )}
            </div>
          </div>
          {member.conditions.length > 0 && (
            <div className="p-2 rounded-lg bg-red-950/30 border border-red-800/30">
              <span className="text-red-400 text-xs">
                {member.conditions.join(", ")}
              </span>
            </div>
          )}
        </div>

        <button onClick={onClose} className="btn-ghost w-full mt-6">
          Close
        </button>
      </div>
    </div>
  );
}

interface Props {
  party: PartyMember[];
  playerClass: string;
  mobileOpen?: boolean;
  onClose?: () => void;
}

export default function PartyPanel({ party, playerClass, mobileOpen, onClose }: Props) {
  const [selected, setSelected] = useState<PartyMember | null>(null);

  const content = (
    <>
      <div className="flex items-center justify-between mb-5">
        <div>
          <p className="section-label">Your Party</p>
          <h2 className="font-display text-lg text-gold mt-1">Companions</h2>
        </div>
        {onClose && (
          <button onClick={onClose} className="lg:hidden btn-ghost !p-2" aria-label="Close">
            ✕
          </button>
        )}
      </div>

      <div className="space-y-3">
        {party.map((member) => {
          const isPlayer = member.agent === playerClass;
          const icon = CLASS_ICONS[member.agent] ?? "◆";
          const gradient = CLASS_COLORS[member.agent] ?? "from-void-100 to-void border-white/10";

          return (
            <button
              key={member.agent}
              onClick={() => setSelected(member)}
              className={`w-full text-left glass-card p-3 transition-all duration-200 hover:border-white/15 hover:shadow-glow group ${
                isPlayer ? "ring-1 ring-gold/30" : ""
              }`}
            >
              <div className="flex items-center gap-3 mb-2">
                <div
                  className={`w-10 h-10 rounded-lg bg-gradient-to-br border flex items-center justify-center text-lg shrink-0 ${gradient}`}
                >
                  {icon}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <span className="font-ui font-medium text-moon truncate">{member.name}</span>
                    {isPlayer && (
                      <span className="text-[9px] uppercase tracking-wider text-gold/70 font-ui shrink-0">
                        You
                      </span>
                    )}
                  </div>
                  <span className="text-xs font-mono text-moon-dim/60">
                    {member.hp_current}/{member.hp_max} HP
                  </span>
                </div>
                <span className="text-xs font-mono text-moon-dim/40 group-hover:text-moon-dim transition-colors">
                  AC {member.ac}
                </span>
              </div>

              <HpBar current={member.hp_current} max={member.hp_max} />

              {member.conditions.length > 0 && (
                <p className="text-[11px] text-red-400 mt-1.5">{member.conditions.join(", ")}</p>
              )}

              {member.inventory.length > 0 && (
                <p className="text-[11px] text-moon-dim/40 mt-1.5 truncate">
                  {member.inventory.slice(0, 2).map((i) => i.replace(/_/g, " ")).join(" · ")}
                  {member.inventory.length > 2 && " · ..."}
                </p>
              )}
            </button>
          );
        })}
      </div>
    </>
  );

  return (
    <>
      {/* Desktop sidebar */}
      <aside className="hidden lg:flex w-72 xl:w-80 flex-col glass-panel border-r border-white/[0.06] p-5 overflow-y-auto shrink-0">
        {content}
      </aside>

      {/* Mobile drawer */}
      {mobileOpen && (
        <div className="lg:hidden fixed inset-0 z-40">
          <div className="absolute inset-0 bg-void/70 backdrop-blur-sm" onClick={onClose} />
          <aside className="absolute left-0 top-0 bottom-0 w-80 max-w-[85vw] glass-panel p-5 overflow-y-auto animate-slide-in-right">
            {content}
          </aside>
        </div>
      )}

      {selected && <StatModal member={selected} onClose={() => setSelected(null)} />}
    </>
  );
}
