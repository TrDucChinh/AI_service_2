import { createSlice } from '@reduxjs/toolkit'

const stored = JSON.parse(localStorage.getItem('auth') || 'null')

const authSlice = createSlice({
  name: 'auth',
  initialState: {
    user: stored?.user || null,
    accessToken: stored?.accessToken || null,
    isAuthenticated: !!stored?.accessToken,
  },
  reducers: {
    setCredentials(state, action) {
      const { user, accessToken, refreshToken } = action.payload
      state.user = user
      state.accessToken = accessToken
      state.isAuthenticated = true
      localStorage.setItem('auth', JSON.stringify({ user, accessToken, refreshToken }))
    },
    logout(state) {
      state.user = null
      state.accessToken = null
      state.isAuthenticated = false
      localStorage.removeItem('auth')
    },
    updateToken(state, action) {
      state.accessToken = action.payload
      const stored = JSON.parse(localStorage.getItem('auth') || '{}')
      localStorage.setItem('auth', JSON.stringify({ ...stored, accessToken: action.payload }))
    },
  },
})

export const { setCredentials, logout, updateToken } = authSlice.actions
export default authSlice.reducer

export const selectCurrentUser = (state) => state.auth.user
export const selectIsAuthenticated = (state) => state.auth.isAuthenticated
export const selectAccessToken = (state) => state.auth.accessToken
export const selectUserRole = (state) => state.auth.user?.role || 'customer'
