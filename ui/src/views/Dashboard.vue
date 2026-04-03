<template>
  <div class="dashboard page-container">
    <!-- 时间范围选择器 -->
    <el-card class="mb-4">
      <div class="flex-between">
        <div class="flex-center" style="gap: 8px">
          <el-icon><Calendar /></el-icon>
          <span class="text-regular" style="font-weight: 500">统计时间范围：</span>
        </div>
        <el-button-group>
          <el-button 
            v-for="item in timeRanges" 
            :key="item.value"
            :type="currentTimeRange === item.value ? 'primary' : ''"
            @click="setTimeRange(item.value)"
          >
            {{ item.label }}
          </el-button>
        </el-button-group>
      </div>
    </el-card>
    
    <!-- 统计卡片 -->
    <el-row :gutter="20" class="mb-4">
      <el-col :span="6" v-for="stat in stats" :key="stat.title">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-content">
            <div class="stat-icon" :style="{ background: stat.color }">
              <el-icon :size="28"><component :is="stat.icon" /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stat.value }}</div>
              <div class="stat-label">{{ stat.title }}</div>
            </div>
          </div>
          <div v-if="stat.trend" class="stat-trend" :class="stat.trend > 0 ? 'up' : 'down'">
            <el-icon><component :is="stat.trend > 0 ? 'Top' : 'Bottom'" /></el-icon>
            {{ Math.abs(stat.trend) }}%
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- 请求趋势图 -->
    <el-row :gutter="20">
      <el-col :span="16">
        <el-card>
          <template #header>
            <div class="flex-between">
              <span class="flex-center" style="gap: 8px">
                <el-icon><TrendCharts /></el-icon>
                请求趋势
              </span>
              <el-tag type="primary">{{ currentTimeRangeLabel }}</el-tag>
            </div>
          </template>
          <div ref="chartRef" style="height: 350px"></div>
        </el-card>
      </el-col>
      
      <el-col :span="8">
        <el-card>
          <template #header>
            <span class="flex-center" style="gap: 8px">
              <el-icon><Lightning /></el-icon>
              快捷操作
            </span>
          </template>
          <div class="quick-actions">
            <el-button type="primary" plain style="width: 100%; margin-bottom: 12px">
              <el-icon><Collection /></el-icon> 数据模型
            </el-button>
            <el-button type="success" plain style="width: 100%; margin-bottom: 12px">
              <el-icon><User /></el-icon> 用户管理
            </el-button>
            <el-button type="info" plain style="width: 100%; margin-bottom: 12px">
              <el-icon><Monitor /></el-icon> API 监控
            </el-button>
            <el-button type="warning" plain style="width: 100%">
              <el-icon><Document /></el-icon> 操作日志
            </el-button>
          </div>
        </el-card>
        
        <el-card style="margin-top: 20px">
          <template #header>
            <span class="flex-center" style="gap: 8px">
              <el-icon><InfoFilled /></el-icon>
              系统信息
            </span>
          </template>
          <el-descriptions :column="1" size="small">
            <el-descriptions-item label="ORM">SQLAlchemy</el-descriptions-item>
            <el-descriptions-item label="模型数量">24</el-descriptions-item>
            <el-descriptions-item label="Flask 版本">3.0.0</el-descriptions-item>
          </el-descriptions>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, nextTick } from 'vue'
import * as echarts from 'echarts'
import { getStats } from '@/api/dashboard'

const chartRef = ref(null)
let chart = null

const currentTimeRange = ref(24)
const timeRanges = [
  { value: 1, label: '1 小时' },
  { value: 6, label: '6 小时' },
  { value: 24, label: '24 小时' },
  { value: 168, label: '7 天' },
  { value: 720, label: '30 天' }
]

const currentTimeRangeLabel = ref('24 小时')

const stats = reactive([
  { title: '请求总数', value: '0', icon: 'DataLine', color: 'linear-gradient(135deg, #409EFF 0%, #337ecc 100%)', trend: 0 },
  { title: '平均响应 (ms)', value: '0', icon: 'Timer', color: 'linear-gradient(135deg, #67C23A 0%, #529b2e 100%)', trend: 0 },
  { title: '错误数量', value: '0', icon: 'WarningFilled', color: 'linear-gradient(135deg, #F56C6C 0%, #c45555 100%)', trend: 0 },
  { title: '错误率', value: '0%', icon: 'PieChart', color: 'linear-gradient(135deg, #E6A23C 0%, #b88230 100%)', trend: 0 }
])

// 加载数据
const loadData = async (hours) => {
  try {
    const res = await getStats(hours)
    
    // 后端返回: total_requests, error_requests, error_rate, avg_response_time, requests_by_hour
    stats[0].value = res.total_requests?.toLocaleString() || '0'
    stats[1].value = res.avg_response_time?.toFixed(2) || '0'
    stats[2].value = res.error_requests?.toLocaleString() || '0'
    stats[3].value = (res.error_rate || 0) + '%'
    
    // 处理小时统计数据
    if (res.requests_by_hour && res.requests_by_hour.length > 0) {
      const hourlyData = {
        labels: res.requests_by_hour.map(item => item.hour),
        data: res.requests_by_hour.map(item => item.count)
      }
      updateChart(hourlyData)
    }
  } catch (error) {
    console.error('加载数据失败:', error)
  }
}

// 更新时间范围
const setTimeRange = (hours) => {
  currentTimeRange.value = hours
  const selected = timeRanges.find(item => item.value === hours)
  currentTimeRangeLabel.value = selected?.label || '24 小时'
  loadData(hours)
}

// 更新图表
const updateChart = (hourlyData) => {
  if (!chartRef.value) return
  
  if (!chart) {
    chart = echarts.init(chartRef.value)
  }
  
  const option = {
    tooltip: { trigger: 'axis' },
    grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: hourlyData.labels || []
    },
    yAxis: { type: 'value' },
    series: [{
      data: hourlyData.data || [],
      type: 'line',
      smooth: true,
      areaStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: 'rgba(64, 158, 255, 0.3)' },
          { offset: 1, color: 'rgba(64, 158, 255, 0.01)' }
        ])
      },
      itemStyle: { color: '#409EFF' }
    }]
  }
  
  chart.setOption(option)
  window.addEventListener('resize', () => chart?.resize())
}

onMounted(() => {
  loadData(24)
})
</script>

<style scoped lang="scss">
.dashboard {
  padding: 20px;
}

.mb-4 {
  margin-bottom: 20px;
}

.stat-card {
  border-radius: 12px;
  transition: all 0.3s;
  
  &:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 24px 0 rgba(0, 0, 0, 0.1);
  }
  
  .stat-content {
    display: flex;
    align-items: center;
    gap: 16px;
  }
  
  .stat-icon {
    width: 64px;
    height: 64px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
  }
  
  .stat-value {
    font-size: 28px;
    font-weight: 600;
    color: var(--el-text-color-primary);
  }
  
  .stat-label {
    font-size: 14px;
    color: var(--el-text-color-secondary);
    margin-top: 4px;
  }
  
  .stat-trend {
    margin-top: 16px;
    font-size: 13px;
    display: flex;
    align-items: center;
    gap: 4px;
    
    &.up {
      color: #10b981;
    }
    
    &.down {
      color: #ef4444;
    }
  }
}

.quick-actions {
  display: flex;
  flex-direction: column;
}
</style>
