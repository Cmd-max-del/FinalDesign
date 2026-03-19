<template>
  <section class="card collab">
    <h2>多用户协同与冲突提示</h2>
    <p>演示同一警员在重叠时段重复派警时的自动冲突检测。</p>

    <div class="grid">
      <input v-model.number="form.incident_id" type="number" placeholder="警情ID (如 1)" />
      <input v-model="form.officer_id" placeholder="警员编号 (如 officer-001)" />
      <input v-model="form.start_time" type="datetime-local" />
      <input v-model="form.end_time" type="datetime-local" />
      <input v-model="form.created_by" placeholder="操作人 (如 admin-a)" />
      <button @click="submit" :disabled="loading">{{ loading ? '提交中...' : '创建派警' }}</button>
    </div>

    <article v-if="result" class="result" :class="result.accepted ? 'ok' : 'warn'">
      <h3>{{ result.accepted ? '创建成功' : '冲突提示' }}</h3>
      <div>{{ result.message }}</div>
      <ul v-if="!result.accepted && result.conflicts?.length">
        <li v-for="item in result.conflicts" :key="item.assignment_id">
          已有任务 #{{ item.assignment_id }}: incident {{ item.incident_id }}, {{ item.start_time }} ~ {{ item.end_time }}
        </li>
      </ul>
    </article>

    <article class="table-wrap">
      <h3>最近派警记录</h3>
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>Incident</th>
            <th>Officer</th>
            <th>Start</th>
            <th>End</th>
            <th>By</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="row in rows" :key="row.id">
            <td>{{ row.id }}</td>
            <td>{{ row.incident_id }}</td>
            <td>{{ row.officer_id }}</td>
            <td>{{ formatTime(row.start_time) }}</td>
            <td>{{ formatTime(row.end_time) }}</td>
            <td>{{ row.created_by }}</td>
          </tr>
        </tbody>
      </table>
    </article>
  </section>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { createAssignment, listAssignments } from '../api/collaboration'

const now = new Date()
const plus1 = new Date(now.getTime() + 60 * 60 * 1000)

const form = ref({
  incident_id: 1,
  officer_id: 'officer-001',
  start_time: toInputValue(now),
  end_time: toInputValue(plus1),
  created_by: 'admin-a'
})

const loading = ref(false)
const rows = ref([])
const result = ref(null)

function toInputValue(d) {
  const y = d.getFullYear()
  const m = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  const h = String(d.getHours()).padStart(2, '0')
  const min = String(d.getMinutes()).padStart(2, '0')
  return `${y}-${m}-${day}T${h}:${min}`
}

function formatTime(s) {
  if (!s) return '-'
  return s.replace('T', ' ').slice(0, 16)
}

async function refresh() {
  rows.value = await listAssignments()
}

async function submit() {
  loading.value = true
  try {
    const payload = {
      ...form.value,
      start_time: new Date(form.value.start_time).toISOString(),
      end_time: new Date(form.value.end_time).toISOString()
    }
    result.value = await createAssignment(payload)
    await refresh()
  } catch (e) {
    result.value = { accepted: false, message: '请求失败，请检查后端服务与输入数据。', conflicts: [] }
  } finally {
    loading.value = false
  }
}

onMounted(refresh)
</script>

<style scoped>
.collab h2 {
  margin-top: 0;
}

.grid {
  display: grid;
  gap: 10px;
  grid-template-columns: repeat(6, minmax(0, 1fr));
}

input,
button {
  padding: 10px 12px;
  border-radius: 10px;
  border: 1px solid var(--panel-border);
}

button {
  background: var(--ink);
  color: #fff;
  cursor: pointer;
}

.result {
  margin-top: 14px;
  border-radius: 12px;
  padding: 10px 12px;
}

.result.ok {
  background: rgba(38, 115, 77, 0.12);
}

.result.warn {
  background: rgba(227, 93, 47, 0.12);
}

.table-wrap {
  margin-top: 16px;
  overflow-x: auto;
}

table {
  width: 100%;
  border-collapse: collapse;
}

th,
td {
  text-align: left;
  border-bottom: 1px solid var(--panel-border);
  padding: 8px;
}

@media (max-width: 1100px) {
  .grid {
    grid-template-columns: 1fr;
  }
}
</style>
