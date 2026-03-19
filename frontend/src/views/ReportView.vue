<template>
  <section class="page">
    <article class="card head">
      <h2>警情多维可视化演示报告</h2>
      <p>生成时间：{{ generatedAtText }}</p>
      <div class="meta">
        <span>总记录：{{ data.total }}</span>
        <span>筛选后：{{ data.filtered }}</span>
        <span v-if="data.keyword">关键字：{{ data.keyword }}</span>
      </div>
      <div class="filters" v-if="data.activeFilters?.length">
        <span v-for="f in data.activeFilters" :key="`${f.field}-${f.value}`" class="chip">
          {{ f.field }} = {{ f.value }}
        </span>
      </div>
      <button class="print" @click="printPage">打印/导出PDF</button>
    </article>

    <section class="kpis">
      <article class="card"><label>时间覆盖</label><strong>{{ data.kpi?.dateSpanText || '-' }}</strong></article>
      <article class="card"><label>高风险占比</label><strong>{{ data.kpi?.highRiskRate || '-' }}</strong></article>
      <article class="card"><label>最繁忙时段</label><strong>{{ data.kpi?.peakHourText || '-' }}</strong></article>
      <article class="card"><label>最高发类别</label><strong>{{ data.kpi?.topCategoryText || '-' }}</strong></article>
    </section>

    <section class="grid">
      <article class="card">
        <h3>警情类别 Top10</h3>
        <ol><li v-for="x in data.topCategory || []" :key="`c-${x.name}`">{{ x.name }}：{{ x.count }}</li></ol>
      </article>
      <article class="card">
        <h3>警情类型 Top10</h3>
        <ol><li v-for="x in data.topType || []" :key="`t-${x.name}`">{{ x.name }}：{{ x.count }}</li></ol>
      </article>
      <article class="card">
        <h3>辖区单位 Top10</h3>
        <ol><li v-for="x in data.topUnit || []" :key="`u-${x.name}`">{{ x.name }}：{{ x.count }}</li></ol>
      </article>
      <article class="card">
        <h3>风险等级分布</h3>
        <ol><li v-for="x in data.topRisk || []" :key="`r-${x.name}`">{{ x.name }}：{{ x.count }}</li></ol>
      </article>
    </section>

    <article class="card">
      <h3>样例明细（前30条）</h3>
      <div class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>事件单编号</th>
              <th>报警时间</th>
              <th>辖区单位</th>
              <th>警情类别</th>
              <th>警情类型</th>
              <th>风险等级</th>
              <th>事发地址</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(r, idx) in data.sampleRows || []" :key="`row-${idx}`">
              <td>{{ r['事件单编号'] }}</td>
              <td>{{ r['报警时间'] }}</td>
              <td>{{ r['辖区单位'] }}</td>
              <td>{{ r['警情类别'] }}</td>
              <td>{{ r['警情类型'] }}</td>
              <td>{{ r['风险等级'] }}</td>
              <td>{{ r['事发地址'] }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </article>
  </section>
</template>

<script setup>
import { computed, ref } from 'vue'

const raw = sessionStorage.getItem('visual_report_payload')
const data = ref(raw ? JSON.parse(raw) : { total: 0, filtered: 0 })

const generatedAtText = computed(() => {
  if (!data.value.generatedAt) return '-'
  return new Date(data.value.generatedAt).toLocaleString()
})

function printPage() {
  window.print()
}
</script>

<style scoped>
.page { display: grid; gap: 14px; }
.head .meta { display: flex; gap: 12px; flex-wrap: wrap; color: var(--muted); }
.filters { margin-top: 8px; display: flex; gap: 8px; flex-wrap: wrap; }
.chip { background: #efe8db; border-radius: 999px; padding: 4px 10px; font-size: 12px; }
.print { margin-top: 10px; border: 0; border-radius: 8px; padding: 8px 12px; background: #1d2b2a; color: #fff; cursor: pointer; }
.kpis { display: grid; gap: 10px; grid-template-columns: repeat(4, minmax(0, 1fr)); }
label { display: block; color: var(--muted); font-size: 12px; }
strong { font-family: 'Space Grotesk', sans-serif; }
.grid { display: grid; gap: 10px; grid-template-columns: repeat(2, minmax(0, 1fr)); }
.table-wrap { overflow-x: auto; }
table { width: 100%; border-collapse: collapse; }
th, td { border-bottom: 1px solid var(--panel-border); text-align: left; padding: 8px; white-space: nowrap; }
@media (max-width: 900px) {
  .kpis, .grid { grid-template-columns: 1fr; }
}
@media print {
  .print { display: none; }
}
</style>
