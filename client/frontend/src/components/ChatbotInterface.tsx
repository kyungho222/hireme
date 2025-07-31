import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';

interface ChatbotInterfaceProps {
  page: string;
  onFieldUpdate?: (field: string, value: string) => void;
  onComplete?: () => void;
}

interface Message {
  type: 'user' | 'bot';
  content: string;
  timestamp: Date;
}

const ChatbotInterface: React.FC<ChatbotInterfaceProps> = ({ page, onFieldUpdate, onComplete }) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [currentField, setCurrentField] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  const scrollToBottom = () => {
    const messagesContainer = messagesEndRef.current?.parentElement;
    if (messagesContainer) {
      messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }
  };

  // 메시지가 추가될 때 스크롤
  useEffect(() => {
    if (messages.length > 0) {
      const timer = setTimeout(() => {
        scrollToBottom();
      }, 100);
      return () => clearTimeout(timer);
    }
  }, [messages]);

  useEffect(() => {
    startSession();
  }, [page]);

  // 입력 필드에 자동 포커스
  useEffect(() => {
    if (!isLoading && inputRef.current) {
      const timer = setTimeout(() => {
        inputRef.current?.focus();
      }, 50);
      return () => clearTimeout(timer);
    }
  }, [isLoading]);

  const startSession = async () => {
    try {
      setIsLoading(true);
      const response = await axios.post('/api/chatbot/start', { page });
      setSessionId(response.data.session_id);
      setCurrentField(response.data.current_field);

      setMessages([
        {
          type: 'bot',
          content: response.data.question,
          timestamp: new Date()
        }
      ]);
    } catch (error) {
      console.error('세션 시작 오류:', error);
      setMessages([
        {
          type: 'bot',
          content: '죄송합니다. 세션을 시작할 수 없습니다.',
          timestamp: new Date()
        }
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const sendMessage = async () => {
    if (!inputValue.trim() || isLoading) return;

    const userMessage: Message = {
      type: 'user',
      content: inputValue,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    try {
      const response = await axios.post('/api/chatbot/ask', {
        page,
        user_input: inputValue,
        session_id: sessionId
      });

      const botMessage: Message = {
        type: 'bot',
        content: response.data.message,
        timestamp: new Date()
      };

      setMessages(prev => [...prev, botMessage]);

      // 필드 값이 업데이트된 경우
      if (response.data.value) {
        onFieldUpdate?.(response.data.field, response.data.value);
        setCurrentField(response.data.field);
      }

      // 모든 입력이 완료된 경우
      if (response.data.message.includes('모든 질문에 답변해 주셔서 감사합니다')) {
        onComplete?.();
      }

    } catch (error) {
      console.error('메시지 전송 오류:', error);
      const errorMessage: Message = {
        type: 'bot',
        content: '죄송합니다. 처리 중 오류가 발생했습니다.',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
      {/* 채팅 메시지 영역 */}
      <div style={{ 
        flex: 1, 
        overflowY: 'auto', 
        padding: '16px', 
        display: 'flex', 
        flexDirection: 'column', 
        gap: '16px',
        minHeight: 0 
      }}>
        {messages.map((message, index) => (
          <div
            key={index}
            style={{ 
              display: 'flex', 
              justifyContent: message.type === 'user' ? 'flex-end' : 'flex-start' 
            }}
          >
            <div style={{
              maxWidth: '280px',
              padding: '8px 16px',
              borderRadius: '8px',
              backgroundColor: message.type === 'user' ? '#2563eb' : '#f3f4f6',
              color: message.type === 'user' ? 'white' : '#1f2937'
            }}>
              <div style={{ fontSize: '14px', whiteSpace: 'pre-wrap' }}>
                {message.content}
              </div>
              <div style={{ fontSize: '12px', opacity: 0.7, marginTop: '4px' }}>
                {message.timestamp.toLocaleTimeString()}
              </div>
            </div>
          </div>
        ))}

        {isLoading && (
          <div style={{ display: 'flex', justifyContent: 'flex-start' }}>
            <div style={{
              backgroundColor: '#f3f4f6',
              color: '#1f2937',
              padding: '8px 16px',
              borderRadius: '8px'
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <div style={{
                  width: '16px',
                  height: '16px',
                  border: '2px solid #d1d5db',
                  borderTop: '2px solid #4b5563',
                  borderRadius: '50%',
                  animation: 'spin 1s linear infinite'
                }}></div>
                <span style={{ fontSize: '14px' }}>입력 중...</span>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* 입력 영역 */}
      <div style={{ 
        borderTop: '1px solid #e5e7eb', 
        padding: '16px', 
        flexShrink: 0 
      }}>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
          <textarea
            ref={inputRef}
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="메시지를 입력하세요..."
            style={{
              width: '100%',
              padding: '8px 16px',
              border: '1px solid #d1d5db',
              borderRadius: '8px',
              fontSize: '14px',
              resize: 'none',
              outline: 'none'
            }}
            rows={3}
            disabled={isLoading}
          />
          <button
            onClick={sendMessage}
            disabled={isLoading || !inputValue.trim()}
            style={{
              padding: '8px 24px',
              backgroundColor: '#2563eb',
              color: 'white',
              border: 'none',
              borderRadius: '8px',
              fontSize: '14px',
              fontWeight: '600',
              cursor: 'pointer',
              alignSelf: 'flex-end',
              opacity: (isLoading || !inputValue.trim()) ? 0.5 : 1
            }}
          >
            전송
          </button>
        </div>
      </div>
    </div>
  );
};

export default ChatbotInterface; 