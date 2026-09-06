import { useEffect, useRef, useState } from 'react'

const API = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export function useClassifier() {
  const [file, setFile] = useState(null)
  const [preview, setPreview] = useState(null)
  const [result, setResult] = useState(null)
  const [examples, setExamples] = useState([])
  const [status, setStatus] = useState('idle') // idle | loading | done | error
  const inputRef = useRef(null)

  useEffect(() => {
    fetch(`${API}/examples`)
      .then((res) => res.json())
      .then(setExamples)
      .catch(() => setExamples([]))
  }, [])

  function onPick(picked) {
    if (!picked) return
    setFile(picked)
    setPreview(URL.createObjectURL(picked))
    setResult(null)
    setStatus('idle')
  }

  async function onAnalyze() {
    if (!file) return
    setStatus('loading')
    try {
      const form = new FormData()
      form.append('file', file)
      const res = await fetch(`${API}/predict`, { method: 'POST', body: form })
      if (!res.ok) throw new Error(`Request failed (${res.status})`)
      const data = await res.json()
      setResult(data)
      setStatus('done')
    } catch (err) {
      setResult(null)
      setStatus('error')
    }
  }

  return { file, preview, result, examples, status, inputRef, onPick, onAnalyze, API }
}
