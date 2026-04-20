import { useState } from 'react'
import { useMutation, useQuery } from '@tanstack/react-query'
import { aiApi } from '../api/ai'

export default function AIInsights() {
  const [question, setQuestion] = useState('Product nao duoc click nhieu nhat?')

  const timelineQuery = useQuery({
    queryKey: ['ai-timeline'],
    queryFn: () => aiApi.getTimeline({ limit: 12 }).then((r) => r.data),
  })

  const predictionQuery = useQuery({
    queryKey: ['ai-predict-next-action'],
    queryFn: () => aiApi.predictNextAction({}).then((r) => r.data),
  })

  const chatMutation = useMutation({
    mutationFn: (q) => aiApi.askChatbot({ question: q }).then((r) => r.data),
  })

  const statusQuery = useQuery({
    queryKey: ['ai-status'],
    queryFn: () => aiApi.getStatus().then((r) => r.data),
  })

  return (
    <div className="max-w-6xl mx-auto px-4 py-8 space-y-8">
      <h1 className="text-2xl font-bold text-gray-900">AI Behavior Insights</h1>

      <section className="bg-white border rounded-xl p-5">
        <h2 className="font-semibold mb-3">Pipeline status</h2>
        {statusQuery.isLoading ? (
          <p>Loading status...</p>
        ) : (
          <div className="text-sm text-gray-700 space-y-1">
            <p>Neo4j connected: <b>{statusQuery.data?.neo4j_enabled ? 'yes' : 'no'}</b></p>
            <p>Trained model loaded: <b>{statusQuery.data?.inference?.using_trained_model ? 'yes' : 'no'}</b></p>
            <p>Chat generator mode: <b>{statusQuery.data?.chatbot?.llm_mode || 'fallback'}</b></p>
          </div>
        )}
      </section>

      <section className="bg-white border rounded-xl p-5">
        <h2 className="font-semibold mb-3">Realtime prediction</h2>
        {predictionQuery.isLoading ? (
          <p>Loading prediction...</p>
        ) : (
          <div className="text-sm text-gray-700 space-y-1">
            <p>Suggested next action: <b>{predictionQuery.data?.predicted_action || 'n/a'}</b></p>
            <p>Confidence: {predictionQuery.data?.confidence || 0}</p>
            <p>Model: {predictionQuery.data?.model_type || 'heuristic'}</p>
            <p>Trained model loaded: {predictionQuery.data?.using_trained_model ? 'yes' : 'no'}</p>
          </div>
        )}
      </section>

      <section className="bg-white border rounded-xl p-5">
        <h2 className="font-semibold mb-3">User behavior timeline</h2>
        {timelineQuery.isLoading ? (
          <p>Loading timeline...</p>
        ) : (
          <div className="space-y-2">
            {(timelineQuery.data?.events || []).map((event, idx) => (
              <div key={`${event.timestamp}-${idx}`} className="text-sm border-b pb-2 text-gray-700">
                <span className="font-medium">{event.action}</span> on product {event.product_id}
                <span className="text-gray-500 ml-2">{event.timestamp}</span>
              </div>
            ))}
          </div>
        )}
      </section>

      <section className="bg-white border rounded-xl p-5">
        <h2 className="font-semibold mb-3">Graph RAG chatbot</h2>
        <div className="flex gap-2 mb-3">
          <input
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            className="flex-1 border rounded-lg px-3 py-2"
          />
          <button onClick={() => chatMutation.mutate(question)} className="bg-primary-600 text-white px-4 py-2 rounded-lg">
            Ask
          </button>
        </div>
        {chatMutation.data && (
          <pre className="bg-gray-50 p-3 rounded-lg text-sm whitespace-pre-wrap">{chatMutation.data.answer}</pre>
        )}
      </section>
    </div>
  )
}
