import { useState, useRef, useCallback } from 'react'
import translations from './translations.json'

const API = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const kurdishName = (sci) => translations[sci?.toLowerCase()] || sci || 'نەزانراو'

export default function App() {
  const [file, setFile] = useState(null)
  const [preview, setPreview] = useState(null)
  const [result, setResult] = useState(null)
  const [examples, setExamples] = useState([])
  const [status, setStatus] = useState('idle') // idle | loading | done | error
  const inputRef = useRef(null)

  const onPick = useCallback((e) => {
    const f = e.target.files[0]
    if (!f) return
    setFile(f)
    setPreview(URL.createObjectURL(f))
    setResult(null)
    setExamples([])
    setStatus('idle')
  }, [])

  const onAnalyze = useCallback(async () => {
    if (!file || status === 'loading') return
    setStatus('loading')
    setExamples([])
    try {
      const body = new FormData()
      body.append('file', file)
      const res = await fetch(`${API}/predict`, { method: 'POST', body })
      if (!res.ok) throw new Error(res.statusText)
      const data = await res.json()
      setResult(data)
      setStatus('done')
      // Fetch gallery
      const ex = await fetch(`${API}/examples?species=${data.scientific_name}`)
      setExamples(await ex.json())
    } catch {
      setStatus('error')
    }
  }, [file, status])

  const conf = result ? (result.confidence * 100).toFixed(1) : 0

  return (
    <div className="app">

      {/* ── Header ── */}
      <header className="header">
        <div className="header-inner">
          <div className="logo-mark">🧠</div>
          <div>
            <h1 className="site-title">ناسینەوەی ئاژەڵ</h1>
            <p className="site-sub">ئاژەڵەکەت بنێرە، AI ناسیەوە</p>
          </div>
        </div>
        <span className="badge">AI • کوردی</span>
      </header>

      <main className="main">

        {/* ── Upload Panel ── */}
        <section className="card upload-card">
          <h2 className="card-title">📤 بارکردنی وێنە</h2>

          <div
            className={`drop-zone ${preview ? 'has-image' : ''}`}
            onClick={() => inputRef.current.click()}
          >
            <input ref={inputRef} type="file" accept="image/*" onChange={onPick} hidden />
            {preview
              ? <img src={preview} alt="پیشاندانی وێنە" className="preview-img" />
              : (
                <div className="drop-hint">
                  <span className="drop-icon">🖼️</span>
                  <p>کلیک بکە یان وێنەکە بکێشە ئێرە</p>
                  <small>JPG، PNG، WEBP</small>
                </div>
              )
            }
            {status === 'loading' && <div className="scan-line" />}
          </div>

          <div className="action-bar">
            <span className={`status-dot ${status}`} />
            <span className="status-text">
              {status === 'idle' && 'چاوەڕوانی وێنە'}
              {status === 'loading' && 'شیکردنەوە...'}
              {status === 'done' && 'ئەنجام ئامادەیە ✓'}
              {status === 'error' && 'هەڵەیەک ڕوویدا، دووبارە هەوڵبدەرەوە'}
            </span>
            <button
              className="btn-analyze"
              onClick={onAnalyze}
              disabled={!file || status === 'loading'}
            >
              {status === 'loading' ? '⏳ شیکردنەوە...' : '🔍 شیکردنەوە'}
            </button>
          </div>
        </section>

        {/* ── Result Panel ── */}
        <section className={`card result-card ${result ? 'has-result' : 'empty'}`}>
          {result ? (
            <>
              <div className="result-badge">دۆزرایەوە ✓</div>
              <h2 className="result-name">{kurdishName(result.scientific_name)}</h2>
              <p className="result-english">{result.species}</p>
              <p dir="ltr" className="result-sci">{result.scientific_name}</p>

              <div className="conf-block">
                <div className="conf-header">
                  <span>پشتبەستن</span>
                  <strong>{conf}%</strong>
                </div>
                <div className="conf-track">
                  <div className="conf-fill" style={{ width: `${conf}%` }} />
                </div>
              </div>
            </>
          ) : (
            <div className="empty-state">
              <span>📊</span>
              <p>ئەنجامەکان ئێرە دەردەکەون</p>
            </div>
          )}
        </section>

        {/* ── Gallery ── */}
        {examples.length > 0 && (
          <section className="card gallery-card">
            <h2 className="card-title">🎨 نموونەی وێنەکان — {kurdishName(result.scientific_name)}</h2>
            <div className="gallery">
              {examples.map((ex, i) => (
                <img
                  key={i}
                  src={`${API}${ex.url}`}
                  alt={ex.species}
                  className="gallery-img"
                  onClick={() => window.open(`${API}${ex.url}`, '_blank')}
                />
              ))}
            </div>
          </section>
        )}

      </main>

      <footer className="footer">
        <p>دروستکرا بۆ پڕۆژەی AI • کوردستان ٢٠٢٦</p>
      </footer>
    </div>
  )
}
