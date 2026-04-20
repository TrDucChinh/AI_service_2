import { Link } from 'react-router-dom'
import { ShoppingCart, Star } from 'lucide-react'
import { motion } from 'framer-motion'
import { useDispatch, useSelector } from 'react-redux'
import { selectIsAuthenticated } from '../store/authSlice'
import { cartApi } from '../api/cart'
import { incrementCount } from '../store/cartSlice'
import toast from 'react-hot-toast'

export default function ProductCard({ product, service }) {
  const dispatch = useDispatch()
  const isAuthenticated = useSelector(selectIsAuthenticated)

  const handleAddToCart = async (e) => {
    e.preventDefault()
    if (!isAuthenticated) {
      toast.error('Please login to add items to cart')
      return
    }
    try {
      await cartApi.addItem({ product_id: product.id, product_service: service, quantity: 1, price: product.current_price || product.price })
      dispatch(incrementCount())
      toast.success('Added to cart!')
    } catch {
      toast.error('Failed to add to cart')
    }
  }

  const price = product.current_price || product.price
  const rating = product.rating?.average_rating

  return (
    <motion.div
      whileHover={{ y: -4, boxShadow: '0 10px 25px rgba(0,0,0,0.1)' }}
      transition={{ duration: 0.2 }}
      className="bg-white rounded-xl border border-gray-200 overflow-hidden group"
    >
      <Link to={`/products/${service}/${product.id}`}>
        <div className="aspect-square bg-gray-100 overflow-hidden">
          <img
            src={product.primary_image || `https://placehold.co/400x400?text=${encodeURIComponent(product.name)}`}
            alt={product.name}
            className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
          />
        </div>
        <div className="p-4">
          {product.is_on_sale && (
            <span className="text-xs bg-red-100 text-red-600 px-2 py-0.5 rounded-full font-medium">Sale</span>
          )}
          <h3 className="text-sm font-medium text-gray-900 mt-1 line-clamp-2">{product.name}</h3>
          <p className="text-xs text-gray-500 mt-0.5">{product.brand_name}</p>
          {rating && (
            <div className="flex items-center gap-1 mt-1">
              <Star size={12} className="fill-yellow-400 text-yellow-400" />
              <span className="text-xs text-gray-600">{parseFloat(rating).toFixed(1)}</span>
            </div>
          )}
          <div className="flex items-center gap-2 mt-2">
            <span className="text-base font-bold text-gray-900">${parseFloat(price).toFixed(2)}</span>
            {product.is_on_sale && product.price && (
              <span className="text-xs text-gray-400 line-through">${parseFloat(product.price).toFixed(2)}</span>
            )}
          </div>
        </div>
      </Link>
      <div className="px-4 pb-4">
        <button
          onClick={handleAddToCart}
          className="w-full bg-primary-600 hover:bg-primary-700 text-white text-sm py-2 rounded-lg flex items-center justify-center gap-2 transition-colors"
        >
          <ShoppingCart size={14} /> Add to Cart
        </button>
      </div>
    </motion.div>
  )
}
