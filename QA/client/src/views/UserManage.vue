<template>
  <!-- User management page (admin only) -->
  <div class="page-container">
    <!-- Toolbar -->
    <el-card shadow="never" class="search-bar">
      <el-row :gutter="16" align="middle">
        <el-col :span="8">
          <el-input
            v-model="queryParams.keyword"
            placeholder="Search by username or nickname"
            clearable
            :prefix-icon="Search"
            @clear="loadList"
            @keyup.enter="loadList"
          />
        </el-col>
        <el-col :span="16" style="text-align: right">
          <el-button type="primary" :icon="Plus" @click="handleAdd">Add User</el-button>
        </el-col>
      </el-row>
    </el-card>

    <!-- Data table -->
    <el-card shadow="never">
      <el-table :data="tableData" v-loading="loading" stripe>
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="username" label="Username" width="120" />
        <el-table-column prop="nickname" label="Nickname" width="120" />
        <el-table-column prop="role" label="Role" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="row.role === 'admin' ? 'danger' : 'primary'" size="small">
              {{ row.role === 'admin' ? 'Admin' : 'User' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="Status" width="80" align="center">
          <template #default="{ row }">
            <el-tag :type="row.status === 1 ? 'success' : 'info'" size="small">
              {{ row.status === 1 ? 'Enabled' : 'Disabled' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="create_time" label="Created At" width="170" />
        <el-table-column label="Actions" width="120" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="handleEdit(row)">Edit</el-button>
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

    <!-- Create/Edit dialog -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? 'Edit User' : 'Add User'"
      width="500px"
    >
      <el-form ref="formRef" :model="formData" :rules="rules" label-width="80px">
        <el-form-item label="Username" prop="username">
          <el-input v-model="formData.username" :disabled="isEdit" placeholder="Please enter username" />
        </el-form-item>
        <el-form-item label="Password" :prop="isEdit ? '' : 'password'">
          <el-input
            v-model="formData.password"
            type="password"
            :placeholder="isEdit ? 'Leave blank to keep unchanged' : 'Please enter password'"
            show-password
          />
        </el-form-item>
        <el-form-item label="Nickname" prop="nickname">
          <el-input v-model="formData.nickname" placeholder="Please enter nickname" />
        </el-form-item>
        <el-form-item label="Role" prop="role">
          <el-select v-model="formData.role" style="width: 100%">
            <el-option label="Admin" value="admin" />
            <el-option label="User" value="user" />
          </el-select>
        </el-form-item>
        <el-form-item v-if="isEdit" label="Status">
          <el-switch v-model="formData.status" :active-value="1" :inactive-value="0" />
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
 * User management page
 * Admins can create/edit users, set roles, and enable/disable status
 */
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Search, Plus } from '@element-plus/icons-vue'
import { getUserList, createUser, updateUser } from '../api/user'

const loading = ref(false)
const submitLoading = ref(false)
const dialogVisible = ref(false)
const isEdit = ref(false)
const tableData = ref([])
const total = ref(0)
const formRef = ref(null)

const queryParams = reactive({ page: 1, page_size: 10, keyword: '' })

const formData = reactive({
  id: null, username: '', password: '', nickname: '', role: 'user', status: 1
})

const rules = {
  username: [{ required: true, message: 'Please enter username', trigger: 'blur' }],
  password: [{ required: true, message: 'Please enter password', trigger: 'blur' }],
  nickname: [{ required: true, message: 'Please enter nickname', trigger: 'blur' }]
}

async function loadList() {
  loading.value = true
  try {
    const res = await getUserList(queryParams)
    tableData.value = res.data.list
    total.value = res.data.total
  } finally {
    loading.value = false
  }
}

function handleAdd() {
  isEdit.value = false
  Object.assign(formData, { id: null, username: '', password: '', nickname: '', role: 'user', status: 1 })
  dialogVisible.value = true
}

function handleEdit(row) {
  isEdit.value = true
  Object.assign(formData, { id: row.id, username: row.username, password: '', nickname: row.nickname, role: row.role, status: row.status })
  dialogVisible.value = true
}

async function handleSubmit() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  submitLoading.value = true
  try {
    if (isEdit.value) {
      const updateData = { nickname: formData.nickname, role: formData.role, status: formData.status }
      if (formData.password) updateData.password = formData.password
      await updateUser(formData.id, updateData)
      ElMessage.success('Updated successfully')
    } else {
      await createUser(formData)
      ElMessage.success('Created successfully')
    }
    dialogVisible.value = false
    loadList()
  } finally {
    submitLoading.value = false
  }
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
