import apiClient from './apiClient'
import type {
  LoginRequest,
  RegisterRequest,
  TokenResponse,
  User,
} from '../types'

// 登录
export const login = async (data: LoginRequest): Promise<TokenResponse> => {
  // FastAPI 的 OAuth2PasswordRequestForm 使用 form-data
  const formData = new FormData()
  formData.append('username', data.username)
  formData.append('password', data.password)

  return apiClient.post('/auth/login', formData, {
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
  })
}

// 注册
export const register = async (data: RegisterRequest): Promise<User> => {
  return apiClient.post('/auth/register', data)
}

// 获取当前用户信息
export const getCurrentUser = async (): Promise<User> => {
  return apiClient.get('/auth/me')
}
