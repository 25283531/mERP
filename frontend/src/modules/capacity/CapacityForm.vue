<template>
  <el-dialog v-model="visible" :title="form.id ? '编辑产能' : '新增产能'" width="500px" @close="onClose">
    <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
      <el-form-item label="工序" prop="processId">
        <el-select v-model="form.processId" placeholder="请选择工序">
          <el-option v-for="item in processOptions" :key="item.id" :label="item.name" :value="item.id" />
        </el-select>
      </el-form-item>
      <el-form-item label="班次" prop="shiftId">
        <el-select v-model="form.shiftId" placeholder="请选择班次">
          <el-option v-for="item in shiftOptions" :key="item.id" :label="item.name" :value="item.id" />
        </el-select>
      </el-form-item>
      <el-form-item label="设备" prop="deviceId">
        <el-select v-model="form.deviceId" placeholder="请选择设备">
          <el-option v-for="item in deviceOptions" :key="item.id" :label="item.name" :value="item.id" />
        </el-select>
      </el-form-item>
      <el-form-item label="产能" prop="capacity">
        <el-input-number v-model="form.capacity" :min="0" :max="99999" style="width: 100%;" />
      </el-form-item>
      <el-form-item label="切换时间(min)" prop="switchTime">
        <el-input-number v-model="form.switchTime" :min="0" :max="1440" style="width: 100%;" />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="onClose">取消</el-button>
      <el-button type="danger" v-if="form.id" @click="onDelete">删除</el-button>
      <el-button type="primary" @click="onSave">保存</el-button>
    </template>
  </el-dialog>
</template>
<script setup>
import { ref, defineProps, defineEmits, onMounted } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
const props = defineProps({
  capacity: { type: Object, default: () => ({}) },
  visible: { type: Boolean, default: false }
});
const emit = defineEmits(['close', 'saved', 'deleted']);
const visible = ref(props.visible);
const form = ref({ ...props.capacity });
const formRef = ref();
const processOptions = ref([]);
const shiftOptions = ref([]);
const deviceOptions = ref([]);
const rules = {
  processId: [{ required: true, message: '请选择工序', trigger: 'change' }],
  shiftId: [{ required: true, message: '请选择班次', trigger: 'change' }],
  deviceId: [{ required: true, message: '请选择设备', trigger: 'change' }],
  capacity: [{ required: true, message: '请输入产能', trigger: 'blur' }],
  switchTime: [{ required: true, message: '请输入切换时间', trigger: 'blur' }]
};
async function fetchOptions() {
  const [procRes, shiftRes, devRes] = await Promise.all([
    fetch('/api/v1/processes'),
    fetch('/api/v1/shifts'),
    fetch('/api/v1/devices')
  ]);
  processOptions.value = await procRes.json();
  shiftOptions.value = await shiftRes.json();
  deviceOptions.value = await devRes.json();
}
function onClose() {
  visible.value = false;
  emit('close');
}
async function onSave() {
  await formRef.value.validate();
  const res = await fetch('/api/v1/capacities', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(form.value)
  });
  if (res.ok) {
    ElMessage.success('保存成功');
    emit('saved');
    onClose();
  } else {
    ElMessage.error('保存失败');
  }
}
async function onDelete() {
  await ElMessageBox.confirm('确定要删除该产能记录吗？', '删除确认', { type: 'warning' });
  const res = await fetch(`/api/v1/capacities/${form.value.id}`, { method: 'DELETE' });
  if (res.ok) {
    ElMessage.success('删除成功');
    emit('deleted');
    onClose();
  } else {
    ElMessage.error('删除失败');
  }
}
onMounted(fetchOptions);
</script>
<style scoped></style>