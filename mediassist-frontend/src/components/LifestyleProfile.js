import React, { useState, useEffect } from 'react';
import { Card, Typography, Tag, Spin, Row, Col } from 'antd';
import { UserOutlined, ManOutlined, WomanOutlined, ColumnHeightOutlined,
         DashboardOutlined, MedicineBoxOutlined, HeartOutlined } from '@ant-design/icons';
import axios from 'axios';

const { Title, Text } = Typography;

const LifestyleProfile = () => {
  const [profileData, setProfileData] = useState(null);
  const [medicalConditions, setMedicalConditions] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        // Fetch user profile data
        const profileResponse = await axios.get('http://localhost:5000/user_profile');
        setProfileData(profileResponse.data.response);
        
        // Fetch medical conditions data
        const conditionsResponse = await axios.get('http://localhost:5000/medical_conditions');
        setMedicalConditions(conditionsResponse.data.response || []);
      } catch (error) {
        console.error('Error fetching lifestyle profile data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  // Function to get unique condition names and count
  const getConditionSummary = () => {
    if (!medicalConditions.length) return [];
    
    // Extract unique condition names
    const uniqueConditions = [...new Set(medicalConditions.map(condition => condition.condition_name))];
    
    // Count occurrences of each condition
    const conditionCounts = uniqueConditions.map(conditionName => {
      const count = medicalConditions.filter(condition => condition.condition_name === conditionName).length;
      return { name: conditionName, count };
    });
    
    return conditionCounts;
  };

  const conditionSummary = getConditionSummary();

  // Helper function to get gender icon
  const getGenderIcon = (gender) => {
    if (!gender) return <UserOutlined />;
    return gender.toLowerCase() === 'male' ? <ManOutlined /> : <WomanOutlined />;
  };

  return (
    <div className="lifestyle-profile">
      <Title level={4}>Your Lifestyle Profile</Title>
      
      {loading ? (
        <div style={{ textAlign: 'center', padding: '20px' }}>
          <Spin />
        </div>
      ) : (
        <Row gutter={16}>
          <Col span={12}>
            <Card
              title={
                <span>
                  <UserOutlined style={{ marginRight: '8px' }} />
                  Basic Information
                </span>
              }
              style={{ height: '100%' }}
            >
              {profileData ? (
                <div>
                  <p>
                    <UserOutlined style={{ marginRight: '8px', color: '#1890ff' }} />
                    <strong>Age:</strong> {profileData.age || 'Not provided'}
                  </p>
                  <p>
                    {getGenderIcon(profileData.gender)}
                    <strong style={{ marginLeft: '8px' }}>Gender:</strong> {profileData.gender || 'Not provided'}
                  </p>
                  <p>
                    <ColumnHeightOutlined style={{ marginRight: '8px', color: '#1890ff' }} />
                    <strong>Height:</strong> {profileData.height ? `${profileData.height} cm` : 'Not provided'}
                  </p>
                  <p>
                    <DashboardOutlined style={{ marginRight: '8px', color: '#1890ff' }} />
                    <strong>Weight:</strong> {profileData.weight ? `${profileData.weight} kg` : 'Not provided'}
                  </p>
                </div>
              ) : (
                <Text type="secondary">No profile information available</Text>
              )}
            </Card>
          </Col>
          
          <Col span={12}>
            <Card
              title={
                <span>
                  <MedicineBoxOutlined style={{ marginRight: '8px' }} />
                  Medical Conditions
                </span>
              }
              style={{ height: '100%' }}
            >
              {conditionSummary.length > 0 ? (
                <div>
                  <p>
                    <HeartOutlined style={{ marginRight: '8px', color: '#1890ff' }} />
                    You have {medicalConditions.length} recorded medical condition{medicalConditions.length !== 1 ? 's' : ''}:
                  </p>
                  <div style={{ marginTop: '10px' }}>
                    {conditionSummary.map((condition, index) => (
                      <Tag
                        key={index}
                        color="blue"
                        icon={<MedicineBoxOutlined />}
                        style={{ marginBottom: '8px', fontSize: '14px', padding: '4px 8px' }}
                      >
                        {condition.name} {condition.count > 1 ? `(${condition.count})` : ''}
                      </Tag>
                    ))}
                  </div>
                </div>
              ) : (
                <div>
                  <MedicineBoxOutlined style={{ marginRight: '8px', color: '#1890ff' }} />
                  <Text type="secondary">No medical conditions recorded</Text>
                </div>
              )}
            </Card>
          </Col>
        </Row>
      )}
    </div>
  );
};

export default LifestyleProfile;