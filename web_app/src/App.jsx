import { useClassifier } from './hooks/useClassifier'
import Header from './components/Header'
import UploadCard from './components/UploadCard'
import ResultCard from './components/ResultCard'
import Gallery from './components/Gallery'

export default function App() {
  const { file, preview, result, examples, status, inputRef, onPick, onAnalyze, API } = useClassifier()

  return (
    <div className="app">
      <Header />
      <main className="main">
        <UploadCard
          preview={preview} status={status}
          inputRef={inputRef} onPick={onPick}
          onAnalyze={onAnalyze} file={file}
        />
        <ResultCard result={result} />
        <Gallery examples={examples} scientificName={result?.scientific_name} API={API} />
      </main>
      <footer className="footer">
        <p>  دروستکراوە لەلایان nexus تیمس بۆ پرۆژەی AI</p>
      </footer>
    </div>
  )
}
