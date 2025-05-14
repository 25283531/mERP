<template>
  <el-dialog
    :model-value="visible"
    :title="`为角色 '${roleName}' 分配用户`"
    width="800px"
    @close="handleClose"
    :close-on-click-modal="false"
  >
    <div class="user-role-container">
      <el-transfer
        v-model="assignedUserKeys"
        filterable
        :filter-placeholder="'搜索用户'"
        :data="allUsers"
        :titles="['所有用户', '已分配用户']"
        :props="{ key: 'id', label: 'name' }"
        :left-default-checked="[]"
        :right-default-checked="[]"
        style="width: 100%; height: 400px;"
      >
        <template #default="{ option }">
          <span>{{ option.name }} ({{ option.email }})</span>
        </template>
      </el-transfer>
    </div>
    <template #footer>
      <span class="dialog-footer">
        <el-button @click="handleClose">取消</el-button>
        <el-button type="primary" @click="handleSaveUserRoles" :loading="loading">保存</el-button>
      </span>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, watch, defineProps, defineEmits, onMounted } from 'vue';
import { ElMessage } from 'element-plus';
// import { getAllUsers, getRoleUsers, updateRoleUsers } from '@/api/permission'; // 假设的API服务

const props = defineProps({
  visible: {
    type: Boolean,
    default: false,
  },
  roleId: {
    type: String,
    required: true,
  },
  roleName: {
    type: String,
    default: '',
  },
});

const emit = defineEmits(['close', 'users-saved']);

const allUsers = ref([]); // { id: string, name: string, email: string }
const assignedUserKeys = ref([]); // array of user ids
const loading = ref(false);

// 模拟API
const mockApi = {
  getAllUsers: async () => {
    return new Promise(resolve => {
      setTimeout(() => {
        resolve({
          code: 200,
          data: [
            { id: 'user1', name: '张三', email: 'zhangsan@example.com' },
            { id: 'user2', name: '李四', email: 'lisi@example.com' },
            { id: 'user3', name: '王五', email: 'wangwu@example.com' },
            { id: 'user4', name: '赵六', email: 'zhaoliu@example.com' },
            { id: 'user5', name: '孙七', email: 'sunqi@example.com' },
          ]
        });
      }, 300);
    });
  },
  getRoleUsers: async (roleId) => {
    console.log('Fetching users for roleId:', roleId);
    let userKeys = [];
    if (roleId === '1') { // 管理员
      userKeys = ['user1', 'user2'];
    } else if (roleId === '2') { // 编辑
      userKeys = ['user3'];
    }
    return new Promise(resolve => {
      setTimeout(() => {
        resolve({ code: 200, data: userKeys });
      }, 200);
    });
  },
  updateRoleUsers: async (roleId, userIds) => {
    console.log('Updating users for roleId:', roleId, 'with userIds:', userIds);
    return new Promise(resolve => {
      setTimeout(() => {
        resolve({ code: 200, message: '用户分配成功' });
      }, 500);
    });
  }
};

async function fetchAllUsersList() {
  try {
    // const response = await getAllUsers();
    const response = await mockApi.getAllUsers();
    if (response.code === 200 && response.data) {
      allUsers.value = response.data;
    } else {
      ElMessage.error('获取所有用户列表失败');
    }
  } catch (error) {
    console.error('Error fetching all users:', error);
    ElMessage.error('获取所有用户列表失败: ' + error.message);
  }
}

async function fetchAssignedUsers() {
  if (!props.roleId) return;
  try {
    // const response = await getRoleUsers(props.roleId);
    const response = await mockApi.getRoleUsers(props.roleId);
    if (response.code === 200 && response.data) {
      assignedUserKeys.value = response.data;
    } else {
      ElMessage.error('获取角色已分配用户失败');
    }
  } catch (error) {
    console.error('Error fetching assigned users:', error);
    ElMessage.error('获取角色已分配用户失败: ' + error.message);
  }
}

watch(() => props.visible, (newVal) => {
  if (newVal && props.roleId) {
    fetchAllUsersList().then(() => {
      fetchAssignedUsers();
    });
  } else {
    // Reset when dialog is hidden or roleId is not present
    allUsers.value = [];
    assignedUserKeys.value = [];
  }
});

function handleClose() {
  emit('close');
}

async function handleSaveUserRoles() {
  loading.value = true;
  try {
    // const response = await updateRoleUsers(props.roleId, assignedUserKeys.value);
    const response = await mockApi.updateRoleUsers(props.roleId, assignedUserKeys.value);
    if (response.code === 200) {
      ElMessage.success('用户分配成功');
      emit('users-saved');
      handleClose();
    } else {
      ElMessage.error(response.message || '用户分配失败');
    }
  } catch (error) {
    console.error('Error saving user roles:', error);
    ElMessage.error('用户分配失败: ' + error.message);
  } finally {
    loading.value = false;
  }
}

onMounted(() => {
  if (props.visible && props.roleId) {
    fetchAllUsersList().then(() => {
      fetchAssignedUsers();
    });
  }
});

</script>

<style scoped>
.user-role-container {
  display: flex;
  justify-content: center;
  align-items: center;
}

/* Element Plus Transfer component might need some style adjustments for height */
:deep(.el-transfer-panel) {
  height: 400px; /* Match the height of el-transfer */
}
:deep(.el-transfer-panel__list.is-filterable) {
    height: calc(100% - 62px); /* Adjust based on your filter input height */
}

.dialog-footer {
  text-align: right;
}
</style>