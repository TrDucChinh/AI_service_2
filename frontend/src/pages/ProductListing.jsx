import { useParams, useSearchParams } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { useState } from 'react'
import { productsApi, PRODUCT_SERVICES, SERVICE_LABELS } from '../api/products'
import ProductCard from '../components/ProductCard'
import LoadingSpinner from '../components/LoadingSpinner'
import { Search, SlidersHorizontal } from 'lucide-react'

export default function ProductListing() {
  const { service } = useParams()
  const [searchParams, setSearchParams] = useSearchParams()
  const [page, setPage] = useState(1)
  const activeService = service || 'laptop'
  const q = searchParams.get('q') || ''
  const [search, setSearch] = useState(q)
  const [minPrice, setMinPrice] = useState('')
  const [maxPrice, setMaxPrice] = useState('')

  const { data, isLoading, error } = useQuery({
    queryKey: ['products', activeService, page, q, minPrice, maxPrice],
    queryFn: () => productsApi.list(activeService, { page, search: q, min_price: minPrice || undefined, max_price: maxPrice || undefined }),
    select: (res) => res.data,
    keepPreviousData: true,
  })

  const handleSearch = (e) => {
    e.preventDefault()
    setSearchParams(search ? { q: search } : {})
    setPage(1)
  }

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      <div className="flex flex-col md:flex-row gap-6">
        {/* Sidebar */}
        <aside className="w-full md:w-56 flex-shrink-0">
          <h2 className="font-bold text-gray-900 mb-3">Categories</h2>
          <ul className="space-y-1">
            {PRODUCT_SERVICES.map(s => (
              <li key={s}>
                <a
                  href={`/products/${s}`}
                  className={`block px-3 py-2 rounded-lg text-sm transition-colors ${s === activeService ? 'bg-primary-600 text-white font-medium' : 'text-gray-700 hover:bg-gray-100'}`}
                >
                  {SERVICE_LABELS[s]}
                </a>
              </li>
            ))}
          </ul>

          <div className="mt-6">
            <h3 className="font-semibold text-gray-700 mb-3 flex items-center gap-2"><SlidersHorizontal size={14} /> Filters</h3>
            <div className="space-y-2">
              <input type="number" value={minPrice} onChange={e => setMinPrice(e.target.value)} placeholder="Min Price" className="w-full border border-gray-300 rounded px-3 py-1.5 text-sm" />
              <input type="number" value={maxPrice} onChange={e => setMaxPrice(e.target.value)} placeholder="Max Price" className="w-full border border-gray-300 rounded px-3 py-1.5 text-sm" />
              <button onClick={() => setPage(1)} className="w-full bg-primary-600 text-white text-sm py-1.5 rounded hover:bg-primary-700">Apply</button>
            </div>
          </div>
        </aside>

        {/* Main content */}
        <div className="flex-1">
          <div className="flex items-center justify-between mb-4">
            <h1 className="text-xl font-bold text-gray-900">{SERVICE_LABELS[activeService]}</h1>
            <form onSubmit={handleSearch} className="flex items-center gap-2">
              <input value={search} onChange={e => setSearch(e.target.value)} placeholder="Search..." className="border border-gray-300 rounded-lg px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 w-48" />
              <button type="submit" className="bg-primary-600 text-white p-2 rounded-lg hover:bg-primary-700"><Search size={14} /></button>
            </form>
          </div>

          {isLoading ? <LoadingSpinner /> : error ? (
            <p className="text-red-500 text-center py-12">Failed to load products. Please try again.</p>
          ) : (
            <>
              <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
                {(data?.results || []).map(p => <ProductCard key={p.id} product={p} service={activeService} />)}
              </div>
              {data?.results?.length === 0 && <p className="text-center text-gray-500 py-12">No products found.</p>}
              {data?.count > 20 && (
                <div className="flex justify-center gap-3 mt-8">
                  <button onClick={() => setPage(p => Math.max(1, p - 1))} disabled={page === 1} className="px-4 py-2 border rounded-lg text-sm disabled:opacity-40 hover:bg-gray-50">Previous</button>
                  <span className="px-4 py-2 text-sm text-gray-600">Page {page}</span>
                  <button onClick={() => setPage(p => p + 1)} disabled={!data?.next} className="px-4 py-2 border rounded-lg text-sm disabled:opacity-40 hover:bg-gray-50">Next</button>
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  )
}
