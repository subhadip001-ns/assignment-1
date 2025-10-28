import { useState, useEffect, useCallback } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { useAuth } from '@/lib/auth'
import { coursesApi, enrollmentsApi, studentsApi } from '@/lib/api'
import type { Course } from '@/lib/types'
import { BookOpen, Users, GraduationCap, Loader2, CheckCircle, XCircle } from 'lucide-react'
import { AxiosError } from 'axios'

export function CourseBrowser() {
  const { user } = useAuth()
  const [courses, setCourses] = useState<Course[]>([])
  const [enrolledCourses, setEnrolledCourses] = useState<Course[]>([])
  const [loading, setLoading] = useState(true)
  const [enrolling, setEnrolling] = useState<number | null>(null)

  const loadData = useCallback(async () => {
    if (!user) return

    try {
      const [coursesRes, enrolledRes] = await Promise.all([
        coursesApi.getAll(),
        studentsApi.getCourses(user.id)
      ])
      setCourses(coursesRes.data)
      setEnrolledCourses(enrolledRes.data)
    } catch (error) {
      console.error('Error loading courses:', error)
    } finally {
      setLoading(false)
    }
  }, [user])

  useEffect(() => {
    loadData()
  }, [loadData])

  const handleEnroll = async (courseId: number) => {
    if (!user) return

    setEnrolling(courseId)
    try {
      await enrollmentsApi.create({
        student_id: user.id,
        course_id: courseId
      })
      // Refresh enrolled courses
      const enrolledRes = await studentsApi.getCourses(user.id)
      setEnrolledCourses(enrolledRes.data)
    } catch (error) {
      console.error('Error enrolling in course:', error)
      const message = error instanceof AxiosError
        ? error.response?.data?.detail || 'Failed to enroll in course'
        : 'Failed to enroll in course'
      alert(message)
    } finally {
      setEnrolling(null)
    }
  }

  const handleUnenroll = async (courseId: number) => {
    if (!user) return

    if (!confirm('Are you sure you want to unenroll from this course?')) {
      return
    }

    setEnrolling(courseId)
    try {
      await enrollmentsApi.deleteByStudentAndCourse(user.id, courseId)
      // Refresh enrolled courses
      const enrolledRes = await studentsApi.getCourses(user.id)
      setEnrolledCourses(enrolledRes.data)
    } catch (error) {
      console.error('Error unenrolling from course:', error)
      const message = error instanceof AxiosError
        ? error.response?.data?.detail || 'Failed to unenroll from course'
        : 'Failed to unenroll from course'
      alert(message)
    } finally {
      setEnrolling(null)
    }
  }

  const isEnrolled = (courseId: number) => {
    return enrolledCourses.some(course => course.id === courseId)
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
        <span className="ml-2 text-gray-600">Loading courses...</span>
      </div>
    )
  }

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Browse Courses</h1>
        <p className="text-gray-600">
          Explore available courses and manage your enrollments. Click "Enroll" to join a course or "Unenroll" to drop one.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {courses.map((course) => {
          const enrolled = isEnrolled(course.id)
          const isProcessing = enrolling === course.id

          return (
            <Card key={course.id} className="bg-white border border-gray-200 hover:shadow-lg transition-shadow">
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <CardTitle className="flex items-center gap-2 mb-2">
                      <BookOpen className="w-5 h-5 text-blue-600" />
                      {course.name}
                    </CardTitle>
                    <div className="flex items-center gap-2 mb-2">
                      <Users className="w-4 h-4 text-gray-500" />
                      <span className="text-sm text-gray-600">by {course.instructor}</span>
                    </div>
                    {enrolled ? (
                      <Badge variant="secondary" className="flex items-center gap-1">
                        <CheckCircle className="w-3 h-3" />
                        Enrolled
                      </Badge>
                    ) : (
                      <Badge variant="outline" className="flex items-center gap-1">
                        <GraduationCap className="w-3 h-3" />
                        Available
                      </Badge>
                    )}
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                {course.description && (
                  <p className="text-gray-600 mb-4 text-sm">{course.description}</p>
                )}

                <div className="flex gap-2">
                  {enrolled ? (
                    <Button
                      onClick={() => handleUnenroll(course.id)}
                      disabled={isProcessing}
                      variant="outline"
                      className="flex-1 border-red-300 text-red-700 hover:bg-red-50"
                    >
                      {isProcessing ? (
                        <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                      ) : (
                        <XCircle className="w-4 h-4 mr-2" />
                      )}
                      {isProcessing ? 'Unenrolling...' : 'Unenroll'}
                    </Button>
                  ) : (
                    <Button
                      onClick={() => handleEnroll(course.id)}
                      disabled={isProcessing}
                      className="flex-1 bg-blue-600 hover:bg-blue-700"
                    >
                      {isProcessing ? (
                        <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                      ) : (
                        <GraduationCap className="w-4 h-4 mr-2" />
                      )}
                      {isProcessing ? 'Enrolling...' : 'Enroll'}
                    </Button>
                  )}
                </div>
              </CardContent>
            </Card>
          )
        })}
      </div>

      {courses.length === 0 && (
        <div className="text-center py-12">
          <BookOpen className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <p className="text-gray-500">No courses available at the moment.</p>
        </div>
      )}
    </div>
  )
}
