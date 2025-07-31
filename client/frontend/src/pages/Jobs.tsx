import React from 'react';
import { useNavigate } from 'react-router-dom';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { 
  faMapMarkerAlt, 
  faClock, 
  faMoneyBillWave 
} from '@fortawesome/free-solid-svg-icons';
import FloatingChatbot from '../components/FloatingChatbot';
import './Jobs.css';

const Jobs: React.FC = () => {
  const navigate = useNavigate();

  const jobs = [
    {
      id: 1,
      title: '프론트엔드 개발자',
      company: '테크스타트업',
      location: '서울 강남구',
      type: '정규직',
      salary: '연 4,000만원 ~ 6,000만원',
      description: 'React, TypeScript를 활용한 웹 애플리케이션 개발',
      skills: ['React', 'TypeScript', 'JavaScript', 'HTML/CSS'],
      postedDate: '2024.01.20',
    },
    {
      id: 2,
      title: '백엔드 개발자',
      company: 'IT서비스기업',
      location: '서울 서초구',
      type: '정규직',
      salary: '연 5,000만원 ~ 7,000만원',
      description: 'Java, Spring Boot를 활용한 서버 개발',
      skills: ['Java', 'Spring Boot', 'MySQL', 'AWS'],
      postedDate: '2024.01.19',
    },
    {
      id: 3,
      title: 'UI/UX 디자이너',
      company: '디자인에이전시',
      location: '서울 마포구',
      type: '계약직',
      salary: '월 300만원 ~ 400만원',
      description: '웹/앱 디자인 및 사용자 경험 설계',
      skills: ['Figma', 'Adobe XD', 'Photoshop', 'Illustrator'],
      postedDate: '2024.01.18',
    },
    {
      id: 4,
      title: '데이터 분석가',
      company: '핀테크기업',
      location: '서울 영등포구',
      type: '정규직',
      salary: '연 4,500만원 ~ 6,500만원',
      description: '빅데이터 분석 및 인사이트 도출',
      skills: ['Python', 'SQL', 'R', 'Tableau'],
      postedDate: '2024.01.17',
    },
  ];

  const handleApply = (jobId: number) => {
    navigate(`/jobs/${jobId}`);
  };

  return (
    <div className="jobs-container">
      <div className="jobs-header">
        <h1 className="jobs-title">채용 공고</h1>
        <p className="jobs-subtitle">
          최신 채용 정보를 확인하고 지원해보세요
        </p>
      </div>

      <div className="filter-buttons">
        <button className="btn btn-primary">전체 공고</button>
        <button className="btn btn-outline">개발자</button>
        <button className="btn btn-outline">디자이너</button>
        <button className="btn btn-outline">기타</button>
      </div>

      <div className="jobs-grid">
        {jobs.map((job) => (
          <div key={job.id} className="job-card">
            <div className="job-content">
              <div className="job-header">
                <h6 className="job-title">{job.title}</h6>
                <span className="job-type">{job.type}</span>
              </div>
              
              <p className="job-company">{job.company}</p>

              <div className="job-meta">
                <div className="meta-item">
                  <FontAwesomeIcon icon={faMapMarkerAlt} className="meta-icon" />
                  <span className="meta-text">{job.location}</span>
                </div>

                <div className="meta-item">
                  <FontAwesomeIcon icon={faMoneyBillWave} className="meta-icon" />
                  <span className="meta-text">{job.salary}</span>
                </div>

                <div className="meta-item">
                  <FontAwesomeIcon icon={faClock} className="meta-icon" />
                  <span className="meta-text">{job.postedDate}</span>
                </div>
              </div>

              <p className="job-description">{job.description}</p>

              <div className="job-skills">
                {job.skills.map((skill, index) => (
                  <span key={index} className="skill-chip">
                    {skill}
                  </span>
                ))}
              </div>

              <div className="job-actions">
                <button 
                  className="btn btn-primary btn-full"
                  onClick={() => handleApply(job.id)}
                >
                  지원하기
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="jobs-footer">
        <button className="btn btn-outline btn-large">
          더 많은 공고 보기
        </button>
      </div>

      {/* 플로팅 챗봇 */}
      <FloatingChatbot
        page="jobs"
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

export default Jobs; 