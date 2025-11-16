import { useState, useEffect } from 'react'
import { useNavigate } from '@tanstack/react-router'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog'
import { coursesApi, modulesApi } from '@/lib/api'
import { type Course, type Module, type CreateModuleRequest } from '@/lib/types'
import { ArrowLeft, Edit, Trash2, BookOpen, Users, GraduationCap, Plus, FileText } from 'lucide-react'

export function CourseDetails() {
  const navigate = useNavigate()
  // Extract courseId from URL pathname as fallback
  const pathname = window.location.pathname
  const courseId = pathname.split('/').pop() || ''
  const [course, setCourse] = useState<Course | null>(null)
  const [students, setStudents] = useState<any[]>([])
  const [modules, setModules] = useState<Module[]>([])
  const [loading, setLoading] = useState(true)
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false)
  const [isCreateModuleDialogOpen, setIsCreateModuleDialogOpen] = useState(false)
  const [isEditModuleDialogOpen, setIsEditModuleDialogOpen] = useState(false)
  const [editingModule, setEditingModule] = useState<Module | null>(null)
  const [editFormData, setEditFormData] = useState({
    name: '',
    description: '',
    instructor: ''
  })
  const [moduleFormData, setModuleFormData] = useState<CreateModuleRequest>({
    course_id: Number(courseId),
    title: '',
    description: '',
    content: '',
    order: 0
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
      const modulesResponse = await modulesApi.getByCourse(Number(courseId))

      setCourse(courseResponse.data)
      setStudents(studentsResponse.data)
      setModules(modulesResponse.data)
      setEditFormData({
        name: courseResponse.data.name,
        description: courseResponse.data.description || '',
        instructor: courseResponse.data.instructor
      })
      setModuleFormData({
        course_id: Number(courseId),
        title: '',
        description: '',
        content: '',
        order: modulesResponse.data.length
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

  const handleCreateModule = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      await modulesApi.create(moduleFormData)
      setIsCreateModuleDialogOpen(false)
      setModuleFormData({
        course_id: Number(courseId),
        title: '',
        description: '',
        content: '',
        order: modules.length
      })
      loadCourseDetails()
    } catch (error) {
      console.error('Error creating module:', error)
    }
  }

  const handleEditModule = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!editingModule) return

    try {
      await modulesApi.update(editingModule.id, {
        title: moduleFormData.title,
        description: moduleFormData.description,
        content: moduleFormData.content,
        order: moduleFormData.order
      })
      setIsEditModuleDialogOpen(false)
      setEditingModule(null)
      loadCourseDetails()
    } catch (error) {
      console.error('Error updating module:', error)
    }
  }

  const handleDeleteModule = async (moduleId: number) => {
    if (confirm('Are you sure you want to delete this module?')) {
      try {
        await modulesApi.delete(moduleId)
        loadCourseDetails()
      } catch (error) {
        console.error('Error deleting module:', error)
      }
    }
  }

  const openEditModuleDialog = (module: Module) => {
    setEditingModule(module)
    setModuleFormData({
      course_id: Number(courseId),
      title: module.title,
      description: module.description || '',
      content: module.content || '',
      order: module.order
    })
    setIsEditModuleDialogOpen(true)
  }

  if (loading) {
    return <div className="text-center">Loading course details...</div>
  }

  if (!course) {
    return <div className="text-center">Course not found</div>
  }

  return (
    <div>
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

      {/* Modules Card */}
      <Card className="mb-6 bg-white border border-gray-200">
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="flex items-center gap-3">
              <FileText className="w-6 h-6 text-purple-600" />
              <div>
                <h3 className="text-xl">Course Modules</h3>
                <p className="text-sm text-gray-600">{modules.length} module{modules.length !== 1 ? 's' : ''}</p>
              </div>
            </CardTitle>
            <Dialog open={isCreateModuleDialogOpen} onOpenChange={setIsCreateModuleDialogOpen}>
              <DialogTrigger asChild>
                <Button className="bg-blue-600 hover:bg-blue-700 cursor-pointer text-white">
                  <Plus className="w-4 h-4 mr-2" />
                  Add Module
                </Button>
              </DialogTrigger>
              <DialogContent className="bg-white">
                <DialogHeader>
                  <DialogTitle>Add New Module</DialogTitle>
                </DialogHeader>
                <form onSubmit={handleCreateModule} className="space-y-4">
                  <div>
                    <Label htmlFor="module-title">Module Title</Label>
                    <Input
                      id="module-title"
                      type="text"
                      value={moduleFormData.title}
                      onChange={(e) => setModuleFormData({ ...moduleFormData, title: e.target.value })}
                      required
                    />
                  </div>
                  <div>
                    <Label htmlFor="module-description">Description</Label>
                    <Textarea
                      id="module-description"
                      value={moduleFormData.description}
                      onChange={(e) => setModuleFormData({ ...moduleFormData, description: e.target.value })}
                      rows={2}
                    />
                  </div>
                  <div>
                    <Label htmlFor="module-content">Content</Label>
                    <Textarea
                      id="module-content"
                      value={moduleFormData.content}
                      onChange={(e) => setModuleFormData({ ...moduleFormData, content: e.target.value })}
                      rows={4}
                      placeholder="Module content, instructions, or materials..."
                    />
                  </div>
                  <div>
                    <Label htmlFor="module-order">Order</Label>
                    <Input
                      id="module-order"
                      type="number"
                      min="0"
                      value={moduleFormData.order}
                      onChange={(e) => setModuleFormData({ ...moduleFormData, order: parseInt(e.target.value) || 0 })}
                    />
                  </div>
                  <Button type="submit" className="w-full bg-blue-600 hover:bg-blue-700 text-white">
                    Create Module
                  </Button>
                </form>
              </DialogContent>
            </Dialog>
          </div>
        </CardHeader>
        <CardContent>
          {modules.length > 0 ? (
            <div className="grid gap-4">
              {modules.map((module) => (
                <Card key={module.id} className="bg-gray-50 border border-gray-200">
                  <CardContent className="pt-4">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-2">
                          <span className="text-xs font-medium text-gray-500 bg-white px-2 py-1 rounded">
                            Module {module.order + 1}
                          </span>
                          <h4 className="font-semibold text-lg">{module.title}</h4>
                        </div>
                        {module.description && (
                          <p className="text-gray-600 text-sm mb-2">{module.description}</p>
                        )}
                        {module.content && (
                          <div className="mt-3 p-3 bg-white rounded border border-gray-200">
                            <p className="text-sm text-gray-700 whitespace-pre-wrap">{module.content}</p>
                          </div>
                        )}
                      </div>
                      <div className="flex gap-2 ml-4">
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => openEditModuleDialog(module)}
                          className="cursor-pointer"
                        >
                          <Edit className="w-4 h-4" />
                        </Button>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleDeleteModule(module.id)}
                          className="border-red-300 text-red-700 hover:bg-red-50 cursor-pointer"
                        >
                          <Trash2 className="w-4 h-4" />
                        </Button>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          ) : (
            <div className="text-center py-8">
              <FileText className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-500">No modules added to this course yet.</p>
              <p className="text-sm text-gray-400 mt-1">Click "Add Module" to create the first module.</p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Edit Module Dialog */}
      <Dialog open={isEditModuleDialogOpen} onOpenChange={setIsEditModuleDialogOpen}>
        <DialogContent className="bg-white">
          <DialogHeader>
            <DialogTitle>Edit Module</DialogTitle>
          </DialogHeader>
          <form onSubmit={handleEditModule} className="space-y-4">
            <div>
              <Label htmlFor="edit-module-title">Module Title</Label>
              <Input
                id="edit-module-title"
                type="text"
                value={moduleFormData.title}
                onChange={(e) => setModuleFormData({ ...moduleFormData, title: e.target.value })}
                required
              />
            </div>
            <div>
              <Label htmlFor="edit-module-description">Description</Label>
              <Textarea
                id="edit-module-description"
                value={moduleFormData.description}
                onChange={(e) => setModuleFormData({ ...moduleFormData, description: e.target.value })}
                rows={2}
              />
            </div>
            <div>
              <Label htmlFor="edit-module-content">Content</Label>
              <Textarea
                id="edit-module-content"
                value={moduleFormData.content}
                onChange={(e) => setModuleFormData({ ...moduleFormData, content: e.target.value })}
                rows={4}
                placeholder="Module content, instructions, or materials..."
              />
            </div>
            <div>
              <Label htmlFor="edit-module-order">Order</Label>
              <Input
                id="edit-module-order"
                type="number"
                min="0"
                value={moduleFormData.order}
                onChange={(e) => setModuleFormData({ ...moduleFormData, order: parseInt(e.target.value) || 0 })}
              />
            </div>
            <Button type="submit" className="w-full bg-blue-600 hover:bg-blue-700 text-white">
              Update Module
            </Button>
          </form>
        </DialogContent>
      </Dialog>

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
