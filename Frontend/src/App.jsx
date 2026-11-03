import { useState } from "react";
import "./App.css";

export default function App() {
  const [jd, setJd] = useState("");
  const [loading, setLoading] = useState(false);
  const [done, setDone] = useState(false);
  const [error, setError] = useState("");

  const handleGenerate = async () => {
    if (!jd.trim()) return;
    setLoading(true);
    setDone(false);
    setError("");

    try {
      const res = await fetch("http://localhost:8000/tailor", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ job_description: jd }),
      });
      const data = await res.json();
      if (data.latex) {
        setDone(true);
      } else {
        setError("Something went wrong. Try again.");
      }
    } catch {
      setError("Could not connect to backend.");
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = () => {
    window.open("http://localhost:8000/download", "_blank");
  };

  return (
    <div className="container">
      <div className="card">
        <div className="header">
          <h1>Resume Tailor</h1>
          <p>Paste a job description and get a tailored LaTeX resume in seconds.</p>
        </div>

        <div className="body">
          <label>Job Description</label>
          <textarea
            value={jd}
            onChange={(e) => setJd(e.target.value)}
            placeholder="Paste the full job description here..."
            rows={12}
          />

          {error && <p className="error">{error}</p>}

          <div className="actions">
            <button
              className="btn-primary"
              onClick={handleGenerate}
              disabled={loading || !jd.trim()}
            >
              {loading ? (
                <span className="spinner-wrap">
                  <span className="spinner" /> Generating...
                </span>
              ) : (
                "Generate Resume"
              )}
            </button>

            {done && (
              <button className="btn-secondary" onClick={handleDownload}>
                Download .tex
              </button>
            )}
          </div>

          {done && (
            <p className="success">
              ✓ Resume generated! Download your <code>.tex</code> file and compile in Overleaf.
            </p>
          )}
        </div>
      </div>
    </div>
  );
}