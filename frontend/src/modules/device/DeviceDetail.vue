<template>
  <el-dialog v-model="visible" title="设备详情" width="800px" @close="onClose">
    <el-descriptions :column="2" border>
      <el-descriptions-item label="设备名称">{{ device.name }}</el-descriptions-item>
      <el-descriptions-item label="设备编号">{{ device.code }}</el-descriptions-item>
      <el-descriptions-item label="类型">{{ device.type }}</el-descriptions-item>
      <el-descriptions-item label="状态">{{ device.status }}</el-descriptions-item>
      <el-descriptions-item label="切换时间(min)">{{ device.switchTime }}</el-descriptions-item>
    </el-descriptions>
    <el-divider>关联排产任务</el-divider>
    <el-table :data="tasks" style="width: 100%" row-key="id">
      <el-table-column prop="name" label="任务名称" />
      <el-table-column prop="status" label="状态" />
      <el-table-column prop="startTime" label="开始时间" />
      <el-table-column prop="endTime" label="结束时间" />
    </el-table>
    <el-pagination
      background
      layout="prev, pager, next, total"
      :total="total"
      :page-size="pageSize"
      :current-page="page"
      @current-change="fetchTasks"
      style="margin-top: 16px;"
    />
    <template #footer>
      <el-button @click="onClose">关闭</el-button>
    </template>
  </el-dialog>
</template>
<script setup>
import { ref, watch, defineProps, defineEmits, onMounted } from 'vue';
const props = defineProps({ deviceId: { type: [String, Number], required: true } });
const emit = defineEmits(['close']);
const visible = ref(true);
const device = ref({});
const tasks = ref([]);
const total = ref(0);
const page = ref(1);
const pageSize = 10;
async function fetchDevice() {
  const res = await fetch(`/api/v1/devices/${props.deviceId}`);
  device.value = await res.json();
}
async function fetchTasks(p = 1) {
  page.value = p;
  const params = new URLSearchParams({ deviceId: props.deviceId, page: p, size: pageSize });
  const res = await fetch(`/api/v1/scheduler/tasks?${params}`);
  const data = await res.json();
  tasks.value = data.items || [];
  total.value = data.total || 0;
}
function onClose() {
  visible.value = false;
  emit('close');
}
watch(() => props.deviceId, () => {
  fetchDevice();
  fetchTasks(1);
}, { immediate: true });
onMounted(() => {
  fetchDevice();
  fetchTasks(1);
});
</script>
<style scoped></style>