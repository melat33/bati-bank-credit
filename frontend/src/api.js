const API_URL = 'http://192.168.3.113:8000'

// 1 — get all scored customers sorted by risk score
export const getAllCustomers = async () => {
  const response = await fetch(`${API_URL}/customers`)
  if (!response.ok) throw new Error('Failed to fetch customers')
  return await response.json()
}

// 2 — predict one customer and get SHAP explanation
export const predictCustomer = async (customerData) => {
  const response = await fetch(`${API_URL}/predict`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(customerData),
  })
  if (!response.ok) throw new Error('Prediction failed')
  return await response.json()
}

// 3 — upload CSV file and score all customers in batch
export const uploadBatch = async (file) => {
  const formData = new FormData()
  formData.append('file', file)
  const response = await fetch(`${API_URL}/batch`, {
    method: 'POST',
    body: formData,
    // do NOT set Content-Type header for FormData
    // browser sets it automatically with correct boundary
  })
  if (!response.ok) throw new Error('Batch upload failed')
  return await response.json()
}

// 4 — health check
export const checkHealth = async () => {
  const response = await fetch(`${API_URL}/health`)
  if (!response.ok) throw new Error('Health check failed')
  return await response.json()
}