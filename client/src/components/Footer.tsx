import React from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { 
  faEnvelope, 
  faPhone, 
  faMapMarkerAlt 
} from '@fortawesome/free-solid-svg-icons';
import './Footer.css';

const Footer: React.FC = () => {
  return (
    <footer className="footer">
      <div className="footer-container">
        <div className="footer-grid">
          {/* 회사 정보 */}
          <div className="footer-section">
            <h6 className="footer-title">HireMe</h6>
            <p className="footer-description">
              AI 기반 채용 관리 시스템으로 더 나은 인재 발굴을 도와드립니다.
            </p>
            <div className="social-links">
              <button className="social-button">
                <FontAwesomeIcon icon={faEnvelope} />
              </button>
              <button className="social-button">
                <FontAwesomeIcon icon={faPhone} />
              </button>
              <button className="social-button">
                <FontAwesomeIcon icon={faMapMarkerAlt} />
              </button>
            </div>
          </div>

          {/* 빠른 링크 */}
          <div className="footer-section">
            <h6 className="footer-title">서비스</h6>
            <a href="/jobs" className="footer-link">채용 공고</a>
            <a href="/applications" className="footer-link">지원서 관리</a>
            <a href="/portfolio" className="footer-link">포트폴리오</a>
            <a href="/recommendations" className="footer-link">인재 추천</a>
          </div>

          {/* 면접 관리 */}
          <div className="footer-section">
            <h6 className="footer-title">면접 관리</h6>
            <a href="/interviews" className="footer-link">면접 일정</a>
            <a href="/interviews" className="footer-link">Zoom 면접</a>
            <a href="/interviews" className="footer-link">영상 면접</a>
            <a href="/interviews" className="footer-link">대면 면접</a>
          </div>

          {/* 고객센터 */}
          <div className="footer-section">
            <h6 className="footer-title">고객센터</h6>
            <p className="footer-info">고객센터: 1588-1234</p>
            <p className="footer-info">업무시간: 평일 9시 ~ 18시</p>
          </div>
        </div>

        <div className="footer-divider"></div>

        {/* 하단 정보 */}
        <div className="footer-bottom">
          <p className="footer-copyright">
            © 2024 HireMe. All Rights Reserved.
          </p>
          <p className="footer-address">
            (12345) 서울특별시 강남구 테헤란로 123 HireMe 빌딩
          </p>
        </div>
      </div>
    </footer>
  );
};

export default Footer; 