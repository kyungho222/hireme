import React, { useState } from 'react';
import styled from 'styled-components';
import { motion } from 'framer-motion';
import { 
  FiFileText, 
  FiDownload, 
  FiSmartphone, 
  FiEye, 
  FiSearch,
  FiFilter,
  FiPlus,
  FiCheckCircle,
  FiClock,
  FiAlertCircle
} from 'react-icons/fi';
import DetailModal, {
  DetailSection,
  SectionTitle,
  DetailGrid,
  DetailItem,
  DetailLabel,
  DetailValue,
  DetailText,
  StatusBadge
} from '../../components/DetailModal/DetailModal';

const ResumeContainer = styled.div`
  padding: 24px 0;
`;

const Header = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 32px;
`;

const Title = styled.h1`
  font-size: 48px;
  font-weight: 700;
  color: var(--text-primary);
`;

const ActionButtons = styled.div`
  display: flex;
  gap: 12px;
`;

const Button = styled.button`
  padding: 20px 40px;
  border: none;
  border-radius: var(--border-radius);
  font-weight: 600;
  cursor: pointer;
  transition: var(--transition);
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 22px;
  
  &.primary {
    background: var(--primary-color);
    color: white;
  }
  
  &.secondary {
    background: white;
    color: var(--text-primary);
    border: 2px solid var(--border-color);
  }
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: var(--shadow-light);
  }
`;

const SearchBar = styled.div`
  display: flex;
  gap: 16px;
  margin-bottom: 24px;
  align-items: center;
`;

const SearchInput = styled.input`
  flex: 1;
  padding: 20px 28px;
  border: 2px solid var(--border-color);
  border-radius: var(--border-radius);
  font-size: 20px;
  
  &:focus {
    outline: none;
    border-color: var(--primary-color);
  }
`;

const FilterButton = styled.button`
  padding: 20px 28px;
  border: 2px solid var(--border-color);
  border-radius: var(--border-radius);
  background: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 12px;
  transition: var(--transition);
  font-size: 20px;
  
  &:hover {
    border-color: var(--primary-color);
  }
`;

const ResumeGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 24px;
`;

const ResumeCard = styled(motion.div)`
  background: white;
  border-radius: var(--border-radius);
  padding: 40px;
  box-shadow: var(--shadow-light);
  transition: var(--transition);
  border: 2px solid var(--border-color);
  
  &:hover {
    transform: translateY(-6px);
    box-shadow: var(--shadow-medium);
  }
`;

const ResumeHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 20px;
`;

const ApplicantInfo = styled.div`
  flex: 1;
`;

const ApplicantName = styled.h3`
  font-size: 32px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 10px;
`;

const ApplicantPosition = styled.div`
  font-size: 22px;
  color: var(--text-secondary);
  margin-bottom: 14px;
`;

// StatusBadge is imported from DetailModal

const ResumeContent = styled.div`
  margin-bottom: 20px;
`;

const ResumeDetail = styled.div`
  display: flex;
  justify-content: space-between;
  margin-bottom: 16px;
  font-size: 20px;
`;

// DetailLabel and DetailValue are imported from DetailModal

const ResumeActions = styled.div`
  display: flex;
  gap: 16px;
  margin-top: 28px;
`;

const ActionButton = styled.button`
  padding: 16px 28px;
  border: 2px solid var(--border-color);
  border-radius: var(--border-radius);
  background: white;
  cursor: pointer;
  font-size: 18px;
  transition: var(--transition);
  display: flex;
  align-items: center;
  gap: 10px;
  
  &:hover {
    background: var(--background-secondary);
    border-color: var(--primary-color);
  }
`;

const AnalysisResult = styled.div`
  margin-top: 28px;
  padding: 24px;
  background: var(--background-secondary);
  border-radius: var(--border-radius);
  border-left: 6px solid var(--primary-color);
`;

const AnalysisTitle = styled.div`
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 18px;
  font-size: 22px;
