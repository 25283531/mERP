<template>
  <div>
    <el-form :inline="true" @submit.prevent>
      <el-form-item label="类型">
        <el-select v-model="filters.type" placeholder="全部类型" clearable @change="fetchDevices(1)">
          <el-option v-for="item in typeOptions" :key="item.value" :label="item.label" :value="item.value" />
        </el-select>
      </el-form-item>
      <el-form-item label="状态">
        <el-select v-model="filters.status" placeholder="全部状态" clearable @change="fetchDevices(1)">
          <el-option v-for="item in statusOptions" :key="item.value" :label="item.label" :value="item.value" />
        </el-select>
      </el-form-item>
      <el-form-item>
        <el-input v-model="filters.keyword" placeholder="设备名称/编号" clearable @input="fetchDevices(1)" />
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="fetchDevices(1)">查询</el-button>
        <el-button type="success" @click="onCreate">新增设备</el-button>
      </el-form-item>
    </el-form>
    <el-table :data="devices" style="width: 100%; margin-top: 16px;" row-key="id">
      <el-table-column prop="name" label="设备名称" />
      <el-table-column prop="code" label="设备编号" />
      <el-table-column prop="type" label="类型" />
      <el-table-column prop="status" label="状态" />
      <el-table-column prop="switchTime" label="切换时间(min)" />
      <el-table-column label="操作">
        <template #default="{ row }">
          <el-button size="mini" @click="onEdit(row)">编辑</el-button>
          <el-button size="mini" type="danger" @click="onDelete(row)">删除</el-button>
          <el-button size="mini" type="info" @click="onDetail(row)">详情</el-button>
        </template>
      </el-table-column>
    </el-table>
    <el-pagination
      background
      layout="prev, pager, next, total"
      :total="total"
      :page-size="pageSize"
      :current-page="page"
      @current-change="fetchDevices"
      style="margin-top: 16px;"
    />
    <device-form v-if="editingDevice" :device="editingDevice" @close="closeForm" @saved="onSaved" />
    <device-detail v-if="showDetail" :device-id="detailId" @close="showDetail = false" />
  </div>
</template>
<script setup>
import { ref, onMounted } from 'vue';
import { ElMessageBox, ElMessage } from 'element-plus';
import DeviceForm from './DeviceForm.vue';
import DeviceDetail from './DeviceDetail.vue';

const devices = ref([]);
const total = ref(0);
const page = ref(1);
const pageSize = 20;
const filters = ref({ type: '', status: '', keyword: '' });
const typeOptions = [
  { label: 'A类', value: 'A' },
  { label: 'B类', value: 'B' },
  { label: 'C类', value: 'C' }
];
const statusOptions = [
  { label: '空闲', value: 'idle' },
  { label: '运行', value: 'running' },
  { label: '维护', value: 'maintenance' }
];
const editingDevice = ref(null);
const showDetail = ref(false);
const detailId = ref(null);

async function fetchDevices(p = 1) {
  page.value = p;
  const params = new URLSearchParams({
    page: p,
    size: pageSize,
    type: filters.value.type || '',
    status: filters.value.status || '',
    keyword: filters.value.keyword || ''
  });
  const res = await fetch(`/api/v1/devices?${params}`);
  const data = await res.json();
  devices.value = data.items || [];
  total.value = data.total || 0;
}

function onCreate() {
  editingDevice.value = {};
}
function onEdit(row) {
  editingDevice.value = { ...row };
}
function closeForm() {
  editingDevice.value = null;
}
function onSaved() {
  closeForm();
  fetchDevices(page.value);
}
async function onDelete(row) {
  try {
    await ElMessageBox.confirm('确定要删除该设备吗？', '提示', { type: 'warning' });
    await fetch(`/api/v1/devices/${row.id}`, { method: 'DELETE' });
    ElMessage.success('删除成功');
    fetchDevices(page.value);
  } catch {}
}
function onDetail(row) {
  detailId.value = row.id;
  showDetail.value = true;
}
onMounted(() => {
  fetchDevices();
});
</script>
<style scoped></style>