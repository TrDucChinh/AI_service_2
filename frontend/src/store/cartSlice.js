import { createSlice } from '@reduxjs/toolkit'

const cartSlice = createSlice({
  name: 'cart',
  initialState: {
    items: [],
    totalItems: 0,
  },
  reducers: {
    setCart(state, action) {
      state.items = action.payload.items || []
      state.totalItems = state.items.reduce((sum, item) => sum + item.quantity, 0)
    },
    clearCart(state) {
      state.items = []
      state.totalItems = 0
    },
    incrementCount(state) {
      state.totalItems += 1
    },
    decrementCount(state) {
      state.totalItems = Math.max(0, state.totalItems - 1)
    },
  },
})

export const { setCart, clearCart, incrementCount, decrementCount } = cartSlice.actions
export default cartSlice.reducer

export const selectCartItems = (state) => state.cart.items
export const selectCartCount = (state) => state.cart.totalItems
