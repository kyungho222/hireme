import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { 
  faMapMarkerAlt, 
  faClock, 
  faMoneyBillWave,
  faBuilding,
  faUser,
  faCalendarAlt,
  faCheckCircle,
  faArrowLeft
} from '@fortawesome/free-solid-svg-icons';
import './JobDetail.css';

const JobDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [isApplied, setIsApplied] = useState(false);

  // 실제로는 API에서 데이터를 가져옴
  const jobDetail = {
    id: id,
    title: '프론트엔드 개발자',
    company: '테크스타트업',
    location: '서울 강남구',
    type: '정규직',
    salary: '연 4,000만원 ~ 6,000만원',
    experience: '3년 이상',
    education: '대졸 이상',
    description: 'React와 TypeScript를 활용한 웹 애플리케이션 개발을 담당합니다. 사용자 경험을 중시하며, 최신 기술 트렌드를 반영한 개발을 진행합니다.',
    requirements: [
      'React, TypeScript, JavaScript 3년 이상 경험',
      'HTML/CSS, 웹 표준 및 웹 접근성에 대한 이해',
      'Git을 활용한 버전 관리 경험',
      'RESTful API 설계 및 개발 경험',
      '성능 최적화 및 코드 품질 관리 경험'
    ],
    preferred: [
      'Next.js, Vue.js 등 다른 프레임워크 경험',
      'AWS, Docker 등 클라우드 환경 경험',
      'TypeScript 고급 활용 능력',
      'UI/UX 디자인에 대한 이해',
      '애자일 개발 방법론 경험'
    ],
    benefits: [
      '유연한 근무 환경 (재택근무 가능)',
      '성과에 따른 인센티브',
      '교육비 지원',
      '건강검진 지원',
      '점심식대 지원',
      '야근수당 지급'
    ],
    skills: ['React', 'TypeScript', 'JavaScript', 'HTML/CSS', 'Git', 'RESTful API'],
    postedDate: '2024.01.20',
    deadline: '2024.02.20',
    applicants: 15,
    views: 128,
  };

  const handleApply = () => {
    setIsApplied(true);
    // 실제로는 지원 API 호출
    alert('지원이 완료되었습니다!');
  };

  const handleBack = () => {
    navigate('/jobs');
  };

  return (
    <div className="job-detail-container">
      {/* 뒤로가기 버튼 */}
      <button className="back-button" onClick={handleBack}>
        <FontAwesomeIcon icon={faArrowLeft} />
        목록으로 돌아가기
      </button>

      <div className="job-detail-content">
        {/* 메인 콘텐츠 */}
        <div className="main-content">
          <div className="job-detail-card">
            <div className="job-detail-header">
              <div className="job-title-section">
                <h2 className="job-title">{jobDetail.title}</h2>
                <p className="job-company">{jobDetail.company}</p>
              </div>
              <span className="job-type">{jobDetail.type}</span>
            </div>

            {/* 기본 정보 */}
            <div className="job-basic-info">
              <div className="info-item">
                <FontAwesomeIcon icon={faMapMarkerAlt} className="info-icon" />
                <span className="info-text">{jobDetail.location}</span>
              </div>
              <div className="info-item">
                <FontAwesomeIcon icon={faMoneyBillWave} className="info-icon" />
                <span className="info-text">{jobDetail.salary}</span>
              </div>
              <div className="info-item">
                <FontAwesomeIcon icon={faUser} className="info-icon" />
                <span className="info-text">경력 {jobDetail.experience}</span>
              </div>
              <div className="info-item">
                <FontAwesomeIcon icon={faBuilding} className="info-icon" />
                <span className="info-text">{jobDetail.education}</span>
              </div>
            </div>

            {/* 기술 스택 */}
            <div className="skills-section">
              <h6 className="section-title">기술 스택</h6>
              <div className="skills-list">
                {jobDetail.skills.map((skill, index) => (
                  <span key={index} className="skill-chip">
                    {skill}
                  </span>
                ))}
              </div>
            </div>

            <div className="divider"></div>

            {/* 상세 설명 */}
            <div className="description-section">
              <h6 className="section-title">직무 설명</h6>
              <p className="description-text">{jobDetail.description}</p>
            </div>

            {/* 주요 업무 */}
            <div className="tasks-section">
              <h6 className="section-title">주요 업무</h6>
              <ul className="task-list">
                <li className="task-item">
                  <FontAwesomeIcon icon={faCheckCircle} className="task-icon" />
                  <span>React와 TypeScript를 활용한 프론트엔드 개발</span>
                </li>
                <li className="task-item">
                  <FontAwesomeIcon icon={faCheckCircle} className="task-icon" />
                  <span>사용자 인터페이스 및 사용자 경험 개선</span>
                </li>
                <li className="task-item">
                  <FontAwesomeIcon icon={faCheckCircle} className="task-icon" />
                  <span>백엔드 API와의 연동 및 데이터 처리</span>
                </li>
                <li className="task-item">
                  <FontAwesomeIcon icon={faCheckCircle} className="task-icon" />
                  <span>코드 리뷰 및 기술 문서 작성</span>
                </li>
              </ul>
            </div>

            {/* 자격 요건 */}
            <div className="requirements-section">
              <h6 className="section-title">자격 요건</h6>
              <ul className="requirement-list">
                {jobDetail.requirements.map((req, index) => (
                  <li key={index} className="requirement-item">
                    <FontAwesomeIcon icon={faCheckCircle} className="requirement-icon" />
                    <span>{req}</span>
                  </li>
                ))}
              </ul>
            </div>

            {/* 우대 사항 */}
            <div className="preferred-section">
              <h6 className="section-title">우대 사항</h6>
              <ul className="preferred-list">
                {jobDetail.preferred.map((pref, index) => (
                  <li key={index} className="preferred-item">
                    <FontAwesomeIcon icon={faCheckCircle} className="preferred-icon" />
                    <span>{pref}</span>
                  </li>
                ))}
              </ul>
            </div>

            {/* 복리후생 */}
            <div className="benefits-section">
              <h6 className="section-title">복리후생</h6>
              <div className="benefits-list">
                {jobDetail.benefits.map((benefit, index) => (
                  <span key={index} className="benefit-chip">
                    {benefit}
                  </span>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* 사이드바 */}
        <div className="sidebar">
          <div className="apply-card">
            <h6 className="apply-title">지원 정보</h6>
            
            <div className="apply-info">
              <div className="info-row">
                <span className="info-label">지원자</span>
                <span className="info-value">{jobDetail.applicants}명</span>
              </div>
              <div className="info-row">
                <span className="info-label">조회수</span>
                <span className="info-value">{jobDetail.views}회</span>
              </div>
              <div className="info-row">
                <span className="info-label">마감일</span>
                <span className="info-value">{jobDetail.deadline}</span>
              </div>
            </div>

            <button
              className={`apply-button ${isApplied ? 'applied' : ''}`}
              disabled={isApplied}
              onClick={handleApply}
            >
              {isApplied && <FontAwesomeIcon icon={faCheckCircle} />}
              {isApplied ? '지원 완료' : '지원하기'}
            </button>

            <div className="date-info">
              <p className="date-text">📅 공고일: {jobDetail.postedDate}</p>
              <p className="date-text">⏰ 마감일: {jobDetail.deadline}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default JobDetail; 