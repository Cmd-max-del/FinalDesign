<template>
  <section class="wrap">
    <EChartPanel title="警情空间热力散点" :option="heatOption" />
    <article class="card desc">
      <h3>研判建议</h3>
      <ul>
        <li>关注热力密集街区，建立高发路段巡防网格。</li>
        <li>结合时段分布，对晚高峰与夜间重点区域动态增援。</li>
        <li>对重复高发点位建立分级预警和联动处置机制。</li>
      </ul>
    </article>
  </section>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import EChartPanel from '../components/EChartPanel.vue'
import { getHeatPoints } from '../api/analytics'

const points = ref([])

const heatOption = computed(() => ({
  tooltip: { trigger: 'item' },
  xAxis: { type: 'value', name: 'Longitude' },
  yAxis: { type: 'value', name: 'Latitude' },
  visualMap: {
    min: 0,
    max: 5,
    show: false,
    inRange: { color: ['#fbd9be', '#f59f5b', '#d74d20'] }
  },
  series: [{
    type: 'scatter',
    symbolSize: 8,
    data: points.value.map((p) => [p.longitude, p.latitude, p.weight]),
    itemStyle: { opacity: 0.72 }
  }]
}))

onMounted(async () => {
  points.value = await getHeatPoints()
})
</script>

<style scoped>
.wrap {
  display: grid;
  gap: 14px;
  animation: lift 0.65s ease;
}

.desc h3 {
  margin-top: 0;
}

.desc ul {
  margin: 0;
  padding-left: 18px;
  line-height: 1.9;
}

@keyframes lift {
  from { opacity: 0; transform: translateY(12px); }
  to { opacity: 1; transform: translateY(0); }
}
</style>
