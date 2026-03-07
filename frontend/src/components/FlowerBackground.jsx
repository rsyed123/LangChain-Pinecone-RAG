const FLOWERS = ['🌸', '🌺', '🌼', '🌻', '🌷', '💐']

// Deterministic positions using golden-angle spread (no Math.random = no flicker on re-render)
const flowers = Array.from({ length: 24 }, (_, i) => ({
  id: i,
  emoji: FLOWERS[i % FLOWERS.length],
  left: `${((i * 61.8) % 100).toFixed(1)}%`,
  top: `${((i * 38.2) % 100).toFixed(1)}%`,
  fontSize: `${1.4 + (i % 4) * 0.35}rem`,
  opacity: 0.12 + (i % 5) * 0.04,
  animationDuration: `${5 + (i % 4)}s`,
  animationDelay: `${(i * 0.4) % 4}s`,
}))

function FlowerBackground() {
  return (
    <div className="flower-bg" aria-hidden="true">
      {flowers.map(f => (
        <span
          key={f.id}
          className="flower"
          style={{
            left: f.left,
            top: f.top,
            fontSize: f.fontSize,
            opacity: f.opacity,
            animationDuration: f.animationDuration,
            animationDelay: f.animationDelay,
          }}
        >
          {f.emoji}
        </span>
      ))}
    </div>
  )
}

export default FlowerBackground
