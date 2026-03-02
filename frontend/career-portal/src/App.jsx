import { useState } from 'react'
import './App.css'
import Spinner from './Spinner'

function App() {
  const [text, setText] = useState("")
  const [loading, setLoading] = useState(false)
  const [ url, setUrl ] = useState("http://localhost:8080/evaluate")
  const [ mode, setMode ] = useState("Unsafe")

  const safeUrl = "http://localhost:8081/evaluate"
  const unsafeUrl = "http://localhost:8080/evaluate"

  async function sendPost() {
    setLoading(true)
    const res = await fetch(
        url,
        {
            method: "POST",
            body: JSON.stringify({
                "resume-text": text
            }),
            headers: { "Content-Type": "application/json" }
        }
    )
    const resBody = await res.json()
    console.log("== resBody:", resBody)
    setLoading(false)
  }

  return (
    <>
      <h1>Applicant Portal</h1>
      <form onSubmit={e => {
        e.preventDefault()
        sendPost()
      }}>
        <textarea placeholder="Enter resume text here..." value={text} onChange={e => setText(e.target.value)}></textarea>
        <input type="submit"/>
        {loading && <Spinner/>}
      </form>
      <button onClick={() => {
          if (mode === "Unsafe") {
            setMode("Safe")
            setUrl(safeUrl)
          } else {
            setMode("Unsafe")
            setUrl(unsafeUrl)
          }
        }}>{mode}</button>
    </>
  )
}

export default App
