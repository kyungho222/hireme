import React from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { 
  faUser, 
  faBriefcase, 
  faFileAlt, 
  faChartBar, 
  faBell, 
  faCog 
} from '@fortawesome/free-solid-svg-icons';
import './MyPage.css';

const MyPage: React.FC = () => {
  const menuItems = [
    {
      icon: faUser,
      text: '내 정보 관리',
      description: '개인정보 및 계정 설정',
    },
    {
      icon: faBriefcase,
      text: '채용 현황',
      description: '진행 중인 채용 현황 확인',
    },
    {
      icon: faFileAlt,
      text: '이력서 관리',
      description: '등록된 이력서 및 포트폴리오',
    },
    {
      icon: faChartBar,
      text: '채용 분석',
      description: '채용 성과 및 통계 분석',
    },
    {
      icon: faBell,
      text: '알림 설정',
      description: '채용 관련 알림 관리',
    },
    {
      icon: faCog,
      text: '설정',
      description: '서비스 이용 설정',
    },
  ];

  const recentActivities = [
    {
      icon: faBriefcase,
      title: 'IT 개발자 채용 공고 등록',
      time: '2024.01.20 14:30',
    },
    {
      icon: faFileAlt,
      title: '지원자 이력서 검토 완료',
      time: '2024.01.19 16:45',
    },
    {
      icon: faChartBar,
      title: '채용 분석 리포트 생성',
      time: '2024.01.18 09:15',
    },
  ];

  return (
    <div className="mypage-container">
      <div className="mypage-header">
        <h1 className="mypage-title">My HireMe</h1>
        <p className="mypage-subtitle">
          개인화된 채용 관리 서비스를 이용해보세요
        </p>
      </div>

      {/* 사용자 정보 카드 */}
      <div className="user-info-card">
        <div className="user-info-content">
          <div className="user-info-main">
            <FontAwesomeIcon 
              icon={faUser} 
              className="user-icon"
            />
            <div className="user-details">
              <h6 className="user-name">홍길동님</h6>
              <p className="user-info">기업 계정 | 가입일: 2024.01.15</p>
            </div>
          </div>
          <div className="user-actions">
            <button className="btn btn-outline btn-small">프로필 수정</button>
            <button className="btn btn-outline btn-small">계정 설정</button>
          </div>
        </div>
      </div>

      {/* 메뉴 리스트 */}
      <div className="menu-grid">
        {menuItems.map((item, index) => (
          <div key={index} className="menu-card">
            <div className="menu-content">
              <div className="menu-item">
                <FontAwesomeIcon 
                  icon={item.icon} 
                  className="menu-icon"
                />
                <div className="menu-text">
                  <h6 className="menu-title">{item.text}</h6>
                  <p className="menu-description">{item.description}</p>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* 최근 활동 */}
      <div className="recent-activities-card">
        <div className="recent-activities-content">
          <h5 className="recent-activities-title">최근 활동</h5>
          <div className="activities-list">
            {recentActivities.map((activity, index) => (
              <div key={index} className="activity-item">
                <div className="activity-icon">
                  <FontAwesomeIcon icon={activity.icon} className="activity-icon-svg" />
                </div>
                <div className="activity-text">
                  <p className="activity-title">{activity.title}</p>
                  <p className="activity-time">{activity.time}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default MyPage; 