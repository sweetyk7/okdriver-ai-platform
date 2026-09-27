import axios from 'axios';

const API = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000',
  headers: {
    'ngrok-skip-browser-warning': '69420'
  }
});

export default API;
