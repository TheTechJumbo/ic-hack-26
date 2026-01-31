'use client'

import { useConversation } from '@11labs/react'
import { useState, useCallback } from 'react'

export default function TalkPage() {
  const [isConnecting, setIsConnecting] = useState(false)
  const [error, setError] = useState(null)

  const conversation = useConversation({
    onConnect: () => {
      console.log('Connected to ElevenLabs')
      setIsConnecting(false)
    },
    onDisconnect: () => {
      console.log('Disconnected from ElevenLabs')
    },
    onError: (error) => {
      console.error('Conversation error:', error)
      setError('Connection error. Please try again.')
      setIsConnecting(false)
    },
    onMessage: (message) => {
      console.log('Message:', message)
    },
  })

  const startConversation = useCallback(async () => {
    setIsConnecting(true)
    setError(null)

    try {
      // Request microphone permission
      await navigator.mediaDevices.getUserMedia({ audio: true })

      // Get signed URL from backend
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
      const res = await fetch(`${apiUrl}/api/conversation/start`, {
        method: 'POST',
      })

      if (!res.ok) {
        throw new Error('Failed to get conversation URL')
      }

      const data = await res.json()

      // Start the conversation session
      await conversation.startSession({
        signedUrl: data.signed_url,
      })
    } catch (err) {
      console.error('Failed to start conversation:', err)
      setError(err.message || 'Failed to start conversation')
      setIsConnecting(false)
    }
  }, [conversation])

  const endConversation = useCallback(async () => {
    await conversation.endSession()
  }, [conversation])

  const getStatusColor = () => {
    switch (conversation.status) {
      case 'connected':
        return 'bg-green-500'
      case 'connecting':
        return 'bg-yellow-500'
      default:
        return 'bg-gray-400'
    }
  }

  const getStatusText = () => {
    if (isConnecting) return 'Connecting...'
    switch (conversation.status) {
      case 'connected':
        return conversation.isSpeaking ? 'Kalm is speaking...' : 'Listening...'
      default:
        return 'Not connected'
    }
  }

  return (
    <main className="min-h-screen flex flex-col items-center justify-center p-4">
      <div className="max-w-md w-full">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-white mb-2">Talk to Kalm</h1>
          <p className="text-white/80 text-lg">
            Real-time voice support
          </p>
        </div>

        <div className="bg-white rounded-2xl shadow-xl p-8">
          {/* Status Indicator */}
          <div className="flex items-center justify-center gap-3 mb-8">
            <div className={`w-3 h-3 rounded-full ${getStatusColor()} ${conversation.status === 'connected' ? 'animate-pulse' : ''}`} />
            <span className="text-gray-600">{getStatusText()}</span>
          </div>

          {/* Visual Feedback */}
          {conversation.status === 'connected' && (
            <div className="flex justify-center mb-8">
              <div className={`w-24 h-24 rounded-full bg-gradient-to-r from-indigo-500 to-purple-500 flex items-center justify-center ${conversation.isSpeaking ? 'animate-pulse' : ''}`}>
                <svg
                  className="w-12 h-12 text-white"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  {conversation.isSpeaking ? (
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M15.536 8.464a5 5 0 010 7.072m2.828-9.9a9 9 0 010 12.728M5.586 15.536a5 5 0 001.414 1.414m2.828-9.9a9 9 0 012.828-2.828"
                    />
                  ) : (
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z"
                    />
                  )}
                </svg>
              </div>
            </div>
          )}

          {/* Error Message */}
          {error && (
            <div className="mb-6 p-4 bg-red-50 text-red-700 rounded-lg text-center">
              {error}
            </div>
          )}

          {/* Action Buttons */}
          {conversation.status !== 'connected' ? (
            <button
              onClick={startConversation}
              disabled={isConnecting}
              className="w-full py-4 px-4 bg-gradient-to-r from-indigo-500 to-purple-500 text-white font-semibold rounded-lg hover:opacity-90 transition-opacity disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isConnecting ? (
                <span className="flex items-center justify-center gap-2">
                  <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                    <circle
                      className="opacity-25"
                      cx="12"
                      cy="12"
                      r="10"
                      stroke="currentColor"
                      strokeWidth="4"
                      fill="none"
                    />
                    <path
                      className="opacity-75"
                      fill="currentColor"
                      d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                    />
                  </svg>
                  Connecting...
                </span>
              ) : (
                <span className="flex items-center justify-center gap-2">
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
                  </svg>
                  Start Conversation
                </span>
              )}
            </button>
          ) : (
            <button
              onClick={endConversation}
              className="w-full py-4 px-4 bg-red-500 text-white font-semibold rounded-lg hover:bg-red-600 transition-colors"
            >
              <span className="flex items-center justify-center gap-2">
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
                End Conversation
              </span>
            </button>
          )}

          <p className="text-center text-gray-500 text-sm mt-6">
            Speak freely - Kalm is here to listen and support you.
          </p>
        </div>

        <div className="text-center mt-6">
          <a
            href="/"
            className="text-white/60 hover:text-white text-sm"
          >
            ← Back to home
          </a>
        </div>
      </div>
    </main>
  )
}
