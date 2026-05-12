<script setup lang="ts">
import { RouterView } from 'vue-router'
import AppLayout from '@/components/AppLayout.vue'
import { useAppStore } from '@/stores/app'
import { onMounted } from 'vue'

const appStore = useAppStore()

onMounted(() => {
  appStore.initialize()
})
</script>

<template>
  <AppLayout>
    <RouterView />
  </AppLayout>
</template>

<style>
@import '@/assets/main.css';
</style>