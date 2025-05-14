<template>
  <div>
    <el-button type="primary" @click="onBatchSave" :disabled="!hasChanges">批量保存</el-button>
    <el-table
      :data="matrixData"
      border
      style="width: 100%; margin-top: 16px;"
      :row-key="row => row.processId"
      v-loading="loading"
      height="600"
      :virtual-scroll="isLargeTable"
    >
      <el-table-column prop="processName" label="工序" fixed width="120" />
      <el-table-column
        v-for="col in dynamicColumns"
        :key="col.key"
        :prop="col.key"
        :label="col.label"
        :width="col.width || 120"
      >
        <template #default="{ row, $index }">
          <el-input-number
            v-model="row[col.key]"
            :min="0"
            :max="99999"
            size="small"
            @change="onCellEdit(row, col.key)"
            style="width: 100px;"
          />
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>
<script setup>
import { ref, computed, onMounted } from 'vue';
import { ElMessageBox, ElMessage } from 'element-plus';
const matrixData = ref([]);
const dynamicColumns = ref([]);
const loading = ref(false);
const changedCells = ref(new Set());
const isLargeTable = computed(() => matrixData.value.length > 20 && dynamicColumns.value.length > 20);
const hasChanges = computed(() => changedCells.value.size > 0);
async function fetchMatrix() {
  loading.value = true;
  const res = await fetch('/api/v1/capacities');
  const data = await res.json();
  // 假设后端返回 { processes:[], shifts:[], devices:[], capacities:[] }
  // 生成动态列和表格数据
  const { processes, shifts, devices, capacities } = data;
  // 列：班次/设备组合
  const cols = [];
  shifts.forEach(shift => {
    devices.forEach(device => {
      cols.push({
        key: `${shift.id}_${device.id}`,
        label: `${shift.name}/${device.name}`
      });
    });
  });
  dynamicColumns.value = cols;
  // 行：工序
  matrixData.value = processes.map(proc => {
    const row = { processId: proc.id, processName: proc.name };
    cols.forEach(col => {
      const [shiftId, deviceId] = col.key.split('_');
      const found = capacities.find(
        c => c.processId == proc.id && c.shiftId == shiftId && c.deviceId == deviceId
      );
      row[col.key] = found ? found.capacity : 0;
    });
    return row;
  });
  changedCells.value.clear();
  loading.value = false;
}
function onCellEdit(row, key) {
  changedCells.value.add(`${row.processId}_${key}`);
}
async function onBatchSave() {
  const changed = Array.from(changedCells.value);
  if (!changed.length) return;
  await ElMessageBox.confirm(`本次共修改 ${changed.length} 条，确认保存？`, '批量保存', { type: 'warning' });
  // 组装变更数据
  const payload = changed.map(cellKey => {
    const [processId, shiftId, deviceId] = cellKey.split('_');
    const row = matrixData.value.find(r => r.processId == processId);
    return {
      processId,
      shiftId,
      deviceId,
      capacity: row[`${shiftId}_${deviceId}`]
    };
  });
  const res = await fetch('/api/v1/capacities', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
  if (res.ok) {
    ElMessage.success('保存成功');
    changedCells.value.clear();
    fetchMatrix();
  } else {
    ElMessage.error('保存失败');
  }
}
onMounted(fetchMatrix);
</script>
<style scoped></style>