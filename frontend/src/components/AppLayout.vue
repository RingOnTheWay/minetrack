<script setup lang="ts">
import Sidebar from './Sidebar.vue'
import TopBar from './TopBar.vue'
import { useDataStore } from '@/stores/data'
import { ref, provide } from 'vue'
import { onMounted } from 'vue'

const data = useDataStore()
const sidebarOpen = ref(false)

function toggleSidebar() {
  sidebarOpen.value = !sidebarOpen.value
}

function closeSidebar() {
  sidebarOpen.value = false
}

provide('sidebarOpen', sidebarOpen)
provide('toggleSidebar', toggleSidebar)
provide('closeSidebar', closeSidebar)

onMounted(() => {
  data.loadAll()
})
</script>

<template>
  <div class="flex h-screen overflow-hidden app-layout-outer">
    <Sidebar :open="sidebarOpen" @close="closeSidebar" />
    <div class="flex-1 flex flex-col overflow-hidden app-layout-inner min-w-0">
      <TopBar />
      <div class="flex-1 overflow-y-auto p-4 md:p-8 space-y-6">
        <slot />
      </div>
    </div>

    <Transition name="loading-fade">
      <div v-if="data.loading" class="global-loading-overlay">
        <div class="global-loading-card">
          <div class="text-sm text-slate-500 dark:text-slate-400 mb-4">{{ data.loadingMessage }}</div>
          <div class="w-48 h-1.5 bg-slate-100 dark:bg-slate-700 rounded-full overflow-hidden">
            <div class="h-full rounded-full loading-progress" />
          </div>
        </div>
      </div>
    </Transition>
  </div>
</template>

<style scoped>
.loading-progress {
  background: linear-gradient(to right, var(--brand), var(--brand-light));
  animation: loading-slide 1.5s ease-in-out infinite;
}

.loading-fade-enter-active {
  transition: opacity 0.3s ease;
}
.loading-fade-leave-active {
  transition: opacity 0.5s ease;
}
.loading-fade-enter-from,
.loading-fade-leave-to {
  opacity: 0;
}

@keyframes loading-slide {
  0% {
    width: 0%;
    margin-left: 0%;
  }
  50% {
    width: 60%;
    margin-left: 20%;
  }
  100% {
    width: 0%;
    margin-left: 100%;
  }
}
</style>
