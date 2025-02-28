import React, { useState, useEffect } from 'react';
import { Bubble, Sender, Prompts, ThoughtChain } from '@ant-design/x';
import { App, Flex, Typography, Card } from 'antd';
import { CopyOutlined, RobotOutlined, UserOutlined, LoadingOutlined } from '@ant-design/icons';
import ReactMarkdown from 'react-markdown';
import { Light as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vs2015 } from 'react-syntax-highlighter/dist/esm/styles/hljs';
import python from 'react-syntax-highlighter/dist/esm/languages/hljs/python';
import javascript from 'react-syntax-highlighter/dist/esm/languages/hljs/javascript';
import typescript from 'react-syntax-highlighter/dist/esm/languages/hljs/typescript';
import bash from 'react-syntax-highlighter/dist/esm/languages/hljs/bash';

// 注册常用的编程语言
SyntaxHighlighter.registerLanguage('python', python);
SyntaxHighlighter.registerLanguage('javascript', javascript);
SyntaxHighlighter.registerLanguage('typescript', typescript);
SyntaxHighlighter.registerLanguage('bash', bash);

window.console.log('=== Chat 组件模块加载 ===');

// 消息类型定义
type MessageType = 'think' | 'message' | 'tool';

interface ThoughtItem {
  type: MessageType;
  content: string;
  timestamp: number;
}

interface Message {
  content: string;
  role: 'user' | 'assistant';
  type?: MessageType;
  thoughts?: ThoughtItem[];
}

// 流式响应数据结构
interface StreamChunk {
  type?: MessageType;
  content: string;
}

