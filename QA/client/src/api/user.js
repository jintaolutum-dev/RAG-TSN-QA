/**
 * User management APIs
 */
import request from './index'

/** Get user list (paginated) */
export function getUserList(params) {
  return request.get('/user/list', { params })
}

/** Create user */
export function createUser(data) {
  return request.post('/user', data)
}

/** Update user */
export function updateUser(id, data) {
  return request.put(`/user/${id}`, data)
}

