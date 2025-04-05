import React, { useState } from 'react';
import { Layout, Typography, message as antMessage } from 'antd';
import axios from 'axios';
import MessageList from './MessageList';
import MessageInput from './MessageInput';

const { Content, Footer } = Layout;
const { Title } = Typography;

// API endpoint for sending messages
const API_ENDPOINT = 'http://localhost:5000/send_message';

const ChatInterface = () => {
  const [messages, setMessages] = useState([
    {
      id: 1,
      type: 'assistant',
      content: 'Hello! I\'m your MediAssist AI. How can I help you with your health today?',
      timestamp: new Date()
    }
  ]);
  const [isLoading, setIsLoading] = useState(false);

  const handleSendMessage = async (content) => {
    if (!content.trim()) return;
    
    // Add user message
    const userMessage = {
      id: messages.length + 1,
      type: 'user',
      content,
      timestamp: new Date()
    };
    
    setMessages([...messages, userMessage]);
    setIsLoading(true);
    
    try {
      console.log('Sending message to:', API_ENDPOINT);
      // Send message to backend API
      const response = await axios.post(API_ENDPOINT, {
        message: content,
        userId: 'user123', // This would be the actual user ID in a real app
      }, {
        headers: {
          'Content-Type': 'application/json'
        }
      });
      console.log('Response received:', response.data);
      
      // Add assistant response
      const assistantMessage = {
        id: messages.length + 2,
        type: 'assistant',
        content: response.data.response || "I'm sorry, I couldn't process your request.",
        timestamp: new Date()
      };
      
      setMessages(prevMessages => [...prevMessages, assistantMessage]);
    } catch (error) {
      console.error('Error sending message:', error);
      antMessage.error('Failed to send message. Please try again.');
      
      // Fallback response in case of error
      const errorMessage = {
        id: messages.length + 2,
        type: 'assistant',
        content: "I'm sorry, I'm having trouble connecting to the server. Please try again later.",
        timestamp: new Date()
      };
      
      setMessages(prevMessages => [...prevMessages, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Layout className="chat-interface" style={{ height: '100%' }}>
      <Content style={{ flex: 1, overflow: 'auto', padding: '16px' }}>
        <Title level={4} style={{ margin: '0 0 16px 0' }}>Chat</Title>
        <MessageList messages={messages} />
      </Content>
      
      <Footer style={{ padding: '10px 16px', background: '#fff', borderTop: '1px solid #e8e8e8' }}>
        <MessageInput onSendMessage={handleSendMessage} isLoading={isLoading} />
      </Footer>
    </Layout>
  );
};

export default ChatInterface;