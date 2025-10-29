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

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;
console.log(API_BASE_URL);

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

// AI Chat API
export interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
}

export interface ChatRequest {
  message: string
  chat_history?: ChatMessage[]
}

export interface ChatResponse {
  response: string
}

export const aiApi = {
  // Regular chat (non-streaming)
  chat: (message: string, chatHistory?: ChatMessage[]) =>
    api.post<ChatResponse>('/ai/chat', {
      message,
      chat_history: chatHistory || []
    }),

  // Streaming chat
  streamChat: async (
    message: string,
    chatHistory: ChatMessage[],
    onChunk: (chunk: string) => void
  ) => {
    const response = await fetch(`${API_BASE_URL}/ai/chat/stream`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('token')}`,
      },
      body: JSON.stringify({
        message,
        chat_history: chatHistory,
      }),
    })

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    const reader = response.body?.getReader()
    if (!reader) {
      throw new Error('Failed to get response reader')
    }

    const decoder = new TextDecoder()
    let buffer = ''

    while (true) {
      const { done, value } = await reader.read()
      if (done) break

      buffer += decoder.decode(value, { stream: true })
      const lines = buffer.split('\n')
      buffer = lines.pop() || '' // Keep incomplete line in buffer

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const data = line.slice(6) // Remove 'data: ' prefix
          if (data === '[DONE]') {
            return
          }
          onChunk(data)
        }
      }
    }
  },
};
