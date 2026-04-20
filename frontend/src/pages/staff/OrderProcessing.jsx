import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import api from '../../api/axios'
import LoadingSpinner from '../../components/LoadingSpinner'
import toast from 'react-hot-toast'
import { ClipboardList } from 'lucide-react'

const NEXT_STATUS = {
  PENDING: 'CONFIRMED',
  CONFIRMED: 'PROCESSING',
  PROCESSING: 'SHIPPED',
  SHIPPED: 'DELIVERED',
}

const STATUS_COLORS = {
  PENDING: 'bg-yellow-100 text-yellow-700',
  CONFIRMED: 'bg-blue-100 text-blue-700',
  PROCESSING: 'bg-purple-100 text-purple-700',
  SHIPPED: 'bg-indigo-100 text-indigo-700',
  DELIVERED: 'bg-green-100 text-green-700',
  CANCELLED: 'bg-red-100 text-red-700',
}

export default function OrderProcessing() {
  const queryClient = useQueryClient()

  const { data, isLoading } = useQuery({
    queryKey: ['staff-orders'],
    queryFn: () => api.get('/orders/'),
    select: (res) => res.data,
  })

  const updateMutation = useMutation({
    mutationFn: ({ id, status }) => api.patch(`/orders/${id}/`, { status }),
    onSuccess: () => { queryClient.invalidateQueries(['staff-orders']); toast.success('Order status updated') },
    onError: () => toast.error('Failed to update order'),
  })

  if (isLoading) return <LoadingSpinner />

  const orders = (data?.results || data || []).filter(o => o.status !== 'DELIVERED' && o.status !== 'CANCELLED')

  return (
    <div className="max-w-7xl mx-auto px-4 py-10">
      <h1 className="text-2xl font-bold mb-6 flex items-center gap-2"><ClipboardList size={24} /> Order Processing</h1>
      <p className="text-sm text-gray-500 mb-6">{orders.length} active orders requiring action</p>

      <div className="space-y-3">
        {orders.map(order => (
          <div key={order.id} className="bg-white border border-gray-200 rounded-xl p-4 flex items-center justify-between gap-4">
            <div className="flex items-center gap-4">
              <div>
                <p className="font-medium text-sm">Order #{order.id}</p>
                <p className="text-xs text-gray-500">{new Date(order.created_at).toLocaleDateString()} · ${parseFloat(order.total_amount).toFixed(2)}</p>
              </div>
              <span className={`text-xs font-medium px-2.5 py-1 rounded-full ${STATUS_COLORS[order.status] || 'bg-gray-100 text-gray-600'}`}>{order.status}</span>
            </div>
            <div className="flex items-center gap-2">
              {NEXT_STATUS[order.status] && (
                <button
                  onClick={() => updateMutation.mutate({ id: order.id, status: NEXT_STATUS[order.status] })}
                  disabled={updateMutation.isPending}
                  className="bg-primary-600 text-white text-xs px-3 py-1.5 rounded-lg hover:bg-primary-700 disabled:opacity-50"
                >
                  Mark {NEXT_STATUS[order.status]}
                </button>
              )}
              <button
                onClick={() => updateMutation.mutate({ id: order.id, status: 'CANCELLED' })}
                disabled={updateMutation.isPending}
                className="border border-red-300 text-red-500 text-xs px-3 py-1.5 rounded-lg hover:bg-red-50 disabled:opacity-50"
              >
                Cancel
              </button>
            </div>
          </div>
        ))}
        {orders.length === 0 && <p className="text-center text-gray-500 py-12">No active orders to process.</p>}
      </div>
    </div>
  )
}
