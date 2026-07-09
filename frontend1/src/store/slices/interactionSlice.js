import { createSlice, createAsyncThunk } from '@reduxjs/toolkit'
import api from '../../services/api'

// Async thunks
export const fetchInteractions = createAsyncThunk(
  'interactions/fetchAll',
  async ({ skip = 0, limit = 50, hcp_id = null }) => {
    const params = new URLSearchParams({ skip: skip.toString(), limit: limit.toString() })
    if (hcp_id) params.append('hcp_id', hcp_id.toString())
    const response = await api.get(`/interactions/?${params}`)
    return response.data
  }
)

export const createInteraction = createAsyncThunk(
  'interactions/create',
  async (interactionData) => {
    const response = await api.post('/interactions/', interactionData)
    return response.data
  }
)

export const updateInteraction = createAsyncThunk(
  'interactions/update',
  async ({ id, data }) => {
    const response = await api.put(`/interactions/${id}`, data)
    return response.data
  }
)

const interactionSlice = createSlice({
  name: 'interactions',
  initialState: {
    items: [],
    current: null,
    loading: false,
    error: null,
  },
  reducers: {
    setCurrentInteraction: (state, action) => {
      state.current = action.payload
    },
    clearCurrentInteraction: (state) => {
      state.current = null
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchInteractions.pending, (state) => {
        state.loading = true
      })
      .addCase(fetchInteractions.fulfilled, (state, action) => {
        state.loading = false
        state.items = action.payload
      })
      .addCase(fetchInteractions.rejected, (state, action) => {
        state.loading = false
        state.error = action.error.message
      })
      .addCase(createInteraction.fulfilled, (state, action) => {
        state.items.unshift(action.payload)
      })
      .addCase(updateInteraction.fulfilled, (state, action) => {
        const index = state.items.findIndex((i) => i.id === action.payload.id)
        if (index !== -1) {
          state.items[index] = action.payload
        }
        if (state.current?.id === action.payload.id) {
          state.current = action.payload
        }
      })
  },
})

export const { setCurrentInteraction, clearCurrentInteraction } = interactionSlice.actions
export default interactionSlice.reducer
