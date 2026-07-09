import React, { useEffect } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { fetchHCPs } from '../store/slices/hcpSlice'
import { createChatSession } from '../store/slices/chatSlice'
import InteractionForm from '../components/InteractionForm'
import ChatInterface from '../components/ChatInterface'

function LogInteraction() {
  const dispatch = useDispatch()
  
  const { items: hcps } = useSelector((state) => state.hcps)
  const { sessionId } = useSelector((state) => state.chat)

  useEffect(() => {
    dispatch(fetchHCPs({ skip: 0, limit: 100 }))
    if (!sessionId) {
      dispatch(createChatSession(1))
    }
  }, [dispatch, sessionId])
  return (
    <div className="log-page">
      <h1 className="log-page-title">Log HCP Interaction</h1>

      <div className="log-interaction-container">
        <div className="form-column">
          <InteractionForm hcps={hcps} />
        </div>

        <div className="chat-column">
          <ChatInterface />
        </div>
      </div>
    </div>
  )
}

export default LogInteraction