`;

const AnalysisScore = styled.div`
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 16px;
`;

const ScoreBar = styled.div`
  flex: 1;
  height: 18px;
  background: var(--border-color);
  border-radius: 9px;
  overflow: hidden;
`;

const ScoreFill = styled.div`
  height: 100%;
  background: ${props => {
    if (props.score >= 90) return '#22c55e'; // 초록
    if (props.score >= 80) return '#f59e0b'; // 노랑
    return '#ef4444'; // 빨강
  }};
  width: ${props => props.score}%;
  transition: width 0.3s ease;
`;

const ScoreText = styled.span`
  font-size: 20px;
  color: var(--text-secondary);
  min-width: 50px;
`;

// 커스텀 StatusBadge 컴포넌트 추가
const CustomStatusBadge = styled.span`
  display: inline-flex;
  align-items: center;
  padding: 12px 28px;
  border-radius: 28px;
  font-size: 20px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;

  &.approved {
    background-color: #dcfce7;
    color: #166534;
    border: 2px solid #22c55e;
  }

  &.pending {
    background-color: #fef3c7;
    color: #92400e;
    border: 2px solid #f59e0b;
  }

  &.rejected {
    background-color: #fee2e2;
    color: #dc2626;
    border: 2px solid #ef4444;
  }

  &.reviewed {
    background-color: #dbeafe;
    color: #1e40af;
    border: 2px solid #3b82f6;
  }
