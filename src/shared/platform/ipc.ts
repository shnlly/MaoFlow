// IPC 通道名称
export const IPC_CHANNELS = {
  SELECT_FILE: 'select-file',
  SELECTED_FILE: 'selected-file'
} as const;

// IPC 事件类型定义
export interface IPCEvents {
  [IPC_CHANNELS.SELECT_FILE]: undefined;
  [IPC_CHANNELS.SELECTED_FILE]: {
    filePath: string;
    fileName: string;
    fileContent: string;
    isDirectory: boolean;
    files?: Array<{
      name: string;
      path: string;
      content: string;
    }>;
  };
}

// 平台类型检查
export const isElectron = () => {
  // 检查是否存在 electron 对象
  if (typeof window !== 'undefined' && window.electron) {
    return true;
  }
  return false;
}; 