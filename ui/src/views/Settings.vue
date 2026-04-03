<template>
  <div class="page-container">
    <el-row :gutter="20">
      <el-col :span="12">
        <!-- 系统信息 -->
        <el-card class="settings-card">
          <template #header>
            <div class="card-header">
              <el-icon><InfoFilled /></el-icon>
              <span>系统信息</span>
            </div>
          </template>
          <el-descriptions :column="1" border>
            <el-descriptions-item label="应用名称">Flask Admin Pro</el-descriptions-item>
            <el-descriptions-item label="版本号">v1.0.0</el-descriptions-item>
            <el-descriptions-item label="框架版本">Flask 3.x + Vue 3.5</el-descriptions-item>
            <el-descriptions-item label="UI框架">Element Plus 2.x</el-descriptions-item>
            <el-descriptions-item label="数据库">SQLite / SQLAlchemy</el-descriptions-item>
          </el-descriptions>
        </el-card>
        
        <!-- 关于 -->
        <el-card class="settings-card" style="margin-top: 20px">
          <template #header>
            <div class="card-header">
              <el-icon><QuestionFilled /></el-icon>
              <span>关于</span>
            </div>
          </template>
          <div class="about-content">
            <p>Flask Admin Pro 是一个可嵌入 Flask 项目的后台管理系统 Python 库，提供即插即用的管理界面、自动 CRUD 生成、多 ORM 适配和 API 监控功能。</p>
            <p class="features-title">核心特性：</p>
            <ul class="features-list">
              <li><el-icon><Check /></el-icon> 即插即用 - 一行代码集成到现有 Flask 项目</li>
              <li><el-icon><Check /></el-icon> 零构建 - 无需 Node.js，无需 npm，无需打包</li>
              <li><el-icon><Check /></el-icon> 现代化 UI - Element Plus + Vue 3</li>
              <li><el-icon><Check /></el-icon> 自动 CRUD - 根据模型自动生成管理界面</li>
              <li><el-icon><Check /></el-icon> API 监控 - 内置接口性能监控和日志</li>
            </ul>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="12">
        <!-- 主题设置 -->
        <el-card class="settings-card">
          <template #header>
            <div class="card-header">
              <el-icon><Brush /></el-icon>
              <span>主题设置</span>
            </div>
          </template>
          <el-form label-width="100px">
            <el-form-item label="主题颜色">
              <div class="theme-colors">
                <div
                  v-for="color in themeColors"
                  :key="color.value"
                  class="color-item"
                  :class="{ active: currentTheme === color.value }"
                  :style="{ backgroundColor: color.color }"
                  @click="setTheme(color.value)"
                >
                  <el-icon v-if="currentTheme === color.value"><Check /></el-icon>
                </div>
              </div>
            </el-form-item>
            <el-form-item label="深色模式">
              <el-switch
                v-model="isDarkMode"
                @change="toggleDarkMode"
                active-text="开启"
                inactive-text="关闭"
              />
            </el-form-item>
          </el-form>
        </el-card>
        
        <!-- 快捷操作 -->
        <el-card class="settings-card" style="margin-top: 20px">
          <template #header>
            <div class="card-header">
              <el-icon><Operation /></el-icon>
              <span>快捷操作</span>
            </div>
          </template>
          <div class="quick-actions">
            <el-button @click="clearCache">
              <el-icon><Delete /></el-icon> 清除缓存
            </el-button>
            <el-button @click="refreshPage">
              <el-icon><Refresh /></el-icon> 刷新页面
            </el-button>
            <el-button type="danger" @click="handleLogout">
              <el-icon><SwitchButton /></el-icon> 退出登录
            </el-button>
          </div>
        </el-card>
        
        <!-- 帮助链接 -->
        <el-card class="settings-card" style="margin-top: 20px">
          <template #header>
            <div class="card-header">
              <el-icon><Link /></el-icon>
              <span>帮助链接</span>
            </div>
          </template>
          <div class="help-links">
            <el-link type="primary" :underline="false" href="https://github.com" target="_blank">
              <el-icon><Link /></el-icon> GitHub 仓库
            </el-link>
            <el-link type="primary" :underline="false" href="https://flask.palletsprojects.com/" target="_blank">
              <el-icon><Link /></el-icon> Flask 文档
            </el-link>
            <el-link type="primary" :underline="false" href="https://element-plus.org/" target="_blank">
              <el-icon><Link /></el-icon> Element Plus 文档
            </el-link>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { logout } from '@/api/user'

