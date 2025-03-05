import { join } from 'path';
import { copyFileSync, existsSync } from 'fs';
import { app } from 'electron';
import { DB_PATH, ensureUserDataDir } from '../shared/platform/paths';

// 初始化数据库
export const initDatabase = () => {
  // 确保用户数据目录存在
  ensureUserDataDir();

  // 如果用户目录中不存在数据库文件，则从资源目录复制
  if (!existsSync(DB_PATH)) {
    const resourceDbPath = app.isPackaged
      ? join(process.resourcesPath, 'backend', 'maoflow.db')
      : join(__dirname, '../../backend/maoflow.db');

    if (existsSync(resourceDbPath)) {
      try {
        copyFileSync(resourceDbPath, DB_PATH);
        console.log('数据库文件已初始化到用户目录:', DB_PATH);
      } catch (error) {
        console.error('复制数据库文件失败:', error);
      }
    } else {
      console.log('资源目录中不存在数据库文件，将在首次运行时自动创建');
    }
  }

  return DB_PATH;
}; 