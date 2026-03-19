<template>
  <section class="card assistant">
    <h2>自然语言警情分析助手</h2>
    <p>示例：近一段时间的警情概况如何？哪类警情最多？</p>
    <div class="status-row">
      <span class="status-tag" :class="status.llm_enabled ? 'ok' : 'warn'">
        {{ status.llm_enabled ? `LLM 已启用 (${status.model})` : 'LLM 未启用，当前为本地规则兜底' }}
      </span>
    </div>

    <div class="input-row">
      <input v-model="question" placeholder="请输入问题" @keyup.enter="submit" />
      <button @click="submit" :disabled="loading">{{ loading ? '分析中...' : '提交' }}</button>
    </div>

    <article class="answer" v-if="answer">
      <h3>回答</h3>
      <small class="source">来源：{{ answerSource === 'llm' ? '大模型' : '本地规则' }}</small>
      <div>{{ answer }}</div>
    </article>
  </section>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { askQuestion, getNLStatus } from '../api/nl'

const question = ref('')
const answer = ref('')
const answerSource = ref('rule-based')
const loading = ref(false)
const status = ref({
  llm_enabled: false,
  model: 'unknown',
  base_url_configured: false,
  api_key_configured: false
})

onMounted(async () => {
  try {
    status.value = await getNLStatus()
  } catch (e) {
    status.value.llm_enabled = false
  }
})

const submit = async () => {
  if (!question.value.trim()) return
  loading.value = true
  try {
    const data = await askQuestion(question.value)
    answer.value = data.answer
    answerSource.value = data.source || 'rule-based'
  } catch (e) {
    answer.value = '请求失败，请检查后端服务是否正常运行。'
    answerSource.value = 'rule-based'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.assistant {
  animation: pop 0.5s ease;
}

h2 {
  margin: 0 0 6px;
}

p {
  margin-top: 0;
  color: var(--muted);
}

.input-row {
  display: flex;
  gap: 10px;
  margin: 12px 0;
}

.status-row {
  margin-bottom: 8px;
}

.status-tag {
  display: inline-block;
  font-size: 12px;
  border-radius: 999px;
  padding: 4px 10px;
  border: 1px solid transparent;
}

.status-tag.ok {
  background: rgba(38, 115, 77, 0.14);
  color: #1f5c3d;
  border-color: rgba(38, 115, 77, 0.4);
}

.status-tag.warn {
  background: rgba(227, 93, 47, 0.12);
  color: #9a3f1f;
  border-color: rgba(227, 93, 47, 0.4);
}

input {
  flex: 1;
  padding: 10px 12px;
  border: 1px solid var(--panel-border);
  border-radius: 10px;
  outline: none;
}

button {
  border: 0;
  border-radius: 10px;
  background: var(--ink);
  color: #fff;
  padding: 10px 16px;
  cursor: pointer;
}

.answer {
  margin-top: 14px;
  border-top: 1px dashed var(--panel-border);
  padding-top: 12px;
}

.source {
  color: var(--muted);
}

@keyframes pop {
  from { opacity: 0; transform: scale(0.98); }
  to { opacity: 1; transform: scale(1); }
}

@media (max-width: 700px) {
  .input-row {
    flex-direction: column;
  }
}
</style>
