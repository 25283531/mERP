<template>
  <el-dialog
    v-model="visible"
    :title="isBatchImport ? '批量导入成员' : (form.id ? '编辑成员' : '新增成员')"
    width="600px"
    @close="onClose"
    :close-on-click-modal="false"
  >
    <template v-if="isBatchImport">
      <el-upload
        ref="uploadRef"
        action=""
        :before-upload="handleBeforeUpload"
        :on-change="handleFileChange"
        :on-remove="handleFileRemove"
        :auto-upload="false"
        :limit="1"
        accept=".xls,.xlsx"
        drag
      >
        <el-icon class="el-icon--upload"><upload-filled /></el-icon>
        <div class="el-upload__text">
          将文件拖到此处，或<em>点击上传</em>
        </div>
        <template #tip>
          <div class="el-upload__tip">
            请上传 Excel 文件 (xls, xlsx)，文件大小不超过 10MB。
            <el-link type="primary" @click="downloadTemplate">下载模板</el-link>
          </div>
        </template>
      </el-upload>
      <div v-if="excelColumns.length > 0" style="margin-top: 20px;">
        <h4>列映射（将 Excel 列名映射到系统字段）</h4>
        <el-table :data="columnMapping" border size="small">
          <el-table-column prop="excelHeader" label="Excel 列名" />
          <el-table-column label="系统字段">
            <template #default="{ row }">
              <el-select v-model="row.systemField" placeholder="选择系统字段" clearable>
                <el-option v-for="field in systemFields" :key="field.value" :label="field.label" :value="field.value" />
              </el-select>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </template>
    <template v-else>
      <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
        <el-form-item label="姓名" prop="name">
          <el-input v-model="form.name" placeholder="请输入姓名" />
        </el-form-item>
        <el-form-item label="工号" prop="employeeId">
          <el-input v-model="form.employeeId" placeholder="请输入工号" />
        </el-form-item>
        <el-form-item label="职位" prop="position">
          <el-input v-model="form.position" placeholder="请输入职位" />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="form.email" placeholder="请输入邮箱" />
        </el-form-item>
        <el-form-item label="电话" prop="phone">
          <el-input v-model="form.phone" placeholder="请输入电话号码" />
        </el-form-item>
        <el-form-item label="所属部门" prop="departmentId">
           <el-input v-model="departmentNameDisplay" disabled />
        </el-form-item>
      </el-form>
    </template>
    <template #footer>
      <el-button @click="onClose">取消</el-button>
      <el-button type="primary" @click="onSave" :loading="saving">{{ isBatchImport ? '开始导入' : '保存' }}</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, watch, defineProps, defineEmits, computed, nextTick } from 'vue';
import { ElMessage, ElMessageBox } from 'element-plus';
import { UploadFilled } from '@element-plus/icons-vue';
import * as XLSX from 'xlsx'; // For Excel import

const props = defineProps({
  member: { type: Object, default: () => ({}) },
  visible: { type: Boolean, default: false },
  isBatchImport: { type: Boolean, default: false },
  departmentId: { type: [String, Number], default: null },
  departmentName: { type: String, default: '' }
});

const emit = defineEmits(['close', 'saved', 'imported']);

const visible = ref(props.visible);
const form = ref({ ...props.member });
const formRef = ref(null);
const uploadRef = ref(null);
const saving = ref(false);
const excelFile = ref(null);
const excelColumns = ref([]);
const columnMapping = ref([]);

const departmentNameDisplay = computed(() => props.departmentName || '未指定部门');

const systemFields = ref([
  { label: '姓名', value: 'name' },
  { label: '工号', value: 'employeeId' },
  { label: '职位', value: 'position' },
  { label: '邮箱', value: 'email' },
  { label: '电话', value: 'phone' },
  // Add more fields as needed
]);

const rules = {
  name: [{ required: true, message: '请输入姓名', trigger: 'blur' }],
  employeeId: [{ required: true, message: '请输入工号', trigger: 'blur' }],
  departmentId: [{ required: true, message: '所属部门不能为空', trigger: 'blur' }]
};

watch(() => props.visible, (newVal) => {
  visible.value = newVal;
  if (newVal) {
    form.value = { ...props.member, departmentId: props.departmentId };
    if (!props.isBatchImport && formRef.value) {
      nextTick(() => formRef.value.resetFields());
    }
    if (props.isBatchImport) {
      excelFile.value = null;
      excelColumns.value = [];
      columnMapping.value = [];
      uploadRef.value?.clearFiles();
    }
  }
});

function onClose() {
  emit('close');
}

async function onSave() {
  saving.value = true;
  if (props.isBatchImport) {
    await handleBatchImportSubmit();
  } else {
    await handleFormSubmit();
  }
  saving.value = false;
}

