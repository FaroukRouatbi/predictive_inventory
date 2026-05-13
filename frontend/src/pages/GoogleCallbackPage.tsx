import { useEffect, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

export default function GoogleCallbackPage() {
  const navigate = useNavigate()
  const { login } = useAuth()
  const handled = useRef(false)

  useEffect(() => {
    if (handled.current) return  // ← prevent double execution
    handled.current = true

    const params = new URLSearchParams(window.location.search)
    const token = params.get('access_token')

    if (token) {
      login(token)
      navigate('/')
    } else {
      navigate('/login')
    }
  }, [])

  return (
    <div className="min-h-screen bg-gray-950 flex items-center justify-center">
      <div className="text-center">
        <div className="w-8 h-8 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
        <p className="text-gray-400 text-sm">Completing sign in...</p>
      </div>
    </div>
  )
}