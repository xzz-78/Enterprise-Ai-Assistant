import React, { useState, useRef, useEffect } from 'react'
import { Send, Bot, User, Loader2, FileText, BarChart2 } from 'lucide-react'
import { chat as chatApi, chatWithSources } from '../services/chat'
import type { ChatMessage, SourceItem } from '../types'

interface ExtendedChatMessage extends ChatMessage {
  sources?: SourceItem[]
  source?: 'rag' | 'llm' | 'empty_knowledge'
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
  const [showSources, setShowSources] = useState(true)
  const messagesEndRef = useRef<HTMLDivElement>(null)

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
        const response = await chatWithSources(question)
        const assistantMessage: ExtendedChatMessage = {
          role: 'assistant',
          content: response.answer,
          timestamp: new Date(),
          sources: response.sources,
        }
        setMessages((prev) => [...prev, assistantMessage])
      } else {
        const response = await chatApi(question)
        const assistantMessage: ExtendedChatMessage = {
          role: 'assistant',
          content: response.answer,
          timestamp: new Date(),
          source: response.source,
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

  const truncateContent = (text: string, max: number = 200) => {
    if (!text) return ''
    return text.length > max ? text.slice(0, max) + '...' : text
  }

  const renderSources = (sources: SourceItem[]) => {
    if (!sources || sources.length === 0) {
      return (
        <div className="mt-3 pt-3 border-t border-dark-600/50">
          <p className="text-xs text-dark-500 italic">暂无参考来源（知识库为空）</p>
        </div>
      )
    }
    return (
      <div className="mt-3 pt-3 border-t border-dark-600/50 space-y-2">
        <div className="flex items-center gap-1.5 text-xs text-dark-400">
          <BarChart2 className="w-3.5 h-3.5" />
          <span>参考来源（{sources.length}）</span>
        </div>
        {sources.map((s, idx) => {
          const pct = (s.score * 100).toFixed(1)
          return (
            <div
              key={`${s.document_id}-${idx}`}
              className="bg-dark-800/60 border border-dark-600/40 rounded-xl p-3 text-xs"
            >
              <div className="flex items-center justify-between gap-2 mb-1.5">
                <div className="flex items-center gap-1.5 text-dark-200 font-medium min-w-0">
                  <FileText className="w-3.5 h-3.5 flex-shrink-0 text-primary-400" />
                  <span className="truncate">{s.filename}</span>
                </div>
                <span className="text-primary-400 font-semibold flex-shrink-0">
                  相似度 {pct}%
                </span>
              </div>
              <p className="text-dark-400 leading-relaxed line-clamp-3">
                {truncateContent(s.content, 200)}
              </p>
            </div>
          )
        })}
      </div>
    )
  }

  const quickQuestions = [
    '公司请假制度是什么？',
    '如何申请报销？',
    '介绍一下公司福利',
    '项目管理流程是怎样的？',
  ]

  return (
    <div className="h-full flex flex-col -m-8">
      <div className="px-8 py-4 bg-dark-700/80 border-b border-dark-600/50 backdrop-blur-sm">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-xl font-bold text-dark-100 flex items-center gap-2">
              <Bot className="w-6 h-6 text-primary-400" />
              AI 智能问答
            </h1>
            <p className="text-sm text-dark-400 mt-1">
              基于企业知识库的智能问答系统，帮您快速获取所需信息
            </p>
          </div>
          <label className="flex items-center gap-2 cursor-pointer select-none">
            <span className="text-sm text-dark-300">显示参考来源</span>
            <button
              type="button"
              role="switch"
              aria-checked={showSources}
              onClick={() => setShowSources((v) => !v)}
              className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                showSources ? 'bg-primary-500' : 'bg-dark-600'
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

      <div className="flex-1 overflow-y-auto p-6 space-y-4">
        {messages.map((message, index) => (
          <div
            key={index}
            className={`flex gap-3 animate-fade-in-up ${message.role === 'user' ? 'flex-row-reverse' : ''}`}
            style={{ animationDelay: `${index * 50}ms` }}
          >
            <div
              className={`w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0 ${
                message.role === 'user' 
                  ? 'gradient-primary' 
                  : 'bg-dark-600/60'
              }`}
            >
              {message.role === 'user' ? (
                <User className="w-5 h-5 text-white" />
              ) : (
                <Bot className="w-5 h-5 text-primary-400" />
              )}
            </div>

            <div className={`max-w-2xl ${message.role === 'user' ? 'text-right' : ''}`}>
              <div
                className={`inline-block px-5 py-3 rounded-2xl text-left ${
                  message.role === 'user'
                    ? 'gradient-primary text-white rounded-tr-sm'
                    : 'bg-dark-700/60 border border-dark-600/40 text-dark-100 rounded-tl-sm'
                }`}
              >
                <p className="whitespace-pre-wrap text-sm leading-relaxed">
                  {message.content}
                </p>
                {message.role === 'assistant' && showSources && message.sources !== undefined && (
                  renderSources(message.sources)
                )}
              </div>
              <div className="mt-1.5 flex items-center gap-2">
                <span className="text-xs text-dark-500">{formatTime(message.timestamp)}</span>
                {message.role === 'assistant' && message.source && (
                  <span
                    className={`text-xs px-2 py-0.5 rounded-full ${
                      message.source === 'rag'
                        ? 'bg-primary-500/20 text-primary-400'
                        : 'bg-dark-600/50 text-dark-400'
                    }`}
                  >
                    {message.source === 'rag' ? '基于知识库' : '基于通用知识'}
                  </span>
                )}
              </div>
            </div>
          </div>
        ))}

        {loading && (
          <div className="flex gap-3 animate-fade-in-up">
            <div className="w-10 h-10 rounded-full bg-dark-600/60 flex items-center justify-center flex-shrink-0">
              <Bot className="w-5 h-5 text-primary-400" />
            </div>
            <div className="bg-dark-700/60 border border-dark-600/40 px-5 py-3 rounded-2xl rounded-tl-sm">
              <div className="flex items-center gap-2">
                <Loader2 className="w-5 h-5 text-primary-500 animate-spin" />
                <span className="text-sm text-dark-400">正在思考中...</span>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {messages.length <= 1 && (
        <div className="px-6 pb-4">
          <p className="text-sm text-dark-400 mb-3">快捷问题：</p>
          <div className="flex flex-wrap gap-2">
            {quickQuestions.map((question, index) => (
              <button
                key={index}
                onClick={() => setInput(question)}
                className="px-4 py-2 bg-dark-700/60 border border-dark-600/40 rounded-full text-sm text-dark-300 hover:border-primary-500/50 hover:text-primary-400 hover:bg-dark-600/40 transition-all duration-200"
              >
                {question}
              </button>
            ))}
          </div>
        </div>
      )}

      <div className="p-6 bg-dark-700/80 border-t border-dark-600/50 backdrop-blur-sm">
        <div className="max-w-4xl mx-auto">
          <div className="flex gap-3 items-end">
            <div className="flex-1 relative">
              <textarea
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="请输入您的问题，按 Enter 发送..."
                rows={1}
                className="w-full px-4 py-3 pr-12 bg-dark-800/60 border border-dark-600/50 rounded-xl resize-none text-dark-100 placeholder-dark-500 focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500/20 transition-all"
                style={{ minHeight: '50px', maxHeight: '150px' }}
              />
            </div>
            <button
              onClick={handleSend}
              disabled={!input.trim() || loading}
              className="p-3 gradient-primary text-white rounded-xl hover:opacity-90 disabled:bg-dark-600 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-glow"
            >
              <Send className="w-5 h-5" />
            </button>
          </div>
          <p className="text-xs text-dark-500 mt-2 text-center">
            AI 回答基于知识库内容生成，仅供参考
          </p>
        </div>
      </div>
    </div>
  )
}

export default ChatPage
