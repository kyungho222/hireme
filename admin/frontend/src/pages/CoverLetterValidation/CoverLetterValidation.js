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
  FiPercent,
  FiXCircle,
  FiAlertTriangle,
  FiThumbsUp,
  FiTarget,
  FiSearch,
  FiCopy,
  FiShield
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
  font-size: 42px;
  font-weight: 700;
  color: var(--text-primary);
`;

const ActionButtons = styled.div`
  display: flex;
  gap: 12px;
`;

const Button = styled.button`
  padding: 16px 32px;
  border: none;
  border-radius: var(--border-radius);
  font-weight: 500;
  cursor: pointer;
  transition: var(--transition);
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 18px;
  
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
  grid-template-columns: repeat(auto-fill, minmax(450px, 1fr));
  gap: 24px;
`;

const CoverLetterCard = styled(motion.div)`
  background: white;
  border-radius: var(--border-radius);
  padding: 32px;
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
  margin-bottom: 24px;
`;

const ApplicantInfo = styled.div`
  flex: 1;
`;

const ApplicantName = styled.h3`
  font-size: 26px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 8px;
`;

const ApplicantPosition = styled.div`
  font-size: 18px;
  color: var(--text-secondary);
  margin-bottom: 12px;
`;

const ValidationScore = styled.span`
  padding: 12px 24px;
  border-radius: 25px;
  font-size: 20px;
  font-weight: 700;
  background: ${props => {
    if (props.score >= 90) return '#dcfce7'; // 연한 초록색
    if (props.score >= 80) return '#fef3c7'; // 연한 노란색
    return '#fee2e2'; // 연한 빨간색
  }};
  color: ${props => {
    if (props.score >= 90) return '#166534'; // 진한 초록색
    if (props.score >= 80) return '#92400e'; // 진한 노란색
    return '#dc2626'; // 진한 빨간색
  }};
  border: 2px solid ${props => {
    if (props.score >= 90) return '#22c55e';
    if (props.score >= 80) return '#f59e0b';
    return '#ef4444';
  }};
  min-width: 80px;
  text-align: center;
`;

const CardContent = styled.div`
  margin-bottom: 24px;
`;

const DetailRow = styled.div`
  display: flex;
  justify-content: space-between;
  margin-bottom: 12px;
  font-size: 18px;
`;

const ValidationResult = styled.div`
  margin-top: 24px;
  padding: 24px;
  background: var(--background-secondary);
  border-radius: var(--border-radius);
  border-left: 4px solid var(--primary-color);
`;

const ValidationTitle = styled.div`
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 20px;
  font-size: 20px;
  display: flex;
  align-items: center;
  gap: 8px;
`;

const ValidationMetrics = styled.div`
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
  margin-bottom: 20px;
`;

const MetricItem = styled.div`
  display: flex;
  align-items: center;
  gap: 12px;
`;

const MetricLabel = styled.span`
  font-size: 16px;
  color: var(--text-secondary);
  min-width: 80px;
  font-weight: 500;
`;

const MetricBar = styled.div`
  flex: 1;
  height: 10px;
  background: var(--border-color);
  border-radius: 5px;
  overflow: hidden;
`;

const MetricFill = styled.div`
  height: 100%;
  background: ${props => {
    if (props.score >= 90) return '#22c55e'; // 초록색
    if (props.score >= 80) return '#f59e0b'; // 노란색
    return '#ef4444'; // 빨간색
  }};
  width: ${props => props.score}%;
  transition: width 0.3s ease;
`;

const MetricValue = styled.span`
  font-size: 16px;
  color: var(--text-secondary);
  min-width: 35px;
  font-weight: 500;
`;

const CardActions = styled.div`
  display: flex;
  gap: 12px;
  margin-top: 24px;
`;

const ActionButton = styled.button`
  padding: 12px 20px;
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius);
  background: white;
  cursor: pointer;
  font-size: 16px;
  transition: var(--transition);
  display: flex;
  align-items: center;
  gap: 8px;
  
  &:hover {
    background: var(--background-secondary);
    border-color: var(--primary-color);
  }
`;

const IssueList = styled.div`
  margin-top: 20px;
