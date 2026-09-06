const STATUS_LABEL = {
  idle: 'ئامادەیە بۆ شیکردنەوە',
  loading: 'شیکردنەوەی وێنە...',
  done: 'شیکردنەوە تەواو بوو',
  error: 'هەڵەیەک ڕوویدا',
}

export default function UploadCard({ preview, status, inputRef, onPick, onAnalyze, file }) {
  return (
    <section className="card">
      <h2 className="card-title">وێنەکە باربکە</h2>

      <div
        className={`drop-zone${preview ? ' has-image' : ''}`}
        onClick={() => inputRef.current?.click()}
      >
        {status === 'loading' && <div className="scan-line" />}
        {preview ? (
          <img src={preview} alt="پێشبینین" className="preview-img" />
        ) : (
          <div className="drop-hint">
            <span className="drop-icon">📷</span>
            <p>وێنەیەک هەڵبژێرە</p>
            <small>JPG, PNG</small>
          </div>
        )}
        <input
          ref={inputRef}
          type="file"
          accept="image/*"
          hidden
          onChange={(e) => onPick(e.target.files?.[0])}
        />
      </div>

      <div className="action-bar">
        <span className={`status-dot ${status}`} />
        <span className="status-text">{STATUS_LABEL[status]}</span>
        <button
          className="btn-analyze"
          disabled={!file || status === 'loading'}
          onClick={onAnalyze}
        >
          شیکردنەوە
        </button>
      </div>
    </section>
  )
}
