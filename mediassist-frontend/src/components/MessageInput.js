import React, { useState, useRef, useEffect } from 'react';
import { Input, Button } from 'antd';
import { SendOutlined, LoadingOutlined, AudioOutlined } from '@ant-design/icons';
import axios from 'axios';

const MessageInput = ({ onSendMessage, isLoading }) => {
  // State for text message
  const [message, setMessage] = useState('');
  
  // States for speech recording
  const [isRecording, setIsRecording] = useState(false);
  const [isTranscribing, setIsTranscribing] = useState(false);
  const [shiftKeyPressed, setShiftKeyPressed] = useState(false);
  
  // Refs for recording
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);

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

  // Effect to add and remove keyboard event listeners
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === 'Shift') {
        setShiftKeyPressed(true);
      }
    };
    
    const handleKeyUp = (e) => {
      if (e.key === 'Shift') {
        setShiftKeyPressed(false);
      }
    };
    
    window.addEventListener('keydown', handleKeyDown);
    window.addEventListener('keyup', handleKeyUp);
    
    return () => {
      window.removeEventListener('keydown', handleKeyDown);
      window.removeEventListener('keyup', handleKeyUp);
    };
  }, []);

  // Start recording function
  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];
      
      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };
      
      mediaRecorder.start();
      setIsRecording(true);
    } catch (error) {
      console.error('Error accessing microphone:', error);
      alert('Could not access microphone. Please check permissions.');
    }
  };
  
  // Stop recording and process audio
  const stopRecording = async () => {
    if (!mediaRecorderRef.current) return;
    
    return new Promise((resolve) => {
      mediaRecorderRef.current.onstop = async () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
        
        // Create form data to send to backend
        const formData = new FormData();
        formData.append('audio', audioBlob);
        
        setIsRecording(false);
        setIsTranscribing(true);
        
        try {
          // Send audio to backend for transcription
          const response = await axios.post('http://localhost:5000/transcribe_audio', formData, {
            headers: {
              'Content-Type': 'multipart/form-data'
            }
          });
          
          const transcribedText = response.data.text;
          
          // If shift key was pressed, put text in input field
          if (shiftKeyPressed) {
            setMessage(transcribedText);
          } else {
            // Otherwise, send message automatically
            onSendMessage(transcribedText);
          }
          
          resolve(transcribedText);
        } catch (error) {
          console.error('Error transcribing audio:', error);
          alert('Error transcribing audio. Please try again.');
          resolve(null);
        } finally {
          setIsTranscribing(false);
          
          // Stop all audio tracks
          mediaRecorderRef.current.stream.getTracks().forEach(track => track.stop());
        }
      };
      
      mediaRecorderRef.current.stop();
    });
  };
  
  // Handle mouse events for the microphone button
  const handleMicMouseDown = (e) => {
    e.preventDefault();
    startRecording();
  };
  
  const handleMicMouseUp = (e) => {
    e.preventDefault();
    if (isRecording) {
      stopRecording();
    }
  };
  
  // Handle touch events for mobile devices
  const handleMicTouchStart = (e) => {
    e.preventDefault();
    startRecording();
  };
  
  const handleMicTouchEnd = (e) => {
    e.preventDefault();
    if (isRecording) {
      stopRecording();
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
        disabled={isLoading || isRecording || isTranscribing}
      />
      <Button
        type="primary"
        icon={isLoading ? <LoadingOutlined /> : <SendOutlined />}
        onClick={handleSend}
        loading={isLoading}
        disabled={isLoading || isRecording || isTranscribing || !message.trim()}
        style={{ marginRight: '8px' }}
      />
      <Button
        type={isRecording ? "danger" : "default"}
        icon={<AudioOutlined />}
        onMouseDown={handleMicMouseDown}
        onMouseUp={handleMicMouseUp}
        onMouseLeave={isRecording ? handleMicMouseUp : undefined}
        onTouchStart={handleMicTouchStart}
        onTouchEnd={handleMicTouchEnd}
        disabled={isLoading || isTranscribing}
        className={`mic-button ${isRecording ? 'recording' : ''} ${shiftKeyPressed ? 'shift-pressed' : ''}`}
        title={shiftKeyPressed ? "Release to transcribe to input field" : "Hold to record, release to send"}
      />
    </div>
  );
};

export default MessageInput;