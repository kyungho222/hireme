import React, { useState, useRef, useEffect } from 'react';

const FloatingChatbot = ({ page, onFieldUpdate, onComplete }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const inputRef = useRef(null);
  const messagesEndRef = useRef(null);

  // 디버깅용 로그
  console.log('FloatingChatbot 렌더링됨, page:', page);

  // 챗봇이 처음 열릴 때 환영 메시지 추가
  const handleOpenChat = async () => {
    if (!isOpen && messages.length === 0) {
      // 환영 메시지 추가
      const welcomeMessage = {
        type: 'bot',
        content: getWelcomeMessage(page),
        timestamp: new Date()
      };
      setMessages([welcomeMessage]);
    }
    setIsOpen(true);
  };

  const getWelcomeMessage = (currentPage) => {
    const welcomeMessages = {
      'dashboard': `안녕하세요! 대시보드에서 어떤 도움이 필요하신가요?

📊 현재 현황을 확인하거나 다음 질문들을 해보세요:
• "현재 등록된 채용공고는 몇 개인가요?"
• "지원자 통계를 보여주세요"
• "면접 일정을 확인해주세요"`,
      
      'job-posting': `채용공고 등록을 도와드리겠습니다! 🎯

다음 질문들을 해보세요:
• "채용공고 등록 방법을 알려주세요"
• "어떤 부서에서 채용하시나요?"
• "채용공고 작성 팁을 알려주세요"
• "새로운 채용공고를 등록하고 싶어요"`,
      
      'resume': `이력서 관리에 대해 도움을 드리겠습니다! 📄

다음 질문들을 해보세요:
• "지원자 이력서를 어떻게 확인하나요?"
• "이력서 검토 방법을 알려주세요"
• "지원자 현황을 보여주세요"
• "이력서 필터링 기능이 있나요?"`,
      
      'interview': `면접 관리에 대해 문의하실 내용이 있으신가요? 🎤

다음 질문들을 해보세요:
• "면접 일정을 확인해주세요"
• "면접 평가 방법을 알려주세요"
• "면접 결과를 입력하고 싶어요"
• "면접 준비사항을 알려주세요"`,
      
      'portfolio': `포트폴리오 분석에 대해 도움을 드리겠습니다! 💼

다음 질문들을 해보세요:
• "포트폴리오 분석 기능이 뭔가요?"
• "지원자 포트폴리오를 어떻게 확인하나요?"
• "포트폴리오 평가 기준을 알려주세요"`,
      
      'cover-letter': `자기소개서 검증에 대해 문의하실 내용이 있으신가요? ✍️

다음 질문들을 해보세요:
• "자기소개서 검증 기능이 뭔가요?"
• "자소서 평가 방법을 알려주세요"
• "자소서 작성 팁을 알려주세요"`,
      
      'talent': `인재 추천에 대해 도움을 드리겠습니다! 👥

다음 질문들을 해보세요:
• "인재 추천 시스템이 어떻게 작동하나요?"
• "추천 인재를 확인하고 싶어요"
• "인재 매칭 기준을 알려주세요"`,
      
      'users': `사용자 관리에 대해 문의하실 내용이 있으신가요? 👤

다음 질문들을 해보세요:
• "사용자 목록을 확인해주세요"
• "새로운 사용자를 추가하고 싶어요"
• "사용자 권한을 변경하고 싶어요"`,
      
      'settings': `설정에 대해 도움을 드리겠습니다! ⚙️

다음 질문들을 해보세요:
• "시스템 설정을 변경하고 싶어요"
• "알림 설정을 확인해주세요"
• "백업 설정을 알려주세요"`
    };
    
    return welcomeMessages[currentPage] || '안녕하세요! 어떤 도움이 필요하신가요?';
  };

  // 자동 스크롤 함수
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  // 메시지가 추가될 때마다 자동 스크롤
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // 입력창 포커스 함수
  const focusInput = () => {
    inputRef.current?.focus();
  };

  const toggleChat = () => {
    console.log('챗봇 토글 클릭됨, 현재 상태:', isOpen);
    if (!isOpen) {
      handleOpenChat();
    } else {
      setIsOpen(false);
    }
    console.log('챗봇 상태 변경됨:', !isOpen);
  };

  const sendMessage = async () => {
    if (!inputValue.trim()) return;

    const userMessage = {
      type: 'user',
      content: inputValue,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    // 백엔드 API 호출 (기존 백엔드 사용)
    try {
      const response = await fetch('/api/chatbot/ask', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: inputValue,
          page: page
        })
      });

      const data = await response.json();
      
      const botMessage = {
        type: 'bot',
        content: data.response,
        timestamp: new Date()
      };

      setMessages(prev => [...prev, botMessage]);
    } catch (error) {
      console.error('챗봇 API 호출 실패:', error);
      const errorMessage = {
        type: 'bot',
        content: '죄송합니다. 일시적인 오류가 발생했습니다.',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
      // 전송 완료 후 입력창에 포커스
      setTimeout(() => {
        focusInput();
      }, 100);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
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
          backgroundColor: '#ff4444',
          borderRadius: '50%',
          boxShadow: '0 10px 25px rgba(255, 68, 68, 0.4)',
          cursor: 'pointer',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 99999,
          transition: 'all 0.3s ease',
          border: '3px solid white'
        }}
        onMouseEnter={(e) => {
          e.currentTarget.style.backgroundColor = '#ff0000';
          e.currentTarget.style.transform = 'scale(1.1)';
        }}
        onMouseLeave={(e) => {
          e.currentTarget.style.backgroundColor = '#ff4444';
          e.currentTarget.style.transform = 'scale(1)';
        }}
      >
        <div style={{ color: 'white', fontSize: '24px', fontWeight: 'bold' }}>
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
              </div>

              {/* 입력 영역 */}
              <div style={{ 
                borderTop: '1px solid #e5e7eb', 
                padding: '16px', 
                flexShrink: 0 
              }}>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                  <textarea
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
          </div>
        </div>
      </div>
    </>
  );
};

export default FloatingChatbot; 