<template>
  <!-- Login page -->
  <div class="login-container">
    <div class="login-card">
      <div class="login-header">
        <el-icon :size="40" color="#409eff"><ChatDotSquare /></el-icon>
        <h2>Enterprise Knowledge Base QA System</h2>
        <p class="subtitle">RAG-powered intelligent knowledge retrieval and QA platform</p>
      </div>
      <el-form
        ref="formRef"
        :model="loginForm"
        :rules="rules"
        class="login-form"
        @keyup.enter="handleLogin"
      >
        <el-form-item prop="username">
          <el-input
            v-model="loginForm.username"
            placeholder="Please enter username"
            :prefix-icon="User"
            size="large"
          />
        </el-form-item>
        <el-form-item prop="password">
          <el-input
            v-model="loginForm.password"
            type="password"
            placeholder="Please enter password"
            :prefix-icon="Lock"
            size="large"
            show-password
          />
        </el-form-item>
        <el-form-item>
          <el-button
            type="primary"
            size="large"
            class="login-btn"
            :loading="loading"
            @click="handleLogin"
          >
            Log In
          </el-button>
        </el-form-item>
      </el-form>
      <div class="login-footer">
        <span>Test accounts: admin / 123456 (Admin) | user1 / 123456 (User)</span>
      </div>
    </div>
  </div>
</template>

<script setup>
/**
 * Login page
 * Supports username/password login and redirects to the corresponding home page after success
 */
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User, Lock } from '@element-plus/icons-vue'
import { login } from '../api/auth'
import { useUserStore } from '../stores/user'

const router = useRouter()
const userStore = useUserStore()
const formRef = ref(null)
const loading = ref(false)

/** Login form */
const loginForm = reactive({
  username: '',
  password: ''
})

/** Form validation rules */
const rules = {
  username: [{ required: true, message: 'Please enter username', trigger: 'blur' }],
  password: [{ required: true, message: 'Please enter password', trigger: 'blur' }]
}

/** Handle login */
async function handleLogin() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  loading.value = true
  try {
    const res = await login(loginForm)
    userStore.setLoginInfo(res.data)
    ElMessage.success('Login successful')
    // Admins go to dashboard, regular users go to QA page
    if (res.data.user.role === 'admin') {
      router.push('/home')
    } else {
      router.push('/chat')
    }
  } catch (err) {
    // Errors are handled by interceptor
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-container {
  width: 100%;
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.login-card {
  width: 420px;
  padding: 40px;
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
}

.login-header {
  text-align: center;
  margin-bottom: 30px;
}

.login-header h2 {
  margin: 12px 0 8px;
  color: #303133;
  font-size: 22px;
}

.subtitle {
  color: #909399;
  font-size: 13px;
}

.login-btn {
  width: 100%;
}

.login-footer {
  text-align: center;
  margin-top: 16px;
  font-size: 12px;
  color: #c0c4cc;
}
</style>

