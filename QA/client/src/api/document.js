/**
 * Document management APIs
 */
import request from './index'

/** Get document list (paginated) */
export function getDocList(params) {
  return request.get('/document/list', { params })
}

/** Upload document */
export function uploadDoc(data) {
  return request.post('/document/upload', data, {
    headers: { 'Content-Type': 'multipart/form-data' },
    timeout: 300000
  })
}

/** Delete document */
export function deleteDoc(id) {
  return request.delete(`/document/${id}`)
}