`;

// 샘플 데이터
const resumes = [
  {
    id: 1,
    name: '김철수',
    position: '프론트엔드 개발자',
    email: 'kim@example.com',
    phone: '010-1234-5678',
    submittedDate: '2024-01-15',
    status: 'reviewed',
    experience: '3년',
    education: '컴퓨터공학과',
    analysisScore: 85,
    analysisResult: '기술 스택이 요구사항과 잘 맞으며, 프로젝트 경험이 풍부합니다.'
  },
  {
    id: 2,
    name: '이영희',
    position: '백엔드 개발자',
    email: 'lee@example.com',
    phone: '010-2345-6789',
    submittedDate: '2024-01-14',
    status: 'approved',
    experience: '5년',
    education: '소프트웨어공학과',
    analysisScore: 92,
    analysisResult: '시스템 설계 경험이 뛰어나고, 성능 최적화 능력이 우수합니다.'
  },
  {
    id: 3,
    name: '박민수',
    position: 'UI/UX 디자이너',
    email: 'park@example.com',
    phone: '010-3456-7890',
    submittedDate: '2024-01-13',
    status: 'pending',
    experience: '2년',
    education: '디자인학과',
    analysisScore: 78,
    analysisResult: '창의적인 디자인 감각을 보유하고 있으며, 사용자 경험에 대한 이해가 깊습니다.'
  },
  {
    id: 4,
    name: '정수진',
    position: '데이터 엔지니어',
    email: 'jung@example.com',
    phone: '010-4567-8901',
    submittedDate: '2024-01-12',
    status: 'rejected',
    experience: '4년',
    education: '통계학과',
    analysisScore: 65,
    analysisResult: '기술적 역량은 우수하나, 팀 협업 경험이 부족합니다.'
  }
];

const getStatusText = (status) => {
  const statusMap = {
    pending: '검토 대기',
    reviewed: '검토 완료',
    approved: '승인',
    rejected: '거절'
  };
  return statusMap[status] || status;
};

const ResumeManagement = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [filterStatus, setFilterStatus] = useState('all');
  const [selectedResume, setSelectedResume] = useState(null);
  const [isDetailModalOpen, setIsDetailModalOpen] = useState(false);
  
  // 필터 상태 추가
  const [isFilterOpen, setIsFilterOpen] = useState(false);
  const [selectedJobs, setSelectedJobs] = useState([]);
  const [selectedExperience, setSelectedExperience] = useState([]);
  const [selectedScoreRanges, setSelectedScoreRanges] = useState([]);

  const handleFilterApply = () => {
    setIsFilterOpen(false);
  };

  const handleFilterClose = () => {
    setIsFilterOpen(false);
  };

  const handleJobToggle = (job) => {
    setSelectedJobs(prev => 
      prev.includes(job) 
        ? prev.filter(j => j !== job)
        : [...prev, job]
    );
  };

  const handleExperienceToggle = (exp) => {
    setSelectedExperience(prev => 
      prev.includes(exp) 
        ? prev.filter(e => e !== exp)
        : [...prev, exp]
    );
  };

  const handleScoreRangeToggle = (range) => {
    setSelectedScoreRanges(prev => 
      prev.includes(range) 
        ? prev.filter(r => r !== range)
        : [...prev, range]
    );
  };

  const filteredResumes = resumes.filter(resume => {
    const matchesSearch = resume.name.toLowerCase().includes(searchTerm.toLowerCase()) || 
                         resume.position.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesFilter = filterStatus === 'all' || resume.status === filterStatus;
    
    // 직무 필터링
    const matchesJob = selectedJobs.length === 0 || selectedJobs.some(job => 
      resume.position.toLowerCase().includes(job.toLowerCase())
    );
    
    // 경력 필터링
    const resumeExp = parseInt(resume.experience);
    const matchesExperience = selectedExperience.length === 0 || selectedExperience.some(exp => {
      if (exp === '1-3년') return resumeExp >= 1 && resumeExp <= 3;
      if (exp === '3-5년') return resumeExp >= 3 && resumeExp <= 5;
      if (exp === '5년이상') return resumeExp >= 5;
      return false;
    });
    
    // 적합도 필터링
    const matchesScore = selectedScoreRanges.length === 0 || selectedScoreRanges.some(range => {
      if (range === '90-100') return resume.analysisScore >= 90;
      if (range === '80-89') return resume.analysisScore >= 80 && resume.analysisScore <= 89;
      if (range === '70-79') return resume.analysisScore >= 70 && resume.analysisScore <= 79;
      return false;
    });
    
    return matchesSearch && matchesFilter && matchesJob && matchesExperience && matchesScore;
  });

  return (
    <ResumeContainer>
      <Header>
        <Title>이력서 관리</Title>
        <ActionButtons>
          <Button className="primary">
            <FiPlus />
            새 이력서 등록
          </Button>
        </ActionButtons>
      </Header>

      <SearchBar>
        <SearchInput
          type="text"
          placeholder="지원자명 또는 직무로 검색..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
        />
        <FilterButton onClick={() => setIsFilterOpen(true)}>
          <FiFilter />
          필터
        </FilterButton>
      </SearchBar>

      {/* 필터 모달 */}
      {isFilterOpen && (
        <>
          {/* 오버레이 */}
          <div style={{
            position: 'fixed',
            top: 0,
            left: 0,
            width: '100vw',
            height: '100vh',
            background: 'rgba(0,0,0,0.3)',
            zIndex: 999
          }} />
          {/* 가로형 필터 모달 */}
          <div style={{
            position: 'fixed',
            top: '50%',
            left: '50%',
            transform: 'translate(-50%, -50%)',
            zIndex: 1000,
            background: 'white',
            border: '2px solid #e5e7eb',
            borderRadius: '16px',
            padding: '32px 48px',
            boxShadow: '0 8px 32px rgba(0,0,0,0.12)',
            minWidth: '900px',
            maxWidth: '1100px',
            minHeight: '220px',
            display: 'flex',
            flexDirection: 'row',
            gap: '48px',
            alignItems: 'flex-start',
            justifyContent: 'center' // x축 중앙 정렬
          }}>
            {/* 직무 필터 */}
            <div style={{ flex: 1 }}>
              <h4 style={{ fontSize: '20px', fontWeight: '700', marginBottom: '16px', color: '#374151' }}>
                직무
              </h4>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '14px' }}>
                {['프론트엔드', '백엔드', '풀스택', '데이터 분석', 'PM', 'UI/UX', 'DevOps', 'QA'].map(job => (
                  <label key={job} style={{ display: 'flex', alignItems: 'center', gap: '10px', fontSize: '18px' }}>
                    <input
                      type="checkbox"
                      checked={selectedJobs.includes(job)}
                      onChange={() => handleJobToggle(job)}
                      style={{ width: '20px', height: '20px', minWidth: '20px', minHeight: '20px', maxWidth: '20px', maxHeight: '20px' }}
                    />
                    {job}
                  </label>
                ))}
              </div>
            </div>
            {/* 경력 필터 */}
            <div style={{ flex: 1 }}>
              <h4 style={{ fontSize: '20px', fontWeight: '700', marginBottom: '16px', color: '#374151' }}>
                경력
              </h4>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
                {['1-3년', '3-5년', '5년이상'].map(exp => (
                  <label key={exp} style={{ display: 'flex', alignItems: 'center', gap: '10px', fontSize: '18px' }}>
                    <input
                      type="checkbox"
                      checked={selectedExperience.includes(exp)}
                      onChange={() => handleExperienceToggle(exp)}
                      style={{ width: '20px', height: '20px', minWidth: '20px', minHeight: '20px', maxWidth: '20px', maxHeight: '20px' }}
                    />
                    {exp}
                  </label>
                ))}
              </div>
            </div>
            {/* 적합도 필터 */}
            <div style={{ flex: 1 }}>
              <h4 style={{ fontSize: '20px', fontWeight: '700', marginBottom: '16px', color: '#374151' }}>
                적합도
              </h4>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
                {['90-100', '80-89', '70-79'].map(range => (
                  <label key={range} style={{ display: 'flex', alignItems: 'center', gap: '10px', fontSize: '18px' }}>
                    <input
                      type="checkbox"
                      checked={selectedScoreRanges.includes(range)}
                      onChange={() => handleScoreRangeToggle(range)}
                      style={{ width: '20px', height: '20px', minWidth: '20px', minHeight: '20px', maxWidth: '20px', maxHeight: '20px' }}
                    />
                    {range}점
                  </label>
                ))}
              </div>
            </div>
            {/* 적용 버튼 */}
            <div style={{ display: 'flex', flexDirection: 'column', justifyContent: 'flex-end', alignItems: 'flex-end', minWidth: '120px', height: '100%' }}>
              <Button 
                className="primary" 
                onClick={handleFilterApply}
                style={{ fontSize: '18px', padding: '16px 32px', marginTop: 'auto' }}
              >
                적용
              </Button>
            </div>
          </div>
        </>
      )}

      <ResumeGrid>
        {filteredResumes.map((resume, index) => (
          <ResumeCard
            key={resume.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: index * 0.1 }}
          >
            <ResumeHeader>
              <ApplicantInfo>
                <ApplicantName>{resume.name}</ApplicantName>
                <ApplicantPosition>{resume.position}</ApplicantPosition>
              </ApplicantInfo>
              <CustomStatusBadge className={resume.status}>
                {getStatusText(resume.status)}
              </CustomStatusBadge>
            </ResumeHeader>

            <ResumeContent>
              <ResumeDetail>
                <DetailLabel>이메일:</DetailLabel>
                <DetailValue>{resume.email}</DetailValue>
              </ResumeDetail>
              <ResumeDetail>
                <DetailLabel>연락처:</DetailLabel>
                <DetailValue>{resume.phone}</DetailValue>
              </ResumeDetail>
              <ResumeDetail>
                <DetailLabel>경력:</DetailLabel>
                <DetailValue>{resume.experience}</DetailValue>
              </ResumeDetail>
              <ResumeDetail>
                <DetailLabel>학력:</DetailLabel>
                <DetailValue>{resume.education}</DetailValue>
              </ResumeDetail>
              <ResumeDetail>
                <DetailLabel>제출일:</DetailLabel>
                <DetailValue>{resume.submittedDate}</DetailValue>
              </ResumeDetail>
            </ResumeContent>

            <AnalysisResult>
              <AnalysisTitle>AI 분석 결과</AnalysisTitle>
              <AnalysisScore>
                <ScoreText>적합도</ScoreText>
                <ScoreBar>
                  <ScoreFill score={resume.analysisScore} />
                </ScoreBar>
                <ScoreText>{resume.analysisScore}%</ScoreText>
              </AnalysisScore>
              <div style={{ fontSize: '16px', color: 'var(--text-secondary)' }}>
                {resume.analysisResult}
              </div>
            </AnalysisResult>

            <ResumeActions>
              <ActionButton onClick={() => {
                setSelectedResume(resume);
                setIsDetailModalOpen(true);
              }}>
                <FiEye />
                상세보기
              </ActionButton>
              <ActionButton>
                <FiDownload />
                PDF 다운로드
              </ActionButton>
            </ResumeActions>
          </ResumeCard>
        ))}
      </ResumeGrid>

      {/* 이력서 상세보기 모달 */}
      <DetailModal
        isOpen={isDetailModalOpen}
        onClose={() => {
          setIsDetailModalOpen(false);
          setSelectedResume(null);
        }}
        title={selectedResume ? `${selectedResume.name} 이력서 상세` : ''}
      >
        {selectedResume && (
          <>
            <DetailSection>
              <SectionTitle>기본 정보</SectionTitle>
              <DetailGrid>
                <DetailItem>
                  <DetailLabel>이름</DetailLabel>
                  <DetailValue>{selectedResume.name}</DetailValue>
                </DetailItem>
                <DetailItem>
                  <DetailLabel>지원 직무</DetailLabel>
                  <DetailValue>{selectedResume.position}</DetailValue>
                </DetailItem>
                <DetailItem>
                  <DetailLabel>이메일</DetailLabel>
                  <DetailValue>{selectedResume.email}</DetailValue>
                </DetailItem>
                <DetailItem>
                  <DetailLabel>연락처</DetailLabel>
                  <DetailValue>{selectedResume.phone}</DetailValue>
                </DetailItem>
                <DetailItem>
                  <DetailLabel>경력</DetailLabel>
                  <DetailValue>{selectedResume.experience}</DetailValue>
                </DetailItem>
                <DetailItem>
                  <DetailLabel>학력</DetailLabel>
                  <DetailValue>{selectedResume.education}</DetailValue>
                </DetailItem>
                <DetailItem>
                  <DetailLabel>제출일</DetailLabel>
                  <DetailValue>{selectedResume.submittedDate}</DetailValue>
                </DetailItem>
                <DetailItem>
                  <DetailLabel>상태</DetailLabel>
                  <CustomStatusBadge className={selectedResume.status} style={{ 
                    padding: '8px 16px', 
                    fontSize: '14px', 
                    borderRadius: '16px',
                    display: 'inline-block',
                    width: '80px',
                    height: '32px',
                    textAlign: 'center',
                    lineHeight: '16px',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center'
                  }}>
                    {getStatusText(selectedResume.status)}
                  </CustomStatusBadge>
                </DetailItem>
              </DetailGrid>
            </DetailSection>

            <DetailSection>
              <SectionTitle>AI 분석 결과</SectionTitle>
              <DetailGrid>
                <DetailItem>
                  <DetailLabel>적합도 점수</DetailLabel>
                  <DetailValue>{selectedResume.analysisScore}%</DetailValue>
                </DetailItem>
                <DetailItem>
                  <DetailLabel>분석 결과</DetailLabel>
                  <DetailValue>{selectedResume.analysisResult}</DetailValue>
                </DetailItem>
              </DetailGrid>
            </DetailSection>

            <DetailSection>
              <SectionTitle>추가 정보</SectionTitle>
              <DetailText>
                이 지원자는 {selectedResume.experience}의 경력을 가지고 있으며, 
                {selectedResume.education} 학력을 보유하고 있습니다. 
                AI 분석 결과 {selectedResume.analysisScore}%의 적합도를 보여주고 있습니다.
              </DetailText>
            </DetailSection>
          </>
        )}
      </DetailModal>
    </ResumeContainer>
  );
};

export default ResumeManagement; 