import { useState } from 'react';

function useChat() {
  const [messages, setMessages] = useState([]);

  const sendMessage = (text) => {
    setMessages((prevMessages) => [...prevMessages, { sender: 'user', text }]);
    // Simulate bot response after a short delay
    setTimeout(() => {
      const botResponse = generateBotResponse(text);
      setMessages((prevMessages) => [...prevMessages, { sender: 'bot', text: botResponse }]);
    }, 500);
  };

  const generateBotResponse = (userMessage) => {
    // Replace with actual API call to a chatbot model
    return `You said: "${userMessage}". This is a sample bot response.`;
  };

  return {
    messages,
    sendMessage,
  };
}

export default useChat;