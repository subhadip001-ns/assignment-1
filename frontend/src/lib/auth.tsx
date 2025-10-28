import { createContext, useContext, useState, useEffect, type ReactNode } from 'react'
import { authApi, type LoginRequest } from './api'

export type UserRole = 'admin' | 'student'

export interface User {
  id: number
  name: string
  email: string
  role: UserRole
}

interface AuthContextType {
  user: User | null
  login: (email: string, password: string, role: UserRole) => Promise<boolean>
  logout: () => void
  isLoading: boolean
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

interface AuthProviderProps {
  children: ReactNode
}

export function AuthProvider({ children }: AuthProviderProps) {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const savedUser = localStorage.getItem('user')
    const savedToken = localStorage.getItem('token')

    if (savedUser && savedToken) {
      try {
        setUser(JSON.parse(savedUser))
        // TODO: Optionally validate token with API here
      } catch (error) {
        console.error('Error parsing saved user:', error)
        localStorage.removeItem('user')
        localStorage.removeItem('token')
      }
    }
    setIsLoading(false)
  }, [])

  const login = async (email: string, password: string, role: UserRole): Promise<boolean> => {
    setIsLoading(true)

    try {
      const loginData: LoginRequest = {
        email,
        password,
        role
      }

      const response = await authApi.login(loginData)

      const user: User = {
        id: response.data.user.id,
        name: response.data.user.name,
        email: response.data.user.email,
        role: response.data.user.role as UserRole
      }

      setUser(user)
      localStorage.setItem('user', JSON.stringify(user))
      localStorage.setItem('token', response.data.access_token)

      return true
    } catch (error) {
      console.error('Login error:', error)
      return false
    } finally {
      setIsLoading(false)
    }
  }

  const logout = async () => {
    try {
      const token = localStorage.getItem('token')
      if (token) {
        await authApi.logout()
      }
    } catch (error) {
      console.error('Logout API error:', error)
      // Continue with local logout even if API call fails
    }

    setUser(null)
    localStorage.removeItem('user')
    localStorage.removeItem('token')
  }

  const value: AuthContextType = {
    user,
    login,
    logout,
    isLoading
  }

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
}
