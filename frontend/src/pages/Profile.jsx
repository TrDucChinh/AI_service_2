import { useForm } from 'react-hook-form'
import { useSelector } from 'react-redux'
import { selectCurrentUser } from '../store/authSlice'
import api from '../api/axios'
import { useQuery, useMutation } from '@tanstack/react-query'
import toast from 'react-hot-toast'
import { useState } from 'react'
import { User, MapPin } from 'lucide-react'

export default function Profile() {
  const user = useSelector(selectCurrentUser)
  const [activeTab, setActiveTab] = useState('profile')

  const { data: profile } = useQuery({
    queryKey: ['profile'],
    queryFn: () => api.get('/users/profile/'),
    select: (res) => res.data,
  })

  const { register, handleSubmit } = useForm({ values: profile })

  const updateMutation = useMutation({
    mutationFn: (data) => api.put('/users/profile/', data),
    onSuccess: () => toast.success('Profile updated!'),
    onError: () => toast.error('Failed to update profile'),
  })

  return (
    <div className="max-w-3xl mx-auto px-4 py-10">
      <h1 className="text-2xl font-bold mb-6">My Account</h1>
      <div className="flex gap-1 mb-6 bg-gray-100 p-1 rounded-lg w-fit">
        {[['profile', 'Profile', User], ['addresses', 'Addresses', MapPin]].map(([id, label, Icon]) => (
          <button key={id} onClick={() => setActiveTab(id)} className={`flex items-center gap-2 px-4 py-2 rounded-md text-sm font-medium transition-colors ${activeTab === id ? 'bg-white shadow-sm text-primary-600' : 'text-gray-600 hover:text-gray-900'}`}>
            <Icon size={14} />{label}
          </button>
        ))}
      </div>

      {activeTab === 'profile' && (
        <div className="bg-white border border-gray-200 rounded-xl p-6">
          <form onSubmit={handleSubmit(data => updateMutation.mutate(data))} className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              {[['first_name', 'First Name'], ['last_name', 'Last Name'], ['phone', 'Phone Number']].map(([name, label]) => (
                <div key={name} className={name === 'phone' ? 'col-span-2' : ''}>
                  <label className="block text-sm font-medium text-gray-700 mb-1">{label}</label>
                  <input {...register(name)} className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500" />
                </div>
              ))}
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Bio</label>
              <textarea {...register('bio')} rows={3} className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500" />
            </div>
            <div className="pt-2">
              <p className="text-xs text-gray-500 mb-4">Logged in as: <strong>{user?.email || user?.username}</strong></p>
              <button type="submit" disabled={updateMutation.isPending} className="bg-primary-600 text-white px-6 py-2 rounded-lg text-sm font-medium hover:bg-primary-700 disabled:opacity-50">
                {updateMutation.isPending ? 'Saving...' : 'Save Changes'}
              </button>
            </div>
          </form>
        </div>
      )}

      {activeTab === 'addresses' && (
        <div className="bg-white border border-gray-200 rounded-xl p-6">
          <p className="text-sm text-gray-500">Address management coming soon.</p>
        </div>
      )}
    </div>
  )
}
