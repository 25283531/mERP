<template>
  <el-container class="org-module-container">
    <el-aside width="300px" class="org-aside">
      <el-card shadow="never" class="full-height-card">
        <template #header>
          <div class="card-header">
            <span>部门结构</span>
          </div>
        </template>
        <OrgTree @node-click="handleDeptNodeClick" ref="orgTreeRef" />
      </el-card>
    </el-aside>
    <el-main class="org-main">
      <el-card shadow="never" class="full-height-card">
        <template #header>
          <div class="card-header">
            <span>部门成员</span>
            <el-button style="margin-left: auto;" @click="refreshAllData" :icon="RefreshRight">刷新数据</el-button>
          </div>
        </template>
        <MemberList 
          :department-id="selectedDepartmentId" 
          :department-name="selectedDepartmentName"
          @add-member="handleAddMember"
          @edit-member="handleEditMember"
          @import-members="handleOpenImportForm"
          ref="memberListRef"
        />
      </el-card>
    </el-main>

    <MemberForm 
      v-if="memberFormVisible"
      :visible="memberFormVisible"
      :member="currentMember"
      :is-batch-import="isBatchImportMode"
      :department-id="formTargetDepartmentId"
      :department-name="formTargetDepartmentName"
      @close="closeMemberForm"
      @saved="handleMemberSaved"
      @imported="handleMembersImported"
    />
  </el-container>
</template>

<script setup>
import { ref } from 'vue';
import OrgTree from './OrgTree.vue';
import MemberList from './MemberList.vue';
import MemberForm from './MemberForm.vue';
import { RefreshRight } from '@element-plus/icons-vue';
import { ElMessage } from 'element-plus';

const orgTreeRef = ref(null);
const memberListRef = ref(null);

const selectedDepartmentId = ref(null);
const selectedDepartmentName = ref('');

const memberFormVisible = ref(false);
const currentMember = ref({});
const isBatchImportMode = ref(false);
const formTargetDepartmentId = ref(null); // For add/import, this is the target department
const formTargetDepartmentName = ref('');

function handleDeptNodeClick(data) {
  selectedDepartmentId.value = data.id;
  selectedDepartmentName.value = data.name;
  // MemberList will watch departmentId and fetch members automatically
}

function handleAddMember(deptId) {
  if (!selectedDepartmentId.value && !deptId) {
    ElMessage.warning('请先选择一个部门。');
    return;
  }
  currentMember.value = {}; // Clear for new member
  isBatchImportMode.value = false;
  formTargetDepartmentId.value = deptId || selectedDepartmentId.value;
  formTargetDepartmentName.value = findDepartmentNameById(formTargetDepartmentId.value) || selectedDepartmentName.value;
  memberFormVisible.value = true;
}

function handleEditMember(member) {
  currentMember.value = { ...member };
  isBatchImportMode.value = false;
  // departmentId for editing is part of the member object, or can be the currently selected one if not present
  formTargetDepartmentId.value = member.departmentId || selectedDepartmentId.value;
  formTargetDepartmentName.value = findDepartmentNameById(formTargetDepartmentId.value) || selectedDepartmentName.value;
  memberFormVisible.value = true;
}

function handleOpenImportForm(deptId) {
   if (!selectedDepartmentId.value && !deptId) {
    ElMessage.warning('请先选择一个部门以导入成员。');
    return;
  }
  isBatchImportMode.value = true;
  currentMember.value = {}; // Not used in batch import but good to clear
  formTargetDepartmentId.value = deptId || selectedDepartmentId.value;
  formTargetDepartmentName.value = findDepartmentNameById(formTargetDepartmentId.value) || selectedDepartmentName.value;
  memberFormVisible.value = true;
}

function closeMemberForm() {
  memberFormVisible.value = false;
  currentMember.value = {};
  isBatchImportMode.value = false;
}

function handleMemberSaved() {
  // MemberForm emits 'saved', MemberList should refresh itself or we trigger it
  if (memberListRef.value) {
    memberListRef.value.refreshList();
  }
  closeMemberForm();
}

function handleMembersImported() {
  if (memberListRef.value) {
    memberListRef.value.refreshList();
  }
  closeMemberForm();
}

function refreshAllData() {
  if (orgTreeRef.value) {
    orgTreeRef.value.refreshTree(); // This will also clear pending changes in tree
  }
  if (memberListRef.value && selectedDepartmentId.value) {
    memberListRef.value.refreshList();
  } else if (!selectedDepartmentId.value) {
    // Clear member list if no department is selected after tree refresh
    if (memberListRef.value) memberListRef.value.members = []; 
  }
  ElMessage.success('数据已刷新');
}

// Helper to find department name if not directly available (e.g. when adding member to a specific dept from tree)
// This is a simplified version. A more robust solution might involve a store or better state management for department names.
function findDepartmentNameById(deptId) {
  if (!orgTreeRef.value || !orgTreeRef.value.treeData) return '';
  
  function searchInTree(nodes, id) {
    for (const node of nodes) {
      if (node.id === id) return node.name;
      if (node.children) {
        const foundName = searchInTree(node.children, id);
        if (foundName) return foundName;
      }
    }
    return null;
  }
  return searchInTree(orgTreeRef.value.treeData, deptId);
}

</script>

<style scoped>
.org-module-container {
  height: calc(100vh - 120px); /* Adjust based on your layout's header/footer */
  padding: 10px;
  background-color: #f4f4f5;
}

.org-aside {
  background-color: #fff;
  border-radius: 4px;
  margin-right: 10px;
  height: 100%;
}

.org-main {
  background-color: #fff;
  border-radius: 4px;
  padding: 0; /* el-card will provide padding */
  height: 100%;
}

.full-height-card {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.full-height-card > :deep(.el-card__header) {
  flex-shrink: 0;
}

.full-height-card > :deep(.el-card__body) {
  flex-grow: 1;
  overflow-y: auto;
  padding: 15px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>