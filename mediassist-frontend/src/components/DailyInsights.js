import React, { useState, useEffect } from 'react';
import { Card, Typography, List, Tag, Progress, Spin, Alert } from 'antd';
import ReactMarkdown from 'react-markdown';
import axios from 'axios';
import {
  HeartOutlined,
  FireOutlined, 
  DashboardOutlined, 
  ClockCircleOutlined,
  WalletOutlined,
  ReloadOutlined
} from '@ant-design/icons';

const { Title, Text } = Typography;

// Fallback mock data for daily insights (used when API fails)
const fallbackDailyInsights = {
  date: new Date().toLocaleDateString('en-US', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' }),
  healthMetrics: {
    steps: 8432,
    stepsGoal: 10000,
    caloriesBurned: 1850,
    caloriesGoal: 2500,
    heartRate: {
      average: 72,
      min: 58,
      max: 135
    },
    sleepHours: 7.5
  },
  medications: [
    { name: 'Vitamin D', taken: true, time: '8:00 AM' },
    { name: 'Omega-3', taken: true, time: '8:00 AM' },
    { name: 'Allergy Med', taken: false, time: '10:00 PM' }
  ],
  waterIntake: {
    current: 1.8,
    goal: 2.5
  }
};

const DailyInsights = () => {
  const [insights, setInsights] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchDailyInsights();
  }, []);

  const fetchDailyInsights = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await axios.get('http://localhost:5000/daily_insights');
      // Use the actual response from the API
      if (response.data && response.data.response) {
        setInsights({
          ...fallbackDailyInsights,
          apiResponse: response.data.response
        });
      } else {
        setInsights(fallbackDailyInsights);
      }
      console.log('API Response:', response.data);
    } catch (err) {
      console.error('Error fetching daily insights:', err);
      setError('Failed to load daily insights');
      setInsights(fallbackDailyInsights);
    } finally {
      setLoading(false);
    }
  };

  // If still loading, show spinner
  if (loading) {
    return (
      <div className="daily-insights-component" style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%' }}>
        <Spin size="large" tip="Loading daily insights..." />
      </div>
    );
  }

  // If error and no insights, show error message
  if (error && !insights) {
    return (
      <div className="daily-insights-component">
        <Alert
          message="Error"
          description={error}
          type="error"
          showIcon
          action={
            <ReloadOutlined onClick={fetchDailyInsights} style={{ fontSize: '16px', cursor: 'pointer' }} />
          }
        />
      </div>
    );
  }

  const { date, healthMetrics, medications, waterIntake } = insights || fallbackDailyInsights;
  
  return (
    <div className="daily-insights-component">
      <Title level={4} style={{ marginBottom: '16px' }}>Daily Insights</Title>
      <Text type="secondary">{date}</Text>
      
      {insights.apiResponse && (
        <Card size="small" style={{ marginTop: '16px' }} title="API Response">
          <div className="markdown-content">
            <ReactMarkdown>{insights.apiResponse}</ReactMarkdown>
          </div>
        </Card>
      )}
      
      <Card size="small" style={{ marginTop: '16px' }} title="Health Metrics">
        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '12px' }}>
          <div>
            <DashboardOutlined style={{ marginRight: '8px', color: '#1890ff' }} />
            <Text>Steps</Text>
          </div>
          <Text>{healthMetrics.steps} / {healthMetrics.stepsGoal}</Text>
        </div>
        <Progress 
          percent={Math.round((healthMetrics.steps / healthMetrics.stepsGoal) * 100)} 
          size="small" 
          status={healthMetrics.steps >= healthMetrics.stepsGoal ? "success" : "active"}
        />
        
        <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '16px', marginBottom: '12px' }}>
          <div>
            <FireOutlined style={{ marginRight: '8px', color: '#ff4d4f' }} />
            <Text>Calories</Text>
          </div>
          <Text>{healthMetrics.caloriesBurned} / {healthMetrics.caloriesGoal}</Text>
        </div>
        <Progress 
          percent={Math.round((healthMetrics.caloriesBurned / healthMetrics.caloriesGoal) * 100)} 
          size="small" 
          strokeColor="#ff4d4f"
          status={healthMetrics.caloriesBurned >= healthMetrics.caloriesGoal ? "success" : "active"}
        />
        
        <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '16px', marginBottom: '12px' }}>
          <div>
            <HeartOutlined style={{ marginRight: '8px', color: '#ff4d4f' }} />
            <Text>Heart Rate</Text>
          </div>
          <Text>{healthMetrics.heartRate.average} BPM</Text>
        </div>
        <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '12px' }}>
          <Text type="secondary">Min: {healthMetrics.heartRate.min} BPM</Text>
          <Text type="secondary">Max: {healthMetrics.heartRate.max} BPM</Text>
        </div>
        
        <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '16px', marginBottom: '12px' }}>
          <div>
            <ClockCircleOutlined style={{ marginRight: '8px', color: '#722ed1' }} />
            <Text>Sleep</Text>
          </div>
          <Text>{healthMetrics.sleepHours} hours</Text>
        </div>
        
        <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '16px', marginBottom: '12px' }}>
          <div>
            <WalletOutlined style={{ marginRight: '8px', color: '#13c2c2' }} />
            <Text>Water</Text>
          </div>
          <Text>{waterIntake.current} / {waterIntake.goal} L</Text>
        </div>
        <Progress 
          percent={Math.round((waterIntake.current / waterIntake.goal) * 100)} 
          size="small" 
          strokeColor="#13c2c2"
          status={waterIntake.current >= waterIntake.goal ? "success" : "active"}
        />
      </Card>
      
      <Card size="small" style={{ marginTop: '16px' }} title="Medications">
        <List
          size="small"
          dataSource={medications}
          renderItem={item => (
            <List.Item
              actions={[
                <Tag color={item.taken ? 'success' : 'warning'}>
                  {item.taken ? 'Taken' : 'Pending'}
                </Tag>
              ]}
            >
              <List.Item.Meta
                title={item.name}
                description={item.time}
              />
            </List.Item>
          )}
        />
      </Card>
    </div>
  );
};

export default DailyInsights;