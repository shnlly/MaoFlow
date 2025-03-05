import { ipcMain, dialog } from 'electron';
import { readFileSync, readdirSync, statSync } from 'fs';
import { join } from 'path';
import { IPC_CHANNELS } from '../../shared/platform/ipc';

// 递归读取目录内容
const readDirectory = (dirPath: string): Array<{ name: string; path: string; content: string }> => {
  const results: Array<{ name: string; path: string; content: string }> = [];
  const files = readdirSync(dirPath);

  for (const file of files) {
    const fullPath = join(dirPath, file);
    const stat = statSync(fullPath);

    if (stat.isFile()) {
      try {
        const content = readFileSync(fullPath, 'utf-8');
        results.push({
          name: file,
          path: fullPath,
          content
        });
      } catch (error) {
        console.error(`Error reading file ${fullPath}:`, error);
      }
    } else if (stat.isDirectory()) {
      // 递归读取子目录
      results.push(...readDirectory(fullPath));
    }
  }

  return results;
};

export const setupFileHandlers = () => {
  ipcMain.on(IPC_CHANNELS.SELECT_FILE, async (event) => {
    try {
      const result = await dialog.showOpenDialog({
        properties: ['openFile', 'openDirectory'],
        filters: [
          { name: 'All Files', extensions: ['*'] }
        ]
      });

      if (!result.canceled && result.filePaths.length > 0) {
        const selectedPath = result.filePaths[0];
        const stats = statSync(selectedPath);
        const isDirectory = stats.isDirectory();

        if (isDirectory) {
          // 如果选择的是目录
          const files = readDirectory(selectedPath);
          const dirName = selectedPath.split('/').pop() || 'unknown';
          
          event.reply(IPC_CHANNELS.SELECTED_FILE, {
            filePath: selectedPath,
            fileName: dirName,
            fileContent: '', // 目录没有直接内容
            isDirectory: true,
            files
          });
        } else {
          // 如果选择的是文件
          const fileContent = readFileSync(selectedPath, 'utf-8');
          const fileName = selectedPath.split('/').pop() || 'unknown';

          event.reply(IPC_CHANNELS.SELECTED_FILE, {
            filePath: selectedPath,
            fileName,
            fileContent,
            isDirectory: false
          });
        }
      }
    } catch (error) {
      console.error('Error selecting file/directory:', error);
    }
  });
}; 