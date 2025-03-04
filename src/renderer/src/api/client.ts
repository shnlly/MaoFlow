import { API_BASE_URL, API_PREFIX } from '@shared/config';

// API 客户端基础配置
const createApiClient = () => {
  return {
    async getStatus() {
      const response = await fetch(`${API_BASE_URL}${API_PREFIX}/status`);
      if (!response.ok) {
        throw new Error('API request failed');
      }
      return response.json();
    },
    
    // 添加其他 API 方法
  };
};

export const apiClient = createApiClient(); 