export default function AtmosphereBackground() {
  const stars = Array.from({ length: 60 }, (_, i) => ({
    id: i,
    left: `${(i * 17 + 7) % 100}%`,
    top: `${(i * 23 + 11) % 100}%`,
    size: i % 5 === 0 ? 2 : 1,
    delay: `${(i % 8) * 0.5}s`,
    duration: `${3 + (i % 4)}s`,
  }));

  return (
    <div className="fixed inset-0 -z-10 overflow-hidden pointer-events-none">
      <div className="absolute inset-0 bg-void" />
      <div className="absolute inset-0 bg-mesh" />

      {/* Moon */}
      <div className="absolute top-[8%] right-[12%] w-32 h-32 md:w-48 md:h-48">
        <div className="absolute inset-0 rounded-full bg-gradient-radial from-moon-glow/20 via-moon/5 to-transparent blur-2xl animate-pulse-soft" />
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-16 h-16 md:w-24 md:h-24 rounded-full bg-gradient-to-br from-moon-glow/30 to-moon-dim/10 border border-moon/10 shadow-[0_0_60px_rgba(200,212,232,0.15)]" />
        <div className="absolute top-1/2 left-1/2 -translate-x-[40%] -translate-y-[45%] w-3 h-3 md:w-4 md:h-4 rounded-full bg-void/40" />
      </div>

      {/* Stars */}
      {stars.map((star) => (
        <div
          key={star.id}
          className="absolute rounded-full bg-moon-glow animate-star-twinkle"
          style={{
            left: star.left,
            top: star.top,
            width: star.size,
            height: star.size,
            animationDelay: star.delay,
            animationDuration: star.duration,
          }}
        />
      ))}

      {/* Horizon mist */}
      <div className="absolute bottom-0 left-0 right-0 h-1/3 bg-gradient-to-t from-mystic-dim/10 via-transparent to-transparent" />
      <div className="absolute bottom-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-moon/10 to-transparent" />
    </div>
  );
}
