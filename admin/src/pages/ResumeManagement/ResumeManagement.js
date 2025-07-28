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
  font-size: 32px;
  font-weight: 700;
  color: var(--text-primary);
`;

const ActionButtons = styled.div`
  display: flex;
  gap: 12px;
`;

const Button = styled.button`
  padding: 12px 24px;
  border: none;
  border-radius: var(--border-radius);
  font-weight: 500;
  cursor: pointer;
  transition: var(--transition);
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  
  &.primary {
    background: var(--primary-color);
    color: white;
  }
  
  &.secondary {
    background: white;
    color: var(--text-primary);
    border: 1px solid var(--border-color);
  }
  
  &:hover {
    transform: translateY(-1px);
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
  padding: 12px 16px;
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius);
  font-size: 14px;
  
  &:focus {
    outline: none;
    border-color: var(--primary-color);
  }
`;

const FilterButton = styled.button`
  padding: 12px 16px;
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius);
  background: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: var(--transition);
  
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
  padding: 24px;
  box-shadow: var(--shadow-light);
  transition: var(--transition);
  border: 1px solid var(--border-color);
  
  &:hover {
    transform: translateY(-4px);
    box-shadow: var(--shadow-medium);
  }
`;

const ResumeHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16px;
`;

const ApplicantInfo = styled.div`
  flex: 1;
`;

const ApplicantName = styled.h3`
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 4px;
`;

const ApplicantPosition = styled.div`
  font-size: 14px;
  color: var(--text-secondary);
  margin-bottom: 8px;
`;

// StatusBadge is imported from DetailModal

const ResumeContent = styled.div`
  margin-bottom: 16px;
`;

const ResumeDetail = styled.div`
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
  font-size: 14px;
`;

// DetailLabel and DetailValue are imported from DetailModal

const ResumeActions = styled.div`
  display: flex;
  gap: 8px;
  margin-top: 16px;
`;

const ActionButton = styled.button`
  padding: 8px 12px;
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius);
  background: white;
  cursor: pointer;
  font-size: 12px;
  transition: var(--transition);
  display: flex;
  align-items: center;
  gap: 4px;
  
  &:hover {
    background: var(--background-secondary);
    border-color: var(--primary-color);
  }
`;

const AnalysisResult = styled.div`
  margin-top: 16px;
  padding: 12px;
  background: var(--background-secondary);
  border-radius: var(--border-radius);
  border-left: 4px solid var(--primary-color);
`;

const AnalysisTitle = styled.div`
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 8px;
  font-size: 14px;
`;

const AnalysisScore = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
`;

const ScoreBar = styled.div`
  flex: 1;
  height: 8px;
  background: var(--border-color);
  border-radius: 4px;
  overflow: hidden;
`;

const ScoreFill = styled.div`
  height: 100%;
  background: var(--primary-color);
  width: ${props => props.score}%;
  transition: width 0.3s ease;
`;

const ScoreText = styled.span`
  font-size: 12px;
  color: var(--text-secondary);
  min-width: 30px;
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

  const filteredResumes = resumes.filter(resume => {
    const matchesSearch = resume.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         resume.position.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesFilter = filterStatus === 'all' || resume.status === filterStatus;
    return matchesSearch && matchesFilter;
  });

  return (
    <ResumeContainer>
      <Header>
        <Title>이력서 관리</Title>
        <ActionButtons>
          <Button className="secondary">
            <FiSmartphone />
            QR 스캔
          </Button>
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
        <FilterButton>
          <FiFilter />
          필터
        </FilterButton>
      </SearchBar>

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
              <StatusBadge className={resume.status}>
                {getStatusText(resume.status)}
              </StatusBadge>
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
              <div style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>
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
              <ActionButton>
                <FiSmartphone />
                QR 생성
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
        onEdit={() => {
          // 수정 기능 구현
          console.log('이력서 수정:', selectedResume);
        }}
        onDelete={() => {
          // 삭제 기능 구현
          console.log('이력서 삭제:', selectedResume);
        }}
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
                  <StatusBadge className={selectedResume.status}>
                    {getStatusText(selectedResume.status)}
                  </StatusBadge>
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