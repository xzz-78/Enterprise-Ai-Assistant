import React, { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { Bot, Loader2 } from 'lucide-react'
import { register as registerApi } from '../services/auth'
import { useAuth } from '../hooks/useAuth'
import { login as loginApi } from '../services/auth'
import AnimatedBackground from '../components/AnimatedBackground'

const RegisterPage: React.FC = () => {
  const navigate = useNavigate()
  const { login } = useAuth()
  const [username, setUsername] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')

    if (password !== confirmPassword) {
      setError('两次输入的密码不一致')
      return
    }

    if (password.length < 6) {
      setError('密码长度至少为 6 位')
      return
    }

    setLoading(true)

    try {
      await registerApi({ username, email, password })
      const loginResponse = await loginApi({ username, password })
      await login(loginResponse.access_token)
      navigate('/dashboard')
    } catch (err: any) {
      setError(err.response?.data?.detail || '注册失败，请稍后重试')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8 relative overflow-hidden">
      <AnimatedBackground />
      
      <div className="relative z-10 max-w-md w-full">
        <div className="text-center mb-8 animate-fade-in-up">
          <div className="relative mx-auto w-20 h-20 mb-6">
            <div className="absolute inset-0 gradient-primary rounded-2xl opacity-20 animate-pulse-slow" />
            <div className="relative w-full h-full gradient-primary rounded-2xl flex items-center justify-center shadow-glow">
              <Bot className="w-12 h-12 text-white" />
            </div>
          </div>
          <h2 className="text-3xl font-bold gradient-text mb-2">
            创建账号
          </h2>
          <p className="text-sm text-dark-300">
            加入企业级 AI 助手平台
          </p>
        </div>

        <form 
          className="glass-card p-8 space-y-6 animate-fade-in-up animate-delay-100" 
          onSubmit={handleSubmit}
        >
          {error && (
            <div className="bg-red-500/10 border border-red-500/30 text-red-300 px-4 py-3 rounded-xl text-sm flex items-center gap-2">
              <span className="w-1.5 h-1.5 bg-red-400 rounded-full animate-pulse" />
              {error}
            </div>
          )}

          <div className="space-y-5">
            <div className="space-y-2">
              <label htmlFor="username" className="block text-sm font-medium text-dark-200">
                用户名
              </label>
              <input
                id="username"
                name="username"
                type="text"
                required
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                className="w-full px-4 py-3.5 bg-dark-800/50 border border-dark-600 rounded-xl text-dark-100 placeholder-dark-500 focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500/20 transition-all duration-300"
                placeholder="请输入用户名（3-50字符）"
              />
            </div>

            <div className="space-y-2">
              <label htmlFor="email" className="block text-sm font-medium text-dark-200">
                邮箱
              </label>
              <input
                id="email"
                name="email"
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full px-4 py-3.5 bg-dark-800/50 border border-dark-600 rounded-xl text-dark-100 placeholder-dark-500 focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500/20 transition-all duration-300"
                placeholder="请输入邮箱地址"
              />
            </div>

            <div className="space-y-2">
              <label htmlFor="password" className="block text-sm font-medium text-dark-200">
                密码
              </label>
              <input
                id="password"
                name="password"
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full px-4 py-3.5 bg-dark-800/50 border border-dark-600 rounded-xl text-dark-100 placeholder-dark-500 focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500/20 transition-all duration-300"
                placeholder="请输入密码（至少6位）"
              />
            </div>

            <div className="space-y-2">
              <label htmlFor="confirmPassword" className="block text-sm font-medium text-dark-200">
                确认密码
              </label>
              <input
                id="confirmPassword"
                name="confirmPassword"
                type="password"
                required
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                className="w-full px-4 py-3.5 bg-dark-800/50 border border-dark-600 rounded-xl text-dark-100 placeholder-dark-500 focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500/20 transition-all duration-300"
                placeholder="请再次输入密码"
              />
            </div>
          </div>

          <div>
            <button
              type="submit"
              disabled={loading}
              className="w-full gradient-primary py-3.5 rounded-xl text-white font-medium shadow-glow hover:opacity-90 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-300 flex items-center justify-center gap-2"
            >
              {loading ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  注册中...
                </>
              ) : (
                '注 册'
              )}
            </button>
          </div>

          <div className="text-center text-sm text-dark-400 pt-2">
            已有账号？{' '}
            <Link 
              to="/login" 
              className="font-medium text-primary-400 hover:text-primary-300 transition-colors"
            >
              立即登录
            </Link>
          </div>
        </form>
      </div>
    </div>
  )
}

export default RegisterPage
