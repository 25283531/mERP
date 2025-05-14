<template>
  <div class="member-list-container">
    <div class="toolbar">
      <el-button type="primary" @click="handleAddMember">新增成员</el-button>
      <el-button @click="handleImportMembers">批量导入成员</el-button>
      <el-button @click="refreshList">刷新列表</el-button>
      <span v-if="selectedDeptName" class="current-dept-display">当前部门: {{ selectedDeptName }}</span>
    </div>
    <el-table :data="members" v-loading="loading" border style="width: 100%">
      <el-table-column prop="name" label="姓名" width="120" />
      <el-table-column prop="employeeId" label="工号" width="100" />
      <el-table-column prop="position" label="职位" width="150" />
      <el-table-column prop="email" label="邮箱" width="180" />
      <el-table-column prop="phone" label="电话" width="150" />
      <el-table-column label="操作" width="180" fixed="right">
        <template #default="{ row }">
          <el-button type="text" size="small" @click="handleEditMember(row)">编辑</el-button>
          <el-button type="text" size="small" @click="handleDeleteMember(row)">删除</el-button>
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
import { ref, watch, defineProps, defineEmits, onMounted } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';

const props = defineProps({
  departmentId: { type: [String, Number], default: null },
  departmentName: { type: String, default: '' }
});

const emit = defineEmits(['edit-member', 'add-member', 'import-members']);

const members = ref([]);
const loading = ref(false);
const selectedDeptName = ref(props.departmentName);
const pagination = ref({
  currentPage: 1,
  pageSize: 10,
  total: 0,
});

watch(() => props.departmentId, (newDeptId) => {
  if (newDeptId) {
    selectedDeptName.value = props.departmentName;
    fetchMembers();
  } else {
    members.value = [];
    pagination.value.total = 0;
    selectedDeptName.value = '';
  }
});

watch(() => props.departmentName, (newName) => {
  selectedDeptName.value = newName;
});

async function fetchMembers() {
  if (!props.departmentId) {
    members.value = [];
    pagination.value.total = 0;
    return;
  }
  loading.value = true;
  try {
    const response = await fetch(`/api/v1/org/members?deptId=${props.departmentId}&page=${pagination.value.currentPage}&pageSize=${pagination.value.pageSize}`);
    if (!response.ok) throw new Error('Failed to fetch members');
    const data = await response.json();
    members.value = data.list;
    pagination.value.total = data.total;
  } catch (error) {
    ElMessage.error(`获取成员列表失败: ${error.message}`);
    members.value = [];
    pagination.value.total = 0;
  }
  loading.value = false;
}

function refreshList() {
  if (props.departmentId) {
    fetchMembers();
    ElMessage.success('成员列表已刷新');
  } else {
    ElMessage.info('请先选择一个部门');
  }
}

function handleAddMember() {
  if (!props.departmentId) {
    ElMessage.warning('请先选择一个部门以添加成员。');
    return;
  }
  emit('add-member', props.departmentId);
}

function handleEditMember(member) {
  emit('edit-member', member);
}

async function handleDeleteMember(member) {
  try {
    await ElMessageBox.confirm(`确定删除成员 "${member.name}"?`, '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    });
    const response = await fetch(`/api/v1/org/members/${member.id}`, { method: 'DELETE' });
    if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.message || '删除成员失败');
    }
    ElMessage.success('成员删除成功');
    fetchMembers(); // Refresh list
  } catch (error) {
    if (error !== 'cancel') {
        ElMessage.error(`删除失败: ${error.message}`);
    }
  }
}

function handleImportMembers() {
  if (!props.departmentId) {
    ElMessage.warning('请先选择一个部门以导入成员。');
    return;
  }
  emit('import-members', props.departmentId);
}

function handleSizeChange(val) {
  pagination.value.pageSize = val;
  fetchMembers();
}

function handleCurrentChange(val) {
  pagination.value.currentPage = val;
  fetchMembers();
}

onMounted(() => {
  if (props.departmentId) {
    fetchMembers();
  }
});

// Expose fetchMembers to be called by parent if needed
defineExpose({ fetchMembers, refreshList });

</script>

<style scoped>
.member-list-container {
  padding: 15px;
}
.toolbar {
  margin-bottom: 15px;
  display: flex;
  align-items: center;
}
.current-dept-display {
  margin-left: auto;
  font-size: 14px;
  color: #606266;
}
.el-button + .el-button {
  margin-left: 8px;
}
</style>