// 根据环境确定 API 基础 URL
const getBaseUrl = () => {
  if (window.__ELECTRON__) {
    return 'http://localhost:8000'; // FastAPI 默认端口
  }
  return import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
};

export const API_BASE_URL = getBaseUrl();

// API 客户端基础配置
const createApiClient = () => {
  return {
    async getStatus() {
      const response = await fetch(`${API_BASE_URL}/api/status`);
      if (!response.ok) {
        throw new Error('API request failed');
      }
      return response.json();
    },
    
    // 添加其他 API 方法
  };
};

export const apiClient = createApiClient(); 