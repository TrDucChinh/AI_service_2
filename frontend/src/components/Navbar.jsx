import { Link, useNavigate } from 'react-router-dom'
import { useSelector, useDispatch } from 'react-redux'
import { ShoppingCart, User, LogOut, Menu, Search } from 'lucide-react'
import { selectIsAuthenticated, selectCurrentUser, selectUserRole, logout } from '../store/authSlice'
import { selectCartCount } from '../store/cartSlice'
import { authApi } from '../api/auth'
import toast from 'react-hot-toast'
import { useState } from 'react'

export default function Navbar() {
  const dispatch = useDispatch()
  const navigate = useNavigate()
  const isAuthenticated = useSelector(selectIsAuthenticated)
  const user = useSelector(selectCurrentUser)
  const role = useSelector(selectUserRole)
  const cartCount = useSelector(selectCartCount)
  const [search, setSearch] = useState('')
  const [menuOpen, setMenuOpen] = useState(false)

  const handleLogout = async () => {
    try {
      const stored = JSON.parse(localStorage.getItem('auth') || '{}')
      await authApi.logout(stored.refreshToken)
    } catch {}
    dispatch(logout())
    navigate('/login')
    toast.success('Logged out successfully')
  }

  const handleSearch = (e) => {
    e.preventDefault()
    if (search.trim()) navigate(`/products?q=${encodeURIComponent(search.trim())}`)
  }

  return (
    <nav className="bg-white shadow-sm border-b border-gray-200 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          <Link to="/" className="text-xl font-bold text-primary-600">TechStore</Link>

          <form onSubmit={handleSearch} className="hidden md:flex items-center flex-1 max-w-md mx-8">
            <div className="relative w-full">
              <input
                type="text"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder="Search products..."
                className="w-full pl-4 pr-10 py-2 border border-gray-300 rounded-full text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
              />
              <button type="submit" className="absolute right-3 top-2.5 text-gray-400 hover:text-primary-600">
                <Search size={16} />
              </button>
            </div>
          </form>

          <div className="flex items-center gap-4">
            <Link to="/products" className="hidden md:block text-sm text-gray-600 hover:text-primary-600">Products</Link>

            {isAuthenticated && (
              <Link to="/cart" className="relative text-gray-600 hover:text-primary-600">
                <ShoppingCart size={22} />
                {cartCount > 0 && (
                  <span className="absolute -top-2 -right-2 bg-primary-600 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center">{cartCount}</span>
                )}
              </Link>
            )}

            {isAuthenticated ? (
              <div className="relative group">
                <button className="flex items-center gap-1 text-sm text-gray-700 hover:text-primary-600">
                  <User size={18} />
                  <span className="hidden md:block">{user?.username || 'Account'}</span>
                </button>
                <div className="absolute right-0 top-8 bg-white border border-gray-200 rounded-lg shadow-lg py-1 w-48 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all">
                  <Link to="/profile" className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-50">Profile</Link>
                  <Link to="/orders" className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-50">Order History</Link>
                  {role === 'admin' && <Link to="/admin" className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-50">Admin Dashboard</Link>}
                  {(role === 'admin' || role === 'staff') && <Link to="/staff/orders" className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-50">Staff Panel</Link>}
                  <button onClick={handleLogout} className="w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-gray-50 flex items-center gap-2">
                    <LogOut size={14} /> Logout
                  </button>
                </div>
              </div>
            ) : (
              <div className="flex items-center gap-2">
                <Link to="/login" className="text-sm text-gray-600 hover:text-primary-600">Login</Link>
                <Link to="/register" className="bg-primary-600 text-white text-sm px-3 py-1.5 rounded-lg hover:bg-primary-700">Sign Up</Link>
              </div>
            )}
          </div>
        </div>
      </div>
    </nav>
  )
}
