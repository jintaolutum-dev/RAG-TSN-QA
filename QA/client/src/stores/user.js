/**
 * User state management (Pinia)
 * Manages login state, user info, and token
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useUserStore = defineStore('user', () => {
  // User info
  const userInfo = ref(JSON.parse(localStorage.getItem('userInfo') || 'null'))
  // Token
  const token = ref(localStorage.getItem('token') || '')

  /** Whether logged in */
  const isLoggedIn = computed(() => !!token.value)

  /** Whether admin */
  const isAdmin = computed(() => userInfo.value?.role === 'admin')

  /**
   * Set login info
   * @param {Object} data - Object containing token and user
   */
  function setLoginInfo(data) {
    token.value = data.token
    userInfo.value = data.user
    localStorage.setItem('token', data.token)
    localStorage.setItem('userInfo', JSON.stringify(data.user))
  }

  /** Clear login info (logout) */
  function logout() {
    token.value = ''
    userInfo.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('userInfo')
  }

  return { userInfo, token, isLoggedIn, isAdmin, setLoginInfo, logout }
})

