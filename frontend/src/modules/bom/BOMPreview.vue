<template>
  <el-card>
    <el-tree
      :data="bomTree"
      :props="treeProps"
      node-key="id"
      default-expand-all
      :expand-on-click-node="false"
      :highlight-current="true"
      :render-content="renderNode"
    />
  </el-card>
</template>
<script setup>
import { defineProps, ref, watch } from 'vue';
const props = defineProps({
  bom: { type: Object, default: () => ({}) }
});
const bomTree = ref([]);
const treeProps = {
  children: 'children',
  label: 'name'
};
watch(() => props.bom, (val) => {
  bomTree.value = val.items ? [val] : [];
}, { immediate: true });
function renderNode(h, { node, data }) {
  return h('span', null, `${data.name}（${data.code || ''}） × ${data.quantity || 1}`);
}
</script>
<style scoped></style>