import React from 'react';
import { Layout } from '@shared/components/Layout';
import { App as AntApp } from 'antd';
import { setPlatformBridge } from '@shared/platform';
import { ElectronPlatformBridge } from './platform/ElectronPlatformBridge';
import 'antd/dist/reset.css';

// 设置 Electron 平台的实现
setPlatformBridge(new ElectronPlatformBridge());

const App: React.FC = () => {
  return (
    <AntApp>
      <Layout />
    </AntApp>
  );
};

export default App;
