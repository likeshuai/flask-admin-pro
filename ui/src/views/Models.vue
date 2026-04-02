<template>
  <div class="page-container">
    <el-card>
      <template #header>
        <div class="flex-between">
          <span>数据模型</span>
          <div style="display: flex; gap: 12px">
            <el-input placeholder="搜索模型..." style="width: 200px" prefix-icon="Search" />
            <el-button type="primary">
              <el-icon><Plus /></el-icon> 新增
            </el-button>
          </div>
        </div>
      </template>
      
      <el-table :data="tableData" stripe border>
        <el-table-column prop="name" label="模型名称" />
        <el-table-column prop="table" label="表名" />
        <el-table-column prop="fields" label="字段数" width="100" />
        <el-table-column prop="records" label="记录数" width="100" />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default>
            <el-button size="small" type="primary">查看</el-button>
            <el-button size="small" type="success">管理</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
const tableData = [
  { name: 'User', table: 'users', fields: 10, records: 1234 },
  { name: 'Role', table: 'roles', fields: 5, records: 10 },
  { name: 'OperationLog', table: 'operation_logs', fields: 12, records: 5678 }
]
</script>
