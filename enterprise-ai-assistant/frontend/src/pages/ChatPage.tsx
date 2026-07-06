import React, { useState, useRef, useEffect } from 'react'
import { Send, Bot, User, Loader2, FileText, BarChart2 } from 'lucide-react'
import { chat as chatApi, chatWithSourcesV2 } from '../services/chat'
import type { ChatMessage, SourceItem } from '../types'

interface ExtendedChatMessage extends ChatMessage {
  sources?: SourceItem[]
}

const ChatPage: React.FC = () => {
  const [messages, setMessages] = useState<ExtendedChatMessage[]>([
    {
      role: 'assistant',
      content: '您好！我是企业AI助手，有什么可以帮助您的吗？您可以询问关于公司制度、业务知识等问题。',
      timestamp: new Date(),
    },
  ])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  // P3 新增：是否显示参考来源（默认开启）
  const [showSources, setShowSources] = useState(true)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  // 自动滚动到底部
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSend = async () => {
    if (!input.trim() || loading) return

    const userMessage: ExtendedChatMessage = {
      role: 'user',
      content: input.trim(),
      timestamp: new Date(),
    }

    setMessages((prev) => [...prev, userMessage])
    const question = input.trim()
    setInput('')
    setLoading(true)

    try {
      if (showSources) {
        // P3：使用带来源 V2 接口
        const response = await chatWithSourcesV2(question)
        const assistantMessage: ExtendedChatMessage = {
          role: 'assistant',
          content: response.answer,
          timestamp: new Date(),
          sources: response.sources,
        }
        setMessages((prev) => [...prev, assistantMessage])
      } else {
        // 保留原有 chat 调用以保持兼容
        const response = await chatApi(question)
        const assistantMessage: ExtendedChatMessage = {
          role: 'assistant',
          content: response.answer,
          timestamp: new Date(),
        }
        setMessages((prev) => [...prev, assistantMessage])
      }
    } catch (error: any) {
      const errorMessage: ExtendedChatMessage = {
        role: 'assistant',
        content: `抱歉，发生了错误：${error.response?.data?.detail || '请稍后重试'}`,
        timestamp: new Date(),
      }
      setMessages((prev) => [...prev, errorMessage])
    } finally {
      setLoading(false)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString('zh-CN', {
      hour: '2-digit',
      minute: '2-digit',
    })
  }

  // 截断内容到 200 字
  const truncateContent = (text: string, max: number = 200) => {
    if (!text) return ''
    return text.length > max ? text.slice(0, max) + '...' : text
  }

  // 渲染来源列表
  const renderSources = (sources: SourceItem[]) => {
    if (!sources || sources.length === 0) {
      return (
        <div className="mt-3 pt-3 border-t border-gray-200">
          <p className="text-xs text-gray-400 italic">暂无参考来源（知识库为空）</p>
        </div>
      )
    }
    return (
      <div className="mt-3 pt-3 border-t border-gray-200 space-y-2">
        <div className="flex items-center gap-1.5 text-xs text-gray-500">
          <BarChart2 className="w-3.5 h-3.5" />
          <span>参考来源（{sources.length}）</span>
        </div>
        {sources.map((s, idx) => {
          const pct = (s.score * 100).toFixed(1)
          return (
            <div
              key={`${s.document_id}-${idx}`}
              className="bg-gray-50 border border-gray-200 rounded-lg p-2.5 text-xs"
            >
              <div className="flex items-center justify-between gap-2 mb-1">
                <div className="flex items-center gap-1.5 text-gray-700 font-medium min-w-0">
                  <FileText className="w-3.5 h-3.5 flex-shrink-0" />
                  <span className="truncate">{s.filename}</span>
                </div>
                <span className="text-blue-600 font-semibold flex-shrink-0">
                  相似度 {pct}%
                </span>
              </div>
              <p className="text-gray-600 leading-relaxed line-clamp-3">
                {truncateContent(s.content, 200)}
              </p>
            </div>
          )
        })}
      </div>
    )
  }

  // 快捷问题
  const quickQuestions = [
    '公司请假制度是什么？',
    '如何申请报销？',
    '介绍一下公司福利',
    '项目管理流程是怎样的？',
  ]

  return (
    <div className="h-full flex flex-col -m-8">
      {/* 页面标题 */}
      <div className="px-8 py-4 bg-white border-b border-gray-200">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-xl font-bold text-gray-900">AI 智能问答</h1>
            <p className="text-sm text-gray-500 mt-1">
              基于企业知识库的智能问答系统，帮您快速获取所需信息
            </p>
          </div>
          {/* P3 新增：显示参考来源开关 */}
          <label className="flex items-center gap-2 cursor-pointer select-none">
            <span className="text-sm text-gray-700">显示参考来源</span>
            <button
              type="button"
              role="switch"
              aria-checked={showSources}
              onClick={() => setShowSources((v) => !v)}
              className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                showSources ? 'bg-blue-600' : 'bg-gray-300'
              }`}
            >
              <span
                className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                  showSources ? 'translate-x-6' : 'translate-x-1'
                }`}
              />
            </button>
          </label>
        </div>
      </div>

      {/* 聊天消息区域 */}
      <div className="flex-1 overflow-y-auto p-6 space-y-4">
        {messages.map((message, index) => (
          <div
            key={index}
            className={`flex gap-3 ${message.role === 'user' ? 'flex-row-reverse' : ''}`}
          >
            {/* 头像 */}
            <div
              className={`w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0 ${
                message.role === 'user' ? 'bg-blue-600' : 'bg-gray-100'
              }`}
            >
              {message.role === 'user' ? (
                <User className="w-5 h-5 text-white" />
              ) : (
                <Bot className="w-5 h-5 text-gray-600" />
              )}
            </div>

            {/* 消息内容 */}
            <div className={`max-w-2xl ${message.role === 'user' ? 'text-right' : ''}`}>
              <div
                className={`inline-block px-4 py-3 rounded-2xl text-left ${
                  message.role === 'user'
                    ? 'bg-blue-600 text-white rounded-tr-sm'
                    : 'bg-white border border-gray-200 text-gray-800 rounded-tl-sm shadow-sm'
                }`}
              >
                <p className="whitespace-pre-wrap text-sm leading-relaxed">
                  {message.content}
                </p>
                {/* P3 新增：来源列表（仅在开启时、且 assistant 消息时显示） */}
                {message.role === 'assistant' && showSources && message.sources !== undefined && (
                  renderSources(message.sources)
                )}
              </div>
              <p className="mt-1 text-xs text-gray-400">
                {formatTime(message.timestamp)}
              </p>
            </div>
          </div>
        ))}

        {/* 加载中 */}
        {loading && (
          <div className="flex gap-3">
            <div className="w-10 h-10 rounded-full bg-gray-100 flex items-center justify-center flex-shrink-0">
              <Bot className="w-5 h-5 text-gray-600" />
            </div>
            <div className="bg-white border border-gray-200 px-4 py-3 rounded-2xl rounded-tl-sm shadow-sm">
              <div className="flex items-center gap-2">
                <Loader2 className="w-5 h-5 text-blue-600 animate-spin" />
                <span className="text-sm text-gray-500">正在思考中...</span>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* 快捷问题（只有一条消息时显示） */}
      {messages.length <= 1 && (
        <div className="px-6 pb-4">
          <p className="text-sm text-gray-500 mb-3">快捷问题：</p>
          <div className="flex flex-wrap gap-2">
            {quickQuestions.map((question, index) => (
              <button
                key={index}
                onClick={() => setInput(question)}
                className="px-4 py-2 bg-white border border-gray-200 rounded-full text-sm text-gray-600 hover:bg-gray-50 hover:border-blue-300 hover:text-blue-600 transition-colors"
              >
                {question}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* 输入区域 */}
      <div className="p-6 bg-white border-t border-gray-200">
        <div className="max-w-4xl mx-auto">
          <div className="flex gap-3 items-end">
            <div className="flex-1 relative">
              <textarea
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="请输入您的问题，按 Enter 发送..."
                rows={1}
                className="w-full px-4 py-3 pr-12 border border-gray-300 rounded-xl resize-none focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition-all"
                style={{ minHeight: '50px', maxHeight: '150px' }}
              />
            </div>
            <button
              onClick={handleSend}
              disabled={!input.trim() || loading}
              className="p-3 bg-blue-600 text-white rounded-xl hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
            >
              <Send className="w-5 h-5" />
            </button>
          </div>
          <p className="text-xs text-gray-400 mt-2 text-center">
            AI 回答基于知识库内容生成，仅供参考
          </p>
        </div>
      </div>
    </div>
  )
}

export default ChatPage
