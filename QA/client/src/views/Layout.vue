
<template>
  <!-- Admin main layout: left menu + top bar + content area -->
  <el-container class="layout-container">
    <!-- Left menu -->
    <el-aside :width="isCollapse ? '64px' : '260px'" class="aside">
      <div class="logo">
        <img src="../assets/icons/TSN.svg" class="logo-icon" />
        <span v-show="!isCollapse" class="logo-text">NETChat</span>
      </div>
      <el-menu
        :default-active="$route.path"
        :collapse="isCollapse"
        :router="true"
        background-color="#304156"
        text-color="#bfcbd9"
        active-text-color="#8d9398"
        class="aside-menu"
      >
        <!-- Admin menu -->
        <template v-if="userStore.isAdmin">
          <el-menu-item index="/home">
            <el-icon><DataAnalysis /></el-icon>
            <template #title>Dashboard</template>
          </el-menu-item>
          <el-menu-item index="/knowledge-base">
            <el-icon><FolderOpened /></el-icon>
            <template #title>Knowledge Base Management</template>
          </el-menu-item>
          <el-menu-item index="/document">
            <el-icon><Document /></el-icon>
            <template #title>Document Management</template>
          </el-menu-item>
          <el-menu-item index="/user-manage">
            <el-icon><User /></el-icon>
            <template #title>User Management</template>
          </el-menu-item>
        </template>
        <!-- Common menu -->
        <el-menu-item index="/chat">
          <el-icon><ChatDotRound /></el-icon>
          <template #title>Intelligent QA</template>
        </el-menu-item>
        <el-menu-item index="/chat-history">
          <el-icon><Clock /></el-icon>
          <template #title>Chat History</template>
        </el-menu-item>
      </el-menu>
    </el-aside>

    <!-- Right content area -->
    <el-container>
      <!-- Top bar -->
      <el-header class="header">
        <div class="header-left">
          <el-icon class="collapse-btn" @click="isCollapse = !isCollapse">
            <Fold v-if="!isCollapse" />
            <Expand v-else />
          </el-icon>
          <span class="page-title">{{ $route.meta.title }}</span>
        </div>
        <div class="header-right">
          <el-dropdown @command="handleCommand">
            <span class="user-info">
              <el-avatar :size="32" :icon="UserFilled" />
              <span class="username">{{ userStore.userInfo?.nickname }}</span>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="logout">
                  <el-icon><SwitchButton /></el-icon>Log out
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>

      <!-- Main content area -->
      <el-main class="main">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
/**
 * Admin layout component
 * Contains sidebar (role-based menu), top bar, and content area
 */
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../stores/user'
import { UserFilled } from '@element-plus/icons-vue'

const router = useRouter()
const userStore = useUserStore()

/** Control sidebar collapse */
const isCollapse = ref(false)

/** Handle dropdown command */
function handleCommand(command) {
  if (command === 'logout') {
    userStore.logout()
    router.push('/login')
  }
}
</script>

<style scoped>
.layout-container {
  height: 100vh;
}

.aside {
  background-color: #304156;
  transition: width 0.3s;
  overflow: hidden;
}



.logo {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  gap: 8px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.logo-icon {
  width: 80px;
  height: 80px;
  display: block;
  flex-shrink: 0;
  color: #e3dfdf;
}

.logo-icon :deep(svg) {
  width: 100%;
  height: 100%;
  display: block;
}

.logo-icon :deep(path) {
  fill: currentColor;
}

.logo-text {
  font-size: 16px;
  font-weight: 600;
  white-space: nowrap;
}

.aside-menu {
  border-right: none;
}

.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid #ebeef5;
  background: #fff;
  padding: 0 20px;
  height: 60px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.collapse-btn {
  font-size: 20px;
  cursor: pointer;
  color: #606266;
}

.page-title {
  font-size: 16px;
  font-weight: 500;
  color: #303133;
}

.header-right .user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}

.username {
  font-size: 14px;
  color: #606266;
}

.main {
  background: #f0f2f5;
  padding: 20px;
  overflow-y: auto;
}


</style>

