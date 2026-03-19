<template>
  <div class="dashboard-shell">
    <header class="topbar card">
      <div>
        <h1>警情多维可视分析系统</h1>
        <p>面向基层公安单位的出警数据研判与辅助决策平台</p>
      </div>
      <nav class="nav-links">
        <RouterLink to="/">本地可视化看板</RouterLink>
        <RouterLink to="/local-dashboard">Excel上传分析</RouterLink>
        <RouterLink to="/report">演示报告</RouterLink>
      </nav>
    </header>

    <main>
      <RouterView />
    </main>
  </div>
</template>

<script setup>
import { RouterLink, RouterView } from 'vue-router'
</script>

<style scoped>
.topbar {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  align-items: center;
  margin-bottom: 18px;
}

h1 {
  margin: 0;
  font-size: 28px;
  font-family: 'Space Grotesk', sans-serif;
}

p {
  margin: 4px 0 0;
  color: var(--muted);
}

.nav-links {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.nav-links a {
  padding: 7px 12px;
  border-radius: 12px;
  border: 1px solid var(--panel-border);
  transition: all 0.22s ease;
}

.nav-links a.router-link-exact-active {
  background: var(--ink);
  color: #fff;
  border-color: var(--ink);
}

@media (max-width: 900px) {
  .topbar {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
