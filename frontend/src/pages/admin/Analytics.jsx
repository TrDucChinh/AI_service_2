import { useQuery } from '@tanstack/react-query'
import api from '../../api/axios'
import LoadingSpinner from '../../components/LoadingSpinner'

export default function Analytics() {
  const { data: orders, isLoading } = useQuery({
    queryKey: ['analytics-orders'],
    queryFn: () => api.get('/orders/'),
    select: (res) => res.data,
  })

  if (isLoading) return <LoadingSpinner />

  const orderList = orders?.results || orders || []
  const statusCounts = orderList.reduce((acc, o) => { acc[o.status] = (acc[o.status] || 0) + 1; return acc }, {})
  const totalRevenue = orderList.reduce((sum, o) => sum + parseFloat(o.total_amount || 0), 0)
  const avgOrderValue = orderList.length ? totalRevenue / orderList.length : 0

  const barMax = Math.max(...Object.values(statusCounts), 1)

  return (
    <div className="max-w-7xl mx-auto px-4 py-10">
      <h1 className="text-2xl font-bold mb-8">Analytics</h1>
      <div className="grid md:grid-cols-3 gap-6 mb-8">
        {[
          { label: 'Total Orders', value: orderList.length },
          { label: 'Total Revenue', value: `$${totalRevenue.toFixed(2)}` },
          { label: 'Avg Order Value', value: `$${avgOrderValue.toFixed(2)}` },
        ].map(({ label, value }) => (
          <div key={label} className="bg-white border border-gray-200 rounded-xl p-6">
            <p className="text-sm text-gray-500">{label}</p>
            <p className="text-3xl font-bold text-gray-900 mt-1">{value}</p>
          </div>
        ))}
      </div>

      <div className="bg-white border border-gray-200 rounded-xl p-6">
        <h2 className="font-bold mb-6">Orders by Status</h2>
        <div className="space-y-3">
          {Object.entries(statusCounts).map(([status, count]) => (
            <div key={status} className="flex items-center gap-4">
              <span className="w-24 text-sm text-gray-600 shrink-0">{status}</span>
              <div className="flex-1 bg-gray-100 rounded-full h-6 overflow-hidden">
                <div
                  className="bg-primary-500 h-full rounded-full flex items-center justify-end pr-2 text-xs text-white font-medium transition-all"
                  style={{ width: `${(count / barMax) * 100}%` }}
                >{count}</div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
