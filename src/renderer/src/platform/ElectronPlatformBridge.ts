import { PlatformBridge, UserSettings } from '@shared/components/types';

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
  // 基本设置
  async loadSettings(): Promise<UserSettings> {
    const theme = await window.api.settings.getTheme();
    return {
      theme,
      language: 'zh'
    };
  }

  async saveSettings(settings: UserSettings): Promise<void> {
    await window.api.settings.setTheme(settings.theme);
  }

  // 会话管理 - 直接使用后端 API
  async getSessions() {
    const response = await fetch('http://localhost:8000/api/sessions');
    const data = await response.json();
    return data.map((session: any) => ({
      ...session,
      createdAt: new Date(session.createdAt),
      updatedAt: new Date(session.updatedAt),
    }));
  }

  async createSession() {
    const response = await fetch('http://localhost:8000/api/sessions', {
      method: 'POST'
    });
    const session = await response.json();
    return {
      ...session,
      createdAt: new Date(session.createdAt),
      updatedAt: new Date(session.updatedAt),
    };
  }

  async deleteSession(sessionId: string) {
    await fetch(`http://localhost:8000/api/sessions/${sessionId}`, {
      method: 'DELETE'
    });
  }

  // 后端服务状态管理
  async checkBackendStatus() {
    return window.api.backend.getStatus();
  }

  async restartBackend() {
    return window.api.backend.restart();
  }
} 