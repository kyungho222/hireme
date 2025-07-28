import React, { useState } from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { 
  faPhone, 
  faEnvelope, 
  faComments, 
  faChevronDown 
} from '@fortawesome/free-solid-svg-icons';
import './CustomerService.css';

const CustomerService: React.FC = () => {
  const [expandedFaq, setExpandedFaq] = useState<number | null>(null);

  const faqs = [
    {
      question: 'HireMe 서비스는 어떻게 이용하나요?',
      answer: '회원가입 후 기업 정보를 등록하고, 원하는 인재 유형을 선택하면 AI가 최적의 매칭을 제공합니다.',
    },
    {
      question: '채용 비용은 얼마인가요?',
      answer: '기본 플랜은 월 30만원부터 시작하며, 기업 규모와 요구사항에 따라 맞춤형 가격을 제공합니다.',
    },
    {
      question: 'AI 매칭의 정확도는 어느 정도인가요?',
      answer: '평균 85% 이상의 높은 매칭 정확도를 보이며, 지속적인 학습을 통해 정확도가 향상되고 있습니다.',
    },
    {
      question: '지원자 이력서는 어떻게 관리되나요?',
      answer: '모든 지원자 정보는 암호화되어 안전하게 보관되며, GDPR 및 개인정보보호법을 준수합니다.',
    },
  ];

  const toggleFaq = (index: number) => {
    setExpandedFaq(expandedFaq === index ? null : index);
  };

  return (
    <div className="customer-service-container">
      <div className="customer-service-header">
        <h1 className="customer-service-title">고객센터</h1>
        <p className="customer-service-subtitle">
          언제든지 도움을 받으실 수 있습니다
        </p>
      </div>

      {/* 연락처 정보 */}
      <div className="contact-grid">
        <div className="contact-card">
          <div className="contact-content">
            <FontAwesomeIcon 
              icon={faPhone} 
              className="contact-icon"
            />
            <h6 className="contact-title">전화 문의</h6>
            <p className="contact-info">1588-1234</p>
            <p className="contact-description">평일 9시 ~ 18시</p>
          </div>
        </div>

        <div className="contact-card">
          <div className="contact-content">
            <FontAwesomeIcon 
              icon={faEnvelope} 
              className="contact-icon"
            />
            <h6 className="contact-title">이메일 문의</h6>
            <p className="contact-info">support@hireme.com</p>
            <p className="contact-description">24시간 접수 가능</p>
          </div>
        </div>

        <div className="contact-card">
          <div className="contact-content">
            <FontAwesomeIcon 
              icon={faComments} 
              className="contact-icon"
            />
            <h6 className="contact-title">실시간 채팅</h6>
            <p className="contact-info">채팅 상담</p>
            <p className="contact-description">평일 9시 ~ 18시</p>
          </div>
        </div>
      </div>

      {/* 문의 폼 */}
      <div className="inquiry-card">
        <div className="inquiry-content">
          <h5 className="inquiry-title">문의하기</h5>
          <form className="inquiry-form">
            <div className="form-grid">
              <div className="form-field">
                <label className="form-label">이름</label>
                <input
                  type="text"
                  className="form-input"
                  required
                />
              </div>
              <div className="form-field">
                <label className="form-label">이메일</label>
                <input
                  type="email"
                  className="form-input"
                  required
                />
              </div>
            </div>
            
            <div className="form-field">
              <label className="form-label">제목</label>
              <input
                type="text"
                className="form-input"
                required
              />
            </div>
            
            <div className="form-field">
              <label className="form-label">문의 내용</label>
              <textarea
                className="form-textarea"
                rows={4}
                required
              />
            </div>
            
            <button type="submit" className="btn btn-primary btn-large">
              문의하기
            </button>
          </form>
        </div>
      </div>

      {/* FAQ */}
      <div className="faq-card">
        <div className="faq-content">
          <h5 className="faq-title">자주 묻는 질문</h5>
          <div className="faq-list">
            {faqs.map((faq, index) => (
              <div key={index} className="faq-item">
                <button
                  className={`faq-question ${expandedFaq === index ? 'expanded' : ''}`}
                  onClick={() => toggleFaq(index)}
                >
                  <span className="faq-question-text">{faq.question}</span>
                  <FontAwesomeIcon 
                    icon={faChevronDown} 
                    className={`faq-icon ${expandedFaq === index ? 'rotated' : ''}`}
                  />
                </button>
                {expandedFaq === index && (
                  <div className="faq-answer">
                    <p>{faq.answer}</p>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default CustomerService; 