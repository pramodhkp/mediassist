import React from 'react';
import './Message.css';

function Message({ sender, text }) {
  return (
    <div className={`message ${sender === 'user' ? 'user' : 'bot'}`}>
      <div className="message-sender">{sender === 'user' ? 'You' : 'Bot'}</div>
      <div className="message-text">{text}</div>
    </div>
  );
}

export default Message;