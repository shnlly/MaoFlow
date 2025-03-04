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
import { Message, MessageType, MessageItem } from './types';

// 注册常用的编程语言
SyntaxHighlighter.registerLanguage('python', python);
SyntaxHighlighter.registerLanguage('javascript', javascript);
SyntaxHighlighter.registerLanguage('typescript', typescript);
SyntaxHighlighter.registerLanguage('bash', bash);

window.console.log('=== Chat 组件模块加载 ===');

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

interface ChatProps {
  sessionId: string;
}

const Chat: React.FC<ChatProps> = ({ sessionId }) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [inputValue, setInputValue] = useState('');
  const { message } = App.useApp();

  // 当 sessionId 改变时加载历史消息
  useEffect(() => {
    loadSessionMessages();
  }, [sessionId]);

  const loadSessionMessages = async () => {
    try {
      const response = await fetch(`http://localhost:8000/api/conversations/${sessionId}/messages`);
      if (response.ok) {
        const history = await response.json();
        setMessages(history);
      }
    } catch (error) {
      console.error('Failed to load session messages:', error);
      message.error('加载历史消息失败');
    }
  };

  useEffect(() => {
    window.console.log('=== 消息列表已更新 ===', messages);
  }, [messages]);

  const copyMessage = (content: string) => {
    navigator.clipboard.writeText(content).then(() => {
      message.success('复制成功！');
    });
  };

  const renderAssistantMessage = (message: Message) => {
    if (!message.message_items || message.message_items.length === 0) {
      return (
        <Typography.Text>
          <ReactMarkdown>{message.content}</ReactMarkdown>
        </Typography.Text>
      );
    }

    const items = message.message_items.map(item => ({
      title: MESSAGE_TYPE_CONFIG[item.type].title,
      description: MESSAGE_TYPE_CONFIG[item.type].description,
      status: MESSAGE_TYPE_CONFIG[item.type].status,
      icon: MESSAGE_TYPE_CONFIG[item.type].icon,
      content: (
        <Typography>
          <Typography.Paragraph>
            {item.type === 'message' ? (
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
                {item.content}
              </ReactMarkdown>
            ) : (
              item.content.split('\n').map((line, index) => (
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
      return (
        <Typography.Text>
          {msg.message_items?.[0]?.content || msg.content}
        </Typography.Text>
      );
    }

    return renderAssistantMessage(msg);
  };

  const renderMessage = (msg: Message) => {
    const isUser = msg.role === 'user';
    return (
      <Flex vertical gap="small" style={{ width: '100%' }}>
        <Flex align="start" justify={isUser ? 'flex-end' : 'flex-start'}>
          {isUser ? (
            <Bubble
              content={msg.message_items?.[0]?.content || msg.content}
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
              <Typography.Text>{msg.message_items?.[0]?.content || msg.content}</Typography.Text>
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
      
      // 添加用户消息到界面
      const userMessage: Message = {
        id: '',
        role: 'user',
        content: text,
        conversation_id: sessionId,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
        message_items: [{
          id: '',
          type: 'message',
          content: text,
          timestamp: new Date().toISOString(),
          message_id: '',
          conversation_id: sessionId
        }]
      };
      
      setMessages(prev => [...prev, userMessage]);
      
      // 创建助手消息占位符
      const assistantMessage: Message = {
        id: '',
        role: 'assistant',
        content: '',
        conversation_id: sessionId,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
        message_items: []
      };
      
      setMessages(prev => [...prev, assistantMessage]);
      
      // 发送请求
      const response = await fetch(
        `http://localhost:8000/api/conversations/${sessionId}/query?query=${encodeURIComponent(text)}`,
        {
          method: 'POST',
        }
      );

      if (!response.ok) {
        throw new Error('请求失败');
      }

      const reader = response.body?.getReader();
      if (!reader) {
        throw new Error('无法读取响应流');
      }

      let currentMessage = '';
      let currentType: MessageType = 'message';
      let thinkContent = '';
      let messageContent = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = new TextDecoder().decode(value);
        const lines = chunk.split('\n');

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6));
              
              if (data.type === 'done') {
                setIsLoading(false);
                break;
              }
              
              if (data.type === 'error') {
                message.error(data.content);
                setIsLoading(false);
                break;
              }
              
              // 更新当前消息类型
              if (data.type) {
                currentType = data.type;
              }
              
              // 根据类型分别累积内容
              if (currentType === 'think') {
                thinkContent += data.content;
              } else if (currentType === 'message') {
                messageContent += data.content;
              }
              
              // 更新消息列表
              setMessages(prev => {
                const newMessages = [...prev];
                const lastMessage = newMessages[newMessages.length - 1];
                
                if (lastMessage.role === 'assistant') {
                  // 更新或创建 message_items
                  const messageItems: MessageItem[] = [];
                  
                  // 添加 think 内容
                  if (thinkContent) {
                    messageItems.push({
                      id: '',
                      type: 'think',
                      content: thinkContent,
                      timestamp: new Date().toISOString(),
                      message_id: lastMessage.id,
                      conversation_id: sessionId
                    });
                  }
                  
                  // 添加 message 内容
                  if (messageContent) {
                    messageItems.push({
                      id: '',
                      type: 'message',
                      content: messageContent,
                      timestamp: new Date().toISOString(),
                      message_id: lastMessage.id,
                      conversation_id: sessionId
                    });
                  }
                  
                  lastMessage.message_items = messageItems;
                  lastMessage.content = messageContent || thinkContent;
                }
                
                return newMessages;
              });
            } catch (error) {
              console.error('Error parsing chunk:', error);
            }
          }
        }
      }
      
      setIsLoading(false);
    } catch (error) {
      console.error('Error in handleRequest:', error);
      message.error('发送消息失败');
      setIsLoading(false);
    }
  };

  return (
    <Flex vertical style={{ height: '100%' }}>
      <Flex flex={1} vertical style={{ overflow: 'auto', padding: '16px' }}>
        {messages.map((msg, index) => (
          <div key={msg.id || index}>
            {renderMessage(msg)}
          </div>
        ))}
      </Flex>
      <Sender
        value={inputValue}
        onChange={setInputValue}
        onSubmit={handleRequest}
        loading={isLoading}
        placeholder="输入消息..."
      />
    </Flex>
  );
};

export default Chat; 