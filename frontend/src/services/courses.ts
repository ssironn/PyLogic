import api from './api';
import { ApiResponse } from './auth';

export interface ClassGroup {
  id: string;
  name: string;
  description: string;
}

export interface Enrollment {
  id: string;
  enrollment_date: string;
  status: string;
  class_group: ClassGroup;
}

export const coursesService = {
  async list(): Promise<ApiResponse<Enrollment[]>> {
    const response = await api.get<ApiResponse<Enrollment[]>>('/api/courses');
    return response.data;
  },
};

export default coursesService;
