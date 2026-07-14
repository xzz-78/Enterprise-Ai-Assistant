import React from 'react'
import { Outlet, useNavigate, useLocation } from 'react-router-dom'
import {
  LayoutDashboard,
  MessageSquare,
  FileText,
  BarChart3,
  LogOut,
  User,
  Bot,
  ChevronLeft,
  ChevronRight,
} from 'lucide-react'
import { useAuth } from '../hooks/useAuth'

const Layout: React.FC = () => {
  const navigate = useNavigate()
  const location = useLocation()
  const { user, logout } = useAuth()
  const [collapsed, setCollapsed] = React.useState(false)

  const menuItems = [
    {
      path: '/dashboard',
      label: '数据看板',
      icon: LayoutDashboard,
    },
    {
      path: '/chat',
      label: 'AI 问答',
      icon: MessageSquare,
    },
    {
      path: '/documents',
      label: '知识库',
      icon: FileText,
    },
    {
      path: '/report',
      label: 'AI 分析报告',
      icon: BarChart3,
    },
  ]

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <div className="flex h-screen bg-dark-800">
      <aside 
        className={`fixed left-0 top-0 h-full z-50 flex flex-col bg-dark-700 border-r border-dark-600/50 transition-all duration-300 ease-in-out ${
          collapsed ? 'w-20' : 'w-64'
        }`}
      >
        <div className="h-16 flex items-center justify-between px-6 border-b border-dark-600/30">
          <div className={`flex items-center gap-3 ${collapsed ? 'justify-center w-full' : ''}`}>
            <div className="relative">
              <div className="w-8 h-8 gradient-primary rounded-lg flex items-center justify-center shadow-glow">
                <Bot className="w-5 h-5 text-white" />
              </div>
            </div>
            {!collapsed && (
              <span className="text-lg font-bold gradient-text whitespace-nowrap">
                AI Assistant
              </span>
            )}
          </div>
          {!collapsed && (
            <button
              onClick={() => setCollapsed(true)}
              className="p-1.5 rounded-lg text-dark-400 hover:text-dark-200 hover:bg-dark-600/30 transition-colors"
            >
              <ChevronLeft className="w-5 h-5" />
            </button>
          )}
        </div>

        <nav className="flex-1 px-4 py-6 space-y-1">
          {menuItems.map((item, index) => {
            const Icon = item.icon
            const isActive = location.pathname === item.path
            return (
              <button
                key={item.path}
                onClick={() => navigate(item.path)}
                className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium transition-all duration-200 group ${
                  isActive
                    ? 'gradient-primary text-white shadow-glow'
                    : 'text-dark-300 hover:bg-dark-600/40 hover:text-dark-100'
                }`}
                style={{ animationDelay: `${index * 50}ms` }}
              >
                <Icon className={`w-5 h-5 transition-transform duration-200 ${!isActive && 'group-hover:scale-110'}`} />
                {!collapsed && (
                  <span className="whitespace-nowrap animate-fade-in">
                    {item.label}
                  </span>
                )}
                {isActive && !collapsed && (
                  <span className="ml-auto w-1.5 h-1.5 bg-white/80 rounded-full" />
                )}
              </button>
            )
          })}
        </nav>

        {collapsed && (
          <button
            onClick={() => setCollapsed(false)}
            className="p-3 border-t border-dark-600/30 text-dark-400 hover:text-dark-200 hover:bg-dark-600/30 transition-colors"
          >
            <ChevronRight className="w-5 h-5 mx-auto" />
          </button>
        )}

        {!collapsed && (
          <div className="p-4 border-t border-dark-600/30">
            <div className="flex items-center gap-3 mb-3">
              <div className="relative">
                <div className="w-10 h-10 gradient-accent rounded-full flex items-center justify-center">
                  <User className="w-5 h-5 text-white" />
                </div>
                <span className="absolute bottom-0 right-0 w-3 h-3 bg-green-500 rounded-full border-2 border-dark-700" />
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-dark-100 truncate">
                  {user?.username}
                </p>
                <p className="text-xs text-dark-400 truncate">{user?.email}</p>
              </div>
            </div>
            <button
              onClick={handleLogout}
              className="w-full flex items-center gap-2 px-4 py-2.5 text-sm text-dark-400 hover:text-red-400 hover:bg-red-500/10 rounded-xl transition-all duration-200"
            >
              <LogOut className="w-4 h-4" />
              退出登录
            </button>
          </div>
        )}
      </aside>

      <main className={`flex-1 overflow-auto transition-all duration-300 ${collapsed ? 'ml-20' : 'ml-64'}`}>
        <div className="p-8">
          <Outlet />
        </div>
      </main>
    </div>
  )
}

export default Layout
