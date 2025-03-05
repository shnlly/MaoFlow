import { contextBridge, ipcRenderer } from 'electron'
import { electronAPI } from '@electron-toolkit/preload'

// 定义渲染进程可用的 API
const api = {
  // 窗口控制
  window: {
    minimize: () => ipcRenderer.send('window:minimize'),
    maximize: () => ipcRenderer.send('window:maximize'),
    close: () => ipcRenderer.send('window:close')
  },

  // 应用设置
  settings: {
    getTheme: () => ipcRenderer.invoke('settings:getTheme'),
    setTheme: (theme: 'light' | 'dark') => ipcRenderer.invoke('settings:setTheme', theme)
  },

  // 后端服务状态
  backend: {
    getStatus: () => ipcRenderer.invoke('backend:status'),
    restart: () => ipcRenderer.invoke('backend:restart')
  }
}

// 合并 electron API
const exposedElectronAPI = {
  ...electronAPI,
  ipcRenderer: {
    invoke: (channel: string, ...args: any[]) => ipcRenderer.invoke(channel, ...args),
    send: (channel: string, ...args: any[]) => ipcRenderer.send(channel, ...args),
    on: (channel: string, func: (...args: any[]) => void) => {
      ipcRenderer.on(channel, (event, ...args) => func(...args));
    },
    once: (channel: string, func: (...args: any[]) => void) => {
      ipcRenderer.once(channel, (event, ...args) => func(...args));
    },
    removeListener: (channel: string, func: (...args: any[]) => void) => {
      ipcRenderer.removeListener(channel, func);
    }
  }
};

// 只在启用上下文隔离时暴露 API
if (process.contextIsolated) {
  try {
    contextBridge.exposeInMainWorld('electron', exposedElectronAPI)
    contextBridge.exposeInMainWorld('api', api)
  } catch (error) {
    console.error(error)
  }
} else {
  // @ts-ignore (define in dts)
  window.electron = exposedElectronAPI
  // @ts-ignore (define in dts)
  window.api = api
}
