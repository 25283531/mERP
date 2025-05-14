<template>
  <el-dialog v-model="visible" :title="form.id ? '编辑设备' : '新增设备'" width="500px" @close="onClose">
    <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
      <el-form-item label="设备名称" prop="name">
        <el-input v-model="form.name" placeholder="请输入设备名称" />
      </el-form-item>
      <el-form-item label="设备编号" prop="code">
        <el-input v-model="form.code" placeholder="请输入设备编号" />
      </el-form-item>
      <el-form-item label="类型" prop="type">
        <el-select v-model="form.type" placeholder="请选择类型">
          <el-option v-for="item in typeOptions" :key="item.value" :label="item.label" :value="item.value" />
        </el-select>
      </el-form-item>
      <el-form-item label="状态" prop="status">
        <el-select v-model="form.status" placeholder="请选择状态">
          <el-option v-for="item in statusOptions" :key="item.value" :label="item.label" :value="item.value" />
        </el-select>
      </el-form-item>
      <el-form-item label="切换时间(min)" prop="switchTime">
        <el-input-number v-model="form.switchTime" :min="0" :max="1440" :step="1" placeholder="0-1440" style="width: 100%;" />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="onClose">取消</el-button>
      <el-button type="primary" @click="onSave">保存</el-button>
    </template>
  </el-dialog>
</template>
<script setup>
import { ref, watch, defineProps, defineEmits } from 'vue';
import { ElMessage } from 'element-plus';
const props = defineProps({ device: { type: Object, default: () => ({}) } });
const emit = defineEmits(['close', 'saved']);
const visible = ref(true);
const form = ref({ ...props.device });
const formRef = ref();
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
const rules = {
  name: [{ required: true, message: '请输入设备名称', trigger: 'blur' }],
  code: [{ required: true, message: '请输入设备编号', trigger: 'blur' }],
  type: [{ required: true, message: '请选择类型', trigger: 'change' }],
  status: [{ required: true, message: '请选择状态', trigger: 'change' }],
  switchTime: [
    { required: true, message: '请输入切换时间', trigger: 'blur' },
    { type: 'number', min: 0, max: 1440, message: '范围0-1440', trigger: 'blur' }
  ]
};
watch(() => props.device, (val) => {
  Object.assign(form.value, val);
});
function onClose() {
  visible.value = false;
  emit('close');
}
async function onSave() {
  await formRef.value.validate();
  const method = form.value.id ? 'PUT' : 'POST';
  const url = form.value.id ? `/api/v1/devices/${form.value.id}` : '/api/v1/devices';
  const res = await fetch(url, {
    method,
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(form.value)
  });
  if (res.ok) {
    ElMessage.success('保存成功');
    emit('saved');
  }
}
</script>
<style scoped></style>