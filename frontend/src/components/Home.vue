<template>
  <div class="home-page">
    <h1>欢迎来到 mERP 系统</h1>
    <p>这是一个基础的首页。</p>
    <p>
      <router-link to="/org">组织管理</router-link> |
      <router-link to="/permission">权限管理</router-link>
    </p>
    <p>
      <el-button @click="logout">登出</el-button>
    </p>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router';

const router = useRouter();

const logout = () => {
  // 清除认证信息
  localStorage.removeItem('user_token');
  localStorage.removeItem('user_permissions');
  // 跳转到登录页
  router.push({ name: 'Login' });
};
</script>

<style scoped>
.home-page {
  padding: 20px;
  text-align: center;
}
</style>