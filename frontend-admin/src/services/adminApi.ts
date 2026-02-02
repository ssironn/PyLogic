import axios from 'axios';
import { authService } from './auth';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:9000';

const adminApi = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

adminApi.interceptors.request.use(
  (config) => {
    const token = authService.getAccessToken();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

adminApi.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      authService.logout();
      if (typeof window !== 'undefined') {
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

export interface ApiResponse<T> {
  status: 'success' | 'error';
  message?: string;
  data?: T;
  errors?: Array<{
    code: string;
    message: string;
    field?: string;
  }>;
}

// ClassGroup types
export interface ClassGroup {
  id: string;
  name: string;
  description: string;
  access_code: string;
  active: boolean;
  configs: Record<string, unknown>;
  created_at: string;
  student_count: number;
}

export interface ClassGroupCreate {
  name: string;
  description?: string;
  access_code: string;
  configs?: Record<string, unknown>;
}

export interface ClassGroupUpdate {
  name?: string;
  description?: string;
  access_code?: string;
  active?: boolean;
  configs?: Record<string, unknown>;
}

// Student types
export interface Student {
  id: string;
  name: string;
  email: string;
  registration_number: string | null;
  active: boolean;
  class_group_id: string;
  class_group_name: string | null;
  created_at: string;
  last_access: string | null;
}

export interface StudentCreate {
  name: string;
  email: string;
  password: string;
  registration_number?: string;
  class_group_id: string;
}

export interface StudentUpdate {
  name?: string;
  email?: string;
  password?: string;
  registration_number?: string;
  class_group_id?: string;
  active?: boolean;
}

// ContentNode types
export interface ContentNode {
  id: string;
  type: 'pasta' | 'arquivo' | 'youtube';
  title: string;
  description: string | null;
  class_group_id: string;
  parent_id: string | null;
  order: number;
  visibility: 'publico' | 'privado' | 'restrito';
  created_by: string;
  created_at: string;
  updated_at: string;
  meta_data: Record<string, unknown>;
  color?: string;
  icon?: string;
  allow_upload?: boolean;
  drive_file_id?: string;
  drive_url?: string;
  original_name?: string;
  mime_type?: string;
  size?: number;
  version?: number;
  upload_date?: string;
  file_hash?: string;
  youtube_id?: string;
  full_url?: string;
  duration?: number;
  thumbnail_url?: string;
  channel?: string;
  published_at?: string;
}

export interface ContentNodeCreate {
  type: 'pasta' | 'arquivo' | 'youtube';
  title: string;
  description?: string;
  class_group_id: string;
  parent_id?: string;
  order?: number;
  visibility?: 'publico' | 'privado' | 'restrito';
  meta_data?: Record<string, unknown>;
  color?: string;
  icon?: string;
  allow_upload?: boolean;
  drive_file_id?: string;
  drive_url?: string;
  original_name?: string;
  mime_type?: string;
  size?: number;
  file_hash?: string;
  youtube_id?: string;
  full_url?: string;
  duration?: number;
  thumbnail_url?: string;
  channel?: string;
  published_at?: string;
}

export interface ContentNodeUpdate {
  title?: string;
  description?: string;
  parent_id?: string | null;
  order?: number;
  visibility?: 'publico' | 'privado' | 'restrito';
  meta_data?: Record<string, unknown>;
  color?: string;
  icon?: string;
  allow_upload?: boolean;
  duration?: number;
  thumbnail_url?: string;
  channel?: string;
}

// ClassGroup API
export const classGroupsApi = {
  list: async (params?: { active?: boolean; search?: string }) => {
    const response = await adminApi.get<ApiResponse<ClassGroup[]>>('/api/admin/class-groups', { params });
    return response.data;
  },
  get: async (id: string) => {
    const response = await adminApi.get<ApiResponse<ClassGroup>>(`/api/admin/class-groups/${id}`);
    return response.data;
  },
  create: async (data: ClassGroupCreate) => {
    const response = await adminApi.post<ApiResponse<ClassGroup>>('/api/admin/class-groups', data);
    return response.data;
  },
  update: async (id: string, data: ClassGroupUpdate) => {
    const response = await adminApi.put<ApiResponse<ClassGroup>>(`/api/admin/class-groups/${id}`, data);
    return response.data;
  },
  delete: async (id: string) => {
    const response = await adminApi.delete<ApiResponse<void>>(`/api/admin/class-groups/${id}`);
    return response.data;
  },
};

// Students API
export const studentsApi = {
  list: async (params?: { class_group_id?: string; active?: boolean; search?: string }) => {
    const response = await adminApi.get<ApiResponse<Student[]>>('/api/admin/students', { params });
    return response.data;
  },
  get: async (id: string) => {
    const response = await adminApi.get<ApiResponse<Student>>(`/api/admin/students/${id}`);
    return response.data;
  },
  create: async (data: StudentCreate) => {
    const response = await adminApi.post<ApiResponse<Student>>('/api/admin/students', data);
    return response.data;
  },
  update: async (id: string, data: StudentUpdate) => {
    const response = await adminApi.put<ApiResponse<Student>>(`/api/admin/students/${id}`, data);
    return response.data;
  },
  delete: async (id: string) => {
    const response = await adminApi.delete<ApiResponse<void>>(`/api/admin/students/${id}`);
    return response.data;
  },
};

// ContentNodes API
export const contentNodesApi = {
  list: async (params?: { class_group_id?: string; parent_id?: string; type?: string; visibility?: string; search?: string }) => {
    const response = await adminApi.get<ApiResponse<ContentNode[]>>('/api/admin/content-nodes', { params });
    return response.data;
  },
  get: async (id: string) => {
    const response = await adminApi.get<ApiResponse<ContentNode>>(`/api/admin/content-nodes/${id}`);
    return response.data;
  },
  create: async (data: ContentNodeCreate) => {
    const response = await adminApi.post<ApiResponse<ContentNode>>('/api/admin/content-nodes', data);
    return response.data;
  },
  update: async (id: string, data: ContentNodeUpdate) => {
    const response = await adminApi.put<ApiResponse<ContentNode>>(`/api/admin/content-nodes/${id}`, data);
    return response.data;
  },
  delete: async (id: string) => {
    const response = await adminApi.delete<ApiResponse<void>>(`/api/admin/content-nodes/${id}`);
    return response.data;
  },
};

// YouTube API
export interface YouTubeVideoInfo {
  video_id: string;
  title: string;
  duration: number;
  channel: string;
  thumbnail_url: string;
}

export const youtubeApi = {
  getVideoInfo: async (videoId: string) => {
    const response = await adminApi.get<ApiResponse<YouTubeVideoInfo>>(`/api/admin/youtube/video-info/${videoId}`);
    return response.data;
  },
};

// Math Area types
export interface MathArea {
  id: string;
  name: string;
  description: string | null;
  icon: string | null;
  color: string | null;
  order: number;
  active: boolean;
  subarea_count: number;
  question_count: number;
  created_at: string;
  updated_at: string;
}

export interface MathAreaCreate {
  name: string;
  description?: string;
  icon?: string;
  color?: string;
  order?: number;
}

export interface MathAreaUpdate {
  name?: string;
  description?: string;
  icon?: string;
  color?: string;
  order?: number;
  active?: boolean;
}

export interface MathSubarea {
  id: string;
  math_area_id: string;
  math_area_name: string | null;
  name: string;
  description: string | null;
  order: number;
  active: boolean;
  question_count: number;
  created_at: string;
  updated_at: string;
}

export interface MathSubareaCreate {
  name: string;
  description?: string;
  order?: number;
}

export interface MathSubareaUpdate {
  name?: string;
  description?: string;
  order?: number;
  active?: boolean;
}

// Question types
export interface Question {
  id: string;
  math_area_id: string;
  math_area_name: string | null;
  math_subarea_id: string | null;
  math_subarea_name: string | null;
  title: string;
  content: string;
  content_latex: string | null;
  answer: string | null;
  answer_latex: string | null;
  explanation: string | null;
  explanation_latex: string | null;
  difficulty: 'facil' | 'medio' | 'dificil' | 'especialista';
  tags: string[];
  active: boolean;
  created_by: string;
  created_at: string;
  updated_at: string;
}

export interface QuestionCreate {
  math_area_id: string;
  math_subarea_id?: string;
  title: string;
  content: string;
  content_latex?: string;
  answer?: string;
  answer_latex?: string;
  explanation?: string;
  explanation_latex?: string;
  difficulty?: 'facil' | 'medio' | 'dificil' | 'especialista';
  tags?: string[];
}

export interface QuestionUpdate {
  math_area_id?: string;
  math_subarea_id?: string | null;
  title?: string;
  content?: string;
  content_latex?: string;
  answer?: string;
  answer_latex?: string;
  explanation?: string;
  explanation_latex?: string;
  difficulty?: 'facil' | 'medio' | 'dificil' | 'especialista';
  tags?: string[];
  active?: boolean;
}

// Math Areas API
export const mathAreasApi = {
  list: async () => {
    const response = await adminApi.get<ApiResponse<MathArea[]>>('/api/admin/math-areas');
    return response.data;
  },
  get: async (id: string) => {
    const response = await adminApi.get<ApiResponse<MathArea>>(`/api/admin/math-areas/${id}`);
    return response.data;
  },
  create: async (data: MathAreaCreate) => {
    const response = await adminApi.post<ApiResponse<MathArea>>('/api/admin/math-areas', data);
    return response.data;
  },
  update: async (id: string, data: MathAreaUpdate) => {
    const response = await adminApi.put<ApiResponse<MathArea>>(`/api/admin/math-areas/${id}`, data);
    return response.data;
  },
  delete: async (id: string) => {
    const response = await adminApi.delete<ApiResponse<void>>(`/api/admin/math-areas/${id}`);
    return response.data;
  },
  getSubareas: async (areaId: string) => {
    const response = await adminApi.get<ApiResponse<MathSubarea[]>>(`/api/admin/math-areas/${areaId}/subareas`);
    return response.data;
  },
  createSubarea: async (areaId: string, data: MathSubareaCreate) => {
    const response = await adminApi.post<ApiResponse<MathSubarea>>(`/api/admin/math-areas/${areaId}/subareas`, data);
    return response.data;
  },
};

// Math Subareas API
export const mathSubareasApi = {
  get: async (id: string) => {
    const response = await adminApi.get<ApiResponse<MathSubarea>>(`/api/admin/math-subareas/${id}`);
    return response.data;
  },
  update: async (id: string, data: MathSubareaUpdate) => {
    const response = await adminApi.put<ApiResponse<MathSubarea>>(`/api/admin/math-subareas/${id}`, data);
    return response.data;
  },
  delete: async (id: string) => {
    const response = await adminApi.delete<ApiResponse<void>>(`/api/admin/math-subareas/${id}`);
    return response.data;
  },
};

// Questions API
export const questionsApi = {
  list: async (params?: { math_area_id?: string; math_subarea_id?: string; difficulty?: string; active?: boolean; search?: string }) => {
    const response = await adminApi.get<ApiResponse<Question[]>>('/api/admin/questions', { params });
    return response.data;
  },
  get: async (id: string) => {
    const response = await adminApi.get<ApiResponse<Question>>(`/api/admin/questions/${id}`);
    return response.data;
  },
  create: async (data: QuestionCreate) => {
    const response = await adminApi.post<ApiResponse<Question>>('/api/admin/questions', data);
    return response.data;
  },
  update: async (id: string, data: QuestionUpdate) => {
    const response = await adminApi.put<ApiResponse<Question>>(`/api/admin/questions/${id}`, data);
    return response.data;
  },
  delete: async (id: string) => {
    const response = await adminApi.delete<ApiResponse<void>>(`/api/admin/questions/${id}`);
    return response.data;
  },
  convertToLatex: async (text: string) => {
    const response = await adminApi.post<ApiResponse<{ latex: string }>>('/api/admin/questions/convert-latex', { text });
    return response.data;
  },
  getAnswers: async (questionId: string) => {
    const response = await adminApi.get<ApiResponse<Answer[]>>(`/api/admin/questions/${questionId}/answers`);
    return response.data;
  },
  getAnswersStats: async (questionId: string) => {
    const response = await adminApi.get<ApiResponse<AnswerStats>>(`/api/admin/questions/${questionId}/answers/stats`);
    return response.data;
  },
};

// Answer types
export interface Answer {
  id: string;
  student_id: string;
  student_name: string | null;
  student_email: string | null;
  question_id: string;
  question_title: string | null;
  content: string;
  content_latex: string | null;
  status: 'pendente' | 'aprovado' | 'rejeitado';
  is_correct: boolean | null;
  feedback: string | null;
  score: number | null;
  reviewed_by: string | null;
  reviewed_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface AnswerReview {
  status: 'aprovado' | 'rejeitado';
  is_correct?: boolean;
  feedback?: string;
  score?: number;
}

export interface AnswerStats {
  total: number;
  pending: number;
  approved: number;
  rejected: number;
  correct: number;
}

// Answers API
export const answersApi = {
  list: async (params?: { question_id?: string; student_id?: string; status?: string }) => {
    const response = await adminApi.get<ApiResponse<Answer[]>>('/api/admin/answers', { params });
    return response.data;
  },
  get: async (id: string) => {
    const response = await adminApi.get<ApiResponse<Answer>>(`/api/admin/answers/${id}`);
    return response.data;
  },
  review: async (id: string, data: AnswerReview) => {
    const response = await adminApi.put<ApiResponse<Answer>>(`/api/admin/answers/${id}/review`, data);
    return response.data;
  },
  delete: async (id: string) => {
    const response = await adminApi.delete<ApiResponse<void>>(`/api/admin/answers/${id}`);
    return response.data;
  },
};

export default adminApi;
