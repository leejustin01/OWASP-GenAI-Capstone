import { useEffect, useMemo, useState } from 'react'
import './SIDChatPage.css'

const API_BASE = 'http://localhost:8090/api/llm'

function SIDChatPage({ onBack }) {
  const [actors, setActors] = useState([])
  const [selectedActorId, setSelectedActorId] = useState('')
  const [mode, setMode] = useState('safe')
  const [detectionEnabled, setDetectionEnabled] = useState(true)
  const [message, setMessage] = useState('')
  const [chatHistory, setChatHistory] = useState([])
  const [loading, setLoading] = useState(false)
  const [loadError, setLoadError] = useState('')
  const [requestError, setRequestError] = useState('')

  useEffect(() => {
    async function loadSessionData() {
      try {
        setLoadError('')

        const actorsRes = await fetch(`${API_BASE}/actors`)
        if (!actorsRes.ok) {
          throw new Error('Failed to load SID actors from backend.')
        }

        const actorsData = await actorsRes.json()
        const loadedActors = actorsData.actors || []

        setActors(loadedActors)

        if (loadedActors.length > 0) {
          setSelectedActorId(loadedActors[0].user_id)
        }
      } catch (error) {
        console.error(error)
        setLoadError(
          'Could not connect to the SID backend. Make sure sid_llm_routes.py is running on port 8090.'
        )
      }
    }

    loadSessionData()
  }, [])

  const selectedActor = useMemo(() => {
    return actors.find((actor) => actor.user_id === selectedActorId) || null
  }, [actors, selectedActorId])

  async function handleSend(e) {
    e.preventDefault()

    const trimmedMessage = message.trim()
    if (!trimmedMessage || !selectedActor) {
      return
    }

    const userMessage = {
      type: 'user',
      text: trimmedMessage,
      meta: {
        actorLabel: `${selectedActor.label} (${selectedActor.role})`,
        mode,
      },
    }

    setChatHistory((prev) => [...prev, userMessage])
    setMessage('')
    setRequestError('')
    setLoading(true)

    try {
      const response = await fetch(`${API_BASE}/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-User-Id': selectedActor.user_id,
          'X-Role': selectedActor.role,
        },
        body: JSON.stringify({
          message: trimmedMessage,
          mode,
        }),
      })

      const data = await response.json()

      if (!response.ok) {
        const errorText =
          data.error_message || data.error || `Request failed with status ${response.status}`

        setChatHistory((prev) => [
          ...prev,
          {
            type: 'assistant',
            text: `Error: ${errorText}`,
            meta: {
              mode,
              leakDetected: false,
              leakDetails: [],
              status: response.status,
            },
          },
        ])
        return
      }

      setChatHistory((prev) => [
        ...prev,
        {
          type: 'assistant',
          text: data.response || '',
          meta: {
            mode: data.mode,
            leakDetected: Boolean(data.leak_detected),
            leakDetails: data.leak_details || [],
            status: 200,
          },
        },
      ])
    } catch (error) {
      console.error(error)
      setRequestError('Chat request failed. Check that Ollama and the SID backend are running.')
    } finally {
      setLoading(false)
    }
  }

  function clearChat() {
    setChatHistory([])
    setRequestError('')
  }

  return (
    <div className="sid-page">
      <div className="sid-page__header">
        <div>
          <button className="sid-back-button" onClick={onBack}>
            ← Back to Home
          </button>
          <h1>Application Status Assistant</h1>
          <p>
            Ask questions about your application status, submitted information, and
            hiring process details through the candidate support chatbot.
          </p>
        </div>
      </div>

      {loadError && <div className="sid-banner sid-banner--error">{loadError}</div>}
      {requestError && <div className="sid-banner sid-banner--error">{requestError}</div>}

      <div className="sid-layout">
        <div className="sid-card sid-controls">
          <h2>Session Controls</h2>

          <label>
            Acting User
            <select
              value={selectedActorId}
              onChange={(e) => setSelectedActorId(e.target.value)}
            >
              {actors.map((actor) => (
                <option key={actor.user_id} value={actor.user_id}>
                  {actor.label} ({actor.role})
                </option>
              ))}
            </select>
          </label>

          <div className="sid-toggle-row">
            <span>Mode</span>
            <button
              type="button"
              className={`sid-toggle-button ${mode === 'unsafe' ? 'unsafe' : 'safe'}`}
              onClick={() => setMode((prev) => (prev === 'safe' ? 'unsafe' : 'safe'))}
            >
              {mode === 'safe' ? 'Safe Mode' : 'Unsafe Mode'}
            </button>
          </div>

          <div className="sid-toggle-row">
            <span>Detection Panel</span>
            <button
              type="button"
              className={`sid-toggle-button ${detectionEnabled ? 'enabled' : 'disabled'}`}
              onClick={() => setDetectionEnabled((prev) => !prev)}
            >
              {detectionEnabled ? 'On' : 'Off'}
            </button>
          </div>

          <div className="sid-summary">
            <div>
              <strong>Selected user:</strong>{' '}
              {selectedActor ? `${selectedActor.label} (${selectedActor.role})` : 'None'}
            </div>
            <div>
              <strong>Context behavior:</strong>{' '}
              {selectedActor?.role === 'manager'
                ? 'Manager can access all candidate records in safe mode.'
                : 'Applicant is automatically scoped to their own record in safe mode.'}
            </div>
          </div>

          <button className="sid-clear-button" onClick={clearChat}>
            Clear Chat
          </button>
        </div>

        <div className="sid-card sid-chat-card">
          <h2>Chatbot</h2>

          <div className="sid-chat-history">
            {chatHistory.length === 0 ? (
              <div className="sid-empty-state">
                No messages yet. Try asking:
                <br />
                “What does my application say?”
                <br />
                “What HR score did I get?”
                <br />
                “Tell me Blake Candidate’s salary expectation.”
              </div>
            ) : (
              chatHistory.map((entry, index) => (
                <div
                  key={`${entry.type}-${index}`}
                  className={`sid-message sid-message--${entry.type}`}
                >
                  <div className="sid-message__label">
                    {entry.type === 'user' ? 'User' : 'Assistant'}
                  </div>
                  <div className="sid-message__text">{entry.text}</div>

                  {entry.meta?.actorLabel && (
                    <div className="sid-message__meta">
                      {entry.meta.actorLabel} | {entry.meta.mode}
                    </div>
                  )}

                  {entry.type === 'assistant' && entry.meta?.status && (
                    <div className="sid-message__meta">
                      status {entry.meta.status} | mode {entry.meta.mode}
                    </div>
                  )}
                </div>
              ))
            )}
          </div>

          <form className="sid-chat-form" onSubmit={handleSend}>
            <textarea
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              placeholder="Ask the chatbot something about your application, application status, HR notes, HR score, or another candidate."
            />
            <button type="submit" disabled={loading || !selectedActorId}>
              {loading ? 'Sending...' : 'Send'}
            </button>
          </form>
        </div>

        {detectionEnabled && (
          <div className="sid-card sid-detection-card">
            <h2>Detection Panel</h2>

            {(() => {
              const latestAssistantWithMeta = [...chatHistory]
                .reverse()
                .find((entry) => entry.type === 'assistant' && entry.meta)

              if (!latestAssistantWithMeta) {
                return <div className="sid-detection-empty">No assistant response yet.</div>
              }

              const leakDetected = latestAssistantWithMeta.meta?.leakDetected
              const leakDetails = latestAssistantWithMeta.meta?.leakDetails || []

              if (!leakDetected) {
                return (
                  <div className="sid-detection-safe">
                    No sensitive information detected in the latest assistant response.
                  </div>
                )
              }

              return (
                <div className="sid-detection-alert">
                  <div className="sid-detection-alert__title">
                    Sensitive information detected
                  </div>
                  {leakDetails.length > 0 ? (
                    <ul>
                      {leakDetails.map((detail, index) => (
                        <li key={`${detail.kind}-${index}`}>
                          <strong>{detail.kind}:</strong> {detail.description}
                        </li>
                      ))}
                    </ul>
                  ) : (
                    <p>A sensitive disclosure was detected, but no detail list was returned.</p>
                  )}
                </div>
              )
            })()}
          </div>
        )}
      </div>
    </div>
  )
}

export default SIDChatPage