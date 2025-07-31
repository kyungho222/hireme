import React, { useState } from 'react';
import styled from 'styled-components';
import { motion } from 'framer-motion';
import { 
  FiEdit3, 
  FiCheckCircle, 
  FiAlertCircle, 
  FiEye, 
  FiDownload,
  FiFileText,
  FiClock,
  FiPercent
} from 'react-icons/fi';
import DetailModal, {
  DetailSection,
  SectionTitle,
  DetailGrid,
  DetailItem,
  DetailLabel,
  DetailValue,
  DetailText
} from '../../components/DetailModal/DetailModal';

const CoverLetterContainer = styled.div`
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

const CoverLetterGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
  gap: 24px;
`;

const CoverLetterCard = styled(motion.div)`
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

const CardHeader = styled.div`
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

const ValidationScore = styled.span`
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
  background: ${props => {
    if (props.score >= 90) return '#d4edda';
    if (props.score >= 80) return '#d1ecf1';
    if (props.score >= 70) return '#fff3cd';
    return '#f8d7da';
  }};
  color: ${props => {
    if (props.score >= 90) return '#155724';
    if (props.score >= 80) return '#0c5460';
    if (props.score >= 70) return '#856404';
    return '#721c24';
  }};
`;

const CardContent = styled.div`
  margin-bottom: 16px;
`;

const DetailRow = styled.div`
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
  font-size: 14px;
`;

// DetailLabel and DetailValue are imported from DetailModal

const ValidationResult = styled.div`
  margin-top: 16px;
  padding: 16px;
  background: var(--background-secondary);
  border-radius: var(--border-radius);
  border-left: 4px solid var(--primary-color);
`;

const ValidationTitle = styled.div`
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 12px;
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 8px;
`;

const ValidationMetrics = styled.div`
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
  margin-bottom: 12px;
`;

const MetricItem = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
`;

const MetricLabel = styled.span`
  font-size: 12px;
  color: var(--text-secondary);
  min-width: 60px;
`;

const MetricBar = styled.div`
  flex: 1;
  height: 6px;
  background: var(--border-color);
  border-radius: 3px;
  overflow: hidden;
`;

const MetricFill = styled.div`
  height: 100%;
  background: var(--primary-color);
  width: ${props => props.score}%;
  transition: width 0.3s ease;
`;

const MetricValue = styled.span`
  font-size: 12px;
  color: var(--text-secondary);
  min-width: 25px;
`;

const CardActions = styled.div`
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

const IssueList = styled.div`
  margin-top: 12px;
`;

const IssueItem = styled.div`
  padding: 8px 12px;
  background: white;
  border-radius: var(--border-radius);
  margin-bottom: 8px;
  font-size: 12px;
  border-left: 3px solid ${props => props.severity === 'high' ? '#dc3545' : props.severity === 'medium' ? '#ffc107' : '#28a745'};
`;

// 샘플 데이터
const coverLetters = [
  {
    id: 1,
    name: '김철수',
    position: '프론트엔드 개발자',
    submittedDate: '2024-01-15',
    wordCount: 1200,
    validationScore: 92,
    originality: 95,
    coherence: 88,
    grammar: 90,
    plagiarism: 98,
    analysis: '자소서의 구성이 체계적이고, 구체적인 경험을 잘 서술했습니다.',
    issues: [
      { text: '일부 문장이 다소 길어 가독성이 떨어집니다', severity: 'low' },
      { text: '특정 기술 스택에 대한 설명이 부족합니다', severity: 'medium' }
    ]
  },
  {
    id: 2,
    name: '이영희',
    position: '백엔드 개발자',
    submittedDate: '2024-01-14',
    wordCount: 1500,
    validationScore: 85,
    originality: 90,
    coherence: 85,
    grammar: 88,
    plagiarism: 92,
    analysis: '기술적 경험을 잘 설명했으나, 일부 문장이 개선이 필요합니다.',
    issues: [
      { text: '문법 오류가 3건 발견되었습니다', severity: 'medium' },
      { text: '다른 지원자와 유사한 표현이 사용되었습니다', severity: 'high' }
    ]
  },
  {
    id: 3,
    name: '박민수',
    position: 'UI/UX 디자이너',
    submittedDate: '2024-01-13',
    wordCount: 800,
    validationScore: 78,
    originality: 85,
    coherence: 75,
    grammar: 80,
    plagiarism: 88,
    analysis: '창의적인 아이디어는 좋으나, 구체적인 프로젝트 경험이 부족합니다.',
    issues: [
      { text: '자소서 길이가 너무 짧습니다', severity: 'high' },
      { text: '디자인 프로세스 설명이 부족합니다', severity: 'medium' },
      { text: '결과 지표가 구체적이지 않습니다', severity: 'medium' }
    ]
  }
];

