export interface User {
  id: string;
  username: string;
  nickname: string;
  avatar?: string;
  bio?: string;
  conversation_count: number;
  message_count: number;
  last_active_at: string;
  settings?: UserSettings;
}

export interface UserSettings {
  theme: 'light' | 'dark';
  language: string;
  notifications_enabled: boolean;
  custom_settings: {
    font_size?: number;
    color?: string;
    [key: string]: any;
  };
}

export interface ChatSession {
  id: string;
  title: string;
  lastMessage?: string;
  createdAt: Date;
  updatedAt: Date;
}

export type MessageType = 'think' | 'message' | 'tool';

export interface ThoughtItem {
  id: string;
  type: 'think' | 'message' | 'tool';
  content: string;
  timestamp: string;
  message_id: string;
}

export interface Message {
  id: string;
  role: 'system' | 'user' | 'assistant' | 'function';
  content: string;
  conversation_id: string;
  created_at: string;
  updated_at: string;
  tokens?: number;
  thoughts?: ThoughtItem[];
}

export interface StreamChunk {
  type?: MessageType;
  content: string;
}

export interface PlatformBridge {
  saveSettings: (settings: UserSettings) => Promise<void>;
  loadSettings: () => Promise<UserSettings>;
  getSessions: () => Promise<ChatSession[]>;
  deleteSession: (sessionId: string) => Promise<void>;
  createSession: () => Promise<ChatSession>;
}

export interface Conversation {
  id: string;
  title: string;
  description?: string;
  user_id: string;
  model: string;
  created_at: string;
  updated_at: string;
  messages: Message[];
} 