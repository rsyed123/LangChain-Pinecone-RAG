import { useState, useEffect } from 'react'
import Login from './components/Login'
import Chat from './components/Chat'

const API_URL = 'http://localhost:8000'

function App() {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetch(`${API_URL}/auth/me`, { credentials: 'include' })
      .then(res => (res.ok ? res.json() : null))
      .then(data => { setUser(data); setLoading(false) })
      .catch(() => setLoading(false))
  }, [])

  const handleLogout = () => {
    window.location.href = `${API_URL}/auth/logout`
  }

  if (loading) return <div className="loading">Loading...</div>

  return (
    <div className="app">
      {user
        ? <Chat user={user} onLogout={handleLogout} apiUrl={API_URL} />
        : <Login apiUrl={API_URL} />
      }
    </div>
  )
}

export default App
