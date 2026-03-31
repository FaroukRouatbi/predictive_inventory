import { useState } from 'react'
import Sidebar from './components/Sidebar'
import InventoryPage from './pages/InventoryPage'
import ForecastPage from './pages/ForecastPage'
import AlertsPage from './pages/AlertsPage'

export type Page = 'inventory' | 'forecast' | 'alerts'

function App() {
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

export default App