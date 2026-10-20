<template>
  <div class="container">
    <div v-if="loading" class="status">数据加载中...</div>
    <div v-else-if="error" class="status error">{{ error }}</div>

    <template v-else>
      <!-- 概览卡片 -->
      <div class="overview-cards">
        <div v-for="item in cards" :key="item.label" class="card">
          <div class="card-icon">{{ item.icon }}</div>
          <div class="card-value">{{ item.value.toLocaleString() }}</div>
          <div class="card-label">{{ item.label }}</div>
        </div>
      </div>

      <!-- 第一行：城市分布 + 行业分布 -->
      <div class="chart-row">
        <div class="chart-box">
          <h3>招聘岗位城市分布 Top15</h3>
          <BaseChart :option="cityOption" />
        </div>
        <div class="chart-box">
          <h3>招聘岗位行业分布 Top15</h3>
          <BaseChart :option="industryOption" />
        </div>
      </div>

      <!-- 第二行：薪资区间 + 各城市平均薪资 -->
      <div class="chart-row">
        <div class="chart-box">
          <h3>薪资区间分布</h3>
          <BaseChart :option="salaryRangeOption" />
        </div>
        <div class="chart-box">
          <h3>各城市平均薪资 Top15 (元)</h3>
          <BaseChart :option="citySalaryOption" />
        </div>
      </div>

      <!-- 第三行：公司规模 + 公司类型 -->
      <div class="chart-row">
        <div class="chart-box">
          <h3>公司规模分布</h3>
          <BaseChart :option="companySizeOption" height="350px" />
        </div>
        <div class="chart-box">
          <h3>公司类型分布</h3>
          <BaseChart :option="companyTypeOption" height="350px" />
        </div>
      </div>

      <!-- 第四行：岗位关键词 + 岗位词频 -->
      <div class="chart-row">
        <div class="chart-box">
          <h3>岗位关键词热度</h3>
          <BaseChart :option="keywordOption" />
        </div>
        <div class="chart-box">
          <h3>岗位名称词频 Top20</h3>
          <BaseChart :option="titleWordOption" />
        </div>
      </div>

      <!-- 第五行：城市薪资交叉 + 高薪比例 -->
      <div class="chart-row">
        <div class="chart-box">
          <h3>热门城市薪资区间分布</h3>
          <BaseChart :option="citySalaryRangeOption" />
        </div>
        <div class="chart-box">
          <h3>各城市高薪岗位比例(≥2万) Top10</h3>
          <BaseChart :option="cityHighSalaryOption" />
        </div>
      </div>

      <!-- 分析结论 -->
      <div class="insight-box">
        <h3>数据分析结论</h3>
        <p><strong>一、岗位分布概况</strong></p>
        <p>
          本次分析共 {{ overview.totalJobs }} 条招聘信息，覆盖 {{ overview.cityCountTotal }} 个城市。
          岗位主要集中在广州、深圳、上海等一线城市，体现了互联网及科技行业对数据分析人才的集中需求。
        </p>
        <p><strong>二、薪资水平分析</strong></p>
        <p>
          在 {{ overview.validSalaryCount }} 条含薪资的岗位中，"5-8千"区间岗位最多，"8千-1.2万"和"1.2-2万"
          区间次之，全量岗位平均薪资约 {{ overview.avgSalary }} 元。高薪岗位(≥2万)主要集中在深圳、上海、北京等城市。
        </p>
        <p><strong>三、行业与企业类型</strong></p>
        <p>
          招聘行业以互联网/电子商务为首，民营企业占据招聘市场主导地位，其次为上市公司和合资企业。
          公司规模方面，"50-150人"和"150-500人"的中小企业是招聘主力军。
        </p>
        <p><strong>四、岗位技能需求</strong></p>
        <p>
          岗位名称中"运营""数据""分析"出现频率最高，反映出企业对数据分析与运营能力的强烈需求。
          大数据、人工智能、机器学习等新兴技术关键词也进入前列，体现技术驱动趋势。
        </p>
      </div>
    </template>
  </div>
</template>

<script setup>
import * as echarts from 'echarts'
import { computed, onMounted, ref } from 'vue'

import { getDashboard } from '../api'
import BaseChart from '../components/BaseChart.vue'

const loading = ref(true)
const error = ref('')
const data = ref(null)

const colorPalette = ['#667eea', '#764ba2', '#f093fb', '#4facfe', '#43e97b',
  '#fa709a', '#fee140', '#a18cd1', '#fbc2eb', '#ff9a9e',
  '#fad0c4', '#ffecd2', '#0cbfc6', '#0ed1dc', '#667eea']

