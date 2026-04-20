import { useForm } from 'react-hook-form'
import { Link, useNavigate } from 'react-router-dom'
import { useDispatch } from 'react-redux'
import { authApi } from '../api/auth'
import { setCredentials } from '../store/authSlice'
import toast from 'react-hot-toast'
import { useState } from 'react'

export default function Register() {
  const { register, handleSubmit, watch, formState: { errors } } = useForm()
  const dispatch = useDispatch()
  const navigate = useNavigate()
  const [loading, setLoading] = useState(false)

  const onSubmit = async (data) => {
    setLoading(true)
    try {
      await authApi.register({ username: data.username, email: data.email, password: data.password, password2: data.confirmPassword })
      const loginRes = await authApi.login({ username: data.username, password: data.password })
      const { access, refresh, user } = loginRes.data
      dispatch(setCredentials({ user, accessToken: access, refreshToken: refresh }))
      toast.success('Account created!')
      navigate('/')
    } catch (err) {
      const errs = err.response?.data
      if (errs) {
        const msg = Object.values(errs).flat().join(', ')
        toast.error(msg || 'Registration failed')
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-[80vh] flex items-center justify-center px-4">
      <div className="bg-white rounded-2xl shadow-lg p-8 w-full max-w-md">
        <h1 className="text-2xl font-bold text-gray-900 mb-2">Create account</h1>
        <p className="text-gray-500 text-sm mb-6">Join TechStore today</p>
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          {[
            { name: 'username', label: 'Username', type: 'text', rules: { required: 'Required', minLength: { value: 3, message: 'Min 3 characters' } } },
            { name: 'email', label: 'Email', type: 'email', rules: { required: 'Required', pattern: { value: /\S+@\S+\.\S+/, message: 'Invalid email' } } },
            { name: 'password', label: 'Password', type: 'password', rules: { required: 'Required', minLength: { value: 8, message: 'Min 8 characters' } } },
            { name: 'confirmPassword', label: 'Confirm Password', type: 'password', rules: { required: 'Required', validate: v => v === watch('password') || 'Passwords do not match' } },
          ].map(({ name, label, type, rules }) => (
            <div key={name}>
              <label className="block text-sm font-medium text-gray-700 mb-1">{label}</label>
              <input type={type} {...register(name, rules)} className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500" />
              {errors[name] && <p className="text-red-500 text-xs mt-1">{errors[name].message}</p>}
            </div>
          ))}
          <button type="submit" disabled={loading} className="w-full bg-primary-600 hover:bg-primary-700 text-white py-2.5 rounded-lg font-semibold text-sm disabled:opacity-50">
            {loading ? 'Creating...' : 'Create Account'}
          </button>
        </form>
        <p className="text-center text-sm text-gray-500 mt-6">
          Already have an account? <Link to="/login" className="text-primary-600 font-medium hover:underline">Sign in</Link>
        </p>
      </div>
    </div>
  )
}
