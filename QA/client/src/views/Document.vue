<template>
  <!-- Document management page -->
  <div class="page-container">
    <!-- Toolbar -->
    <el-card shadow="never" class="search-bar">
      <el-row :gutter="16" align="middle">
        <el-col :span="8">
          <el-select
            v-model="queryParams.kb_id"
            placeholder="Filter by knowledge base"
            clearable
            @change="loadList"
            style="width: 100%"
          >
            <el-option
              v-for="kb in kbOptions"
              :key="kb.id"
              :label="kb.kb_name"
              :value="kb.id"
            />
          </el-select>
        </el-col>
        <el-col :span="16" style="text-align: right">
          <el-button type="primary" :icon="Upload" @click="uploadVisible = true">Upload Document</el-button>
        </el-col>
      </el-row>
    </el-card>

    <!-- Data table -->
    <el-card shadow="never">
      <el-table :data="tableData" v-loading="loading" stripe>
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="file_name" label="File Name" min-width="200" show-overflow-tooltip />
        <el-table-column prop="kb_name" label="Knowledge Base" width="150" />
        <el-table-column prop="file_type" label="Type" width="80" align="center">
          <template #default="{ row }">
            <el-tag size="small">{{ row.file_type }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="Size" width="100" align="center">
          <template #default="{ row }">
            {{ formatSize(row.file_size) }}
          </template>
        </el-table-column>
        <el-table-column prop="chunk_count" label="Chunks" width="80" align="center" />
        <el-table-column prop="status" label="Status" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="statusMap[row.status]?.type" size="small">
              {{ statusMap[row.status]?.label }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="create_time" label="Uploaded At" width="170" />
        <el-table-column label="Actions" width="80" fixed="right">
          <template #default="{ row }">
            <el-popconfirm title="Are you sure you want to delete this document?" @confirm="handleDelete(row.id)">
              <template #reference>
                <el-button type="danger" link>Delete</el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination">
        <el-pagination
          v-model:current-page="queryParams.page"
          v-model:page-size="queryParams.page_size"
          :total="total"
          :page-sizes="[10, 20, 50]"
          layout="total, sizes, prev, pager, next"
          @change="loadList"
        />
      </div>
    </el-card>

    <!-- Upload dialog -->
    <el-dialog v-model="uploadVisible" title="Upload Document" width="500px">
      <el-form label-width="100px">
        <el-form-item label="Knowledge Base" required>
          <el-select v-model="uploadKbId" placeholder="Please select a knowledge base" style="width: 100%">
            <el-option
              v-for="kb in kbOptions"
              :key="kb.id"
              :label="kb.kb_name"
              :value="kb.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="File" required>
          <el-upload
            ref="uploadRef"
            v-model:file-list="fileList"
            :auto-upload="false"
            :limit="1"
            :on-exceed="() => ElMessage.warning('Only one file can be uploaded')"
            accept=".txt,.pdf,.md,.docx"
          >
            <el-button type="primary" plain>Select File</el-button>
            <template #tip>
              <div class="el-upload__tip">Supported formats: txt, pdf, md, docx. Max size: 50MB.</div>
            </template>
          </el-upload>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="uploadVisible = false">Cancel</el-button>
        <el-button type="primary" :loading="uploading" @click="handleUpload">Upload</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
/**
 * Document management page
 * Supports filtering by knowledge base, uploading new documents, and deleting documents
 */
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Upload } from '@element-plus/icons-vue'
import { getDocList, uploadDoc, deleteDoc } from '../api/document'
import { getAllKB } from '../api/knowledge'

const loading = ref(false)
const uploading = ref(false)
const uploadVisible = ref(false)
const tableData = ref([])
const total = ref(0)
const kbOptions = ref([])
const uploadKbId = ref(null)
const uploadRef = ref(null)
const fileList = ref([])

/** Query params */
const queryParams = reactive({ page: 1, page_size: 10, kb_id: null })

/** Document status map */
const statusMap = {
  uploading: { label: 'Processing', type: 'warning' },
  vectorized: { label: 'Ready', type: 'success' },
  failed: { label: 'Failed', type: 'danger' }
}

/** Format file size */
function formatSize(bytes) {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
}

/** Load knowledge base options */
async function loadKBOptions() {
  const res = await getAllKB()
  kbOptions.value = res.data
}

/** Load document list */
async function loadList() {
  loading.value = true
  try {
    const res = await getDocList(queryParams)
    tableData.value = res.data.list
    total.value = res.data.total
  } finally {
    loading.value = false
  }
}

/** Handle document upload */
async function handleUpload() {
  if (!uploadKbId.value) {
    return ElMessage.warning('Please select a knowledge base')
  }
  if (fileList.value.length === 0) {
    return ElMessage.warning('Please select a file')
  }

  const formData = new FormData()
  formData.append('file', fileList.value[0].raw)
  formData.append('kb_id', uploadKbId.value)

  uploading.value = true
  try {
    await uploadDoc(formData)
    ElMessage.success('Upload successful')
    uploadVisible.value = false
    fileList.value = []
    loadList()
  } finally {
    uploading.value = false
  }
}

/** Delete document */
async function handleDelete(id) {
  await deleteDoc(id)
  ElMessage.success('Deleted successfully')
  loadList()
}

onMounted(() => {
  loadKBOptions()
  loadList()
})
</script>

<style scoped>
.page-container {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.pagination {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}
</style>

