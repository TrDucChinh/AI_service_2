import { useQuery } from '@tanstack/react-query'
import api from '../../api/axios'
import LoadingSpinner from '../../components/LoadingSpinner'
import { Link } from 'react-router-dom'
import { Users, ShoppingBag, DollarSign, TrendingUp } from 'lucide-react'

export default function Dashboard() {
  const { data: orders, isLoading } = useQuery({
    queryKey: ['admin-orders'],
    queryFn: () => api.get('/orders/'),
    select: (res) => res.data,
  })

  if (isLoading) return <LoadingSpinner />

  const orderList = orders?.results || orders || []
  const totalRevenue = orderList.reduce((sum, o) => sum + parseFloat(o.total_amount || 0), 0)
  const pending = orderList.filter(o => o.status === 'PENDING').length
  const delivered = orderList.filter(o => o.status === 'DELIVERED').length

  const stats = [
    { label: 'Total Orders', value: orderList.length, icon: ShoppingBag, color: 'bg-blue-500' },
    { label: 'Total Revenue', value: `$${totalRevenue.toFixed(2)}`, icon: DollarSign, color: 'bg-green-500' },
    { label: 'Pending Orders', value: pending, icon: TrendingUp, color: 'bg-yellow-500' },
    { label: 'Delivered', value: delivered, icon: Users, color: 'bg-purple-500' },
  ]

  return (
    <div className="max-w-7xl mx-auto px-4 py-10">
      <div className="flex items-center justify-between mb-8">
        <h1 className="text-2xl font-bold">Admin Dashboard</h1>
        <div className="flex gap-3">
          <Link to="/admin/users" className="bg-white border border-gray-300 text-sm px-4 py-2 rounded-lg hover:bg-gray-50">Manage Users</Link>
          <Link to="/admin/products" className="bg-primary-600 text-white text-sm px-4 py-2 rounded-lg hover:bg-primary-700">Manage Products</Link>
        </div>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
        {stats.map(({ label, value, icon: Icon, color }) => (
          <div key={label} className="bg-white border border-gray-200 rounded-xl p-6">
            <div className={`${color} w-10 h-10 rounded-lg flex items-center justify-center mb-3`}>
              <Icon size={20} className="text-white" />
            </div>
            <p className="text-2xl font-bold text-gray-900">{value}</p>
            <p className="text-sm text-gray-500 mt-1">{label}</p>
          </div>
        ))}
      </div>

      <div className="bg-white border border-gray-200 rounded-xl p-6">
        <h2 className="font-bold mb-4">Recent Orders</h2>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-gray-100">
                <th className="text-left pb-3 text-gray-500 font-medium">Order ID</th>
                <th className="text-left pb-3 text-gray-500 font-medium">Status</th>
                <th className="text-left pb-3 text-gray-500 font-medium">Amount</th>
                <th className="text-left pb-3 text-gray-500 font-medium">Date</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-50">
              {orderList.slice(0, 10).map(order => (
                <tr key={order.id}>
                  <td className="py-3 font-mono text-xs">#{order.id}</td>
                  <td className="py-3"><span className="px-2 py-0.5 bg-gray-100 rounded text-xs">{order.status}</span></td>
                  <td className="py-3 font-medium">${parseFloat(order.total_amount).toFixed(2)}</td>
                  <td className="py-3 text-gray-500">{new Date(order.created_at).toLocaleDateString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
