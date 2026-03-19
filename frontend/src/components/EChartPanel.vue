<template>
  <section class="card panel">
    <h3>{{ title }}</h3>
    <div ref="chartEl" class="chart"></div>
  </section>
</template>

<script setup>
import * as echarts from 'echarts'
import { onBeforeUnmount, onMounted, ref, watch } from 'vue'

const props = defineProps({
  title: { type: String, required: true },
  option: { type: Object, required: true }
})
const emit = defineEmits(['chart-click'])

const chartEl = ref(null)
let chart = null

const render = () => {
  if (!chartEl.value) return
  if (!chart) {
    chart = echarts.init(chartEl.value)
    chart.on('click', (params) => emit('chart-click', params))
  }
  chart.setOption(props.option)
}

onMounted(() => {
  render()
  window.addEventListener('resize', render)
})

watch(
  () => props.option,
  () => render(),
  { deep: true }
)

onBeforeUnmount(() => {
  window.removeEventListener('resize', render)
  if (chart) {
    chart.dispose()
    chart = null
  }
})
</script>

<style scoped>
.panel h3 {
  margin: 2px 0 10px;
}

.chart {
  width: 100%;
  height: 360px;
}
</style>
