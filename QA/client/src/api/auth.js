/**
 * Authentication APIs
 */
import request from './index'

/** User login */
export function login(data) {
  return request.post('/auth/login', data)
}

/** Get current user info */
export function getUserInfo() {
  return request.get('/auth/info')
}

