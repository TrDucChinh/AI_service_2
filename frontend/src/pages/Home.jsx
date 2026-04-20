import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { useQuery } from '@tanstack/react-query'
import { productsApi, PRODUCT_SERVICES, SERVICE_LABELS } from '../api/products'
import ProductCard from '../components/ProductCard'
import LoadingSpinner from '../components/LoadingSpinner'
import { ShoppingBag, Shield, Truck, Star } from 'lucide-react'

const FEATURED_SERVICE = 'laptop'

export default function Home() {
  const { data: featuredData, isLoading } = useQuery({
    queryKey: ['featured-products'],
    queryFn: () => productsApi.list(FEATURED_SERVICE, { page_size: 8, ordering: '-created_at' }),
    select: (res) => res.data,
  })

  const categories = PRODUCT_SERVICES.slice(0, 8)

  return (
    <div>
      {/* Hero */}
      <motion.section
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-gradient-to-r from-primary-700 to-primary-500 text-white py-20 px-4"
      >
        <div className="max-w-5xl mx-auto text-center">
          <h1 className="text-4xl md:text-5xl font-bold mb-4">The Best Tech, One Place</h1>
          <p className="text-lg text-primary-100 mb-8">Laptops, phones, cameras, peripherals — everything you need.</p>
          <div className="flex items-center justify-center gap-4">
            <Link to="/products" className="bg-white text-primary-700 px-6 py-3 rounded-lg font-semibold hover:bg-primary-50">
              Shop Now
            </Link>
            <Link to="/products/laptop" className="border border-white text-white px-6 py-3 rounded-lg font-semibold hover:bg-white/10">
              View Laptops
            </Link>
          </div>
        </div>
      </motion.section>

      {/* Features */}
      <section className="bg-white py-10 border-b border-gray-100">
        <div className="max-w-5xl mx-auto px-4 grid grid-cols-2 md:grid-cols-4 gap-6">
          {[
            { icon: Truck, text: 'Free Shipping over $50' },
            { icon: Shield, text: '2-Year Warranty' },
            { icon: ShoppingBag, text: 'Easy Returns' },
            { icon: Star, text: 'Top Rated Products' },
          ].map(({ icon: Icon, text }) => (
            <div key={text} className="flex flex-col items-center gap-2 text-center">
              <Icon className="text-primary-600" size={24} />
              <span className="text-sm font-medium text-gray-700">{text}</span>
            </div>
          ))}
        </div>
      </section>

      {/* Categories */}
      <section className="max-w-7xl mx-auto px-4 py-12">
        <h2 className="text-2xl font-bold text-gray-900 mb-6">Shop by Category</h2>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
          {categories.map((service) => (
            <motion.div key={service} whileHover={{ scale: 1.03 }} transition={{ duration: 0.15 }}>
              <Link
                to={`/products/${service}`}
                className="flex flex-col items-center justify-center bg-gradient-to-br from-primary-50 to-white border border-primary-100 rounded-xl p-6 h-28 hover:border-primary-300 transition-colors"
              >
                <span className="text-2xl mb-2">💻</span>
                <span className="text-sm font-semibold text-gray-800">{SERVICE_LABELS[service]}</span>
              </Link>
            </motion.div>
          ))}
        </div>
      </section>

      {/* Featured Products */}
      <section className="max-w-7xl mx-auto px-4 pb-16">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-bold text-gray-900">Featured Laptops</h2>
          <Link to="/products/laptop" className="text-primary-600 hover:underline text-sm font-medium">View all →</Link>
        </div>
        {isLoading ? (
          <LoadingSpinner />
        ) : (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
            {(featuredData?.results || []).slice(0, 8).map((product) => (
              <ProductCard key={product.id} product={product} service={FEATURED_SERVICE} />
            ))}
          </div>
        )}
      </section>
    </div>
  )
}
