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

const DashboardPage: React.FC = () => {
  const [summary, setSummary] = useState<DashboardSummary | null>(null)
  const [trend, setTrend] = useState<SalesTrendItemV2[]>([])
  const [categoryStats, setCategoryStats] = useState<CategoryStatsResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [generating, setGenerating] = useState(false)
  const [days, setDays] = useState(30)

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

  useEffect(() => {
    fetchData(days)
  }, [days])

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

  const formatNumber = (num: number) => {
    if (num >= 10000) {
      return (num / 10000).toFixed(2) + '万'
    }
    return num.toLocaleString()
  }

  const formatCurrency = (num: number) => {
    return '¥' + formatNumber(num)
  }

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

  const trendChartData = useMemo(
    () =>
      trend.map((item) => ({
        ...item,
        displayDate: item.date ? item.date.slice(5) : '',
      })),
    [trend]
  )

  const PIE_COLORS = ['#6366f1', '#06b6d4', '#8b5cf6', '#f59e0b', '#10b981', '#ec4899']
  const pieData = useMemo(() => {
    if (!categoryStats || !categoryStats.items) return []
    return categoryStats.items.map((item) => ({
      name: item.category,
      value: item.revenue,
    }))
  }, [categoryStats])

  const statCards = [
    {
      title: '总销售额',
      value: formatCurrency(summary?.total_revenue || 0),
      icon: DollarSign,
      gradient: 'from-primary-500 to-primary-600',
      lightColor: 'bg-primary-500/10',
      textColor: 'text-primary-400',
    },
    {
      title: '总订单数',
      value: formatNumber(summary?.total_orders || 0),
      icon: ShoppingCart,
      gradient: 'from-accent-500 to-accent-600',
      lightColor: 'bg-accent-500/10',
      textColor: 'text-accent-400',
    },
    {
      title: '总客户数',
      value: formatNumber(summary?.total_customers || 0),
      icon: Users,
      gradient: 'from-purple-500 to-purple-600',
      lightColor: 'bg-purple-500/10',
      textColor: 'text-purple-400',
    },
    {
      title: '销售增长率',
      value: growthRate.toFixed(2) + '%',
      icon: growthRate >= 0 ? TrendingUp : TrendingDown,
      gradient: growthRate >= 0 ? 'from-emerald-500 to-emerald-600' : 'from-red-500 to-red-600',
      lightColor: growthRate >= 0 ? 'bg-emerald-500/10' : 'bg-red-500/10',
      textColor: growthRate >= 0 ? 'text-emerald-400' : 'text-red-400',
    },
  ]

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <RefreshCw className="w-8 h-8 text-primary-500 animate-spin mx-auto mb-3" />
          <p className="text-dark-300">加载中...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-dark-100">数据看板</h1>
          <p className="mt-1 text-sm text-dark-400">
            企业销售数据概览与趋势分析
            {summary?.last_updated && (
              <span className="ml-2 text-dark-500">
                数据更新至 {summary.last_updated}
              </span>
            )}
          </p>
        </div>
        <div className="flex items-center gap-3">
          <select
            value={days}
            onChange={(e) => setDays(Number(e.target.value))}
            className="px-4 py-2 bg-dark-700/60 border border-dark-600/50 rounded-xl text-sm text-dark-200 focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500/20 transition-all"
          >
            <option value={7}>最近 7 天</option>
            <option value={30}>最近 30 天</option>
            <option value={90}>最近 90 天</option>
          </select>
          <button
            onClick={handleGenerateMockData}
            disabled={generating}
            className="flex items-center gap-2 px-4 py-2 gradient-primary text-white rounded-xl hover:opacity-90 disabled:opacity-50 transition-all text-sm shadow-glow"
          >
            <RefreshCw className={`w-4 h-4 ${generating ? 'animate-spin' : ''}`} />
            {generating ? '生成中...' : '生成模拟数据'}
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {statCards.map((card, index) => {
          const Icon = card.icon
          return (
            <div
              key={index}
              className="glass-card p-6 hover:shadow-lg transition-all duration-300 group hover:-translate-y-1"
            >
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-dark-400 mb-2">{card.title}</p>
                  <p className="text-2xl font-bold text-dark-100">
                    {card.value}
                  </p>
                </div>
                <div className={`p-3 rounded-xl ${card.lightColor}`}>
                  <Icon className={`w-6 h-6 ${card.textColor}`} />
                </div>
              </div>
              <div className={`mt-4 h-1 w-full bg-dark-600/50 rounded-full overflow-hidden`}>
                <div 
                  className={`h-full bg-gradient-to-r ${card.gradient} rounded-full transition-all duration-1000`}
                  style={{ width: '75%' }}
                />
              </div>
            </div>
          )
        })}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="glass-card p-6">
          <h3 className="text-lg font-semibold text-dark-100 mb-4 flex items-center gap-2">
            <span className="w-2 h-2 bg-primary-500 rounded-full" />
            销售额趋势
          </h3>
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={trendChartData}>
                <defs>
                  <linearGradient id="colorRevenue" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#6366f1" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#6366f1" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                <XAxis
                  dataKey="displayDate"
                  tick={{ fontSize: 12, fill: '#64748b' }}
                  stroke="#475569"
                />
                <YAxis
                  tick={{ fontSize: 12, fill: '#64748b' }}
                  stroke="#475569"
                  tickFormatter={(value) => Number(value) / 1000 + 'k'}
                />
                <Tooltip
                  formatter={(value: number) => [
                    '¥' + Number(value).toLocaleString(),
                    '销售额',
                  ]}
                  contentStyle={{
                    borderRadius: '8px',
                    border: '1px solid #334155',
                    backgroundColor: '#1e293b',
                    boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.3)',
                  }}
                />
                <Area
                  type="monotone"
                  dataKey="revenue"
                  stroke="#6366f1"
                  strokeWidth={2}
                  fillOpacity={1}
                  fill="url(#colorRevenue)"
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="glass-card p-6">
          <h3 className="text-lg font-semibold text-dark-100 mb-4 flex items-center gap-2">
            <span className="w-2 h-2 bg-accent-500 rounded-full" />
            订单趋势
          </h3>
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={trendChartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                <XAxis
                  dataKey="displayDate"
                  tick={{ fontSize: 12, fill: '#64748b' }}
                  stroke="#475569"
                />
                <YAxis tick={{ fontSize: 12, fill: '#64748b' }} stroke="#475569" />
                <Tooltip
                  formatter={(value: number) => [value.toLocaleString(), '订单数']}
                  contentStyle={{
                    borderRadius: '8px',
                    border: '1px solid #334155',
                    backgroundColor: '#1e293b',
                    boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.3)',
                  }}
                />
                <Line
                  type="monotone"
                  dataKey="orders"
                  name="订单数"
                  stroke="#06b6d4"
                  strokeWidth={2}
                  dot={false}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="glass-card p-6">
          <h3 className="text-lg font-semibold text-dark-100 mb-4 flex items-center gap-2">
            <span className="w-2 h-2 bg-purple-500 rounded-full" />
            用户增长趋势
          </h3>
          <div className="h-80">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={trendChartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                <XAxis
                  dataKey="displayDate"
                  tick={{ fontSize: 12, fill: '#64748b' }}
                  stroke="#475569"
                />
                <YAxis tick={{ fontSize: 12, fill: '#64748b' }} stroke="#475569" />
                <Tooltip
                  formatter={(value: number) => [value.toLocaleString(), '客户数']}
                  contentStyle={{
                    borderRadius: '8px',
                    border: '1px solid #334155',
                    backgroundColor: '#1e293b',
                    boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.3)',
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

        <div className="glass-card p-6">
          <h3 className="text-lg font-semibold text-dark-100 mb-4 flex items-center gap-2">
            <span className="w-2 h-2 bg-amber-500 rounded-full" />
            产品分类占比
          </h3>
          <div className="h-80">
            {pieData.length === 0 ? (
              <div className="h-full flex items-center justify-center text-dark-500 text-sm">
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
                    labelLine={false}
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
                      border: '1px solid #334155',
                      backgroundColor: '#1e293b',
                      boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.3)',
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
