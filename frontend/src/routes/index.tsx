
export function Dashboard() {
  return (
    <div className="min-h-screen bg-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">
          Student Course Enrollment Portal
        </h1>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
          <div className="bg-white border border-gray-200 rounded-lg p-6 shadow-sm">
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Students</h3>
            <p className="text-gray-600">Manage student profiles and enrollments</p>
          </div>

          <div className="bg-white border border-gray-200 rounded-lg p-6 shadow-sm">
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Courses</h3>
            <p className="text-gray-600">Create and manage course offerings</p>
          </div>

          <div className="bg-white border border-gray-200 rounded-lg p-6 shadow-sm">
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Enrollments</h3>
            <p className="text-gray-600">Track student course enrollments</p>
          </div>
        </div>

        <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
          <h2 className="text-xl font-semibold text-blue-900 mb-4">Welcome to the Portal</h2>
          <p className="text-blue-800">
            Use the navigation to manage students, courses, and enrollments. This portal allows administrators
            to create courses and students to enroll in available courses.
          </p>
        </div>
      </div>
    </div>
  )
}
