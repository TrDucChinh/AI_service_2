import { useQuery } from '@tanstack/react-query'
import api from '../../api/axios'
import LoadingSpinner from '../../components/LoadingSpinner'
import { Warehouse, AlertTriangle, Package, TrendingDown } from 'lucide-react'

export default function InventoryDashboard() {
  const { data: aggregate, isLoading: aggLoading } = useQuery({
    queryKey: ['inventory-aggregate'],
    queryFn: () => api.get('/inventory/'),
    select: (res) => res.data,
    refetchInterval: 60000,
  })

  const { data: lowStock, isLoading: lowLoading } = useQuery({
    queryKey: ['inventory-low-stock'],
    queryFn: () => api.get('/inventory/low-stock/'),
    select: (res) => res.data,
    refetchInterval: 60000,
  })

  if (aggLoading || lowLoading) return <LoadingSpinner />

  const summary = aggregate?.summary || {}
  const services = aggregate?.services || {}
  const lowItems = lowStock?.results || []

  return (
    <div className="max-w-7xl mx-auto px-4 py-10">
      <h1 className="text-2xl font-bold mb-8 flex items-center gap-2"><Warehouse size={24} /> Inventory Dashboard</h1>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
        {[
          { label: 'Total Products', value: summary.total_products || 0, icon: Package, color: 'text-blue-600' },
          { label: 'Total Units', value: (summary.total_units || 0).toLocaleString(), icon: Warehouse, color: 'text-green-600' },
          { label: 'Out of Stock', value: summary.total_out_of_stock || 0, icon: TrendingDown, color: 'text-red-600' },
          { label: 'Low Stock', value: summary.total_low_stock || 0, icon: AlertTriangle, color: 'text-yellow-600' },
        ].map(({ label, value, icon: Icon, color }) => (
          <div key={label} className="bg-white border border-gray-200 rounded-xl p-5">
            <div className="flex items-center gap-2 mb-1">
              <Icon size={16} className={color} />
              <p className="text-xs text-gray-500">{label}</p>
            </div>
            <p className={`text-2xl font-bold ${color}`}>{value}</p>
          </div>
        ))}
      </div>

      <div className="grid md:grid-cols-2 gap-6">
        <div className="bg-white border border-gray-200 rounded-xl overflow-hidden">
          <div className="px-4 py-3 border-b border-gray-100 font-semibold text-sm">By Service</div>
          <table className="w-full text-sm">
            <thead className="bg-gray-50">
              <tr>
                {['Service', 'Products', 'In Stock', 'Low', 'Out'].map(h => (
                  <th key={h} className="text-left px-4 py-2 text-xs text-gray-500 font-medium">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {Object.entries(services).map(([name, stats]) => (
                <tr key={name} className="hover:bg-gray-50">
                  <td className="px-4 py-2 font-medium capitalize">{name}</td>
                  <td className="px-4 py-2">{stats.total_products}</td>
                  <td className="px-4 py-2 text-green-600">{stats.in_stock}</td>
                  <td className="px-4 py-2 text-yellow-600">{stats.low_stock}</td>
                  <td className="px-4 py-2 text-red-600">{stats.out_of_stock}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <div className="bg-white border border-gray-200 rounded-xl overflow-hidden">
          <div className="px-4 py-3 border-b border-gray-100 font-semibold text-sm flex items-center gap-2">
            <AlertTriangle size={14} className="text-yellow-500" /> Low Stock Items
          </div>
          <div className="overflow-y-auto max-h-80">
            {lowItems.length === 0 ? (
              <p className="text-center text-gray-400 py-8 text-sm">All products well stocked!</p>
            ) : (
              <table className="w-full text-sm">
                <thead className="bg-gray-50 sticky top-0">
                  <tr>
                    {['Product', 'Service', 'Stock'].map(h => (
                      <th key={h} className="text-left px-4 py-2 text-xs text-gray-500 font-medium">{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100">
                  {lowItems.map((item, i) => (
                    <tr key={i} className="hover:bg-gray-50">
                      <td className="px-4 py-2 max-w-xs truncate">{item.name}</td>
                      <td className="px-4 py-2 capitalize text-gray-500">{item.service}</td>
                      <td className="px-4 py-2">
                        <span className={`font-bold ${item.stock === 0 ? 'text-red-600' : 'text-yellow-600'}`}>{item.stock}</span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
