import { useState, useEffect } from 'react'
import { useNavigate } from '@tanstack/react-router'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog'
import { coursesApi } from '@/lib/api'
import { type Course, type CreateCourseRequest } from '@/lib/types'
import { Plus, Eye, BookOpen } from 'lucide-react'

export function Courses() {
  const navigate = useNavigate()
  const [courses, setCourses] = useState<Course[]>([])
  const [loading, setLoading] = useState(true)
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false)
  const [formData, setFormData] = useState<CreateCourseRequest>({
    name: '',
    description: '',
    instructor: ''
  })

  useEffect(() => {
    loadCourses()
  }, [])

  const loadCourses = async () => {
    try {
      const response = await coursesApi.getAll()
      setCourses(response.data)
    } catch (error) {
      console.error('Error loading courses:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleCreateCourse = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      await coursesApi.create(formData)
      setFormData({ name: '', description: '', instructor: '' })
      setIsCreateDialogOpen(false)
      loadCourses()
    } catch (error) {
      console.error('Error creating course:', error)
    }
  }

  const handleViewDetails = (courseId: number) => {
    navigate({ to: `/courses/${courseId}` })
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
            Courses
          </h1>
          <p className="text-gray-600">Manage all courses in the system</p>
        </div>
        <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
          <DialogTrigger asChild>
            <Button className="bg-gray-900 hover:bg-gray-800 cursor-pointer text-white h-11">
              <Plus className="w-4 h-4 mr-2" />
              Add Course
            </Button>
          </DialogTrigger>
          <DialogContent className="bg-white">
            <DialogHeader>
              <DialogTitle>Add New Course</DialogTitle>
            </DialogHeader>
            <form onSubmit={handleCreateCourse} className="space-y-5">
              <div className="space-y-2">
                <Label htmlFor="name" className="text-sm font-medium text-gray-900">Course Name</Label>
                <Input
                  id="name"
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  required
                  className="h-11"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="description" className="text-sm font-medium text-gray-900">Description</Label>
                <Textarea
                  id="description"
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  rows={3}
                  className="min-h-[80px]"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="instructor" className="text-sm font-medium text-gray-900">Instructor</Label>
                <Input
                  id="instructor"
                  type="text"
                  value={formData.instructor}
                  onChange={(e) => setFormData({ ...formData, instructor: e.target.value })}
                  required
                  className="h-11"
                />
              </div>
              <Button type="submit" className="w-full bg-gray-900 hover:bg-gray-800 text-white h-11 cursor-pointer">
                Create Course
              </Button>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {courses.map((course) => (
          <Card key={course.id} className="bg-white border border-gray-200">
            <CardHeader>
              <CardTitle className="text-lg font-semibold text-gray-900">
                {course.name}
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <p className="text-sm text-gray-600 mb-1">Instructor</p>
                <p className="font-medium text-gray-900">{course.instructor}</p>
              </div>
              {course.description && (
                <p className="text-sm text-gray-600">{course.description}</p>
              )}
              <Button
                variant="outline"
                onClick={() => handleViewDetails(course.id)}
                className="w-full border-gray-200 dark:border-gray-800 hover:bg-gray-50 cursor-pointer h-10"
              >
                <Eye className="w-4 h-4 mr-2" />
                View Details
              </Button>
            </CardContent>
          </Card>
        ))}
      </div>

      {courses.length === 0 && (
        <div className="text-center py-12">
          <BookOpen className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <p className="text-gray-500">No courses found. Create your first course!</p>
        </div>
      )}
    </div>
  )
}
