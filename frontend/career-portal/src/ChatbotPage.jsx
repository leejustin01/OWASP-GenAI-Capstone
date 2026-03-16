import { useState, useRef, useEffect } from 'react'
import './App.css'
import Spinner from './Spinner'

function ChatbotPage({ onNavigate, mode, toggleMode }) {
  // ── Chat state ──────────────────────────────────────────────────────────
  const [messages,    setMessages]    = useState([
    { role: "bot", text: "Hi! I'm the TechCorp HR assistant. Ask me anything about the Senior Software Engineer role." }
  ])
  const [chatInput,   setChatInput]   = useState("")
  const [chatLoading, setChatLoading] = useState(false)
  const messagesEndRef = useRef(null)

  // ── Theft demo state ────────────────────────────────────────────────────
  const [extractLoading, setExtractLoading] = useState(false)
  const [verifyLoading,  setVerifyLoading]  = useState(false)
  const [extractResult,  setExtractResult]  = useState(null)
  const [verifyResult,   setVerifyResult]   = useState(null)
  const [demoError,      setDemoError]      = useState(null)

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages, chatLoading])

  // ── Chat ────────────────────────────────────────────────────────────────
  async function sendChat() {
    const question = chatInput.trim()
    if (!question) return
    setMessages(prev => [...prev, { role: "user", text: question }])
    setChatInput("")
    setChatLoading(true)
    try {
      const res  = await fetch("http://localhost:8082/chat", {
        method:  "POST",
        headers: { "Content-Type": "application/json" },
        body:    JSON.stringify({ question }),
      })
      const body = await res.json()
      setMessages(prev => [...prev, { role: "bot", text: body.response ?? body.error ?? "No response." }])
    } catch {
      setMessages(prev => [...prev, { role: "bot", text: "Could not reach the server. Make sure hiring_server_unsafe_amit.py is running on port 8082." }])
    }
    setChatLoading(false)
  }

  // ── Theft demo ──────────────────────────────────────────────────────────
  async function runExtract() {
    setExtractLoading(true)
    setExtractResult(null)
    setVerifyResult(null)
    setDemoError(null)
    try {
      const res  = await fetch("http://localhost:8082/extract", { method: "POST" })
      const body = await res.json()
      setExtractResult(body)
    } catch {
      setDemoError("Could not reach the demo server on port 8082.")
    }
    setExtractLoading(false)
  }

  async function runVerify() {
    setVerifyLoading(true)
    setVerifyResult(null)
    setDemoError(null)
    try {
      const res  = await fetch("http://localhost:8082/verify", { method: "POST" })
      const body = await res.json()
      setVerifyResult(body)
    } catch {
      setDemoError("Could not reach the demo server on port 8082.")
    }
    setVerifyLoading(false)
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
          <button className="nav-link nav-link-active" onClick={() => onNavigate('chatbot')}>Job Info Chatbot</button>
          <button className="nav-link" onClick={() => onNavigate('home')}>Requirements</button>
          <button className="nav-link" onClick={() => onNavigate('home')}>Apply</button>
          <button className="nav-link" onClick={() => onNavigate('home')}>Contact</button>
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
      <section className="hero">
        <div className="hero-content">
          <span className="job-badge">AI Assistant</span>
          <h1 className="hero-title">Job Info Chatbot</h1>
          <p className="hero-subtitle">
            Ask our AI assistant anything about the Senior Software Engineer role,
            requirements, or the hiring process.
          </p>
        </div>
      </section>

      {/* ── Main ── */}
      <main className="main-content">
        <div className="content-grid" style={{ gridTemplateColumns: "1fr", maxWidth: "860px" }}>

          {/* Position Details */}
          <section className="card job-details">
            <h2>Position Details: Senior Software Engineer</h2>
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

          {/* Ask about job info */}
          <section className="card" id="chatbot">
            <h2>Ask About Job Info</h2>
            <p className="section-desc">
              Have questions about the role? Ask our AI assistant below.
            </p>

            {/* ── Chat UI ── */}
            <div className="chat-messages">
              {messages.map((msg, i) => (
                <div key={i} className={`chat-bubble chat-bubble-${msg.role}`}>
                  {msg.text}
                </div>
              ))}
              {chatLoading && (
                <div className="chat-bubble chat-bubble-bot chat-bubble-typing">
                  <Spinner size="small" /> Thinking…
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>

            <form className="chat-input-row" onSubmit={e => { e.preventDefault(); sendChat() }}>
              <input
                className="chat-input"
                type="text"
                placeholder="Ask about the role…"
                value={chatInput}
                onChange={e => setChatInput(e.target.value)}
                disabled={chatLoading}
              />
              <button
                type="submit"
                className="submit-btn chat-send-btn"
                disabled={chatLoading || !chatInput.trim()}
              >
                Send
              </button>
            </form>

            {/* ── Model Theft Demo (Unsafe only) ── */}
            {mode === "Unsafe" && (
              <>
                <div className="chat-divider" />
                <h3>Model Theft Demo</h3>
                <p className="section-desc">
                  In unsafe mode the model can be probed freely. <strong>Extract</strong> harvests
                  input/output pairs from the live model. <strong>Verify</strong> re-runs the same
                  probes and confirms the extraction is stable — enough to train a surrogate.
                </p>

                <div style={{ display: "flex", gap: "0.75rem" }}>
                  <button
                    className="submit-btn"
                    style={{ marginTop: 0, flex: 1 }}
                    onClick={runExtract}
                    disabled={extractLoading || verifyLoading}
                  >
                    {extractLoading ? "Extracting…" : "Extract Model Outputs"}
                  </button>
                  <button
                    className="submit-btn"
                    style={{ marginTop: 0, flex: 1, background: "#7c3aed" }}
                    onClick={runVerify}
                    disabled={extractLoading || verifyLoading}
                  >
                    {verifyLoading ? "Verifying…" : "Verify Theft"}
                  </button>
                </div>

                {(extractLoading || verifyLoading) && (
                  <div className="spinner-wrap">
                    <Spinner />
                    <span className="spinner-label">
                      {extractLoading ? "Probing model with extraction queries…" : "Re-running probes and comparing outputs…"}
                    </span>
                  </div>
                )}

                {demoError && (
                  <div className="error-card" style={{ marginTop: "1rem" }}>
                    <strong>Connection Error</strong>
                    <p>{demoError}</p>
                  </div>
                )}

                {extractResult && (
                  <div className={`result-card ${extractResult.success ? "result-pass" : "result-fail"}`} style={{ marginTop: "1rem" }}>
                    <div className="result-icon">{extractResult.success ? "✓" : "✗"}</div>
                    <div className="result-body">
                      <h3 className="result-title">
                        {extractResult.success ? `Extracted ${extractResult.num_queries} query/response pairs` : "Extraction Failed"}
                      </h3>
                      <p className="result-msg">
                        {extractResult.success
                          ? `Saved at ${new Date(extractResult.timestamp).toLocaleTimeString()}. Run Verify to confirm stability.`
                          : extractResult.error}
                      </p>
                    </div>
                  </div>
                )}

                {verifyResult && (
                  <div style={{ marginTop: "1rem" }}>
                    <div className={`result-card ${verifyResult.success ? "result-pass" : "result-fail"}`} style={{ marginTop: 0 }}>
                      <div className="result-icon">{verifyResult.success ? "✓" : "✗"}</div>
                      <div className="result-body">
                        <h3 className="result-title">
                          {verifyResult.success ? `Match Score: ${verifyResult.score}` : "Verification Failed"}
                        </h3>
                        <p className="result-msg">
                          {verifyResult.success
                            ? "Outputs are stable, this dataset could train an identical surrogate model."
                            : verifyResult.error}
                        </p>
                      </div>
                    </div>

                    {verifyResult.success && verifyResult.results && (
                      <div className="theft-results">
                        {verifyResult.results.map((r, i) => (
                          <div key={i} className="theft-row">
                            <p className="theft-prompt">
                              {r.prompt}
                              <span className={r.match ? "theft-match" : "theft-diff"}>
                                {r.match ? " ✓ Match" : " ✗ Diff"}
                              </span>
                            </p>
                            <p className="theft-line"><strong>Original:</strong> {r.original}</p>
                            <p className="theft-line"><strong>Clone:</strong>    {r.clone}</p>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                )}
              </>
            )}

            {mode === "Safe" && (
              <div className="mode-info mode-info-safe" style={{ marginTop: "1rem" }}>
                <p className="mode-info-label">Safe Mode Active</p>
                <p className="mode-info-desc">
                  Model theft demo is disabled. Switch to Unsafe Mode to see the attack.
                </p>
              </div>
            )}
          </section>

        </div>
      </main>

      {/* ── Footer ── */}
      <footer className="footer">
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

export default ChatbotPage
