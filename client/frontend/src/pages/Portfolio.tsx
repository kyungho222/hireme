import React, { useState } from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { 
  faExternalLinkAlt, 
  faCode, 
  faStar,
  faEye,
  faCodeBranch
} from '@fortawesome/free-solid-svg-icons';
import { faGithub as faGithubBrand } from '@fortawesome/free-brands-svg-icons';
import './Portfolio.css';

const Portfolio: React.FC = () => {
  const [githubUrl, setGithubUrl] = useState('https://github.com/username');
  const [repositories, setRepositories] = useState([
    {
      id: 1,
      name: 'react-ecommerce-app',
      description: 'React와 TypeScript로 개발한 이커머스 웹 애플리케이션',
      language: 'TypeScript',
      stars: 15,
      forks: 8,
      watchers: 12,
      url: 'https://github.com/username/react-ecommerce-app',
      topics: ['react', 'typescript', 'ecommerce', 'web-app']
    },
    {
      id: 2,
      name: 'nodejs-api-server',
      description: 'Express.js와 MongoDB를 활용한 RESTful API 서버',
      language: 'JavaScript',
      stars: 23,
      forks: 12,
      watchers: 18,
      url: 'https://github.com/username/nodejs-api-server',
      topics: ['nodejs', 'express', 'mongodb', 'api']
    },
    {
      id: 3,
      name: 'python-data-analysis',
      description: 'Python을 활용한 데이터 분석 및 시각화 프로젝트',
      language: 'Python',
      stars: 8,
      forks: 3,
      watchers: 6,
      url: 'https://github.com/username/python-data-analysis',
      topics: ['python', 'data-analysis', 'pandas', 'matplotlib']
    }
  ]);

  const handleGithubUrlChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setGithubUrl(event.target.value);
  };

  const handleAddRepository = () => {
    // 실제로는 GitHub API를 호출하여 저장소 정보를 가져옴
    const newRepo = {
      id: repositories.length + 1,
      name: 'new-repository',
      description: '새로 추가된 저장소',
      language: 'JavaScript',
      stars: 0,
      forks: 0,
      watchers: 1,
      url: 'https://github.com/username/new-repository',
      topics: ['new', 'project']
    };
    setRepositories([...repositories, newRepo]);
  };

  return (
    <div className="portfolio-container">
      <div className="portfolio-header">
        <h1 className="portfolio-title">포트폴리오</h1>
        <p className="portfolio-subtitle">
          GitHub 프로젝트를 관리하고 포트폴리오를 구성해보세요
        </p>
      </div>

      {/* GitHub URL 설정 */}
      <div className="github-setup-card">
        <div className="github-setup-content">
          <h5 className="github-setup-title">GitHub 프로필 설정</h5>
          <p className="github-setup-description">
            GitHub 프로필 URL을 입력하면 자동으로 저장소 정보를 가져옵니다.
          </p>
          
          <div className="github-url-input">
            <input
              type="text"
              className="url-input"
              value={githubUrl}
              onChange={handleGithubUrlChange}
              placeholder="https://github.com/username"
            />
            <button className="btn btn-primary">
              <FontAwesomeIcon icon={faGithubBrand} />
              연결하기
            </button>
          </div>
        </div>
      </div>

      {/* 저장소 목록 */}
      <div className="repositories-section">
        <div className="repositories-header">
          <h5 className="repositories-title">
            프로젝트 저장소 ({repositories.length})
          </h5>
          <button className="btn btn-outline">
            <FontAwesomeIcon icon={faCode} />
            새 저장소 추가
          </button>
        </div>

        <div className="repositories-list">
          {repositories.map((repo) => (
            <div key={repo.id} className="repository-card">
              <div className="repository-content">
                <div className="repository-header">
                  <div className="repository-info">
                    <h6 className="repository-name">{repo.name}</h6>
                    <p className="repository-description">{repo.description}</p>
                  </div>
                  <span className="language-chip">{repo.language}</span>
                </div>

                <div className="repository-stats">
                  <div className="stat-item">
                    <FontAwesomeIcon icon={faStar} className="stat-icon star" />
                    <span className="stat-text">{repo.stars}</span>
                  </div>
                  <div className="stat-item">
                    <FontAwesomeIcon icon={faCodeBranch} className="stat-icon" />
                    <span className="stat-text">{repo.forks}</span>
                  </div>
                  <div className="stat-item">
                    <FontAwesomeIcon icon={faEye} className="stat-icon" />
                    <span className="stat-text">{repo.watchers}</span>
                  </div>
                </div>

                <div className="repository-topics">
                  {repo.topics.map((topic, index) => (
                    <span key={index} className="topic-chip">
                      {topic}
                    </span>
                  ))}
                </div>

                <div className="repository-actions">
                  <a
                    href={repo.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="btn btn-outline btn-small"
                  >
                    <FontAwesomeIcon icon={faGithubBrand} />
                    GitHub 보기
                  </a>
                  <button className="btn btn-outline btn-small">
                    <FontAwesomeIcon icon={faExternalLinkAlt} />
                    라이브 데모
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* 통계 */}
      <div className="stats-card">
        <div className="stats-content">
          <h5 className="stats-title">포트폴리오 통계</h5>
          
          <div className="stats-grid">
            <div className="stat-item">
              <h4 className="stat-number">{repositories.length}</h4>
              <p className="stat-label">총 프로젝트</p>
            </div>
            
            <div className="stat-item">
              <h4 className="stat-number">
                {repositories.reduce((sum, repo) => sum + repo.stars, 0)}
              </h4>
              <p className="stat-label">총 스타</p>
            </div>
            
            <div className="stat-item">
              <h4 className="stat-number">
                {repositories.reduce((sum, repo) => sum + repo.forks, 0)}
              </h4>
              <p className="stat-label">총 포크</p>
            </div>
            
            <div className="stat-item">
              <h4 className="stat-number">
                {repositories.length > 0 ? Math.round(repositories.reduce((sum, repo) => sum + repo.stars, 0) / repositories.length) : 0}
              </h4>
              <p className="stat-label">평균 스타</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Portfolio; 