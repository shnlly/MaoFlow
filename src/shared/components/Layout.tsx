import React, { useState, useEffect } from 'react';
import { Layout as AntLayout, Menu, theme, Button, Avatar } from 'antd';
import { 
  MessageOutlined, 
  SettingOutlined, 
  UserOutlined, 
  PlusOutlined,
} from '@ant-design/icons';
import { SessionList } from './SessionList';
import { UserProfile } from './UserProfile';
import { Settings } from './Settings';
import Chat from './Chat';
import { User, ChatSession, UserSettings } from './types';
import { getPlatformBridge } from '../platform';

const { Header, Content, Sider } = AntLayout;

const isElectron = 'electron' in window;

export const Layout: React.FC = () => {
  const [sessions, setSessions] = useState<ChatSession[]>([]);
  const [currentSession, setCurrentSession] = useState<ChatSession | null>(null);
  const [showSettings, setShowSettings] = useState(false);
  const [collapsed, setCollapsed] = useState(false);
  const [user, setUser] = useState<User>({
    id: '1',
    name: '用户',
    settings: {
      theme: 'light',
      language: 'zh',
    },
  });

  const { token } = theme.useToken();
  const platform = getPlatformBridge();

  useEffect(() => {
    loadSessions();
    loadSettings();
  }, []);

  const loadSessions = async () => {
    const loadedSessions = await platform.getSessions();
    setSessions(loadedSessions);
    if (loadedSessions.length > 0 && !currentSession) {
      setCurrentSession(loadedSessions[0]);
    }
  };

  const loadSettings = async () => {
    const settings = await platform.loadSettings();
    setUser(prev => ({
      ...prev,
      settings,
    }));
  };

  const handleNewSession = async () => {
    const newSession = await platform.createSession();
    setSessions(prev => [...prev, newSession]);
    setCurrentSession(newSession);
  };

  const handleDeleteSession = async (sessionId: string) => {
    await platform.deleteSession(sessionId);
    setSessions(prev => prev.filter(s => s.id !== sessionId));
    if (currentSession?.id === sessionId) {
      setCurrentSession(sessions[0] || null);
    }
  };

  const handleSaveSettings = async (settings: UserSettings) => {
    await platform.saveSettings(settings);
    setUser(prev => ({
      ...prev,
      settings,
    }));
  };

  return (
    <AntLayout style={{ 
      height: '100vh', 
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      overflow: 'hidden'
    }}>
      <AntLayout>
        <Sider 
          collapsible 
          collapsed={collapsed} 
          onCollapse={setCollapsed}
          theme="light"
          style={{
            borderRight: `1px solid ${token.colorBorder}`,
            height: '100vh',
            overflow: 'auto'
          }}
        >
          <div style={{ 
            padding: '16px',
            display: 'flex',
            justifyContent: 'center',
            borderBottom: `1px solid ${token.colorBorder}`,
          }}>
            <Button 
              type="primary" 
              icon={<PlusOutlined />}
              onClick={handleNewSession}
            >
              {!collapsed && '新建会话'}
            </Button>
          </div>
          <Menu
            mode="inline"
            selectedKeys={currentSession ? [currentSession.id] : []}
            style={{ borderRight: 0 }}
          >
            {sessions.map(session => (
              <Menu.Item 
                key={session.id}
                icon={<MessageOutlined />}
                onClick={() => setCurrentSession(session)}
              >
                {session.title}
              </Menu.Item>
            ))}
          </Menu>
          <div style={{
            position: 'absolute',
            bottom: 0,
            width: '100%',
            borderTop: `1px solid ${token.colorBorder}`,
            padding: '16px',
          }}>
            <Menu mode="inline" selectable={false}>
              <Menu.Item 
                key="settings" 
                icon={<SettingOutlined />}
                onClick={() => setShowSettings(true)}
              >
                {!collapsed && '设置'}
              </Menu.Item>
              <Menu.Item 
                key="user" 
                icon={<Avatar size="small" icon={<UserOutlined />} />}
              >
                {!collapsed && user.name}
              </Menu.Item>
            </Menu>
          </div>
        </Sider>
        <Content style={{ 
          height: '100vh',
          overflow: 'auto',
          background: token.colorBgContainer,
          display: 'flex',
          flexDirection: 'column'
        }}>
          {currentSession ? (
            <Chat sessionId={currentSession.id} />
          ) : (
            <div style={{ 
              flex: 1,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: token.colorTextSecondary,
            }}>
              请选择或创建一个会话
            </div>
          )}
        </Content>
      </AntLayout>

      {showSettings && (
        <Settings
          initialSettings={user.settings!}
          onSave={handleSaveSettings}
          onClose={() => setShowSettings(false)}
        />
      )}
    </AntLayout>
  );
}; 