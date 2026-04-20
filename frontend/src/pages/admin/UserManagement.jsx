import { useQuery } from '@tanstack/react-query'
import api from '../../api/axios'
import LoadingSpinner from '../../components/LoadingSpinner'
import { UserCheck, UserX } from 'lucide-react'

const ROLE_COLORS = { admin: 'bg-red-100 text-red-700', staff: 'bg-blue-100 text-blue-700', customer: 'bg-green-100 text-green-700' }

export default function UserManagement() {
  const { data, isLoading } = useQuery({
    queryKey: ['admin-users'],
    queryFn: () => api.get('/auth/users/'),
    select: (res) => res.data,
  })

  if (isLoading) return <LoadingSpinner />

  const users = data?.results || data || []

  return (
    <div className="max-w-7xl mx-auto px-4 py-10">
      <h1 className="text-2xl font-bold mb-6">User Management</h1>
      <div className="bg-white border border-gray-200 rounded-xl overflow-hidden">
        <div className="p-4 border-b border-gray-100 flex items-center justify-between">
          <span className="text-sm text-gray-500">{users.length} users total</span>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="bg-gray-50">
              <tr>
                {['ID', 'Username', 'Email', 'Role', 'Active', 'Joined'].map(h => (
                  <th key={h} className="text-left px-4 py-3 text-gray-500 font-medium text-xs uppercase tracking-wider">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {users.map(u => (
                <tr key={u.id} className="hover:bg-gray-50">
                  <td className="px-4 py-3 text-gray-500">#{u.id}</td>
                  <td className="px-4 py-3 font-medium">{u.username}</td>
                  <td className="px-4 py-3 text-gray-600">{u.email}</td>
                  <td className="px-4 py-3">
                    <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${ROLE_COLORS[u.role] || 'bg-gray-100 text-gray-600'}`}>{u.role || 'customer'}</span>
                  </td>
                  <td className="px-4 py-3">
                    {u.is_active ? <UserCheck size={16} className="text-green-500" /> : <UserX size={16} className="text-red-400" />}
                  </td>
                  <td className="px-4 py-3 text-gray-500">{new Date(u.date_joined).toLocaleDateString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
