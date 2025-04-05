import React, { useState, useEffect } from 'react';
import { Card, Typography, Statistic, Row, Col, Spin, Alert } from 'antd';
import ReactMarkdown from 'react-markdown';
import axios from 'axios';
import {
  ArrowUpOutlined,
  ArrowDownOutlined, 
  CalendarOutlined,
  CheckCircleOutlined,
  ReloadOutlined
} from '@ant-design/icons';

const { Title, Text } = Typography;

// Fallback mock data for weekly insights (used when API fails)
const fallbackWeeklyInsights = {
  weekRange: 'May 1 - May 7, 2025',
  healthTrends: {
    steps: {
      average: 8750,
      change: 5.2,
      improved: true
    },
    sleep: {
      average: 7.2,
      change: -0.3,
      improved: false
    },
    heartRate: {
      average: 68,
      change: -2.1,
      improved: true
    },
    caloriesBurned: {
      average: 1920,
      change: 8.5,
      improved: true
    }
  },
  achievements: [
    'Completed 5 days of 8000+ steps',
    'Maintained consistent sleep schedule',
    'Reduced resting heart rate'
  ],
  recommendations: [
    'Try to increase water intake by 0.5L daily',
    'Consider adding 15 minutes of meditation',
    'Schedule a follow-up appointment next week'
  ]
};

const WeeklyInsights = () => {
  const [insights, setInsights] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchWeeklyInsights();
  }, []);

  const fetchWeeklyInsights = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await axios.get('http://localhost:5000/weekly_insights');
      // Use the actual response from the API
      if (response.data && response.data.response) {
        setInsights({
          ...fallbackWeeklyInsights,
          apiResponse: response.data.response
        });
      } else {
        setInsights(fallbackWeeklyInsights);
      }
      console.log('API Response:', response.data);
    } catch (err) {
      console.error('Error fetching weekly insights:', err);
      setError('Failed to load weekly insights');
      setInsights(fallbackWeeklyInsights);
    } finally {
      setLoading(false);
    }
  };

  // If still loading, show spinner
  if (loading) {
    return (
      <div className="weekly-insights-component" style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%' }}>
        <Spin size="large" tip="Loading weekly insights..." />
      </div>
    );
  }

  // If error and no insights, show error message
  if (error && !insights) {
    return (
      <div className="weekly-insights-component">
        <Alert
          message="Error"
          description={error}
          type="error"
          showIcon
          action={
            <ReloadOutlined onClick={fetchWeeklyInsights} style={{ fontSize: '16px', cursor: 'pointer' }} />
          }
        />
      </div>
    );
  }

  const { weekRange, healthTrends, achievements, recommendations } = insights || fallbackWeeklyInsights;
  
  return (
    <div className="weekly-insights-component">
      <Title level={4} style={{ marginBottom: '16px' }}>Weekly Insights</Title>
      <Text type="secondary">
        <CalendarOutlined style={{ marginRight: '8px' }} />
        {weekRange}
      </Text>
      
      {insights.apiResponse && (
        <Card size="small" style={{ marginTop: '16px' }} title="API Response">
          <div className="markdown-content">
            <ReactMarkdown>{insights.apiResponse}</ReactMarkdown>
          </div>
        </Card>
      )}
      
      <Card size="small" style={{ marginTop: '16px' }} title="Health Trends">
        <Row gutter={[16, 16]}>
          <Col span={12}>
            <Statistic
              title="Avg. Steps"
              value={healthTrends.steps.average}
              precision={0}
              valueStyle={{ color: healthTrends.steps.improved ? '#3f8600' : '#cf1322' }}
              prefix={healthTrends.steps.improved ? <ArrowUpOutlined /> : <ArrowDownOutlined />}
              suffix={
                <Text type="secondary" style={{ fontSize: '12px' }}>
                  {healthTrends.steps.change}%
                </Text>
              }
            />
          </Col>
          <Col span={12}>
            <Statistic
              title="Avg. Sleep"
              value={healthTrends.sleep.average}
              precision={1}
              valueStyle={{ color: healthTrends.sleep.improved ? '#3f8600' : '#cf1322' }}
              prefix={healthTrends.sleep.improved ? <ArrowUpOutlined /> : <ArrowDownOutlined />}
              suffix={
                <span>
                  hrs
                  <Text type="secondary" style={{ fontSize: '12px', marginLeft: '5px' }}>
                    {healthTrends.sleep.change}%
                  </Text>
                </span>
              }
            />
          </Col>
          <Col span={12}>
            <Statistic
              title="Avg. Heart Rate"
              value={healthTrends.heartRate.average}
              precision={0}
              valueStyle={{ color: healthTrends.heartRate.improved ? '#3f8600' : '#cf1322' }}
              prefix={healthTrends.heartRate.improved ? <ArrowDownOutlined /> : <ArrowUpOutlined />}
              suffix={
                <span>
                  BPM
                  <Text type="secondary" style={{ fontSize: '12px', marginLeft: '5px' }}>
                    {healthTrends.heartRate.change}%
                  </Text>
                </span>
              }
            />
          </Col>
          <Col span={12}>
            <Statistic
              title="Avg. Calories"
              value={healthTrends.caloriesBurned.average}
              precision={0}
              valueStyle={{ color: healthTrends.caloriesBurned.improved ? '#3f8600' : '#cf1322' }}
              prefix={healthTrends.caloriesBurned.improved ? <ArrowUpOutlined /> : <ArrowDownOutlined />}
              suffix={
                <Text type="secondary" style={{ fontSize: '12px' }}>
                  {healthTrends.caloriesBurned.change}%
                </Text>
              }
            />
          </Col>
        </Row>
      </Card>
      
      <Card size="small" style={{ marginTop: '16px' }} title="Achievements">
        <ul style={{ paddingLeft: '20px', margin: 0 }}>
          {achievements.map((achievement, index) => (
            <li key={index} style={{ marginBottom: '8px' }}>
              <Text>
                <CheckCircleOutlined style={{ color: '#52c41a', marginRight: '8px' }} />
                {achievement}
              </Text>
            </li>
          ))}
        </ul>
      </Card>
      
      <Card size="small" style={{ marginTop: '16px' }} title="Recommendations">
        <ul style={{ paddingLeft: '20px', margin: 0 }}>
          {recommendations.map((recommendation, index) => (
            <li key={index} style={{ marginBottom: '8px' }}>
              <Text>{recommendation}</Text>
            </li>
          ))}
        </ul>
      </Card>
    </div>
  );
};

export default WeeklyInsights;