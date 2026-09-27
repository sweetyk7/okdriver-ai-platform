import axios from 'axios';

// Use the Vercel rewrite proxy in production to bypass ngrok warnings and CORS
const API = axios.create({
  baseURL: import.meta.env.PROD ? '/api' : 'http://127.0.0.1:8000',
});

export default API;
