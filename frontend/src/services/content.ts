import api from './api';
import { ApiResponse } from './auth';

export interface ContentNode {
  id: string;
  type: 'pasta' | 'arquivo' | 'youtube';
  title: string;
  description: string | null;
  class_group_id: string;
  parent_id: string | null;
  order: number;
  visibility: 'publico' | 'privado' | 'restrito';
  created_at: string;
  // Folder fields
  color?: string;
  icon?: string;
  // File fields
  drive_file_id?: string;
  drive_url?: string;
  original_name?: string;
  mime_type?: string;
  size?: number;
  // YouTube fields
  youtube_id?: string;
  full_url?: string;
  duration?: number;
  thumbnail_url?: string;
  channel?: string;
}

export interface Breadcrumb {
  id: string;
  title: string;
  type: string;
}

export const contentService = {
  async listContents(classGroupId: string, parentId?: string): Promise<ApiResponse<ContentNode[]>> {
    const params: Record<string, string> = {};
    if (parentId) {
      params.parent_id = parentId;
    }
    const response = await api.get<ApiResponse<ContentNode[]>>(
      `/api/content/class/${classGroupId}`,
      { params }
    );
    return response.data;
  },

  async getContent(contentId: string): Promise<ApiResponse<ContentNode>> {
    const response = await api.get<ApiResponse<ContentNode>>(
      `/api/content/${contentId}`
    );
    return response.data;
  },

  async getBreadcrumbs(contentId: string): Promise<ApiResponse<Breadcrumb[]>> {
    const response = await api.get<ApiResponse<Breadcrumb[]>>(
      `/api/content/${contentId}/breadcrumbs`
    );
    return response.data;
  },
};

export default contentService;
