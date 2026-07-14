import { Navigate, Route, Routes } from 'react-router-dom'
import BookingPage from './pages/BookingPage'
import AppointmentConfirmationPage from './pages/AppointmentConfirmationPage'

function App() {
  return (
    <Routes>
      <Route path="/" element={<Navigate to="/book" replace />} />
      <Route path="/book" element={<BookingPage />} />
      <Route path="/appointments/:id/confirmation" element={<AppointmentConfirmationPage />} />
    </Routes>
  )
}

export default App
