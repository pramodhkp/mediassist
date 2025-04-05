import React, { useEffect, useRef } from 'react';
import { Avatar, Typography } from 'antd';
import { UserOutlined, RobotOutlined } from '@ant-design/icons';

const { Text } = Typography;

const MessageList = ({ messages }) => {
  const messagesEndRef = useRef(null);

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const formatTime = (timestamp) => {
    return new Date(timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  return (
    <div className="message-list">
      {messages.map((message) => (
        <div
          key={message.id}
          className={`message ${message.type}`}
        >
          <Avatar
            icon={message.type === 'user' ? <UserOutlined /> : <RobotOutlined />}
            style={{
              backgroundColor: message.type === 'user' ? '#1890ff' : '#52c41a',
            }}
          />
          <div className="message-bubble">
            <div style={{ wordWrap: 'break-word' }}>{message.content}</div>
            <div style={{ textAlign: 'right', marginTop: '4px' }}>
              <Text type="secondary" style={{ fontSize: '12px' }}>
                {formatTime(message.timestamp)}
              </Text>
            </div>
          </div>
        </div>
      ))}
      <div ref={messagesEndRef} />
    </div>
  );
};

export default MessageList;