const CoverLetterValidation = () => {
  const [selectedCoverLetter, setSelectedCoverLetter] = useState(null);
  const [isDetailModalOpen, setIsDetailModalOpen] = useState(false);

  return (
    <CoverLetterContainer>
      <Header>
        <Title>자소서 검증</Title>
        <ActionButtons>
          <Button className="secondary">
            <FiFileText />
            일괄 분석
          </Button>
          <Button className="primary">
            <FiEdit3 />
            새 자소서 검증
          </Button>
        </ActionButtons>
      </Header>

      <CoverLetterGrid>
        {coverLetters.map((coverLetter, index) => (
          <CoverLetterCard
            key={coverLetter.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: index * 0.1 }}
          >
            <CardHeader>
              <ApplicantInfo>
                <ApplicantName>{coverLetter.name}</ApplicantName>
                <ApplicantPosition>{coverLetter.position}</ApplicantPosition>
              </ApplicantInfo>
              <ValidationScore score={coverLetter.validationScore}>
                {coverLetter.validationScore}점
              </ValidationScore>
            </CardHeader>

            <CardContent>
              <DetailRow>
                <DetailLabel>제출일:</DetailLabel>
                <DetailValue>{coverLetter.submittedDate}</DetailValue>
              </DetailRow>
              <DetailRow>
                <DetailLabel>글자 수:</DetailLabel>
                <DetailValue>{coverLetter.wordCount}자</DetailValue>
              </DetailRow>
            </CardContent>

            <ValidationResult>
              <ValidationTitle>
                <FiCheckCircle />
                AI 검증 결과
              </ValidationTitle>
              <ValidationMetrics>
                <MetricItem>
                  <MetricLabel>독창성</MetricLabel>
                  <MetricBar>
                    <MetricFill score={coverLetter.originality} />
                  </MetricBar>
                  <MetricValue>{coverLetter.originality}%</MetricValue>
                </MetricItem>
                <MetricItem>
                  <MetricLabel>일관성</MetricLabel>
                  <MetricBar>
                    <MetricFill score={coverLetter.coherence} />
                  </MetricBar>
                  <MetricValue>{coverLetter.coherence}%</MetricValue>
                </MetricItem>
                <MetricItem>
                  <MetricLabel>문법</MetricLabel>
                  <MetricBar>
                    <MetricFill score={coverLetter.grammar} />
                  </MetricBar>
                  <MetricValue>{coverLetter.grammar}%</MetricValue>
                </MetricItem>
                <MetricItem>
                  <MetricLabel>표절 검사</MetricLabel>
                  <MetricBar>
                    <MetricFill score={coverLetter.plagiarism} />
                  </MetricBar>
                  <MetricValue>{coverLetter.plagiarism}%</MetricValue>
                </MetricItem>
              </ValidationMetrics>
              
              <div style={{ fontSize: '12px', color: 'var(--text-secondary)', marginBottom: '12px' }}>
                {coverLetter.analysis}
              </div>
              
              <IssueList>
                <div style={{ fontSize: '12px', fontWeight: '600', marginBottom: '8px', color: 'var(--text-primary)' }}>
                  개선 사항:
                </div>
                {coverLetter.issues.map((issue, iIndex) => (
                  <IssueItem key={iIndex} severity={issue.severity}>
                    {issue.text}
                  </IssueItem>
                ))}
              </IssueList>
            </ValidationResult>

            <CardActions>
              <ActionButton onClick={() => {
                setSelectedCoverLetter(coverLetter);
                setIsDetailModalOpen(true);
              }}>
                <FiEye />
                상세보기
              </ActionButton>
              <ActionButton>
                <FiDownload />
                리포트
              </ActionButton>
              <ActionButton>
                <FiEdit3 />
                수정 제안
              </ActionButton>
            </CardActions>
          </CoverLetterCard>
        ))}
      </CoverLetterGrid>

      {/* 자소서 상세보기 모달 */}
      <DetailModal
        isOpen={isDetailModalOpen}
        onClose={() => {
          setIsDetailModalOpen(false);
          setSelectedCoverLetter(null);
        }}
        title={selectedCoverLetter ? `${selectedCoverLetter.name} 자소서 상세` : ''}
        onEdit={() => {
          // 수정 기능 구현
          console.log('자소서 수정:', selectedCoverLetter);
        }}
        onDelete={() => {
          // 삭제 기능 구현
          console.log('자소서 삭제:', selectedCoverLetter);
        }}
      >
        {selectedCoverLetter && (
          <>
            <DetailSection>
              <SectionTitle>지원자 정보</SectionTitle>
              <DetailGrid>
                <DetailItem>
                  <DetailLabel>지원자명</DetailLabel>
                  <DetailValue>{selectedCoverLetter.name}</DetailValue>
                </DetailItem>
                <DetailItem>
                  <DetailLabel>지원 직무</DetailLabel>
                  <DetailValue>{selectedCoverLetter.position}</DetailValue>
                </DetailItem>
                <DetailItem>
                  <DetailLabel>제출일</DetailLabel>
                  <DetailValue>{selectedCoverLetter.submittedDate}</DetailValue>
                </DetailItem>
                <DetailItem>
                  <DetailLabel>글자 수</DetailLabel>
                  <DetailValue>{selectedCoverLetter.wordCount}자</DetailValue>
                </DetailItem>
                <DetailItem>
                  <DetailLabel>검증 점수</DetailLabel>
                  <DetailValue>{selectedCoverLetter.validationScore}점</DetailValue>
                </DetailItem>
              </DetailGrid>
            </DetailSection>

            <DetailSection>
              <SectionTitle>AI 검증 결과</SectionTitle>
              <DetailGrid>
                <DetailItem>
                  <DetailLabel>독창성</DetailLabel>
                  <DetailValue>{selectedCoverLetter.originality}%</DetailValue>
                </DetailItem>
                <DetailItem>
                  <DetailLabel>일관성</DetailLabel>
                  <DetailValue>{selectedCoverLetter.coherence}%</DetailValue>
                </DetailItem>
                <DetailItem>
                  <DetailLabel>문법</DetailLabel>
                  <DetailValue>{selectedCoverLetter.grammar}%</DetailValue>
                </DetailItem>
                <DetailItem>
                  <DetailLabel>표절 검사</DetailLabel>
                  <DetailValue>{selectedCoverLetter.plagiarism}%</DetailValue>
                </DetailItem>
              </DetailGrid>
            </DetailSection>

            <DetailSection>
              <SectionTitle>분석 결과</SectionTitle>
              <DetailText>
                {selectedCoverLetter.analysis}
              </DetailText>
            </DetailSection>

            <DetailSection>
              <SectionTitle>개선 사항</SectionTitle>
              <DetailText>
                {selectedCoverLetter.issues.map((issue, index) => (
                  <div key={index} style={{ 
                    marginBottom: '8px', 
                    padding: '8px', 
                    backgroundColor: issue.severity === 'high' ? '#fee2e2' : issue.severity === 'medium' ? '#fef3c7' : '#d1fae5',
                    borderRadius: '4px',
                    borderLeft: `4px solid ${issue.severity === 'high' ? '#ef4444' : issue.severity === 'medium' ? '#f59e0b' : '#10b981'}`
                  }}>
                    {issue.text}
                  </div>
                ))}
              </DetailText>
            </DetailSection>
          </>
        )}
      </DetailModal>
    </CoverLetterContainer>
  );
};

export default CoverLetterValidation; 