async function handleFormSubmit() {
  if (!formRef.value) return;
  try {
    const valid = await formRef.value.validate();
    if (!valid) return;

    const payload = { ...form.value };
    if (!payload.departmentId && props.departmentId) {
        payload.departmentId = props.departmentId;
    }

    if (!payload.departmentId) {
        ElMessage.error('必须指定成员所属的部门');
        return;
    }

    const response = await fetch('/api/v1/org/members', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.message || (form.value.id ? '更新成员失败' : '新增成员失败'));
    }
    ElMessage.success(form.value.id ? '成员更新成功' : '成员新增成功');
    emit('saved');
    onClose();
  } catch (error) {
    ElMessage.error(`操作失败: ${error.message}`);
  }
}

function handleBeforeUpload(file) {
  const isExcel = file.type === 'application/vnd.ms-excel' || file.type === 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet';
  const isLt10M = file.size / 1024 / 1024 < 10;
  if (!isExcel) {
    ElMessage.error('只能上传 Excel 文件!');
    return false;
  }
  if (!isLt10M) {
    ElMessage.error('上传文件大小不能超过 10MB!');
    return false;
  }
  return true;
}

function handleFileChange(file, fileList) {
  if (fileList.length > 0) {
    excelFile.value = file.raw;
    parseExcelHeader(file.raw);
  }
}

function handleFileRemove() {
  excelFile.value = null;
  excelColumns.value = [];
  columnMapping.value = [];
}

function parseExcelHeader(file) {
  const reader = new FileReader();
  reader.onload = (e) => {
    const data = e.target.result;
    const workbook = XLSX.read(data, { type: 'binary' });
    const firstSheetName = workbook.SheetNames[0];
    const worksheet = workbook.Sheets[firstSheetName];
    const header = XLSX.utils.sheet_to_json(worksheet, { header: 1 })[0];
    excelColumns.value = header.map(h => String(h).trim()).filter(h => h);
    // Auto-map if possible, or set up for manual mapping
    columnMapping.value = excelColumns.value.map(excelHeader => {
      const foundSystemField = systemFields.value.find(sf => sf.label.toLowerCase() === excelHeader.toLowerCase() || sf.value.toLowerCase() === excelHeader.toLowerCase());
      return {
        excelHeader,
        systemField: foundSystemField ? foundSystemField.value : null,
      };
    });
  };
  reader.readAsBinaryString(file);
}

async function handleBatchImportSubmit() {
  if (!excelFile.value) {
    ElMessage.error('请先上传 Excel 文件');
    return;
  }
  if (!props.departmentId) {
    ElMessage.error('未指定导入的目标部门');
    return;
  }
  if (columnMapping.value.some(m => !m.systemField)) {
    ElMessage.error('请完成所有 Excel 列到系统字段的映射');
    return;
  }

  const reader = new FileReader();
  reader.onload = async (e) => {
    const data = e.target.result;
    const workbook = XLSX.read(data, { type: 'binary' });
    const firstSheetName = workbook.SheetNames[0];
    const worksheet = workbook.Sheets[firstSheetName];
    const jsonData = XLSX.utils.sheet_to_json(worksheet);

    const membersToImport = jsonData.map(row => {
      const member = { departmentId: props.departmentId };
      columnMapping.value.forEach(mapping => {
        if (mapping.systemField && row[mapping.excelHeader] !== undefined) {
          member[mapping.systemField] = row[mapping.excelHeader];
        }
      });
      return member;
    }).filter(member => member.name && member.employeeId); // Basic validation

    if (membersToImport.length === 0) {
      ElMessage.warning('没有可导入的有效成员数据。请检查文件内容和列映射。');
      return;
    }

    try {
      const response = await fetch('/api/v1/org/members/batch', { // Assuming a batch import endpoint
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ departmentId: props.departmentId, members: membersToImport }),
      });
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.message || '批量导入失败');
      }
      ElMessage.success(`成功导入 ${membersToImport.length} 名成员`);
      emit('imported');
      onClose();
    } catch (error) {
      ElMessage.error(`导入失败: ${error.message}`);
    }
  };
  reader.readAsBinaryString(excelFile.value);
}

function downloadTemplate() {
    const templateData = [systemFields.value.map(f => f.label)];
    // Example row
    const exampleRow = {};
    systemFields.value.forEach(f => exampleRow[f.label] = `示例${f.label}`);
    templateData.push(Object.values(exampleRow));

    const ws = XLSX.utils.aoa_to_sheet(templateData);
    const wb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb, ws, '成员导入模板');
    XLSX.writeFile(wb, '成员导入模板.xlsx');
    ElMessage.info('模板文件已开始下载。');
}

</script>

<style scoped>
.el-upload__tip {
  line-height: 1.2;
  margin-top: 7px;
}
.el-upload__tip .el-link {
  font-size: 12px;
  vertical-align: baseline;
  margin-left: 5px;
}
</style>