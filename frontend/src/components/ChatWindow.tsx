import { useEffect, useRef, useState } from "react";
import type { ChatMessage } from "../types";
import ChoiceChips from "./ChoiceChips";
import MessageBubble from "./MessageBubble";

interface Props {
  messages: ChatMessage[];
  choices: string[];
  onSend: (action: string) => void;
  loading: boolean;
  awaitingConfirmation: boolean;
}

export default function ChatWindow({
  messages,
  choices,
  onSend,
  loading,
  awaitingConfirmation,
}: Props) {
  const [input, setInput] = useState("");
  const bottomRef = useRef<HTMLDivElement>(null);
  const lastMessageId = messages[messages.length - 1]?.id;

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const trimmed = input.trim();
    if (!trimmed || loading) return;
    onSend(trimmed);
    setInput("");
  };

  const handleChoice = (choice: string) => {
    if (loading) return;
    onSend(choice);
  };

  return (
    <div className="flex flex-col h-full min-h-0">
      {/* Narrative scroll area */}
      <div className="flex-1 overflow-y-auto px-4 md:px-8 py-6 md:py-8">
        <div className="max-w-3xl mx-auto">
          {messages.length === 0 && !loading && (
            <div className="text-center py-20">
              <p className="font-narrative text-xl text-moon-dim/50 italic">
                The story awaits your first move...
              </p>
            </div>
          )}

          {messages.map((msg) => (
            <MessageBubble
              key={msg.id}
              type={msg.type}
              content={msg.content}
              isLatest={msg.id === lastMessageId && !loading}
            />
          ))}

          {loading && (
            <div className="flex items-center gap-3 py-4 animate-fade-in">
              <div className="flex gap-1">
                <span className="w-2 h-2 rounded-full bg-gold/60 animate-bounce" style={{ animationDelay: "0ms" }} />
                <span className="w-2 h-2 rounded-full bg-gold/60 animate-bounce" style={{ animationDelay: "150ms" }} />
                <span className="w-2 h-2 rounded-full bg-gold/60 animate-bounce" style={{ animationDelay: "300ms" }} />
              </div>
              <span className="font-narrative text-moon-dim/60 italic text-lg">
                The Game Master weaves the next scene...
              </span>
            </div>
          )}

          <div ref={bottomRef} />
        </div>
      </div>

      {/* Action area */}
      <div className="shrink-0 border-t border-white/[0.06] bg-void-50/80 backdrop-blur-xl">
        <ChoiceChips
          choices={choices}
          onSelect={handleChoice}
          loading={loading}
          awaitingConfirmation={awaitingConfirmation}
        />

        <form onSubmit={handleSubmit} className="px-4 md:px-6 pb-4 md:pb-5 flex gap-3">
          <div className="flex-1 relative">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              disabled={loading}
              placeholder={
                awaitingConfirmation
                  ? "Type your decision, or use the buttons above..."
                  : "Describe what you do — explore, speak, fight, investigate..."
              }
              className="input-field !text-base pr-12"
            />
            <kbd className="hidden md:inline absolute right-3 top-1/2 -translate-y-1/2 text-[10px] text-moon-dim/30 font-mono px-1.5 py-0.5 rounded border border-white/[0.06]">
              Enter
            </kbd>
          </div>
          <button
            type="submit"
            disabled={loading || !input.trim()}
            className="btn-primary !px-5 md:!px-8 shrink-0"
          >
            <span className="hidden sm:inline">Act</span>
            <span className="sm:hidden">→</span>
          </button>
        </form>
      </div>
    </div>
  );
}
