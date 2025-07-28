import React from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { 
  faUser, 
  faStar, 
  faMapMarkerAlt, 
  faBriefcase,
  faCheckCircle
} from '@fortawesome/free-solid-svg-icons';
import './Recommendations.css';

const Recommendations: React.FC = () => {
  const recommendations = [
    {
      id: 1,
      name: '김개발',
      position: '프론트엔드 개발자',
      experience: '3년',
      location: '서울 강남구',
      skills: ['React', 'TypeScript', 'JavaScript', 'HTML/CSS'],
      matchRate: 95,
      avatar: 'https://via.placeholder.com/60',
      description: 'React와 TypeScript에 능숙하며, 사용자 경험을 중시하는 개발자입니다.',
      rating: 4.8,
    },
    {
      id: 2,
      name: '이백엔드',
      position: '백엔드 개발자',
      experience: '5년',
      location: '서울 서초구',
      skills: ['Java', 'Spring Boot', 'MySQL', 'AWS'],
      matchRate: 92,
      avatar: 'https://via.placeholder.com/60',
      description: 'Java와 Spring Boot를 활용한 안정적인 서버 개발 경험이 풍부합니다.',
      rating: 4.9,
    },
    {
      id: 3,
      name: '박디자인',
      position: 'UI/UX 디자이너',
      experience: '4년',
      location: '서울 마포구',
      skills: ['Figma', 'Adobe XD', 'Photoshop', 'Illustrator'],
      matchRate: 88,
      avatar: 'https://via.placeholder.com/60',
      description: '사용자 중심의 디자인을 추구하며, 직관적인 인터페이스를 설계합니다.',
      rating: 4.7,
    },
    {
      id: 4,
      name: '최데이터',
      position: '데이터 분석가',
      experience: '6년',
      location: '서울 영등포구',
      skills: ['Python', 'SQL', 'R', 'Tableau'],
      matchRate: 90,
      avatar: 'https://via.placeholder.com/60',
      description: '빅데이터 분석과 인사이트 도출에 전문성을 가지고 있습니다.',
      rating: 4.8,
    },
  ];

  return (
    <div className="recommendations-container">
      <div className="recommendations-header">
        <h1 className="recommendations-title">인재 추천</h1>
        <p className="recommendations-subtitle">
          AI가 분석한 최적의 인재를 추천해드립니다
        </p>
      </div>

      {/* 필터 옵션 */}
      <div className="filter-card">
        <div className="filter-content">
          <h6 className="filter-title">추천 조건 설정</h6>
          <div className="filter-buttons">
            <button className="btn btn-primary btn-small">전체</button>
            <button className="btn btn-outline btn-small">개발자</button>
            <button className="btn btn-outline btn-small">디자이너</button>
            <button className="btn btn-outline btn-small">데이터 분석가</button>
            <button className="btn btn-outline btn-small">경력 3년 이상</button>
            <button className="btn btn-outline btn-small">서울 지역</button>
          </div>
        </div>
      </div>

      {/* 추천 인재 목록 */}
      <div className="recommendations-list">
        {recommendations.map((person) => (
          <div key={person.id} className="recommendation-card">
            <div className="recommendation-content">
              <div className="recommendation-header">
                <img
                  src={person.avatar}
                  alt={person.name}
                  className="recommendation-avatar"
                />
                
                <div className="recommendation-info">
                  <div className="recommendation-main">
                    <div className="recommendation-details">
                      <h6 className="recommendation-name">{person.name}</h6>
                      <p className="recommendation-position">{person.position}</p>
                    </div>
                    <div className="recommendation-match">
                      <h5 className="match-rate">{person.matchRate}%</h5>
                      <p className="match-label">매칭률</p>
                    </div>
                  </div>

                  <div className="recommendation-meta">
                    <div className="meta-item">
                      <FontAwesomeIcon icon={faBriefcase} className="meta-icon" />
                      <span className="meta-text">{person.experience} 경력</span>
                    </div>
                    <div className="meta-item">
                      <FontAwesomeIcon icon={faMapMarkerAlt} className="meta-icon" />
                      <span className="meta-text">{person.location}</span>
                    </div>
                    <div className="meta-item">
                      <FontAwesomeIcon icon={faStar} className="meta-icon star" />
                      <span className="meta-text">{person.rating}</span>
                    </div>
                  </div>

                  <p className="recommendation-description">
                    {person.description}
                  </p>

                  <div className="skills-container">
                    {person.skills.map((skill, index) => (
                      <span key={index} className="skill-chip">
                        {skill}
                      </span>
                    ))}
                  </div>

                  <div className="recommendation-actions">
                    <button className="btn btn-primary">
                      <FontAwesomeIcon icon={faCheckCircle} />
                      추천하기
                    </button>
                    <button className="btn btn-outline">상세보기</button>
                    <button className="btn btn-outline">메시지 보내기</button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* 통계 */}
      <div className="stats-card">
        <div className="stats-content">
          <h5 className="stats-title">추천 통계</h5>
          
          <div className="stats-grid">
            <div className="stat-item">
              <h4 className="stat-number">{recommendations.length}</h4>
              <p className="stat-label">추천 인재</p>
            </div>
            
            <div className="stat-item">
              <h4 className="stat-number">
                {Math.round(recommendations.reduce((sum, person) => sum + person.matchRate, 0) / recommendations.length)}
              </h4>
              <p className="stat-label">평균 매칭률</p>
            </div>
            
            <div className="stat-item">
              <h4 className="stat-number">
                {Math.round(recommendations.reduce((sum, person) => sum + person.rating, 0) / recommendations.length * 10) / 10}
              </h4>
              <p className="stat-label">평균 평점</p>
            </div>
            
            <div className="stat-item">
              <h4 className="stat-number">4개</h4>
              <p className="stat-label">직무 분야</p>
            </div>
          </div>
        </div>
      </div>

      {/* 추가 정보 */}
      <div className="additional-info">
        <h5 className="additional-title">더 정확한 추천을 원하시나요?</h5>
        <p className="additional-description">
          상세한 요구사항을 입력하면 더 정확한 인재를 추천해드립니다.
        </p>
        <button className="btn btn-primary btn-large">
          상세 요구사항 입력
        </button>
      </div>
    </div>
  );
};

export default Recommendations; 