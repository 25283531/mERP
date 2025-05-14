<template>
  <div class="gantt-chart-container">
    <div ref="ganttChart" class="gantt-chart"></div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch, nextTick } from 'vue';
import { ElMessage } from 'element-plus';
import * as d3 from 'd3'; // 使用 d3 来绘制甘特图
import _ from 'lodash'; // 引入 lodash 用于节流

const props = defineProps({
  plans: {
    type: Array,
    required: true,
    default: () => []
  }
});

const emit = defineEmits(['update-plan-time']);

const ganttChart = ref(null);
let svg = null;
let tooltip = null;

const margin = { top: 20, right: 30, bottom: 40, left: 150 };
let width = 800;
let height = 400;

// 节流处理拖拽更新
const throttledUpdatePlanTime = _.throttle((id, startTime, endTime) => {
  emit('update-plan-time', { id, startTime: startTime.toISOString(), endTime: endTime.toISOString() });
}, 500);

const drawChart = () => {
  if (!ganttChart.value || !props.plans || props.plans.length === 0) {
    if (svg) svg.selectAll('*').remove(); // 清空旧图
    return;
  }

  d3.select(ganttChart.value).selectAll('*').remove(); // 清空旧图

  const containerWidth = ganttChart.value.clientWidth;
  width = containerWidth - margin.left - margin.right;
  height = props.plans.length * 40 + margin.top + margin.bottom; // 根据任务数量动态调整高度

  svg = d3.select(ganttChart.value)
    .append('svg')
    .attr('width', width + margin.left + margin.right)
    .attr('height', height + margin.top + margin.bottom)
    .append('g')
    .attr('transform', `translate(${margin.left},${margin.top})`);

  // 时间转换
  const parseTime = d3.utcParse('%Y-%m-%dT%H:%M:%S.%LZ');
  const data = props.plans.map(d => ({
    ...d,
    startTime: parseTime(d.startTime),
    endTime: parseTime(d.endTime)
  })).filter(d => d.startTime && d.endTime); // 过滤掉无效时间的数据

  if (data.length === 0) {
    svg.append('text')
      .attr('x', width / 2)
      .attr('y', height / 2)
      .attr('text-anchor', 'middle')
      .text('暂无有效的生产计划数据');
    return;
  }

  const x = d3.scaleTime()
    .domain([d3.min(data, d => d.startTime), d3.max(data, d => d.endTime)])
    .range([0, width])
    .nice();

  const y = d3.scaleBand()
    .domain(data.map(d => d.name)) // 假设每个计划有唯一的 name
    .range([0, height - margin.top - margin.bottom])
    .padding(0.1);

  // X轴
  svg.append('g')
    .attr('transform', `translate(0,${height - margin.top - margin.bottom})`)
    .call(d3.axisBottom(x).ticks(d3.timeHour.every(6)).tickFormat(d3.timeFormat('%m-%d %H:%M')));

  // Y轴
  svg.append('g')
    .call(d3.axisLeft(y));

  // Tooltip
  tooltip = d3.select('body').append('div')
    .attr('class', 'gantt-tooltip')
    .style('position', 'absolute')
    .style('visibility', 'hidden')
    .style('background-color', 'white')
    .style('border', 'solid 1px black')
    .style('padding', '5px')
    .style('border-radius', '3px');

  // 任务条
  const bars = svg.selectAll('.bar')
    .data(data)
    .enter()
    .append('rect')
    .attr('class', 'bar')
    .attr('x', d => x(d.startTime))
    .attr('y', d => y(d.name))
    .attr('width', d => Math.max(0, x(d.endTime) - x(d.startTime))) // 确保宽度不为负
    .attr('height', y.bandwidth())
    .attr('fill', 'steelblue')
    .on('mouseover', (event, d) => {
      tooltip.style('visibility', 'visible')
             .html(`<strong>${d.name}</strong><br/>开始: ${d3.timeFormat('%Y-%m-%d %H:%M')(d.startTime)}<br/>结束: ${d3.timeFormat('%Y-%m-%d %H:%M')(d.endTime)}<br/>产品: ${d.productName}<br/>数量: ${d.quantity}`);
    })
    .on('mousemove', (event) => {
      tooltip.style('top', (event.pageY - 10) + 'px').style('left', (event.pageX + 10) + 'px');
    })
    .on('mouseout', () => {
      tooltip.style('visibility', 'hidden');
    });

  // 拖拽逻辑 (简化版，实际应用中需要更复杂的处理)
  const drag = d3.drag()
    .on('start', function(event, d) {
      d3.select(this).raise().attr('stroke', 'black');
    })
    .on('drag', function(event, d) {
      const newX = x.invert(event.x);
      const duration = d.endTime.getTime() - d.startTime.getTime();
      d.startTime = newX;
      d.endTime = new Date(newX.getTime() + duration);
      d3.select(this)
        .attr('x', x(d.startTime))
        .attr('width', Math.max(0, x(d.endTime) - x(d.startTime)));
      // 更新tooltip位置
      tooltip.style('top', (event.sourceEvent.pageY - 10) + 'px').style('left', (event.sourceEvent.pageX + 10) + 'px')
             .html(`<strong>${d.name}</strong><br/>开始: ${d3.timeFormat('%Y-%m-%d %H:%M')(d.startTime)}<br/>结束: ${d3.timeFormat('%Y-%m-%d %H:%M')(d.endTime)}`);
    })
    .on('end', function(event, d) {
      d3.select(this).attr('stroke', null);
      tooltip.style('visibility', 'hidden');
      // 将Date对象转换为ISO 8601 UTC字符串发送给后端
      throttledUpdatePlanTime(d.id, d.startTime, d.endTime);
      ElMessage.info(`计划 "${d.name}" 时间已调整，请在表单中确认保存。`);
    });

  bars.call(drag);

  // 懒加载和性能优化提示：
  // 对于大量批次，可以考虑：
  // 1. 虚拟滚动/渲染：只渲染视口内的条目。
  // 2. 数据聚合：在缩放级别较低时，聚合相邻的短期任务。
  // 3. 按时间段加载：仅加载特定时间范围内的任务，并在用户滚动时间轴时动态加载更多。
};

// 监听窗口大小变化，重新绘制图表
const resizeObserver = new ResizeObserver(() => {
  if (ganttChart.value) {
    nextTick(drawChart);
  }
});

onMounted(() => {
  if (ganttChart.value) {
    resizeObserver.observe(ganttChart.value);
  }
  drawChart();
});

onUnmounted(() => {
  if (ganttChart.value) {
    resizeObserver.unobserve(ganttChart.value);
  }
  if (tooltip) {
    tooltip.remove();
  }
});

watch(() => props.plans, () => {
  nextTick(drawChart);
}, { deep: true });

// 暴露给父组件调用的方法
defineExpose({
  redraw: drawChart
});

</script>

<style scoped>
.gantt-chart-container {
  width: 100%;
  height: 500px; /* 可根据需要调整默认高度 */
  overflow-x: auto; /* 允许水平滚动 */
}
.gantt-chart {
  min-width: 600px; /* 保证图表最小宽度 */
}

/* D3 Tooltip 样式 */
:global(.gantt-tooltip) {
  font-family: sans-serif;
  font-size: 12px;
  pointer-events: none; /* 允许鼠标事件穿透tooltip */
  box-shadow: 0px 0px 5px rgba(0,0,0,0.2);
}
</style>