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
import { API_BASE_URL, API_PREFIX } from '../config';

const { Content, Sider } = AntLayout;

export const Layout: React.FC = () => {
  const [sessions, setSessions] = useState<ChatSession[]>([]);
  const [currentSession, setCurrentSession] = useState<ChatSession | null>(null);
  const [showSettings, setShowSettings] = useState(false);
  const [collapsed, setCollapsed] = useState(false);
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [models, setModels] = useState<any[]>([]);
  const [defaultModel, setDefaultModel] = useState<string | null>(null);

  const { token } = theme.useToken();
  const platform = getPlatformBridge();

  useEffect(() => {
    initializeUser();
  }, []);

  useEffect(() => {
    if (user?.id) {
      loadSessions();
      loadModels();
    }
  }, [user?.id]);

  const initializeUser = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}${API_PREFIX}/user/test-user`);
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
      const response = await fetch(`${API_BASE_URL}${API_PREFIX}/conversations/user/${user.id}`);
      if (!response.ok) throw new Error('Failed to load sessions');
      const loadedSessions = await response.json();
      setSessions(loadedSessions);
      if (loadedSessions.length > 0 && !currentSession) {
        setCurrentSession(loadedSessions[0]);
      }
    } catch (error) {
      console.error('Failed to load sessions:', error);
      message.error('加载会话列表失败');
    }
  };

  const loadModels = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}${API_PREFIX}/models`);
      if (!response.ok) throw new Error('Failed to load models');
      const data = await response.json();
      setModels(data.items);
      if (data.items.length > 0) {
        setDefaultModel(data.items[0].id);
      }
    } catch (error) {
      console.error('Failed to load models:', error);
      message.error('加载模型列表失败');
    }
  };

  const loadSettings = async () => {
    if (!user?.id) return;
    try {
      const response = await fetch(`http://localhost:8000/api/user/${user.id}/settings`);
      if (!response.ok) throw new Error('Failed to load settings');
      const settings = await response.json();
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
    if (!user || !defaultModel) {
      message.error('用户未初始化或未加载默认模型');
      return;
    }
    
    try {
      console.log('Creating new session with model:', defaultModel);
      const newSessionData = {
        title: "新会话",
        user_id: user.id,
        model_id: defaultModel,
        description: "",
        system_prompt: "",
        status: "active",
        meta_info: {
          tags: [],
          custom_settings: {}
        }
      };
      
      console.log('Sending request to:', `${API_BASE_URL}${API_PREFIX}/conversations`);
      console.log('Request data:', JSON.stringify(newSessionData, null, 2));
      
      const response = await fetch(`${API_BASE_URL}${API_PREFIX}/conversations`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(newSessionData),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => null);
        console.error('Server response:', {
          status: response.status,
          statusText: response.statusText,
          data: errorData
        });
        throw new Error(`Failed to create session: ${response.statusText}`);
      }

      const newSession = await response.json();
      console.log('New session created:', newSession);
      
      setSessions(prev => [...prev, newSession]);
      setCurrentSession(newSession);
      message.success('新会话创建成功');
    } catch (error) {
      console.error('Failed to create session:', error);
      message.error(`创建新会话失败: ${error instanceof Error ? error.message : '未知错误'}`);
    }
  };

  const handleDeleteSession = async (sessionId: string) => {
    try {
      const response = await fetch(`${API_BASE_URL}${API_PREFIX}/conversations/${sessionId}`, {
        method: 'DELETE',
      });
      if (!response.ok) throw new Error('Failed to delete session');
      setSessions(prev => prev.filter(s => s.id !== sessionId));
      if (currentSession?.id === sessionId) {
        setCurrentSession(sessions[0] || null);
      }
      message.success('会话已删除');
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
            items={sessions.map(session => ({
              key: session.id,
              icon: <MessageOutlined />,
              label: session.title,
              onClick: () => setCurrentSession(session)
            }))}
          />
          <div style={{
            position: 'absolute',
            bottom: 0,
            width: '100%',
            borderTop: `1px solid ${token.colorBorder}`,
            padding: '16px',
          }}>
            <Menu 
              mode="inline" 
              selectable={false}
              items={[
                {
                  key: 'settings',
                  icon: <SettingOutlined />,
                  label: !collapsed && '设置',
                  onClick: () => setShowSettings(true)
                },
                {
                  key: 'user',
                  icon: <Avatar size="small" icon={<UserOutlined />} />,
                  label: !collapsed && user.nickname
                }
              ]}
            />
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