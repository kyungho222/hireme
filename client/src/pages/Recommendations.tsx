import React, { useState, useEffect } from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { 
  faUser, 
  faStar, 
  faMapMarkerAlt, 
  faBriefcase,
  faCheckCircle,
  faPlus
} from '@fortawesome/free-solid-svg-icons';
import axios from 'axios';
import './Recommendations.css';

interface Talent {
  id: number;
  name: string;
  position: string;
  experience: string;
  location: string;
  skills: string[];
  matchRate: number;
  avatar: string;
  description: string;
  rating: number;
  aiTags?: string[];
}

interface TalentFormData {
  name: string;
  position: string;
  experience: string;
  location: string;
  skills: string[];
  description: string;
}

const Recommendations: React.FC = () => {
  const [recommendations, setRecommendations] = useState<Talent[]>([]);
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState<TalentFormData>({
    name: '',
    position: '',
    experience: '',
    location: '',
    skills: [],
    description: ''
  });

  useEffect(() => {
    fetchRecommendations();
  }, []);

  const fetchRecommendations = async () => {
    try {
      const response = await axios.get('/api/recommendations');
      setRecommendations(response.data);
    } catch (error) {
      console.error('Failed to fetch recommendations:', error);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await axios.post('/api/recommendations', formData);
      setShowForm(false);
      fetchRecommendations();
    } catch (error) {
      console.error('Failed to submit talent data:', error);
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: name === 'skills' ? value.split(',').map(s => s.trim()) : value
    }));
  };

  // 기존의 샘플 데이터는 임시로 유지
  const sampleRecommendations = [
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
      {/* 왼쪽 사이드바 */}
      <div className="recommendations-sidebar">
        <div className="sidebar-header">
          <h1 className="recommendations-title">인재 추천</h1>
          <p className="recommendations-subtitle">
            AI가 분석한 최적의 인재를 추천해드립니다
          </p>
        </div>

        {/* 필터 옵션 */}
        <div className="filter-section">
          <h6 className="section-title">직무 분야</h6>
          <div className="filter-buttons vertical">
            <button className="btn btn-primary btn-small">전체</button>
            <button className="btn btn-outline btn-small">개발자</button>
            <button className="btn btn-outline btn-small">디자이너</button>
            <button className="btn btn-outline btn-small">데이터 분석가</button>
          </div>

          <h6 className="section-title">경력</h6>
          <div className="filter-buttons vertical">
            <button className="btn btn-outline btn-small">전체</button>
            <button className="btn btn-outline btn-small">신입</button>
            <button className="btn btn-outline btn-small">1-3년</button>
            <button className="btn btn-outline btn-small">3-5년</button>
            <button className="btn btn-outline btn-small">5년 이상</button>
          </div>

          <h6 className="section-title">지역</h6>
          <div className="filter-buttons vertical">
            <button className="btn btn-outline btn-small">전체</button>
            <button className="btn btn-outline btn-small">서울</button>
            <button className="btn btn-outline btn-small">경기</button>
            <button className="btn btn-outline btn-small">인천</button>
            <button className="btn btn-outline btn-small">기타 지역</button>
          </div>
        </div>

        {/* 통계 섹션 */}
        <div className="stats-section">
          <h6 className="section-title">현재 통계</h6>
          <div className="stats-grid">
            <div className="stat-item">
              <h4 className="stat-number">{recommendations.length}</h4>
              <p className="stat-label">추천 인재</p>
            </div>
            <div className="stat-item">
              <h4 className="stat-number">
                {Math.round(recommendations.reduce((sum, person) => sum + person.matchRate, 0) / recommendations.length)}%
              </h4>
              <p className="stat-label">평균 매칭률</p>
            </div>
          </div>
        </div>
      </div>

      {/* 메인 컨텐츠 영역 */}
      <div className="recommendations-main">
        <div className="main-header">
          <div className="search-bar">
            <input type="text" placeholder="이름, 기술, 직무로 검색" className="search-input" />
          </div>
          <button className="btn btn-primary" onClick={() => setShowForm(true)}>
            <FontAwesomeIcon icon={faPlus} /> 인재 등록
          </button>
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

        {/* 인재 등록 폼 */}
        {showForm ? (
          <div className="talent-form-container">
            <h3>인재 정보 등록</h3>
            <form onSubmit={handleSubmit}>
              <div className="form-group">
                <label>이름</label>
                <input
                  type="text"
                  name="name"
                  value={formData.name}
                  onChange={handleInputChange}
                  required
                />
              </div>
              <div className="form-group">
                <label>직무</label>
                <input
                  type="text"
                  name="position"
                  value={formData.position}
                  onChange={handleInputChange}
                  required
                />
              </div>
              <div className="form-group">
                <label>경력</label>
                <input
                  type="text"
                  name="experience"
                  value={formData.experience}
                  onChange={handleInputChange}
                  required
                />
              </div>
              <div className="form-group">
                <label>지역</label>
                <input
                  type="text"
                  name="location"
                  value={formData.location}
                  onChange={handleInputChange}
                  required
                />
              </div>
              <div className="form-group">
                <label>기술 스택 (쉼표로 구분)</label>
                <input
                  type="text"
                  name="skills"
                  value={formData.skills.join(', ')}
                  onChange={handleInputChange}
                  required
                />
              </div>
              <div className="form-group">
                <label>자기 소개</label>
                <textarea
                  name="description"
                  value={formData.description}
                  onChange={handleInputChange}
                  required
                />
              </div>
              <div className="form-actions">
                <button type="submit" className="btn btn-primary">등록하기</button>
                <button type="button" className="btn btn-outline" onClick={() => setShowForm(false)}>취소</button>
              </div>
            </form>
          </div>
        ) : (
          <div className="additional-info">
            <h5 className="additional-title">인재 등록하기</h5>
            <p className="additional-description">
              AI가 분석하여 최적의 매칭을 도와드립니다.
            </p>
            <button className="btn btn-primary btn-large" onClick={() => setShowForm(true)}>
              <FontAwesomeIcon icon={faPlus} /> 인재 정보 등록
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default Recommendations; 