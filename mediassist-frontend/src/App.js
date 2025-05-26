import React from 'react';
import { Layout } from 'antd';
import './App.css';
import ChatInterface from './components/ChatInterface';
import DailyInsights from './components/DailyInsights';
import WeeklyInsights from './components/WeeklyInsights';
import LifestyleProfile from './components/LifestyleProfile';
import MedicalReports from './components/MedicalReports';
import MedicationsPage from './components/MedicationsPage'; // Import MedicationsPage

const { Header, Content, Sider } = Layout; // Added Sider for potential navigation

function App() {
  // Simple state to switch between views, as no router is present
  const [currentView, setCurrentView] = React.useState('insights'); // 'insights' or 'medications'

  return (
    <Layout className="app-container" style={{ minHeight: '100vh' }}>
      <Header style={{ background: '#fff', padding: '0 16px', height: '64px', lineHeight: '64px', borderBottom: '1px solid #e8e8e8', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h1 style={{ margin: 0, fontSize: '20px' }}>HealthSphere</h1>
        {/* Simple navigation buttons */}
        <div>
          <Button type={currentView === 'insights' ? 'primary' : 'default'} onClick={() => setCurrentView('insights')} style={{ marginRight: 8 }}>
            Insights & Profile
          </Button>
          <Button type={currentView === 'medications' ? 'primary' : 'default'} onClick={() => setCurrentView('medications')}>
            Medications
          </Button>
        </div>
      </Header>
      <Layout> {/* Adding another Layout to contain Sider and Content if needed, or just Content */}
        <Content style={{ display: 'flex', height: 'calc(100vh - 64px)', width: '100%', padding: '10px' }}>
          {currentView === 'insights' && (
            <>
              <div className="chat-panel">
                <ChatInterface />
              </div>
              <div className="insights-container">
                <div className="top-row">
                  <div className="lifestyle-profile-container">
                    <LifestyleProfile />
                  </div>
                  <div className="medical-reports-container">
                    <MedicalReports />
                  </div>
                </div>
                <div className="daily-insights">
                  <DailyInsights />
                </div>
                <div className="weekly-insights">
                  <WeeklyInsights />
                </div>
              </div>
            </>
          )}
          {currentView === 'medications' && (
            // MedicationsPage might need its own internal layout (e.g. full width)
            <div style={{ width: '100%', overflowY: 'auto' }}> {/* Ensure it's scrollable if content exceeds height */}
              <MedicationsPage />
            </div>
          )}
        </Content>
      </Layout>
    </Layout>
  );
}

export default App;
