/**
 * API Client for Ads Monkee Backend
 */
import axios from 'axios'

// API Configuration
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor for authentication
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('ads_monkee_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Clear invalid token
      localStorage.removeItem('ads_monkee_token')
      // Redirect to login (implement when auth is ready)
      console.warn('Authentication expired')
    }
    return Promise.reject(error)
  }
)

// API Types
export interface Client {
  id: number
  name: string
  slug: string
  status: string
  google_ads_customer_id: string
  google_ads_account_name: string | null
  ghl_location_id: string | null
  ghl_contact_id: string | null
  last_sync_at: string | null
  last_analysis_at: string | null
  created_at: string
  updated_at: string
}

export interface ReportGenerationResponse {
  success: boolean
  client_id: number
  file_path: string
  message: string
}

export interface GHLUploadResponse {
  success: boolean
  client_id: number
  contact_id: string
  upload_result: {
    success: boolean
    file_id: string
    file_url: string
    message: string
  }
  message: string
}

// API Functions
export const clientsAPI = {
  // Get all clients
  getClients: async (): Promise<Client[]> => {
    const response = await apiClient.get('/api/clients')
    return response.data
  },

  // Get specific client
  getClient: async (clientId: number): Promise<Client> => {
    const response = await apiClient.get(`/api/clients/${clientId}`)
    return response.data
  },
}

export const reportsAPI = {
  // Generate report for client
  generateReport: async (clientId: number): Promise<ReportGenerationResponse> => {
    const response = await apiClient.post(`/api/reports/generate/${clientId}`)
    return response.data
  },

  // Generate and upload report to GHL
  generateAndUploadReport: async (
    clientId: number,
    contactId: string,
    customField: string = 'ads_monkee_report'
  ): Promise<GHLUploadResponse> => {
    const response = await apiClient.post(`/api/reports/generate-and-upload/${clientId}`, {
      contact_id: contactId,
      custom_field: customField,
    })
    return response.data
  },
}

export const analysisAPI = {
  // Get analysis for client
  getAnalysis: async (clientId: number) => {
    const response = await apiClient.get(`/api/analysis/${clientId}`)
    return response.data
  },

  // Run new analysis
  runAnalysis: async (clientId: number) => {
    const response = await apiClient.post(`/api/analysis/run/${clientId}`)
    return response.data
  },
}

export default apiClient
