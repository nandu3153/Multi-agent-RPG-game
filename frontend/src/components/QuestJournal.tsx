import type { QuestEntry } from "../types";

interface Props {
  questLog: QuestEntry[];
  location: string;
  activeQuest: string;
}

function QuestCard({ quest, variant }: { quest: QuestEntry; variant: "active" | "available" | "completed" }) {
  const styles = {
    active: "border-emerald-500/20 bg-emerald-950/20",
    available: "border-gold/15 bg-gold/5",
    completed: "border-white/[0.04] bg-void/40 opacity-60",
  };

  const statusDot = {
    active: "bg-emerald-400 shadow-[0_0_8px_rgba(52,211,153,0.5)]",
    available: "bg-gold/60",
    completed: "bg-moon-dim/30",
  };

  return (
    <div className={`p-3 rounded-xl border ${styles[variant]} transition-all duration-200`}>
      <div className="flex items-start gap-2.5">
        <div className={`w-2 h-2 rounded-full mt-1.5 shrink-0 ${statusDot[variant]}`} />
        <div className="min-w-0">
          <h4
            className={`font-ui text-sm font-medium ${
              variant === "completed" ? "line-through text-moon-dim/50" : "text-moon"
            }`}
          >
            {quest.title}
          </h4>
          {variant !== "completed" && quest.description && (
            <p className="text-xs text-moon-dim/60 font-narrative mt-1 leading-relaxed">
              {quest.description}
            </p>
          )}
        </div>
      </div>
    </div>
  );
}

export default function QuestJournal({ questLog, location, activeQuest }: Props) {
  const active = questLog.filter((q) => q.status === "active");
  const available = questLog.filter((q) => q.status === "available");
  const completed = questLog.filter((q) => q.status === "completed");

  return (
    <aside className="w-full lg:w-72 xl:w-80 flex flex-col glass-panel border-l border-white/[0.06] shrink-0 overflow-hidden">
      <div className="p-5 border-b border-white/[0.06]">
        <p className="section-label">World</p>
        <h2 className="font-display text-lg text-gold mt-1">Quest Journal</h2>
      </div>

      <div className="flex-1 overflow-y-auto p-5 space-y-5">
        {/* Location card */}
        <div className="p-4 rounded-xl bg-gradient-to-br from-mystic/10 to-void border border-mystic/20">
          <p className="section-label mb-1">Current Location</p>
          <p className="font-narrative text-lg text-moon-glow">{location}</p>
        </div>

        {/* Active quest highlight */}
        <div className="p-4 rounded-xl bg-gradient-to-br from-gold/10 to-void border border-gold/20">
          <p className="section-label mb-1">Main Objective</p>
          <p className="font-ui text-sm text-gold font-medium leading-snug">{activeQuest}</p>
        </div>

        {active.length > 0 && (
          <section>
            <h3 className="section-label mb-2 text-emerald-400/70">Active Quests</h3>
            <div className="space-y-2">
              {active.map((q) => (
                <QuestCard key={q.id} quest={q} variant="active" />
              ))}
            </div>
          </section>
        )}

        {available.length > 0 && (
          <section>
            <h3 className="section-label mb-2 text-gold/70">Available</h3>
            <div className="space-y-2">
              {available.map((q) => (
                <QuestCard key={q.id} quest={q} variant="available" />
              ))}
            </div>
          </section>
        )}

        {completed.length > 0 && (
          <section>
            <h3 className="section-label mb-2">Completed</h3>
            <div className="space-y-2">
              {completed.map((q) => (
                <QuestCard key={q.id} quest={q} variant="completed" />
              ))}
            </div>
          </section>
        )}
      </div>
    </aside>
  );
}
