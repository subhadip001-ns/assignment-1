import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog'
import { enrollmentsApi, studentsApi, coursesApi } from '@/lib/api'
import { type EnrollmentWithDetails, type Student, type Course } from '@/lib/types'
import { Plus, Trash2, UserCheck } from 'lucide-react'

export function Enrollments() {
  const [enrollments, setEnrollments] = useState<EnrollmentWithDetails[]>([])
  const [students, setStudents] = useState<Student[]>([])
  const [courses, setCourses] = useState<Course[]>([])
  const [loading, setLoading] = useState(true)
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false)
  const [selectedStudentId, setSelectedStudentId] = useState<string>('')
  const [selectedCourseId, setSelectedCourseId] = useState<string>('')

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    try {
      const [enrollmentsRes, studentsRes, coursesRes] = await Promise.all([
        enrollmentsApi.getAll(),
        studentsApi.getAll(),
        coursesApi.getAll()
      ])
      setEnrollments(enrollmentsRes.data)
      setStudents(studentsRes.data)
      setCourses(coursesRes.data)
    } catch (error) {
      console.error('Error loading data:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleCreateEnrollment = async () => {
    if (!selectedStudentId || !selectedCourseId) return

    try {
      await enrollmentsApi.create({
        student_id: parseInt(selectedStudentId),
        course_id: parseInt(selectedCourseId)
      })
      setSelectedStudentId('')
      setSelectedCourseId('')
      setIsCreateDialogOpen(false)
      loadData()
    } catch (error) {
      console.error('Error creating enrollment:', error)
      alert('Failed to create enrollment. Student might already be enrolled in this course.')
    }
  }

  const handleDeleteEnrollment = async (studentId: number, courseId: number) => {
    if (confirm('Are you sure you want to unenroll this student from the course?')) {
      try {
        await enrollmentsApi.deleteByStudentAndCourse(studentId, courseId)
        loadData()
      } catch (error) {
        console.error('Error deleting enrollment:', error)
      }
    }
  }

  if (loading) {
    return <div className="text-center">Loading...</div>
  }

  return (
    <div>
      <div className="flex justify-between items-center mb-10">
        <div>
          <h1 
            className="text-4xl font-bold text-gray-900 mb-2"
            style={{ fontFamily: "'Instrument Serif', serif" }}
          >
            Enrollments
          </h1>
          <p className="text-gray-600">Manage student course enrollments</p>
        </div>
        <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
          <DialogTrigger asChild>
            <Button className="bg-gray-900 hover:bg-gray-800 cursor-pointer text-white h-11">
              <Plus className="w-4 h-4 mr-2" />
              Enroll Student
            </Button>
          </DialogTrigger>
          <DialogContent className="bg-white">
            <DialogHeader>
              <DialogTitle>Enroll Student in Course</DialogTitle>
            </DialogHeader>
            <div className="space-y-5">
              <div className="space-y-2">
                <label className="block text-sm font-medium text-gray-900">Student</label>
                <Select value={selectedStudentId} onValueChange={setSelectedStudentId}>
                  <SelectTrigger className="h-11">
                    <SelectValue placeholder="Select a student" />
                  </SelectTrigger>
                  <SelectContent>
                    {students.map((student) => (
                      <SelectItem key={student.id} value={student.id.toString()}>
                        {student.name} ({student.email})
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div className="space-y-2">
                <label className="block text-sm font-medium text-gray-900">Course</label>
                <Select value={selectedCourseId} onValueChange={setSelectedCourseId}>
                  <SelectTrigger className="h-11">
                    <SelectValue placeholder="Select a course" />
                  </SelectTrigger>
                  <SelectContent>
                    {courses.map((course) => (
                      <SelectItem key={course.id} value={course.id.toString()}>
                        {course.name} - {course.instructor}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <Button
                onClick={handleCreateEnrollment}
                disabled={!selectedStudentId || !selectedCourseId}
                className="w-full bg-gray-900 hover:bg-gray-800 cursor-pointer text-white h-11"
              >
                Create Enrollment
              </Button>
            </div>
          </DialogContent>
        </Dialog>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {enrollments.map((enrollment) => (
          <Card key={enrollment.id} className="bg-white border border-gray-200">
            <CardHeader>
              <CardTitle className="text-lg font-semibold text-gray-900">
                Enrollment #{enrollment.id}
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-3">
                <div>
                  <p className="text-xs text-gray-600 mb-1">Student</p>
                  <p className="font-medium text-gray-900">{enrollment.student.name}</p>
                  <p className="text-sm text-gray-600">{enrollment.student.email}</p>
                </div>
                <div>
                  <p className="text-xs text-gray-600 mb-1">Course</p>
                  <p className="font-medium text-gray-900">{enrollment.course.name}</p>
                  <p className="text-sm text-gray-600">by {enrollment.course.instructor}</p>
                </div>
              </div>
              <Button
                onClick={() => handleDeleteEnrollment(enrollment.student.id, enrollment.course.id)}
                className="w-full bg-red-50 hover:bg-red-100 text-red-600 border-none cursor-pointer h-10"
              >
                <Trash2 className="w-4 h-4 mr-2" />
                Unenroll
              </Button>
            </CardContent>
          </Card>
        ))}
      </div>

      {enrollments.length === 0 && (
        <div className="text-center py-12">
          <UserCheck className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <p className="text-gray-500">No enrollments found. Create your first enrollment!</p>
        </div>
      )}
    </div>
  )
}
