import axios from 'axios'

const baseURL = import.meta.env.VITE_API_BASE_URL

if (!baseURL) {
  console.warn('VITE_API_BASE_URL is not set — API calls will fail. Check your .env file.')
}

export const apiClient = axios.create({ baseURL })
