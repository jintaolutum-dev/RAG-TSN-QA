<template>
  <!-- Admin dashboard - statistics overview -->
  <div class="home-container">
    <!-- Stat cards area -->
    <el-row :gutter="20" class="stat-cards">
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-content">
            <div class="stat-info">
              <span class="stat-label">Total Users</span>
              <span class="stat-value">{{ stats.user_count }}</span>
            </div>
            <el-icon class="stat-icon" :size="48" color="#409eff"><User /></el-icon>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-content">
            <div class="stat-info">
              <span class="stat-label">Number of Knowledge Bases</span>
              <span class="stat-value">{{ stats.kb_count }}</span>
            </div>
            <el-icon class="stat-icon" :size="48" color="#67c23a"><FolderOpened /></el-icon>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-content">
            <div class="stat-info">
              <span class="stat-label">Total Documents</span>
              <span class="stat-value">{{ stats.doc_count }}</span>
            </div>
            <el-icon class="stat-icon" :size="48" color="#e6a23c"><Document /></el-icon>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-content">
            <div class="stat-info">
              <span class="stat-label">Questions Today</span>
              <span class="stat-value">{{ stats.today_chat_count }}</span>
            </div>
            <el-icon class="stat-icon" :size="48" color="#f56c6c"><ChatDotRound /></el-icon>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Charts area -->
    <el-row :gutter="20" class="chart-row">
      <el-col :span="14">
        <el-card shadow="hover">
          <template #header>
            <span class="card-title">Question Trend (Last 7 Days)</span>
          </template>
          <div ref="trendChartRef" class="chart-box"></div>
        </el-card>
      </el-col>
      <el-col :span="10">
        <el-card shadow="hover">
          <template #header>
            <span class="card-title">Knowledge Base Document Distribution</span>
          </template>
          <div ref="pieChartRef" class="chart-box"></div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
/**
 * Admin dashboard
 * Shows stat cards and ECharts charts (question trend line + KB doc ratio pie)
 */
import { ref, reactive, onMounted, onBeforeUnmount } from 'vue'
import * as echarts from 'echarts'
import { getOverview } from '../api/stats'

/** Statistics data */
const stats = reactive({
  user_count: 0,
  kb_count: 0,
  doc_count: 0,
  today_chat_count: 0,
  trend_data: [],
  kb_doc_data: []
})

/** Chart DOM refs */
const trendChartRef = ref(null)
const pieChartRef = ref(null)
let trendChart = null
let pieChart = null

/** Load statistics */
async function loadStats() {
  try {
    const res = await getOverview()
    Object.assign(stats, res.data)
    renderTrendChart()
    renderPieChart()
  } catch (err) {
    // Errors are handled by interceptor
  }
}

/** Render 7-day question trend line chart */
function renderTrendChart() {
  if (!trendChartRef.value) return
  trendChart = echarts.init(trendChartRef.value)

  const dates = stats.trend_data.map(item => item.date)
  const counts = stats.trend_data.map(item => item.count)

  trendChart.setOption({
    tooltip: { trigger: 'axis' },
    grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
    xAxis: {
      type: 'category',
      data: dates,
      boundaryGap: false
    },
    yAxis: {
      type: 'value',
      minInterval: 1
    },
    series: [{
      name: 'Questions',
      type: 'line',
      smooth: true,
      data: counts,
      areaStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: 'rgba(64, 158, 255, 0.3)' },
          { offset: 1, color: 'rgba(64, 158, 255, 0.05)' }
        ])
      },
      lineStyle: { color: '#409eff', width: 2 },
      itemStyle: { color: '#409eff' }
    }]
  })
}

/** Render KB document ratio pie chart */
function renderPieChart() {
  if (!pieChartRef.value) return
  pieChart = echarts.init(pieChartRef.value)

  const data = stats.kb_doc_data.length > 0
    ? stats.kb_doc_data
    : [{ name: 'No data', value: 1 }]

  pieChart.setOption({
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {c} ({d}%)'
    },
    legend: {
      orient: 'vertical',
      right: '5%',
      top: 'center'
    },
    series: [{
      type: 'pie',
      radius: ['40%', '70%'],
      center: ['40%', '50%'],
      avoidLabelOverlap: false,
      label: { show: false },
      emphasis: {
        label: { show: true, fontSize: 14, fontWeight: 'bold' }
      },
      data: data
    }]
  })
}

/** Redraw charts on window resize */
function handleResize() {
  trendChart?.resize()
  pieChart?.resize()
}

onMounted(() => {
  loadStats()
  window.addEventListener('resize', handleResize)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)
  trendChart?.dispose()
  pieChart?.dispose()
})
</script>

<style scoped>
.home-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.stat-card {
  border-radius: 8px;
}

.stat-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.stat-info {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.stat-label {
  font-size: 14px;
  color: #909399;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: #303133;
}

.stat-icon {
  opacity: 0.8;
}

.card-title {
  font-weight: 600;
  font-size: 15px;
  color: #303133;
}

.chart-box {
  width: 100%;
  height: 320px;
}
</style>

