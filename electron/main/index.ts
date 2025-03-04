import { app, shell, BrowserWindow, ipcMain, Menu } from 'electron'
import { join } from 'path'
import { electronApp, optimizer, is } from '@electron-toolkit/utils'
import { spawn } from 'child_process'
import icon from '../../resources/icon.png?asset'

let pythonProcess: any = null
let mainWindow: BrowserWindow | null = null

function startPythonBackend(): void {
  // 启动 Python 后端服务
  const pythonPath = is.dev ? 'python' : join(process.resourcesPath, 'backend', 'maoflow')
  const args = [
    '-m', 
    'uvicorn', 
    'app.main:app', 
    '--host', 
    'localhost',
    '--port', 
    '17349',
    '--reload'
  ]
  
  const cwd = is.dev ? join(__dirname, '../../backend') : join(process.resourcesPath, 'backend')
  console.log('Starting Python backend with:', {
    pythonPath,
    args,
    cwd
  })
  
  pythonProcess = spawn(pythonPath, args, { cwd })

  pythonProcess.stdout.on('data', (data: any) => {
    console.log(`Python Backend: ${data}`)
  })

  pythonProcess.stderr.on('data', (data: any) => {
    console.error(`Python Backend Error: ${data}`)
  })

  pythonProcess.on('error', (error: any) => {
    console.error('Failed to start Python backend:', error)
  })

  pythonProcess.on('exit', (code: number, signal: string) => {
    console.log(`Python backend exited with code ${code} and signal ${signal}`)
  })
}

function createWindow(): void {
  // 创建浏览器窗口
  mainWindow = new BrowserWindow({
    width: 900,
    height: 670,
    show: false,
    ...(process.platform === 'linux' ? { icon } : {}),
    webPreferences: {
      preload: join(__dirname, '../preload/index.js'),
      sandbox: false,
      webSecurity: false,
      allowRunningInsecureContent: true,
      contextIsolation: true
    }
  })

  // 创建应用菜单
  const template = [
    {
      label: '文件',
      submenu: [
        {
          label: '退出',
          accelerator: 'CmdOrCtrl+Q',
          click: () => {
            app.quit()
          }
        }
      ]
    },
    {
      label: '视图',
      submenu: [
        {
          label: '刷新',
          accelerator: 'CmdOrCtrl+R',
          click: () => {
            if (mainWindow) {
              mainWindow.webContents.reload()
            }
          }
        },
        {
          label: '强制刷新',
          accelerator: 'CmdOrCtrl+Shift+R',
          click: () => {
            if (mainWindow) {
              mainWindow.webContents.reloadIgnoringCache()
            }
          }
        },
        { type: 'separator' },
        {
          label: '开发者工具',
          accelerator: 'CmdOrCtrl+Shift+I',
          click: () => {
            if (mainWindow) {
              mainWindow.webContents.toggleDevTools()
            }
          }
        },
        { type: 'separator' },
        {
          label: '重启应用',
          accelerator: 'CmdOrCtrl+Shift+R',
          click: () => {
            app.relaunch()
            app.exit(0)
          }
        }
      ]
    }
  ]
  const menu = Menu.buildFromTemplate(template as any)
  Menu.setApplicationMenu(menu)

  // 注册快捷键处理
  mainWindow.webContents.on('before-input-event', (event, input) => {
    if (input.control || input.meta) {
      if (input.key === 'r' && !input.shift) {
        mainWindow?.webContents.reload()
        event.preventDefault()
      } else if (input.key === 'r' && input.shift) {
        mainWindow?.webContents.reloadIgnoringCache()
        event.preventDefault()
      } else if (input.key === 'i' && input.shift) {
        mainWindow?.webContents.toggleDevTools()
        event.preventDefault()
      }
    }
  })

  mainWindow.on('ready-to-show', () => {
    mainWindow?.show()
  })

  mainWindow.webContents.setWindowOpenHandler((details) => {
    shell.openExternal(details.url)
    return { action: 'deny' }
  })

  // 根据环境加载不同的 URL
  if (is.dev && process.env['ELECTRON_RENDERER_URL']) {
    mainWindow.loadURL(process.env['ELECTRON_RENDERER_URL'])
    // 开发环境下自动打开开发者工具
    mainWindow.webContents.openDevTools()
  } else {
    mainWindow.loadFile(join(__dirname, '../renderer/index.html'))
  }
}

app.whenReady().then(() => {
  electronApp.setAppUserModelId('com.electron')

  // 启动 Python 后端
  startPythonBackend()

  app.on('browser-window-created', (_, window) => {
    optimizer.watchWindowShortcuts(window)
  })

  createWindow()

  app.on('activate', function () {
    if (BrowserWindow.getAllWindows().length === 0) createWindow()
  })
})

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

// 添加重启应用的 IPC 处理
ipcMain.handle('restart-app', () => {
  app.relaunch()
  app.exit(0)
}) 