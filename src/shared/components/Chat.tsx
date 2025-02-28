import React, { useState, useEffect } from 'react';
import { Bubble, Sender, Prompts, ThoughtChain } from '@ant-design/x';
import { App, Flex, Typography, Card } from 'antd';
import { CopyOutlined, RobotOutlined, UserOutlined, LoadingOutlined } from '@ant-design/icons';
import ReactMarkdown from 'react-markdown';

window.console.log('=== Chat 组件模块加载 ===');

// 消息类型定义
type MessageType = 'think' | 'message' | 'tool';

interface Message {
  content: string;
  role: 'user' | 'assistant';
  type?: MessageType;
}

// 流式响应数据结构
interface StreamChunk {
  type?: MessageType;
  content: string;
}

// 消息类型配置
const MESSAGE_TYPE_CONFIG = {
  think: {
    title: '思考过程',
    icon: <LoadingOutlined />,
    render: (content: string) => (
      <ThoughtChain
        items={[
          {
            title: '思考过程',
            status: 'pending',
            icon: <LoadingOutlined />,
            content: content,
          }
        ]}
      />
    )
  },
  message: {
    title: '回答',
    render: (content: string) => <ReactMarkdown>{content}</ReactMarkdown>
  },
  tool: {
    title: '工具使用',
    render: (content: string) => (
      <Card title="工具调用" style={{ marginTop: 8, background: '#fafafa' }}>
        <ReactMarkdown>{content}</ReactMarkdown>
      </Card>
    )
  }
};

const suggestedPrompts = [
  {
    key: '1',
    icon: <RobotOutlined style={{ color: '#1677ff' }} />,
    description: '你能做什么？',
  },
  {
    key: '2',
    icon: <RobotOutlined style={{ color: '#1677ff' }} />,
    description: '给我讲个故事',
  },
  {
    key: '3',
    icon: <RobotOutlined style={{ color: '#1677ff' }} />,
    description: '帮我写一段代码',
  },
];

const Chat: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const { message } = App.useApp();

  useEffect(() => {
    window.console.log('=== 消息列表已更新 ===', messages);
  }, [messages]);

  const copyMessage = (content: string) => {
    navigator.clipboard.writeText(content).then(() => {
      message.success('复制成功！');
    });
  };

  const renderMessageContent = (msg: Message) => {
    if (msg.role === 'user') {
      return <Typography.Text>{msg.content}</Typography.Text>;
    }

    const typeConfig = MESSAGE_TYPE_CONFIG[msg.type || 'message'];
    return typeConfig.render(msg.content);
  };

  const renderMessage = (msg: Message) => {
    const isUser = msg.role === 'user';
    return (
      <Flex vertical gap="small">
        <Flex align="start" justify={isUser ? 'flex-end' : 'flex-start'}>
          <Bubble
            content={msg.content}
            placement={isUser ? 'end' : 'start'}
            variant="filled"
            shape="round"
            style={{ maxWidth: '80%' }}
            classNames={{
              content: isUser ? 'user-message' : 'ai-message'
            }}
            avatar={
              isUser ? (
                <UserOutlined style={{ 
                  fontSize: '18px',
                  padding: '8px',
                  backgroundColor: '#e6f4ff',
                  borderRadius: '50%',
                  color: '#1677ff' 
                }} />
              ) : (
                <RobotOutlined style={{ 
                  fontSize: '18px',
                  padding: '8px',
                  backgroundColor: '#f6ffed',
                  borderRadius: '50%',
                  color: '#52c41a' 
                }} />
              )
            }
          >
            {renderMessageContent(msg)}
            {msg.role === 'assistant' && (
              <CopyOutlined
                style={{ 
                  marginLeft: 8, 
                  cursor: 'pointer',
                  opacity: 0.7,
                  fontSize: '14px',
                  color: isUser ? '#fff' : '#666',
                  transition: 'opacity 0.2s'
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.opacity = '1';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.opacity = '0.7';
                }}
                onClick={() => copyMessage(msg.content)}
              />
            )}
          </Bubble>
        </Flex>
      </Flex>
    );
  };

  const handleRequest = async (text: string) => {
    try {
      setIsLoading(true);
      setMessages(prev => [...prev, { content: text, role: 'user' }]);
      
      const response = await fetch(`http://localhost:8000/api/chat?query=${encodeURIComponent(text)}`, {
        method: 'GET',
      });

      if (!response.ok) {
        throw new Error('请求失败');
      }

      const reader = response.body?.getReader();
      if (!reader) {
        throw new Error('无法读取响应');
      }

      let currentMessage: Message = { 
        content: '', 
        role: 'assistant',
        type: 'think'
      };

      setMessages(prev => [...prev, currentMessage]);

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = new TextDecoder().decode(value);
        const lines = chunk.split('\n');
        
        for (const line of lines) {
          if (line.startsWith('data: ') && line.length > 6) {
            try {
              const data: StreamChunk = JSON.parse(line.slice(6));
              
              currentMessage = {
                ...currentMessage,
                content: data.content,
                type: data.type || currentMessage.type
              };

              setMessages(prev => {
                const newMessages = [...prev];
                newMessages[newMessages.length - 1] = currentMessage;
                return newMessages;
              });
            } catch (e) {
              console.error('解析响应数据失败:', e);
            }
          }
        }
      }
    } catch (error) {
      console.error('Error:', error);
      message.error('发生错误，请稍后重试');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <App>
      <Flex vertical gap="middle" style={{ 
        height: '100vh', 
        padding: '20px',
        backgroundColor: '#f5f5f5'
      }}>
        <div style={{ 
          flex: 1, 
          overflow: 'auto',
          padding: '20px',
          borderRadius: '8px',
          backgroundColor: '#fff',
          boxShadow: '0 2px 8px rgba(0,0,0,0.06)'
        }}>
          {messages.map((msg, index) => (
            <div key={index} style={{ 
              marginBottom: 24,
              animation: 'fadeIn 0.3s ease-in-out'
            }}>
              {renderMessage(msg)}
            </div>
          ))}
        </div>
        
        {messages.length === 0 && (
          <div onClick={(e) => {
            const target = e.target as HTMLElement;
            const promptItem = target.closest('[data-key]');
            if (promptItem) {
              const key = promptItem.getAttribute('data-key');
              const prompt = suggestedPrompts.find(p => p.key === key);
              if (prompt) {
                handleRequest(prompt.description);
              }
            }
          }}>
            <Prompts
              title="👋 你可以这样问我："
              items={suggestedPrompts}
              vertical
              style={{ marginBottom: 20 }}
            />
          </div>
        )}

        {isLoading && (
          <ThoughtChain
            items={[
              {
                title: 'AI 正在思考',
                status: 'pending',
                icon: <LoadingOutlined />,
                content: '正在生成回答...',
              },
            ]}
          />
        )}

        <Sender 
          onSubmit={handleRequest}
          disabled={isLoading}
          placeholder={isLoading ? "AI 正在思考中..." : "请输入您的问题"}
          loading={isLoading}
          onCancel={() => {
            setIsLoading(false);
            message.info('已取消发送');
          }}
        />
      </Flex>
    </App>
  );
};

export default Chat; 