const CLASSES = [
  {
    id: "warrior",
    name: "Warrior",
    icon: "⚔",
    tagline: "Shield of the party",
    description: "Iron resolve and devastating strikes. You lead from the front.",
    accent: "from-ember/20 to-ember-dim/5 border-ember/30",
    activeAccent: "from-ember/30 to-ember-dim/10 border-ember/60 shadow-[0_0_30px_rgba(196,92,62,0.2)]",
    textAccent: "text-ember",
  },
  {
    id: "mage",
    name: "Mage",
    icon: "✦",
    tagline: "Weaver of arcane forces",
    description: "Ancient runes answer your call. Knowledge is your weapon.",
    accent: "from-mystic/20 to-mystic-dim/5 border-mystic/30",
    activeAccent: "from-mystic/30 to-mystic-dim/10 border-mystic-glow/50 shadow-glow",
    textAccent: "text-mystic-glow",
  },
  {
    id: "rogue",
    name: "Rogue",
    icon: "◈",
    tagline: "Shadow in the moonlight",
    description: "Quick wit, quicker blade. You see what others miss.",
    accent: "from-emerald-900/30 to-emerald-950/10 border-emerald-700/30",
    activeAccent: "from-emerald-800/30 to-emerald-950/10 border-emerald-500/40 shadow-[0_0_30px_rgba(52,211,153,0.15)]",
    textAccent: "text-emerald-400",
  },
  {
    id: "healer",
    name: "Healer",
    icon: "✿",
    tagline: "Voice of the Silver Root",
    description: "Sacred light mends wounds. Your faith guides the lost.",
    accent: "from-gold/15 to-gold-dim/5 border-gold/25",
    activeAccent: "from-gold/25 to-gold-dim/10 border-gold/50 shadow-glow-gold",
    textAccent: "text-gold",
  },
] as const;

interface Props {
  playerName: string;
  characterClass: string;
  loading: boolean;
  error: string | null;
  onNameChange: (name: string) => void;
  onClassChange: (cls: string) => void;
  onStart: () => void;
}

export default function CharacterCreation({
  playerName,
  characterClass,
  loading,
  error,
  onNameChange,
  onClassChange,
  onStart,
}: Props) {
  const selected = CLASSES.find((c) => c.id === characterClass) ?? CLASSES[0];

  return (
    <div className="min-h-screen flex items-center justify-center p-4 md:p-8">
      <div className="w-full max-w-2xl animate-fade-in-up">
        {/* Title block */}
        <div className="text-center mb-10">
          <p className="section-label mb-3">A Dark Fantasy Adventure</p>
          <h1 className="font-display text-3xl md:text-5xl text-gold tracking-wide mb-2">
            The Shattered Moon
          </h1>
          <p className="font-narrative text-xl md:text-2xl text-moon-dim italic">
            of Eldervale
          </p>
          <div className="mt-6 flex items-center justify-center gap-3">
            <div className="h-px w-16 bg-gradient-to-r from-transparent to-gold/40" />
            <span className="text-moon-dim/50 text-lg">☽</span>
            <div className="h-px w-16 bg-gradient-to-l from-transparent to-gold/40" />
          </div>
        </div>

        {/* Main card */}
        <div className="glass-panel rounded-2xl p-6 md:p-8">
          <div className="mb-6">
            <label className="section-label block mb-2">Your Name</label>
            <input
              value={playerName}
              onChange={(e) => onNameChange(e.target.value)}
              placeholder="Enter your hero's name..."
              className="input-field"
              maxLength={32}
            />
          </div>

          <div className="mb-8">
            <label className="section-label block mb-3">Choose Your Path</label>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              {CLASSES.map((cls) => {
                const isActive = characterClass === cls.id;
                return (
                  <button
                    key={cls.id}
                    type="button"
                    onClick={() => onClassChange(cls.id)}
                    className={`group relative text-left p-4 rounded-xl border bg-gradient-to-br transition-all duration-300 ${
                      isActive ? cls.activeAccent : `${cls.accent} hover:border-white/20`
                    }`}
                  >
                    <div className="flex items-start gap-3">
                      <span
                        className={`text-2xl ${isActive ? cls.textAccent : "text-moon-dim/60"} transition-colors`}
                      >
                        {cls.icon}
                      </span>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2">
                          <span className={`font-ui font-semibold ${isActive ? "text-moon" : "text-moon-dim"}`}>
                            {cls.name}
                          </span>
                          {isActive && (
                            <span className="text-[10px] uppercase tracking-wider text-gold/80 font-ui">
                              Selected
                            </span>
                          )}
                        </div>
                        <p className="text-xs text-moon-dim/70 font-ui mt-0.5">{cls.tagline}</p>
                      </div>
                    </div>
                  </button>
                );
              })}
            </div>

            {/* Selected class detail */}
            <div className="mt-4 p-4 rounded-xl bg-void/50 border border-white/[0.04]">
              <p className="font-narrative text-lg text-moon/80 italic leading-relaxed">
                {selected.description}
              </p>
            </div>
          </div>

          <button
            onClick={onStart}
            disabled={loading || !playerName.trim()}
            className="btn-primary w-full text-center"
          >
            {loading ? (
              <span className="flex items-center justify-center gap-2">
                <span className="w-4 h-4 border-2 border-void/30 border-t-void rounded-full animate-spin" />
                Summoning the Game Master...
              </span>
            ) : (
              "Begin Your Adventure"
            )}
          </button>

          {error && (
            <div className="mt-4 p-3 rounded-lg bg-red-950/40 border border-red-800/40 text-red-300 text-sm font-ui">
              {error}
            </div>
          )}
        </div>

        <p className="text-center mt-6 text-moon-dim/40 text-xs font-ui">
          Your choices shape the story. Every action has consequences.
        </p>
      </div>
    </div>
  );
}