`;

const IssueItem = styled.div`
  padding: 16px 20px;
  border-radius: var(--border-radius);
  margin-bottom: 12px;
  font-size: 16px;
  display: flex;
  align-items: center;
  gap: 12px;
  background: ${props => {
    if (props.severity === 'high') return '#fee2e2'; // 빨간색 배경
    if (props.severity === 'medium') return '#fef3c7'; // 노란색 배경
    return '#dcfce7'; // 초록색 배경
  }};
  border-left: 4px solid ${props => {
    if (props.severity === 'high') return '#ef4444'; // 빨간색
    if (props.severity === 'medium') return '#f59e0b'; // 노란색
    return '#22c55e'; // 초록색
  }};
  color: ${props => {
    if (props.severity === 'high') return '#991b1b'; // 진한 빨간색
    if (props.severity === 'medium') return '#92400e'; // 진한 노란색
    return '#166534'; // 진한 초록색
  }};
`;

const IssueIcon = styled.div`
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: ${props => {
    if (props.severity === 'high') return '#ef4444'; // 빨간색
    if (props.severity === 'medium') return '#f59e0b'; // 노란색
    return '#22c55e'; // 초록색
  }};
  color: white;
  font-size: 14px;
`;

const IssueText = styled.span`
  flex: 1;
  font-weight: 500;
`;

// 새로운 컴포넌트들
const KeywordSection = styled.div`
  margin-top: 20px;
  padding: 20px;
  background: #f8fafc;
  border-radius: var(--border-radius);
  border: 1px solid #e2e8f0;
`;

const KeywordTitle = styled.div`
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 16px;
  display: flex;
  align-items: center;
  gap: 8px;
`;

const KeywordMatch = styled.div`
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
  font-size: 16px;
`;

const MatchCount = styled.span`
  background: #22c55e;
  color: white;
  padding: 6px 12px;
  border-radius: 15px;
  font-size: 14px;
  font-weight: 600;
`;

const KeywordList = styled.div`
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 10px;
`;

const KeywordTag = styled.span`
  background: ${props => props.matched ? '#dcfce7' : '#fef3c7'};
  color: ${props => props.matched ? '#166534' : '#92400e'};
  padding: 6px 12px;
  border-radius: 15px;
  font-size: 14px;
  font-weight: 500;
  border: 1px solid ${props => props.matched ? '#22c55e' : '#f59e0b'};
`;

const PlagiarismSection = styled.div`
  margin-top: 20px;
  padding: 20px;
  background: ${props => props.score > 90 ? '#dcfce7' : props.score > 80 ? '#fef3c7' : '#fee2e2'};
  border-radius: var(--border-radius);
  border-left: 4px solid ${props => props.score > 90 ? '#22c55e' : props.score > 80 ? '#f59e0b' : '#ef4444'};
`;

const PlagiarismTitle = styled.div`
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 16px;
  display: flex;
  align-items: center;
  gap: 8px;
`;

const PlagiarismScore = styled.div`
  font-size: 22px;
  font-weight: 700;
  color: ${props => props.score > 90 ? '#166534' : props.score > 80 ? '#92400e' : '#dc2626'};
  margin-bottom: 10px;
`;

const PlagiarismDetail = styled.div`
  font-size: 16px;
  color: var(--text-secondary);
  line-height: 1.6;
