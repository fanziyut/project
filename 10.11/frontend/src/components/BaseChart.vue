<template>
  <div ref="chartEl" class="chart" :style="{ height }"></div>
</template>

<script setup>
import * as echarts from 'echarts'
import { onBeforeUnmount, onMounted, ref, watch } from 'vue'

const props = defineProps({
  option: { type: Object, default: null },
  height: { type: String, default: '420px' },
})

const chartEl = ref(null)
let chart = null

function render() {
  if (chart && props.option) {
    chart.setOption(props.option, true)
  }
}

function resize() {
  if (chart) chart.resize()
}

onMounted(() => {
  chart = echarts.init(chartEl.value)
  render()
  window.addEventListener('resize', resize)
})

// 数据从后端返回后重新渲染
watch(() => props.option, render, { deep: true })

onBeforeUnmount(() => {
  window.removeEventListener('resize', resize)
  if (chart) chart.dispose()
  chart = null
})
</script>
