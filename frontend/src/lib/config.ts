export const API_BASE_URL = import.meta.env.PROD 
  ? '/api'  // Production API URL
  : 'http://localhost:8000/api';  // Development API URL
