<template>
  <div>
    <el-upload
      class="upload-demo"
      drag
      action=""
      :auto-upload="false"
      :before-upload="beforeUpload"
      :on-change="onFileChange"
      :file-list="fileList"
      :show-file-list="true"
    >
      <i class="el-icon-upload"></i>
      <div class="el-upload__text">将 Excel 文件拖到此处，或<em>点击上传</em></div>
    </el-upload>
    <el-button type="primary" @click="onImport" :disabled="!selectedFile">导入</el-button>
    <el-button @click="onExport">导出模板</el-button>
  </div>
</template>
<script setup>
import { ref } from 'vue';
import { ElMessage } from 'element-plus';
import * as XLSX from 'xlsx';
const fileList = ref([]);
const selectedFile = ref(null);
function beforeUpload(file) {
  const isExcel = file.type.includes('sheet') || file.name.endsWith('.xlsx') || file.name.endsWith('.xls');
  if (!isExcel) {
    ElMessage.error('请上传 Excel 文件');
  }
  return isExcel;
}
function onFileChange(file) {
  selectedFile.value = file.raw;
}
function validateSheet(sheet) {
  const requiredHeaders = ['工序', '班次', '设备', '产能', '切换时间'];
  const headers = sheet[0];
  for (const h of requiredHeaders) {
    if (!headers.includes(h)) {
      ElMessage.error(`缺少必填列：${h}`);
      return false;
    }
  }
  return true;
}
async function onImport() {
  if (!selectedFile.value) return;
  const reader = new FileReader();
  reader.onload = async (e) => {
    const data = new Uint8Array(e.target.result);
    const workbook = XLSX.read(data, { type: 'array' });
    const sheetName = workbook.SheetNames[0];
    const sheet = XLSX.utils.sheet_to_json(workbook.Sheets[sheetName], { header: 1 });
    if (!validateSheet(sheet)) return;
    const rows = sheet.slice(1).filter(r => r.length);
    const payload = rows.map(r => ({
      process: r[0], shift: r[1], device: r[2], capacity: r[3], switchTime: r[4]
    }));
    const res = await fetch('/api/v1/capacities/import', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    if (res.ok) {
      ElMessage.success('导入成功');
    } else {
      ElMessage.error('导入失败');
    }
  };
  reader.readAsArrayBuffer(selectedFile.value);
}
function onExport() {
  const ws = XLSX.utils.aoa_to_sheet([
    ['工序', '班次', '设备', '产能', '切换时间'],
    ['示例工序', '早班', '设备A', 100, 10]
  ]);
  const wb = XLSX.utils.book_new();
  XLSX.utils.book_append_sheet(wb, ws, '模板');
  XLSX.writeFile(wb, '产能导入模板.xlsx');
}
</script>
<style scoped></style>