onMounted(async () => {
  try {
    data.value = await getDashboard()
  } catch (e) {
    error.value = '数据加载失败，请确认后端服务 (python app.py) 已启动'
  } finally {
    loading.value = false
  }
})

const overview = computed(() => data.value?.overview ?? {
  totalJobs: 0, validSalaryCount: 0, cityCountTotal: 0, industryCountTotal: 0, avgSalary: 0,
})

const cards = computed(() => [
  { icon: '📊', value: overview.value.totalJobs, label: '招聘岗位总数' },
  { icon: '🏙️', value: overview.value.cityCountTotal, label: '覆盖城市数量' },
  { icon: '💰', value: overview.value.validSalaryCount, label: '含薪资岗位数' },
  { icon: '🏢', value: overview.value.industryCountTotal, label: '涉及行业数量' },
])

function gradient(x2, y2, from, to) {
  return new echarts.graphic.LinearGradient(0, 0, x2, y2, [
    { offset: 0, color: from },
    { offset: 1, color: to },
  ])
}

// 1. 城市分布
const cityOption = computed(() => {
  const list = data.value?.cityCount ?? []
  return {
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    grid: { left: '3%', right: '8%', bottom: '3%', top: '8%', containLabel: true },
    xAxis: { type: 'value' },
    yAxis: { type: 'category', data: list.map((d) => d.城市).reverse(), axisLabel: { fontSize: 11 } },
    series: [{
      type: 'bar',
      data: list.map((d) => d.岗位数量).reverse(),
      itemStyle: { color: gradient(1, 0, '#667eea', '#764ba2'), borderRadius: [0, 4, 4, 0] },
      label: { show: true, position: 'right', formatter: '{c}', fontSize: 10 },
    }],
    toolbox: { feature: { saveAsImage: {} } },
  }
})

// 2. 行业分布
const industryOption = computed(() => {
  const list = data.value?.industryCount ?? []
  return {
    tooltip: { trigger: 'item' },
    legend: { orient: 'vertical', right: '5%', top: 'center', fontSize: 10 },
    series: [{
      type: 'pie',
      radius: ['30%', '70%'],
      center: ['38%', '50%'],
      itemStyle: { borderRadius: 6, borderColor: '#fff', borderWidth: 2 },
      label: { show: true, formatter: '{b}: {d}%', fontSize: 10 },
      data: list.map((d) => ({ name: d.行业, value: d.岗位数量 })),
      color: colorPalette,
    }],
    toolbox: { feature: { saveAsImage: {} } },
  }
})

// 3. 薪资区间分布
const salaryRangeOption = computed(() => {
  const list = data.value?.salaryRangeCount ?? []
  return {
    tooltip: { trigger: 'item' },
    legend: { orient: 'horizontal', bottom: '2%', fontSize: 11 },
    series: [{
      type: 'pie',
      radius: '62%',
      center: ['50%', '44%'],
      itemStyle: { borderRadius: 6, borderColor: '#fff', borderWidth: 2 },
      label: { show: true, formatter: '{b}: {d}%', fontSize: 11 },
      data: list.map((d) => ({ name: d.薪资区间, value: d.岗位数量 })),
      color: ['#5470c6', '#91cc75', '#fac858', '#ee6666', '#73c0de', '#3ba272', '#a5a5a5'],
    }],
    toolbox: { feature: { saveAsImage: {} } },
  }
})

// 4. 各城市平均薪资
const citySalaryOption = computed(() => {
  const list = data.value?.citySalaryAvg ?? []
  return {
    tooltip: { trigger: 'axis', formatter: '{b}: {c} 元' },
    grid: { left: '3%', right: '8%', bottom: '3%', top: '8%', containLabel: true },
    xAxis: {
      type: 'category',
      data: list.map((d) => d.城市).reverse(),
      axisLabel: { rotate: 30, fontSize: 11 },
    },
    yAxis: { type: 'value', name: '平均薪资(元)', nameTextStyle: { fontSize: 11 } },
    series: [{
      type: 'bar',
      data: list.map((d) => d.平均薪资).reverse(),
      itemStyle: { color: gradient(0, 1, '#4facfe', '#00f2fe'), borderRadius: [4, 4, 0, 0] },
      label: { show: true, position: 'top', formatter: '{c}', fontSize: 10 },
    }],
    toolbox: { feature: { saveAsImage: {} } },
  }
})

