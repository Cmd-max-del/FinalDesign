<template>
  <section>
    <EChartPanel title="日警情趋势" :option="trendOption" />
  </section>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import EChartPanel from '../components/EChartPanel.vue'
import { getDailyTrend } from '../api/analytics'

const trendData = ref([])

const trendOption = computed(() => ({
  tooltip: { trigger: 'axis' },
  dataZoom: [{ type: 'inside' }, { type: 'slider' }],
  xAxis: { type: 'category', data: trendData.value.map((x) => x.date) },
  yAxis: { type: 'value' },
  series: [{
    type: 'line',
    data: trendData.value.map((x) => x.count),
    smooth: true,
    lineStyle: { color: '#26734d', width: 3 },
    areaStyle: { color: 'rgba(38,115,77,0.18)' }
  }]
}))

onMounted(async () => {
  trendData.value = await getDailyTrend()
})
</script>
