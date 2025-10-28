import axios from 'axios';
import type {
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

export interface LoginRequest {
  email: string;
  password: string;
  role: 'admin' | 'student';
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  user: {
    id: number;
    name: string;
    email: string;
    role: string;
  };
}

export interface LogoutResponse {
  message: string;
  user: {
    id: number;
    name: string;
    email: string;
    role: string;
  };
}

const API_BASE_URL = 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add request interceptor to include auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Add response interceptor to handle auth errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token is invalid or expired, clear local storage
      localStorage.removeItem('user');
      localStorage.removeItem('token');
      // Optionally redirect to login page here
    }
    return Promise.reject(error);
  }
);

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

// Authentication API
export const authApi = {
  login: (data: LoginRequest) => api.post<LoginResponse>('/auth/login', data),
  logout: () => api.post<LogoutResponse>('/auth/logout'),
  getCurrentUser: () => api.get('/auth/me'),
};
