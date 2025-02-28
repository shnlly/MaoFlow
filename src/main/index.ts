import { app, shell, BrowserWindow, ipcMain } from 'electron'
import { join } from 'path'
import { electronApp, optimizer, is } from '@electron-toolkit/utils'
import { spawn } from 'child_process'

let pythonProcess: any = null
let mainWindow: BrowserWindow | null = null

function startPythonBackend(): void {
  // 启动 Python 后端服务
  pythonProcess = spawn('python', ['-m', 'uvicorn', 'app.main:app', '--reload'], {
    cwd: join(__dirname, '../../backend')
  })

  pythonProcess.stdout.on('data', (data: any) => {
    console.log(`Python Backend: ${data}`)
  })

  pythonProcess.stderr.on('data', (data: any) => {
    console.error(`Python Backend Error: ${data}`)
  })
}

function setupIpcHandlers() {
  // 窗口控制
  ipcMain.on('window:minimize', () => {
    mainWindow?.minimize()
  })

  ipcMain.on('window:maximize', () => {
    if (mainWindow?.isMaximized()) {
      mainWindow?.unmaximize()
    } else {
      mainWindow?.maximize()
    }
  })

  ipcMain.on('window:close', () => {
    mainWindow?.close()
  })

  // 主题设置
  let currentTheme: 'light' | 'dark' = 'light'
  ipcMain.handle('settings:getTheme', () => currentTheme)
  ipcMain.handle('settings:setTheme', (_, theme: 'light' | 'dark') => {
    currentTheme = theme
  })

  // 后端服务状态
  ipcMain.handle('backend:status', () => ({
    running: pythonProcess !== null && !pythonProcess.killed
  }))

  ipcMain.handle('backend:restart', () => {
    if (pythonProcess) {
      pythonProcess.kill()
    }
    startPythonBackend()
  })
}

function createWindow(): void {
  // Create the browser window.
  mainWindow = new BrowserWindow({
    width: 900,
    height: 670,
    show: false,
    autoHideMenuBar: true,
    backgroundColor: '#f5f5f5',
    transparent: false,
    webPreferences: {
      preload: join(__dirname, '../preload/index.js'),
      sandbox: false,
      webSecurity: false,  // 禁用 web 安全限制
      allowRunningInsecureContent: true,  // 允许运行不安全内容
      contextIsolation: true,
      nodeIntegration: true
    }
  })

  mainWindow.on('ready-to-show', () => {
    mainWindow?.show()
  })

  mainWindow.webContents.setWindowOpenHandler((details) => {
    shell.openExternal(details.url)
    return { action: 'deny' }
  })

  // HMR for renderer base on electron-vite cli.
  // Load the remote URL for development or the local html file for production.
  if (is.dev && process.env['ELECTRON_RENDERER_URL']) {
    mainWindow.loadURL(process.env['ELECTRON_RENDERER_URL'])
  } else {
    mainWindow.loadFile(join(__dirname, '../renderer/index.html'))
  }
}

// This method will be called when Electron has finished
// initialization and is ready to create browser windows.
// Some APIs can only be used after this event occurs.
app.whenReady().then(() => {
  // Set app user model id for windows
  electronApp.setAppUserModelId('com.electron')

  // Default open or close DevTools by F12 in development
  // and ignore CommandOrControl + R in production.
  // see https://github.com/alex8088/electron-toolkit/tree/master/packages/utils
  app.on('browser-window-created', (_, window) => {
    optimizer.watchWindowShortcuts(window)
  })

  // 设置 IPC 处理器
  setupIpcHandlers()

  // 启动 Python 后端
  startPythonBackend()

  createWindow()

  app.on('activate', function () {
    // On macOS it's common to re-create a window in the app when the
    // dock icon is clicked and there are no other windows open.
    if (BrowserWindow.getAllWindows().length === 0) createWindow()
  })
})

// Quit when all windows are closed, except on macOS. There, it's common
// for applications and their menu bar to stay active until the user quits
// explicitly with Cmd + Q.
app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit()
  }
})

app.on('will-quit', () => {
  // 关闭 Python 后端进程
  if (pythonProcess) {
    pythonProcess.kill()
  }
})

// In this file you can include the rest of your app's specific main process
// code. You can also put them in separate files and require them here.
