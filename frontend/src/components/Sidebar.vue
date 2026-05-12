<script setup lang="ts">
import { useRouter, useRoute } from 'vue-router'
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

const { t, locale } = useI18n()
const router = useRouter()
const route = useRoute()

const navItems = computed(() => [
  { path: '/', icon: 'dashboard', label: t('nav.dashboard') },
  { path: '/map', icon: 'map', label: t('nav.mapStats') },
  { path: '/players', icon: 'people', label: t('nav.playerStats') },
  { path: '/battle', icon: 'swords', label: t('nav.battleStats') },
  { path: '/craft', icon: 'build', label: t('nav.craftStats') },
  { path: '/items', icon: 'inventory_2', label: t('nav.itemStats') },
  { path: '/activity', icon: 'timeline', label: t('nav.activity') },
])

const currentPath = computed(() => route.path)

function navigate(path: string) {
  router.push(path)
}

function toggleLocale() {
  locale.value = locale.value === 'zh-CN' ? 'en-US' : 'zh-CN'
}
</script>

<template>
  <aside class="sidebar">
    <div class="sidebar-header">
      <span class="material-symbols-outlined" style="font-size:32px;color:var(--md-sys-color-primary)">analytics</span>
      <h1>{{ t('app.title') }}</h1>
    </div>
    <nav class="sidebar-nav">
      <button
        v-for="item in navItems"
        :key="item.path"
        class="nav-item"
        :class="{ active: currentPath === item.path }"
        @click="navigate(item.path)"
      >
        <span class="material-symbols-outlined">{{ item.icon }}</span>
        <span>{{ item.label }}</span>
      </button>
    </nav>
    <div class="sidebar-footer">
      <button class="lang-btn" @click="toggleLocale">
        <span class="material-symbols-outlined">translate</span>
        <span>{{ t('lang.switchTo') }}</span>
      </button>
    </div>
  </aside>
</template>

<style scoped>
.sidebar {
  width: var(--sidebar-width);
  background: var(--md-sys-color-surface-container-low);
  border-right: 1px solid var(--md-sys-color-outline-variant);
  position: fixed;
  left: 0;
  top: 0;
  bottom: 0;
  display: flex;
  flex-direction: column;
  z-index: 100;
}

.sidebar-header {
  padding: 20px 24px;
  display: flex;
  align-items: center;
  gap: 12px;
  border-bottom: 1px solid var(--md-sys-color-outline-variant);
}

.sidebar-header h1 {
  font-size: 20px;
  font-weight: 500;
  color: var(--md-sys-color-on-surface);
}

.sidebar-nav {
  flex: 1;
  padding: 12px 0;
  overflow-y: auto;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 24px;
  margin: 4px 12px;
  border-radius: 24px;
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  color: var(--md-sys-color-on-surface);
  font-size: 14px;
  font-weight: 500;
  width: calc(100% - 24px);
  text-align: left;
}

.nav-item:hover {
  background: var(--md-sys-color-surface-container-highest);
}

.nav-item.active {
  background: var(--md-sys-color-secondary-container);
  color: var(--md-sys-color-on-secondary-container);
}

.nav-item .material-symbols-outlined {
  font-size: 24px;
}

.sidebar-footer {
  padding: 12px 16px;
  border-top: 1px solid var(--md-sys-color-outline-variant);
}

.lang-btn {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 16px;
  width: 100%;
  border-radius: 24px;
  font-size: 14px;
  font-weight: 500;
  color: var(--md-sys-color-on-surface-variant);
  transition: background 0.2s;
  cursor: pointer;
}

.lang-btn:hover {
  background: var(--md-sys-color-surface-container-highest);
}

.lang-btn .material-symbols-outlined {
  font-size: 20px;
}
</style>
