import { Navigate } from 'react-router-dom'
import { useSelector } from 'react-redux'
import { selectIsAuthenticated, selectUserRole } from '../store/authSlice'

export default function AdminRoute({ children, staffOnly = false }) {
  const isAuthenticated = useSelector(selectIsAuthenticated)
  const role = useSelector(selectUserRole)
  if (!isAuthenticated) return <Navigate to="/login" replace />
  if (staffOnly && !['admin', 'staff'].includes(role)) return <Navigate to="/" replace />
  if (!staffOnly && role !== 'admin') return <Navigate to="/" replace />
  return children
}
