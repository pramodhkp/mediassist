import React, { useState } from 'react';
import { Input, Button } from 'antd';
import { SendOutlined, LoadingOutlined } from '@ant-design/icons';

const MessageInput = ({ onSendMessage, isLoading }) => {
  const [message, setMessage] = useState('');

  const handleSend = () => {
    if (message.trim() && !isLoading) {
      onSendMessage(message);
      setMessage('');
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="message-input">
      <Input.TextArea
        value={message}
        onChange={(e) => setMessage(e.target.value)}
        onKeyPress={handleKeyPress}
        placeholder="Type your message here..."
        autoSize={{ minRows: 1, maxRows: 4 }}
        style={{ borderRadius: '8px', resize: 'none', flex: 1 }}
        disabled={isLoading}
      />
      <Button
        type="primary"
        icon={isLoading ? <LoadingOutlined /> : <SendOutlined />}
        onClick={handleSend}
        loading={isLoading}
        disabled={isLoading || !message.trim()}
      />
    </div>
  );
};

export default MessageInput;