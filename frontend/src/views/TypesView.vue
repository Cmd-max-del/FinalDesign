<template>
  <section class="page">
    <EChartPanel title="警情类型环形占比" :option="pieOption" />
  </section>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import EChartPanel from '../components/EChartPanel.vue'
import { getTypeDistribution } from '../api/analytics'

const typeData = ref([])

const pieOption = computed(() => ({
  tooltip: { trigger: 'item' },
  legend: { top: 6 },
  series: [{
    type: 'pie',
    radius: ['40%', '72%'],
    data: typeData.value.map((x) => ({ name: x.incident_type, value: x.count })),
    itemStyle: {
      borderColor: '#fffdf8',
      borderWidth: 3
    }
  }]
}))

onMounted(async () => {
  typeData.value = await getTypeDistribution()
})
</script>

<style scoped>
.page {
  animation: fadeIn 0.6s ease;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}
</style>