const router = useRouter()

const themeColors = [
  { value: 'blue', color: '#409EFF', name: '默认蓝' },
  { value: 'purple', color: '#722ED1', name: '典雅紫' },
  { value: 'green', color: '#52C41A', name: '自然绿' },
  { value: 'orange', color: '#FA8C16', name: '活力橙' },
  { value: 'red', color: '#F5222D', name: '热情红' }
]

const currentTheme = ref('blue')
const isDarkMode = ref(false)

onMounted(() => {
  // 从localStorage读取主题设置
  const savedTheme = localStorage.getItem('admin_theme')
  if (savedTheme) {
    currentTheme.value = savedTheme
  }
  
  const savedDarkMode = localStorage.getItem('admin_dark_mode')
  if (savedDarkMode === 'true') {
    isDarkMode.value = true
    document.documentElement.classList.add('dark')
  }
})

const setTheme = (theme) => {
  currentTheme.value = theme
  localStorage.setItem('admin_theme', theme)
  ElMessage.success(`主题已切换为 ${themeColors.find(c => c.value === theme)?.name}`)
}

const toggleDarkMode = (value) => {
  if (value) {
    document.documentElement.classList.add('dark')
    localStorage.setItem('admin_dark_mode', 'true')
    ElMessage.success('已开启深色模式')
  } else {
    document.documentElement.classList.remove('dark')
    localStorage.setItem('admin_dark_mode', 'false')
    ElMessage.success('已关闭深色模式')
  }
}

const clearCache = () => {
  ElMessageBox.confirm('确定要清除缓存吗？这将清除所有本地存储的数据。', '确认操作', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    localStorage.clear()
    ElMessage.success('缓存已清除')
  }).catch(() => {})
}

const refreshPage = () => {
  window.location.reload()
}

const handleLogout = async () => {
  try {
    await ElMessageBox.confirm('确定要退出登录吗？', '确认退出', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await logout()
    localStorage.removeItem('admin_token')
    localStorage.removeItem('admin_user')
    ElMessage.success('退出登录成功')
    router.push('/login')
  } catch (error) {
    if (error !== 'cancel') {
      console.error('退出登录失败:', error)
      localStorage.removeItem('admin_token')
      localStorage.removeItem('admin_user')
      router.push('/login')
    }
  }
}
</script>

<style scoped lang="scss">
.page-container {
  padding: 20px;
}

.settings-card {
  .card-header {
    display: flex;
    align-items: center;
    gap: 8px;
    font-weight: 600;
  }
}

.about-content {
  line-height: 1.8;
  color: #606266;
  
  .features-title {
    margin-top: 16px;
    font-weight: 600;
    color: #303133;
  }
  
  .features-list {
    margin: 12px 0;
    padding-left: 0;
    list-style: none;
    
    li {
      display: flex;
      align-items: center;
      gap: 8px;
      margin-bottom: 8px;
      
      .el-icon {
        color: #67C23A;
      }
    }
  }
}

.theme-colors {
  display: flex;
  gap: 12px;
  
  .color-item {
    width: 40px;
    height: 40px;
    border-radius: 8px;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    transition: transform 0.2s, box-shadow 0.2s;
    
    &:hover {
      transform: scale(1.1);
    }
    
    &.active {
      box-shadow: 0 0 0 3px rgba(0, 0, 0, 0.1);
    }
  }
}

.quick-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.help-links {
  display: flex;
  flex-direction: column;
  gap: 12px;
  
  .el-link {
    display: flex;
    align-items: center;
    gap: 8px;
  }
}
</style>
