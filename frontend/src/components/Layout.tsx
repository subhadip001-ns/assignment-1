import { Link, Outlet, useNavigate } from '@tanstack/react-router'
import { Users, BookOpen, UserCheck, Home, LogOut, User, GraduationCap, MessageSquare } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { useAuth } from '@/lib/auth'

export function Layout() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  const handleLogout = () => {
    logout()
    navigate({ to: '/login' })
  }

  const isAdmin = user?.role === 'admin'

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Navigation Header */}
      <nav className="bg-white border-b border-gray-200 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex">
              <div className="flex-shrink-0 flex items-center">
                <h1 className="text-xl font-bold text-gray-900">
                  Enrollment Portal
                </h1>
              </div>
              <div className="hidden sm:ml-6 sm:flex sm:space-x-8">
                <Link
                  to="/"
                  className="inline-flex items-center px-1 pt-1 border-b-2 border-transparent text-sm font-medium text-gray-500 hover:text-gray-700 hover:border-gray-300"
                >
                  <Home className="w-4 h-4 mr-2" />
                  Dashboard
                </Link>
                {!isAdmin && (
                  <Link
                    to="/browse-courses"
                    className="inline-flex items-center px-1 pt-1 border-b-2 border-transparent text-sm font-medium text-gray-500 hover:text-gray-700 hover:border-gray-300"
                  >
                    <GraduationCap className="w-4 h-4 mr-2" />
                    Browse Courses
                  </Link>
                )}
                <Link
                  to="/ai-chat"
                  className="inline-flex items-center px-1 pt-1 border-b-2 border-transparent text-sm font-medium text-gray-500 hover:text-gray-700 hover:border-gray-300"
                >
                  <MessageSquare className="w-4 h-4 mr-2" />
                  AI Chat
                </Link>
                {isAdmin && (
                  <>
                    <Link
                      to="/students"
                      className="inline-flex items-center px-1 pt-1 border-b-2 border-transparent text-sm font-medium text-gray-500 hover:text-gray-700 hover:border-gray-300"
                    >
                      <Users className="w-4 h-4 mr-2" />
                      Students
                    </Link>
                    <Link
                      to="/courses"
                      className="inline-flex items-center px-1 pt-1 border-b-2 border-transparent text-sm font-medium text-gray-500 hover:text-gray-700 hover:border-gray-300"
                    >
                      <BookOpen className="w-4 h-4 mr-2" />
                      Courses
                    </Link>
                    <Link
                      to="/enrollments"
                      className="inline-flex items-center px-1 pt-1 border-b-2 border-transparent text-sm font-medium text-gray-500 hover:text-gray-700 hover:border-gray-300"
                    >
                      <UserCheck className="w-4 h-4 mr-2" />
                      Enrollments
                    </Link>
                  </>
                )}
              </div>
            </div>

            {/* User menu */}
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <User className="w-4 h-4 text-gray-500" />
                <span className="text-sm text-gray-700">
                  {user?.name} ({user?.role})
                </span>
              </div>
              <Button
                onClick={handleLogout}
                variant="outline"
                size="sm"
                className="flex items-center"
              >
                <LogOut className="w-4 h-4 mr-2" />
                Logout
              </Button>
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <Outlet />
      </main>
    </div>
  )
}
