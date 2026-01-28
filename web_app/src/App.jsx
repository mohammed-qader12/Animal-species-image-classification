import { useState, useRef } from 'react'
import translations from './translations.json';

const API_URL = `http://${window.location.hostname}:8000`;

function App() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [speciesExamples, setSpeciesExamples] = useState([]);
  const fileInputRef = useRef(null);

  const handleFileSelect = (e) => {
    const file = e.target.files[0];
    if (file) {
      setSelectedFile(file);
      setPreview(URL.createObjectURL(file));
      setResult(null);
      setSpeciesExamples([]);
    }
  };

  const fetchExamplesForSpecies = async (speciesName) => {
    try {
      const res = await fetch(`${API_URL}/examples?species=${speciesName}`);
      const data = await res.json();
      setSpeciesExamples(data);
    } catch (err) {
      console.error("Failed to load species examples", err);
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) return;

    setLoading(true);
    setSpeciesExamples([]);
    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
      const response = await fetch(`${API_URL}/predict`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`Error: ${response.statusText}`);
      }

      const data = await response.json();
      setResult(data);

      if (data.scientific_name) {
        fetchExamplesForSpecies(data.scientific_name);
      }
    } catch (error) {
      console.error("Prediction failed", error);
      alert("پرۆسەکە سەرکەوتوو نەبوو. تکایە دووبارە هەوڵبدەرەوە.");
    } finally {
      setLoading(false);
    }
  };

  const getKurdishName = (scientificName) => {
    if (!scientificName) return "نەزانراو";
    const key = scientificName.toLowerCase();
    return translations[key] || "ناو بە کوردی بەردەست نییە";
  };

  const triggerFileInput = () => {
    fileInputRef.current.click();
  };

  return (
    <div className="min-h-screen bg-[#030712] text-slate-200 selection:bg-indigo-500/30 font-[Vazirmatn] overflow-x-hidden">

      {/* Navbar / Header - Minimal Tech */}
      <nav className="border-b border-indigo-900/30 bg-black/40 backdrop-blur-md sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded bg-indigo-600 flex items-center justify-center text-white font-bold shadow-[0_0_15px_rgba(79,70,229,0.5)]">AI</div>
            <span className="font-bold text-lg tracking-wider text-white">X-SPECIES</span>
          </div>
          <div className="text-xs font-mono text-indigo-400 opacity-70 dir-ltr">SYSTEM_ONLINE</div>
        </div>
      </nav>

      <div className="max-w-7xl mx-auto px-4 py-8 grid grid-cols-1 lg:grid-cols-12 gap-8">

        {/* LEFT COLUMN: UPLOAD & PREVIEW (Span 7) */}
        <div className="lg:col-span-7 flex flex-col gap-6">

          <div className="tech-border rounded-2xl p-1 overflow-hidden group relative min-h-[500px] flex flex-col">
            {/* Header Line */}
            <div className="absolute top-4 left-4 z-20 flex gap-2">
              <span className="w-2 h-2 rounded-full bg-red-500"></span>
              <span className="w-2 h-2 rounded-full bg-yellow-500"></span>
              <span className="w-2 h-2 rounded-full bg-green-500"></span>
            </div>

            {/* Main Interactive Area */}
            <div
              onClick={triggerFileInput}
              className="flex-1 bg-black/50 rounded-xl relative overflow-hidden cursor-pointer hover:bg-slate-900/50 transition-colors border border-dashed border-slate-700 hover:border-indigo-500 m-2 flex items-center justify-center p-4"
            >
              <input
                ref={fileInputRef}
                type="file"
                accept="image/*"
                onChange={handleFileSelect}
                className="hidden"
              />

              {!preview ? (
                <div className="text-center space-y-4 animate-pulse">
                  <svg className="w-20 h-20 mx-auto text-slate-600 group-hover:text-indigo-500 transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="1" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"></path></svg>
                  <p className="text-xl font-medium text-slate-400">وێنە باربکە بۆ شیکردنەوە</p>
                  <p className="text-xs font-mono text-slate-600">INPUT: JPG, PNG, WEBP // MAX: 10MB</p>
                </div>
              ) : (
                <div className="relative w-full h-full flex items-center justify-center">
                  {/* DYNAMIC IMAGE SIZING: w-auto h-auto max-w-full max-h-full. 
                       This respects the image's ratio inside the flex container. */}
                  <img
                    src={preview}
                    alt="Target"
                    className="max-w-full max-h-[600px] object-contain shadow-2xl rounded-lg z-10"
                  />

                  {/* Scanning Overlay Effect */}
                  {loading && (
                    <div className="absolute inset-0 z-20 overflow-hidden rounded-lg pointer-events-none">
                      <div className="w-full h-1 bg-indigo-500 shadow-[0_0_20px_#6366f1] animate-scan opacity-80"></div>
                    </div>
                  )}
                </div>
              )}
            </div>

            {/* Action Bar */}
            <div className="p-4 bg-slate-900/50 border-t border-slate-800 flex justify-between items-center backdrop-blur-sm">
              <div className="text-xs font-mono text-slate-500">
                STATUS: {loading ? <span className="text-yellow-400 animate-pulse">PROCESSING...</span> : selectedFile ? <span className="text-green-400">READY</span> : 'IDLE'}
              </div>
              <button
                onClick={(e) => { e.stopPropagation(); handleUpload(); }}
                disabled={!selectedFile || loading}
                className={`px-8 py-3 rounded-lg font-bold tracking-wide transition-all shadow-lg
                    ${!selectedFile || loading
                    ? 'bg-slate-800 text-slate-500 cursor-not-allowed'
                    : 'bg-indigo-600 text-white hover:bg-indigo-500 shadow-indigo-600/30 hover:shadow-indigo-600/50 active:scale-95'}
                  `}
              >
                {loading ? 'ANALYZING...' : 'START SCAN'}
              </button>
            </div>
          </div>
        </div>

        {/* RIGHT COLUMN: RESULTS & DATA (Span 5) */}
        <div className="lg:col-span-5 flex flex-col gap-6">

          {result ? (
            <div className="tech-border rounded-2xl p-8 h-full fade-in flex flex-col justify-center relative overflow-hidden">
              <div className="absolute top-0 right-0 w-32 h-32 bg-indigo-600/10 rounded-bl-full pointer-events-none"></div>

              <div className="mb-8 text-center sm:text-right">
                <span className="inline-block px-3 py-1 rounded bg-indigo-900/50 text-indigo-300 text-xs font-mono border border-indigo-700/50 mb-4">MATCH FOUND</span>
                <h2 className="text-5xl font-black text-transparent bg-clip-text bg-gradient-to-r from-white to-slate-400 mb-2">{getKurdishName(result.scientific_name)}</h2>
                <h3 className="text-2xl text-indigo-400 font-light tracking-wide">{result.species}</h3>
              </div>

              <div className="space-y-6">
                <div className="bg-slate-900/80 p-6 rounded-xl border border-slate-800">
                  <div className="flex justify-between items-end mb-2">
                    <span className="text-sm font-mono text-slate-500">CONFIDENCE SCORE</span>
                    <span className="text-3xl font-bold text-white">{(result.confidence * 100).toFixed(1)}%</span>
                  </div>
                  <div className="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-indigo-500 relative"
                      style={{ width: `${(result.confidence * 100).toFixed(1)}%` }}
                    >
                      <div className="absolute right-0 top-[-2px] bottom-[-2px] w-1 bg-white shadow-[0_0_10px_white]"></div>
                    </div>
                  </div>
                </div>

                <div className="bg-slate-900/80 p-4 rounded-xl border border-slate-800 flex items-center justify-between">
                  <div className="text-sm font-mono text-slate-500">SCIENTIFIC NAME</div>
                  <div className="text-lg font-mono text-indigo-300 pointer-events-none select-none dir-ltr">{result.scientific_name}</div>
                </div>
              </div>
            </div>
          ) : (
            <div className="tech-border rounded-2xl p-8 h-full flex items-center justify-center opacity-50 border-dashed border-slate-800">
              <div className="text-center">
                <div className="text-6xl mb-4 opacity-20">📊</div>
                <p className="text-slate-500 font-mono">NO DATA AVAILABLE</p>
              </div>
            </div>
          )}

        </div>

        {/* BOTTOM SECTION: GALLERY (Full Width) */}
        {speciesExamples.length > 0 && (
          <div className="col-span-1 lg:col-span-12 mt-4">
            <div className="tech-border rounded-2xl p-6 fade-in">
              <div className="flex items-center justify-between mb-6 border-b border-slate-800 pb-4">
                <h3 className="text-xl font-bold text-white flex items-center gap-2">
                  <span className="text-indigo-500">///</span> DATABASE EXAMPLES
                </h3>
                <span className="text-xs font-mono text-slate-500">subject: {result.scientific_name}</span>
              </div>

              <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
                {speciesExamples.map((ex, idx) => (
                  <div
                    key={idx}
                    className="aspect-square rounded-lg overflow-hidden border border-slate-800 hover:border-indigo-500 transition-colors cursor-pointer group relative bg-black"
                    onClick={() => window.open(API_URL + ex.url, '_blank')}
                  >
                    <img
                      src={`${API_URL}${ex.url}`}
                      alt={ex.species}
                      className="w-full h-full object-cover opacity-70 group-hover:opacity-100 group-hover:scale-110 transition-all duration-500"
                    />
                    <div className="absolute inset-0 ring-1 ring-inset ring-black/50 group-hover:ring-transparent transition-all"></div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

      </div>
    </div>
  )
}

export default App
