import React, { useState } from 'react'
import {
  FileText,
  Loader2,
  Sparkles,
  Lightbulb,
  ListChecks,
  TrendingUp,
  AlertCircle,
} from 'lucide-react'
import { generateBusinessReport } from '../services/report'
import type { BusinessInsightReport } from '../types'

const ReportPage: React.FC = () => {
  // P2 扩展：业务分析师报告状态
  const [report, setReport] = useState<BusinessInsightReport | null>(null)
  const [loading, setLoading] = useState(false)
  // 分析窗口下拉值，默认 30 天
  const [days, setDays] = useState(30)
  // 错误提示
  const [errorMsg, setErrorMsg] = useState<string | null>(null)

  const handleGenerateReport = async () => {
    setLoading(true)
    setErrorMsg(null)
    try {
      const result = await generateBusinessReport(days)
      setReport(result)
    } catch (error: any) {
      setErrorMsg(error?.response?.data?.detail || '报告生成失败，请稍后重试')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      {/* 页面标题（保留原结构） */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
          <Sparkles className="w-6 h-6 text-blue-600" />
          AI 分析报告
        </h1>
        <p className="mt-1 text-sm text-gray-500">
          基于销售数据自动生成结构化业务分析报告（执行摘要 + 关键洞察 + 行动建议）
        </p>
      </div>

      {/* 控制区：分析窗口下拉 + 主按钮 */}
      <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
        <div className="flex flex-wrap items-end gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              分析窗口
            </label>
            <select
              value={days}
              onChange={(e) => setDays(Number(e.target.value))}
              disabled={loading}
              className="px-4 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none disabled:opacity-50"
            >
              <option value={7}>最近 7 天</option>
              <option value={30}>最近 30 天</option>
              <option value={90}>最近 90 天</option>
            </select>
          </div>
          <div>
            <button
              onClick={handleGenerateReport}
              disabled={loading}
              className="flex items-center gap-2 px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {loading ? (
                <Loader2 className="w-5 h-5 animate-spin" />
              ) : (
                <Sparkles className="w-5 h-5" />
              )}
              {loading ? '生成中...' : '生成本月经营报告'}
            </button>
          </div>
        </div>
        {errorMsg && (
          <div className="mt-4 flex items-start gap-2 p-3 bg-red-50 border border-red-100 rounded-lg text-sm text-red-700">
            <AlertCircle className="w-4 h-4 mt-0.5 flex-shrink-0" />
            <span>{errorMsg}</span>
          </div>
        )}
      </div>

      {/* Loading 状态：首次加载且无报告 */}
      {loading && !report && (
        <div className="bg-white rounded-xl p-12 shadow-sm border border-gray-100">
          <div className="flex flex-col items-center">
            <Loader2 className="w-12 h-12 text-blue-600 animate-spin mb-4" />
            <p className="text-lg text-gray-600">正在生成业务分析报告...</p>
            <p className="text-sm text-gray-400 mt-2">
              AI 正在执行 SQL 聚合并撰写分析，请稍候
            </p>
          </div>
        </div>
      )}

      {/* 空状态：未点击生成 */}
      {!report && !loading && (
        <div className="bg-white rounded-xl p-12 shadow-sm border border-gray-100 text-center">
          <FileText className="w-16 h-16 text-gray-300 mx-auto mb-4" />
          <p className="text-gray-500 mb-2">
            点击「生成本月经营报告」，AI 将自动分析销售数据并生成报告
          </p>
          <p className="text-sm text-gray-400">
            报告将包含：执行摘要（summary）、关键洞察（insights）与行动建议（suggestions）
          </p>
        </div>
      )}

      {/* 三段式报告内容 */}
      {report && (
        <div className="space-y-6">
          {/* 第一段：执行摘要（蓝色高亮卡片） */}
          <div className="bg-white rounded-xl p-6 shadow-sm border border-blue-100">
            <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
              <FileText className="w-5 h-5 text-blue-600" />
              执行摘要
            </h2>
            <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-xl p-6 border border-blue-100">
              {report.summary ? (
                <p className="text-gray-800 leading-relaxed whitespace-pre-wrap">
                  {report.summary}
                </p>
              ) : (
                <p className="text-gray-400 italic">暂无执行摘要。</p>
              )}
            </div>
          </div>

          {/* 第二段：关键洞察（编号列表 + 图标） */}
          <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
            <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
              <Lightbulb className="w-5 h-5 text-yellow-500" />
              关键洞察
              <span className="ml-auto text-xs font-normal text-gray-400">
                {report.insights?.length ?? 0} 条
              </span>
            </h2>
            {report.insights && report.insights.length > 0 ? (
              <div className="space-y-3">
                {report.insights.map((insight, index) => (
                  <div
                    key={index}
                    className="flex items-start gap-3 p-4 bg-gray-50 rounded-xl hover:bg-gray-100 transition-colors"
                  >
                    <div className="w-7 h-7 bg-yellow-500 text-white rounded-full flex items-center justify-center text-sm font-medium flex-shrink-0">
                      {index + 1}
                    </div>
                    <Lightbulb className="w-4 h-4 text-yellow-500 mt-2 flex-shrink-0" />
                    <p className="text-gray-700 pt-1 leading-relaxed">{insight}</p>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-gray-400 italic text-sm">暂无关键洞察。</p>
            )}
          </div>

          {/* 第三段：行动建议（编号列表 + 图标） */}
          <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
            <h2 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
              <ListChecks className="w-5 h-5 text-green-500" />
              行动建议
              <span className="ml-auto text-xs font-normal text-gray-400">
                {report.suggestions?.length ?? 0} 条
              </span>
            </h2>
            {report.suggestions && report.suggestions.length > 0 ? (
              <div className="space-y-3">
                {report.suggestions.map((suggestion, index) => (
                  <div
                    key={index}
                    className="flex items-start gap-3 p-4 bg-gray-50 rounded-xl hover:bg-gray-100 transition-colors"
                  >
                    <div className="w-7 h-7 bg-green-500 text-white rounded-full flex items-center justify-center text-sm font-medium flex-shrink-0">
                      {index + 1}
                    </div>
                    <TrendingUp className="w-4 h-4 text-green-500 mt-2 flex-shrink-0" />
                    <p className="text-gray-700 pt-1 leading-relaxed">{suggestion}</p>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-gray-400 italic text-sm">暂无行动建议。</p>
            )}
          </div>
        </div>
      )}
    </div>
  )
}

export default ReportPage
