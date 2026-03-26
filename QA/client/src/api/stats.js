/**
 * Statistics APIs
 */
import request from './index'

/** Get dashboard overview */
export function getOverview() {
  return request.get('/stats/overview')
}

