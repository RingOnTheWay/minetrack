<script setup lang="ts">
import Sidebar from './Sidebar.vue'
import TopBar from './TopBar.vue'
</script>

<template>
  <div class="app-container">
    <Sidebar />
    <div class="main-content">
      <TopBar />
      <div class="content-area">
        <slot />
      </div>
    </div>
  </div>
</template>

<style scoped>
.app-container {
  display: flex;
  min-height: 100vh;
}

.main-content {
  margin-left: var(--sidebar-width);
  flex: 1;
  display: flex;
  flex-direction: column;
}

.content-area {
  flex: 1;
  width: 100%;
  padding: 24px;
  overflow-y: auto;
}
</style>