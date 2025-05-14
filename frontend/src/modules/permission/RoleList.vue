<template>
  <div class="role-list-container">
    <div class="toolbar">
      <el-button type="primary" @click="handleAddRole">新增角色</el-button>
      <el-button @click="refreshList">刷新列表</el-button>
    </div>
    <el-table :data="roles" v-loading="loading" border style="width: 100%">
      <el-table-column prop="name" label="角色名称" width="180" />
      <el-table-column prop="description" label="角色描述" />
      <el-table-column label="操作" width="250" fixed="right">
        <template #default="{ row }">
          <el-button type="text" size="small" @click="handleEditRole(row)">编辑</el-button>
          <el-button type="text" size="small" @click="handleSetPermissions(row)">分配权限</el-button>
          <el-button type="text" size="small" @click="handleManageUsers(row)">管理用户</el-button>
          <el-button type="text" size="small" @click="handleDeleteRole(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-pagination
      style="margin-top: 20px;"
      :current-page="pagination.currentPage"
      :page-size="pagination.pageSize"
      :total="pagination.total"
      layout="total, sizes, prev, pager, next, jumper"
      @size-change="handleSizeChange"
      @current-change="handleCurrentChange"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, defineEmits, defineExpose } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
// import { getRoles, deleteRole } from '@/api/permission'; // 假设的API服务

const emit = defineEmits(['edit-role', 'set-permissions', 'manage-users']);

const roles = ref([]);
const loading = ref(false);
const pagination = ref({
  currentPage: 1,
  pageSize: 10,
  total: 0,
});

// 模拟API调用
const mockApi = {
  getRoles: async (params) => {
    console.log('Fetching roles with params:', params);
    return new Promise(resolve => {
      setTimeout(() => {
        const allRoles = [
          { id: '1', name: '管理员', description: '拥有所有权限' },
          { id: '2', name: '编辑', description: '可以编辑内容' },
          { id: '3', name: '访客', description: '只能查看内容' },
        ];
        const start = (params.page - 1) * params.limit;
        const end = start + params.limit;
        resolve({
          data: {
            items: allRoles.slice(start, end),
            total: allRoles.length,
          },
          code: 200
        });
      }, 500);
    });
  },
  deleteRole: async (id) => {
    console.log('Deleting role with id:', id);
    return new Promise(resolve => {
      setTimeout(() => {
        resolve({ code: 200, message: '删除成功' });
      }, 300);
    });
  }
};

async function fetchRoles() {
  loading.value = true;
  try {
    // const response = await getRoles({ page: pagination.value.currentPage, limit: pagination.value.pageSize });
    const response = await mockApi.getRoles({ page: pagination.value.currentPage, limit: pagination.value.pageSize });
    if (response.data && response.code === 200) {
      roles.value = response.data.items;
      pagination.value.total = response.data.total;
    } else {
      ElMessage.error('获取角色列表失败');
    }
  } catch (error) {
    console.error('Error fetching roles:', error);
    ElMessage.error('获取角色列表失败: ' + error.message);
  } finally {
    loading.value = false;
  }
}

function handleAddRole() {
  emit('edit-role', {}); // 传递空对象表示新增
}

function handleEditRole(role) {
  emit('edit-role', role);
}

function handleSetPermissions(role) {
  emit('set-permissions', role);
}

function handleManageUsers(role) {
  emit('manage-users', role);
}

async function handleDeleteRole(role) {
  try {
    await ElMessageBox.confirm(`确定要删除角色 “${role.name}” 吗？`, '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    });
    // await deleteRole(role.id);
    await mockApi.deleteRole(role.id);
    ElMessage.success('角色删除成功');
    fetchRoles(); // 重新加载列表
  } catch (error) {
    if (error !== 'cancel') {
      console.error('Error deleting role:', error);
      ElMessage.error('角色删除失败: ' + (error.message || ''));
    }
  }
}

function refreshList() {
  fetchRoles();
}

function handleSizeChange(val) {
  pagination.value.pageSize = val;
  fetchRoles();
}

function handleCurrentChange(val) {
  pagination.value.currentPage = val;
  fetchRoles();
}

onMounted(() => {
  fetchRoles();
});

defineExpose({
  refreshList,
});

</script>

<style scoped>
.role-list-container {
  padding: 15px;
}
.toolbar {
  margin-bottom: 15px;
}
</style>