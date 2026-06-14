interface Props {
  choices: string[];
  onSelect: (choice: string) => void;
  loading: boolean;
  awaitingConfirmation: boolean;
}

function stripNumberPrefix(choice: string): string {
  return choice.replace(/^\d+\.\s*/, "").trim();
}

export default function ChoiceChips({ choices, onSelect, loading, awaitingConfirmation }: Props) {
  if (choices.length === 0 && !awaitingConfirmation) return null;

  if (awaitingConfirmation) {
    return (
      <div className="px-4 md:px-6 pb-3">
        <p className="section-label mb-2 text-ember">This action cannot be undone</p>
        <div className="flex flex-wrap gap-2">
          <button
            onClick={() => onSelect("Yes, proceed")}
            disabled={loading}
            className="px-4 py-2 rounded-xl text-sm font-ui bg-ember/20 border border-ember/40 text-ember hover:bg-ember/30 transition-all disabled:opacity-40"
          >
            ✓ Proceed
          </button>
          <button
            onClick={() => onSelect("No, reconsider")}
            disabled={loading}
            className="btn-ghost !text-sm"
          >
            ✕ Reconsider
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="px-4 md:px-6 pb-3">
      <p className="section-label mb-2">Suggested Actions</p>
      <div className="flex flex-wrap gap-2">
        {choices.map((choice, i) => (
          <button
            key={`${choice}-${i}`}
            onClick={() => onSelect(stripNumberPrefix(choice))}
            disabled={loading}
            className="group px-4 py-2.5 rounded-xl text-sm font-ui text-left
              bg-void/60 border border-white/[0.08] text-moon-dim
              hover:border-gold/30 hover:text-moon hover:bg-gold/5
              transition-all duration-200 disabled:opacity-40
              max-w-full"
          >
            <span className="text-gold/50 group-hover:text-gold mr-2 font-mono text-xs">
              {i + 1}
            </span>
            {stripNumberPrefix(choice)}
          </button>
        ))}
      </div>
    </div>
  );
}
