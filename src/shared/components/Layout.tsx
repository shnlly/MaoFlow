import React, { useState, useEffect } from 'react';
import { Layout as AntLayout, Menu, theme, Button, Avatar, message } from 'antd';
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

const { Content, Sider } = AntLayout;

export const Layout: React.FC = () => {
  const [sessions, setSessions] = useState<ChatSession[]>([]);
  const [currentSession, setCurrentSession] = useState<ChatSession | null>(null);
  const [showSettings, setShowSettings] = useState(false);
  const [collapsed, setCollapsed] = useState(false);
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  const { token } = theme.useToken();
  const platform = getPlatformBridge();

  useEffect(() => {
    initializeUser();
  }, []);

  useEffect(() => {
    if (user) {
      loadSessions();
      loadSettings();
    }
  }, [user]);

  const initializeUser = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/user/test-user');
      if (response.ok) {
        const userData = await response.json();
        setUser(userData);
      }
    } catch (error) {
      console.error('Failed to initialize user:', error);
      message.error('初始化用户信息失败');
    } finally {
      setLoading(false);
    }
  };

  const loadSessions = async () => {
    if (!user) return;
    try {
      const loadedSessions = await platform.getSessions();
      setSessions(loadedSessions);
      if (loadedSessions.length > 0 && !currentSession) {
        setCurrentSession(loadedSessions[0]);
      }
    } catch (error) {
      console.error('Failed to load sessions:', error);
      message.error('加载会话列表失败');
    }
  };

  const loadSettings = async () => {
    if (!user) return;
    try {
      const settings = await platform.loadSettings();
      setUser(prev => prev ? {
        ...prev,
        settings,
      } : null);
    } catch (error) {
      console.error('Failed to load settings:', error);
      message.error('加载用户设置失败');
    }
  };

  const handleNewSession = async () => {
    if (!user) return;
    try {
      const newSession = await platform.createSession();
      setSessions(prev => [...prev, newSession]);
      setCurrentSession(newSession);
    } catch (error) {
      console.error('Failed to create session:', error);
      message.error('创建新会话失败');
    }
  };

  const handleDeleteSession = async (sessionId: string) => {
    try {
      await platform.deleteSession(sessionId);
      setSessions(prev => prev.filter(s => s.id !== sessionId));
      if (currentSession?.id === sessionId) {
        setCurrentSession(sessions[0] || null);
      }
    } catch (error) {
      console.error('Failed to delete session:', error);
      message.error('删除会话失败');
    }
  };

  const handleSaveSettings = async (settings: UserSettings) => {
    try {
      await platform.saveSettings(settings);
      setUser(prev => prev ? {
        ...prev,
        settings,
      } : null);
      message.success('设置保存成功');
    } catch (error) {
      console.error('Failed to save settings:', error);
      message.error('保存设置失败');
    }
  };

  if (loading) {
    return <div>加载中...</div>;
  }

  if (!user) {
    return <div>用户初始化失败</div>;
  }

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