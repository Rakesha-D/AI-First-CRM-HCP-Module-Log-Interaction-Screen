import React, { useState, useRef, useEffect } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { sendChatMessage, addMessage } from '../store/slices/chatSlice'

function ChatInterface() {
  const dispatch = useDispatch()
  const { messages, sessionId, loading } = useSelector((state) => state.chat)
  const [input, setInput] = useState('')
  const messagesEndRef = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSend = async () => {
    if (!input.trim() || loading) return

    const messageContent = input
    const userMessage = { role: 'user', content: messageContent }
    dispatch(addMessage(userMessage))
    setInput('')

    try {
      await dispatch(sendChatMessage({ sessionId, content: messageContent })).unwrap()
    } catch (error) {
      console.error('Failed to send message:', error)
      dispatch(addMessage({
        role: 'assistant',
        content: 'Sorry, I encountered an error processing your request. Please try again.',
      }))
    }
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <div className="log-card ai-assistant-card">
      <div className="ai-assistant-header">
        <div className="ai-icon" aria-hidden="true">AI</div>
        <div>
          <h3>AI Assistant</h3>
          <p>Log interaction via chat</p>
        </div>
      </div>

      <div className="chat-messages">
        {messages.length === 0 && (
          <button
            type="button"
            className="assistant-prompt"
            onClick={() => setInput('Met Dr. Smith, discussed Product X efficacy, positive sentiment, shared brochure.')}
          >
            Log interaction details here (e.g., "Met Dr. Smith, discussed Product X efficacy, positive sentiment, shared brochure") or ask for help.
          </button>
        )}

        {messages.map((msg, index) => (
          <div key={index} className={`chat-message ${msg.role}`}>
            <div className="chat-avatar">
              {msg.role === 'user' ? 'JR' : 'AI'}
            </div>
            <div className="chat-bubble">
              {msg.content}
            </div>
          </div>
        ))}

        {loading && (
          <div className="chat-message assistant">
            <div className="chat-avatar">AI</div>
            <div className="chat-bubble">
              <div className="spinner" />
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      <div className="chat-input-container">
        <input
          type="text"
          className="chat-input"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Describe interaction..."
          disabled={loading}
        />
        <button
          className="btn btn-primary chat-log-btn"
          onClick={handleSend}
          disabled={!input.trim() || loading}
        >
          {loading ? <span className="spinner" /> : 'Log'}
        </button>
      </div>
    </div>
  )
}

export default ChatInterface
