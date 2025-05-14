import { createApp } from 'vue';
import App from './App.vue'; // 需要创建一个 App.vue 作为根组件
import router from './router';
import { createPinia } from 'pinia';
import ElementPlus from 'element-plus';
import 'element-plus/dist/index.css';
import * as ElementPlusIconsVue from '@element-plus/icons-vue';
import { useAuthStore } from './store/auth'; // 新增：引入 auth store

// 引入之前创建的 request.js，虽然在这里不直接使用，但确保它被打包
import './utils/request'; 

const app = createApp(App);

// 注册 Element Plus 图标
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component);
}

const pinia = createPinia(); // 修改：创建 Pinia 实例
app.use(pinia); // 修改：使用 Pinia 实例

// 新增：在 Pinia 挂载后初始化 auth store
const authStore = useAuthStore();
authStore.initializeAuth();

app.use(router);
app.use(ElementPlus);

app.mount('#app');

// 为了让应用能够运行，还需要一个 public/index.html 文件和一个 App.vue 根组件
// 这里我们先专注于 main.js 的创建