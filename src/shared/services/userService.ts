import { UserSettings } from '../components/types';
import { API_BASE_URL, API_PREFIX } from '../config';

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

  constructor() {
    this.baseUrl = `${API_BASE_URL}${API_PREFIX}`;
  }

  async getDefaultUser(): Promise<User> {
    const response = await fetch(`${this.baseUrl}/user/default`);
    if (!response.ok) {
      throw new Error('Failed to fetch default user');
    }
    return response.json();
  }

  async getUserSettings(userId: string): Promise<UserSettings> {
    const response = await fetch(`${this.baseUrl}/user/${userId}/settings`);
    if (!response.ok) {
      throw new Error('Failed to fetch user settings');
    }
    return response.json();
  }

  async updateUserSettings(userId: string, settings: Partial<UserSettings>): Promise<UserSettings> {
    const response = await fetch(`${this.baseUrl}/user/${userId}/settings`, {
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