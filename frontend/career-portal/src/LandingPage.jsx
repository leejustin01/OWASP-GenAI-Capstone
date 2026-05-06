function LandingPage({ onNavigate }) {
  const team = [
    { name: "Amit Guha",        vuln: "Model Theft",                  github: "https://github.com/AmitGuha04" },
    { name: "Justin Lee",       vuln: "Prompt Injection",             github: "https://github.com/leejustin01" },
    { name: "Ohm Thakor",       vuln: "Sensitive Information Disclosure", github: "https://github.com/ohmthakor" },
    { name: "Jackson Miller",   vuln: "Data & Model Poisoning",       github: "https://github.com/Jackson-David-Miller" },
    { name: "Jared Yin",        vuln: "Improper Output Handling",     github: "https://github.com/Jayrradical" },
  ]

  return (
    <div className="app">

      {/* Banner */}
      <header className="banner">
        <div className="banner-left">
          <div className="brand-icon">TC</div>
          <span className="brand-name">TechCorp Careers</span>
        </div>
        <nav className="banner-nav">
          <button className="nav-link" onClick={() => onNavigate("home")}>Try the Demo</button>
          <button className="nav-link" onClick={() => onNavigate("chatbot")}>Chatbot</button>
        </nav>
      </header>

      {/* Hero */}
      <section className="hero">
        <div className="hero-content">
          <span className="job-badge">OWASP GenAI Capstone 2025</span>
          <h1 className="hero-title">AI Security Showcase</h1>
          <p className="hero-subtitle">
            Hands-on analysis of five OWASP 2025 AI vulnerabilities with live safe vs. unsafe demos
            showing how real-world AI tools can be exploited and defended.
          </p>
          <button className="hero-cta" onClick={() => onNavigate("home")}>
            Try the Demo →
          </button>
        </div>
      </section>

      {/* Main */}
      <main className="main-content">
        <div style={{ maxWidth: "1100px", margin: "0 auto", display: "flex", flexDirection: "column", gap: "1.75rem" }}>

          {/* About + Features row */}
          <div className="content-grid">

            {/* About */}
            <section className="card">
              <h2>About This Project</h2>
              <p className="section-desc">
                This project analyzes prevention and mitigation strategies for five of the 2025 OWASP
                security vulnerabilities found in AI-powered applications.
              </p>
              <p className="section-desc" style={{ marginBottom: 0 }}>
                Proper knowledge of these vulnerabilities is critical as gaps in understanding can
                leave backdoors open for users worldwide to have their data stolen and exploited.
              </p>
            </section>

            {/* Features */}
            <section className="card">
              <h2>Key Features</h2>
              <ul className="req-list">
                <li>Upload a resume to an <strong>AI reviewer</strong></li>
                <li>Ask an <strong>AI chatbot</strong> about job details</li>
                <li>Toggle <strong>Safe / Unsafe mode</strong> to observe vulnerability differences live</li>
                <li>Extract model outputs and <strong>verify model theft</strong> success</li>
              </ul>
            </section>

          </div>

          {/* How to Access */}
          <section className="card">
            <h2>How to Try It</h2>
            <div className="content-grid" style={{ marginTop: "0.75rem" }}>
              <div>
                <h3>Access</h3>
                <p className="section-desc" style={{ marginBottom: 0 }}>
                  Click on the <strong>Try the Demo</strong> button, then use the <strong>Safe / Unsafe</strong> toggle in the
                  top-right of the banner to switch between protected and unprotected AI modes in real time.
                </p>
              </div>
              <div>
                <h3>Requirements</h3>
                <ul className="req-list">
                  <li>A web browser</li>
                  <li>An internet connection</li>
                  <li>No installs or accounts needed</li>
                </ul>
              </div>
            </div>
          </section>

          {/* Team */}
          <section className="card">
            <h2>Team Credits</h2>
            <p className="section-desc">Each member explored a distinct OWASP GenAI vulnerability.</p>
            <div className="team-grid">
              {team.map(member => (
                <div key={member.name} className="team-card">
                  <p className="team-name">{member.name}</p>
                  <p className="team-vuln">{member.vuln}</p>
                  <a className="team-link" href={member.github} target="_blank" rel="noreferrer">
                    GitHub →
                  </a>
                </div>
              ))}
            </div>
            <div style={{ marginTop: "1.5rem", paddingTop: "1.25rem", borderTop: "1px solid #e2e8f0" }}>
              <a
                className="submit-btn"
                href="https://forms.gle/SnbtBVeF8Ms6ggnZ7"
                target="_blank"
                rel="noreferrer"
                style={{ display: "inline-block", width: "auto", padding: "0.7rem 1.75rem", textDecoration: "none" }}
              >
                Give Feedback →
              </a>
            </div>
          </section>

        </div>
      </main>

      {/* Footer */}
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

export default LandingPage
