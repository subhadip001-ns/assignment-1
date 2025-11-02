import { useState, useEffect } from 'react'
import { useNavigate } from '@tanstack/react-router'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog'
import { coursesApi } from '@/lib/api'
import { type Course } from '@/lib/types'
import { ArrowLeft, Edit, Trash2, BookOpen, Users, GraduationCap } from 'lucide-react'

export function CourseDetails() {
  const navigate = useNavigate()
  // Extract courseId from URL pathname as fallback
  const pathname = window.location.pathname
  const courseId = pathname.split('/').pop() || ''
  const [course, setCourse] = useState<Course | null>(null)
  const [students, setStudents] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false)
  const [editFormData, setEditFormData] = useState({
    name: '',
    description: '',
    instructor: ''
  })

  useEffect(() => {
    if (courseId) {
      loadCourseDetails()
    }
  }, [courseId])

  const loadCourseDetails = async () => {
    try {
      const courseResponse = await coursesApi.getById(Number(courseId))
      const studentsResponse = await coursesApi.getStudents(Number(courseId))

      setCourse(courseResponse.data)
      setStudents(studentsResponse.data)
      setEditFormData({
        name: courseResponse.data.name,
        description: courseResponse.data.description || '',
        instructor: courseResponse.data.instructor
      })
    } catch (error) {
      console.error('Error loading course details:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleEditCourse = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!course) return

    try {
      await coursesApi.update(course.id, editFormData)
      setIsEditDialogOpen(false)
      loadCourseDetails()
    } catch (error) {
      console.error('Error updating course:', error)
    }
  }

  const handleDeleteCourse = async () => {
    if (!course) return

    if (confirm('Are you sure you want to delete this course? This action cannot be undone.')) {
      try {
        await coursesApi.delete(course.id)
        navigate({ to: '/courses' })
      } catch (error) {
        console.error('Error deleting course:', error)
      }
    }
  }

  if (loading) {
    return <div className="text-center">Loading course details...</div>
  }

  if (!course) {
    return <div className="text-center">Course not found</div>
  }

  return (
    <div className="max-w-4xl mx-auto">
      {/* Header with back button */}
      <div className="flex items-center gap-4 mb-6">
        <Button
          variant="outline"
          onClick={() => navigate({ to: '/courses' })}
          className="flex items-center gap-2 cursor-pointer"
        >
          <ArrowLeft className="w-4 h-4" />
          Back to Courses
        </Button>
        <h1 className="text-3xl font-bold text-gray-900">Course Details</h1>
      </div>

      {/* Course Information Card */}
      <Card className="mb-6 bg-white border border-gray-200">
        <CardHeader>
          <CardTitle className="flex items-center gap-3">
            <BookOpen className="w-6 h-6 text-blue-600" />
            <div>
              <h2 className="text-2xl">{course.name}</h2>
              <p className="text-gray-600">Course ID: {course.id}</p>
            </div>
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <Label className="text-sm font-medium text-gray-700">Instructor</Label>
            <p className="text-lg">{course.instructor}</p>
          </div>
          {course.description && (
            <div>
              <Label className="text-sm font-medium text-gray-700">Description</Label>
              <p className="text-gray-700 mt-1">{course.description}</p>
            </div>
          )}

          {/* Action Buttons */}
          <div className="flex gap-3 pt-4">
            <Dialog open={isEditDialogOpen} onOpenChange={setIsEditDialogOpen}>
              <DialogTrigger asChild>
                <Button className="bg-blue-600 hover:bg-blue-700 cursor-pointer text-white">
                  <Edit className="w-4 h-4 mr-2" />
                  Edit Course
                </Button>
              </DialogTrigger>
              <DialogContent className="bg-white">
                <DialogHeader>
                  <DialogTitle>Edit Course</DialogTitle>
                </DialogHeader>
                <form onSubmit={handleEditCourse} className="space-y-4">
                  <div>
                    <Label htmlFor="edit-name">Course Name</Label>
                    <Input
                      id="edit-name"
                      type="text"
                      value={editFormData.name}
                      onChange={(e) => setEditFormData({ ...editFormData, name: e.target.value })}
                      required
                    />
                  </div>
                  <div>
                    <Label htmlFor="edit-description">Description</Label>
                    <Textarea
                      id="edit-description"
                      value={editFormData.description}
                      onChange={(e) => setEditFormData({ ...editFormData, description: e.target.value })}
                      rows={3}
                    />
                  </div>
                  <div>
                    <Label htmlFor="edit-instructor">Instructor</Label>
                    <Input
                      id="edit-instructor"
                      type="text"
                      value={editFormData.instructor}
                      onChange={(e) => setEditFormData({ ...editFormData, instructor: e.target.value })}
                      required
                    />
                  </div>
                  <Button type="submit" className="w-full bg-blue-600 hover:bg-blue-700 text-white">
                    Update Course
                  </Button>
                </form>
              </DialogContent>
            </Dialog>

            <Button
              variant="outline"
              onClick={handleDeleteCourse}
              className="border-red-300 text-red-700 hover:bg-red-50 cursor-pointer"
            >
              <Trash2 className="w-4 h-4 mr-2" />
              Delete Course
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Enrolled Students Card */}
      <Card className="bg-white border border-gray-200">
        <CardHeader>
          <CardTitle className="flex items-center gap-3">
            <Users className="w-6 h-6 text-green-600" />
            <div>
              <h3 className="text-xl">Enrolled Students</h3>
              <p className="text-sm text-gray-600">{students.length} student{students.length !== 1 ? 's' : ''} enrolled</p>
            </div>
          </CardTitle>
        </CardHeader>
        <CardContent>
          {students.length > 0 ? (
            <div className="grid gap-3">
              {students.map((student) => (
                <div key={student.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div className="flex items-center gap-3">
                    <GraduationCap className="w-5 h-5 text-blue-600" />
                    <div>
                      <p className="font-medium">{student.name}</p>
                      <p className="text-sm text-gray-600">{student.email}</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8">
              <Users className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-500">No students enrolled in this course yet.</p>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
