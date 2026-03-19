<template>
  <section class="grid">
    <article class="card stat" v-for="item in cards" :key="item.label">
      <span>{{ item.label }}</span>
      <strong>{{ item.value }}</strong>
    </article>

    <EChartPanel title="24小时警情分布" :option="hourOption" />
    <EChartPanel title="警情类型TOP10" :option="typeOption" />
  </section>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import EChartPanel from '../components/EChartPanel.vue'
import { getHourDistribution, getOverview, getTypeDistribution } from '../api/analytics'

const overview = ref({ total_incidents: 0, avg_duration_min: 0, avg_police_unit_count: 0 })
const hourData = ref([])
const typeData = ref([])

const cards = computed(() => [
  { label: '警情总量', value: overview.value.total_incidents },
  { label: '平均处置时长(分钟)', value: overview.value.avg_duration_min },
  { label: '平均调配警力', value: overview.value.avg_police_unit_count }
])

const hourOption = computed(() => ({
  tooltip: { trigger: 'axis' },
  xAxis: { type: 'category', data: hourData.value.map((x) => `${x.hour}:00`) },
  yAxis: { type: 'value' },
  series: [{
    data: hourData.value.map((x) => x.count),
    type: 'line',
    smooth: true,
    lineStyle: { color: '#1f7a79' },
    areaStyle: { color: 'rgba(31,122,121,0.2)' }
  }]
}))

const typeOption = computed(() => ({
  tooltip: { trigger: 'item' },
  xAxis: { type: 'value' },
  yAxis: { type: 'category', data: typeData.value.map((x) => x.incident_type) },
  series: [{
    type: 'bar',
    data: typeData.value.map((x) => x.count),
    itemStyle: { color: '#e35d2f' }
  }]
}))

onMounted(async () => {
  const [o, h, t] = await Promise.all([getOverview(), getHourDistribution(), getTypeDistribution()])
  overview.value = o
  hourData.value = h
  typeData.value = t
})
</script>

<style scoped>
.grid {
  display: grid;
  grid-template-columns: repeat(12, 1fr);
  gap: 14px;
  animation: fadeIn 0.7s ease;
}

.stat {
  grid-column: span 4;
  min-height: 120px;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.stat span {
  color: var(--muted);
  margin-bottom: 8px;
}

.stat strong {
  font-size: 34px;
  font-family: 'Space Grotesk', sans-serif;
}

.grid :deep(.panel) {
  grid-column: span 6;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(8px); }
  to { opacity: 1; transform: translateY(0); }
}

@media (max-width: 900px) {
  .stat,
  .grid :deep(.panel) {
    grid-column: span 12;
  }
}
</style>
