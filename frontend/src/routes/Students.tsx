import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { studentsApi } from '@/lib/api'
import { type Student } from '@/lib/types'
import { Edit, Trash2, Users } from 'lucide-react'

export function Students() {
  const [students, setStudents] = useState<Student[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadStudents()
  }, [])

  const loadStudents = async () => {
    try {
      const response = await studentsApi.getAll()
      setStudents(response.data)
    } catch (error) {
      console.error('Error loading students:', error)
    } finally {
      setLoading(false)
    }
  }


  const handleDeleteStudent = async (id: number) => {
    if (confirm('Are you sure you want to delete this student?')) {
      try {
        await studentsApi.delete(id)
        loadStudents()
      } catch (error) {
        console.error('Error deleting student:', error)
      }
    }
  }

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
          Students
        </h1>
        <p className="text-gray-600 text-lg">View and manage all registered students</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {students.map((student) => (
          <Card key={student.id} className="bg-white border border-gray-200">
            <CardHeader>
              <CardTitle className="text-lg font-semibold text-gray-900">
                {student.name}
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <p className="text-sm text-gray-600">{student.email}</p>
              <div className="flex gap-2">
                <Button
                  variant="outline"
                  onClick={() => {}}
                  className="flex-1 border-gray-200 dark:border-gray-800 hover:bg-gray-50 cursor-pointer h-10"
                >
                  <Edit className="w-4 h-4 mr-1" />
                  Edit
                </Button>
                <Button
                  onClick={() => handleDeleteStudent(student.id)}
                  className="flex-1 bg-red-50 hover:bg-red-100 text-red-600 border-none cursor-pointer h-10"
                >
                  <Trash2 className="w-4 h-4 mr-1" />
                  Delete
                </Button>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {students.length === 0 && (
        <div className="text-center py-12">
          <Users className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <p className="text-gray-500">No students found. Create your first student!</p>
        </div>
      )}
    </div>
  )
}
