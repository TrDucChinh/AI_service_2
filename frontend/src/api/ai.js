import api from './axios'

export const aiApi = {
  getStatus: () => api.get('/ai/status/'),
  getTimeline: (params = {}) => api.get('/ai/behavior/timeline/', { params }),
  predictNextAction: (payload = {}) => api.post('/ai/predict-next-action/', payload),
  askChatbot: (payload) => api.post('/ai/chat/', payload),
  ingestEvent: (payload) => api.post('/ai/behavior/event/', payload),
}

export const trackBehaviorEvent = async ({ productId, action, userId }) => {
  if (!productId || !action || !userId) return
  try {
    await aiApi.ingestEvent({
      user_id: userId,
      product_id: String(productId),
      action,
      timestamp: new Date().toISOString(),
    })
  } catch {
    // Tracking is best-effort and must not block user flows.
  }
}
