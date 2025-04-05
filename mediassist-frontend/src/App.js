import React from 'react';
import { Layout } from 'antd';
import './App.css';
import ChatInterface from './components/ChatInterface';
import DailyInsights from './components/DailyInsights';
import WeeklyInsights from './components/WeeklyInsights';
import LifestyleProfile from './components/LifestyleProfile';

const { Header, Content } = Layout;

function App() {
  return (
    <Layout className="app-container">
      <Header style={{ background: '#fff', padding: '0 16px', height: '64px', lineHeight: '64px', borderBottom: '1px solid #e8e8e8' }}>
        <h1 style={{ margin: 0, fontSize: '20px' }}>MediAssist</h1>
      </Header>
      <Content style={{ display: 'flex', height: 'calc(100vh - 64px)' }}>
        <div className="chat-panel">
          <ChatInterface />
        </div>
        <div className="insights-container">
          <div className="lifestyle-profile-container">
            <LifestyleProfile />
          </div>
          <div className="daily-insights">
            <DailyInsights />
          </div>
          <div className="weekly-insights">
            <WeeklyInsights />
          </div>
        </div>
      </Content>
    </Layout>
  );
}

export default App;
