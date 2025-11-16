import { useState } from 'react'
import { useNavigate } from '@tanstack/react-router'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { useAuth } from '@/lib/auth'
import { GraduationCap, Shield, Loader2, Eye, EyeOff } from 'lucide-react'
import wallImage from '@/assets/wall.jpeg'

export function Login() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [rememberMe, setRememberMe] = useState(false)
  const [loginError, setLoginError] = useState('')
  const { login, isLoading } = useAuth()
  const navigate = useNavigate()

  const handleLogin = async (role: 'student' | 'admin' = 'student') => {
    if (!email || !password) {
      setLoginError('Please fill in all fields')
      return
    }

    const success = await login(email, password, role)
    if (success) {
      navigate({ to: '/' })
    } else {
      setLoginError('Login failed. Please try again.')
    }
  }

  const handleAdminQuickLogin = () => {
    setEmail('admin@admin.com')
    setPassword('admin')
    setLoginError('')
    // Auto-submit after setting values
    setTimeout(() => {
      handleLogin('admin')
    }, 100)
  }

  return (
    <div className="min-h-screen flex">
      {/* Left Side - Background Image with Title */}
      <div className="hidden lg:flex lg:w-1/2 items-center justify-center p-8">
        <div 
          className="relative w-full h-full rounded-2xl bg-cover bg-center bg-no-repeat overflow-hidden"
          style={{
            backgroundImage: `url(${wallImage})`
          }}
        >
          <div className="absolute inset-0 from-blue-900/80 to-indigo-900/60" />
          <div className="relative z-10 flex flex-col justify-end items-start p-12 text-white h-full">
            <div>
              <h1 
                className="text-6xl font-bold text-white leading-tight mb-4"
                style={{ fontFamily: "'Instrument Serif', serif" }}
              >
                Student Course Enrollment Platform
              </h1>
              <p className="text-xl text-white/90 max-w-md">
                Welcome to your academic journey. Manage courses, enrollments, and connect with your learning community.
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Right Side - Login Form */}
      <div className="flex-1 flex items-center justify-center p-8 bg-white">
        <div className="w-full max-w-md">
          {/* Mobile Header */}
          <div className="text-center mb-8 lg:hidden">
            <div className="flex items-center justify-center gap-2 mb-4">
              <GraduationCap className="w-8 h-8 text-blue-600" />
              <h1 className="text-3xl font-bold text-gray-900">Enrollment Portal</h1>
            </div>
            <p className="text-gray-600">Sign in to access your account</p>
          </div>

          {/* Logo/Brand */}
          <div className="text-center mb-12 hidden lg:block">
            <div className="flex items-center justify-center gap-2 mb-2">
              <GraduationCap className="w-6 h-6 text-gray-900" />
              <span className="text-xl font-semibold text-gray-900">Enrollment Portal</span>
            </div>
          </div>

          {/* Welcome Title */}
          <div className="mb-8">
            <h1 
              className="text-4xl font-bold text-gray-900 mb-2 text-center lg:text-left"
              style={{ fontFamily: "'Instrument Serif', serif" }}
            >
              Welcome Back
            </h1>
            <p className="text-gray-600 text-center lg:text-left">
              Enter your email and password to access your account
            </p>
          </div>

          {/* Login Form */}
          <div className="space-y-6">
            <div className="space-y-2">
              <Label htmlFor="email" className="text-sm font-medium text-gray-900">
                Email
              </Label>
              <Input
                id="email"
                type="email"
                placeholder="Enter your email"
                value={email}
                onChange={(e) => {
                  setEmail(e.target.value)
                  setLoginError('')
                }}
                onKeyDown={(e) => {
                  if (e.key === 'Enter') {
                    handleLogin('student')
                  }
                }}
                className="h-12 border-gray-200 dark:border-gray-800"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="password" className="text-sm font-medium text-gray-900">
                Password
              </Label>
              <div className="relative">
                <Input
                  id="password"
                  type={showPassword ? 'text' : 'password'}
                  placeholder="Enter your password"
                  value={password}
                  onChange={(e) => {
                    setPassword(e.target.value)
                    setLoginError('')
                  }}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter') {
                      handleLogin('student')
                    }
                  }}
                  className="h-12 border-gray-200 dark:border-gray-800 pr-10"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-700 cursor-pointer"
                  aria-label={showPassword ? 'Hide password' : 'Show password'}
                >
                  {showPassword ? (
                    <EyeOff className="w-5 h-5" />
                  ) : (
                    <Eye className="w-5 h-5" />
                  )}
                </button>
              </div>
            </div>

            {/* Remember Me & Forgot Password */}
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <input
                  type="checkbox"
                  id="remember"
                  checked={rememberMe}
                  onChange={(e) => setRememberMe(e.target.checked)}
                  className="w-4 h-4 border-gray-300 rounded cursor-pointer"
                />
                <Label htmlFor="remember" className="text-sm text-gray-700 cursor-pointer">
                  Remember me
                </Label>
              </div>
              <button
                type="button"
                className="text-sm text-gray-600 hover:text-gray-900 cursor-pointer"
              >
                Forgot Password?
              </button>
            </div>

            {loginError && (
              <div className="p-3 rounded-md bg-red-50 border border-red-200">
                <p className="text-sm text-red-600 font-medium">{loginError}</p>
              </div>
            )}

            {/* Sign In Button */}
            <Button
              onClick={() => handleLogin('student')}
              disabled={isLoading}
              className="w-full h-12 bg-gray-900 hover:bg-gray-800 cursor-pointer text-white font-medium text-base"
            >
              {isLoading ? (
                <>
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                  Signing in...
                </>
              ) : (
                'Sign In'
              )}
            </Button>

            {/* Admin Login Button */}
            <Button
              onClick={handleAdminQuickLogin}
              disabled={isLoading}
              variant="outline"
              className="w-full h-12 cursor-pointer font-medium border-gray-200 dark:border-gray-800 bg-white hover:bg-gray-50"
            >
              <Shield className="w-4 h-4 mr-2" />
              Sign in as Admin
            </Button>
          </div>
        </div>
      </div>
    </div>
  )
}
