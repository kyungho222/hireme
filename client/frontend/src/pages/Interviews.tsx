import React, { useState } from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { 
  faVideo, 
  faUpload, 
  faCalendarAlt, 
  faClock,
  faUser,
  faBuilding,
  faCheckCircle,
  faPlay,
  faPause
} from '@fortawesome/free-solid-svg-icons';
import './Interviews.css';

const Interviews: React.FC = () => {
  const [interviewType, setInterviewType] = useState('zoom');
  const [scheduledInterviews, setScheduledInterviews] = useState([
    {
      id: 1,
      company: '테크스타트업',
      position: '프론트엔드 개발자',
      date: '2024.01.25',
      time: '14:00',
      type: 'zoom',
      status: 'scheduled',
      interviewer: '김면접관',
      duration: '60분',
    },
    {
      id: 2,
      company: 'IT서비스기업',
      position: '백엔드 개발자',
      date: '2024.01.28',
      time: '10:00',
      type: 'video',
      status: 'pending',
      interviewer: '이면접관',
      duration: '90분',
    },
  ]);

  const handleInterviewTypeChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setInterviewType(event.target.value);
  };

  return (
    <div className="interviews-container">
      <div className="interviews-header">
        <h1 className="interviews-title">면접 관리</h1>
        <p className="interviews-subtitle">
          면접 일정을 관리하고 면접을 진행해보세요
        </p>
      </div>

      {/* 면접 방식 선택 */}
      <div className="interview-type-card">
        <div className="interview-type-content">
          <h5 className="interview-type-title">면접 방식 선택</h5>
          <p className="interview-type-description">
            면접 진행 방식을 선택해주세요.
          </p>

          <div className="interview-type-options">
            <label className="interview-type-option">
              <input
                type="radio"
                name="interviewType"
                value="zoom"
                checked={interviewType === 'zoom'}
                onChange={handleInterviewTypeChange}
              />
              <div className="option-content">
                <FontAwesomeIcon icon={faVideo} className="option-icon" />
                <div className="option-text">
                  <span className="option-title">Zoom 면접</span>
                  <span className="option-description">실시간 화상 면접으로 진행</span>
                </div>
              </div>
            </label>

            <label className="interview-type-option">
              <input
                type="radio"
                name="interviewType"
                value="video"
                checked={interviewType === 'video'}
                onChange={handleInterviewTypeChange}
              />
              <div className="option-content">
                <FontAwesomeIcon icon={faUpload} className="option-icon" />
                <div className="option-text">
                  <span className="option-title">영상 업로드 면접</span>
                  <span className="option-description">미리 녹화한 영상을 업로드하여 면접 진행</span>
                </div>
              </div>
            </label>

            <label className="interview-type-option">
              <input
                type="radio"
                name="interviewType"
                value="onsite"
                checked={interviewType === 'onsite'}
                onChange={handleInterviewTypeChange}
              />
              <div className="option-content">
                <FontAwesomeIcon icon={faBuilding} className="option-icon" />
                <div className="option-text">
                  <span className="option-title">대면 면접</span>
                  <span className="option-description">사무실에서 직접 면접 진행</span>
                </div>
              </div>
            </label>
          </div>

          {interviewType === 'zoom' && (
            <div className="interview-setup zoom-setup">
              <h6 className="setup-title">Zoom 면접 설정</h6>
              <div className="setup-form">
                <input
                  type="text"
                  className="setup-input"
                  placeholder="Zoom 회의 ID"
                />
                <input
                  type="password"
                  className="setup-input"
                  placeholder="비밀번호"
                />
              </div>
              <button className="btn btn-primary">Zoom 링크 생성</button>
            </div>
          )}

          {interviewType === 'video' && (
            <div className="interview-setup video-setup">
              <h6 className="setup-title">영상 업로드 면접</h6>
              <p className="setup-description">
                면접 질문에 대한 답변을 영상으로 녹화하여 업로드해주세요.
              </p>
              <label className="upload-button">
                <FontAwesomeIcon icon={faUpload} />
                영상 파일 업로드
                <input type="file" hidden accept="video/*" />
              </label>
            </div>
          )}

          {interviewType === 'onsite' && (
            <div className="interview-setup onsite-setup">
              <h6 className="setup-title">대면 면접 정보</h6>
              <div className="setup-form">
                <input
                  type="text"
                  className="setup-input"
                  placeholder="면접 장소"
                />
                <input
                  type="text"
                  className="setup-input"
                  placeholder="도착 시간"
                />
              </div>
            </div>
          )}
        </div>
      </div>

      {/* 예정된 면접 */}
      <div className="scheduled-interviews-card">
        <div className="scheduled-interviews-content">
          <h5 className="scheduled-interviews-title">
            예정된 면접 ({scheduledInterviews.length})
          </h5>

          <div className="interviews-list">
            {scheduledInterviews.map((interview) => (
              <div key={interview.id} className="interview-item">
                <div className="interview-header">
                  <div className="interview-info">
                    <h6 className="interview-company">{interview.company}</h6>
                    <p className="interview-position">{interview.position}</p>
                  </div>
                  <span className={`interview-status ${interview.status}`}>
                    {interview.status === 'scheduled' ? '예정' : '대기중'}
                  </span>
                </div>

                <div className="interview-meta">
                  <div className="meta-item">
                    <FontAwesomeIcon icon={faCalendarAlt} className="meta-icon" />
                    <span className="meta-text">{interview.date}</span>
                  </div>
                  <div className="meta-item">
                    <FontAwesomeIcon icon={faClock} className="meta-icon" />
                    <span className="meta-text">{interview.time} ({interview.duration})</span>
                  </div>
                  <div className="meta-item">
                    <FontAwesomeIcon icon={faUser} className="meta-icon" />
                    <span className="meta-text">{interview.interviewer}</span>
                  </div>
                </div>

                <div className="interview-actions">
                  <button className="btn btn-primary">
                    <FontAwesomeIcon icon={faPlay} />
                    면접 시작
                  </button>
                  <button className="btn btn-outline">일정 변경</button>
                  <button className="btn btn-outline btn-danger">취소</button>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* 면접 준비 가이드 */}
      <div className="interview-guide-card">
        <div className="interview-guide-content">
          <h5 className="interview-guide-title">면접 준비 가이드</h5>
          
          <div className="guide-grid">
            <div className="guide-item">
              <h6 className="guide-item-title">📋 면접 전 체크리스트</h6>
              <ul className="guide-list">
                <li>이력서와 포트폴리오 준비</li>
                <li>면접 질문 예상 및 답변 준비</li>
                <li>회사 및 직무에 대한 조사</li>
                <li>적절한 복장 및 환경 준비</li>
              </ul>
            </div>

            <div className="guide-item">
              <h6 className="guide-item-title">🎯 면접 팁</h6>
              <ul className="guide-list">
                <li>자신감 있게 말하기</li>
                <li>구체적인 경험 사례 제시</li>
                <li>질문이 있을 때 적극적으로 물어보기</li>
                <li>면접 후 감사 인사 잊지 않기</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Interviews; 