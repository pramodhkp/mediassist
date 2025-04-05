import React from 'react';
import ChatPanel from './components/ChatPanel';
import DailyInsightsPanel from './components/DailyInsightsPanel';
import WeeklyInsightsPanel from './components/WeeklyInsightsPanel';
import './App.css';

function App() {
  return (
    <div className="app-container">
      <div className="main-panel">
        <ChatPanel />
      </div>
      <div className="right-panels">
        <DailyInsightsPanel />
        <WeeklyInsightsPanel />
      </div>
    </div>
  );
}

export default App;