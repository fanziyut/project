<template>
  <div class="container">
    <!-- 筛选条件 -->
    <div class="filter-bar">
      <input v-model="query.keyword" placeholder="搜索岗位名称 / 公司名称" @keyup.enter="search" />
      <select v-model="query.city" @change="search">
        <option value="">全部城市</option>
        <option v-for="c in filters.cities" :key="c" :value="c">{{ c }}</option>
      </select>
      <select v-model="query.industry" @change="search">
        <option value="">全部行业</option>
        <option v-for="i in filters.industries" :key="i" :value="i">{{ i }}</option>
      </select>
      <select v-model="query.salary_range" @change="search">
        <option value="">全部薪资区间</option>
        <option v-for="s in filters.salaryRanges" :key="s" :value="s">{{ s }}</option>
      </select>
      <select v-model="query.company_size" @change="search">
        <option value="">全部公司规模</option>
        <option v-for="s in filters.companySizes" :key="s" :value="s">{{ s }}</option>
      </select>
      <select v-model="query.company_type" @change="search">
        <option value="">全部公司类型</option>
        <option v-for="t in filters.companyTypes" :key="t" :value="t">{{ t }}</option>
      </select>
      <select v-model="query.sort" @change="search">
        <option value="default">默认排序</option>
        <option value="salary_desc">薪资从高到低</option>
        <option value="salary_asc">薪资从低到高</option>
      </select>
      <button class="btn" @click="search">查询</button>
      <button class="btn ghost" @click="reset">重置</button>
    </div>

    <!-- 列表 -->
    <div class="table-box">
      <div v-if="loading" class="status">加载中...</div>
      <template v-else>
        <p style="font-size: 13px; color: #888; padding: 12px 10px 0">
          共 {{ result.total.toLocaleString() }} 条岗位，第 {{ result.page }} / {{ result.pages || 1 }} 页
        </p>
        <table>
          <thead>
            <tr>
              <th>岗位名称</th>
              <th>公司名称</th>
              <th>城市</th>
              <th>薪资</th>
              <th>薪资区间</th>
              <th>公司类型</th>
              <th>公司规模</th>
              <th>行业</th>
              <th>发布日期</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="job in result.items" :key="job.id" @click="openDetail(job.id)">
              <td>{{ job.title }}</td>
              <td>{{ job.company || '-' }}</td>
              <td>{{ job.city }}</td>
              <td>{{ job.salary || '面议' }}</td>
              <td><span class="tag">{{ job.salaryRange }}</span></td>
              <td>{{ job.companyType || '-' }}</td>
              <td>{{ job.companySize || '-' }}</td>
              <td>{{ job.industry || '-' }}</td>
              <td>{{ job.publishDate || '-' }}</td>
            </tr>
            <tr v-if="!result.items.length">
              <td colspan="9" style="text-align: center; color: #999; padding: 40px 0">
                没有符合条件的岗位
              </td>
            </tr>
          </tbody>
        </table>

        <div class="pagination">
          <button :disabled="result.page <= 1" @click="go(result.page - 1)">上一页</button>
          <span>{{ result.page }} / {{ result.pages || 1 }}</span>
          <button :disabled="result.page >= result.pages" @click="go(result.page + 1)">下一页</button>
          <select v-model.number="query.page_size" @change="search" style="padding: 6px 10px; border: 1px solid #dcdfe6; border-radius: 6px">
            <option :value="10">10 条/页</option>
            <option :value="20">20 条/页</option>
            <option :value="50">50 条/页</option>
          </select>
        </div>
      </template>
    </div>

    <!-- 详情弹窗 -->
    <div v-if="detail" class="modal-mask" @click.self="detail = null">
      <div class="modal">
        <h3>{{ detail.title }}</h3>
        <p class="modal-sub">{{ detail.company || '未知公司' }} · {{ detail.city }} · {{ detail.salary || '面议' }}</p>

        <div class="detail-grid">
          <div class="detail-item">
            <div class="label">薪资区间</div>
            <div class="value">{{ detail.salaryRange }}</div>
          </div>
          <div class="detail-item">
            <div class="label">平均薪资</div>
            <div class="value">{{ salaryText(detail) }}</div>
          </div>
          <div class="detail-item">
            <div class="label">公司类型</div>
            <div class="value">{{ detail.companyType || '-' }}</div>
          </div>
          <div class="detail-item">
            <div class="label">公司规模</div>
            <div class="value">{{ detail.companySize || '-' }}</div>
          </div>
          <div class="detail-item">
            <div class="label">所属行业</div>
            <div class="value">{{ detail.industry || '-' }}</div>
          </div>
          <div class="detail-item">
            <div class="label">发布日期</div>
            <div class="value">{{ detail.publishDate || '-' }}</div>
          </div>
        </div>

        <div v-if="detail.detail" class="detail-block">
          <div class="label">岗位详情</div>
          <div class="content">{{ detail.detail }}</div>
        </div>
        <div v-if="detail.description" class="detail-block">
          <div class="label">岗位描述</div>
          <div class="content">{{ detail.description }}</div>
        </div>

        <div class="modal-actions">
          <button class="btn ghost" @click="detail = null">关闭</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'

import { getFilters, getJobDetail, getJobs } from '../api'

const filters = ref({ cities: [], industries: [], companyTypes: [], companySizes: [], salaryRanges: [] })
const result = ref({ total: 0, page: 1, pages: 1, pageSize: 20, items: [] })
const loading = ref(false)
const detail = ref(null)

const query = reactive({
  page: 1,
  page_size: 20,
  city: '',
  industry: '',
  company_type: '',
  company_size: '',
  salary_range: '',
  keyword: '',
  sort: 'default',
})

async function load() {
  loading.value = true
  try {
    result.value = await getJobs({ ...query })
  } finally {
    loading.value = false
  }
}

function search() {
  query.page = 1
  load()
}

function reset() {
  Object.assign(query, {
    page: 1, page_size: 20, city: '', industry: '',
    company_type: '', company_size: '', salary_range: '', keyword: '', sort: 'default',
  })
  load()
}

function go(page) {
  if (page < 1 || page > (result.value.pages || 1)) return
  query.page = page
  load()
}

function salaryText(job) {
  return job.salaryAvg ? `约 ${Math.round(job.salaryAvg).toLocaleString()} 元/月` : '薪资未知'
}

async function openDetail(id) {
  detail.value = await getJobDetail(id)
}

onMounted(async () => {
  filters.value = await getFilters()
  await load()
})
</script>
