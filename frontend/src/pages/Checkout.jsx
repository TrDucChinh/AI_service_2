import { useForm } from 'react-hook-form'
import { useQuery } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { useState } from 'react'
import { cartApi } from '../api/cart'
import { ordersApi } from '../api/orders'
import LoadingSpinner from '../components/LoadingSpinner'
import toast from 'react-hot-toast'
import { CreditCard, Truck } from 'lucide-react'

export default function Checkout() {
  const navigate = useNavigate()
  const { register, handleSubmit, formState: { errors } } = useForm()
  const [paymentMethod, setPaymentMethod] = useState('CREDIT_CARD')
  const [submitting, setSubmitting] = useState(false)

  const { data: cart, isLoading } = useQuery({
    queryKey: ['cart'],
    queryFn: () => cartApi.get(),
    select: (res) => res.data,
  })

  const items = cart?.items || []
  const subtotal = items.reduce((sum, item) => sum + parseFloat(item.price) * item.quantity, 0)
  const shipping = subtotal >= 50 ? 0 : 5.99
  const total = subtotal + shipping

  const onSubmit = async (data) => {
    setSubmitting(true)
    try {
      const orderItems = items.map(item => ({
        product_id: item.product_id,
        product_service: item.product_service,
        quantity: item.quantity,
        unit_price: item.price,
      }))

      const shippingAddress = `${data.street}, ${data.city}, ${data.state} ${data.zip}, ${data.country}`

      const orderRes = await ordersApi.create({
        items: orderItems,
        shipping_address: shippingAddress,
        total_amount: total.toFixed(2),
      })

      const order = orderRes.data
      await ordersApi.initiatePayment({ order_id: order.id, method: paymentMethod, amount: total.toFixed(2) })

      await cartApi.clear()
      toast.success('Order placed successfully!')
      navigate('/orders')
    } catch (err) {
      toast.error(err.response?.data?.error || 'Failed to place order')
    } finally {
      setSubmitting(false)
    }
  }

  if (isLoading) return <LoadingSpinner />
  if (items.length === 0) { navigate('/cart'); return null }

  return (
    <div className="max-w-5xl mx-auto px-4 py-10">
      <h1 className="text-2xl font-bold mb-8">Checkout</h1>
      <div className="grid md:grid-cols-3 gap-8">
        <div className="md:col-span-2">
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
            <div className="bg-white border border-gray-200 rounded-xl p-6">
              <h2 className="font-bold mb-4 flex items-center gap-2"><Truck size={18} /> Shipping Address</h2>
              <div className="grid grid-cols-2 gap-4">
                {[
                  { name: 'street', label: 'Street Address', col: 2 },
                  { name: 'city', label: 'City' },
                  { name: 'state', label: 'State / Province' },
                  { name: 'zip', label: 'ZIP Code' },
                  { name: 'country', label: 'Country' },
                ].map(({ name, label, col }) => (
                  <div key={name} className={col === 2 ? 'col-span-2' : ''}>
                    <label className="block text-sm font-medium text-gray-700 mb-1">{label}</label>
                    <input {...register(name, { required: 'Required' })} className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500" />
                    {errors[name] && <p className="text-red-500 text-xs mt-1">{errors[name].message}</p>}
                  </div>
                ))}
              </div>
            </div>

            <div className="bg-white border border-gray-200 rounded-xl p-6">
              <h2 className="font-bold mb-4 flex items-center gap-2"><CreditCard size={18} /> Payment Method</h2>
              <div className="space-y-2">
                {[['CREDIT_CARD', 'Credit / Debit Card'], ['COD', 'Cash on Delivery'], ['BANK_TRANSFER', 'Bank Transfer']].map(([val, label]) => (
                  <label key={val} className={`flex items-center gap-3 p-3 border rounded-lg cursor-pointer transition-colors ${paymentMethod === val ? 'border-primary-500 bg-primary-50' : 'border-gray-200 hover:border-gray-300'}`}>
                    <input type="radio" value={val} checked={paymentMethod === val} onChange={() => setPaymentMethod(val)} className="text-primary-600" />
                    <span className="text-sm font-medium">{label}</span>
                  </label>
                ))}
              </div>
            </div>

            <button type="submit" disabled={submitting} className="w-full bg-primary-600 hover:bg-primary-700 text-white py-3 rounded-lg font-semibold disabled:opacity-50">
              {submitting ? 'Placing Order...' : `Place Order — $${total.toFixed(2)}`}
            </button>
          </form>
        </div>

        <div className="bg-white border border-gray-200 rounded-xl p-6 h-fit">
          <h2 className="font-bold mb-4">Order Summary</h2>
          <div className="space-y-2 text-sm mb-4 max-h-64 overflow-y-auto">
            {items.map(item => (
              <div key={item.id} className="flex justify-between">
                <span className="text-gray-600">Product #{item.product_id} × {item.quantity}</span>
                <span>${(parseFloat(item.price) * item.quantity).toFixed(2)}</span>
              </div>
            ))}
          </div>
          <div className="border-t pt-3 space-y-1 text-sm">
            <div className="flex justify-between"><span>Subtotal</span><span>${subtotal.toFixed(2)}</span></div>
            <div className="flex justify-between"><span>Shipping</span><span>{shipping === 0 ? 'Free' : `$${shipping}`}</span></div>
            <div className="flex justify-between font-bold text-base pt-1"><span>Total</span><span>${total.toFixed(2)}</span></div>
          </div>
        </div>
      </div>
    </div>
  )
}
