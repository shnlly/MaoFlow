import { PlatformBridge, UserSettings, ChatSession } from '../components/types';

// Web平台的默认实现
export class WebPlatformBridge implements PlatformBridge {
  private settings: UserSettings = {
    theme: 'light',
    language: 'zh',
  };

  async saveSettings(settings: UserSettings): Promise<void> {
    this.settings = settings;
    localStorage.setItem('user_settings', JSON.stringify(settings));
  }

  async loadSettings(): Promise<UserSettings> {
    const stored = localStorage.getItem('user_settings');
    if (stored) {
      this.settings = JSON.parse(stored);
    }
    return this.settings;
  }

  async getSessions(): Promise<ChatSession[]> {
    const stored = localStorage.getItem('chat_sessions');
    return stored ? JSON.parse(stored) : [];
  }

  async deleteSession(sessionId: string): Promise<void> {
    const sessions = await this.getSessions();
    const filtered = sessions.filter(s => s.id !== sessionId);
    localStorage.setItem('chat_sessions', JSON.stringify(filtered));
  }

  async createSession(): Promise<ChatSession> {
    const sessions = await this.getSessions();
    const newSession: ChatSession = {
      id: Date.now().toString(),
      title: '新会话',
      createdAt: new Date(),
      updatedAt: new Date(),
    };
    sessions.push(newSession);
    localStorage.setItem('chat_sessions', JSON.stringify(sessions));
    return newSession;
  }
}

// 创建平台适配器实例
let platformInstance: PlatformBridge;

export function getPlatformBridge(): PlatformBridge {
  if (!platformInstance) {
    // 根据环境判断使用哪个平台实现
    if (typeof window !== 'undefined') {
      platformInstance = new WebPlatformBridge();
    } else {
      // 这里可以根据需要添加其他平台的实现
      throw new Error('Unsupported platform');
    }
  }
  return platformInstance;
}

// 用于测试或开发时注入模拟实现
export function setPlatformBridge(bridge: PlatformBridge) {
  platformInstance = bridge;
} 