import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { productsApi, PRODUCT_SERVICES, SERVICE_LABELS } from '../../api/products'
import LoadingSpinner from '../../components/LoadingSpinner'
import { Plus, Pencil, Trash2 } from 'lucide-react'

export default function ProductManagement() {
  const [service, setService] = useState('laptop')
  const [page, setPage] = useState(1)

  const { data, isLoading } = useQuery({
    queryKey: ['admin-products', service, page],
    queryFn: () => productsApi.list(service, { page, show_inactive: true }),
    select: (res) => res.data,
  })

  const products = data?.results || []

  return (
    <div className="max-w-7xl mx-auto px-4 py-10">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold">Product Management</h1>
        <button className="bg-primary-600 text-white text-sm px-4 py-2 rounded-lg hover:bg-primary-700 flex items-center gap-2">
          <Plus size={16} /> Add Product
        </button>
      </div>

      <div className="flex gap-2 mb-6 overflow-x-auto pb-2">
        {PRODUCT_SERVICES.map(s => (
          <button key={s} onClick={() => { setService(s); setPage(1) }} className={`flex-shrink-0 px-3 py-1.5 rounded-full text-xs font-medium transition-colors ${s === service ? 'bg-primary-600 text-white' : 'bg-white border border-gray-300 text-gray-600 hover:border-primary-300'}`}>
            {SERVICE_LABELS[s]}
          </button>
        ))}
      </div>

      {isLoading ? <LoadingSpinner /> : (
        <div className="bg-white border border-gray-200 rounded-xl overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-gray-50">
              <tr>
                {['ID', 'Name', 'SKU', 'Brand', 'Price', 'Stock', 'Active', 'Actions'].map(h => (
                  <th key={h} className="text-left px-4 py-3 text-gray-500 font-medium text-xs uppercase tracking-wider">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {products.map(p => (
                <tr key={p.id} className="hover:bg-gray-50">
                  <td className="px-4 py-3 text-gray-500">#{p.id}</td>
                  <td className="px-4 py-3 font-medium max-w-xs truncate">{p.name}</td>
                  <td className="px-4 py-3 font-mono text-xs text-gray-500">{p.sku}</td>
                  <td className="px-4 py-3 text-gray-600">{p.brand_name}</td>
                  <td className="px-4 py-3 font-medium">${parseFloat(p.current_price || p.price).toFixed(2)}</td>
                  <td className="px-4 py-3">{p.stock}</td>
                  <td className="px-4 py-3">
                    <span className={`text-xs px-2 py-0.5 rounded-full ${p.is_active ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-500'}`}>{p.is_active ? 'Active' : 'Inactive'}</span>
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-2">
                      <button className="text-blue-500 hover:text-blue-700"><Pencil size={14} /></button>
                      <button className="text-red-400 hover:text-red-600"><Trash2 size={14} /></button>
                    </div>
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
