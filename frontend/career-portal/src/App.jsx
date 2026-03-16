import { useState } from 'react'
import './App.css'
import Spinner from './Spinner'
import ChatbotPage from './ChatbotPage'
import SIDChatPage from './sid/SIDChatPage'

function App() {
  const [page, setPage] = useState("home")
  const [text, setText] = useState("")
  const [loading, setLoading] = useState(false)
  const [url, setUrl] = useState("http://localhost:8080/evaluate")
  const [mode, setMode] = useState("Unsafe")
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)

  const poisonedUrl = "http://localhost:8082/evaluate"
  const safeUrl = "http://localhost:8081/evaluate"
  const unsafeUrl = "http://localhost:8080/evaluate"

  async function sendPost() {
    setLoading(true)
    setResult(null)
    setError(null)
    try {
      const res = await fetch(url, {
        method: "POST",
        body: JSON.stringify({ "resume-text": text,
          "mode": mode === "Safe" ? "safe" : "poisoned"}),
        headers: { "Content-Type": "application/json" }
      })
      const resBody = await res.json()
      setResult(resBody)
    } catch {
      setError("Failed to connect to the server. Please ensure the backend is running.")
    }
    setLoading(false)
  }

  async function sendPoisoned() {

    setLoading(true)
    setResult(null)
    setError(null)

    try {

      const res = await fetch(poisonedUrl, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          "resume-text": text,
          "mode": "poisoned"
        })
      })

      const resBody = await res.json()
      setResult(resBody)

    } catch {

      setError("Failed to connect to the poisoned model server.")

    }

    setLoading(false)

  }

  function toggleMode() {
    if (mode === "Unsafe") {
      setMode("Safe")
      setUrl(safeUrl)
    } else {
      setMode("Unsafe")
      setUrl(unsafeUrl)
    }
    setResult(null)
    setError(null)
  }

  console.log("resultStr:", result ? String(result.verdict): null)
  const resultStr = result ? String(result.verdict).trim() : ""
  const qualified = resultStr === "Likely" || resultStr === "Highly Likely"

  if (page === "chatbot") {
    return <ChatbotPage onNavigate={setPage} mode={mode} toggleMode={toggleMode} />
  }
  if (page === "sidChat") {
    return <SIDChatPage onBack={() => setPage("home")} />
  }

  return (
    <div className="app">

      {/* ── Banner ── */}
      <header className="banner">
        <div className="banner-left">
          <div className="brand-icon">TC</div>
          <span className="brand-name">TechCorp Careers</span>
        </div>
        <nav className="banner-nav">
          <button className="nav-link" onClick={() => setPage("chatbot")}>Job Info Chatbot</button>
          <a href="#requirements" className="nav-link">Requirements</a>
          <a href="#apply" className="nav-link">Apply</a>
          <a href="#contact" className="nav-link">Contact</a>
          <button
            className={`mode-toggle ${mode === "Safe" ? "mode-safe" : "mode-unsafe"}`}
            onClick={toggleMode}
            title="Toggle between safe and unsafe AI mode"
          >
            {mode === "Safe" ? "✔ Safe Mode" : "⚠ Unsafe Mode"}
          </button>
        </nav>
      </header>

      {/* ── Hero ── */}
      <section className="hero" id="jobs">
        <div className="hero-content">
          <span className="job-badge">Now Hiring</span>
          <h1 className="hero-title">Senior Software Engineer</h1>
          <p className="hero-subtitle">
            Join our world-class engineering team and help shape the future of enterprise technology.
          </p>
          <div className="job-meta">
            <span className="meta-item"> San Francisco, CA &nbsp;(Hybrid)</span>
            <span className="meta-item">💼 Full-Time</span>
            <span className="meta-item"> $150k – $220k</span>
          </div>
          <a href="#apply" className="hero-cta">Apply Now →</a>
        </div>
      </section>

      {/* ── Main ── */}
      <main className="main-content">
        <div className="content-grid">

          {/* Job Details */}
          <section className="card job-details" id="requirements">
            <h2>Position Details</h2>
            <p className="section-desc">
              We're looking for an experienced engineer with a passion for building
              secure, scalable systems.
            </p>

            <h3>Required Skills</h3>
            <ul className="req-list">
              <li>Proficiency in <strong>Go</strong> and <strong>Node.js</strong></li>
              <li>Experience with <strong>PostgreSQL</strong></li>
              <li><strong>5+ years</strong> of software engineering experience</li>
              <li>Solid understanding of <strong>cybersecurity</strong> principles</li>
            </ul>

            <h3>Responsibilities</h3>
            <ul className="req-list">
              <li>Design and build scalable backend services</li>
              <li>Collaborate with product and design teams</li>
              <li>Lead code reviews and architecture discussions</li>
              <li>Champion security best practices across the stack</li>
            </ul>

            <div className={`mode-info ${mode === "Safe" ? "mode-info-safe" : "mode-info-unsafe"}`}>
              <p className="mode-info-label">
                {mode === "Safe" ? "✔ Safe AI Mode" : "⚠ Unsafe AI Mode"}
              </p>
              <p className="mode-info-desc">
                {mode === "Safe"
                  ? "Vulnerability detection/prevention is enabled. System and user prompts are separated for security."
                  : "No vulnerability detection/prevention. This version is vulnerable to attacks."}
              </p>
            </div>
          </section>

          {/* Application Form */}
          <section className="card application-section" id="apply">
            <h2>Submit Your Application</h2>
            <p className="section-desc">
              Paste your resume below. Our AI screening tool will evaluate whether
              your experience matches the role.
            </p>

            <form onSubmit={e => { e.preventDefault(); sendPost() }}>
              <label className="form-label" htmlFor="resume-input">
                Resume / CV <span className="form-hint">(plain text)</span>
              </label>
              <textarea
                id="resume-input"
                className="resume-textarea"
                placeholder="Paste your resume text here…"
                value={text}
                onChange={e => setText(e.target.value)}
                rows={13}
              />
              <button
                type="submit"
                className="submit-btn"
                disabled={loading || !text.trim()}
              >
                {loading ? "Evaluating…" : "Submit Application"}
              </button>

              {mode === "Unsafe" && (
                <button
                    type="button"
                    className="submit-btn poisoned-btn"
                    disabled={loading || !text.trim()}
                    onClick={sendPoisoned}
                  >
                    Submit Application (Poisoned) 
                </button>
                )}
            </form>

            {loading && (
              <div className="spinner-wrap">
                <Spinner />
                <span className="spinner-label">AI is reviewing your resume…</span>
              </div>
            )}

            {result && !loading && (
              <div className={`result-card ${qualified ? "result-pass" : "result-fail"}`}>
                <div className="result-icon">{qualified ? "✓" : "✗"}</div>
                <div className="result-body">
                  <h3 className="result-title">
                    {qualified ? "Application Approved" : "Not Qualified"}
                  </h3>
                  <p className="result-msg">{resultStr}</p>
                </div>
              </div>
            )}

            {error && (
              <div className="error-card">
                <strong>Connection Error</strong>
                <p>{error}</p>
              </div>
              <div className="chatbot-card">
                <h3>Questions About Your Application?</h3>
                <p>
                  Our AI assistant can help you check your application status,
                  review feedback, and answer questions about your submission.
                </p>
                <button
                  className="chatbot-button"
                  onClick={() => setPage("sidChat")}
                >
                  Chat About Your Application →
                </button>
            </div>
            )}
          </section>

        </div>
      </main>

      {/* ── Footer ── */}
      <footer className="footer" id="contact">
        <div className="footer-grid">
          <div>
            <p className="footer-brand">TechCorp Careers</p>
            <p className="footer-copy">© 2025 TechCorp Inc. All rights reserved.</p>
          </div>
          <div>
            <p className="footer-heading">Contact</p>
            <p className="footer-text">careers@techcorp.example.com</p>
          </div>
          <div>
            <p className="footer-heading">OWASP GenAI Demo</p>
            <p className="footer-text">Educational security demonstration project.</p>
          </div>
        </div>
      </footer>

    </div>
  )
}

export default App
