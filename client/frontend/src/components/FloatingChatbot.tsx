import React, { useState } from 'react';
import ChatbotInterface from './ChatbotInterface';

interface FloatingChatbotProps {
  page: string;
  onFieldUpdate?: (field: string, value: string) => void;
  onComplete?: () => void;
}

const FloatingChatbot: React.FC<FloatingChatbotProps> = ({ page, onFieldUpdate, onComplete }) => {
  const [isOpen, setIsOpen] = useState(false);

  const toggleChat = () => {
    setIsOpen(!isOpen);
  };

  return (
    <>
      {/* 플로팅 아이콘 */}
      <div
        onClick={toggleChat}
        style={{
          position: 'fixed',
          bottom: '24px',
          right: '24px',
          width: '64px',
          height: '64px',
          backgroundColor: '#2563eb',
          borderRadius: '50%',
          boxShadow: '0 10px 25px rgba(0, 0, 0, 0.2)',
          cursor: 'pointer',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 9999,
          transition: 'all 0.3s ease'
        }}
        onMouseEnter={(e) => {
          e.currentTarget.style.backgroundColor = '#1d4ed8';
          e.currentTarget.style.transform = 'scale(1.1)';
        }}
        onMouseLeave={(e) => {
          e.currentTarget.style.backgroundColor = '#2563eb';
          e.currentTarget.style.transform = 'scale(1)';
        }}
      >
        <div style={{ color: 'white', fontSize: '24px' }}>
          {isOpen ? '✕' : '💬'}
        </div>
      </div>

      {/* 모달 채팅창 */}
      <div
        style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          backgroundColor: 'rgba(0, 0, 0, 0.5)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 9998,
          padding: '16px',
          opacity: isOpen ? 1 : 0,
          pointerEvents: isOpen ? 'auto' : 'none',
          transition: 'opacity 0.3s ease'
        }}
      >
        <div style={{
          backgroundColor: 'white',
          borderRadius: '12px',
          boxShadow: '0 20px 60px rgba(0, 0, 0, 0.3)',
          width: '100%',
          maxWidth: '500px',
          height: '600px',
          display: 'flex',
          flexDirection: 'column',
          overflow: 'hidden'
        }}>
          {/* 헤더 */}
          <div style={{
            padding: '16px',
            borderBottom: '1px solid #e5e7eb',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            flexShrink: 0
          }}>
            <h3 style={{ fontSize: '18px', fontWeight: '600', color: '#1f2937', margin: 0 }}>
              AI 챗봇
            </h3>
            <button
              onClick={toggleChat}
              style={{
                background: 'none',
                border: 'none',
                fontSize: '18px',
                color: '#6b7280',
                cursor: 'pointer',
                padding: '4px'
              }}
            >
              ✕
            </button>
          </div>
          
          {/* 채팅 인터페이스 */}
          <div style={{ flex: 1, overflow: 'hidden' }}>
            <ChatbotInterface
              page={page}
              onFieldUpdate={onFieldUpdate}
              onComplete={onComplete}
            />
          </div>
        </div>
      </div>
    </>
  );
};

export default FloatingChatbot; 