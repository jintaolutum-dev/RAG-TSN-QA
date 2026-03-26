/**
 * Axios instance configuration
 * Sets baseURL, request interceptor (auto token), and response interceptor (unified error handling)
 */
import axios from 'axios'
import { ElMessage } from 'element-plus'
import router from '../router'

// Create axios instance
const request = axios.create({
  baseURL: '/api',
  timeout: 60000
})

// Request interceptor: attach token automatically
request.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// Response interceptor: handle errors uniformly
request.interceptors.response.use(
  (response) => {
    const res = response.data
    if (res.code === 200) {
      return res
    }
    // Token expired or not logged in, redirect to login
    if (res.code === 401) {
      localStorage.removeItem('token')
      localStorage.removeItem('userInfo')
      router.push('/login')
      ElMessage.error(res.message || 'Session expired. Please log in again.')
      return Promise.reject(new Error(res.message))
    }
    ElMessage.error(res.message || 'Request failed')
    return Promise.reject(new Error(res.message))
  },
  (error) => {
    ElMessage.error(error.message || 'Network error')
    return Promise.reject(error)
  }
)

export default request

