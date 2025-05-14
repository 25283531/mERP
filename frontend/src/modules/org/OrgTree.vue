<template>
  <div class="org-tree-container">
    <div class="toolbar">
      <el-input v-model="filterText" placeholder="筛选部门" style="width: 200px; margin-right: 10px;" />
      <el-button type="primary" @click="handleAddTopLevelDept">新增一级部门</el-button>
      <el-button type="success" @click="batchSubmitChanges" :disabled="!hasChanges">批量保存</el-button>
      <el-button @click="refreshTree">刷新</el-button>
    </div>
    <el-tree
      ref="treeRef"
      :data="treeData"
      :props="defaultProps"
      node-key="id"
      show-checkbox
      draggable
      :allow-drop="allowDrop"
      :allow-drag="allowDrag"
      :filter-node-method="filterNode"
      @node-drop="handleNodeDrop"
      @check-change="handleCheckChange"
    >
      <template #default="{ node, data }">
        <span class="custom-tree-node">
          <span>{{ node.label }}</span>
          <span>
            <el-button type="text" size="small" @click.stop="() => append(data)">新增子部门</el-button>
            <el-button type="text" size="small" @click.stop="() => edit(data)">编辑</el-button>
            <el-button type="text" size="small" @click.stop="() => remove(node, data)">删除</el-button>
          </span>
        </span>
      </template>
    </el-tree>

    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="30%">
      <el-form :model="form" ref="formRef" label-width="80px">
        <el-form-item label="部门名称" prop="name" :rules="[{ required: true, message: '请输入部门名称', trigger: 'blur' }]">
          <el-input v-model="form.name" />
        </el-form-item>
        <el-form-item label="部门编码" prop="code">
          <el-input v-model="form.code" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="submitForm">确定</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, watch, nextTick, onMounted } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';

const treeRef = ref(null);
const filterText = ref('');
const treeData = ref([]);
const defaultProps = {
  children: 'children',
  label: 'name',
};
const dialogVisible = ref(false);
const dialogTitle = ref('');
const form = ref({ id: null, name: '', code: '', parentId: null });
const formRef = ref(null);
const currentEditNode = ref(null);
const pendingChanges = ref({ added: [], updated: [], deleted: [] });
const hasChanges = ref(false);

watch(filterText, (val) => {
  treeRef.value.filter(val);
});

const filterNode = (value, data) => {
  if (!value) return true;
  return data.name.includes(value);
};

async function fetchDepartments() {
  try {
    const response = await fetch('/api/v1/org/departments');
    if (!response.ok) throw new Error('Failed to fetch departments');
    const data = await response.json();
    treeData.value = arrayToTree(data); // Assuming API returns flat list, needs conversion
  } catch (error) {
    ElMessage.error(`获取部门数据失败: ${error.message}`);
    treeData.value = []; // Fallback to empty or example data
  }
}

function arrayToTree(list, parentId = null) {
  return list
    .filter(item => item.parentId === parentId)
    .map(item => ({
      ...item,
      children: arrayToTree(list, item.id)
    }));
}

function refreshTree() {
  fetchDepartments();
  pendingChanges.value = { added: [], updated: [], deleted: [] };
  hasChanges.value = false;
  ElMessage.success('部门树已刷新');
}

function handleAddTopLevelDept() {
  dialogTitle.value = '新增一级部门';
  form.value = { id: null, name: '', code: '', parentId: null };
  currentEditNode.value = null;
  dialogVisible.value = true;
  nextTick(() => formRef.value?.resetFields());
}

function append(data) {
  dialogTitle.value = '新增子部门';
  form.value = { id: null, name: '', code: '', parentId: data.id };
  currentEditNode.value = null; // Not editing, but creating under this parent
  dialogVisible.value = true;
  nextTick(() => formRef.value?.resetFields());
}

function edit(data) {
  dialogTitle.value = '编辑部门';
  form.value = { ...data }; // Create a copy to avoid direct mutation
  currentEditNode.value = data; // Keep track of the original node data for update logic
  dialogVisible.value = true;
  nextTick(() => formRef.value?.resetFields());
}

