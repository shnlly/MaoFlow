import React, { useState } from 'react';
import { Bubble, Sender } from '@ant-design/x';

interface Message {
  content: string;
  role: 'user' | 'assistant';
}

const Chat: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([
    {
      content: '你好！我是 AI 助手，有什么我可以帮你的吗？',
      role: 'assistant',
    },
  ]);

  const handleSend = (content: string) => {
    // 添加用户消息
    setMessages(prev => [...prev, { content, role: 'user' }]);
    
    // 模拟 AI 回复
    setTimeout(() => {
      setMessages(prev => [...prev, {
        content: `我收到了你的消息：${content}`,
        role: 'assistant',
      }]);
    }, 1000);
  };

  return (
    <div style={{ 
      height: '100vh',
      display: 'flex',
      flexDirection: 'column',
      padding: '20px',
      maxWidth: '800px',
      margin: '0 auto',
    }}>
      <div style={{ flex: 1, overflow: 'auto' }}>
        <Bubble.List items={messages} />
      </div>
      <div style={{ marginTop: '20px' }}>
        <Sender onSubmit={handleSend} />
      </div>
    </div>
  );
};

export default Chat; 