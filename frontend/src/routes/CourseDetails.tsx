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
      <div className="mb-10">
        <Button
          variant="outline"
          onClick={() => navigate({ to: '/courses' })}
          className="mb-6 border-gray-200 dark:border-gray-800 hover:bg-gray-50 cursor-pointer"
        >
          <ArrowLeft className="w-4 h-4 mr-2" />
          Back to Courses
        </Button>
        <h1 
          className="text-4xl font-bold text-gray-900 mb-2"
          style={{ fontFamily: "'Instrument Serif', serif" }}
        >
          Course Details
        </h1>
      </div>

      {/* Course Information Card */}
      <Card className="mb-8 bg-white border border-gray-200">
        <CardHeader>
          <CardTitle className="text-2xl font-semibold text-gray-900">
            {course.name}
          </CardTitle>
          <p className="text-sm text-gray-600 mt-1">Course ID: {course.id}</p>
        </CardHeader>
        <CardContent className="space-y-5">
          <div>
            <Label className="text-sm font-medium text-gray-600 mb-1 block">Instructor</Label>
            <p className="text-lg font-medium text-gray-900">{course.instructor}</p>
          </div>
          {course.description && (
            <div>
              <Label className="text-sm font-medium text-gray-600 mb-1 block">Description</Label>
              <p className="text-gray-700">{course.description}</p>
            </div>
          )}

          {/* Action Buttons */}
          <div className="flex gap-3 pt-2">
            <Dialog open={isEditDialogOpen} onOpenChange={setIsEditDialogOpen}>
              <DialogTrigger asChild>
                <Button className="bg-gray-900 hover:bg-gray-800 cursor-pointer text-white h-11">
                  <Edit className="w-4 h-4 mr-2" />
                  Edit Course
                </Button>
              </DialogTrigger>
              <DialogContent className="bg-white">
                <DialogHeader>
                  <DialogTitle>Edit Course</DialogTitle>
                </DialogHeader>
                <form onSubmit={handleEditCourse} className="space-y-5">
                  <div className="space-y-2">
                    <Label htmlFor="edit-name" className="text-sm font-medium text-gray-900">Course Name</Label>
                    <Input
                      id="edit-name"
                      type="text"
                      value={editFormData.name}
                      onChange={(e) => setEditFormData({ ...editFormData, name: e.target.value })}
                      required
                      className="h-11"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="edit-description" className="text-sm font-medium text-gray-900">Description</Label>
                    <Textarea
                      id="edit-description"
                      value={editFormData.description}
                      onChange={(e) => setEditFormData({ ...editFormData, description: e.target.value })}
                      rows={3}
                      className="min-h-[80px]"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="edit-instructor" className="text-sm font-medium text-gray-900">Instructor</Label>
                    <Input
                      id="edit-instructor"
                      type="text"
                      value={editFormData.instructor}
                      onChange={(e) => setEditFormData({ ...editFormData, instructor: e.target.value })}
                      required
                      className="h-11"
                    />
                  </div>
                  <Button type="submit" className="w-full bg-gray-900 hover:bg-gray-800 text-white h-11 cursor-pointer">
                    Update Course
                  </Button>
                </form>
              </DialogContent>
            </Dialog>

            <Button
              onClick={handleDeleteCourse}
              className="bg-red-50 hover:bg-red-100 text-red-600 border-none cursor-pointer h-11"
            >
              <Trash2 className="w-4 h-4 mr-2" />
              Delete Course
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Modules Card */}
      <Card className="mb-8 bg-white border border-gray-200">
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="text-xl font-semibold text-gray-900">Course Modules</CardTitle>
              <p className="text-sm text-gray-600 mt-1">{modules.length} module{modules.length !== 1 ? 's' : ''}</p>
            </div>
            <Dialog open={isCreateModuleDialogOpen} onOpenChange={setIsCreateModuleDialogOpen}>
              <DialogTrigger asChild>
                <Button className="bg-gray-900 hover:bg-gray-800 cursor-pointer text-white h-11">
                  <Plus className="w-4 h-4 mr-2" />
                  Add Module
                </Button>
              </DialogTrigger>
              <DialogContent className="bg-white">
                <DialogHeader>
                  <DialogTitle>Add New Module</DialogTitle>
                </DialogHeader>
                <form onSubmit={handleCreateModule} className="space-y-5">
                  <div className="space-y-2">
                    <Label htmlFor="module-title" className="text-sm font-medium text-gray-900">Module Title</Label>
                    <Input
                      id="module-title"
                      type="text"
                      value={moduleFormData.title}
                      onChange={(e) => setModuleFormData({ ...moduleFormData, title: e.target.value })}
                      required
                      className="h-11"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="module-description" className="text-sm font-medium text-gray-900">Description</Label>
                    <Textarea
                      id="module-description"
                      value={moduleFormData.description}
                      onChange={(e) => setModuleFormData({ ...moduleFormData, description: e.target.value })}
                      rows={2}
                      className="min-h-[60px]"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="module-content" className="text-sm font-medium text-gray-900">Content</Label>
                    <Textarea
                      id="module-content"
                      value={moduleFormData.content}
                      onChange={(e) => setModuleFormData({ ...moduleFormData, content: e.target.value })}
                      rows={4}
                      placeholder="Module content, instructions, or materials..."
                      className="min-h-[100px]"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="module-order" className="text-sm font-medium text-gray-900">Order</Label>
                    <Input
                      id="module-order"
                      type="number"
                      min="0"
                      value={moduleFormData.order}
                      onChange={(e) => setModuleFormData({ ...moduleFormData, order: parseInt(e.target.value) || 0 })}
                      className="h-11"
                    />
                  </div>
                  <Button type="submit" className="w-full bg-gray-900 hover:bg-gray-800 text-white h-11 cursor-pointer">
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
                          className="cursor-pointer border-gray-200 dark:border-gray-800 hover:bg-gray-50"
                        >
                          <Edit className="w-4 h-4" />
                        </Button>
                        <Button
                          size="sm"
                          onClick={() => handleDeleteModule(module.id)}
                          className="bg-red-50 hover:bg-red-100 text-red-600 border-none cursor-pointer"
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
          <form onSubmit={handleEditModule} className="space-y-5">
            <div className="space-y-2">
              <Label htmlFor="edit-module-title" className="text-sm font-medium text-gray-900">Module Title</Label>
              <Input
                id="edit-module-title"
                type="text"
                value={moduleFormData.title}
                onChange={(e) => setModuleFormData({ ...moduleFormData, title: e.target.value })}
                required
                className="h-11"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="edit-module-description" className="text-sm font-medium text-gray-900">Description</Label>
              <Textarea
                id="edit-module-description"
                value={moduleFormData.description}
                onChange={(e) => setModuleFormData({ ...moduleFormData, description: e.target.value })}
                rows={2}
                className="min-h-[60px]"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="edit-module-content" className="text-sm font-medium text-gray-900">Content</Label>
              <Textarea
                id="edit-module-content"
                value={moduleFormData.content}
                onChange={(e) => setModuleFormData({ ...moduleFormData, content: e.target.value })}
                rows={4}
                placeholder="Module content, instructions, or materials..."
                className="min-h-[100px]"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="edit-module-order" className="text-sm font-medium text-gray-900">Order</Label>
              <Input
                id="edit-module-order"
                type="number"
                min="0"
                value={moduleFormData.order}
                onChange={(e) => setModuleFormData({ ...moduleFormData, order: parseInt(e.target.value) || 0 })}
                className="h-11"
              />
            </div>
            <Button type="submit" className="w-full bg-gray-900 hover:bg-gray-800 text-white h-11 cursor-pointer">
              Update Module
            </Button>
          </form>
        </DialogContent>
      </Dialog>

      {/* Enrolled Students Card */}
      <Card className="bg-white border border-gray-200">
        <CardHeader>
          <div>
            <CardTitle className="text-xl font-semibold text-gray-900">Enrolled Students</CardTitle>
            <p className="text-sm text-gray-600 mt-1">{students.length} student{students.length !== 1 ? 's' : ''} enrolled</p>
          </div>
        </CardHeader>
        <CardContent>
          {students.length > 0 ? (
            <div className="grid gap-3">
              {students.map((student) => (
                <div key={student.id} className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
                  <div>
                    <p className="font-medium text-gray-900">{student.name}</p>
                    <p className="text-sm text-gray-600 mt-1">{student.email}</p>
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
