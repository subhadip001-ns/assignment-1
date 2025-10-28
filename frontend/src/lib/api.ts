import axios from 'axios';
import {
  Student,
  Course,
  Enrollment,
  EnrollmentWithDetails,
  CreateStudentRequest,
  UpdateStudentRequest,
  CreateCourseRequest,
  UpdateCourseRequest,
  CreateEnrollmentRequest,
} from './types';

const API_BASE_URL = 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Students API
export const studentsApi = {
  getAll: () => api.get<Student[]>('/students/'),
  getById: (id: number) => api.get<Student>(`/students/${id}`),
  create: (data: CreateStudentRequest) => api.post<Student>('/students/', data),
  update: (id: number, data: UpdateStudentRequest) => api.put<Student>(`/students/${id}`, data),
  delete: (id: number) => api.delete(`/students/${id}`),
  getCourses: (id: number) => api.get<Course[]>(`/students/${id}/courses`),
};

// Courses API
export const coursesApi = {
  getAll: () => api.get<Course[]>('/courses/'),
  getById: (id: number) => api.get<Course>(`/courses/${id}`),
  create: (data: CreateCourseRequest) => api.post<Course>('/courses/', data),
  update: (id: number, data: UpdateCourseRequest) => api.put<Course>(`/courses/${id}`, data),
  delete: (id: number) => api.delete(`/courses/${id}`),
  getStudents: (id: number) => api.get<Student[]>(`/courses/${id}/students`),
};

// Enrollments API
export const enrollmentsApi = {
  getAll: () => api.get<EnrollmentWithDetails[]>('/enrollments/'),
  getById: (id: number) => api.get<EnrollmentWithDetails>(`/enrollments/${id}`),
  create: (data: CreateEnrollmentRequest) => api.post<Enrollment>('/enrollments/', data),
  delete: (id: number) => api.delete(`/enrollments/${id}`),
  deleteByStudentAndCourse: (studentId: number, courseId: number) =>
    api.delete(`/enrollments/student/${studentId}/course/${courseId}`),
};
