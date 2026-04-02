<template>
  <div class="page-container">
    <el-card>
      <template #header>
        <div class="flex-between">
          <span>用户管理</span>
          <el-button type="primary">
            <el-icon><Plus /></el-icon> 新增用户
          </el-button>
        </div>
      </template>
      
      <el-table :data="tableData" stripe border>
        <el-table-column prop="username" label="用户名" />
        <el-table-column prop="email" label="邮箱" />
        <el-table-column prop="role" label="角色" width="100" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === 'active' ? 'success' : 'danger'">
              {{ row.status === 'active' ? '正常' : '禁用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default>
            <el-button size="small" type="primary">编辑</el-button>
            <el-button size="small" type="danger">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
const tableData = [
  { username: 'admin', email: 'admin@example.com', role: '管理员', status: 'active' },
  { username: 'user1', email: 'user1@example.com', role: '用户', status: 'active' }
]
</script>
