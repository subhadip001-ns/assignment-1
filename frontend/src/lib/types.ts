// Types matching the backend API schemas

export interface Student {
  id: number;
  name: string;
  email: string;
}

export interface Course {
  id: number;
  name: string;
  description?: string;
  instructor: string;
}

export interface Enrollment {
  id: number;
  student_id: number;
  course_id: number;
}

export interface EnrollmentWithDetails {
  id: number;
  student: Student;
  course: Course;
}

export interface StudentWithCourses extends Student {
  courses: Course[];
}

export interface CourseWithStudents extends Course {
  students: Student[];
}

// API request types
export interface CreateStudentRequest {
  name: string;
  email: string;
}

export interface UpdateStudentRequest {
  name?: string;
  email?: string;
}

export interface CreateCourseRequest {
  name: string;
  description?: string;
  instructor: string;
}

export interface UpdateCourseRequest {
  name?: string;
  description?: string;
  instructor?: string;
}

export interface CreateEnrollmentRequest {
  student_id: number;
  course_id: number;
}

export interface Module {
  id: number;
  course_id: number;
  title: string;
  description?: string;
  content?: string;
  order: number;
}

export interface CreateModuleRequest {
  course_id: number;
  title: string;
  description?: string;
  content?: string;
  order?: number;
}

export interface UpdateModuleRequest {
  title?: string;
  description?: string;
  content?: string;
  order?: number;
}
