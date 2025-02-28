import { PlatformBridge, UserSettings, ChatSession } from '@shared/components/types';

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
    if (!stored) return [];
    
    const sessions = JSON.parse(stored);
    return sessions.map((session: any) => ({
      ...session,
      createdAt: new Date(session.createdAt),
      updatedAt: new Date(session.updatedAt),
    }));
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