// 消息类型配置
const MESSAGE_TYPE_CONFIG = {
  think: {
    title: '思考推理',
    description: '正在分析和思考问题',
    icon: <LoadingOutlined style={{ color: '#1677ff' }} />,
    status: 'pending' as const
  },
  message: {
    title: '最终回答',
    description: '已完成分析',
    icon: <RobotOutlined style={{ color: '#52c41a' }} />,
    status: 'success' as const
  },
  tool: {
    title: '工具调用',
    description: '使用工具辅助分析',
    icon: <LoadingOutlined style={{ color: '#faad14' }} />,
    status: 'pending' as const
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
  const [inputValue, setInputValue] = useState('');
  const { message } = App.useApp();

  useEffect(() => {
    window.console.log('=== 消息列表已更新 ===', messages);
  }, [messages]);

  const copyMessage = (content: string) => {
    navigator.clipboard.writeText(content).then(() => {
      message.success('复制成功！');
    });
  };

  const renderAssistantMessage = (thoughts: ThoughtItem[]) => {
    const items = thoughts.map(thought => ({
      title: MESSAGE_TYPE_CONFIG[thought.type].title,
      description: MESSAGE_TYPE_CONFIG[thought.type].description,
      status: MESSAGE_TYPE_CONFIG[thought.type].status,
      icon: MESSAGE_TYPE_CONFIG[thought.type].icon,
      content: (
        <Typography>
          <Typography.Paragraph>
            {thought.type === 'message' ? (
              <ReactMarkdown
                components={{
                  code({ className, children }) {
                    const match = /language-(\w+)/.exec(className || '');
                    const language = match ? match[1] : '';
                    const code = String(children).replace(/\n$/, '');
                    
                    if (language) {
                      return (
                        <SyntaxHighlighter
                          language={language}
                          style={vs2015}
                          customStyle={{
                            margin: '0.5em 0',
                            padding: '1em',
                            borderRadius: '4px',
                            fontSize: '14px'
                          }}
                        >
                          {code}
                        </SyntaxHighlighter>
                      );
                    }
                    
                    return (
                      <code 
                        className={className}
                        style={{
                          backgroundColor: '#f6f8fa',
                          padding: '0.2em 0.4em',
                          borderRadius: '3px',
                          fontSize: '85%'
                        }}
                      >
                        {children}
                      </code>
                    );
                  }
                }}
              >
                {thought.content}
              </ReactMarkdown>
            ) : (
              thought.content.split('\n').map((line, index) => (
                <div key={index}>{line}</div>
              ))
            )}
          </Typography.Paragraph>
        </Typography>
      ),
    }));

    return (
      <Card style={{ width: '100%', marginBottom: 16 }}>
        <ThoughtChain
          size="small"
          items={items}
          collapsible
        />
      </Card>
    );
  };

  const renderMessageContent = (msg: Message) => {
    if (msg.role === 'user') {
      return <Typography.Text>{msg.content}</Typography.Text>;
    }

    return msg.thoughts ? renderAssistantMessage(msg.thoughts) : null;
  };

  const renderMessage = (msg: Message) => {
    const isUser = msg.role === 'user';
    return (
      <Flex vertical gap="small" style={{ width: '100%' }}>
        <Flex align="start" justify={isUser ? 'flex-end' : 'flex-start'}>
          {isUser ? (
            <Bubble
              content={msg.content}
              placement="end"
              variant="filled"
              shape="round"
              style={{ maxWidth: '80%' }}
              classNames={{
                content: 'user-message'
              }}
              avatar={
                <UserOutlined style={{ 
                  fontSize: '18px',
                  padding: '8px',
                  backgroundColor: '#e6f4ff',
                  borderRadius: '50%',
                  color: '#1677ff' 
                }} />
              }
            >
              <Typography.Text>{msg.content}</Typography.Text>
            </Bubble>
          ) : (
            <div style={{ width: '100%' }}>
              {renderMessageContent(msg)}
            </div>
          )}
        </Flex>
      </Flex>
    );
  };

  const handleRequest = async (text: string) => {
    try {
      setIsLoading(true);
      setInputValue('');
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
        thoughts: []
      };

      let currentThought: ThoughtItem = {
        type: 'think',
        content: '',
        timestamp: Date.now()
      };

      setMessages(prev => [...prev, currentMessage]);

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = new TextDecoder().decode(value);
        const lines = chunk.split('\n');
        
        for (const line of lines) {
          if (!line || !line.startsWith('data: ')) continue;
          
          // 检查是否是结束标记
          if (line.includes('[DONE]')) {
            console.log('Stream completed');
            continue;
          }

          try {
            const data: StreamChunk = JSON.parse(line.slice(6));
            
            // 如果类型发生变化，创建新的思维节点
            if (data.type && data.type !== currentThought.type) {
              // 将当前思维节点添加到消息中
              if (currentThought.content) {
                currentMessage = {
                  ...currentMessage,
                  thoughts: [...(currentMessage.thoughts || []), { ...currentThought }]
                };
              }
              // 创建新的思维节点
              currentThought = {
                type: data.type,
                content: data.content,
                timestamp: Date.now()
              };
            } else {
              // 更新当前思维节点的内容
              currentThought = {
                ...currentThought,
                content: data.content
              };
            }

            // 更新消息，使用当前所有已完成的思维节点和当前正在进行的思维节点
            setMessages(prev => {
              const newMessages = [...prev];
              const lastMessage = newMessages[newMessages.length - 1];
              
              // 获取已有的思维节点，但排除掉与当前节点相同类型的
              const existingThoughts = (lastMessage.thoughts || []).filter(
                t => t.type !== currentThought.type
              );
              
              newMessages[newMessages.length - 1] = {
                ...currentMessage,
                content: data.content,
                thoughts: [...existingThoughts, currentThought]
              };
              return newMessages;
            });
          } catch (e) {
            if (!line.includes('[DONE]')) {
              console.error('解析响应数据失败:', e, '数据:', line);
            }
          }
        }
      }

      // 确保最后一个思维节点被添加到消息中
      if (currentThought.content) {
        setMessages(prev => {
          const newMessages = [...prev];
          const lastMessage = newMessages[newMessages.length - 1];
          
          // 获取已有的思维节点，但排除掉与当前节点相同类型的
          const existingThoughts = (lastMessage.thoughts || []).filter(
            t => t.type !== currentThought.type
          );
          
          newMessages[newMessages.length - 1] = {
            ...lastMessage,
            thoughts: [...existingThoughts, currentThought]
          };
          return newMessages;
        });
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
          value={inputValue}
          onChange={setInputValue}
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