async function remove(node, data) {
  try {
    await ElMessageBox.confirm(`确定删除部门 "${data.name}"?`, '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    });
    // Add to pending changes instead of direct API call
    if (data.id) { // Only mark for deletion if it's an existing department
        pendingChanges.value.deleted.push(data.id);
    }
    // Remove from treeData locally
    const parent = node.parent;
    const children = parent.data.children || parent.data;
    const index = children.findIndex(d => d.id === data.id);
    children.splice(index, 1);
    hasChanges.value = true;
    ElMessage.success('部门已标记为删除');
  } catch (e) {
    // Catch cancellation of ElMessageBox
    if (e !== 'cancel') {
        ElMessage.info('取消删除');
    }
  }
}

function submitForm() {
  formRef.value.validate(async (valid) => {
    if (valid) {
      if (form.value.id) { // Editing existing department
        // Update in pendingChanges
        const existingIndex = pendingChanges.value.updated.findIndex(d => d.id === form.value.id);
        if (existingIndex > -1) {
          pendingChanges.value.updated[existingIndex] = { ...form.value };
        } else {
          pendingChanges.value.updated.push({ ...form.value });
        }
        // Update treeData locally
        if (currentEditNode.value) {
            Object.assign(currentEditNode.value, form.value);
        }
      } else { // Adding new department
        const newDept = {
          ...form.value,
          id: `temp-${Date.now()}` // Temporary ID for new nodes
        };
        pendingChanges.value.added.push(newDept);
        // Add to treeData locally
        if (form.value.parentId) {
          const parentNode = findNode(treeData.value, form.value.parentId);
          if (parentNode) {
            if (!parentNode.children) parentNode.children = [];
            parentNode.children.push(newDept);
          }
        } else {
          treeData.value.push(newDept);
        }
      }
      hasChanges.value = true;
      dialogVisible.value = false;
      ElMessage.success('部门信息已暂存');
    } else {
      return false;
    }
  });
}

function findNode(nodes, id) {
    for (const node of nodes) {
        if (node.id === id) return node;
        if (node.children) {
            const found = findNode(node.children, id);
            if (found) return found;
        }
    }
    return null;
}

async function batchSubmitChanges() {
  if (!hasChanges.value) {
    ElMessage.info('没有需要保存的更改');
    return;
  }
  try {
    // Replace temporary IDs in added items before sending to backend
    const payload = {
        added: pendingChanges.value.added.map(item => ({ ...item, id: undefined })),
        updated: pendingChanges.value.updated,
        deleted: pendingChanges.value.deleted
    };

    const response = await fetch('/api/v1/org/departments', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.message || '批量保存失败');
    }
    ElMessage.success('更改已成功保存到服务器');
    await fetchDepartments(); // Refresh tree from server
    pendingChanges.value = { added: [], updated: [], deleted: [] };
    hasChanges.value = false;
  } catch (error) {
    ElMessage.error(`保存失败: ${error.message}`);
  }
}

// Drag and drop handlers
const allowDrop = (draggingNode, dropNode, type) => {
  // Disallow dropping on itself or making a parent its own child
  if (dropNode.data.id === draggingNode.data.id) return false;
  // More complex cycle detection might be needed for deeper nesting
  return true;
};

const allowDrag = (draggingNode) => {
  return true; // Allow all nodes to be draggable by default
};

const handleNodeDrop = (draggingNode, dropNode, dropType, ev) => {
  // dropType can be 'before', 'after', 'inner'
  console.log('tree drop: ', draggingNode.data.name, dropNode.data.name, dropType);
  // Update parentId for the dragged node
  let newParentId = null;
  if (dropType === 'inner') {
    newParentId = dropNode.data.id;
  } else if (dropType === 'before' || dropType === 'after') {
    newParentId = dropNode.parent.data.id || null; // Root if parent is null
  }

  const draggedItem = { ...draggingNode.data, parentId: newParentId };

  // Add to updated list or move from added if it was a new node
  const existingAddedIndex = pendingChanges.value.added.findIndex(d => d.id === draggedItem.id);
  if (existingAddedIndex > -1) {
    pendingChanges.value.added[existingAddedIndex] = draggedItem;
  } else {
    const existingUpdatedIndex = pendingChanges.value.updated.findIndex(d => d.id === draggedItem.id);
    if (existingUpdatedIndex > -1) {
        pendingChanges.value.updated[existingUpdatedIndex] = draggedItem;
    } else {
        pendingChanges.value.updated.push(draggedItem);
    }
  }
  hasChanges.value = true;
  ElMessage.info(`部门 "${draggingNode.data.name}" 已移动，请批量保存以生效。`);
  // Note: ElTree handles the visual update. We just need to record the change.
};

const handleCheckChange = (data, checked, indeterminate) => {
    // console.log(data, checked, indeterminate);
    // Potentially useful for batch operations on selected nodes
};

onMounted(() => {
  fetchDepartments();
});

</script>

<style scoped>
.org-tree-container {
  padding: 20px;
}
.toolbar {
  margin-bottom: 15px;
}
.custom-tree-node {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 14px;
  padding-right: 8px;
}
.el-button + .el-button {
  margin-left: 8px;
}
</style>