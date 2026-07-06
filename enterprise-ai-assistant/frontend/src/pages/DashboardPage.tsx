import React, { useEffect, useMemo, useState } from 'react'
import {
  Area,
  AreaChart,
  CartesianGrid,
  Cell,
  Legend,
  Line,
  LineChart,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import {
  DollarSign,
  RefreshCw,
  ShoppingCart,
  TrendingDown,
  TrendingUp,
  Users,
} from 'lucide-react'
import {
  getCategoryStats,
  getSummary,
  getTrend,
  generateMockData,
} from '../services/dashboard'
import type {
  CategoryStatsResponse,
  DashboardSummary,
  SalesTrendItemV2,
} from '../types'

/**
 * Dashboard 数据分析页
 *
 * P1 升级：
 * 1. 顶部四张统计卡片（总销售额 / 总订单数 / 总客户数 / 销售增长率）
 * 2. 中部四张 Recharts 图表：销售额趋势（Area）/ 订单趋势（Line）/ 用户增长（Line）/ 产品分类占比（Pie）
 * 3. 顶部支持 7/30/90 天切换
 * 4. 保留"生成模拟数据"按钮
 */
const DashboardPage: React.FC = () => {
  // 汇总数据
  const [summary, setSummary] = useState<DashboardSummary | null>(null)
  // 趋势数据（按天）
  const [trend, setTrend] = useState<SalesTrendItemV2[]>([])
  // 产品分类统计
  const [categoryStats, setCategoryStats] = useState<CategoryStatsResponse | null>(null)
  // 加载状态
  const [loading, setLoading] = useState(true)
  // 模拟数据生成状态
  const [generating, setGenerating] = useState(false)
  // 时间窗口（7/30/90 天）
  const [days, setDays] = useState(30)

  /**
   * 并行拉取汇总、趋势、分类数据
   * 任何一个失败都不影响其他数据展示
   */
  const fetchData = async (windowDays: number) => {
    setLoading(true)
    try {
      const [summaryRes, trendRes, categoryRes] = await Promise.all([
        getSummary(),
        getTrend(windowDays),
        getCategoryStats(),
      ])
      setSummary(summaryRes)
      setTrend(trendRes || [])
      setCategoryStats(categoryRes)
    } catch (error) {
      console.error('获取 Dashboard 数据失败:', error)
    } finally {
      setLoading(false)
    }
  }

  // days 切换时重新拉取
  useEffect(() => {
    fetchData(days)
  }, [days])

  /**
   * 生成模拟数据按钮
   * 重新生成 90 天数据后再拉取一次，让图表立刻反映新数据
   */
  const handleGenerateMockData = async () => {
    setGenerating(true)
    try {
      await generateMockData(90)
      await fetchData(days)
    } catch (error) {
      console.error('生成模拟数据失败:', error)
    } finally {
      setGenerating(false)
    }
  }

  // 数字格式化：>= 1万 时显示 X.XX 万
  const formatNumber = (num: number) => {
    if (num >= 10000) {
      return (num / 10000).toFixed(2) + '万'
    }
    return num.toLocaleString()
  }

  // 货币格式化
  const formatCurrency = (num: number) => {
    return '¥' + formatNumber(num)
  }

  /**
   * 计算销售增长率
   * 趋势数据前半段 vs 后半段的平均值对比
   */
  const growthRate = useMemo(() => {
    if (!trend || trend.length < 2) return 0
    const mid = Math.floor(trend.length / 2)
    if (mid === 0) return 0
    const firstHalf = trend.slice(0, mid)
    const secondHalf = trend.slice(mid)
    const firstAvg =
      firstHalf.reduce((sum, item) => sum + item.revenue, 0) / firstHalf.length
    const secondAvg =
      secondHalf.reduce((sum, item) => sum + item.revenue, 0) / secondHalf.length
    if (firstAvg === 0) return 0
    return ((secondAvg - firstAvg) / firstAvg) * 100
  }, [trend])

  /**
   * 趋势图数据：把 date 截短为月-日，方便 X 轴展示
   */
  const trendChartData = useMemo(
    () =>
      trend.map((item) => ({
        ...item,
        // 后端返回 YYYY-MM-DD，前端只显示 MM-DD
        displayDate: item.date ? item.date.slice(5) : '',
      })),
    [trend]
  )

  /**
   * 饼图数据：使用 product_category 聚合结果
   * 配色：固定 6 色的循环数组
   */
  const PIE_COLORS = ['#3b82f6', '#10b981', '#8b5cf6', '#f59e0b', '#ef4444', '#06b6d4']
  const pieData = useMemo(() => {
    if (!categoryStats || !categoryStats.items) return []
    return categoryStats.items.map((item) => ({
      name: item.category,
      value: item.revenue,
    }))
  }, [categoryStats])

  // 顶部四个统计卡片的配置
  const statCards = [
    {
      title: '总销售额',
      value: formatCurrency(summary?.total_revenue || 0),
      icon: DollarSign,
      color: 'bg-blue-500',
      bgColor: 'bg-blue-50',
      textColor: 'text-blue-600',
    },
    {
      title: '总订单数',
      value: formatNumber(summary?.total_orders || 0),
      icon: ShoppingCart,
      color: 'bg-green-500',
      bgColor: 'bg-green-50',
      textColor: 'text-green-600',
    },
    {
      title: '总客户数',
      value: formatNumber(summary?.total_customers || 0),
      icon: Users,
      color: 'bg-purple-500',
      bgColor: 'bg-purple-50',
      textColor: 'text-purple-600',
    },
    {
      title: '销售增长率',
      value: growthRate.toFixed(2) + '%',
      icon: growthRate >= 0 ? TrendingUp : TrendingDown,
      color: growthRate >= 0 ? 'bg-emerald-500' : 'bg-red-500',
      bgColor: growthRate >= 0 ? 'bg-emerald-50' : 'bg-red-50',
      textColor: growthRate >= 0 ? 'text-emerald-600' : 'text-red-600',
    },
  ]

  // 加载态
  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-lg text-gray-600">加载中...</div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* 页面标题 + 日期下拉 + 生成模拟数据按钮 */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">数据看板</h1>
          <p className="mt-1 text-sm text-gray-500">企业销售数据概览与趋势分析</p>
        </div>
        <div className="flex items-center gap-3">
          <select
            value={days}
            onChange={(e) => setDays(Number(e.target.value))}
            className="px-4 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none"
          >
            <option value={7}>最近 7 天</option>
            <option value={30}>最近 30 天</option>
            <option value={90}>最近 90 天</option>
          </select>
          <button
            onClick={handleGenerateMockData}
            disabled={generating}
            className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 transition-colors text-sm"
          >
            <RefreshCw className={`w-4 h-4 ${generating ? 'animate-spin' : ''}`} />
            {generating ? '生成中...' : '生成模拟数据'}
          </button>
        </div>
      </div>

      {/* 顶部四个统计卡片 */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {statCards.map((card, index) => {
          const Icon = card.icon
          return (
            <div
              key={index}
              className="bg-white rounded-xl p-6 shadow-sm border border-gray-100"
            >
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-500">{card.title}</p>
                  <p className="mt-2 text-2xl font-bold text-gray-900">
                    {card.value}
                  </p>
                </div>
                <div className={`p-3 rounded-xl ${card.bgColor}`}>
                  <Icon className={`w-6 h-6 ${card.textColor}`} />
                </div>
              </div>
            </div>
          )
        })}
      </div>

      {/* 图表区：四张图，2x2 排版 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* 1. 销售额趋势：AreaChart，蓝色 */}
        <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">销售额趋势</h3>
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={trendChartData}>
                <defs>
                  <linearGradient id="colorRevenue" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                <XAxis
                  dataKey="displayDate"
                  tick={{ fontSize: 12 }}
                  stroke="#9ca3af"
                />
                <YAxis
                  tick={{ fontSize: 12 }}
                  stroke="#9ca3af"
                  tickFormatter={(value) => Number(value) / 1000 + 'k'}
                />
                <Tooltip
                  formatter={(value: number) => [
                    '¥' + Number(value).toLocaleString(),
                    '销售额',
                  ]}
                  contentStyle={{
                    borderRadius: '8px',
                    border: '1px solid #e5e7eb',
                    boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
                  }}
                />
                <Area
                  type="monotone"
                  dataKey="revenue"
                  stroke="#3b82f6"
                  strokeWidth={2}
                  fillOpacity={1}
                  fill="url(#colorRevenue)"
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* 2. 订单趋势：LineChart，绿色 monotone */}
        <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">订单趋势</h3>
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={trendChartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                <XAxis
                  dataKey="displayDate"
                  tick={{ fontSize: 12 }}
                  stroke="#9ca3af"
                />
                <YAxis tick={{ fontSize: 12 }} stroke="#9ca3af" />
                <Tooltip
                  formatter={(value: number) => [value.toLocaleString(), '订单数']}
                  contentStyle={{
                    borderRadius: '8px',
                    border: '1px solid #e5e7eb',
                    boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
                  }}
                />
                <Line
                  type="monotone"
                  dataKey="orders"
                  name="订单数"
                  stroke="#10b981"
                  strokeWidth={2}
                  dot={false}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* 3. 用户增长趋势：LineChart，紫色 monotone */}
        <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">用户增长趋势</h3>
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={trendChartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                <XAxis
                  dataKey="displayDate"
                  tick={{ fontSize: 12 }}
                  stroke="#9ca3af"
                />
                <YAxis tick={{ fontSize: 12 }} stroke="#9ca3af" />
                <Tooltip
                  formatter={(value: number) => [value.toLocaleString(), '客户数']}
                  contentStyle={{
                    borderRadius: '8px',
                    border: '1px solid #e5e7eb',
                    boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
                  }}
                />
                <Line
                  type="monotone"
                  dataKey="customers"
                  name="客户数"
                  stroke="#8b5cf6"
                  strokeWidth={2}
                  dot={false}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* 4. 产品分类占比：PieChart，多色扇形 + Tooltip 显示百分比 */}
        <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">产品分类占比</h3>
          <div className="h-80">
            {pieData.length === 0 ? (
              <div className="h-full flex items-center justify-center text-gray-400 text-sm">
                暂无产品分类数据，请先生成模拟数据
              </div>
            ) : (
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={pieData}
                    dataKey="value"
                    nameKey="name"
                    cx="50%"
                    cy="50%"
                    outerRadius={100}
                    label={(entry) => `${entry.name}`}
                  >
                    {pieData.map((_, index) => (
                      <Cell
                        key={`cell-${index}`}
                        fill={PIE_COLORS[index % PIE_COLORS.length]}
                      />
                    ))}
                  </Pie>
                  <Tooltip
                    formatter={(value: number, name: string) => {
                      const total = pieData.reduce(
                        (sum, item) => sum + item.value,
                        0
                      )
                      const pct =
                        total > 0
                          ? ((value / total) * 100).toFixed(2) + '%'
                          : '0%'
                      return [`¥${Number(value).toLocaleString()} (${pct})`, name]
                    }}
                    contentStyle={{
                      borderRadius: '8px',
                      border: '1px solid #e5e7eb',
                      boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
                    }}
                  />
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

export default DashboardPage
