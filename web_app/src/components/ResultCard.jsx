function formatScientificName(slug) {
  const words = slug.split('-')
  return words.map((w, i) => (i === 0 ? w[0].toUpperCase() + w.slice(1) : w)).join(' ')
}

export default function ResultCard({ result }) {
  if (!result) {
    return (
      <section className="card result-card empty">
        <div className="empty-state">
          <span>🔍</span>
          <p>ئەنجامەکە لێرە دەردەکەوێت</p>
        </div>
      </section>
    )
  }

  const confidencePct = Math.round(result.confidence * 100)

  return (
    <section className="card result-card has-result">
      <span className="result-badge">دۆزرایەوە</span>
      <h2 className="result-name">{result.species}</h2>
      <p className="result-sci">{formatScientificName(result.scientific_name)}</p>

      <div className="conf-block">
        <div className="conf-header">
          <span>متمانە</span>
          <strong>{confidencePct}%</strong>
        </div>
        <div className="conf-track">
          <div className="conf-fill" style={{ width: `${confidencePct}%` }} />
        </div>
      </div>
    </section>
  )
}
