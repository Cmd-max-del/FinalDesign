<template>
  <section class="page">
    <article class="card uploader">
      <h2>本地 Excel 多维可视化看板</h2>
      <p class="lead">仅前端运行，不依赖后端。上传 `测试数据.xlsx` 后自动生成统计图，点击图表可下钻查看明细。</p>

      <div class="hero-meta" v-if="rows.length">
        <span>单维核心图模式</span>
        <span>支持图表下钻筛选</span>
        <span>本地离线分析</span>
      </div>

      <div class="controls">
        <input type="file" accept=".xlsx,.xls" @change="onFileChange" />
        <input v-model="keyword" placeholder="关键字过滤（地址/警情明细/事件详情/处理结果）" />
      </div>

      <div class="suggestions" v-if="rows.length">
        <span>快速提示词:</span>
        <button v-for="kw in suggestedKeywords" :key="kw" @click="applyKeyword(kw)">{{ kw }}</button>
        <small>点一下就会把关键词填入过滤框，用于快速定位相关警情。</small>
      </div>

      <section class="prompt-analysis card-lite" v-if="keyword.trim()">
        <h4>提示词专项分析：{{ keyword.trim() }}</h4>
        <div class="prompt-grid">
          <EChartPanel title="该类警情时间分布(小时)" :option="promptHourOption" />
          <EChartPanel title="该类警情地点分布(辖区单位)" :option="promptPlaceOption" @chart-click="(p) => applyFilter('辖区单位', p.name)" />
        </div>
      </section>

      <div class="chips">
        <span class="chip">总记录: {{ rows.length }}</span>
        <span class="chip">筛选后: {{ filteredRecords.length }}</span>
        <span class="chip" v-if="keyword.trim()">关键词: {{ keyword.trim() }}</span>
        <span class="chip" v-for="f in activeFilters" :key="`${f.field}-${f.value}`">
          {{ f.field }} = {{ f.value }}
          <button class="chip-close" @click="removeFilter(f)">x</button>
        </span>
        <button v-if="activeFilters.length" class="reset action-btn" @click="clearFilter">清除下钻</button>
        <button v-if="filteredRecords.length" class="export action-btn" @click="exportCurrentCsv">导出当前筛选 Excel</button>
        <button v-if="rows.length" class="report action-btn" @click="openReport">进入演示报告页</button>
      </div>

      <div class="kpi-grid" v-if="rows.length">
        <div class="kpi card-lite">
          <span>时间覆盖</span>
          <strong>{{ dateSpanText }}</strong>
        </div>
        <div class="kpi card-lite">
          <span>高风险占比</span>
          <strong>{{ highRiskRate }}</strong>
        </div>
        <div class="kpi card-lite">
          <span>最繁忙时段</span>
          <strong>{{ peakHourText }}</strong>
        </div>
        <div class="kpi card-lite">
          <span>最高发大类</span>
          <strong>{{ topCategoryText }}</strong>
        </div>
      </div>
    </article>

    <section class="dimension-layout" v-if="rows.length">
      <aside class="card dim-sidebar">
        <h3>维度导航</h3>
        <div class="dim-tree">
          <section v-for="dim in dimensions" :key="dim" class="tree-group">
            <button class="tree-root" :class="{ active: selectedDimension === dim }" @click="selectDimension(dim)">
              {{ dim }}
            </button>
            <div class="tree-leaf-wrap" v-if="selectedDimension === dim">
              <button
                v-for="metric in metricMap[dim]"
                :key="metric"
                class="tree-leaf"
                :class="{ active: selectedMetric === metric }"
                @click="selectedMetric = metric"
              >
                {{ metric }}
              </button>
            </div>
          </section>
        </div>
      </aside>

      <section class="card dim-main">
        <div class="dim-main-head">
          <h3>{{ currentChartTitle }}</h3>
          <label class="night-config">
            夜间口径
            <select v-model="nightRange">
              <option value="18-6">18:00-06:00</option>
              <option value="20-8">20:00-08:00</option>
              <option value="22-6">22:00-06:00</option>
            </select>
          </label>
        </div>
        <EChartPanel :title="currentChartTitle" :option="currentChartOption" @chart-click="onCurrentChartClick" />
      </section>
    </section>

    <article class="card table-card">
      <h3>下钻明细</h3>
      <div class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>事件ID</th>
              <th>原始事件单编号(脱敏)</th>
              <th>报警时间</th>
              <th>所属分局</th>
              <th>辖区单位</th>
              <th>警情大类</th>
              <th>警情类型</th>
              <th>风险等级</th>
              <th>事发地址</th>
              <th>处理结果</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in pageRecords" :key="item._id" class="clickable-row" @click="openDetail(item)">
              <td>{{ item['事件单编号'] }}</td>
              <td>{{ item['原始事件单编号脱敏'] || '-' }}</td>
              <td>{{ formatTime(item['报警时间']) }}</td>
              <td>{{ item['所属分局'] }}</td>
              <td>{{ item['辖区单位'] }}</td>
              <td>{{ item['警情类别'] }}</td>
              <td>{{ item['警情类型'] }}</td>
              <td>{{ item['风险等级'] }}</td>
              <td>{{ item['事发地址'] }}</td>
              <td>{{ item['处理结果'] }}</td>
            </tr>
          </tbody>
        </table>
      </div>

      <div class="pager">
        <button @click="prevPage" :disabled="page <= 1">上一页</button>
        <span>第 {{ page }} / {{ totalPages }} 页</span>
        <button @click="nextPage" :disabled="page >= totalPages">下一页</button>
      </div>
    </article>

    <aside v-if="detailRow" class="detail-mask" @click.self="detailRow = null">
      <section class="detail-panel card">
        <header>
          <h3>事件详情</h3>
          <button @click="detailRow = null">关闭</button>
        </header>
        <div class="detail-grid">
          <div><label>事件ID</label><span>{{ detailRow['事件单编号'] }}</span></div>
          <div>
            <label>原始事件单编号(脱敏)</label>
            <span>{{ detailRow['原始事件单编号脱敏'] || '-' }}</span>
            <small v-if="detailRow['原始编号近似还原']" class="approx-tip">由科学计数法近似还原</small>
            <small v-if="detailRow['疑似身份证']" class="approx-tip">疑似身份证样式，已脱敏展示</small>
          </div>
          <div><label>报警时间</label><span>{{ formatTime(detailRow['报警时间']) }}</span></div>
          <div><label>所属分局</label><span>{{ detailRow['所属分局'] }}</span></div>
          <div><label>辖区单位</label><span>{{ detailRow['辖区单位'] }}</span></div>
          <div><label>警情大类</label><span>{{ detailRow['警情类别'] }}</span></div>
          <div><label>警情类型</label><span>{{ detailRow['警情类型'] }}</span></div>
          <div><label>风险等级</label><span>{{ detailRow['风险等级'] }}</span></div>
          <div><label>处理结果</label><span>{{ detailRow['处理结果'] }}</span></div>
          <div class="full"><label>事发地址</label><span>{{ detailRow['事发地址'] }}</span></div>
          <div class="full"><label>警情明细</label><span>{{ detailRow['警情明细'] }}</span></div>
          <div class="full"><label>事件详情</label><span>{{ detailRow['事件详情'] }}</span></div>
        </div>
      </section>
    </aside>
  </section>
