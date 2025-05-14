<template>
  <el-container class="app-container">
    <el-aside width="200px" class="app-aside">
      <el-menu
        default-active="/"
        class="el-menu-vertical-demo"
        router
        :collapse="isCollapse"
      >
        <el-menu-item index="/">
          <el-icon><house /></el-icon>
          <span>首页</span>
        </el-menu-item>
        <el-sub-menu index="/management">
          <template #title>
            <el-icon><setting /></el-icon>
            <span>系统管理</span>
          </template>
          <el-menu-item index="/org">
            <el-icon><office-building /></el-icon>
            <span>组织管理</span>
          </el-menu-item>
          <el-menu-item index="/permission">
            <el-icon><key /></el-icon>
            <span>权限管理</span>
          </el-menu-item>
        </el-sub-menu>
         <el-menu-item index="/production">
          <el-icon><data-analysis /></el-icon>
          <span>生产计划</span>
        </el-menu-item>
        <!-- 其他模块导航 -->
      </el-menu>
    </el-aside>
    <el-container>
      <el-header class="app-header">
        <div class="header-left">
          <el-button type="text" @click="toggleCollapse">
            <el-icon><expand v-if="isCollapse" /><fold v-else /></el-icon>
          </el-button>
          <span>mERP</span>
        </div>
        <div class="header-right">
          <el-dropdown @command="handleCommand">
            <span class="el-dropdown-link">
              {{ userInfo.username || '用户' }}<el-icon class="el-icon--right"><arrow-down /></el-icon>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="logout">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>
      <el-main class="app-main">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { ref, computed } from 'vue';
import { useAuthStore } from './store/auth';
import { useRouter } from 'vue-router';
import { House, Setting, OfficeBuilding, Key, DataAnalysis, Expand, Fold, ArrowDown } from '@element-plus/icons-vue';

const authStore = useAuthStore();
const router = useRouter();

const isCollapse = ref(false);

const userInfo = computed(() => authStore.userInfo);

const toggleCollapse = () => {
  isCollapse.value = !isCollapse.value;
};

const handleCommand = (command) => {
  if (command === 'logout') {
    authStore.logout();
  }
};

// 初始化时检查认证状态，如果未认证且当前不是登录页，则跳转到登录页
if (!authStore.isAuthenticated && router.currentRoute.value.path !== '/login') {
  router.push('/login');
}

</script>

<style>
html, body, #app {
  height: 100%;
  margin: 0;
}

.app-container {
  height: 100%;
}

.app-aside {
  background-color: #f4f6f8;
  border-right: 1px solid #e6e6e6;
}

.el-menu-vertical-demo:not(.el-menu--collapse) {
  width: 200px;
  min-height: 400px;
}

.app-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: #fff;
  border-bottom: 1px solid #e6e6e6;
  padding: 0 20px;
}

.header-left {
  display: flex;
  align-items: center;
}

.header-left .el-button {
  margin-right: 10px;
}

.header-right .el-dropdown-link {
  cursor: pointer;
  display: flex;
  align-items: center;
}

.app-main {
  padding: 20px;
  background-color: #eef0f3;
  height: calc(100vh - 60px); /* 减去header高度 */
  overflow-y: auto;
}
</style>