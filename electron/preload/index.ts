import { contextBridge, ipcRenderer } from 'electron'

// 暴露安全的 API 到渲染进程
contextBridge.exposeInMainWorld('__ELECTRON__', true)

contextBridge.exposeInMainWorld('electronAPI', {
  // 文件操作
  readFile: (path: string) => ipcRenderer.invoke('file-read', path),
  writeFile: (path: string, content: string) => ipcRenderer.invoke('file-write', path, content),
  
  // 系统操作
  getAppVersion: () => ipcRenderer.invoke('get-app-version'),
  
  // 其他 API...
}) 