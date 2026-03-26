<template>
  <!-- Knowledge base management page -->
  <div class="page-container">
    <!-- Toolbar -->
    <el-card shadow="never" class="search-bar">
      <el-row :gutter="16" align="middle">
        <el-col :span="8">
          <el-input
            v-model="queryParams.keyword"
            placeholder="Search knowledge base name"
            clearable
            :prefix-icon="Search"
            @clear="loadList"
            @keyup.enter="loadList"
          />
        </el-col>
        <el-col :span="16" style="text-align: right">
          <el-button type="primary" :icon="Plus" @click="handleAdd">Add Knowledge Base</el-button>
        </el-col>
      </el-row>
    </el-card>

    <!-- Data table -->
    <el-card shadow="never" class="table-card">
      <el-table :data="tableData" v-loading="loading" stripe>
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="kb_name" label="Knowledge Base Name" min-width="150" />
        <el-table-column prop="description" label="Description" min-width="200" show-overflow-tooltip />
        <el-table-column prop="doc_count" label="Docs" width="80" align="center" />
        <el-table-column prop="creator_name" label="Created By" width="100" />
        <el-table-column prop="create_time" label="Created At" width="170" />
        <el-table-column label="Actions" width="160" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="handleEdit(row)">Edit</el-button>
            <el-popconfirm title="Are you sure you want to delete this knowledge base?" @confirm="handleDelete(row.id)">
              <template #reference>
                <el-button type="danger" link>Delete</el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>

      <!-- Pagination -->
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

    <!-- Create/Edit dialog -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? 'Edit Knowledge Base' : 'Add Knowledge Base'"
      width="500px"
    >
      <el-form ref="formRef" :model="formData" :rules="rules" label-width="100px">
        <el-form-item label="Knowledge Base Name" prop="kb_name">
          <el-input v-model="formData.kb_name" placeholder="Please enter a knowledge base name" />
        </el-form-item>
        <el-form-item label="Description" prop="description">
          <el-input
            v-model="formData.description"
            type="textarea"
            :rows="3"
            placeholder="Please enter a description"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">Cancel</el-button>
        <el-button type="primary" :loading="submitLoading" @click="handleSubmit">Confirm</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
/**
 * Knowledge base management page
 * Supports list query, create, update, and delete operations for knowledge bases
 */
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Search, Plus } from '@element-plus/icons-vue'
import { getKBList, createKB, updateKB, deleteKB } from '../api/knowledge'

const loading = ref(false)
const submitLoading = ref(false)
const dialogVisible = ref(false)
const isEdit = ref(false)
const tableData = ref([])
const total = ref(0)
const formRef = ref(null)

/** Query params */
const queryParams = reactive({ page: 1, page_size: 10, keyword: '' })

/** Form data */
const formData = reactive({ id: null, kb_name: '', description: '' })

/** Form validation */
const rules = {
  kb_name: [{ required: true, message: 'Please enter a knowledge base name', trigger: 'blur' }]
}

/** Load knowledge base list */
async function loadList() {
  loading.value = true
  try {
    const res = await getKBList(queryParams)
    tableData.value = res.data.list
    total.value = res.data.total
  } finally {
    loading.value = false
  }
}

/** Open create dialog */
function handleAdd() {
  isEdit.value = false
  Object.assign(formData, { id: null, kb_name: '', description: '' })
  dialogVisible.value = true
}

/** Open edit dialog */
function handleEdit(row) {
  isEdit.value = true
  Object.assign(formData, { id: row.id, kb_name: row.kb_name, description: row.description })
  dialogVisible.value = true
}

/** Submit form */
async function handleSubmit() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  submitLoading.value = true
  try {
    if (isEdit.value) {
      await updateKB(formData.id, formData)
      ElMessage.success('Updated successfully')
    } else {
      await createKB(formData)
      ElMessage.success('Created successfully')
    }
    dialogVisible.value = false
    loadList()
  } finally {
    submitLoading.value = false
  }
}

/** Delete knowledge base */
async function handleDelete(id) {
  await deleteKB(id)
  ElMessage.success('Deleted successfully')
  loadList()
}

onMounted(() => loadList())
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

