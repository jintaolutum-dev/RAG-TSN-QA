<template>
  <!-- Intelligent QA chat page -->
  <div class="chat-container">
    <!-- Left knowledge base selector -->
    <div class="chat-sidebar">
      <div class="sidebar-title">Select Knowledge Base</div>
      <div class="kb-list">
        <div
          v-for="kb in kbList"
          :key="kb.id"
          class="kb-item"
          :class="{ active: selectedKb?.id === kb.id }"
          @click="selectKb(kb)"
        >
          <el-icon><FolderOpened /></el-icon>
          <span class="kb-name">{{ kb.kb_name }}</span>
          <el-tag size="small" type="info">{{ kb.doc_count }} docs</el-tag>
        </div>
      </div>
      <div v-if="kbList.length === 0" class="empty-tip">
        <el-empty description="No knowledge base available" :image-size="60" />
      </div>
    </div>

    <!-- Right chat area -->
    <div class="chat-main">
      <!-- Chat window title -->
      <div class="chat-header">
        <span v-if="selectedKb">
          <el-icon><ChatDotRound /></el-icon>
          Querying: {{ selectedKb.kb_name }}
        </span>
        <span v-else class="hint">Please select a knowledge base on the left first</span>
      </div>

      <!-- Message list -->
      <div class="chat-messages" ref="messagesRef">
        <div v-if="messages.length === 0" class="welcome">
          <el-icon :size="64" color="#c0c4cc"><ChatDotSquare /></el-icon>
          <h3>Welcome to the Enterprise Knowledge Base QA System</h3>
          <p>Select a knowledge base on the left, then enter your question</p>
        </div>
        <ChatMessage v-for="(msg, i) in messages" :key="i" :message="msg" />
        <!-- Loading hint -->
        <div v-if="asking" class="loading-msg">
          <el-avatar :size="36" :icon="Monitor" style="background-color: #67c23a" />
          <div class="loading-bubble">
            <span class="loading-dot">Thinking</span>
            <el-icon class="is-loading"><Loading /></el-icon>
          </div>
        </div>
      </div>

      <!-- Input area -->
      <div class="chat-input">
        <el-input
          v-model="question"
          type="textarea"
          :rows="2"
          placeholder="Please enter your question..."
          :disabled="!selectedKb || asking"
          @keydown.enter.exact.prevent="sendQuestion"
          resize="none"
        />
        <el-button
          type="primary"
          :icon="Promotion"
          :loading="asking"
          :disabled="!selectedKb || !question.trim()"
          @click="sendQuestion"
          class="send-btn"
        >
          Send
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
/**
 * Intelligent QA chat page
 * Select knowledge base on the left and chat on the right
 * Supports multi-turn chat and shows AI answers with references
 */
import { ref, onMounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { Promotion, Loading, Monitor } from '@element-plus/icons-vue'
import { getAllKB } from '../api/knowledge'
import { askQuestion } from '../api/chat'
import ChatMessage from '../components/ChatMessage.vue'

/** Knowledge base list */
const kbList = ref([])
/** Currently selected knowledge base */
const selectedKb = ref(null)
/** Chat message list */
const messages = ref([])
/** Current input question */
const question = ref('')
/** Whether a request is in progress */
const asking = ref(false)
/** Current session ID */
const sessionId = ref('')
/** Message list DOM ref */
const messagesRef = ref(null)

/** Load knowledge base list */
async function loadKBList() {
  try {
    const res = await getAllKB()
    kbList.value = res.data
  } catch (err) {
    // Errors are handled by interceptor
  }
}

/** Select knowledge base */
function selectKb(kb) {
  if (selectedKb.value?.id === kb.id) return
  selectedKb.value = kb
  messages.value = []
  sessionId.value = generateSessionId()
}

/** Generate session ID */
function generateSessionId() {
  return 'sess_' + Date.now().toString(36) + Math.random().toString(36).slice(2, 8)
}

/** Auto scroll to bottom */
async function scrollToBottom() {
  await nextTick()
  if (messagesRef.value) {
    messagesRef.value.scrollTop = messagesRef.value.scrollHeight
  }
}

/** Send question */
async function sendQuestion() {
  const q = question.value.trim()
  if (!q || !selectedKb.value || asking.value) return

  // Add user message
  messages.value.push({ role: 'user', content: q })
  question.value = ''
  asking.value = true
  scrollToBottom()

  try {
    const res = await askQuestion({
      question: q,
      kb_id: selectedKb.value.id,
      session_id: sessionId.value
    })

    // Add AI reply
    messages.value.push({
      role: 'ai',
      content: res.data.answer,
      sources: res.data.source_docs
    })
  } catch (err) {
    messages.value.push({
      role: 'ai',
      content: 'Sorry, the service is temporarily unavailable. Please try again later.'
    })
  } finally {
    asking.value = false
    scrollToBottom()
  }
}

onMounted(() => loadKBList())
</script>

<style scoped>
.chat-container {
  display: flex;
  height: calc(100vh - 100px);
  background: #fff;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
}

/* Left knowledge base panel */
.chat-sidebar {
  width: 260px;
  border-right: 1px solid #ebeef5;
  display: flex;
  flex-direction: column;
  background: #fafafa;
}

.sidebar-title {
  padding: 16px 20px;
  font-weight: 600;
  font-size: 15px;
  color: #303133;
  border-bottom: 1px solid #ebeef5;
}

.kb-list {
  flex: 1;
  overflow-y: auto;
  padding: 8px;
}

.kb-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 12px;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.2s;
  margin-bottom: 4px;
}

.kb-item:hover {
  background: #ecf5ff;
}

.kb-item.active {
  background: #409eff;
  color: #fff;
}

.kb-item.active .el-tag {
  color: #fff;
  background: rgba(255, 255, 255, 0.2);
  border-color: transparent;
}

.kb-name {
  flex: 1;
  font-size: 14px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.empty-tip {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* Right chat area */
.chat-main {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.chat-header {
  padding: 14px 20px;
  border-bottom: 1px solid #ebeef5;
  font-size: 14px;
  font-weight: 500;
  color: #303133;
  display: flex;
  align-items: center;
  gap: 6px;
}

.chat-header .hint {
  color: #909399;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
}

.welcome {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #c0c4cc;
  gap: 12px;
}

.welcome h3 {
  color: #909399;
  font-size: 18px;
}

.welcome p {
  font-size: 14px;
}

.loading-msg {
  display: flex;
  gap: 12px;
  align-items: flex-start;
  margin-bottom: 20px;
}

.loading-bubble {
  background: #f4f4f5;
  padding: 12px 16px;
  border-radius: 12px;
  border-top-left-radius: 4px;
  display: flex;
  align-items: center;
  gap: 8px;
  color: #909399;
  font-size: 14px;
}

/* Input area */
.chat-input {
  padding: 16px 20px;
  border-top: 1px solid #ebeef5;
  display: flex;
  gap: 12px;
  align-items: flex-end;
  background: #fff;
}

.chat-input :deep(.el-textarea__inner) {
  border-radius: 8px;
}

.send-btn {
  height: 54px;
  border-radius: 8px;
}
</style>

