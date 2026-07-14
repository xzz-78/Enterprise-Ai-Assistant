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
  const [report, setReport] = useState<BusinessInsightReport | null>(null)
  const [loading, setLoading] = useState(false)
  const [days, setDays] = useState(30)
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
      <div>
        <h1 className="text-2xl font-bold text-dark-100 flex items-center gap-2">
          <Sparkles className="w-6 h-6 text-primary-400" />
          AI 分析报告
        </h1>
        <p className="mt-1 text-sm text-dark-400">
          基于销售数据自动生成结构化业务分析报告（执行摘要 + 关键洞察 + 行动建议）
        </p>
      </div>

      <div className="glass-card p-6">
        <div className="flex flex-wrap items-end gap-4">
          <div>
            <label className="block text-sm font-medium text-dark-300 mb-2">
              分析窗口
            </label>
            <select
              value={days}
              onChange={(e) => setDays(Number(e.target.value))}
              disabled={loading}
              className="px-4 py-2 bg-dark-800/60 border border-dark-600/50 rounded-xl text-sm text-dark-200 focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500/20 transition-all disabled:opacity-50"
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
              className="flex items-center gap-2 px-6 py-2.5 gradient-primary text-white rounded-xl hover:opacity-90 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-glow"
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
          <div className="mt-4 flex items-start gap-2 p-3 bg-red-500/10 border border-red-500/30 rounded-xl text-sm text-red-300">
            <AlertCircle className="w-4 h-4 mt-0.5 flex-shrink-0" />
            <span>{errorMsg}</span>
          </div>
        )}
      </div>

      {loading && !report && (
        <div className="glass-card p-12">
          <div className="flex flex-col items-center">
            <div className="relative">
              <Loader2 className="w-12 h-12 text-primary-500 animate-spin mb-4" />
              <div className="absolute inset-0 w-12 h-12 border-2 border-primary-500/20 rounded-full animate-ping" />
            </div>
            <p className="text-lg text-dark-200">正在生成业务分析报告...</p>
            <p className="text-sm text-dark-400 mt-2">
              AI 正在执行 SQL 聚合并撰写分析，请稍候
            </p>
          </div>
        </div>
      )}

      {!report && !loading && (
        <div className="glass-card p-12 text-center">
          <div className="w-20 h-20 mx-auto mb-6 rounded-full bg-dark-600/50 flex items-center justify-center">
            <FileText className="w-10 h-10 text-dark-400" />
          </div>
          <p className="text-dark-300 mb-2">
            点击「生成本月经营报告」，AI 将自动分析销售数据并生成报告
          </p>
          <p className="text-sm text-dark-500">
            报告将包含：执行摘要（summary）、关键洞察（insights）与行动建议（suggestions）
          </p>
        </div>
      )}

      {report && (
        <div className="space-y-6">
          <div className="glass-card p-6 border-l-4 border-primary-500">
            <h2 className="text-lg font-semibold text-dark-100 mb-4 flex items-center gap-2">
              <FileText className="w-5 h-5 text-primary-400" />
              执行摘要
            </h2>
            <div className="bg-primary-500/5 rounded-xl p-6 border border-primary-500/10">
              {report.summary ? (
                <p className="text-dark-200 leading-relaxed whitespace-pre-wrap">
                  {report.summary}
                </p>
              ) : (
                <p className="text-dark-500 italic">暂无执行摘要。</p>
              )}
            </div>
          </div>

          <div className="glass-card p-6">
            <h2 className="text-lg font-semibold text-dark-100 mb-4 flex items-center gap-2">
              <Lightbulb className="w-5 h-5 text-amber-400" />
              关键洞察
              <span className="ml-auto text-xs font-normal text-dark-500">
                {report.insights?.length ?? 0} 条
              </span>
            </h2>
            {report.insights && report.insights.length > 0 ? (
              <div className="space-y-3">
                {report.insights.map((insight, index) => (
                  <div
                    key={index}
                    className="flex items-start gap-3 p-4 bg-dark-600/20 rounded-xl hover:bg-dark-600/30 transition-all duration-200 animate-fade-in-up"
                    style={{ animationDelay: `${index * 100}ms` }}
                  >
                    <div className="w-7 h-7 gradient-primary rounded-full flex items-center justify-center text-sm font-medium text-white flex-shrink-0">
                      {index + 1}
                    </div>
                    <div className="flex-1">
                      <div className="flex items-start gap-2">
                        <Lightbulb className="w-4 h-4 text-amber-400 mt-1 flex-shrink-0" />
                        <p className="text-dark-200 leading-relaxed">{insight}</p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-dark-500 italic text-sm">暂无关键洞察。</p>
            )}
          </div>

          <div className="glass-card p-6">
            <h2 className="text-lg font-semibold text-dark-100 mb-4 flex items-center gap-2">
              <ListChecks className="w-5 h-5 text-emerald-400" />
              行动建议
              <span className="ml-auto text-xs font-normal text-dark-500">
                {report.suggestions?.length ?? 0} 条
              </span>
            </h2>
            {report.suggestions && report.suggestions.length > 0 ? (
              <div className="space-y-3">
                {report.suggestions.map((suggestion, index) => (
                  <div
                    key={index}
                    className="flex items-start gap-3 p-4 bg-dark-600/20 rounded-xl hover:bg-dark-600/30 transition-all duration-200 animate-fade-in-up"
                    style={{ animationDelay: `${index * 100}ms` }}
                  >
                    <div className="w-7 h-7 gradient-accent rounded-full flex items-center justify-center text-sm font-medium text-white flex-shrink-0">
                      {index + 1}
                    </div>
                    <div className="flex-1">
                      <div className="flex items-start gap-2">
                        <TrendingUp className="w-4 h-4 text-emerald-400 mt-1 flex-shrink-0" />
                        <p className="text-dark-200 leading-relaxed">{suggestion}</p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-dark-500 italic text-sm">暂无行动建议。</p>
            )}
          </div>
        </div>
      )}
    </div>
  )
}

export default ReportPage
