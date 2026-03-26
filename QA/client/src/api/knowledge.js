/**
 * Knowledge base management APIs
 */
import request from './index'

/** Get knowledge base list (paginated) */
export function getKBList(params) {
  return request.get('/knowledge_base/list', { params })
}

/** Get all knowledge bases (no pagination) */
export function getAllKB() {
  return request.get('/knowledge_base/all')
}

/** Create knowledge base */
export function createKB(data) {
  return request.post('/knowledge_base', data)
}

/** Update knowledge base */
export function updateKB(id, data) {
  return request.put(`/knowledge_base/${id}`, data)
}

/** Delete knowledge base */
export function deleteKB(id) {
  return request.delete(`/knowledge_base/${id}`)
}

