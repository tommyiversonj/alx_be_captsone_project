const API_BASE_URL = import.meta.env.VITE_API_BASE_URL

const TOKEN_STORAGE_KEY = 'inventory_api_token'

export function getToken() {
  return localStorage.getItem(TOKEN_STORAGE_KEY)
}

export function setToken(token) {
  localStorage.setItem(TOKEN_STORAGE_KEY, token)
}

export function clearToken() {
  localStorage.removeItem(TOKEN_STORAGE_KEY)
}

export class ApiError extends Error {
  constructor(message, status, data) {
    super(message)
    this.status = status
    this.data = data
  }
}

async function request(path, { method = 'GET', body, auth = true } = {}) {
  const headers = { 'Content-Type': 'application/json' }
  if (auth) {
    const token = getToken()
    if (token) headers.Authorization = `Token ${token}`
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    method,
    headers,
    body: body ? JSON.stringify(body) : undefined,
  })

  const isJson = response.headers.get('content-type')?.includes('application/json')
  const data = isJson ? await response.json() : null

  if (!response.ok) {
    const message = data?.detail || `Request failed with status ${response.status}`
    throw new ApiError(message, response.status, data)
  }

  return data
}

export const api = {
  login: (username, password) =>
    request('login/', { method: 'POST', body: { username, password }, auth: false }),

  listProducts: () => request('inventory/products/'),

  createSale: (items) => request('sales/', { method: 'POST', body: { items } }),
}
