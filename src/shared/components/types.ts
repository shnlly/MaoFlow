export interface User {
  id: string;
  name: string;
  avatar?: string;
  settings?: UserSettings;
}

export interface UserSettings {
  theme: 'light' | 'dark';
  language: string;
  apiKey?: string;
}

export interface ChatSession {
  id: string;
  title: string;
  lastMessage?: string;
  createdAt: Date;
  updatedAt: Date;
}

export interface PlatformBridge {
  saveSettings: (settings: UserSettings) => Promise<void>;
  loadSettings: () => Promise<UserSettings>;
  getSessions: () => Promise<ChatSession[]>;
  deleteSession: (sessionId: string) => Promise<void>;
  createSession: () => Promise<ChatSession>;
} 