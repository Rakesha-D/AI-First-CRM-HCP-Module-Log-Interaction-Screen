import { createSlice, createAsyncThunk } from '@reduxjs/toolkit'
import api from '../../services/api'

export const fetchHCPs = createAsyncThunk(
  'hcps/fetchAll',
  async ({ skip = 0, limit = 50, search = null }) => {
    const params = new URLSearchParams({ skip: skip.toString(), limit: limit.toString() })
    if (search) params.append('search', search)
    const response = await api.get(`/hcps/?${params}`)
    return response.data
  }
)

export const createHCP = createAsyncThunk(
  'hcps/create',
  async (hcpData) => {
    const response = await api.post('/hcps/', hcpData)
    return response.data
  }
)

const hcpSlice = createSlice({
  name: 'hcps',
  initialState: {
    items: [],
    current: null,
    loading: false,
    error: null,
  },
  reducers: {
    setCurrentHCP: (state, action) => {
      state.current = action.payload
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchHCPs.pending, (state) => {
        state.loading = true
      })
      .addCase(fetchHCPs.fulfilled, (state, action) => {
        state.loading = false
        state.items = action.payload
      })
      .addCase(fetchHCPs.rejected, (state, action) => {
        state.loading = false
        state.error = action.error.message
      })
      .addCase(createHCP.fulfilled, (state, action) => {
        state.items.push(action.payload)
      })
  },
})

export const { setCurrentHCP } = hcpSlice.actions
export default hcpSlice.reducer
