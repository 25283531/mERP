<template>
  <div class="no-permission-page">
    <el-result icon="warning" title="无权限访问" sub-title="抱歉，您没有权限访问此页面。">
      <template #extra>
        <el-button type="primary" @click="goBack">返回上一页</el-button>
        <el-button @click="goHome">返回首页</el-button>
      </template>
    </el-result>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router';

const router = useRouter();

const goBack = () => {
  router.go(-1);
};

const goHome = () => {
  router.push('/');
};
</script>

<style scoped>
.no-permission-page {
  display: flex;
  justify-content: center;
  align-items: center;
  height: calc(100vh - 100px); /* Adjust based on your layout */
  padding: 20px;
}
</style>