<script setup lang="ts">
import { useRoute } from 'vue-router'
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()
const route = useRoute()

const breadcrumbMap: Record<string, string> = {
  '/': 'nav.dashboard',
  '/map': 'nav.mapStats',
  '/players': 'nav.playerStats',
  '/battle': 'nav.battleStats',
  '/craft': 'nav.craftStats',
  '/items': 'nav.itemStats',
  '/activity': 'nav.activity',
}

const currentLabel = computed(() => t(breadcrumbMap[route.path] || 'nav.dashboard'))
</script>

<template>
  <header class="top-bar">
    <div class="breadcrumb">
      <span class="breadcrumb-current">{{ currentLabel }}</span>
    </div>
  </header>
</template>

<style scoped>
.top-bar {
  height: var(--topbar-height);
  background: var(--md-sys-color-surface);
  border-bottom: 1px solid var(--md-sys-color-outline-variant);
  display: flex;
  align-items: center;
  padding: 0 24px;
  position: sticky;
  top: 0;
  z-index: 50;
}

.breadcrumb {
  display: flex;
  align-items: center;
  gap: 8px;
  color: var(--md-sys-color-on-surface-variant);
  font-size: 14px;
}

.breadcrumb-current {
  color: var(--md-sys-color-on-surface);
  font-weight: 500;
  font-size: 18px;
}
</style>