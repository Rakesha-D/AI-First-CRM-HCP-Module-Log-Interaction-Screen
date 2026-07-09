import { createSlice, createAsyncThunk } from '@reduxjs/toolkit'
import api from '../../services/api'

export const sendChatMessage = createAsyncThunk(
  'chat/sendMessage',
  async ({ sessionId, content }, thunkAPI) => {
    const state = thunkAPI.getState()
    const currentDraft = state.interactions.current || {}

    if (sessionId) {
      try {
        await api.post('/chat/messages', {
          session_id: sessionId,
          role: 'user',
          content,
        })
      } catch (error) {
        console.warn('Skipping chat message persistence:', error)
      }
    }

    // Update the read-only interaction draft through the AI Assistant API.
    const aiResponse = await api.post('/ai/interaction-draft/update', {
      message: content,
      current_draft: currentDraft,
    })

    // Save assistant message
    if (sessionId) {
      try {
        await api.post('/chat/messages', {
          session_id: sessionId,
          role: 'assistant',
          content: aiResponse.data.message,
        })
      } catch (error) {
        console.warn('Skipping assistant message persistence:', error)
      }
    }

    if (aiResponse.data.updated_draft) {
      thunkAPI.dispatch({
        type: 'interactions/setCurrentInteraction',
        payload: aiResponse.data.updated_draft,
      })
    }

    return {
      role: 'assistant',
      content: aiResponse.data.message,
    }
  }
)

export const createChatSession = createAsyncThunk(
  'chat/createSession',
  async (userId = 1) => {
    const response = await api.post('/chat/sessions', { user_id: userId })
    return response.data
  }
)

export const fetchChatMessages = createAsyncThunk(
  'chat/fetchMessages',
  async (sessionId) => {
    const response = await api.get(`/chat/messages/${sessionId}`)
    return response.data
  }
)

const chatSlice = createSlice({
  name: 'chat',
  initialState: {
    messages: [],
    sessionId: null,
    loading: false,
    error: null,
  },
  reducers: {
    addMessage: (state, action) => {
      state.messages.push(action.payload)
    },
    clearMessages: (state) => {
      state.messages = []
    },
    setSessionId: (state, action) => {
      state.sessionId = action.payload
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(sendChatMessage.pending, (state) => {
        state.loading = true
      })
      .addCase(sendChatMessage.fulfilled, (state, action) => {
        state.loading = false
        state.messages.push(action.payload)
      })
      .addCase(sendChatMessage.rejected, (state, action) => {
        state.loading = false
        state.error = action.error.message
      })
      .addCase(createChatSession.fulfilled, (state, action) => {
        state.sessionId = action.payload.id
      })
      .addCase(fetchChatMessages.fulfilled, (state, action) => {
        state.messages = action.payload
      })
  },
})

export const { addMessage, clearMessages, setSessionId } = chatSlice.actions
export default chatSlice.reducer
