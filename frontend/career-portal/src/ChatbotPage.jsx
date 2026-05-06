import { useState, useRef, useEffect } from 'react'
import './App.css'
import Spinner from './Spinner'

function ChatbotPage({ onNavigate, mode, toggleMode }) {
  // Chat Setup
  const [messages,    setMessages]    = useState([
    { role: "bot", text: "Hi! I'm the TechCorp HR assistant. Ask me anything about the Senior Software Engineer role." }
  ])
  const [chatInput,   setChatInput]   = useState("")
  const [chatLoading, setChatLoading] = useState(false)
  const messagesEndRef = useRef(null)

  //Theft Demo states
  const [extractLoading, setExtractLoading] = useState(false)
  const [verifyLoading,  setVerifyLoading]  = useState(false)
  const [extractResult,  setExtractResult]  = useState(null)
  const [verifyResult,   setVerifyResult]   = useState(null)
  const [demoError,      setDemoError]      = useState(null)
  const [chatLocked,     setChatLocked]     = useState(false)
  const [resetLoading,   setResetLoading]   = useState(false)

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages, chatLoading])

  // Chat functionality
  const chatBaseUrl = mode === "Safe" ? "http://localhost:8081" : "http://localhost:8080"

  async function sendChat() {
    const question = chatInput.trim()
    if (!question) return
    setMessages(prev => [...prev, { role: "user", text: question }])
    setChatInput("")
    setChatLoading(true)
    try {
      const res  = await fetch(`${chatBaseUrl}/chat`, {
        method:  "POST",
        headers: { "Content-Type": "application/json" },
        body:    JSON.stringify({ question }),
      })
      const body = await res.json()
      if (body.locked) setChatLocked(true)
      setMessages(prev => [...prev, { role: "bot", text: body.response ?? body.error ?? "No response." }])
    } catch {
      const serverFile = mode === "Safe" ? "hiring_server_safe_chatbot.py (port 8081)" : "hiring_server_unsafe_chatbot.py (port 8080)"
      setMessages(prev => [...prev, { role: "bot", text: `Could not reach the server. Make sure ${serverFile} is running.` }])
    }
    setChatLoading(false)
  }

  // Theft Demo functionality
  const demoPort = mode === "Safe" ? "8081" : "8080"

  async function runExtract() {
    setExtractLoading(true)
    setExtractResult(null)
    setVerifyResult(null)
    setDemoError(null)
    try {
      const res  = await fetch(`${chatBaseUrl}/extract`, { method: "POST" })
      const body = await res.json()
      if (body.blocked || (body.attempts != null && body.attempts >= 3)) setChatLocked(true)
      setExtractResult(body)
    } catch {
      setDemoError(`Could not reach the demo server on port ${demoPort}.`)
    }
    setExtractLoading(false)
  }

  async function runVerify() {
    setVerifyLoading(true)
    setVerifyResult(null)
    setDemoError(null)
    try {
      const res  = await fetch(`${chatBaseUrl}/verify`, { method: "POST" })
      const body = await res.json()
      if (body.blocked || (body.attempts != null && body.attempts >= 3)) setChatLocked(true)
      setVerifyResult(body)
    } catch {
      setDemoError(`Could not reach the demo server on port ${demoPort}.`)
    }
    setVerifyLoading(false)
  }

  async function runReset() {
    setResetLoading(true)
    try {
      await fetch(`${chatBaseUrl}/reset`, { method: "POST" })
      setChatLocked(false)
      setExtractResult(null)
      setVerifyResult(null)
      setDemoError(null)
    } catch {
      setDemoError(`Could not reach the demo server on port ${demoPort}.`)
    }
    setResetLoading(false)
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
            {mode === "Safe" ? "Safe Mode" : "Unsafe Mode"}
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
                {mode === "Safe" ? "Safe AI Mode" : "Unsafe AI Mode"}
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
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", gap: "0.75rem" }}>
              <h2 style={{ margin: 0 }}>Ask About Job Info</h2>
              {mode === "Safe" && (
                <button
                  onClick={runReset}
                  disabled={extractLoading || verifyLoading || resetLoading}
                  title="Clear the extraction tripwire and unlock the chatbot"
                  style={{
                    padding: "0.25rem 0.6rem",
                    fontSize: "0.75rem",
                    background: "#475569",
                    color: "#fff",
                    border: "none",
                    borderRadius: "4px",
                    cursor: "pointer",
                    lineHeight: 1.2,
                  }}
                >
                  {resetLoading ? "Resetting…" : "Reset"}
                </button>
              )}
            </div>
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

            {chatLocked && (
              <div className="error-card" style={{ marginBottom: "0.75rem" }}>
                <strong>Chatbot Locked</strong>
                <p>PyTorch state_dict tripwire fired 3 times. Chat is sealed until the extraction counter is reset.</p>
              </div>
            )}

            <form className="chat-input-row" onSubmit={e => { e.preventDefault(); sendChat() }}>
              <input
                className="chat-input"
                type="text"
                placeholder={chatLocked ? "Chatbot locked — reset to continue" : "Ask about the role…"}
                value={chatInput}
                onChange={e => setChatInput(e.target.value)}
                disabled={chatLoading || chatLocked}
              />
              <button
                type="submit"
                className="submit-btn chat-send-btn"
                disabled={chatLoading || chatLocked || !chatInput.trim()}
              >
                Send
              </button>
            </form>

            {/* ── Model Theft Demo ── */}
            <div className="chat-divider" />
            <h3>Model Theft Demo</h3>
            <p className="section-desc">
              <strong>Extract</strong> harvests input/output pairs from the live model. <strong>Verify</strong> re-runs the same
              queries and confirms the extraction is done well enough to train a proper clone.
              {mode === "Safe" && " In Safe Mode the server detects these calls, returns scrambled weights, and locks out the IP after repeated attempts."}
            </p>

            <div style={{ display: "flex", gap: "0.75rem", alignItems: "stretch" }}>
              <button
                className="submit-btn"
                style={{ marginTop: 0, flex: 1 }}
                onClick={runExtract}
                disabled={extractLoading || verifyLoading || resetLoading}
              >
                {extractLoading ? "Extracting…" : "Extract Model Outputs"}
              </button>
              <button
                className="submit-btn"
                style={{ marginTop: 0, flex: 1, background: "#7c3aed" }}
                onClick={runVerify}
                disabled={extractLoading || verifyLoading || resetLoading}
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
                    {extractResult.success
                      ? `Extracted ${extractResult.num_queries} query/response pairs`
                      : extractResult.blocked ? "Extraction Blocked — IP Locked"
                      : extractResult.detected ? "Extraction Blocked"
                      : "Extraction Failed"}
                  </h3>
                  <p className="result-msg">
                    {extractResult.success
                      ? `Saved at ${new Date(extractResult.timestamp).toLocaleTimeString()}. Run Verify to confirm stability.`
                      : [extractResult.alert, extractResult.explanation, extractResult.error].filter(Boolean).join(" ")}
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
                      {verifyResult.success
                        ? `Match Score: ${verifyResult.score}`
                        : verifyResult.blocked ? "Verification Blocked — IP Locked"
                        : verifyResult.detected ? "Verification Blocked"
                        : "Verification Failed"}
                    </h3>
                    <p className="result-msg">
                      {verifyResult.success
                        ? "Outputs are stable, this dataset could train an identical surrogate model."
                        : [verifyResult.alert, verifyResult.explanation, verifyResult.error].filter(Boolean).join(" ")}
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

            {mode === "Safe" && (
              <div className="mode-info mode-info-safe" style={{ marginTop: "1rem" }}>
                <p className="mode-info-label">Safe Mode Active — Model Theft Defenses</p>
                <p className="mode-info-desc">
                  <strong>1. Tripwire</strong>: PyTorch fires a hook every time .state_dict() is called.<br />
                  <strong>2. Lockout</strong>: after 3 attempts the chatbot seals until Reset is pressed.<br />
                  <strong>3. Scrambled weights</strong>: returned tensors are random noise, not real weights.
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
