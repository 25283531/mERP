<template>
  <el-dialog
    :model-value="visible"
    :title="isEditMode ? '编辑角色' : '新增角色'"
    width="500px"
    @close="handleClose"
    :close-on-click-modal="false"
  >
    <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
      <el-form-item label="角色名称" prop="name">
        <el-input v-model="form.name" placeholder="请输入角色名称" />
      </el-form-item>
      <el-form-item label="角色标识" prop="key">
        <el-input v-model="form.key" placeholder="请输入角色标识 (例如: admin, editor)" :disabled="isEditMode"/>
      </el-form-item>
      <el-form-item label="角色描述" prop="description">
        <el-input v-model="form.description" type="textarea" placeholder="请输入角色描述" />
      </el-form-item>
    </el-form>
    <template #footer>
      <span class="dialog-footer">
        <el-button @click="handleClose">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="loading">确定</el-button>
      </span>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, watch, nextTick, computed } from 'vue';
import { ElMessage } from 'element-plus';
// import { createRole, updateRole } from '@/api/permission'; // 假设的API服务

const props = defineProps({
  visible: {
    type: Boolean,
    default: false,
  },
  role: {
    type: Object,
    default: () => ({}),
  },
});

const emit = defineEmits(['close', 'saved']);

const formRef = ref(null);
const form = ref({ id: null, name: '', key: '', description: '' });
const loading = ref(false);

const isEditMode = computed(() => !!form.value.id);

const rules = {
  name: [{ required: true, message: '请输入角色名称', trigger: 'blur' }],
  key: [
    { required: true, message: '请输入角色标识', trigger: 'blur' },
    { 
      validator: (rule, value, callback) => {
        if (!/^[a-zA-Z0-9_]+$/.test(value)) {
          callback(new Error('角色标识只能包含字母、数字和下划线'));
        } else {
          callback();
        }
      },
      trigger: 'blur'
    }
  ],
};

// 模拟API
const mockApi = {
  createRole: async (data) => {
    console.log('Creating role:', data);
    return new Promise(resolve => {
      setTimeout(() => {
        resolve({ code: 200, data: { ...data, id: Date.now().toString() }, message: '创建成功' });
      }, 300);
    });
  },
  updateRole: async (id, data) => {
    console.log('Updating role:', id, data);
    return new Promise(resolve => {
      setTimeout(() => {
        resolve({ code: 200, data: { ...data, id }, message: '更新成功' });
      }, 300);
    });
  }
};

watch(() => props.visible, (newVal) => {
  if (newVal) {
    nextTick(() => {
      if (formRef.value) {
        formRef.value.resetFields();
      }
      if (props.role && props.role.id) {
        form.value = { ...props.role };
      } else {
        form.value = { id: null, name: '', key: '', description: '' };
      }
    });
  }
});

function handleClose() {
  emit('close');
}

async function handleSubmit() {
  if (!formRef.value) return;
  formRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true;
      try {
        let response;
        const payload = { name: form.value.name, key: form.value.key, description: form.value.description };
        if (isEditMode.value) {
          // response = await updateRole(form.value.id, payload);
          response = await mockApi.updateRole(form.value.id, payload);
        } else {
          // response = await createRole(payload);
          response = await mockApi.createRole(payload);
        }
        if (response.code === 200) {
          ElMessage.success(isEditMode.value ? '角色更新成功' : '角色创建成功');
          emit('saved', response.data);
          handleClose();
        } else {
          ElMessage.error(response.message || (isEditMode.value ? '角色更新失败' : '角色创建失败'));
        }
      } catch (error) {
        console.error('Error saving role:', error);
        ElMessage.error((isEditMode.value ? '角色更新失败: ' : '角色创建失败: ') + error.message);
      } finally {
        loading.value = false;
      }
    } else {
      return false;
    }
  });
}

</script>

<style scoped>
.dialog-footer {
  text-align: right;
}
</style>