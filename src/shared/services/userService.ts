import { UserSettings } from '../components/types';

export interface User {
  id: string;
  username: string;
  nickname: string;
  avatar?: string;
  bio?: string;
  conversation_count: number;
  message_count: number;
  last_active_at: string;
}

export class UserService {
  private baseUrl: string;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
  }

  async getDefaultUser(): Promise<User> {
    const response = await fetch(`${this.baseUrl}/api/user/default`);
    if (!response.ok) {
      throw new Error('Failed to fetch default user');
    }
    return response.json();
  }

  async getUserSettings(userId: string): Promise<UserSettings> {
    const response = await fetch(`${this.baseUrl}/api/user/${userId}/settings`);
    if (!response.ok) {
      throw new Error('Failed to fetch user settings');
    }
    return response.json();
  }

  async updateUserSettings(userId: string, settings: Partial<UserSettings>): Promise<UserSettings> {
    const response = await fetch(`${this.baseUrl}/api/user/${userId}/settings`, {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(settings),
    });
    if (!response.ok) {
      throw new Error('Failed to update user settings');
    }
    return response.json();
  }
} 