import axios from 'axios';
import { ElMessage } from 'element-plus';
import router from '../router'; // 确保router实例可以被正确导入

// 创建 Axios 实例
const service = axios.create({
  baseURL: process.env.VUE_APP_API_BASE_URL || '/api/v1', // 从环境变量读取或使用默认值
  timeout: 10000, // 请求超时时间
});

// 请求拦截器
service.interceptors.request.use(
  config => {
    // 在发送请求之前做些什么，例如添加token
    const token = localStorage.getItem('user_token');
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    return config;
  },
  error => {
    // 对请求错误做些什么
    console.error('Request Error:', error); // for debug
    return Promise.reject(error);
  }
);

// 响应拦截器
service.interceptors.response.use(
  response => {
    // 对响应数据做点什么
    const res = response.data;
    // 如果自定义代码不是200/20000等成功状态，则判断为错误。
    // 这里可以根据实际后端API的返回结构进行调整
    if (res.code !== 200 && res.code !== 20000 && response.status === 200) {
      ElMessage({
        message: res.message || 'Error',
        type: 'error',
        duration: 5 * 1000,
      });
      // 50008: Illegal token; 50012: Other clients logged in; 50014: Token expired;
      if (res.code === 50008 || res.code === 50012 || res.code === 50014) {
        // TODO: 重新登录
        // ElMessageBox.confirm('您已登出，可以取消继续留在该页面，或者重新登录', '确认登出', {
        //   confirmButtonText: '重新登录',
        //   cancelButtonText: '取消',
        //   type: 'warning',
        // }).then(() => {
        //   store.dispatch('user/resetToken').then(() => {
        //     location.reload(); // 为了重新实例化vue-router对象 避免bug
        //   });
        // });
        console.warn('Token issue, redirecting to login.');
        localStorage.removeItem('user_token');
        localStorage.removeItem('user_permissions');
        router.push(`/login?redirect=${router.currentRoute.value.fullPath}`);
      }
      return Promise.reject(new Error(res.message || 'Error'));
    }
    return res;
  },
  error => {
    console.error('Response Error:', error); // for debug
    if (error.response) {
      switch (error.response.status) {
        case 401:
          // 未授权，通常是token无效或过期
          ElMessage({
            message: '认证失败或登录已过期，请重新登录。',
            type: 'error',
            duration: 3 * 1000,
          });
          localStorage.removeItem('user_token');
          localStorage.removeItem('user_permissions');
          router.push(`/login?redirect=${router.currentRoute.value.fullPath}`);
          break;
        case 403:
          // 禁止访问
          ElMessage({
            message: '您没有权限执行此操作或访问此资源。',
            type: 'error',
            duration: 3 * 1000,
          });
          // 可以选择跳转到无权限页面，或者停留在当前页
          // router.push({ name: 'NoPermission' }); 
          break;
        case 404:
          ElMessage({
            message: '请求的资源未找到。',
            type: 'error',
            duration: 3 * 1000,
          });
          break;
        case 500:
        case 502:
        case 503:
        case 504:
          ElMessage({
            message: '服务器错误，请稍后重试。',
            type: 'error',
            duration: 3 * 1000,
          });
          break;
        default:
          ElMessage({
            message: error.message || '请求失败',
            type: 'error',
            duration: 5 * 1000,
          });
      }
    } else if (error.message.includes('timeout')) {
        ElMessage({
            message: '请求超时，请检查您的网络连接。',
            type: 'error',
            duration: 3 * 1000,
        });
    } else {
        ElMessage({
            message: '发生未知错误，请联系管理员。',
            type: 'error',
            duration: 3 * 1000,
        });
    }
    return Promise.reject(error);
  }
);

export default service;