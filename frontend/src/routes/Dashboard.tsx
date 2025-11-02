import { useState, useEffect, useCallback } from 'react'
import { Link } from '@tanstack/react-router'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { useAuth } from '@/lib/auth'
import { coursesApi, studentsApi, enrollmentsApi } from '@/lib/api'
import { type Course } from '@/lib/types'
import { Users, BookOpen, UserCheck, GraduationCap, Shield, Plus } from 'lucide-react'

export function Dashboard() {
  const { user } = useAuth()
  const [courses, setCourses] = useState<Course[]>([])
  const [enrolledCourses, setEnrolledCourses] = useState<Course[]>([])
  const [stats, setStats] = useState({
    totalStudents: 0,
    totalEnrollments: 0
  })
  const [loading, setLoading] = useState(true)

  const isAdmin = user?.role === 'admin'

  const loadDashboardData = useCallback(async () => {
    try {
      if (isAdmin) {
        // Admin sees all courses, students, and enrollments
        const [coursesRes, studentsRes, enrollmentsRes] = await Promise.all([
          coursesApi.getAll(),
          studentsApi.getAll(),
          enrollmentsApi.getAll()
        ])
        setCourses(coursesRes.data)
        setStats({
          totalStudents: studentsRes.data.length,
          totalEnrollments: enrollmentsRes.data.length
        })
      } else {
        // Student sees available courses and their enrollments
        const [coursesRes, enrolledRes] = await Promise.all([
          coursesApi.getAll(),
          studentsApi.getCourses(user!.id)
        ])
        setCourses(coursesRes.data)
        setEnrolledCourses(enrolledRes.data)
      }
    } catch (error) {
      console.error('Error loading dashboard data:', error)
    } finally {
      setLoading(false)
    }
  }, [isAdmin, user])

  useEffect(() => {
    loadDashboardData()
  }, [loadDashboardData])

  if (loading) {
    return <div className="text-center">Loading...</div>
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">
            Welcome back, {user?.name}!
          </h1>
          <p className="text-gray-600 mt-2">
            {isAdmin
              ? 'Manage students, courses, and enrollments from your admin dashboard.'
              : 'Browse available courses and manage your enrollments.'
            }
          </p>
        </div>
        <Badge variant={isAdmin ? "default" : "secondary"} className="flex items-center gap-1">
          {isAdmin ? <Shield className="w-3 h-3" /> : <GraduationCap className="w-3 h-3" />}
          {user?.role === 'admin' ? 'Administrator' : 'Student'}
        </Badge>
      </div>

      {isAdmin ? (
        // Admin Dashboard
        <>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            <Card className="bg-white border border-gray-200">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Total Courses</CardTitle>
                <BookOpen className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{courses.length}</div>
              </CardContent>
            </Card>

            <Card className="bg-white border border-gray-200">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Active Enrollments</CardTitle>
                <UserCheck className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{stats.totalEnrollments}</div>
                <p className="text-xs text-muted-foreground">Total student enrollments</p>
              </CardContent>
            </Card>

            <Card className="bg-white border border-gray-200">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Total Students</CardTitle>
                <Users className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{stats.totalStudents}</div>
                <p className="text-xs text-muted-foreground">Registered students</p>
              </CardContent>
            </Card>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <Card className="bg-white border border-gray-200">
              <CardHeader>
                <CardTitle>Quick Actions</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <Link to="/courses">
                  <Button className="w-full justify-start bg-blue-600 hover:bg-blue-700 cursor-pointer text-white">
                    <Plus className="w-4 h-4 mr-2" />
                    Add New Course
                  </Button>
                </Link>
                <Link to="/students">
                  <Button variant="outline" className="w-full justify-start">
                    <Users className="w-4 h-4 mr-2" />
                    Manage Students
                  </Button>
                </Link>
                <Link to="/enrollments">
                  <Button variant="outline" className="w-full justify-start">
                    <UserCheck className="w-4 h-4 mr-2" />
                    View Enrollments
                  </Button>
                </Link>
              </CardContent>
            </Card>

            <Card className="bg-white border border-gray-200">
              <CardHeader>
                <CardTitle>Recent Courses</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {courses.slice(0, 3).map((course) => (
                    <div key={course.id} className="flex items-center justify-between">
                      <div>
                        <p className="font-medium text-sm">{course.name}</p>
                        <p className="text-xs text-gray-500">by {course.instructor}</p>
                      </div>
                    </div>
                  ))}
                  {courses.length === 0 && (
                    <p className="text-sm text-gray-500">No courses created yet</p>
                  )}
                </div>
              </CardContent>
            </Card>
          </div>
        </>
      ) : (
        // Student Dashboard
        <>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
            <Card className="bg-white border border-gray-200">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <BookOpen className="w-5 h-5 text-blue-600" />
                  My Enrolled Courses
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {enrolledCourses.map((course) => (
                    <div key={course.id} className="flex items-center justify-between p-3 bg-gray-50 rounded">
                      <div>
                        <p className="font-medium">{course.name}</p>
                        <p className="text-sm text-gray-600">by {course.instructor}</p>
                      </div>
                      <Badge variant="secondary">Enrolled</Badge>
                    </div>
                  ))}
                  {enrolledCourses.length === 0 && (
                    <p className="text-gray-500 text-sm">You haven't enrolled in any courses yet.</p>
                  )}
                </div>
              </CardContent>
            </Card>

            <Card className="bg-white border border-gray-200">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <GraduationCap className="w-5 h-5 text-blue-600" />
                  Available Courses
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {courses.slice(0, 3).map((course) => {
                    const isEnrolled = enrolledCourses.some(ec => ec.id === course.id)
                    return (
                      <div key={course.id} className="flex items-center justify-between p-3 bg-gray-50 rounded">
                        <div>
                          <p className="font-medium">{course.name}</p>
                          <p className="text-sm text-gray-600">by {course.instructor}</p>
                        </div>
                        {isEnrolled ? (
                          <Badge variant="secondary">Enrolled</Badge>
                        ) : (
                          <Badge variant="outline">Available</Badge>
                        )}
                      </div>
                    )
                  })}
                  {courses.length === 0 && (
                    <p className="text-gray-500 text-sm">No courses available yet.</p>
                  )}
                </div>
              </CardContent>
            </Card>
          </div>

          <Card className="bg-blue-50 border border-blue-200">
            <CardContent className="pt-6">
              <h3 className="text-lg font-semibold text-blue-900 mb-2">Ready to Learn?</h3>
              <p className="text-blue-800 mb-4">
                Browse available courses and enroll in the ones that interest you.
                Start building your academic journey today!
              </p>
              <Link to="/browse-courses">
                <Button className="bg-blue-600 hover:bg-blue-700 cursor-pointer text-white">
                  <GraduationCap className="w-4 h-4 mr-2" />
                  Browse All Courses
                </Button>
              </Link>
            </CardContent>
          </Card>
        </>
      )}
    </div>
  )
}
