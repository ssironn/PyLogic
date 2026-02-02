import api from './api';
import { ApiResponse } from './auth';

export interface ProfileData {
  id: string;
  name: string;
  email: string;
  registration_number: string;
  created_at: string;
  last_access: string;
}

export interface ProfileUpdateRequest {
  name: string;
  email: string;
}

export interface PasswordChangeRequest {
  current_password: string;
  new_password: string;
  confirm_password: string;
}

export const profileService = {
  async get(): Promise<ApiResponse<ProfileData>> {
    const response = await api.get<ApiResponse<ProfileData>>('/api/profile');
    return response.data;
  },

  async update(data: ProfileUpdateRequest): Promise<ApiResponse<ProfileData>> {
    const response = await api.put<ApiResponse<ProfileData>>('/api/profile', data);
    return response.data;
  },

  async changePassword(data: PasswordChangeRequest): Promise<ApiResponse<null>> {
    const response = await api.put<ApiResponse<null>>('/api/profile/password', data);
    return response.data;
  },
};

export default profileService;
