/**
 * QA chat APIs
 */
import request from './index'

/** Send question (RAG QA) */
export function askQuestion(data) {
  return request.post('/chat/ask', data, {
    timeout: 3600000
  })
}

/** Get chat history list */
export function getChatHistory(params) {
  return request.get('/chat/history', { params })
}

/** Get chat records for a specific session */
export function getSessionChats(sessionId) {
  return request.get(`/chat/session/${sessionId}`)
}

