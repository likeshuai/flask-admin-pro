<template>
  <div class="page-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span class="title">操作日志</span>
          <div class="filters">
            <el-date-picker
              v-model="dateRange"
              type="daterange"
              range-separator="至"
              start-placeholder="开始日期"
              end-placeholder="结束日期"
              style="width: 260px"
              @change="loadLogs"
            />
            <el-select v-model="methodFilter" placeholder="请求方法" clearable style="width: 120px; margin-left: 12px" @change="loadLogs">
              <el-option label="GET" value="GET" />
              <el-option label="POST" value="POST" />
              <el-option label="PUT" value="PUT" />
              <el-option label="DELETE" value="DELETE" />
            </el-select>
            <el-button style="margin-left: 12px" @click="loadLogs" :loading="loading">
              <el-icon><Refresh /></el-icon> 刷新
            </el-button>
          </div>
        </div>
      </template>
      
      <el-table :data="logs" v-loading="loading" stripe border>
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="method" label="操作类型" width="100">
          <template #default="{ row }">
            <el-tag :type="getMethodTagType(row.method)" size="small">
              {{ getOperationType(row.method) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="path" label="操作路径" min-width="250" show-overflow-tooltip />
        <el-table-column prop="status_code" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status_code < 400 ? 'success' : 'danger'" size="small">
              {{ row.status_code < 400 ? '成功' : '失败' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="ip_address" label="IP地址" width="140" />
        <el-table-column prop="response_time" label="耗时" width="100">
          <template #default="{ row }">
            {{ row.response_time?.toFixed(2) }} ms
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="操作时间" width="180">
          <template #default="{ row }">
            {{ formatDateTime(row.created_at) }}
          </template>
        </el-table-column>
      </el-table>
      
      <div class="pagination-wrapper">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[20, 50, 100]"
          :total="total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="loadLogs"
          @current-change="loadLogs"
        />
      </div>
    </el-card>
    
    <el-card class="tips-card" style="margin-top: 20px">
      <template #header>
        <span>日志说明</span>
      </template>
      <ul class="tips-list">
        <li><el-tag type="success" size="small">GET</el-tag> 查询操作：获取数据列表或详情</li>
        <li><el-tag type="primary" size="small">POST</el-tag> 创建操作：新增数据记录</li>
        <li><el-tag type="warning" size="small">PUT</el-tag> 更新操作：修改现有数据</li>
        <li><el-tag type="danger" size="small">DELETE</el-tag> 删除操作：移除数据记录</li>
      </ul>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getMonitorLogs } from '@/api/dashboard'

const loading = ref(false)
const logs = ref([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(20)
const methodFilter = ref('')
const dateRange = ref(null)

const formatDateTime = (dateStr) => {
  if (!dateStr) return '-'
  try {
    return new Date(dateStr).toLocaleString('zh-CN')
  } catch {
    return dateStr
  }
}

const getMethodTagType = (method) => {
  const types = {
    'GET': 'success',
    'POST': 'primary',
    'PUT': 'warning',
    'DELETE': 'danger'
  }
  return types[method] || 'info'
}

const getOperationType = (method) => {
  const types = {
    'GET': '查询',
    'POST': '创建',
    'PUT': '更新',
    'DELETE': '删除'
  }
  return types[method] || method
}

const loadLogs = async () => {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      per_page: pageSize.value
    }
    if (methodFilter.value) {
      params.method = methodFilter.value
    }
    
    const res = await getMonitorLogs(params)
    logs.value = res.logs || []
    total.value = res.total || 0
  } catch (error) {
    console.error('加载日志失败:', error)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadLogs()
})
</script>

<style scoped lang="scss">
.page-container {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  
  .title {
    font-size: 16px;
    font-weight: 600;
  }
  
  .filters {
    display: flex;
    align-items: center;
  }
}

.pagination-wrapper {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.tips-card {
  .tips-list {
    margin: 0;
    padding: 0;
    list-style: none;
    
    li {
      margin-bottom: 12px;
      display: flex;
      align-items: center;
      gap: 8px;
      color: #606266;
    }
  }
}
</style>
