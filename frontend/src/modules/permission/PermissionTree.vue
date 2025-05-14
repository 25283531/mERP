<template>
  <div class="permission-tree-container">
    <el-input v-model="filterText" placeholder="筛选权限" style="margin-bottom: 10px;" />
    <el-tree
      ref="treeRef"
      :data="treeData"
      :props="defaultProps"
      show-checkbox
      node-key="id"
      :default-expanded-keys="expandedKeys"
      :default-checked-keys="checkedKeys"
      :filter-node-method="filterNode"
      @check-change="handleCheckChange"
    />
    <div style="margin-top: 20px; text-align: right;">
      <el-button @click="handleCancel">取消</el-button>
      <el-button type="primary" @click="handleSavePermissions" :loading="loading">保存权限</el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, defineProps, defineEmits, nextTick } from 'vue';
import { ElMessage } from 'element-plus';
// import { getPermissions, getRolePermissions, updateRolePermissions } from '@/api/permission'; // 假设的API服务

const props = defineProps({
  roleId: {
    type: String,
    required: true,
  },
  roleName: {
    type: String,
    default: '',
  }
});

const emit = defineEmits(['close', 'permissions-saved']);

const treeRef = ref(null);
const filterText = ref('');
const treeData = ref([]);
const defaultProps = {
  children: 'children',
  label: 'name',
};
const expandedKeys = ref([]);
const checkedKeys = ref([]); 
const loading = ref(false);

// 模拟API
const mockApi = {
  getPermissions: async () => {
    return new Promise(resolve => {
      setTimeout(() => {
        resolve({
          code: 200,
          data: [
            { id: '1', name: '系统管理', children: [
              { id: '1-1', name: '用户管理', children: [
                { id: '1-1-1', name: '查看用户' },
                { id: '1-1-2', name: '新增用户' },
                { id: '1-1-3', name: '编辑用户' },
                { id: '1-1-4', name: '删除用户' },
              ]},
              { id: '1-2', name: '角色管理', children: [
                { id: '1-2-1', name: '查看角色' },
                { id: '1-2-2', name: '新增角色' },
                { id: '1-2-3', name: '编辑角色' },
                { id: '1-2-4', name: '删除角色' },
                { id: '1-2-5', name: '分配权限' },
              ]},
            ]},
            { id: '2', name: '内容管理', children: [
              { id: '2-1', name: '文章管理' },
              { id: '2-2', name: '评论管理' },
            ]}
          ]
        });
      }, 300);
    });
  },
  getRolePermissions: async (roleId) => {
    console.log('Fetching permissions for roleId:', roleId);
    // 模拟不同角色有不同权限
    let permissions = [];
    if (roleId === '1') { // 管理员
      permissions = ['1-1-1', '1-1-2', '1-1-3', '1-1-4', '1-2-1', '1-2-2', '1-2-3', '1-2-4', '1-2-5', '2-1', '2-2'];
    } else if (roleId === '2') { // 编辑
      permissions = ['1-1-1', '1-2-1', '2-1', '2-2'];
    }
    return new Promise(resolve => {
      setTimeout(() => {
        resolve({ code: 200, data: permissions });
      }, 200);
    });
  },
  updateRolePermissions: async (roleId, permissionIds) => {
    console.log('Updating permissions for roleId:', roleId, 'with permissions:', permissionIds);
    return new Promise(resolve => {
      setTimeout(() => {
        resolve({ code: 200, message: '权限更新成功' });
      }, 500);
    });
  }
};

watch(filterText, (val) => {
  treeRef.value.filter(val);
});

function filterNode(value, data) {
  if (!value) return true;
  return data.name.includes(value);
}

async function fetchAllPermissions() {
  try {
    // const response = await getPermissions();
    const response = await mockApi.getPermissions();
    if (response.code === 200 && response.data) {
      treeData.value = response.data;
      // 默认展开所有一级节点
      expandedKeys.value = response.data.map(node => node.id);
    } else {
      ElMessage.error('获取权限列表失败');
    }
  } catch (error) {
    console.error('Error fetching all permissions:', error);
    ElMessage.error('获取权限列表失败: ' + error.message);
  }
}

async function fetchRolePermissions() {
  if (!props.roleId) return;
  try {
    // const response = await getRolePermissions(props.roleId);
    const response = await mockApi.getRolePermissions(props.roleId);
    if (response.code === 200 && response.data) {
      checkedKeys.value = response.data;
      nextTick(() => {
        if (treeRef.value) {
            // 清空之前的选中状态，然后设置新的选中状态
            treeRef.value.setCheckedKeys([], false); // false表示不触发check-change事件
            treeRef.value.setCheckedKeys(response.data, false);
        }
      });
    } else {
      ElMessage.error('获取角色权限失败');
    }
  } catch (error) {
    console.error('Error fetching role permissions:', error);
    ElMessage.error('获取角色权限失败: ' + error.message);
  }
}

function handleCheckChange(data, checked, indeterminate) {
  // console.log(data, checked, indeterminate);
  // The checkedKeys will be automatically updated by the tree component
}

async function handleSavePermissions() {
  loading.value = true;
  try {
    const currentCheckedKeys = treeRef.value.getCheckedKeys();
    const halfCheckedKeys = treeRef.value.getHalfCheckedKeys();
    const allSelectedKeys = [...currentCheckedKeys, ...halfCheckedKeys];
    
    // const response = await updateRolePermissions(props.roleId, allSelectedKeys);
    const response = await mockApi.updateRolePermissions(props.roleId, allSelectedKeys);
    if (response.code === 200) {
      ElMessage.success('权限保存成功');
      emit('permissions-saved');
      emit('close');
    } else {
      ElMessage.error(response.message || '权限保存失败');
    }
  } catch (error) {
    console.error('Error saving permissions:', error);
    ElMessage.error('权限保存失败: ' + error.message);
  } finally {
    loading.value = false;
  }
}

function handleCancel() {
  emit('close');
}

function resetTree() {
    if (treeRef.value) {
        treeRef.value.setCheckedKeys([], false);
    }
    filterText.value = '';
}

// Watch for roleId changes to re-fetch permissions
watch(() => props.roleId, (newRoleId) => {
  resetTree();
  if (newRoleId) {
    fetchAllPermissions().then(() => {
        fetchRolePermissions();
    });
  } else {
      treeData.value = [];
      checkedKeys.value = [];
  }
}, { immediate: true });


</script>

<style scoped>
.permission-tree-container {
  padding: 10px;
  min-height: 300px; /* Ensure it has some height */
}
</style>