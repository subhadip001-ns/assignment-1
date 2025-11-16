import { useState } from 'react'
import { useNavigate } from '@tanstack/react-router'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { useAuth } from '@/lib/auth'
import { GraduationCap, Shield, Loader2 } from 'lucide-react'

export function Login() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
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
            backgroundImage: 'url(https://images.unsplash.com/photo-1760841386196-32ab1aae90cc?q=80&w=987&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D)'
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
      <div className="flex-1 flex items-center justify-center p-8 bg-gradient-to-br from-gray-50 to-gray-100">
        <div className="w-full max-w-md">
          <div className="text-center mb-8 lg:hidden">
            <div className="flex items-center justify-center gap-2 mb-4">
              <GraduationCap className="w-8 h-8 text-blue-600" />
              <h1 className="text-3xl font-bold text-gray-900">Enrollment Portal</h1>
            </div>
            <p className="text-gray-600">Sign in to access your account</p>
          </div>

          <Card className="border-gray-200 dark:border-gray-800 bg-white">
            <CardHeader className="space-y-1 pb-6">
              <CardTitle className="flex items-center gap-2 text-2xl font-semibold">
                <div className="p-2 rounded-lg bg-blue-50">
                  <GraduationCap className="w-5 h-5 text-blue-600" />
                </div>
                Welcome Back
              </CardTitle>
              <p className="text-sm text-muted-foreground mt-3">
                Sign in to your account to continue
              </p>
            </CardHeader>
            <CardContent className="space-y-5">
              <div className="space-y-2">
                <Label htmlFor="email" className="text-sm font-medium">
                  Email Address
                </Label>
                <Input
                  id="email"
                  type="email"
                  placeholder="student@university.edu"
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
                  className="h-11"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="password" className="text-sm font-medium">
                  Password
                </Label>
                <Input
                  id="password"
                  type="password"
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
                  className="h-11"
                />
              </div>
              {loginError && (
                <div className="p-3 rounded-lg bg-red-50 border border-red-200">
                  <p className="text-sm text-red-600 font-medium">{loginError}</p>
                </div>
              )}
              <Button
                onClick={() => handleLogin('student')}
                disabled={isLoading}
                className="w-full h-11 bg-blue-600 hover:bg-blue-700 cursor-pointer text-white font-medium text-base"
              >
                {isLoading ? (
                  <>
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                    Signing in...
                  </>
                ) : (
                  <>
                    <GraduationCap className="w-4 h-4 mr-2" />
                    Sign in as Student
                  </>
                )}
              </Button>

              <div className="relative my-6">
                <div className="absolute inset-0 flex items-center">
                  <div className="w-full border-t border-gray-200 dark:border-gray-800" />
                </div>
                <div className="relative flex justify-center text-xs uppercase tracking-wider">
                  <span className="bg-white px-3 text-muted-foreground font-medium">Or continue with</span>
                </div>
              </div>

              <Button
                onClick={handleAdminQuickLogin}
                disabled={isLoading}
                variant="outline"
                className="w-full h-11 cursor-pointer font-medium"
              >
                <Shield className="w-4 h-4 mr-2" />
                Sign in as Admin
              </Button>

              <p className="text-xs text-center text-muted-foreground mt-2">
                Admin credentials will be auto-filled
              </p>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}
