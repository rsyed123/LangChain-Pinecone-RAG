import { useState, useRef, useEffect } from 'react'
import FlowerBackground from './FlowerBackground'

function Chat({ user, onLogout, apiUrl }) {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const bottomRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, loading])

  const sendMessage = async () => {
    if (!input.trim() || loading) return

    const userMsg = { role: 'user', content: input.trim() }
    const updated = [...messages, userMsg]
    setMessages(updated)
    setInput('')
    setLoading(true)

    try {
      const res = await fetch(`${apiUrl}/api/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ messages: updated }),
      })
      if (!res.ok) throw new Error('Request failed')
      const data = await res.json()
      setMessages([...updated, { role: 'assistant', content: data.response }])
    } catch {
      setMessages([...updated, { role: 'assistant', content: 'Something went wrong. Please try again.' }])
    } finally {
      setLoading(false)
    }
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  return (
    <div className="chat-container">
      <FlowerBackground />
      <header className="chat-header">
        <h1>Chatbot</h1>
        <div className="user-info">
          {user.picture && (
            <img src={user.picture} alt={user.name} className="avatar" referrerPolicy="no-referrer" />
          )}
          <span>{user.name || user.email}</span>
          <button onClick={onLogout} className="logout-btn">Sign out</button>
        </div>
      </header>

      <div className="messages">
        {messages.length === 0 && (
          <p className="empty-state">Ask me anything about the documents.</p>
        )}
        {messages.map((msg, i) => (
          <div key={i} className={`message ${msg.role}`}>
            <div className="message-content">{msg.content}</div>
          </div>
        ))}
        {loading && (
          <div className="message assistant">
            <div className="message-content typing">•••</div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      <div className="input-area">
        <textarea
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Type a message… (Enter to send)"
          rows={1}
          disabled={loading}
        />
        <button onClick={sendMessage} disabled={loading || !input.trim()}>
          Send
        </button>
      </div>
    </div>
  )
}

export default Chat
