<template>
  <el-dialog
    :model-value="visible"
    :title="isEdit ? '编辑生产计划' : '新增生产计划'"
    width="600px"
    @close="handleClose"
    :close-on-click-modal="false"
  >
    <el-form :model="form" :rules="rules" ref="planFormRef" label-width="100px">
      <el-form-item label="计划名称" prop="name">
        <el-input v-model="form.name" placeholder="请输入计划名称"></el-input>
      </el-form-item>
      <el-form-item label="产品名称" prop="productName">
        <el-input v-model="form.productName" placeholder="请输入产品名称"></el-input>
      </el-form-item>
      <el-form-item label="数量" prop="quantity">
        <el-input-number v-model="form.quantity" :min="1" placeholder="请输入数量"></el-input-number>
      </el-form-item>
      <el-form-item label="开始时间" prop="startTime">
        <el-date-picker
          v-model="form.startTime"
          type="datetime"
          placeholder="选择开始时间"
          value-format="YYYY-MM-DDTHH:mm:ss.SSSZ"
          :default-time="defaultTimeStart"
        ></el-date-picker>
      </el-form-item>
      <el-form-item label="结束时间" prop="endTime">
        <el-date-picker
          v-model="form.endTime"
          type="datetime"
          placeholder="选择结束时间"
          value-format="YYYY-MM-DDTHH:mm:ss.SSSZ"
          :default-time="defaultTimeEnd"
        ></el-date-picker>
      </el-form-item>
      <el-form-item label="备注" prop="notes">
        <el-input type="textarea" v-model="form.notes" placeholder="请输入备注信息"></el-input>
      </el-form-item>
    </el-form>
    <template #footer>
      <span class="dialog-footer">
        <el-button @click="handleClose">取消</el-button>
        <el-button type="primary" @click="handleSubmit">确定</el-button>
        <el-button v-if="isEdit" type="danger" @click="handleDelete" style="float: left;">删除</el-button>
      </span>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, watch, nextTick, computed } from 'vue';
import request from '@/utils/request';
import { ElMessage, ElMessageBox } from 'element-plus';

const props = defineProps({
  visible: {
    type: Boolean,
    required: true,
  },
  plan: {
    type: Object,
    default: null,
  },
});

const emit = defineEmits(['close', 'saved', 'deleted']);

const planFormRef = ref(null);
const form = ref({
  id: null,
  name: '',
  productName: '',
  quantity: 1,
  startTime: '',
  endTime: '',
  notes: '',
});

const defaultTimeStart = new Date(2000, 1, 1, 8, 0, 0);
const defaultTimeEnd = new Date(2000, 1, 1, 17, 0, 0);

const isEdit = computed(() => !!form.value.id);

const rules = {
  name: [{ required: true, message: '请输入计划名称', trigger: 'blur' }],
  productName: [{ required: true, message: '请输入产品名称', trigger: 'blur' }],
  quantity: [{ required: true, message: '请输入数量', trigger: 'blur' }, { type: 'number', min: 1, message: '数量必须大于0', trigger: 'blur' }],
  startTime: [{ required: true, message: '请选择开始时间', trigger: 'change' }],
  endTime: [
    { required: true, message: '请选择结束时间', trigger: 'change' },
    {
      validator: (rule, value, callback) => {
        if (form.value.startTime && value && new Date(value) < new Date(form.value.startTime)) {
          callback(new Error('结束时间不能早于开始时间'));
        } else {
          callback();
        }
      },
      trigger: 'change',
    },
  ],
};

watch(() => props.plan, (newVal) => {
  if (newVal) {
    form.value = { ...newVal };
    // 后端返回的是ISO 8601 UTC，Element Plus DatePicker可以直接使用
  } else {
    form.value = {
      id: null,
      name: '',
      productName: '',
      quantity: 1,
      startTime: '',
      endTime: '',
      notes: '',
    };
  }
  // 清除校验结果
  nextTick(() => {
    planFormRef.value?.clearValidate();
  });
}, { immediate: true, deep: true });

const handleClose = () => {
  emit('close');
};

const handleSubmit = async () => {
  if (!planFormRef.value) return;
  await planFormRef.value.validate(async (valid) => {
    if (valid) {
      try {
        let response;
        const payload = { ...form.value };
        // 确保时间是UTC格式提交
        if (payload.startTime) payload.startTime = new Date(payload.startTime).toISOString();
        if (payload.endTime) payload.endTime = new Date(payload.endTime).toISOString();

        if (isEdit.value) {
          response = await request.put(`/api/v1/plans/${form.value.id}`, payload);
        } else {
          response = await request.post('/api/v1/plans', payload);
        }
        if (response) { // 假设请求成功后，request拦截器会处理response.data
          ElMessage.success(isEdit.value ? '更新成功' : '创建成功');
          emit('saved');
          handleClose();
        } 
      } catch (error) {
        console.error('Failed to save plan:', error);
        // ElMessage.error(isEdit.value ? '更新生产计划失败' : '创建生产计划失败'); // request拦截器会处理
      }
    }
  });
};

const handleDelete = async () => {
  if (!form.value.id) return;
  try {
    await ElMessageBox.confirm('确定删除此生产计划吗?', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    });
    await request.delete(`/api/v1/plans/${form.value.id}`);
    ElMessage.success('删除成功');
    emit('deleted');
    handleClose();
  } catch (error) {
    if (error !== 'cancel') {
      console.error('Failed to delete plan:', error);
      ElMessage.error('删除生产计划失败');
    }
  }
};

</script>

<style scoped>
.dialog-footer {
  text-align: right;
}
</style>