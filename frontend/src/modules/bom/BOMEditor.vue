<template>
  <el-dialog v-model="visible" title="编辑BOM" width="800px" @close="onClose">
    <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
      <bom-form-list v-model:list="form.items" :level="0" />
    </el-form>
    <template #footer>
      <el-button @click="onClose">取消</el-button>
      <el-button type="primary" @click="onSave">保存</el-button>
    </template>
  </el-dialog>
</template>
<script setup>
import { ref, watch, defineProps, defineEmits } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import * as yup from 'yup';
import BomFormList from './BOMFormList.vue';

const props = defineProps({
  bom: { type: Object, default: () => ({}) }
});
const emit = defineEmits(['close']);
const visible = ref(true);
const form = ref({ ...props.bom, items: props.bom.items || [] });
const formRef = ref();

const rules = {
  name: [ { required: true, message: '请输入物料名称', trigger: 'blur' } ],
  code: [ { required: true, message: '请输入物料编码', trigger: 'blur' } ],
  quantity: [ { required: true, message: '请输入数量', trigger: 'blur' } ]
};

function hasCycle(items, parentIds = []) {
  for (const item of items) {
    if (parentIds.includes(item.id)) return true;
    if (item.children && hasCycle(item.children, [...parentIds, item.id])) return true;
  }
  return false;
}

async function onSave() {
  await formRef.value.validate();
  if (hasCycle(form.value.items)) {
    ElMessage.error('检测到循环引用，请检查BOM结构');
    return;
  }
  const method = form.value.id ? 'PUT' : 'POST';
  const url = form.value.id ? `/api/v1/bom/${form.value.id}` : '/api/v1/bom';
  await fetch(url, {
    method,
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(form.value)
  });
  ElMessage.success('保存成功');
  emit('close');
}

function onClose() {
  if (JSON.stringify(form.value) !== JSON.stringify(props.bom)) {
    ElMessageBox.confirm('有未保存的更改，确定要离开吗？', '提示', { type: 'warning' })
      .then(() => emit('close'));
  } else {
    emit('close');
  }
}

watch(() => props.bom, (val) => {
  form.value = { ...val, items: val.items || [] };
});
</script>
<style scoped></style>