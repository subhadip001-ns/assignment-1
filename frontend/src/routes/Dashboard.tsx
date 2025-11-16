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
      <div className="mb-10">
        <h1 
          className="text-4xl font-bold text-gray-900 mb-2"
          style={{ fontFamily: "'Instrument Serif', serif" }}
        >
          Welcome back, {user?.name}!
        </h1>
        <p className="text-gray-600 text-lg">
          {isAdmin
            ? 'Manage students, courses, and enrollments from your admin dashboard.'
            : 'Browse available courses and manage your enrollments.'
          }
        </p>
      </div>

      {isAdmin ? (
        // Admin Dashboard
        <>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-10">
            <Card className="bg-white border border-gray-200">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-3">
                <CardTitle className="text-sm font-medium text-gray-600">Total Courses</CardTitle>
                <BookOpen className="h-5 w-5 text-gray-400" />
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold text-gray-900">{courses.length}</div>
              </CardContent>
            </Card>

            <Card className="bg-white border border-gray-200">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-3">
                <CardTitle className="text-sm font-medium text-gray-600">Active Enrollments</CardTitle>
                <UserCheck className="h-5 w-5 text-gray-400" />
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold text-gray-900">{stats.totalEnrollments}</div>
                <p className="text-sm text-gray-500 mt-1">Total student enrollments</p>
              </CardContent>
            </Card>

            <Card className="bg-white border border-gray-200">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-3">
                <CardTitle className="text-sm font-medium text-gray-600">Total Students</CardTitle>
                <Users className="h-5 w-5 text-gray-400" />
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold text-gray-900">{stats.totalStudents}</div>
                <p className="text-sm text-gray-500 mt-1">Registered students</p>
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
                  <Button className="w-full justify-start bg-gray-900 hover:bg-gray-800 cursor-pointer text-white h-11">
                    <Plus className="w-4 h-4 mr-2" />
                    Add New Course
                  </Button>
                </Link>
                <Link to="/students">
                  <Button variant="outline" className="w-full justify-start h-11 cursor-pointer border-gray-200 dark:border-gray-800">
                    <Users className="w-4 h-4 mr-2" />
                    Manage Students
                  </Button>
                </Link>
                <Link to="/enrollments">
                  <Button variant="outline" className="w-full justify-start h-11 cursor-pointer border-gray-200 dark:border-gray-800">
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
                <CardTitle className="text-lg font-semibold text-gray-900">My Enrolled Courses</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {enrolledCourses.map((course) => (
                    <div key={course.id} className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
                      <div>
                        <p className="font-medium text-gray-900">{course.name}</p>
                        <p className="text-sm text-gray-600 mt-1">by {course.instructor}</p>
                      </div>
                      <Badge variant="secondary" className="bg-gray-100 text-gray-700">Enrolled</Badge>
                    </div>
                  ))}
                  {enrolledCourses.length === 0 && (
                    <p className="text-gray-500 text-sm py-4">You haven't enrolled in any courses yet.</p>
                  )}
                </div>
              </CardContent>
            </Card>

            <Card className="bg-white border border-gray-200">
              <CardHeader>
                <CardTitle className="text-lg font-semibold text-gray-900">Available Courses</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {courses.slice(0, 3).map((course) => {
                    const isEnrolled = enrolledCourses.some(ec => ec.id === course.id)
                    return (
                      <div key={course.id} className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
                        <div>
                          <p className="font-medium text-gray-900">{course.name}</p>
                          <p className="text-sm text-gray-600 mt-1">by {course.instructor}</p>
                        </div>
                        {isEnrolled ? (
                          <Badge variant="secondary" className="bg-gray-100 text-gray-700">Enrolled</Badge>
                        ) : (
                          <Badge variant="outline" className="border-gray-300">Available</Badge>
                        )}
                      </div>
                    )
                  })}
                  {courses.length === 0 && (
                    <p className="text-gray-500 text-sm py-4">No courses available yet.</p>
                  )}
                </div>
              </CardContent>
            </Card>
          </div>

          <Card className="bg-white border border-gray-200">
            <CardContent className="pt-6">
              <h3 className="text-xl font-semibold text-gray-900 mb-2">Ready to Learn?</h3>
              <p className="text-gray-600 mb-6">
                Browse available courses and enroll in the ones that interest you.
                Start building your academic journey today!
              </p>
              <Link to="/browse-courses">
                <Button className="bg-gray-900 hover:bg-gray-800 cursor-pointer text-white h-11">
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
