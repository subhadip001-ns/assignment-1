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
      <div className="mb-10">
        <h1 
          className="text-4xl font-bold text-gray-900 mb-2"
          style={{ fontFamily: "'Instrument Serif', serif" }}
        >
          Browse Courses
        </h1>
        <p className="text-gray-600 text-lg">
          Explore available courses and manage your enrollments. Click "Enroll" to join a course or "Unenroll" to drop one.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {courses.map((course) => {
          const enrolled = isEnrolled(course.id)
          const isProcessing = enrolling === course.id

          return (
            <Card key={course.id} className="bg-white border border-gray-200">
              <CardHeader>
                <CardTitle className="text-lg font-semibold text-gray-900 mb-3">
                  {course.name}
                </CardTitle>
                <div className="space-y-2">
                  <p className="text-sm text-gray-600">by {course.instructor}</p>
                  {enrolled ? (
                    <Badge variant="secondary" className="bg-gray-100 text-gray-700">
                      <CheckCircle className="w-3 h-3 mr-1" />
                      Enrolled
                    </Badge>
                  ) : (
                    <Badge variant="outline" className="border-gray-300">
                      <GraduationCap className="w-3 h-3 mr-1" />
                      Available
                    </Badge>
                  )}
                </div>
              </CardHeader>
              <CardContent className="space-y-4">
                {course.description && (
                  <p className="text-sm text-gray-600">{course.description}</p>
                )}

                {enrolled ? (
                  <Button
                    onClick={() => handleUnenroll(course.id)}
                    disabled={isProcessing}
                    className="w-full bg-red-50 hover:bg-red-100 text-red-600 border-none cursor-pointer h-11 disabled:opacity-50"
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
                    className="w-full bg-gray-900 hover:bg-gray-800 cursor-pointer text-white h-11"
                  >
                    {isProcessing ? (
                      <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                    ) : (
                      <GraduationCap className="w-4 h-4 mr-2" />
                    )}
                    {isProcessing ? 'Enrolling...' : 'Enroll'}
                  </Button>
                )}
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
