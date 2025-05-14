<template>
  <div class="production-planning-page">
    <el-row :gutter="20">
      <el-col :span="16">
        <el-card header="生产甘特图">
          <GanttChart :plans="planList" @update-plan-time="handleGanttUpdate" ref="ganttChartRef" />
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card header="生产计划列表">
          <div style="margin-bottom: 16px;">
            <el-button type="primary" @click="openPlanForm(null)">新增计划</el-button>
          </div>
          <PlanList @edit-plan="openPlanForm" ref="planListRef" />
        </el-card>
      </el-col>
    </el-row>

    <PlanForm
      v-if="formVisible"
      :visible="formVisible"
      :plan="currentPlan"
      @close="formVisible = false"
      @saved="handlePlanSaved"
      @deleted="handlePlanDeleted"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick } from 'vue';
import PlanList from './PlanList.vue';
import GanttChart from './GanttChart.vue';
import PlanForm from './PlanForm.vue';
import request from '@/utils/request';
import { ElMessage } from 'element-plus';

const planList = ref([]);
const formVisible = ref(false);
const currentPlan = ref(null);
const planListRef = ref(null);
const ganttChartRef = ref(null);

const fetchAllPlans = async () => {
  try {
    const response = await request.get('/api/v1/plans');
    if (response && response.data) {
      planList.value = response.data.map(plan => ({
        ...plan,
        // 确保时间字段是存在的，甘特图和列表组件内部会处理UTC到本地时间的转换显示
        startTime: plan.startTime, 
        endTime: plan.endTime,
      }));
      // 刷新甘特图
      nextTick(() => {
        if (ganttChartRef.value && ganttChartRef.value.redraw) {
          ganttChartRef.value.redraw();
        }
      });
    } else {
      planList.value = [];
    }
  } catch (error) {
    console.error('Failed to fetch plans for index:', error);
    ElMessage.error('加载生产计划数据失败');
    planList.value = [];
  }
};

const openPlanForm = (plan) => {
  currentPlan.value = plan ? { ...plan } : null;
  formVisible.value = true;
};

const handlePlanSaved = () => {
  formVisible.value = false;
  fetchAllPlans(); // 刷新列表和甘特图
  if (planListRef.value && planListRef.value.fetchPlans) {
      planListRef.value.fetchPlans();
  }
};

const handlePlanDeleted = () => {
  formVisible.value = false;
  fetchAllPlans(); // 刷新列表和甘特图
   if (planListRef.value && planListRef.value.fetchPlans) {
      planListRef.value.fetchPlans();
  }
};

const handleGanttUpdate = async (updatedTimeData) => {
  try {
    // 后端API PUT /api/v1/plans/:id 用于更新时间或数量
    // GanttChart组件已经将时间转换为ISOString
    await request.put(`/api/v1/plans/${updatedTimeData.id}`, {
      startTime: updatedTimeData.startTime,
      endTime: updatedTimeData.endTime,
    });
    ElMessage.success('计划时间已通过甘特图更新');
    // 重新获取数据以确保一致性，或者仅更新本地数据中对应项
    const index = planList.value.findIndex(p => p.id === updatedTimeData.id);
    if (index !== -1) {
      planList.value[index].startTime = updatedTimeData.startTime;
      planList.value[index].endTime = updatedTimeData.endTime;
       // 刷新列表组件的数据
      if (planListRef.value && planListRef.value.fetchPlans) {
        planListRef.value.fetchPlans(); // 让列表组件自己刷新
      }
      // 触发甘特图重绘（如果它不自动响应prop变化的话，但通常会）
      nextTick(() => {
        if (ganttChartRef.value && ganttChartRef.value.redraw) {
          ganttChartRef.value.redraw();
        }
      });
    } else {
        fetchAllPlans(); // 如果找不到，则全部刷新
    }

  } catch (error) {
    console.error('Failed to update plan time from Gantt:', error);
    ElMessage.error('通过甘特图更新计划时间失败');
    fetchAllPlans(); // 出错时回滚到服务器最新状态
  }
};

onMounted(() => {
  fetchAllPlans();
});

</script>

<style scoped>
.production-planning-page {
  padding: 24px;
}
.el-card {
  margin-bottom: 20px;
}
</style>