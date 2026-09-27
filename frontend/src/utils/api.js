import axios from 'axios';

// Use the VITE_API_URL environment variable if it exists, otherwise fallback to local
const API = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000',
  headers: {
    'ngrok-skip-browser-warning': 'true'
  }
});

export default API;
