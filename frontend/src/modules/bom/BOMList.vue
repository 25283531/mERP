<template>
  <div>
    <el-input v-model="search" placeholder="搜索BOM" style="width: 300px; margin-bottom: 16px;" @input="fetchBOMs(1)" clearable />
    <el-table :data="bomTree" style="width: 100%" row-key="id" :expand-row-keys="expandedKeys" :tree-props="{children: 'children', hasChildren: 'hasChildren'}" :default-expand-all="false">
      <el-table-column prop="name" label="物料名称" />
      <el-table-column prop="code" label="物料编码" />
      <el-table-column prop="quantity" label="数量" />
      <el-table-column label="操作">
        <template #default="{ row }">
          <el-button size="mini" @click="editBOM(row)">编辑</el-button>
          <el-button size="mini" type="danger" @click="deleteBOM(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
    <el-pagination
      background
      layout="prev, pager, next, total"
      :total="total"
      :page-size="pageSize"
      :current-page="page"
      @current-change="fetchBOMs"
      style="margin-top: 16px;"
    />
    <bom-editor v-if="editingBOM" :bom="editingBOM" @close="editingBOM = null; fetchBOMs(page)" />
  </div>
</template>
<script setup>
import { ref, onMounted } from 'vue';
import { ElMessageBox, ElMessage } from 'element-plus';
import BOMEditor from './BOMEditor.vue';

const search = ref('');
const bomTree = ref([]);
const page = ref(1);
const pageSize = 20;
const total = ref(0);
const expandedKeys = ref([]);
const editingBOM = ref(null);

async function fetchBOMs(p = 1) {
  page.value = p;
  const params = new URLSearchParams({ page: p, pageSize, search: search.value });
  const res = await fetch(`/api/v1/bom?${params}`);
  const data = await res.json();
  bomTree.value = data.items;
  total.value = data.total;
}

function editBOM(row) {
  editingBOM.value = { ...row };
}

async function deleteBOM(row) {
  try {
    await ElMessageBox.confirm('确定要删除该BOM吗？', '提示', { type: 'warning' });
    await fetch(`/api/v1/bom/${row.id}`, { method: 'DELETE' });
    ElMessage.success('删除成功');
    fetchBOMs(page.value);
  } catch {}
}

onMounted(() => {
  fetchBOMs();
});
</script>
<style scoped>
</style>