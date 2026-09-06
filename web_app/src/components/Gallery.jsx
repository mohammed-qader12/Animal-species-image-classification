export default function Gallery({ examples, scientificName, API }) {
  return (
    <section className="card gallery-card">
      <h2 className="card-title">نموونەکانی خۆرئاوا</h2>
      <div className="gallery">
        {examples.map((ex, i) => (
          <img
            key={`${ex.species}-${i}`}
            src={`${API}${ex.url}`}
            alt={ex.species}
            title={ex.species}
            className="gallery-img"
            style={ex.species === scientificName ? { borderColor: 'var(--accent)' } : undefined}
          />
        ))}
      </div>
    </section>
  )
}
