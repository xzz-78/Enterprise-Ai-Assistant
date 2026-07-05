import React, { useState } from 'react'
import {
  FileText,
  Download,
  RefreshCw,
  TrendingUp,
  TrendingDown,
  Lightbulb,
  BarChart3,
  Loader2,
} from 'lucide-react'
import { generateReport } from '../services/report'
import type { ReportResponse } from '../types'

const ReportPage: React.FC = () => {
  const [report, setReport] = useState<ReportResponse | null>(null)
  const [loading, setLoading] = useState(false)
  const [days, setDays] = useState(30)

  const handleGenerateReport = async () => {
    setLoading(true)
    try {
      const result = await generateReport(days)
      setReport(result)
    } catch (error: any) {
      alert(error.response?.data?.detail || '报告生成失败')
    } finally {
      setLoading(false)
    }
  }

  const formatCurrency = (num: number) => {
    if (num >= 10000) {
      return '¥' + (num / 10000).toFixed(2) + '万'
    }
    return '¥' + num.toLocaleString()
  }

  const formatNumber = (num: number) => {
    return num.toLocaleString()
  }

  const handleExport = () => {
    if (!report) return

    const content = `企业销售数据分析报告
生成时间：${new Date().toLocaleString('zh-CN')}
分析周期：最近 ${days} 天

【数据摘要】
总销售额：${formatCurrency(report.data_summary.total_revenue)}
总订单数：${formatNumber(report.data_summary.total_orders)} 单
总客户数：${formatNumber(report.data_summary.total_customers)} 人
日均销售额：${formatCurrency(report.data_summary.avg_daily_revenue)}
销售增长率：${report.data_summary.revenue_growth_rate.toFixed(2)}%

【AI 智能分析】
${report.ai_analysis}

【改进建议】
${report.recommendations.map((r, i) => `${i + 1}. ${r}`).join('\n')}
`

    const blob = new Blob([content], { type: 'text/plain;charset=utf-8' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `销售分析报告_${new Date().toISOString().slice(0, 10)}.txt`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }

  const statItems = report
    ? [
        {
          label: '总销售额',
          value: formatCurrency(report.data_summary.total_revenue),
          icon: BarChart3,
          color: 'text-blue-600',
          bgColor: 'bg-blue-50',
        },
        {
          label: '总订单数',
          value: formatNumber(report.data_summary.total_orders),
          icon: FileText,
          color: 'text-green-600',
          bgColor: 'bg-green-50',
        },
        {
          label: '总客户数',
          value: formatNumber(report.data_summary.total_customers),
          icon: FileText,
          color: 'text-purple-600',
          bgColor: 'bg-purple-50',
        },
        {
          label: '日均销售额',
          value: formatCurrency(report.data_summary.avg_daily_revenue),
          icon: FileText,
          color: 'text-orange-600',
          bgColor: 'bg-orange-50',
        },
        {
          label: '销售增长率',
          value: report.data_summary.revenue_growth_rate.toFixed(2) + '%',
          icon:
            report.data_summary.revenue_growth_rate >= 0
              ? TrendingUp
              : TrendingDown,
          color:
            report.data_summary.revenue_growth_rate >= 0
              ? 'text-emerald-600'
              : 'text-red-600',
          bgColor:
            report.data_summary.revenue_growth_rate >= 0
              ? 'bg-emerald-50'
              : 'bg-red-50',
        },
      ]
    : []

  return (
    <div className="space-y-6">
      {/* 页面标题 */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">AI 分析报告</h1>
          <p className="mt-1 text-sm text-gray-500">
            基于销售数据自动生成智能分析报告与改进建议
          </p>
        </div>
        <div className="flex items-center gap-3">
          {report && (
            <button
              onClick={handleExport}
              className="flex items-center gap-2 px-4 py-2 bg-white border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-colors text-sm"
            >
              <Download className="w-4 h-4" />
              导出报告
            </button>
          )}
        </div>
      </div>

      {/* 生成报告区域 */}
      <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
        <div className="flex flex-wrap items-end gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              分析周期
            </label>
            <select
              value={days}
              onChange={(e) => setDays(Number(e.target.value))}
              className="px-4 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none"
            >
              <option value={7}>最近 7 天</option>
              <option value={15}>最近 15 天</option>
              <option value={30}>最近 30 天</option>
              <option value={60}>最近 60 天</option>
              <option value={90}>最近 90 天</option>
            </select>
          </div>
          <div>
            <button
              onClick={handleGenerateReport}
              disabled={loading}
              className="flex items-center gap-2 px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 transition-colors"
            >
              {loading ? (
                <Loader2 className="w-5 h-5 animate-spin" />
              ) : (
                <RefreshCw className="w-5 h-5" />
              )}
              {loading ? '生成中...' : '生成分析报告'}
            </button>
          </div>
        </div>
      </div>

      {/* 报告内容 */}
      {loading && !report && (
        <div className="bg-white rounded-xl p-12 shadow-sm border border-gray-100">
          <div className="flex flex-col items-center">
            <Loader2 className="w-12 h-12 text-blue-600 animate-spin mb-4" />
            <p className="text-lg text-gray-600">正在生成分析报告...</p>
            <p className="text-sm text-gray-400 mt-2">
              AI 正在分析销售数据并生成报告，请稍候
            </p>
          </div>
        </div>
      )}

      {!report && !loading && (
        <div className="bg-white rounded-xl p-12 shadow-sm border border-gray-100 text-center">
          <FileText className="w-16 h-16 text-gray-300 mx-auto mb-4" />
          <p className="text-gray-500 mb-4">
            点击「生成分析报告」按钮，AI 将自动分析销售数据并生成报告
          </p>
          <p className="text-sm text-gray-400">
            报告将包含数据摘要、AI 智能分析和改进建议
          </p>
        </div>
      )}

      {report && (
        <div className="space-y-6">
          {/* 数据摘要卡片 */}
          <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
            <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
              <BarChart3 className="w-5 h-5 text-blue-600" />
              数据摘要
            </h2>
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
              {statItems.map((item, index) => {
                const Icon = item.icon
                return (
                  <div
                    key={index}
                    className="p-4 rounded-xl border border-gray-100 bg-gray-50"
                  >
                    <div className={`w-10 h-10 rounded-lg ${item.bgColor} flex items-center justify-center mb-3`}>
                      <Icon className={`w-5 h-5 ${item.color}`} />
                    </div>
                    <p className="text-sm text-gray-500">{item.label}</p>
                    <p className="text-xl font-bold text-gray-900 mt-1">
                      {item.value}
                    </p>
                  </div>
                )
              })}
            </div>
          </div>

          {/* AI 分析 */}
          <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
            <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
              <Lightbulb className="w-5 h-5 text-yellow-500" />
              AI 智能分析
            </h2>
            <div className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-xl p-6 border border-blue-100">
              <p className="text-gray-700 leading-relaxed whitespace-pre-wrap">
                {report.ai_analysis}
              </p>
            </div>
          </div>

          {/* 改进建议 */}
          <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
            <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
              <TrendingUp className="w-5 h-5 text-green-500" />
              改进建议
            </h2>
            <div className="space-y-3">
              {report.recommendations.map((rec, index) => (
                <div
                  key={index}
                  className="flex items-start gap-3 p-4 bg-gray-50 rounded-xl hover:bg-gray-100 transition-colors"
                >
                  <div className="w-7 h-7 bg-blue-600 text-white rounded-full flex items-center justify-center text-sm font-medium flex-shrink-0">
                    {index + 1}
                  </div>
                  <p className="text-gray-700 pt-1">{rec}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default ReportPage
