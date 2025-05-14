<template>
  <el-container class="permission-module-container">
    <el-main class="permission-main">
      <el-card shadow="never" class="full-height-card">
        <template #header>
          <div class="card-header">
            <span>角色与权限管理</span>
            <el-button style="margin-left: auto;" @click="refreshRoleList" :icon="RefreshRight">刷新角色</el-button>
          </div>
        </template>
        <RoleList 
          ref="roleListRef"
          @edit-role="handleOpenRoleForm"
          @set-permissions="handleOpenPermissionTree"
          @manage-users="handleOpenUserRoleDialog"
        />
      </el-card>
    </el-main>

    <RoleForm 
      :visible="roleFormVisible"
      :role="currentRole"
      @close="handleCloseRoleForm"
      @saved="handleRoleSaved"
    />

    <el-dialog 
      v-model="permissionTreeVisible"
      :title="`为角色 '${currentRoleForPermission?.name}' 分配权限`"
      width="600px"
      @close="handleClosePermissionTree"
      :close-on-click-modal="false"
      destroy-on-close
    >
      <PermissionTree 
        v-if="permissionTreeVisible" 
        :role-id="currentRoleForPermission?.id || ''"
        :role-name="currentRoleForPermission?.name || ''"
        @close="handleClosePermissionTree"
        @permissions-saved="handlePermissionsSaved"
      />
    </el-dialog>

    <UserRole
      :visible="userRoleDialogVisible"
      :role-id="currentRoleForUserAssignment?.id || ''"
      :role-name="currentRoleForUserAssignment?.name || ''"
      @close="handleCloseUserRoleDialog"
      @users-saved="handleUsersSaved"
    />

  </el-container>
</template>

<script setup>
import { ref } from 'vue';
import RoleList from './RoleList.vue';
import RoleForm from './RoleForm.vue';
import PermissionTree from './PermissionTree.vue';
import UserRole from './UserRole.vue';
import { RefreshRight } from '@element-plus/icons-vue';
import { ElMessage } from 'element-plus';

const roleListRef = ref(null);

const roleFormVisible = ref(false);
const currentRole = ref({}); // For RoleForm

const permissionTreeVisible = ref(false);
const currentRoleForPermission = ref(null); // For PermissionTree title and props

const userRoleDialogVisible = ref(false);
const currentRoleForUserAssignment = ref(null); // For UserRole title and props

function refreshRoleList() {
  if (roleListRef.value) {
    roleListRef.value.refreshList();
    ElMessage.success('角色列表已刷新');
  }
}

// RoleForm handlers
function handleOpenRoleForm(role) {
  currentRole.value = role ? { ...role } : {}; // Pass a copy or empty object for new
  roleFormVisible.value = true;
}

function handleCloseRoleForm() {
  roleFormVisible.value = false;
}

function handleRoleSaved() {
  roleFormVisible.value = false;
  refreshRoleList(); 
  // Potentially refresh user auth if current user's roles changed
  // store.dispatch('auth/fetchUser'); 
}

// PermissionTree handlers
function handleOpenPermissionTree(role) {
  if (!role || !role.id) {
    ElMessage.warning('请选择一个有效的角色');
    return;
  }
  currentRoleForPermission.value = { ...role };
  permissionTreeVisible.value = true;
}

function handleClosePermissionTree() {
  permissionTreeVisible.value = false;
  currentRoleForPermission.value = null;
}

function handlePermissionsSaved() {
  permissionTreeVisible.value = false;
  currentRoleForPermission.value = null;
  ElMessage.success('角色权限已更新');
  // Refresh user auth if current user's permissions changed
  // store.dispatch('auth/fetchUser'); 
}

// UserRole dialog handlers
function handleOpenUserRoleDialog(role) {
  if (!role || !role.id) {
    ElMessage.warning('请选择一个有效的角色');
    return;
  }
  currentRoleForUserAssignment.value = { ...role };
  userRoleDialogVisible.value = true;
}

function handleCloseUserRoleDialog() {
  userRoleDialogVisible.value = false;
  currentRoleForUserAssignment.value = null;
}

function handleUsersSaved() {
  userRoleDialogVisible.value = false;
  currentRoleForUserAssignment.value = null;
  ElMessage.success('角色用户分配已更新');
  // Potentially refresh user auth if current user's roles changed
  // store.dispatch('auth/fetchUser'); 
}

</script>

<style scoped>
.permission-module-container {
  height: calc(100vh - 50px); /* Adjust 50px based on your header/navbar height */
  padding: 15px;
  box-sizing: border-box;
}

.permission-main {
  padding: 0;
  height: 100%;
}

.full-height-card {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.full-height-card :deep(.el-card__body) {
  flex-grow: 1;
  overflow-y: auto;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>