// 5. 公司规模分布
const companySizeOption = computed(() => {
  const list = data.value?.companySizeCount ?? []
  return {
    tooltip: { trigger: 'item' },
    series: [{
      type: 'pie',
      radius: ['30%', '70%'],
      itemStyle: { borderRadius: 6, borderColor: '#fff', borderWidth: 2 },
      label: { show: true, formatter: '{b}: {d}%', fontSize: 11 },
      data: list.map((d) => ({ name: d.公司规模, value: d.岗位数量 })),
      color: colorPalette,
    }],
    toolbox: { feature: { saveAsImage: {} } },
  }
})

// 6. 公司类型分布
const companyTypeOption = computed(() => {
  const list = data.value?.companyTypeCount ?? []
  return {
    tooltip: { trigger: 'item' },
    legend: { orient: 'vertical', right: '5%', top: 'center', fontSize: 10 },
    series: [{
      type: 'pie',
      radius: ['30%', '70%'],
      center: ['38%', '50%'],
      itemStyle: { borderRadius: 6, borderColor: '#fff', borderWidth: 2 },
      label: { show: true, formatter: '{b}: {d}%', fontSize: 10 },
      data: list.map((d) => ({ name: d.公司类型, value: d.岗位数量 })),
      color: ['#5470c6', '#91cc75', '#fac858', '#ee6666', '#73c0de', '#3ba272', '#a5a5a5'],
    }],
    toolbox: { feature: { saveAsImage: {} } },
  }
})

// 7. 岗位关键词热度
const keywordOption = computed(() => {
  const list = data.value?.keywordCount ?? []
  return {
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    grid: { left: '3%', right: '8%', bottom: '3%', top: '8%', containLabel: true },
    xAxis: { type: 'value' },
    yAxis: { type: 'category', data: list.map((d) => d.关键词).reverse(), axisLabel: { fontSize: 11 } },
    series: [{
      type: 'bar',
      data: list.map((d) => d.出现次数).reverse(),
      itemStyle: { color: gradient(1, 0, '#43e97b', '#38f9d7'), borderRadius: [0, 4, 4, 0] },
      label: { show: true, position: 'right', formatter: '{c}', fontSize: 10 },
    }],
    toolbox: { feature: { saveAsImage: {} } },
  }
})

// 8. 岗位名称词频
const titleWordOption = computed(() => {
  const list = data.value?.titleWordCount ?? []
  return {
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    grid: { left: '3%', right: '10%', bottom: '3%', top: '8%', containLabel: true },
    xAxis: { type: 'value' },
    yAxis: { type: 'category', data: list.map((d) => d.岗位词).reverse(), axisLabel: { fontSize: 10 } },
    series: [{
      type: 'bar',
      data: list.map((d) => d.出现次数).reverse(),
      itemStyle: { color: gradient(1, 0, '#fa709a', '#fee140'), borderRadius: [0, 4, 4, 0] },
      label: { show: true, position: 'right', formatter: '{c}', fontSize: 10 },
    }],
    toolbox: { feature: { saveAsImage: {} } },
  }
})

// 9. 城市 × 薪资区间交叉
const citySalaryRangeOption = computed(() => {
  const cross = data.value?.citySalaryRange
  if (!cross) return {}
  return {
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    legend: { top: '2%', fontSize: 10 },
    grid: { left: '3%', right: '3%', bottom: '3%', top: '16%', containLabel: true },
    xAxis: { type: 'category', data: cross.series.map((s) => s.name), axisLabel: { rotate: 30, fontSize: 10 } },
    yAxis: { type: 'value', name: '岗位数' },
    series: cross.series.map((s, idx) => ({
      name: s.name,
      type: 'bar',
      stack: 'total',
      emphasis: { focus: 'series' },
      data: s.data,
      itemStyle: { color: colorPalette[idx % colorPalette.length] },
    })),
    toolbox: { feature: { saveAsImage: {} } },
  }
})

// 10. 各城市高薪岗位比例
const cityHighSalaryOption = computed(() => {
  const list = data.value?.cityHighSalary ?? []
  return {
    tooltip: { trigger: 'axis', formatter: '{b}: {c}%' },
    grid: { left: '3%', right: '8%', bottom: '3%', top: '8%', containLabel: true },
    xAxis: { type: 'category', data: list.map((d) => d.城市).reverse(), axisLabel: { rotate: 30, fontSize: 11 } },
    yAxis: { type: 'value', name: '高薪岗位比例(%)', max: 100 },
    series: [{
      type: 'bar',
      data: list.map((d) => d.高薪岗位比例).reverse(),
      itemStyle: { color: gradient(0, 1, '#a18cd1', '#fbc2eb'), borderRadius: [4, 4, 0, 0] },
      label: { show: true, position: 'top', formatter: '{c}%', fontSize: 10 },
    }],
    toolbox: { feature: { saveAsImage: {} } },
  }
})
</script>
