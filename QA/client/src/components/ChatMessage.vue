<template>
  <!-- Chat message bubble component -->
  <div class="message-wrapper" :class="{ 'is-user': isUser }">
    <div class="avatar">
      <el-avatar :size="36" :icon="isUser ? UserFilled : Monitor" :style="avatarStyle" />
    </div>
    <div class="bubble" :class="{ 'user-bubble': isUser, 'ai-bubble': !isUser }">
      <div class="message-text">{{ message.content }}</div>
      <!-- Show references for AI answers -->
      <div v-if="!isUser && message.sources?.length" class="sources">
        <div class="sources-title">References:</div>
        <el-tag
          v-for="(src, i) in message.sources"
          :key="i"
          size="small"
          type="info"
          class="source-tag"
        >
          {{ src.file_name }}
        </el-tag>
      </div>
    </div>
  </div>
</template>

<script setup>
/**
 * Chat message bubble component
 * Differentiates user and AI messages; AI messages can show references
 */
import { computed } from 'vue'
import { UserFilled, Monitor } from '@element-plus/icons-vue'

const props = defineProps({
  /** Message object { role: 'user'|'ai', content: string, sources?: array } */
  message: { type: Object, required: true }
})

/** Whether this is a user message */
const isUser = computed(() => props.message.role === 'user')

/** Avatar style */
const avatarStyle = computed(() => ({
  backgroundColor: isUser.value ? '#409eff' : '#67c23a'
}))
</script>

<style scoped>
.message-wrapper {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
  align-items: flex-start;
}

.message-wrapper.is-user {
  flex-direction: row-reverse;
}

.bubble {
  max-width: 70%;
  padding: 12px 16px;
  border-radius: 12px;
  line-height: 1.6;
  word-break: break-word;
  white-space: pre-wrap;
}

.user-bubble {
  background: #409eff;
  color: #fff;
  border-top-right-radius: 4px;
}

.ai-bubble {
  background: #f4f4f5;
  color: #303133;
  border-top-left-radius: 4px;
}

.message-text {
  font-size: 14px;
}

.sources {
  margin-top: 10px;
  padding-top: 8px;
  border-top: 1px solid #e4e7ed;
}

.sources-title {
  font-size: 12px;
  color: #909399;
  margin-bottom: 4px;
}

.source-tag {
  margin-right: 4px;
  margin-bottom: 4px;
}
</style>

