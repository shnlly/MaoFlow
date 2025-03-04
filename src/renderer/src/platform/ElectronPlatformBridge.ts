import { PlatformBridge, UserSettings, ChatSession, User } from '../../../shared/components/types';
import { API_BASE_URL, API_PREFIX } from '../../../shared/config';

declare global {
  interface Window {
    api: {
      window: {
        minimize: () => void;
        maximize: () => void;
        close: () => void;
      };
      settings: {
        getTheme: () => Promise<'light' | 'dark'>;
        setTheme: (theme: 'light' | 'dark') => Promise<void>;
      };
      backend: {
        getStatus: () => Promise<{ running: boolean }>;
        restart: () => Promise<void>;
      };
    };
  }
}

export class ElectronPlatformBridge implements PlatformBridge {
  private apiBaseUrl: string;
  private testUserId: number | null = null;

  constructor() {
    this.apiBaseUrl = `${API_BASE_URL}${API_PREFIX}`;
    // 初始化时获取测试用户ID
    this.initTestUser();
  }

  private async initTestUser() {
    try {
      const response = await fetch(`${this.apiBaseUrl}/user/test-user`);
      if (response.ok) {
        const user: User = await response.json();
        this.testUserId = user.id;
      }
    } catch (error) {
      console.error('Failed to initialize test user:', error);
    }
  }

  async loadSettings(): Promise<UserSettings> {
    if (!this.testUserId) {
      await this.initTestUser();
    }
    try {
      const response = await fetch(`${this.apiBaseUrl}/settings/${this.testUserId}`);
      if (!response.ok) {
        throw new Error('Failed to load settings');
      }
      return await response.json();
    } catch (error) {
      console.error('Failed to load settings:', error);
      // 返回默认设置
      return {
        theme: 'light',
        language: 'zh',
      };
    }
  }

  async saveSettings(settings: UserSettings): Promise<void> {
    if (!this.testUserId) {
      await this.initTestUser();
    }
    try {
      await fetch(`${this.apiBaseUrl}/settings/${this.testUserId}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(settings),
      });
    } catch (error) {
      console.error('Failed to save settings:', error);
      throw error;
    }
  }

  async getSessions(): Promise<ChatSession[]> {
    if (!this.testUserId) {
      await this.initTestUser();
    }
    try {
      const response = await fetch(`${this.apiBaseUrl}/chat/sessions/${this.testUserId}`);
      if (!response.ok) {
        throw new Error('Failed to get sessions');
      }
      return await response.json();
    } catch (error) {
      console.error('Failed to get sessions:', error);
      return [];
    }
  }

  async deleteSession(sessionId: string): Promise<void> {
    try {
      await fetch(`${this.apiBaseUrl}/chat/sessions/${sessionId}`, {
        method: 'DELETE',
      });
    } catch (error) {
      console.error('Failed to delete session:', error);
      throw error;
    }
  }

  async createSession(): Promise<ChatSession> {
    if (!this.testUserId) {
      await this.initTestUser();
    }
    try {
      const response = await fetch(`${this.apiBaseUrl}/chat/sessions`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_id: this.testUserId,
          title: '新会话',
          model: 'gpt-3.5-turbo',
        }),
      });
      if (!response.ok) {
        throw new Error('Failed to create session');
      }
      return await response.json();
    } catch (error) {
      console.error('Failed to create session:', error);
      throw error;
    }
  }

  // 后端服务状态管理
  async checkBackendStatus() {
    return window.api.backend.getStatus();
  }

  async restartBackend() {
    return window.api.backend.restart();
  }
} 