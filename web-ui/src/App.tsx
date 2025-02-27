import React from 'react'
import { Layout } from 'antd'
import { Chat } from 'src/shared/components/Chat'

const { Content } = Layout

const App: React.FC = () => {
  return (
    <Layout style={{ height: '100vh' }}>
      <Content style={{ padding: '20px' }}>
        <Chat />
      </Content>
    </Layout>
  )
}

export default App 