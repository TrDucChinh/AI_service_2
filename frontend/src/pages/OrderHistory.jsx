import { useQuery } from '@tanstack/react-query'
import { ordersApi } from '../api/orders'
import LoadingSpinner from '../components/LoadingSpinner'
import { Package, ChevronDown } from 'lucide-react'
import { useState } from 'react'

const STATUS_COLORS = {
  PENDING: 'bg-yellow-100 text-yellow-700',
  CONFIRMED: 'bg-blue-100 text-blue-700',
  PROCESSING: 'bg-purple-100 text-purple-700',
  SHIPPED: 'bg-indigo-100 text-indigo-700',
  DELIVERED: 'bg-green-100 text-green-700',
  CANCELLED: 'bg-red-100 text-red-700',
}

export default function OrderHistory() {
  const [expandedId, setExpandedId] = useState(null)

  const { data, isLoading } = useQuery({
    queryKey: ['orders'],
    queryFn: () => ordersApi.list(),
    select: (res) => res.data,
  })

  if (isLoading) return <LoadingSpinner />

  const orders = data?.results || data || []

  if (orders.length === 0) return (
    <div className="flex flex-col items-center justify-center py-24 gap-4">
      <Package size={64} className="text-gray-300" />
      <h2 className="text-xl font-bold text-gray-700">No orders yet</h2>
    </div>
  )

  return (
    <div className="max-w-4xl mx-auto px-4 py-10">
      <h1 className="text-2xl font-bold mb-6">Order History</h1>
      <div className="space-y-4">
        {orders.map((order) => (
          <div key={order.id} className="bg-white border border-gray-200 rounded-xl overflow-hidden">
            <div
              className="flex items-center justify-between p-4 cursor-pointer hover:bg-gray-50"
              onClick={() => setExpandedId(expandedId === order.id ? null : order.id)}
            >
              <div className="flex items-center gap-4">
                <Package size={20} className="text-gray-400" />
                <div>
                  <p className="font-medium text-sm">Order #{order.id}</p>
                  <p className="text-xs text-gray-500">{new Date(order.created_at).toLocaleDateString()}</p>
                </div>
              </div>
              <div className="flex items-center gap-4">
                <span className={`text-xs font-medium px-2.5 py-1 rounded-full ${STATUS_COLORS[order.status] || 'bg-gray-100 text-gray-600'}`}>{order.status}</span>
                <span className="font-bold text-sm">${parseFloat(order.total_amount).toFixed(2)}</span>
                <ChevronDown size={16} className={`text-gray-400 transition-transform ${expandedId === order.id ? 'rotate-180' : ''}`} />
              </div>
            </div>
            {expandedId === order.id && (
              <div className="border-t border-gray-100 p-4">
                <p className="text-xs text-gray-500 mb-3">Shipping to: {order.shipping_address}</p>
                <div className="space-y-2">
                  {(order.items || []).map((item, i) => (
                    <div key={i} className="flex justify-between text-sm">
                      <span className="text-gray-600">Product #{item.product_id} × {item.quantity}</span>
                      <span>${(parseFloat(item.unit_price) * item.quantity).toFixed(2)}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}
