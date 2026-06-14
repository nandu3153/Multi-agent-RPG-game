import ReactMarkdown from "react-markdown";

interface Props {
  type: "player" | "gm";
  content: string;
  isLatest?: boolean;
}

export default function MessageBubble({ type, content, isLatest }: Props) {
  const isPlayer = type === "player";

  if (isPlayer) {
    return (
      <div className={`flex justify-end mb-6 ${isLatest ? "animate-fade-in-up" : ""}`}>
        <div className="max-w-[90%] md:max-w-[75%]">
          <div className="flex items-center justify-end gap-2 mb-1.5">
            <span className="section-label text-mystic-glow/60">Your Action</span>
          </div>
          <div className="relative px-5 py-4 rounded-2xl rounded-br-md bg-gradient-to-br from-mystic/25 to-mystic-dim/15 border border-mystic/30 shadow-glow">
            <p className="font-narrative text-lg text-moon-glow leading-relaxed">{content}</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={`mb-8 ${isLatest ? "animate-fade-in-up" : ""}`}>
      <div className="flex items-center gap-2 mb-3">
        <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-gold/30 to-gold-dim/10 border border-gold/30 flex items-center justify-center text-sm">
          ☽
        </div>
        <span className="section-label text-gold/70">The Game Master</span>
      </div>
      <div className="relative pl-1 md:pl-4 border-l-2 border-gold/20">
        <div className="narrative-prose">
          <ReactMarkdown
            components={{
              p: ({ children }) => <p className="mb-4 last:mb-0">{children}</p>,
              strong: ({ children }) => (
                <strong className="text-gold font-semibold">{children}</strong>
              ),
              em: ({ children }) => <em className="text-moon-glow">{children}</em>,
            }}
          >
            {content}
          </ReactMarkdown>
        </div>
      </div>
    </div>
  );
}
