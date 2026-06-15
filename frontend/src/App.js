import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Sidebar     from './components/Sidebar'
import Overview    from './pages/Overview'
import Performance from './pages/Performance'
import BatchUpload from './pages/BatchUpload'
import History     from './pages/History'

export default function App() {
  return (
    <BrowserRouter>
      <div style={{ display: 'flex', minHeight: '100vh', fontFamily: 'system-ui, sans-serif' }}>

        {/* sidebar always visible on left */}
        <Sidebar />

        {/* page content on right — changes based on route */}
        <Routes>
          <Route path="/"            element={<Overview />}    />
          <Route path="/performance" element={<Performance />} />
          <Route path="/batch"       element={<BatchUpload />} />
          <Route path="/history"     element={<History />}     />
        </Routes>

      </div>
    </BrowserRouter>
  )
}