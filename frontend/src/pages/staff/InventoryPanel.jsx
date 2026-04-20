import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { productsApi, PRODUCT_SERVICES, SERVICE_LABELS } from '../../api/products'
import LoadingSpinner from '../../components/LoadingSpinner'
import { AlertTriangle, Package } from 'lucide-react'

export default function InventoryPanel() {
  const [service, setService] = useState('laptop')

  const { data, isLoading } = useQuery({
    queryKey: ['inventory', service],
    queryFn: () => productsApi.list(service, { show_inactive: true, page_size: 50 }),
    select: (res) => res.data,
  })

  const products = data?.results || []
  const lowStock = products.filter(p => p.stock <= 10)

  return (
    <div className="max-w-7xl mx-auto px-4 py-10">
      <h1 className="text-2xl font-bold mb-6 flex items-center gap-2"><Package size={24} /> Inventory Panel</h1>

      {lowStock.length > 0 && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-xl p-4 mb-6 flex items-start gap-3">
          <AlertTriangle size={18} className="text-yellow-600 mt-0.5" />
          <div>
            <p className="font-semibold text-yellow-800 text-sm">Low Stock Alert</p>
            <p className="text-yellow-700 text-xs mt-0.5">{lowStock.length} product(s) have ≤10 units remaining in {SERVICE_LABELS[service]}.</p>
          </div>
        </div>
      )}

      <div className="flex gap-2 mb-6 overflow-x-auto pb-2">
        {PRODUCT_SERVICES.map(s => (
          <button key={s} onClick={() => setService(s)} className={`flex-shrink-0 px-3 py-1.5 rounded-full text-xs font-medium transition-colors ${s === service ? 'bg-primary-600 text-white' : 'bg-white border border-gray-300 text-gray-600 hover:border-primary-300'}`}>
            {SERVICE_LABELS[s]}
          </button>
        ))}
      </div>

      {isLoading ? <LoadingSpinner /> : (
        <div className="bg-white border border-gray-200 rounded-xl overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-gray-50">
              <tr>
                {['Product', 'SKU', 'Price', 'In Stock', 'Status'].map(h => (
                  <th key={h} className="text-left px-4 py-3 text-gray-500 font-medium text-xs uppercase tracking-wider">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {products.map(p => (
                <tr key={p.id} className="hover:bg-gray-50">
                  <td className="px-4 py-3 font-medium max-w-xs truncate">{p.name}</td>
                  <td className="px-4 py-3 font-mono text-xs text-gray-500">{p.sku}</td>
                  <td className="px-4 py-3">${parseFloat(p.current_price || p.price).toFixed(2)}</td>
                  <td className="px-4 py-3">
                    <span className={`font-medium ${p.stock <= 5 ? 'text-red-600' : p.stock <= 10 ? 'text-yellow-600' : 'text-green-600'}`}>{p.stock}</span>
                  </td>
                  <td className="px-4 py-3">
                    {p.stock === 0 ? <span className="text-xs bg-red-100 text-red-600 px-2 py-0.5 rounded-full">Out of Stock</span>
                      : p.stock <= 10 ? <span className="text-xs bg-yellow-100 text-yellow-600 px-2 py-0.5 rounded-full">Low Stock</span>
                      : <span className="text-xs bg-green-100 text-green-600 px-2 py-0.5 rounded-full">In Stock</span>}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
