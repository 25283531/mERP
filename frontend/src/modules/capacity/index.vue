<template>
  <div class="capacity-page">
    <el-card>
      <div style="margin-bottom: 16px;">
        <el-button type="primary" @click="openForm()">新增产能</el-button>
        <el-button @click="openImport()">批量导入</el-button>
      </div>
      <CapacityMatrix @edit="editCapacity" />
    </el-card>
    <CapacityForm
      v-if="formVisible"
      :visible="formVisible"
      :capacity="currentCapacity"
      @close="formVisible = false"
      @saved="refreshMatrix"
      @deleted="refreshMatrix"
    />
    <CapacityImport
      v-if="importVisible"
      :visible="importVisible"
      @close="importVisible = false"
      @imported="refreshMatrix"
    />
  </div>
</template>
<script setup>
import { ref } from 'vue';
import CapacityMatrix from './CapacityMatrix.vue';
import CapacityForm from './CapacityForm.vue';
import CapacityImport from './CapacityImport.vue';

const formVisible = ref(false);
const importVisible = ref(false);
const currentCapacity = ref(null);
const matrixRef = ref();

function openForm() {
  currentCapacity.value = null;
  formVisible.value = true;
}
function editCapacity(capacity) {
  currentCapacity.value = { ...capacity };
  formVisible.value = true;
}
function openImport() {
  importVisible.value = true;
}
function refreshMatrix() {
  if (matrixRef.value && matrixRef.value.fetchData) {
    matrixRef.value.fetchData();
  }
}
</script>
<style scoped>
.capacity-page {
  padding: 24px;
}
</style>