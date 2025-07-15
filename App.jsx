import React, { useState, useEffect } from 'react';

// API configuration
const API_BASE_URL = import.meta.env.DEV ? '/api' : '/api';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import Navbar from './Navbar.jsx'
import Dashboard from './Dashboard.jsx'
import Chat from './Chat.jsx'
import Models from './Models.jsx'
import Training from './Training.jsx'
import DataIngestion from './DataIngestion.jsx'
import Settings from './Settings.jsx'
import Subscription from './Subscription.jsx'
import LoginPage from './LoginPage.jsx'

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    checkAuthStatus()
  }, [])

  const checkAuthStatus = async () => {
    const token = localStorage.getItem('access_token')
    if (token) {
      try {
        const response = await fetch('/api/v1/auth/me', {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        })

        if (response.ok) {
          const data = await response.json()
          setUser(data.user)
          setIsAuthenticated(true)
        } else {
          localStorage.removeItem('access_token')
        }
      } catch (error) {
        console.error('Auth check failed:', error)
        localStorage.removeItem('access_token')
      }
    }
    setLoading(false)
  }

  const handleLogin = (userData, token) => {
    setIsAuthenticated(true)
    setUser(userData)
    localStorage.setItem('access_token', token)
  }

  const handleLogout = () => {
    setIsAuthenticated(false)
    setUser(null)
    localStorage.removeItem('access_token')
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-indigo-600"></div>
      </div>
    )
  }

  return (
    <Router>
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
        {isAuthenticated ? (
          <>
            <Navbar user={user} onLogout={handleLogout} />
            <main className="container mx-auto px-4 py-8">
              <Routes>
                <Route path="/" element={<Dashboard />} />
                <Route path="/chat" element={<Chat />} />
                <Route path="/models" element={<Models />} />
                <Route path="/training" element={<Training />} />
                <Route path="/data" element={<DataIngestion />} />
                <Route path="/subscription" element={<Subscription />} />
                <Route path="/settings" element={<Settings />} />
                <Route path="*" element={<Navigate to="/" replace />} />
              </Routes>
            </main>
          </>
        ) : (
          <LoginPage onLogin={handleLogin} />
        )}
      </div>
    </Router>
  )
}

export default App