<template>
  <div class="page-container">
    <!-- 统计卡片 -->
    <el-row :gutter="20" class="stats-row">
      <el-col :span="6" v-for="stat in stats" :key="stat.title">
        <el-card shadow="hover" class="stat-card" :style="{ borderTop: `3px solid ${stat.color}` }">
          <div class="stat-content">
            <div class="stat-info">
              <div class="stat-title">{{ stat.title }}</div>
              <div class="stat-value">{{ stat.value }}</div>
            </div>
            <div class="stat-icon" :style="{ background: stat.color }">
              <el-icon :size="24"><component :is="stat.icon" /></el-icon>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- 趋势图表 -->
    <el-card class="chart-card">
      <template #header>
        <div class="card-header">
          <span class="title">请求趋势</span>
          <el-radio-group v-model="timeRange" size="small" @change="loadStats">
            <el-radio-button :value="1">1小时</el-radio-button>
            <el-radio-button :value="6">6小时</el-radio-button>
            <el-radio-button :value="24">24小时</el-radio-button>
            <el-radio-button :value="168">7天</el-radio-button>
          </el-radio-group>
        </div>
      </template>
      <div ref="chartRef" style="height: 300px"></div>
    </el-card>
    
    <!-- 请求日志 -->
    <el-card class="logs-card">
      <template #header>
        <div class="card-header">
          <span class="title">请求日志</span>
          <div class="filters">
            <el-select v-model="methodFilter" placeholder="HTTP方法" clearable style="width: 120px" @change="loadLogs">
              <el-option label="GET" value="GET" />
              <el-option label="POST" value="POST" />
              <el-option label="PUT" value="PUT" />
              <el-option label="DELETE" value="DELETE" />
            </el-select>
            <el-select v-model="statusFilter" placeholder="状态码" clearable style="width: 120px; margin-left: 12px" @change="loadLogs">
              <el-option label="成功(2xx)" :value="200" />
              <el-option label="错误(4xx+)" :value="400" />
            </el-select>
            <el-button style="margin-left: 12px" @click="loadLogs" :loading="logsLoading">
              <el-icon><Refresh /></el-icon> 刷新
            </el-button>
          </div>
        </div>
      </template>
      
      <el-table :data="logs" v-loading="logsLoading" stripe border max-height="400">
        <el-table-column prop="method" label="方法" width="80">
          <template #default="{ row }">
            <el-tag :type="getMethodTagType(row.method)" size="small">{{ row.method }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="path" label="请求路径" min-width="200" show-overflow-tooltip />
        <el-table-column prop="status_code" label="状态码" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status_code < 400 ? 'success' : 'danger'" size="small">
              {{ row.status_code }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="response_time" label="响应时间" width="120">
          <template #default="{ row }">
            <span :class="{ 'slow-response': row.response_time > 1000 }">
              {{ row.response_time?.toFixed(2) }} ms
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="ip_address" label="IP地址" width="140" />
        <el-table-column prop="created_at" label="时间" width="180">
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
          :total="logsTotal"
          layout="total, sizes, prev, pager, next"
          @size-change="loadLogs"
          @current-change="loadLogs"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted, nextTick } from 'vue'
import * as echarts from 'echarts'
import { getStats, getMonitorLogs } from '@/api/dashboard'

const chartRef = ref(null)
let chart = null

const timeRange = ref(24)
const statsLoading = ref(false)
const logsLoading = ref(false)

const stats = reactive([
  { title: '请求总数', value: '0', icon: 'DataLine', color: '#409EFF' },
  { title: '错误数量', value: '0', icon: 'WarningFilled', color: '#F56C6C' },
  { title: '错误率', value: '0%', icon: 'PieChart', color: '#E6A23C' },
  { title: '平均响应时间', value: '0 ms', icon: 'Timer', color: '#67C23A' }
])

const logs = ref([])
const logsTotal = ref(0)
const currentPage = ref(1)
const pageSize = ref(20)
const methodFilter = ref('')
const statusFilter = ref(null)

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

const loadStats = async () => {
  statsLoading.value = true
  try {
    const res = await getStats(timeRange.value)
    
    stats[0].value = (res.total_requests || 0).toLocaleString()
    stats[1].value = (res.error_requests || 0).toLocaleString()
    stats[2].value = (res.error_rate || 0) + '%'
    stats[3].value = (res.avg_response_time || 0).toFixed(2) + ' ms'
    
    // 更新图表
    if (res.requests_by_hour && res.requests_by_hour.length > 0) {
      updateChart(res.requests_by_hour)
    } else {
      updateChart([])
    }
  } catch (error) {
    console.error('加载统计数据失败:', error)
  } finally {
    statsLoading.value = false
  }
}

const loadLogs = async () => {
  logsLoading.value = true
  try {
    const params = {
      page: currentPage.value,
      per_page: pageSize.value
    }
    if (methodFilter.value) {
      params.method = methodFilter.value
    }
    if (statusFilter.value) {
      params.status_min = statusFilter.value
    }
    
    const res = await getMonitorLogs(params)
    logs.value = res.logs || []
    logsTotal.value = res.total || 0
  } catch (error) {
    console.error('加载日志失败:', error)
  } finally {
    logsLoading.value = false
  }
}

const updateChart = (hourlyData) => {
  if (!chartRef.value) return
  
  if (!chart) {
    chart = echarts.init(chartRef.value)
  }
  
  const labels = hourlyData.map(item => item.hour)
  const data = hourlyData.map(item => item.count)
  
  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: labels,
      axisLabel: {
        rotate: 45,
        fontSize: 10
      }
    },
    yAxis: {
      type: 'value',
      minInterval: 1
    },
    series: [{
      data: data,
      type: 'bar',
      barMaxWidth: 30,
      itemStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: '#409EFF' },
          { offset: 1, color: '#79bbff' }
        ]),
        borderRadius: [4, 4, 0, 0]
      }
    }]
  }
  
  chart.setOption(option)
}

const handleResize = () => {
  chart?.resize()
}

onMounted(async () => {
  await nextTick()
  loadStats()
  loadLogs()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  chart?.dispose()
})
</script>

<style scoped lang="scss">
.page-container {
  padding: 20px;
}

.stats-row {
  margin-bottom: 20px;
}

.stat-card {
  .stat-content {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  
  .stat-info {
    .stat-title {
      font-size: 14px;
      color: #909399;
      margin-bottom: 8px;
    }
    
    .stat-value {
      font-size: 24px;
      font-weight: 600;
      color: #303133;
    }
  }
  
  .stat-icon {
    width: 48px;
    height: 48px;
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
  }
}

.chart-card {
  margin-bottom: 20px;
}

.logs-card {
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
}

.pagination-wrapper {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}

.slow-response {
  color: #F56C6C;
  font-weight: 500;
}
</style>
