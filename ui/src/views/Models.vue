<template>
  <div class="page-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span class="title">数据模型</span>
          <div class="actions">
            <el-button @click="loadModels" :loading="loading">
              <el-icon><Refresh /></el-icon> 刷新
            </el-button>
          </div>
        </div>
      </template>
      
      <el-table :data="models" v-loading="loading" stripe border>
        <el-table-column prop="name" label="模型名称" min-width="150">
          <template #default="{ row }">
            <el-link type="primary" @click="goToModelCrud(row)">
              {{ row.name }}
            </el-link>
          </template>
        </el-table-column>
        <el-table-column prop="table" label="数据库表名" min-width="150" />
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button size="small" type="primary" @click="goToModelCrud(row)">
              <el-icon><Setting /></el-icon> 管理数据
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <el-empty v-if="!loading && models.length === 0" description="暂无数据模型" />
    </el-card>
    
    <el-card class="tips-card" style="margin-top: 20px">
      <template #header>
        <span>使用说明</span>
      </template>
      <ul class="tips-list">
        <li>Flask Admin Pro 会自动扫描并注册 Flask-SQLAlchemy 模型</li>
        <li>点击模型名称或"管理数据"按钮进入数据管理页面</li>
        <li>支持对所有注册模型进行增删改查操作</li>
        <li>系统会自动识别字段类型并生成对应的表单控件</li>
      </ul>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getModels } from '@/api/dashboard'

const router = useRouter()
const loading = ref(false)
const models = ref([])

const loadModels = async () => {
  loading.value = true
  try {
    const res = await getModels()
    models.value = res.models || []
  } catch (error) {
    console.error('加载模型列表失败:', error)
    ElMessage.error('加载模型列表失败')
  } finally {
    loading.value = false
  }
}

const goToModelCrud = (model) => {
  router.push(`/models/${model.name}`)
}

onMounted(() => {
  loadModels()
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
  
  .actions {
    display: flex;
    align-items: center;
    gap: 12px;
  }
}

.tips-card {
  .tips-list {
    margin: 0;
    padding-left: 20px;
    color: #666;
    line-height: 2;
    
    li {
      margin-bottom: 8px;
    }
  }
}
</style>
