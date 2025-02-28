import React from 'react'
import { Layout } from '@shared/components/Layout'
import { App as AntApp } from 'antd'
import { setPlatformBridge } from '@shared/platform'
import { WebPlatformBridge } from './platform/WebPlatformBridge'
import 'antd/dist/reset.css'

// 设置 Web 平台的实现
setPlatformBridge(new WebPlatformBridge())

const App: React.FC = () => {
  return (
    <AntApp>
      <Layout />
    </AntApp>
  )
}

export default App 