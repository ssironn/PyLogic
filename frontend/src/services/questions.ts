import axios from 'axios';
import { authService } from './auth';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:9000';

const questionsApi = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

questionsApi.interceptors.request.use(
  (config) => {
    const token = authService.getAccessToken();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

export interface ApiResponse<T> {
  status: 'success' | 'error';
  message?: string;
  data?: T;
}

export interface MathArea {
  id: string;
  name: string;
  icon: string | null;
  color: string | null;
}

export interface MathSubarea {
  id: string;
  name: string;
}

export interface MyAnswer {
  id: string;
  content: string;
  content_latex: string | null;
  status: 'pendente' | 'aprovado' | 'rejeitado';
  is_correct: boolean | null;
  feedback: string | null;
  score: number | null;
  created_at: string;
}

export interface Question {
  id: string;
  math_area_id: string;
  math_area_name: string | null;
  math_subarea_id: string | null;
  math_subarea_name: string | null;
  title: string;
  content: string;
  content_latex: string | null;
  difficulty: 'facil' | 'medio' | 'dificil' | 'especialista';
  tags: string[];
  created_at: string;
  my_answer: MyAnswer | null;
  approved_answers_count: number;
}

export interface ApprovedAnswer {
  id: string;
  student_name: string;
  content: string;
  content_latex: string | null;
  is_correct: boolean | null;
  score: number | null;
  created_at: string;
}

export interface AnswerSubmission {
  content: string;
  content_latex?: string;
}

export interface SubmittedAnswer {
  id: string;
  content: string;
  content_latex: string | null;
  status: string;
  created_at: string;
  updated_at?: string;
}

export const questionsService = {
  async listQuestions(params?: {
    math_area_id?: string;
    math_subarea_id?: string;
    difficulty?: string;
    search?: string;
  }): Promise<Question[]> {
    const response = await questionsApi.get<ApiResponse<Question[]>>('/api/questions', { params });
    if (response.data.status === 'success' && response.data.data) {
      return response.data.data;
    }
    return [];
  },

  async getQuestion(id: string): Promise<Question | null> {
    const response = await questionsApi.get<ApiResponse<Question>>(`/api/questions/${id}`);
    if (response.data.status === 'success' && response.data.data) {
      return response.data.data;
    }
    return null;
  },

  async submitAnswer(questionId: string, data: AnswerSubmission): Promise<SubmittedAnswer | null> {
    const response = await questionsApi.post<ApiResponse<SubmittedAnswer>>(
      `/api/questions/${questionId}/answer`,
      data
    );
    if (response.data.status === 'success' && response.data.data) {
      return response.data.data;
    }
    return null;
  },

  async getApprovedAnswers(questionId: string): Promise<ApprovedAnswer[]> {
    const response = await questionsApi.get<ApiResponse<ApprovedAnswer[]>>(
      `/api/questions/${questionId}/approved-answers`
    );
    if (response.data.status === 'success' && response.data.data) {
      return response.data.data;
    }
    return [];
  },

  async listMathAreas(): Promise<MathArea[]> {
    const response = await questionsApi.get<ApiResponse<MathArea[]>>('/api/questions/math-areas');
    if (response.data.status === 'success' && response.data.data) {
      return response.data.data;
    }
    return [];
  },

  async listSubareas(areaId: string): Promise<MathSubarea[]> {
    const response = await questionsApi.get<ApiResponse<MathSubarea[]>>(
      `/api/questions/math-areas/${areaId}/subareas`
    );
    if (response.data.status === 'success' && response.data.data) {
      return response.data.data;
    }
    return [];
  },

  async convertToLatex(text: string): Promise<string> {
    const response = await questionsApi.post<ApiResponse<{ latex: string }>>(
      '/api/questions/convert-latex',
      { text }
    );
    if (response.data.status === 'success' && response.data.data) {
      return response.data.data.latex;
    }
    return text;
  },
};
