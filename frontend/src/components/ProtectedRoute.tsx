import { useEffect, type ReactNode } from 'react'
import { useNavigate } from '@tanstack/react-router'
import { useAuth } from '@/lib/auth'
import { Loader2 } from 'lucide-react'

interface ProtectedRouteProps {
  requireAdmin?: boolean
  children: ReactNode
}

export function ProtectedRoute({ requireAdmin = false, children }: ProtectedRouteProps) {
  const { user, isLoading } = useAuth()
  const navigate = useNavigate()

  useEffect(() => {
    if (!isLoading) {
      if (!user) {
        // Not logged in, redirect to login
        navigate({ to: '/login' })
      } else if (requireAdmin && user.role !== 'admin') {
        // Not admin, redirect to dashboard
        navigate({ to: '/' })
      }
    }
  }, [user, isLoading, requireAdmin, navigate])

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="w-8 h-8 animate-spin mx-auto mb-4 text-blue-600" />
          <p className="text-gray-600">Loading...</p>
        </div>
      </div>
    )
  }

  if (!user) {
    return null // Will redirect in useEffect
  }

  if (requireAdmin && user.role !== 'admin') {
    return null // Will redirect in useEffect
  }

  return <>{children}</>
}
