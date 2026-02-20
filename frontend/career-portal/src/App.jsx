import { useState } from 'react'
import './App.css'
import Spinner from './Spinner'

function App() {
  const [text, setText] = useState("")
  const [loading, setLoading] = useState(false)

  async function sendPost() {
    setLoading(true)
    const res = await fetch(
        "http://localhost:8080/evaluate",
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
    </>
  )
}

export default App
