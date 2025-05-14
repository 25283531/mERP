<template>
  <div class="plan-list-page">
    <el-card>
      <el-table :data="plans" style="width: 100%">
        <el-table-column prop="name" label="计划名称" />
        <el-table-column prop="productName" label="产品名称" />
        <el-table-column prop="quantity" label="数量" />
        <el-table-column prop="startTime" label="开始时间">
          <template #default="scope">
            {{ formatDateTime(scope.row.startTime) }}
          </template>
        </el-table-column>
        <el-table-column prop="endTime" label="结束时间">
          <template #default="scope">
            {{ formatDateTime(scope.row.endTime) }}
          </template>
        </el-table-column>
        <el-table-column label="操作">
          <template #default="scope">
            <el-button size="small" @click="handleEdit(scope.row)">编辑</el-button>
            <el-button size="small" type="danger" @click="handleDelete(scope.row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import request from '@/utils/request';
import { ElMessage, ElMessageBox } from 'element-plus';

const plans = ref([]);

const emit = defineEmits(['edit-plan']);

const fetchPlans = async () => {
  try {
    const response = await request.get('/api/v1/plans');
    if (response && response.data) {
      plans.value = response.data;
    }
  } catch (error) {
    console.error('Failed to fetch plans:', error);
    ElMessage.error('获取生产计划列表失败');
  }
};

const formatDateTime = (dateTimeStr) => {
  if (!dateTimeStr) return '';
  // 假设后端返回的是 ISO 8601 UTC 时间字符串
  const date = new Date(dateTimeStr);
  return date.toLocaleString(); // 本地化显示
};

const handleEdit = (plan) => {
  emit('edit-plan', plan);
};

const handleDelete = async (id) => {
  try {
    await ElMessageBox.confirm('确定删除此生产计划吗?', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    });
    await request.delete(`/api/v1/plans/${id}`);
    ElMessage.success('删除成功');
    fetchPlans(); // 重新加载列表
  } catch (error) {
    if (error !== 'cancel') {
      console.error('Failed to delete plan:', error);
      ElMessage.error('删除生产计划失败');
    }
  }
};

onMounted(() => {
  fetchPlans();
});

// 暴露给父组件调用的方法
defineExpose({
  fetchPlans
});

</script>

<style scoped>
.plan-list-page {
  padding: 10px;
}
</style>