import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { useState } from 'react'
import { AuthProvider } from './context/AuthContext'
import ProtectedRoute from './components/ProtectedRoute'
import Sidebar from './components/Sidebar'
import LoginPage from './pages/LoginPage'
import InventoryPage from './pages/InventoryPage'
import ForecastPage from './pages/ForecastPage'
import AlertsPage from './pages/AlertsPage'
import GoogleCallbackPage from './pages/GoogleCallbackPage'

export type Page = 'inventory' | 'forecast' | 'alerts'

function Dashboard() {
  const [currentPage, setCurrentPage] = useState<Page>('inventory')

  const renderPage = () => {
    switch (currentPage) {
      case 'inventory': return <InventoryPage />
      case 'forecast':  return <ForecastPage />
      case 'alerts':    return <AlertsPage />
    }
  }

  return (
    <div className="flex h-screen bg-gray-950 text-gray-100 overflow-hidden">
      <Sidebar currentPage={currentPage} onNavigate={setCurrentPage} />
      <main className="flex-1 overflow-y-auto p-8">
        {renderPage()}
      </main>
    </div>
  )
}

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route
            path="/"
            element={
              <ProtectedRoute>
                <Dashboard />
              </ProtectedRoute>
            }
          />
          <Route path="*" element={<Navigate to="/" replace />} />
          <Route path="/auth/google/callback" element={<GoogleCallbackPage />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  )
}

export default App