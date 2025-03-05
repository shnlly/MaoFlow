import { app } from 'electron';
import { join } from 'path';
import { existsSync, mkdirSync } from 'fs';

// 用户数据目录常量
export const APP_NAME = 'MaoFlow';
export const USER_DATA_DIR = process.platform === 'darwin' 
  ? join(app.getPath('home'), 'Library', 'Application Support', APP_NAME)
  : join(app.getPath('appData'), APP_NAME);

// 数据库文件路径
export const DB_FILE_NAME = 'maoflow.db';
export const DB_PATH = join(USER_DATA_DIR, DB_FILE_NAME);

// 确保用户数据目录存在
export const ensureUserDataDir = () => {
  if (!existsSync(USER_DATA_DIR)) {
    mkdirSync(USER_DATA_DIR, { recursive: true });
  }
  return USER_DATA_DIR;
}; 