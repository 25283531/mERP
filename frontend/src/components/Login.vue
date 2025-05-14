<template>
  <div class="login-container">
    <el-card class="login-card">
      <template #header>
        <div class="card-header">
          <span>用户登录</span>
        </div>
      </template>
      <el-form :model="loginForm" :rules="loginRules" ref="loginFormRef" @submit.prevent="handleLogin">
        <el-form-item prop="username">
          <el-input v-model="loginForm.username" placeholder="用户名" prefix-icon="User" />
        </el-form-item>
        <el-form-item prop="password">
          <el-input v-model="loginForm.password" type="password" placeholder="密码" prefix-icon="Lock" show-password />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" native-type="submit" :loading="loading" style="width: 100%;">登录</el-button>
        </el-form-item>
      </el-form>
      <div class="mock-info">
        <p><strong>测试账户:</strong></p>
        <p>管理员: admin / 123456 (权限: view_org, manage_org, view_permission, manage_permission)</p>
        <p>编辑: editor / 123456 (权限: view_org, view_permission)</p>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { ElMessage } from 'element-plus';
// import { login as apiLogin } from '@/api/auth'; // 假设的API服务

const router = useRouter();
const route = useRoute();

const loginFormRef = ref(null);
const loginForm = ref({
  username: '',
  password: '',
});
const loading = ref(false);

const loginRules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
};

// 模拟登录API
const mockApiLogin = async (credentials) => {
  return new Promise((resolve, reject) => {
    setTimeout(() => {
      if (credentials.username === 'admin' && credentials.password === '123456') {
        resolve({
          code: 200,
          data: {
            token: 'fake_admin_token_'.concat(Date.now().toString()),
            permissions: ['view_org', 'manage_org', 'view_permission', 'manage_permission']
          },
          message: '登录成功'
        });
      } else if (credentials.username === 'editor' && credentials.password === '123456') {
        resolve({
          code: 200,
          data: {
            token: 'fake_editor_token_'.concat(Date.now().toString()),
            permissions: ['view_org', 'view_permission']
          },
          message: '登录成功'
        });
      } else {
        reject({ code: 401, message: '用户名或密码错误' });
      }
    }, 500);
  });
};

const handleLogin = async () => {
  if (!loginFormRef.value) return;
  loginFormRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true;
      try {
        // const response = await apiLogin(loginForm.value);
        const response = await mockApiLogin(loginForm.value);

        if (response.code === 200 && response.data) {
          localStorage.setItem('user_token', response.data.token);
          localStorage.setItem('user_permissions', JSON.stringify(response.data.permissions || []));
          ElMessage.success('登录成功');
          
          // 调用 store action 更新用户信息 (如果使用 Vuex/Pinia)
          // store.dispatch('auth/fetchUser');
          
          const redirect = route.query.redirect || '/';
          router.push(redirect);
        } else {
          ElMessage.error(response.message || '登录失败');
        }
      } catch (error) {
        console.error('Login error:', error);
        ElMessage.error(error.message || '登录时发生错误');
      } finally {
        loading.value = false;
      }
    } else {
      return false;
    }
  });
};
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background-color: #f0f2f5;
}

.login-card {
  width: 400px;
}

.card-header {
  text-align: center;
  font-size: 20px;
  font-weight: bold;
}

.mock-info {
  margin-top: 20px;
  padding: 10px;
  border: 1px solid #eee;
  border-radius: 4px;
  font-size: 12px;
  color: #606266;
}
.mock-info p {
  margin: 5px 0;
}
</style>