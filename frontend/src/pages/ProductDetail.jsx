import { useParams, Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { useDispatch, useSelector } from 'react-redux'
import { ShoppingCart, Star, Package, CheckCircle } from 'lucide-react'
import { productsApi } from '../api/products'
import { cartApi } from '../api/cart'
import api from '../api/axios'
import { selectIsAuthenticated } from '../store/authSlice'
import { incrementCount } from '../store/cartSlice'
import LoadingSpinner from '../components/LoadingSpinner'
import toast from 'react-hot-toast'
import { useState } from 'react'

export default function ProductDetail() {
  const { service, id } = useParams()
  const dispatch = useDispatch()
  const isAuthenticated = useSelector(selectIsAuthenticated)
  const [qty, setQty] = useState(1)
  const [activeImage, setActiveImage] = useState(0)

  const { data: product, isLoading } = useQuery({
    queryKey: ['product', service, id],
    queryFn: () => productsApi.get(service, id),
    select: (res) => res.data,
  })

  const { data: recommendations } = useQuery({
    queryKey: ['recommendations', service, id],
    queryFn: () => api.get(`/recommendations/?product_id=${id}&service=${service}&limit=4`),
    select: (res) => res.data?.results || [],
    enabled: !!product,
  })

  const handleAddToCart = async () => {
    if (!isAuthenticated) { toast.error('Please login first'); return }
    try {
      await cartApi.addItem({ product_id: product.id, product_service: service, quantity: qty, price: product.current_price || product.price })
      dispatch(incrementCount())
      toast.success(`${qty} item(s) added to cart!`)
    } catch { toast.error('Failed to add to cart') }
  }

  if (isLoading) return <LoadingSpinner />
  if (!product) return <p className="text-center py-12 text-red-500">Product not found.</p>

  const images = product.images?.length ? product.images : [{ image: `https://placehold.co/800x600?text=${encodeURIComponent(product.name)}`, alt_text: product.name }]
  const rating = product.rating?.average_rating

  return (
    <div className="max-w-6xl mx-auto px-4 py-10">
      <div className="grid md:grid-cols-2 gap-10">
        {/* Images */}
        <div>
          <div className="aspect-square bg-gray-100 rounded-xl overflow-hidden mb-3">
            <img src={images[activeImage]?.image} alt={product.name} className="w-full h-full object-cover" />
          </div>
          <div className="flex gap-2 overflow-x-auto pb-1">
            {images.map((img, i) => (
              <button key={i} onClick={() => setActiveImage(i)} className={`flex-shrink-0 w-16 h-16 rounded-lg overflow-hidden border-2 ${i === activeImage ? 'border-primary-500' : 'border-transparent'}`}>
                <img src={img.image} alt={img.alt_text} className="w-full h-full object-cover" />
              </button>
            ))}
          </div>
        </div>

        {/* Info */}
        <div className="space-y-4">
          <div>
            <p className="text-sm text-primary-600 font-medium">{product.brand?.name || product.brand_name}</p>
            <h1 className="text-2xl font-bold text-gray-900">{product.name}</h1>
          </div>

          {rating && (
            <div className="flex items-center gap-2">
              <div className="flex items-center gap-0.5">
                {[1,2,3,4,5].map(s => <Star key={s} size={16} className={s <= Math.round(rating) ? 'fill-yellow-400 text-yellow-400' : 'text-gray-300'} />)}
              </div>
              <span className="text-sm text-gray-600">{parseFloat(rating).toFixed(1)} ({product.rating?.total_reviews} reviews)</span>
            </div>
          )}

          <div className="flex items-baseline gap-3">
            <span className="text-3xl font-bold text-gray-900">${parseFloat(product.current_price || product.price).toFixed(2)}</span>
            {product.is_on_sale && <span className="text-lg text-gray-400 line-through">${parseFloat(product.price).toFixed(2)}</span>}
            {product.is_on_sale && <span className="bg-red-100 text-red-600 text-sm px-2 py-0.5 rounded-full">Sale</span>}
          </div>

          <p className="text-gray-600 text-sm leading-relaxed">{product.description}</p>

          <div className="flex items-center gap-2 text-sm">
            {product.stock > 0 ? (
              <><CheckCircle size={16} className="text-green-500" /><span className="text-green-600 font-medium">In Stock ({product.stock} available)</span></>
            ) : (
              <><Package size={16} className="text-red-400" /><span className="text-red-500">Out of Stock</span></>
            )}
          </div>

          {product.stock > 0 && (
            <div className="flex items-center gap-3">
              <div className="flex items-center border border-gray-300 rounded-lg overflow-hidden">
                <button onClick={() => setQty(q => Math.max(1, q - 1))} className="px-3 py-2 text-gray-600 hover:bg-gray-50">−</button>
                <span className="px-4 py-2 text-sm font-medium border-x border-gray-300">{qty}</span>
                <button onClick={() => setQty(q => Math.min(product.stock, q + 1))} className="px-3 py-2 text-gray-600 hover:bg-gray-50">+</button>
              </div>
              <button onClick={handleAddToCart} className="flex-1 bg-primary-600 hover:bg-primary-700 text-white py-2.5 rounded-lg font-semibold flex items-center justify-center gap-2">
                <ShoppingCart size={18} /> Add to Cart
              </button>
            </div>
          )}

          {/* Specs */}
          {product.specifications && Object.keys(product.specifications).length > 0 && (
            <div className="border-t border-gray-100 pt-4">
              <h3 className="font-semibold text-gray-900 mb-3">Specifications</h3>
              <dl className="grid grid-cols-2 gap-2">
                {Object.entries(product.specifications).map(([k, v]) => (
                  <div key={k} className="bg-gray-50 rounded-lg px-3 py-2">
                    <dt className="text-xs text-gray-500 capitalize">{k.replace(/_/g, ' ')}</dt>
                    <dd className="text-sm font-medium text-gray-900">{String(v)}</dd>
                  </div>
                ))}
              </dl>
            </div>
          )}
        </div>
      </div>

      {/* Reviews */}
      {product.reviews?.length > 0 && (
        <div className="mt-12">
          <h2 className="text-xl font-bold mb-6">Customer Reviews</h2>
          <div className="space-y-4">
            {product.reviews.slice(0, 5).map((review) => (
              <div key={review.id} className="bg-white border border-gray-200 rounded-xl p-4">
                <div className="flex items-center gap-3 mb-2">
                  <div className="flex gap-0.5">
                    {[1,2,3,4,5].map(s => <Star key={s} size={12} className={s <= review.rating ? 'fill-yellow-400 text-yellow-400' : 'text-gray-200'} />)}
                  </div>
                  <span className="text-sm font-medium">{review.user_name || `User #${review.user_id}`}</span>
                  {review.is_verified && <span className="text-xs bg-green-100 text-green-600 px-2 py-0.5 rounded-full">Verified</span>}
                </div>
                {review.title && <p className="font-medium text-sm mb-1">{review.title}</p>}
                <p className="text-sm text-gray-600">{review.body}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {recommendations?.length > 0 && (
        <div className="mt-12">
          <h2 className="text-xl font-bold mb-6">You May Also Like</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {recommendations.map((p) => (
              <Link key={p.id} to={`/products/${service}/${p.id}`} className="bg-white border border-gray-200 rounded-xl p-3 hover:shadow-md transition-shadow">
                <div className="aspect-square bg-gray-50 rounded-lg overflow-hidden mb-2">
                  <img
                    src={p.images?.[0]?.image || `https://placehold.co/400x400?text=${encodeURIComponent(p.name)}`}
                    alt={p.name}
                    className="w-full h-full object-cover"
                  />
                </div>
                <p className="text-sm font-medium text-gray-900 line-clamp-2">{p.name}</p>
                <p className="text-sm font-bold text-primary-600 mt-1">${parseFloat(p.current_price || p.price).toFixed(2)}</p>
              </Link>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
