import React from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { 
  faUsers, 
  faChartLine, 
  faBuilding, 
  faHeadset 
} from '@fortawesome/free-solid-svg-icons';
import FloatingChatbot from '../components/FloatingChatbot';
import './Home.css';

const Home: React.FC = () => {
  return (
    <div className="home">
      {/* 히어로 섹션 */}
      <div className="hero-section">
        <div className="hero-content">
          <h5 className="hero-title">
            더 나은 인재 발굴을 위한 스마트한 솔루션
          </h5>
          <h6 className="hero-subtitle">
            AI 기술을 활용한 효율적인 채용 관리 시스템
          </h6>
          <div className="hero-buttons">
            <button className="btn btn-primary btn-large">
              무료 체험하기
            </button>
            <button className="btn btn-outline btn-large">
              서비스 소개
            </button>
          </div>
        </div>
      </div>

      {/* 주요 기능 */}
      <div className="features-section">
        <div className="features-container">
          <h2 className="section-title">주요 기능</h2>
          <div className="features-grid">
            <div className="feature-card">
              <div className="feature-content">
                <FontAwesomeIcon 
                  icon={faUsers} 
                  className="feature-icon"
                />
                <h6 className="feature-title">스마트 매칭</h6>
                <p className="feature-description">
                  AI가 지원자와 직무를 최적화하여 매칭해드립니다
                </p>
              </div>
            </div>

            <div className="feature-card">
              <div className="feature-content">
                <FontAwesomeIcon 
                  icon={faChartLine} 
                  className="feature-icon"
                />
                <h6 className="feature-title">실시간 분석</h6>
                <p className="feature-description">
                  채용 과정의 모든 데이터를 실시간으로 분석합니다
                </p>
              </div>
            </div>

            <div className="feature-card">
              <div className="feature-content">
                <FontAwesomeIcon 
                  icon={faBuilding} 
                  className="feature-icon"
                />
                <h6 className="feature-title">기업 맞춤형</h6>
                <p className="feature-description">
                  기업의 특성에 맞는 맞춤형 채용 솔루션을 제공합니다
                </p>
              </div>
            </div>

            <div className="feature-card">
              <div className="feature-content">
                <FontAwesomeIcon 
                  icon={faHeadset} 
                  className="feature-icon"
                />
                <h6 className="feature-title">24/7 지원</h6>
                <p className="feature-description">
                  언제든지 전문가의 도움을 받을 수 있습니다
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* 통계 섹션 */}
      <div className="stats-section">
        <div className="stats-container">
          <h2 className="section-title">신뢰받는 서비스</h2>
          <div className="stats-grid">
            <div className="stat-item">
              <h3 className="stat-number">500+</h3>
              <p className="stat-label">기업 고객</p>
            </div>
            <div className="stat-item">
              <h3 className="stat-number">10,000+</h3>
              <p className="stat-label">성공 매칭</p>
            </div>
            <div className="stat-item">
              <h3 className="stat-number">98%</h3>
              <p className="stat-label">고객 만족도</p>
            </div>
            <div className="stat-item">
              <h3 className="stat-number">24/7</h3>
              <p className="stat-label">고객 지원</p>
            </div>
          </div>
        </div>
      </div>

      {/* CTA 섹션 */}
      <div className="cta-section">
        <div className="cta-container">
          <h2 className="section-title">지금 시작해보세요</h2>
          <h6 className="cta-subtitle">
            AI 기반 채용 관리로 더 나은 인재를 찾아보세요
          </h6>
          <button className="btn btn-primary btn-large">
            무료로 시작하기
          </button>
        </div>
      </div>

      {/* 플로팅 챗봇 */}
      <FloatingChatbot
        page="home"
        onFieldUpdate={(field, value) => {
          console.log('챗봇 입력:', field, value);
        }}
        onComplete={() => {
          console.log('챗봇 대화 완료');
        }}
      />
    </div>
  );
};

export default Home; 