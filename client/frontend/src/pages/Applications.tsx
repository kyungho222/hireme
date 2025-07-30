import React, { useState } from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { 
  faFileAlt, 
  faUpload, 
  faTrash, 
  faEye 
} from '@fortawesome/free-solid-svg-icons';
import FloatingChatbot from '../components/FloatingChatbot';
import './Applications.css';

const Applications: React.FC = () => {
  const [tabValue, setTabValue] = useState(0);
  const [uploadedFiles, setUploadedFiles] = useState<string[]>([
    '이력서_홍길동.pdf',
    '포트폴리오_홍길동.pdf',
    '자기소개서_홍길동.pdf'
  ]);

  const handleTabChange = (index: number) => {
    setTabValue(index);
  };

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files;
    if (files) {
      const newFiles = Array.from(files).map(file => file.name);
      setUploadedFiles([...uploadedFiles, ...newFiles]);
    }
  };

  const handleFileDelete = (index: number) => {
    const newFiles = uploadedFiles.filter((_, i) => i !== index);
    setUploadedFiles(newFiles);
  };

  return (
    <div className="applications-container">
      <div className="applications-header">
        <h1 className="applications-title">지원서 관리</h1>
        <p className="applications-subtitle">
          지원서를 작성하고 관리해보세요
        </p>
      </div>

      <div className="applications-card">
        <div className="applications-content">
          <div className="tabs">
            <button
              className={`tab ${tabValue === 0 ? 'active' : ''}`}
              onClick={() => handleTabChange(0)}
            >
              입력 페이지
            </button>
            <button
              className={`tab ${tabValue === 1 ? 'active' : ''}`}
              onClick={() => handleTabChange(1)}
            >
              PDF 등록
            </button>
          </div>

          {tabValue === 0 && (
            <div className="tab-content">
              <form className="application-form">
                <h5 className="form-section-title">기본 정보</h5>
                
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

                <div className="form-grid">
                  <div className="form-field">
                    <label className="form-label">전화번호</label>
                    <input
                      type="tel"
                      className="form-input"
                      required
                    />
                  </div>
                  <div className="form-field">
                    <label className="form-label">희망 직무</label>
                    <select className="form-select">
                      <option value="">선택해주세요</option>
                      <option value="frontend">프론트엔드 개발자</option>
                      <option value="backend">백엔드 개발자</option>
                      <option value="fullstack">풀스택 개발자</option>
                      <option value="designer">UI/UX 디자이너</option>
                      <option value="data">데이터 분석가</option>
                    </select>
                  </div>
                </div>

                <h5 className="form-section-title">학력 및 경력</h5>

                <div className="form-field">
                  <label className="form-label">최종 학력</label>
                  <input
                    type="text"
                    className="form-input"
                  />
                </div>

                <div className="form-field">
                  <label className="form-label">전공</label>
                  <input
                    type="text"
                    className="form-input"
                  />
                </div>

                <div className="form-field">
                  <label className="form-label">경력 연차</label>
                  <input
                    type="text"
                    className="form-input"
                  />
                </div>

                <h5 className="form-section-title">기술 스택</h5>

                <div className="skills-container">
                  <span className="skill-chip">React</span>
                  <span className="skill-chip">TypeScript</span>
                  <span className="skill-chip">JavaScript</span>
                  <span className="skill-chip">HTML/CSS</span>
                  <span className="skill-chip">Node.js</span>
                  <span className="skill-chip">Python</span>
                </div>

                <h5 className="form-section-title">자기소개</h5>

                <div className="form-field">
                  <label className="form-label">자기소개</label>
                  <textarea
                    className="form-textarea"
                    rows={6}
                  />
                </div>

                <div className="form-actions">
                  <button type="submit" className="btn btn-primary btn-large">
                    저장하기
                  </button>
                  <button type="button" className="btn btn-outline btn-large">
                    미리보기
                  </button>
                </div>
              </form>
            </div>
          )}

          {tabValue === 1 && (
            <div className="tab-content">
              <h5 className="form-section-title">PDF 파일 등록</h5>
              <p className="form-description">
                최대 3개의 PDF 파일을 등록할 수 있습니다.
              </p>

              <div className="upload-section">
                <div className="upload-header">
                  <FontAwesomeIcon icon={faUpload} className="upload-icon" />
                  <h6 className="upload-title">파일 업로드</h6>
                </div>
                
                <label className="upload-button">
                  <FontAwesomeIcon icon={faFileAlt} />
                  PDF 파일 선택
                  <input
                    type="file"
                    hidden
                    multiple
                    accept=".pdf"
                    onChange={handleFileUpload}
                  />
                </label>

                <p className="upload-description">
                  지원 파일: 이력서, 포트폴리오, 자기소개서 등
                </p>
              </div>

              <h6 className="files-title">
                등록된 파일 ({uploadedFiles.length}/3)
              </h6>

              <div className="files-list">
                {uploadedFiles.map((file, index) => (
                  <div key={index} className="file-item">
                    <div className="file-info">
                      <FontAwesomeIcon icon={faFileAlt} className="file-icon" />
                      <span className="file-name">{file}</span>
                    </div>
                    <div className="file-actions">
                      <button className="btn btn-small">
                        <FontAwesomeIcon icon={faEye} />
                        보기
                      </button>
                      <button 
                        className="btn btn-small btn-danger"
                        onClick={() => handleFileDelete(index)}
                      >
                        <FontAwesomeIcon icon={faTrash} />
                        삭제
                      </button>
                    </div>
                  </div>
                ))}
              </div>

              {uploadedFiles.length === 0 && (
                <div className="empty-files">
                  <p className="empty-text">등록된 파일이 없습니다.</p>
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      {/* 플로팅 챗봇 */}
      <FloatingChatbot
        page="applications"
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

export default Applications; 