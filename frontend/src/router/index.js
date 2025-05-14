import { createRouter, createWebHistory } from 'vue-router';
import Home from '../components/Home.vue'; // 假设有一个 Home 组件
import Login from '../components/Login.vue'; // 假设有一个 Login 组件
import NoPermission from '../components/NoPermission.vue'; // 假设有一个无权限提示组件
import OrgManagement from '../modules/org/index.vue';
import PermissionManagement from '../modules/permission/index.vue';
import ProductionPlanning from '../modules/production/index.vue'; // 新增：引入生产计划模块

// 模拟用户权限数据，实际项目中应从 store 或 API 获取
const getCurrentUserPermissions = () => {
  // return ['view_org', 'manage_org', 'view_permission', 'manage_permission']; // 示例：拥有所有权限
  // return ['view_org', 'view_permission']; // 示例：只拥有查看权限
  return JSON.parse(localStorage.getItem('user_permissions') || '[]');
};

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home,
    meta: { requiresAuth: true }
  },
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: { requiresAuth: false }
  },
  {
    path: '/no-permission',
    name: 'NoPermission',
    component: NoPermission,
    meta: { requiresAuth: false }
  },
  {
    path: '/org',
    name: 'OrgManagement',
    component: OrgManagement,
    meta: { requiresAuth: true, permissions: ['view_org'] } // 示例权限
  },
  {
    path: '/permission',
    name: 'PermissionManagement',
    component: PermissionManagement,
    meta: { requiresAuth: true, permissions: ['manage_permission'] } // 示例权限
  },
  {
    path: '/production',
    name: 'ProductionPlanning',
    component: ProductionPlanning,
    meta: { requiresAuth: true } // 假设访问生产计划需要登录
  },
  // 可以在这里添加更多应用的路由
];

const router = createRouter({
  history: createWebHistory(process.env.BASE_URL || '/'), // Ensure BASE_URL is configured in vue.config.js or .env
  routes,
});

router.beforeEach((to, from, next) => {
  const isAuthenticated = !!localStorage.getItem('user_token'); // 简化的认证检查
  const userPermissions = getCurrentUserPermissions();

  if (to.meta.requiresAuth) {
    if (!isAuthenticated) {
      next({ name: 'Login', query: { redirect: to.fullPath } });
    } else {
      if (to.meta.permissions) {
        const hasPermission = to.meta.permissions.every(p => userPermissions.includes(p));
        if (hasPermission) {
          next();
        } else {
          next({ name: 'NoPermission' });
        }
      } else {
        // 如果路由需要认证但没有指定特定权限，则允许访问
        next();
      }
    }
  } else {
    next();
  }
});

export default router;