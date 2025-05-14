import { defineStore } from 'pinia';
import request from '../utils/request'; // 引入封装的axios实例
import router from '../router'; // 引入router实例

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('user_token') || null,
    userInfo: JSON.parse(localStorage.getItem('user_info') || '{}'),
    permissions: JSON.parse(localStorage.getItem('user_permissions') || '[]'),
  }),
  getters: {
    isAuthenticated: (state) => !!state.token,
    getUserInfo: (state) => state.userInfo,
    getPermissions: (state) => state.permissions,
  },
  actions: {
    async login(credentials) {
      try {
        // 假设登录API返回 { code, data: { token, user, permissions }, message }
        const response = await request.post('/auth/login', credentials);
        if (response && response.data) { // 假设成功时，实际数据在 response.data 中
          const { token, user, permissions } = response.data;
          this.token = token;
          this.userInfo = user;
          this.permissions = permissions;
          localStorage.setItem('user_token', token);
          localStorage.setItem('user_info', JSON.stringify(user));
          localStorage.setItem('user_permissions', JSON.stringify(permissions));
          
          // 登录成功后，尝试跳转到之前的页面或首页
          const redirect = router.currentRoute.value.query.redirect;
          if (typeof redirect === 'string') {
            router.push(redirect);
          } else {
            router.push('/');
          }
          return true;
        } else {
          // ElMessage已经在request拦截器中处理了大部分错误提示
          console.error('Login failed:', response?.message || 'Unknown error');
          return false;
        }
      } catch (error) {
        console.error('Login API error:', error);
        // ElMessage已经在request拦截器中处理了大部分错误提示
        return false;
      }
    },
    logout() {
      // 实际项目中，这里可能需要调用后端的登出接口
      // await request.post('/auth/logout');
      this.token = null;
      this.userInfo = {};
      this.permissions = [];
      localStorage.removeItem('user_token');
      localStorage.removeItem('user_info');
      localStorage.removeItem('user_permissions');
      router.push('/login');
    },
    async fetchPermissions() {
      try {
        // 假设获取权限API返回 { code, data: { permissions }, message }
        const response = await request.get('/auth/me/permissions'); // 或者其他获取用户信息的接口
        if (response && response.data && response.data.permissions) {
          this.permissions = response.data.permissions;
          localStorage.setItem('user_permissions', JSON.stringify(response.data.permissions));
        } else if (response && response.data && response.data.user && response.data.user.permissions) {
          // 兼容返回用户信息中包含权限的情况
          this.permissions = response.data.user.permissions;
          localStorage.setItem('user_permissions', JSON.stringify(response.data.user.permissions));
        }
      } catch (error) {
        console.error('Failed to fetch permissions:', error);
        // 如果获取权限失败，可以选择清空本地权限或保留旧权限
        // this.permissions = [];
        // localStorage.removeItem('user_permissions');
      }
    },
    initializeAuth() {
      const token = localStorage.getItem('user_token');
      const userInfo = localStorage.getItem('user_info');
      const permissions = localStorage.getItem('user_permissions');
      if (token) {
        this.token = token;
      }
      if (userInfo) {
        try {
          this.userInfo = JSON.parse(userInfo);
        } catch (e) {
          this.userInfo = {};
          localStorage.removeItem('user_info');
        }
      }
      if (permissions) {
        try {
          this.permissions = JSON.parse(permissions);
        } catch (e) {
          this.permissions = [];
          localStorage.removeItem('user_permissions');
        }
      }
      // 可选：如果token存在，可以尝试刷新用户信息和权限
      // if (this.isAuthenticated) {
      //   this.fetchPermissions(); 
      // }
    },
    // 用于在权限变更后，从外部调用刷新权限缓存
    refreshPermissionsCache() {
      this.fetchPermissions();
    }
  },
});