`;

// 샘플 데이터 업데이트
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
    contentStructure: 94,
    keywordMatch: 85,
    jobRelevance: 92,
    writingQuality: 88,
    analysis: '자소서의 구성이 체계적이고, 구체적인 경험을 잘 서술했습니다.',
    issues: [
      { text: '일부 문장이 다소 길어 가독성이 떨어집니다', severity: 'low', type: 'improvement' },
      { text: '특정 기술 스택에 대한 설명이 부족합니다', severity: 'medium', type: 'improvement' }
    ],
    keywords: {
      required: ['React', 'JavaScript', '협업', '프로젝트 경험', '사용자 경험', '성능 최적화', 'Git'],
      matched: ['React', 'JavaScript', '협업', '프로젝트 경험', '사용자 경험', 'Git'],
      total: 7,
      matchedCount: 6
    },
    plagiarismDetails: {
      score: 98,
      status: '우수',
      description: '표절 의심 구간이 없으며, 원문 작성이 확인되었습니다.'
    }
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
    contentStructure: 88,
    keywordMatch: 78,
    jobRelevance: 85,
    writingQuality: 82,
    analysis: '기술적 경험을 잘 설명했으나, 일부 문장이 개선이 필요합니다.',
    issues: [
      { text: '문법 오류가 3건 발견되었습니다', severity: 'high', type: 'error' },
      { text: '다른 지원자와 유사한 표현이 사용되었습니다', severity: 'high', type: 'error' },
      { text: '프로젝트 결과에 대한 구체적 수치가 부족합니다', severity: 'medium', type: 'improvement' }
    ],
    keywords: {
      required: ['Java', 'Spring', '데이터베이스', 'API 설계', '성능 튜닝', '보안', '마이크로서비스'],
      matched: ['Java', 'Spring', '데이터베이스', 'API 설계'],
      total: 7,
      matchedCount: 4
    },
    plagiarismDetails: {
      score: 92,
      status: '양호',
      description: '일부 구간에서 유사한 표현이 발견되었으나, 전반적으로 양호합니다.'
    }
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
    contentStructure: 82,
    keywordMatch: 72,
    jobRelevance: 78,
    writingQuality: 75,
    analysis: '창의적인 아이디어는 좋으나, 구체적인 프로젝트 경험이 부족합니다.',
    issues: [
      { text: '자소서 길이가 너무 짧습니다', severity: 'high', type: 'error' },
      { text: '디자인 프로세스 설명이 부족합니다', severity: 'medium', type: 'improvement' },
      { text: '결과 지표가 구체적이지 않습니다', severity: 'medium', type: 'improvement' },
      { text: '사용자 피드백 반영 과정이 잘 서술되었습니다', severity: 'low', type: 'strength' }
    ],
    keywords: {
      required: ['Figma', '사용자 연구', '프로토타이핑', '디자인 시스템', '사용자 테스트', '접근성'],
      matched: ['Figma', '프로토타이핑'],
      total: 6,
      matchedCount: 2
    },
    plagiarismDetails: {
      score: 88,
      status: '주의',
      description: '일부 구간에서 다른 자소서와 유사한 표현이 발견되었습니다.'
    }
  }
];

const CoverLetterValidation = () => {
  const [selectedCoverLetter, setSelectedCoverLetter] = useState(null);
  const [isDetailModalOpen, setIsDetailModalOpen] = useState(false);

  const getIssueIcon = (type, severity) => {
    if (type === 'error') return <FiXCircle />;
    if (type === 'improvement') return <FiAlertTriangle />;
    if (type === 'strength') return <FiThumbsUp />;
    return <FiAlertCircle />;
  };

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
                  <MetricLabel>내용 구조</MetricLabel>
                  <MetricBar>
                    <MetricFill score={coverLetter.contentStructure} />
                  </MetricBar>
                  <MetricValue>{coverLetter.contentStructure}%</MetricValue>
                </MetricItem>
                <MetricItem>
                  <MetricLabel>키워드 적합성</MetricLabel>
                  <MetricBar>
                    <MetricFill score={coverLetter.keywordMatch} />
                  </MetricBar>
                  <MetricValue>{coverLetter.keywordMatch}%</MetricValue>
                </MetricItem>
                <MetricItem>
                  <MetricLabel>직무 연관성</MetricLabel>
                  <MetricBar>
                    <MetricFill score={coverLetter.jobRelevance} />
                  </MetricBar>
                  <MetricValue>{coverLetter.jobRelevance}%</MetricValue>
                </MetricItem>
                <MetricItem>
                  <MetricLabel>문체 품질</MetricLabel>
                  <MetricBar>
                    <MetricFill score={coverLetter.writingQuality} />
                  </MetricBar>
                  <MetricValue>{coverLetter.writingQuality}%</MetricValue>
                </MetricItem>
                <MetricItem>
                  <MetricLabel>문법/표현</MetricLabel>
                  <MetricBar>
                    <MetricFill score={coverLetter.grammar} />
                  </MetricBar>
                  <MetricValue>{coverLetter.grammar}%</MetricValue>
                </MetricItem>
                <MetricItem>
                  <MetricLabel>표절률</MetricLabel>
                  <MetricBar>
                    <MetricFill score={coverLetter.plagiarism} />
                  </MetricBar>
                  <MetricValue>{coverLetter.plagiarism}%</MetricValue>
                </MetricItem>
              </ValidationMetrics>
              
              <div style={{ fontSize: '16px', color: 'var(--text-secondary)', marginBottom: '20px', lineHeight: '1.6' }}>
                {coverLetter.analysis}
              </div>

              {/* 키워드/직무 적합성 영역 */}
              <KeywordSection>
                <KeywordTitle>
                  <FiTarget />
                  키워드/직무 적합성
                </KeywordTitle>
                                 <KeywordMatch>
                   <MatchCount>✅ {coverLetter.keywords.total}개 중 {coverLetter.keywords.matchedCount}개 일치</MatchCount>
                   <span style={{ fontSize: '16px', color: 'var(--text-secondary)' }}>
                     ({coverLetter.keywords.matchedCount}/{coverLetter.keywords.total})
                   </span>
                 </KeywordMatch>
                <KeywordList>
                  {coverLetter.keywords.required.map((keyword, idx) => (
                    <KeywordTag 
                      key={idx} 
                      matched={coverLetter.keywords.matched.includes(keyword)}
                    >
                      {keyword}
                    </KeywordTag>
                  ))}
                </KeywordList>
              </KeywordSection>

              {/* 표절 탐지 시각화 */}
              <PlagiarismSection score={coverLetter.plagiarismDetails.score}>
                <PlagiarismTitle>
                  <FiShield />
                  표절 탐지 결과
                </PlagiarismTitle>
                <PlagiarismScore score={coverLetter.plagiarismDetails.score}>
                  {coverLetter.plagiarismDetails.score}% - {coverLetter.plagiarismDetails.status}
                </PlagiarismScore>
                <PlagiarismDetail>
                  {coverLetter.plagiarismDetails.description}
                </PlagiarismDetail>
              </PlagiarismSection>
              
              <IssueList>
                <div style={{ fontSize: '18px', fontWeight: '600', marginBottom: '16px', color: 'var(--text-primary)' }}>
                  개선 사항:
                </div>
                {coverLetter.issues.map((issue, iIndex) => (
                  <IssueItem key={iIndex} severity={issue.severity}>
                    <IssueIcon severity={issue.severity}>
                      {getIssueIcon(issue.type, issue.severity)}
                    </IssueIcon>
                    <IssueText>{issue.text}</IssueText>
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
                  <DetailLabel>내용 구조</DetailLabel>
                  <DetailValue>{selectedCoverLetter.contentStructure}%</DetailValue>
                </DetailItem>
                <DetailItem>
                  <DetailLabel>키워드 적합성</DetailLabel>
                  <DetailValue>{selectedCoverLetter.keywordMatch}%</DetailValue>
                </DetailItem>
                <DetailItem>
                  <DetailLabel>직무 연관성</DetailLabel>
                  <DetailValue>{selectedCoverLetter.jobRelevance}%</DetailValue>
                </DetailItem>
                <DetailItem>
                  <DetailLabel>문체 품질</DetailLabel>
                  <DetailValue>{selectedCoverLetter.writingQuality}%</DetailValue>
                </DetailItem>
                <DetailItem>
                  <DetailLabel>문법/표현</DetailLabel>
                  <DetailValue>{selectedCoverLetter.grammar}%</DetailValue>
                </DetailItem>
                <DetailItem>
                  <DetailLabel>표절률</DetailLabel>
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
                    marginBottom: '16px', 
                    padding: '16px 20px', 
                    backgroundColor: issue.severity === 'high' ? '#fee2e2' : issue.severity === 'medium' ? '#fef3c7' : '#dcfce7',
                    borderRadius: '8px',
                    borderLeft: `4px solid ${issue.severity === 'high' ? '#ef4444' : issue.severity === 'medium' ? '#f59e0b' : '#22c55e'}`,
                    display: 'flex',
                    alignItems: 'center',
                    gap: '12px',
                    color: issue.severity === 'high' ? '#991b1b' : issue.severity === 'medium' ? '#92400e' : '#166534'
                  }}>
                    <div style={{
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      width: '28px',
                      height: '28px',
                      borderRadius: '50%',
                      background: issue.severity === 'high' ? '#ef4444' : issue.severity === 'medium' ? '#f59e0b' : '#22c55e',
                      color: 'white',
                      fontSize: '14px'
                    }}>
                      {getIssueIcon(issue.type, issue.severity)}
                    </div>
                    <span style={{ fontWeight: '500', fontSize: '16px' }}>{issue.text}</span>
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