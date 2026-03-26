/**
 * Vue Router configuration
 * Defines page routes and navigation guards (access control)
 */
import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/Login.vue'),
    meta: { title: 'Login' }
  },
  {
    path: '/',
    component: () => import('../views/Layout.vue'),
    redirect: '/chat',
    children: [
      {
        path: 'home',
        name: 'Home',
        component: () => import('../views/Home.vue'),
        meta: { title: 'Home', requireAdmin: true }
      },
      {
        path: 'knowledge-base',
        name: 'KnowledgeBase',
        component: () => import('../views/KnowledgeBase.vue'),
        meta: { title: 'Knowledge Base Management', requireAdmin: true }
      },
      {
        path: 'document',
        name: 'Document',
        component: () => import('../views/Document.vue'),
        meta: { title: 'Document Management', requireAdmin: true }
      },
      {
        path: 'user-manage',
        name: 'UserManage',
        component: () => import('../views/UserManage.vue'),
        meta: { title: 'User Management', requireAdmin: true }
      },
      {
        path: 'chat',
        name: 'Chat',
        component: () => import('../views/Chat.vue'),
        meta: { title: 'Intelligent QA' }
      },
      {
        path: 'chat-history',
        name: 'ChatHistory',
        component: () => import('../views/ChatHistory.vue'),
        meta: { title: 'Chat History' }
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Global before guard: login and permission checks
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  const userInfo = JSON.parse(localStorage.getItem('userInfo') || 'null')

  // Not logged in and not on login page, redirect to login
  if (!token && to.path !== '/login') {
    return next('/login')
  }

  // Logged in and visiting login page, redirect to home
  if (token && to.path === '/login') {
    return next('/')
  }

  // Pages requiring admin permissions are inaccessible to regular users
  if (to.meta.requireAdmin && userInfo?.role !== 'admin') {
    return next('/chat')
  }

  // Set page title
  document.title = to.meta.title ? `${to.meta.title} - Enterprise Knowledge Base` : 'Enterprise Knowledge Base'
  next()
})

export default router

