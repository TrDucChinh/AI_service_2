import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useDispatch } from 'react-redux'
import { Link, useNavigate } from 'react-router-dom'
import { Trash2, Plus, Minus, ShoppingBag } from 'lucide-react'
import { cartApi } from '../api/cart'
import { setCart } from '../store/cartSlice'
import LoadingSpinner from '../components/LoadingSpinner'
import toast from 'react-hot-toast'

export default function Cart() {
  const dispatch = useDispatch()
  const navigate = useNavigate()
  const queryClient = useQueryClient()

  const { data: cart, isLoading } = useQuery({
    queryKey: ['cart'],
    queryFn: () => cartApi.get(),
    select: (res) => {
      dispatch(setCart({ items: res.data.items || [] }))
      return res.data
    },
  })

  const updateMutation = useMutation({
    mutationFn: ({ id, quantity }) => cartApi.updateItem(id, { quantity }),
    onSuccess: () => queryClient.invalidateQueries(['cart']),
  })

  const removeMutation = useMutation({
    mutationFn: (id) => cartApi.removeItem(id),
    onSuccess: () => { queryClient.invalidateQueries(['cart']); toast.success('Item removed') },
  })

  if (isLoading) return <LoadingSpinner />

  const items = cart?.items || []
  const subtotal = items.reduce((sum, item) => sum + parseFloat(item.price) * item.quantity, 0)

  if (items.length === 0) return (
    <div className="flex flex-col items-center justify-center py-24 gap-4">
      <ShoppingBag size={64} className="text-gray-300" />
      <h2 className="text-xl font-bold text-gray-700">Your cart is empty</h2>
      <Link to="/products" className="bg-primary-600 text-white px-6 py-2.5 rounded-lg hover:bg-primary-700">Start Shopping</Link>
    </div>
  )

  return (
    <div className="max-w-4xl mx-auto px-4 py-10">
      <h1 className="text-2xl font-bold mb-6">Shopping Cart ({items.length} items)</h1>
      <div className="grid md:grid-cols-3 gap-6">
        <div className="md:col-span-2 space-y-3">
          {items.map((item) => (
            <div key={item.id} className="bg-white border border-gray-200 rounded-xl p-4 flex items-center gap-4">
              <div className="w-20 h-20 bg-gray-100 rounded-lg flex-shrink-0 overflow-hidden">
                <img src={`https://placehold.co/200x200?text=${item.product_service}`} alt="" className="w-full h-full object-cover" />
              </div>
              <div className="flex-1 min-w-0">
                <p className="font-medium text-sm text-gray-900 truncate">Product #{item.product_id}</p>
                <p className="text-xs text-gray-500 capitalize">{item.product_service}</p>
                <p className="font-bold text-primary-600 mt-1">${parseFloat(item.price).toFixed(2)}</p>
              </div>
              <div className="flex items-center gap-2">
                <button onClick={() => updateMutation.mutate({ id: item.id, quantity: Math.max(1, item.quantity - 1) })} className="p-1 border rounded hover:bg-gray-50"><Minus size={14} /></button>
                <span className="w-8 text-center text-sm font-medium">{item.quantity}</span>
                <button onClick={() => updateMutation.mutate({ id: item.id, quantity: item.quantity + 1 })} className="p-1 border rounded hover:bg-gray-50"><Plus size={14} /></button>
              </div>
              <button onClick={() => removeMutation.mutate(item.id)} className="text-red-400 hover:text-red-600 p-1"><Trash2 size={16} /></button>
            </div>
          ))}
        </div>

        <div className="bg-white border border-gray-200 rounded-xl p-6 h-fit">
          <h2 className="font-bold text-lg mb-4">Order Summary</h2>
          <div className="space-y-2 text-sm mb-4">
            <div className="flex justify-between"><span>Subtotal</span><span>${subtotal.toFixed(2)}</span></div>
            <div className="flex justify-between"><span>Shipping</span><span className="text-green-600">{subtotal >= 50 ? 'Free' : '$5.99'}</span></div>
            <div className="border-t border-gray-100 pt-2 flex justify-between font-bold text-base">
              <span>Total</span>
              <span>${(subtotal + (subtotal >= 50 ? 0 : 5.99)).toFixed(2)}</span>
            </div>
          </div>
          <button onClick={() => navigate('/checkout')} className="w-full bg-primary-600 hover:bg-primary-700 text-white py-3 rounded-lg font-semibold">
            Proceed to Checkout
          </button>
        </div>
      </div>
    </div>
  )
}