</template>

<script setup>
import * as XLSX from 'xlsx'
import { computed, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import EChartPanel from '../components/EChartPanel.vue'

const router = useRouter()

const rows = ref([])
const keyword = ref('')
const activeFilters = ref([])
const detailRow = ref(null)
const quality = ref({
  total: 0,
  filled: 0,
  filledTime: 0,
  approxEventId: 0,
  suspectedIdCount: 0,
  missingBefore: {},
  missingAfter: {}
})
const page = ref(1)
const pageSize = 20

const suggestedKeywords = ['盗窃', '诈骗', '纠纷', '交通', '打架', '噪音', '火灾', '校园', '医院', '夜间']
const dimensions = ['警情维度', '时间维度', '地点维度']
const selectedDimension = ref('警情维度')
const selectedMetric = ref('警情大类')
const nightRange = ref('18-6')

const REQUIRED_FIELDS = [
  '事件单编号',
  '报警时间',
  '所属分局',
  '辖区单位',
  '警情类别',
  '警情类型',
  '警情细类',
  '警情明细',
  '处理结果',
  '风险等级',
  '事发地址',
  '事件详情'
]

const NULL_LIKE = new Set(['', '-', '--', 'null', 'NULL', 'nan', 'NaN', 'N/A', '无'])

const normalizeRow = (r, idx) => ({
  _id: `row-${idx + 1}`,
  ...r,
  事件单编号: idx + 1,
  报警时间: parseExcelDate(r['报警时间'])
})

function normText(v) {
  const s = String(v ?? '').trim()
  return NULL_LIKE.has(s) ? '' : s
}

function isScientificNotation(s) {
  return /^[+-]?\d+(?:\.\d+)?[eE][+-]?\d+$/.test(String(s).trim())
}

function expandScientificNotation(s) {
  const str = String(s).trim()
  const m = str.match(/^([+-]?)(\d+)(?:\.(\d+))?[eE]([+-]?\d+)$/)
  if (!m) return str
  const sign = m[1] === '-' ? '-' : ''
  const intPart = m[2]
  const fracPart = m[3] || ''
  const exp = parseInt(m[4], 10)
  const digits = intPart + fracPart

  if (exp >= 0) {
    const zeros = exp - fracPart.length
    if (zeros >= 0) {
      return sign + digits + '0'.repeat(zeros)
    }
    const split = intPart.length + exp
    return sign + digits.slice(0, split) + '.' + digits.slice(split)
  }

  const zeros = Math.abs(exp) - intPart.length
  if (zeros >= 0) {
    return sign + '0.' + '0'.repeat(zeros) + digits
  }
  const split = intPart.length + exp
  return sign + digits.slice(0, split) + '.' + digits.slice(split)
}

function isValidChinaId18(idText) {
  const id = String(idText || '').toUpperCase()
  if (!/^\d{17}[\dX]$/.test(id)) return false
  const weights = [7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2]
  const checks = ['1', '0', 'X', '9', '8', '7', '6', '5', '4', '3', '2']
  let sum = 0
  for (let i = 0; i < 17; i += 1) {
    sum += Number(id[i]) * weights[i]
  }
  return checks[sum % 11] === id[17]
}

function maskSensitiveId(text) {
  const s = String(text || '')
  if (!s) return ''
  if (s.length <= 8) return s
  return `${s.slice(0, 4)}********${s.slice(-4)}`
}

function normalizeOriginalEventId(rawVal) {
  const raw = normText(rawVal)
  if (!raw) return { text: '', approx: false, suspectedId: false, masked: '' }

  if (isScientificNotation(raw)) {
    const expanded = expandScientificNotation(raw)
    const digitsOnly = expanded.replace(/\D/g, '')
    const txt = digitsOnly || expanded
    const suspectedId = isValidChinaId18(txt)
    return { text: txt, approx: true, suspectedId, masked: maskSensitiveId(txt) }
  }

  const suspectedId = isValidChinaId18(raw)
  return { text: raw, approx: false, suspectedId, masked: maskSensitiveId(raw) }
}

function inferRiskFromText(text) {
  const t = text.toLowerCase()
  const high = ['伤人', '爆炸', '持刀', '死亡', '火灾', '群体', '危化', '溺水', '抢劫']
  const medium = ['纠纷', '盗窃', '诈骗', '交通', '打架', '噪音']
  if (high.some((k) => t.includes(k))) return '高'
  if (medium.some((k) => t.includes(k))) return '中'
  return '低'
}

function cleanRow(raw, idx, alarmTime) {
  const row = { ...raw }
  for (const f of REQUIRED_FIELDS) {
    if (!(f in row)) row[f] = ''
  }

  const normalizedOriginal = normalizeOriginalEventId(row['事件单编号'])
  const eventId = idx + 1

  const category = normText(row['警情类别'])
  const subtype = normText(row['警情细类'])
  const type = normText(row['警情类型']) || subtype || category || '未分类'
  const fixedCategory = category || (type.includes('纠纷') ? '纠纷类' : type.includes('交通') ? '交通类' : '其他类')

  const branch = normText(row['所属分局'])
  const unit = normText(row['辖区单位']) || branch || '未知辖区'
  const fixedBranch = branch || (unit.includes('派出所') ? unit : '未知分局')

  const result = normText(row['处理结果']) || '待处理'
  const detail = normText(row['警情明细'])
  const fullDetail = normText(row['事件详情'])
  const addr = normText(row['事发地址']) || '地址缺失'
  const risk = normText(row['风险等级']) || inferRiskFromText(`${type} ${detail} ${fullDetail}`)

  return {
    ...row,
    _id: `row-${idx + 1}`,
    原始事件单编号: normalizedOriginal.text,
    原始事件单编号脱敏: normalizedOriginal.masked,
    原始编号近似还原: normalizedOriginal.approx,
    疑似身份证: normalizedOriginal.suspectedId,
    事件单编号: eventId,
    报警时间: alarmTime,
    所属分局: fixedBranch,
    辖区单位: unit,
    警情类别: fixedCategory,
    警情类型: type,
    警情细类: subtype || type,
    警情明细: detail,
    处理结果: result,
    风险等级: risk,
    事发地址: addr,
    事件详情: fullDetail
  }
}

function countMissing(list, field) {
  let n = 0
  for (const r of list) {
    const v = field === '报警时间' ? parseExcelDate(r[field]) : normText(r[field])
    if (!v) n += 1
  }
  return n
}

function buildQuality(rawRows, cleanedRows) {
  const keys = ['报警时间', '所属分局', '辖区单位', '警情类别', '警情类型', '风险等级', '处理结果', '事发地址']
  const missingBefore = {}
  const missingAfter = {}
  let filled = 0
  for (const k of keys) {
    missingBefore[k] = countMissing(rawRows, k)
    missingAfter[k] = countMissing(cleanedRows, k)
    filled += Math.max(0, missingBefore[k] - missingAfter[k])
  }
  quality.value = {
    total: cleanedRows.length,
    filled,
    filledTime: quality.value.filledTime || 0,
    missingBefore,
    missingAfter
  }
}

function parseExcelDate(val) {
  if (val === '*') return null
  if (!val) return null
  if (typeof val === 'string' && val.trim() === '*') return null
  if (val instanceof Date) return val

  // Excel numeric datetime should be interpreted as local calendar time.
  if (typeof val === 'number') {
    const parsed = XLSX.SSF.parse_date_code(val)
    if (parsed) {
      return new Date(parsed.y, parsed.m - 1, parsed.d, parsed.H, parsed.M, Math.floor(parsed.S || 0))
    }
  }

  const dt = new Date(val)
  if (!Number.isNaN(dt.getTime())) return dt
  return null
}

function fillMissingAlarmTimes(rawRows) {
  const parsed = rawRows.map((r) => parseExcelDate(r['报警时间']))
  const filled = [...parsed]

  for (let i = 1; i < filled.length; i += 1) {
    if (!filled[i] && filled[i - 1]) {
      filled[i] = new Date(filled[i - 1].getTime() + 60 * 1000)
    }
  }

  for (let i = filled.length - 2; i >= 0; i -= 1) {
    if (!filled[i] && filled[i + 1]) {
      filled[i] = new Date(filled[i + 1].getTime() - 60 * 1000)
    }
  }

  const firstValid = filled.find((x) => !!x)
  if (!firstValid) {
    const base = new Date()
    base.setHours(8, 0, 0, 0)
    for (let i = 0; i < filled.length; i += 1) {
      filled[i] = new Date(base.getTime() + i * 60 * 1000)
    }
  }

  let filledCount = 0
  for (let i = 0; i < parsed.length; i += 1) {
    if (!parsed[i] && filled[i]) filledCount += 1
  }
  return { filledTimes: filled, filledCount }
}

function onFileChange(e) {
  const file = e.target.files?.[0]
  if (!file) return
  const reader = new FileReader()
  reader.onload = (evt) => {
    const data = evt.target?.result
    const wb = XLSX.read(data, { type: 'array' })
    const firstSheet = wb.Sheets[wb.SheetNames[0]]
    const json = XLSX.utils.sheet_to_json(firstSheet, { defval: '' })
    const { filledTimes, filledCount } = fillMissingAlarmTimes(json)
    const cleaned = json.map((r, idx) => cleanRow(r, idx, filledTimes[idx]))
    quality.value.filledTime = filledCount
    quality.value.approxEventId = cleaned.filter((x) => x['原始编号近似还原']).length
    quality.value.suspectedIdCount = cleaned.filter((x) => x['疑似身份证']).length
    buildQuality(json, cleaned)
    rows.value = cleaned
    activeFilters.value = []
    keyword.value = ''
    page.value = 1
    detailRow.value = null
  }
  reader.readAsArrayBuffer(file)
}

function applyKeyword(kw) {
  keyword.value = kw
  page.value = 1
}

function isNightHour(dateObj) {
  if (!dateObj) return false
  const h = dateObj.getHours()
  const [startStr, endStr] = String(nightRange.value).split('-')
  const start = Number(startStr)
  const end = Number(endStr)
  if (Number.isNaN(start) || Number.isNaN(end)) return h >= 18 || h <= 5
  if (start <= end) return h >= start && h <= end
  return h >= start || h <= end
}

function isDawnHour(dateObj) {
  if (!dateObj) return false
  const h = dateObj.getHours()
  return h >= 0 && h <= 5
}

function keywordMatchesRow(row, kwLower) {
  if (!kwLower) return true

  // Semantic handling for time words to avoid text-only false positives.
  if (kwLower === '夜间' || kwLower === '夜晚' || kwLower === '深夜') {
    return isNightHour(row['报警时间'])
  }
  if (kwLower === '凌晨') {
    return isDawnHour(row['报警时间'])
  }

  return ['事发地址', '警情明细', '事件详情', '警情类型', '警情类别', '处理结果']
    .some((k) => String(row[k] || '').toLowerCase().includes(kwLower))
}

function isFilterActive(field, value) {
  return activeFilters.value.some((x) => x.field === field && x.value === value)
}

const filteredBaseForCharts = computed(() => {
  const kw = keyword.value.trim().toLowerCase()
  return rows.value.filter((r) => {
    const byFilters = activeFilters.value.every((f) => String(r[f.field] || '') === String(f.value))
    if (!byFilters) return false
    if (!kw) return true
    return keywordMatchesRow(r, kw)
  })
})

function countByFrom(list, field, topN = 15) {
  const map = new Map()
  for (const r of list) {
    const key = String(r[field] || '未知').trim() || '未知'
    map.set(key, (map.get(key) || 0) + 1)
  }
  return [...map.entries()]
    .sort((a, b) => b[1] - a[1])
    .slice(0, topN)
    .map(([name, count]) => ({ name, count }))
}

const byCategory = computed(() => countByFrom(filteredBaseForCharts.value, '警情类别'))
const byType = computed(() => countByFrom(filteredBaseForCharts.value, '警情类型'))
const byUnit = computed(() => countByFrom(filteredBaseForCharts.value, '辖区单位'))
const bySubtype = computed(() => countByFrom(filteredBaseForCharts.value, '警情细类'))
const byResult = computed(() => countByFrom(filteredBaseForCharts.value, '处理结果', 12))
const byRisk = computed(() => countByFrom(filteredBaseForCharts.value, '风险等级', 10))

const byHour = computed(() => {
  const bucket = Array.from({ length: 24 }, (_, i) => ({ hour: i, count: 0 }))
  for (const r of filteredBaseForCharts.value) {
    if (!r['报警时间']) continue
    bucket[r['报警时间'].getHours()].count += 1
  }
  return bucket
})

const promptScopedRecords = computed(() => {
  const kw = keyword.value.trim().toLowerCase()
  if (!kw) return []
  return rows.value.filter((r) => keywordMatchesRow(r, kw))
})

const promptByHour = computed(() => {
  const bucket = Array.from({ length: 24 }, (_, i) => ({ hour: i, count: 0 }))
  for (const r of promptScopedRecords.value) {
    if (!r['报警时间']) continue
    bucket[r['报警时间'].getHours()].count += 1
  }
  return bucket
})

const promptByPlace = computed(() => {
  const map = new Map()
  for (const r of promptScopedRecords.value) {
    const key = String(r['辖区单位'] || '未知辖区').trim() || '未知辖区'
    map.set(key, (map.get(key) || 0) + 1)
  }
  return [...map.entries()]
    .sort((a, b) => b[1] - a[1])
    .slice(0, 15)
    .map(([name, count]) => ({ name, count }))
})

const byDaily = computed(() => {
  const map = new Map()
  for (const r of filteredBaseForCharts.value) {
    if (!r['报警时间']) continue
    const t = r['报警时间']
    const y = t.getFullYear()
    const m = String(t.getMonth() + 1).padStart(2, '0')
    const d = String(t.getDate()).padStart(2, '0')
    const key = `${y}-${m}-${d}`
    map.set(key, (map.get(key) || 0) + 1)
  }
  return [...map.entries()]
    .sort((a, b) => (a[0] > b[0] ? 1 : -1))
    .map(([date, count]) => ({ date, count }))
})

const byWeekday = computed(() => {
  const labels = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
  const counts = Array.from({ length: 7 }, () => 0)
  for (const r of filteredBaseForCharts.value) {
    if (!r['报警时间']) continue
    const day = r['报警时间'].getDay()
    const idx = day === 0 ? 6 : day - 1
    counts[idx] += 1
  }
  return labels.map((name, i) => ({ name, count: counts[i] }))
})

const byTimeSegment = computed(() => {
  const items = [
    { name: '凌晨(00-05)', count: 0 },
    { name: '上午(06-11)', count: 0 },
    { name: '下午(12-17)', count: 0 },
    { name: '晚间(18-23)', count: 0 }
  ]
  for (const r of filteredBaseForCharts.value) {
    if (!r['报警时间']) continue
    const h = r['报警时间'].getHours()
    if (h <= 5) items[0].count += 1
    else if (h <= 11) items[1].count += 1
    else if (h <= 17) items[2].count += 1
    else items[3].count += 1
  }
  return items
})

const byMonth = computed(() => {
  const map = new Map()
  for (const r of filteredBaseForCharts.value) {
    if (!r['报警时间']) continue
    const y = r['报警时间'].getFullYear()
    const m = String(r['报警时间'].getMonth() + 1).padStart(2, '0')
    const key = `${y}-${m}`
    map.set(key, (map.get(key) || 0) + 1)
  }
  return [...map.entries()].sort((a, b) => (a[0] > b[0] ? 1 : -1)).map(([month, count]) => ({ month, count }))
})

const categoryOption = computed(() => ({
  tooltip: { trigger: 'item', formatter: (p) => `${p.name}: ${p.value} 起` },
  grid: { left: 90, right: 16, top: 20, bottom: 20 },
  xAxis: { type: 'value' },
  yAxis: { type: 'category', data: byCategory.value.map((x) => x.name), name: '数量(起)' },
  series: [{
    type: 'bar',
    data: byCategory.value.map((x) => ({
      value: x.count,
      itemStyle: {
        color: isFilterActive('警情类别', x.name) ? '#c24419' : '#e35d2f',
        opacity: isFilterActive('警情类别', x.name) || !activeFilters.value.length ? 1 : 0.72
      }
    }))
  }]
}))

const typeOption = computed(() => ({
  tooltip: { trigger: 'item', formatter: (p) => `${p.name}: ${p.value} 起` },
  grid: { left: 90, right: 16, top: 20, bottom: 20 },
  xAxis: { type: 'value' },
  yAxis: { type: 'category', data: byType.value.map((x) => x.name), name: '数量(起)' },
  series: [{
    type: 'bar',
    data: byType.value.map((x) => ({
      value: x.count,
      itemStyle: {
        color: isFilterActive('警情类型', x.name) ? '#145554' : '#1f7a79',
        opacity: isFilterActive('警情类型', x.name) || !activeFilters.value.length ? 1 : 0.72
      }
    }))
  }]
}))

const unitOption = computed(() => ({
  tooltip: { trigger: 'item', formatter: (p) => `${p.name}: ${p.value} 起` },
  grid: { left: 90, right: 16, top: 20, bottom: 20 },
  xAxis: { type: 'value' },
  yAxis: { type: 'category', data: byUnit.value.map((x) => x.name), name: '数量(起)' },
  series: [{
    type: 'bar',
    data: byUnit.value.map((x) => ({
      value: x.count,
      itemStyle: {
        color: isFilterActive('辖区单位', x.name) ? '#1b5337' : '#26734d',
        opacity: isFilterActive('辖区单位', x.name) || !activeFilters.value.length ? 1 : 0.72
      }
    }))
  }]
}))

const subtypeOption = computed(() => ({
  tooltip: { trigger: 'item', formatter: (p) => `${p.name}: ${p.value} 起` },
  grid: { left: 90, right: 16, top: 20, bottom: 20 },
  xAxis: { type: 'value' },
  yAxis: { type: 'category', data: bySubtype.value.map((x) => x.name), name: '数量(起)' },
  series: [{
    type: 'bar',
    data: bySubtype.value.map((x) => ({
      value: x.count,
      itemStyle: { color: '#8269c4', opacity: isFilterActive('警情细类', x.name) || !activeFilters.value.length ? 1 : 0.72 }
    }))
  }]
}))

const resultOption = computed(() => ({
  tooltip: { trigger: 'item', formatter: '{b}: {c} 起 ({d}%)' },
  series: [{
    type: 'pie',
    radius: ['35%', '70%'],
    data: byResult.value.map((x) => ({
      name: x.name,
      value: x.count,
      itemStyle: { opacity: isFilterActive('处理结果', x.name) || !activeFilters.value.length ? 1 : 0.66 }
    }))
  }]
}))

const riskOption = computed(() => ({
  tooltip: { trigger: 'item', formatter: '{b}: {c} 起 ({d}%)' },
  series: [{
    type: 'pie',
    radius: ['40%', '72%'],
    data: byRisk.value.map((x) => ({
      name: x.name,
      value: x.count,
      itemStyle: {
        opacity: isFilterActive('风险等级', x.name) || !activeFilters.value.length ? 1 : 0.66
      }
    }))
  }]
}))

const hourOption = computed(() => ({
  tooltip: { trigger: 'axis' },
  xAxis: { type: 'category', data: byHour.value.map((x) => `${x.hour}:00`) },
  yAxis: { type: 'value', name: '数量(起)' },
  series: [{
    type: 'line',
    smooth: true,
    data: byHour.value.map((x) => x.count),
    lineStyle: { color: '#b04a22' },
    areaStyle: { color: 'rgba(176,74,34,0.12)' }
  }]
}))

const trendOption = computed(() => ({
  tooltip: { trigger: 'axis' },
  dataZoom: [{ type: 'inside' }, { type: 'slider' }],
  xAxis: { type: 'category', data: byDaily.value.map((x) => x.date) },
  yAxis: { type: 'value', name: '数量(起)' },
  series: [{
    type: 'line',
    smooth: true,
    data: byDaily.value.map((x) => x.count),
    lineStyle: { color: '#1d2b2a' }
  }]
}))

const timeSegmentOption = computed(() => ({
  tooltip: { trigger: 'item', formatter: (p) => `${p.name}: ${p.value} 起` },
  xAxis: { type: 'category', data: byTimeSegment.value.map((x) => x.name) },
  yAxis: { type: 'value', name: '数量(起)' },
  series: [{
    type: 'bar',
    data: byTimeSegment.value.map((x) => x.count),
    itemStyle: { color: '#7a4f2a' }
  }]
}))

const monthTrendOption = computed(() => ({
  tooltip: { trigger: 'axis' },
  xAxis: { type: 'category', data: byMonth.value.map((x) => x.month) },
  yAxis: { type: 'value', name: '数量(起)' },
  series: [{
    type: 'line',
    smooth: true,
    data: byMonth.value.map((x) => x.count),
    lineStyle: { color: '#405f98' },
    areaStyle: { color: 'rgba(64,95,152,0.14)' }
  }]
}))

const promptHourOption = computed(() => ({
  tooltip: { trigger: 'axis' },
  xAxis: { type: 'category', data: promptByHour.value.map((x) => `${x.hour}:00`) },
  yAxis: { type: 'value', name: '数量(起)' },
  series: [{
    type: 'line',
    smooth: true,
    data: promptByHour.value.map((x) => x.count),
    lineStyle: { color: '#b04a22' },
    areaStyle: { color: 'rgba(176,74,34,0.14)' }
  }]
}))

const promptPlaceOption = computed(() => ({
  tooltip: { trigger: 'item', formatter: (p) => `${p.name}: ${p.value} 起` },
  grid: { left: 90, right: 16, top: 20, bottom: 20 },
  xAxis: { type: 'value' },
  yAxis: { type: 'category', data: promptByPlace.value.map((x) => x.name), name: '数量(起)' },
  series: [{
    type: 'bar',
    data: promptByPlace.value.map((x) => x.count),
    itemStyle: { color: '#335f9f' }
  }]
}))

const weekdayOption = computed(() => ({
  tooltip: { trigger: 'item', formatter: (p) => `${p.name}: ${p.value} 起` },
  xAxis: { type: 'category', data: byWeekday.value.map((x) => x.name) },
  yAxis: { type: 'value', name: '数量(起)' },
  series: [{
    type: 'bar',
    data: byWeekday.value.map((x) => x.count),
    itemStyle: { color: '#cf8a1a' }
  }]
}))

const metricMap = {
  警情维度: ['警情大类', '警情类型', '警情细类', '风险等级', '处理结果'],
  时间维度: ['小时分布', '时段分层', '周内分布', '日趋势', '月趋势'],
  地点维度: ['辖区单位']
}

const availableMetrics = computed(() => metricMap[selectedDimension.value] || [])

watch(
  () => selectedDimension.value,
  (val) => {
    const metrics = metricMap[val] || []
    selectedMetric.value = metrics[0] || ''
  }
)

const currentChartTitle = computed(() => {
  if (!selectedMetric.value) return '维度图表'
  return `维度分析 - ${selectedMetric.value}`
})

const currentChartOption = computed(() => {
  const m = selectedMetric.value
  if (m === '警情大类') return categoryOption.value
  if (m === '警情类型') return typeOption.value
  if (m === '警情细类') return subtypeOption.value
  if (m === '风险等级') return riskOption.value
  if (m === '处理结果') return resultOption.value
  if (m === '辖区单位') return unitOption.value
  if (m === '小时分布') return hourOption.value
  if (m === '时段分层') return timeSegmentOption.value
  if (m === '周内分布') return weekdayOption.value
  if (m === '日趋势') return trendOption.value
  if (m === '月趋势') return monthTrendOption.value
  return categoryOption.value
})

function selectDimension(dim) {
  selectedDimension.value = dim
}

function onCurrentChartClick(params) {
  const filterMap = {
    警情大类: '警情类别',
    警情类型: '警情类型',
    警情细类: '警情细类',
    风险等级: '风险等级',
    处理结果: '处理结果',
    辖区单位: '辖区单位'
  }
  const field = filterMap[selectedMetric.value]
  if (field && params?.name) {
    applyFilter(field, params.name)
  }
}

function applyFilter(field, value) {
  const exists = activeFilters.value.find((x) => x.field === field && x.value === value)
  if (exists) {
    activeFilters.value = activeFilters.value.filter((x) => !(x.field === field && x.value === value))
  } else {
    activeFilters.value.push({ field, value })
  }
  page.value = 1
}

function clearFilter() {
  activeFilters.value = []
  detailRow.value = null
  page.value = 1
}

function removeFilter(filter) {
  activeFilters.value = activeFilters.value.filter((x) => !(x.field === filter.field && x.value === filter.value))
  page.value = 1
}

const filteredRecords = computed(() => {
  return filteredBaseForCharts.value
})

const dateSpanText = computed(() => {
  const vals = rows.value.map((x) => x['报警时间']).filter(Boolean)
  if (!vals.length) return '-'
  const sorted = [...vals].sort((a, b) => a - b)
  return `${formatTime(sorted[0])} ~ ${formatTime(sorted[sorted.length - 1])}`
})

const highRiskRate = computed(() => {
  if (!rows.value.length) return '-'
  const highCount = rows.value.filter((x) => String(x['风险等级'] || '').includes('高')).length
  return `${((highCount / rows.value.length) * 100).toFixed(1)}%`
})

const peakHourText = computed(() => {
  if (!byHour.value.length) return '-'
  const top = [...byHour.value].sort((a, b) => b.count - a.count)[0]
  return `${String(top.hour).padStart(2, '0')}:00 (${top.count}起)`
})

const topCategoryText = computed(() => {
  if (!byCategory.value.length) return '-'
  const t = byCategory.value[0]
  return `${t.name} (${t.count}起)`
})

function exportCurrentCsv() {
  const exportRows = filteredRecords.value.map((x) => ({
    事件单编号: x['事件单编号'],
    报警时间: formatTime(x['报警时间']),
    所属分局: x['所属分局'],
    辖区单位: x['辖区单位'],
    警情类别: x['警情类别'],
    警情类型: x['警情类型'],
    警情明细: x['警情明细'],
    风险等级: x['风险等级'],
    事发地址: x['事发地址'],
    处理结果: x['处理结果']
  }))
  const ws = XLSX.utils.json_to_sheet(exportRows)
  const wb = XLSX.utils.book_new()
  XLSX.utils.book_append_sheet(wb, ws, '筛选结果')
  XLSX.writeFile(wb, '筛选结果导出.xlsx')
}

function openReport() {
  const payload = {
    generatedAt: new Date().toISOString(),
    total: rows.value.length,
    filtered: filteredRecords.value.length,
    activeFilters: activeFilters.value,
    keyword: keyword.value,
    kpi: {
      dateSpanText: dateSpanText.value,
      highRiskRate: highRiskRate.value,
      peakHourText: peakHourText.value,
      topCategoryText: topCategoryText.value
    },
    topCategory: byCategory.value.slice(0, 10),
    topType: byType.value.slice(0, 10),
    topUnit: byUnit.value.slice(0, 10),
    topRisk: byRisk.value.slice(0, 10),
    sampleRows: filteredRecords.value.slice(0, 30).map((x) => ({
      事件单编号: x['事件单编号'],
      报警时间: formatTime(x['报警时间']),
      辖区单位: x['辖区单位'],
      警情类别: x['警情类别'],
      警情类型: x['警情类型'],
      风险等级: x['风险等级'],
      事发地址: x['事发地址']
    }))
  }
  sessionStorage.setItem('visual_report_payload', JSON.stringify(payload))
  router.push('/report')
}

function openDetail(row) {
  detailRow.value = row
}

const totalPages = computed(() => Math.max(1, Math.ceil(filteredRecords.value.length / pageSize)))
const pageRecords = computed(() => {
  const start = (page.value - 1) * pageSize
  return filteredRecords.value.slice(start, start + pageSize)
})

function prevPage() {
  if (page.value > 1) page.value -= 1
}

function nextPage() {
  if (page.value < totalPages.value) page.value += 1
}

function formatTime(v) {
  if (!v) return '-'
  if (v instanceof Date) {
    const y = v.getFullYear()
    const m = String(v.getMonth() + 1).padStart(2, '0')
    const d = String(v.getDate()).padStart(2, '0')
    const hh = String(v.getHours()).padStart(2, '0')
    const mm = String(v.getMinutes()).padStart(2, '0')
    return `${y}-${m}-${d} ${hh}:${mm}`
  }
  return String(v)
}
</script>

<style scoped>
.page {
  display: grid;
  gap: 14px;
  animation: fadeIn 0.7s ease;
}

.uploader h2 {
  margin: 0 0 8px;
  font-size: clamp(22px, 3.6vw, 30px);
  line-height: 1.2;
  letter-spacing: 0.4px;
}

.uploader {
  position: relative;
  overflow: hidden;
}

.uploader::before {
  content: '';
  position: absolute;
  inset: 0 0 auto 0;
  height: 3px;
  background: linear-gradient(90deg, #1f7a79, #b04a22);
}

.lead {
  margin: 0;
  color: #4e5d5a;
}

.hero-meta {
  margin-top: 10px;
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.hero-meta span {
  font-size: 12px;
  color: #2f3e3b;
  background: linear-gradient(135deg, #f7efe3, #e8f3ef);
  border: 1px solid #d9ceb8;
  border-radius: 999px;
  padding: 4px 10px;
}

.controls {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}

.controls input {
  padding: 10px 12px;
  border: 1px solid var(--panel-border);
  border-radius: 10px;
  background: #fff;
}

.controls input[type='file'] {
  background: #fdf8ef;
}

.controls input:focus {
  border-color: #1f7a79;
  outline: 2px solid rgba(31, 122, 121, 0.15);
}

.suggestions {
  margin-top: 10px;
  display: flex;
  gap: 8px;
  align-items: center;
  flex-wrap: wrap;
}

.suggestions span {
  color: var(--muted);
  font-size: 12px;
}

.suggestions button {
  border: 1px solid var(--panel-border);
  background: #fffdf8;
  border-radius: 999px;
  padding: 4px 10px;
  cursor: pointer;
  transition: all 0.18s ease;
}

.suggestions button:hover {
  border-color: #1f7a79;
  color: #1f7a79;
}

.suggestions small {
  color: var(--muted);
  font-size: 12px;
}

.chips {
  margin-top: 10px;
  display: flex;
  gap: 8px;
  align-items: center;
  flex-wrap: wrap;
}

.chip {
  font-size: 12px;
  background: #efe8db;
  padding: 4px 8px;
  border-radius: 999px;
  border: 1px solid #e1d6c1;
}

.chip-close {
  margin-left: 6px;
  border: 0;
  border-radius: 999px;
  width: 18px;
  height: 18px;
  cursor: pointer;
  background: #d8ccba;
}

.action-btn {
  box-shadow: 0 5px 14px rgba(0, 0, 0, 0.12);
}

.reset {
  border: 0;
  background: #1d2b2a;
  color: #fff;
  border-radius: 999px;
  padding: 6px 10px;
  cursor: pointer;
  transition: transform 0.16s ease;
}

.reset:hover,
.export:hover,
.report:hover {
  transform: translateY(-1px);
}

.export {
  border: 0;
  background: #1f7a79;
  color: #fff;
  border-radius: 999px;
  padding: 6px 10px;
  cursor: pointer;
}

.report {
  border: 0;
  background: #b04a22;
  color: #fff;
  border-radius: 999px;
  padding: 6px 10px;
  cursor: pointer;
}

.kpi-grid {
  margin-top: 12px;
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 10px;
}

.card-lite {
  position: relative;
  border: 1px solid var(--panel-border);
  border-radius: 10px;
  padding: 12px;
  background: linear-gradient(145deg, #fffdf8, #fbf3e7);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.7);
}

.card-lite::after {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  width: 100%;
  height: 2px;
  background: linear-gradient(90deg, rgba(31, 122, 121, 0.8), rgba(176, 74, 34, 0.8));
  border-radius: 10px 10px 0 0;
}

.card-lite span {
  display: block;
  color: var(--muted);
  font-size: 12px;
}

.card-lite strong {
  font-family: 'Space Grotesk', sans-serif;
  font-size: 18px;
}

.prompt-analysis {
  margin-top: 12px;
}

.prompt-analysis h4 {
  margin: 0 0 10px;
}

.prompt-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
}

.grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px;
}

.dimension-layout {
  display: grid;
  grid-template-columns: 280px 1fr;
  gap: 14px;
  align-items: start;
}

.dim-sidebar {
  position: sticky;
  top: 12px;
}

.dim-sidebar h3,
.dim-main h3 {
  margin-top: 0;
}

.dim-tree {
  display: grid;
  gap: 8px;
}

.tree-group {
  border: 1px solid var(--panel-border);
  border-radius: 10px;
  background: #fffbf4;
  padding: 8px;
}

.tree-root {
  width: 100%;
  text-align: left;
  border: 0;
  border-radius: 8px;
  padding: 8px 10px;
  cursor: pointer;
  background: #f3ede2;
  font-weight: 600;
}

.tree-root.active {
  background: #1d2b2a;
  color: #fff;
}

.tree-leaf-wrap {
  display: grid;
  gap: 6px;
  margin-top: 8px;
}

.tree-leaf {
  border: 1px solid var(--panel-border);
  border-radius: 8px;
  padding: 6px 8px;
  text-align: left;
  background: #fff;
  cursor: pointer;
  transition: all 0.16s ease;
}

.tree-leaf:hover {
  border-color: #1f7a79;
}

.tree-leaf.active {
  background: #1f7a79;
  border-color: #1f7a79;
  color: #fff;
}

.dim-main-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 10px;
  margin-bottom: 8px;
}

.dim-main {
  background: linear-gradient(180deg, #fffdf8 0%, #fffaf2 100%);
  border-color: #cfc2a7;
}

.night-config {
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--muted);
  font-size: 13px;
}

.night-config select {
  border: 1px solid var(--panel-border);
  border-radius: 8px;
  padding: 6px 8px;
  background: #fff;
}

.table-wrap {
  overflow-x: auto;
  border: 1px solid var(--panel-border);
  border-radius: 12px;
  background: #fff;
}

table {
  width: 100%;
  border-collapse: collapse;
}

th,
td {
  border-bottom: 1px solid var(--panel-border);
  text-align: left;
  padding: 10px 8px;
  white-space: nowrap;
}

th {
  background: #f7f2e8;
  font-weight: 700;
  position: sticky;
  top: 0;
  z-index: 2;
}

tbody tr:nth-child(even) {
  background: #fcf8f0;
}

.clickable-row {
  cursor: pointer;
}

.clickable-row:hover {
  background: #f8f3ea;
}

.pager {
  margin-top: 12px;
  display: flex;
  gap: 10px;
  align-items: center;
}

.pager button {
  border: 0;
  background: var(--ink);
  color: #fff;
  border-radius: 8px;
  padding: 6px 10px;
  cursor: pointer;
  transition: transform 0.16s ease;
}

.pager button:hover:not(:disabled) {
  transform: translateY(-1px);
}

.pager button:disabled {
  opacity: 0.45;
  cursor: not-allowed;
}

.detail-mask {
  position: fixed;
  inset: 0;
  background: rgba(29, 43, 42, 0.35);
  display: flex;
  justify-content: flex-end;
  z-index: 40;
}

.detail-panel {
  width: min(560px, 100%);
  height: 100%;
  border-radius: 0;
  overflow-y: auto;
}

.detail-panel header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid var(--panel-border);
  padding-bottom: 8px;
}

.detail-panel header button {
  border: 0;
  border-radius: 8px;
  background: #1d2b2a;
  color: #fff;
  padding: 6px 10px;
}

.detail-grid {
  margin-top: 10px;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}

.detail-grid .full {
  grid-column: span 2;
}

.detail-grid label {
  display: block;
  color: var(--muted);
  font-size: 12px;
}

.detail-grid span {
  display: block;
}

.approx-tip {
  display: inline-block;
  margin-top: 4px;
  font-size: 12px;
  color: #9a3f1f;
  background: rgba(227, 93, 47, 0.12);
  border-radius: 999px;
  padding: 2px 8px;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(8px); }
  to { opacity: 1; transform: translateY(0); }
}

@media (max-width: 900px) {
  .controls,
  .grid {
    grid-template-columns: 1fr;
  }

  .dimension-layout {
    grid-template-columns: 1fr;
  }

  .dim-sidebar {
    position: static;
  }

  .prompt-grid {
    grid-template-columns: 1fr;
  }

  .kpi-grid,
  .detail-grid {
    grid-template-columns: 1fr;
  }

  .uploader h2 {
    font-size: 22px;
  }

  .chips {
    gap: 6px;
  }

  .action-btn {
    width: 100%;
    text-align: center;
  }

  .detail-grid .full {
    grid-column: span 1;
  }
}
</style>
