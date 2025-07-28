import React, { useState } from 'react';
import styled from 'styled-components';
import { motion } from 'framer-motion';
import { 
  FiVideo, 
  FiCalendar, 
  FiClock, 
  FiUser, 
  FiSettings,
  FiPlay,
  FiPause,
  FiEye,
  FiDownload,
  FiMessageSquare,
  FiCheckCircle,
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

const InterviewContainer = styled.div`
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

const StatsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 24px;
  margin-bottom: 32px;
`;

const StatCard = styled.div`
  background: white;
  border-radius: var(--border-radius);
  padding: 24px;
  box-shadow: var(--shadow-light);
  text-align: center;
`;

const StatValue = styled.div`
  font-size: 32px;
  font-weight: 700;
  color: var(--primary-color);
  margin-bottom: 8px;
`;

const StatLabel = styled.div`
  font-size: 14px;
  color: var(--text-secondary);
`;

const InterviewGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
  gap: 24px;
`;

const InterviewCard = styled(motion.div)`
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

const InterviewHeader = styled.div`
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

const InterviewDetails = styled.div`
  margin-bottom: 16px;
`;

const DetailRow = styled.div`
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
  font-size: 14px;
`;

// DetailLabel and DetailValue are imported from DetailModal

const AIAnalysis = styled.div`
  margin-top: 16px;
  padding: 16px;
  background: var(--background-secondary);
  border-radius: var(--border-radius);
  border-left: 4px solid var(--primary-color);
`;

const AnalysisTitle = styled.div`
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 12px;
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 8px;
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

const InterviewActions = styled.div`
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
  
  &.primary {
    background: var(--primary-color);
    color: white;
    border-color: var(--primary-color);
  }
`;

const QuestionList = styled.div`
  margin-top: 12px;
`;

const QuestionItem = styled.div`
  padding: 8px 12px;
  background: white;
  border-radius: var(--border-radius);
  margin-bottom: 8px;
  font-size: 12px;
  border-left: 3px solid var(--primary-color);
`;

// 샘플 데이터
const interviews = [
  {
    id: 1,
    name: '김철수',
    position: '프론트엔드 개발자',
    date: '2024-01-20',
    time: '14:00',
    duration: '60분',
    status: 'scheduled',
    type: '비대면',
    platform: 'Zoom',
    aiScore: 85,
    questions: [
      'React와 Vue.js의 차이점에 대해 설명해주세요',
      '상태 관리 라이브러리 사용 경험을 말씀해주세요',
      '성능 최적화 방법에 대해 설명해주세요'
    ],
    analysis: '기술적 이해도가 높고, 명확한 설명 능력을 보유합니다.'
  },
  {
    id: 2,
    name: '이영희',
    position: '백엔드 개발자',
    date: '2024-01-19',
    time: '15:30',
    duration: '90분',
    status: 'completed',
    type: '대면',
    platform: '회사 면접실',
    aiScore: 92,
    questions: [
      '마이크로서비스 아키텍처 설계 경험을 말씀해주세요',
      '데이터베이스 최적화 방법에 대해 설명해주세요',
      '보안 관련 경험을 말씀해주세요'
    ],
    analysis: '시스템 설계 경험이 풍부하고, 보안에 대한 이해도가 높습니다.'
  },
  {
    id: 3,
    name: '박민수',
    position: 'UI/UX 디자이너',
    date: '2024-01-21',
    time: '10:00',
    duration: '60분',
    status: 'in-progress',
    type: '비대면',
    platform: 'Teams',
    aiScore: 78,
    questions: [
      '디자인 시스템 구축 경험을 말씀해주세요',
      '사용자 리서치 방법론에 대해 설명해주세요',
      '프로토타이핑 도구 사용 경험을 말씀해주세요'
    ],
    analysis: '창의적인 디자인 감각을 보유하고 있으며, 사용자 중심 사고가 뛰어납니다.'
  }
];

const stats = [
  { label: '예정된 면접', value: '12' },
  { label: '진행 중', value: '3' },
  { label: '완료된 면접', value: '45' },
  { label: '평균 점수', value: '82' }
];

const getStatusText = (status) => {
  const statusMap = {
    scheduled: '예정됨',
    'in-progress': '진행 중',
    completed: '완료',
    cancelled: '취소됨'
  };
  return statusMap[status] || status;
};

const InterviewManagement = () => {
  const [selectedInterview, setSelectedInterview] = useState(null);
  const [isDetailModalOpen, setIsDetailModalOpen] = useState(false);

  return (
    <InterviewContainer>
      <Header>
        <Title>면접 관리</Title>
        <ActionButtons>
          <Button className="secondary">
            <FiSettings />
            AI 설정
          </Button>
          <Button className="primary">
            <FiCalendar />
            면접 일정 등록
          </Button>
        </ActionButtons>
      </Header>

      <StatsGrid>
        {stats.map((stat, index) => (
          <StatCard key={index}>
            <StatValue>{stat.value}</StatValue>
            <StatLabel>{stat.label}</StatLabel>
          </StatCard>
        ))}
      </StatsGrid>

      <InterviewGrid>
        {interviews.map((interview, index) => (
          <InterviewCard
            key={interview.id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: index * 0.1 }}
          >
            <InterviewHeader>
              <ApplicantInfo>
                <ApplicantName>{interview.name}</ApplicantName>
                <ApplicantPosition>{interview.position}</ApplicantPosition>
              </ApplicantInfo>
              <StatusBadge className={interview.status}>
                {getStatusText(interview.status)}
              </StatusBadge>
            </InterviewHeader>

            <InterviewDetails>
              <DetailRow>
                <DetailLabel>면접 일시:</DetailLabel>
                <DetailValue>{interview.date} {interview.time}</DetailValue>
              </DetailRow>
              <DetailRow>
                <DetailLabel>소요 시간:</DetailLabel>
                <DetailValue>{interview.duration}</DetailValue>
              </DetailRow>
              <DetailRow>
                <DetailLabel>면접 유형:</DetailLabel>
                <DetailValue>{interview.type}</DetailValue>
              </DetailRow>
              <DetailRow>
                <DetailLabel>플랫폼:</DetailLabel>
                <DetailValue>{interview.platform}</DetailValue>
              </DetailRow>
            </InterviewDetails>

            <AIAnalysis>
              <AnalysisTitle>
                <FiCheckCircle />
                AI 면접 분석
              </AnalysisTitle>
              <AnalysisScore>
                <ScoreText>종합 점수</ScoreText>
                <ScoreBar>
                  <ScoreFill score={interview.aiScore} />
                </ScoreBar>
                <ScoreText>{interview.aiScore}%</ScoreText>
              </AnalysisScore>
              <div style={{ fontSize: '12px', color: 'var(--text-secondary)', marginBottom: '12px' }}>
                {interview.analysis}
              </div>
              
              <QuestionList>
                <div style={{ fontSize: '12px', fontWeight: '600', marginBottom: '8px', color: 'var(--text-primary)' }}>
                  AI 생성 질문:
                </div>
                {interview.questions.map((question, qIndex) => (
                  <QuestionItem key={qIndex}>
                    {question}
                  </QuestionItem>
                ))}
              </QuestionList>
            </AIAnalysis>

            <InterviewActions>
              {interview.status === 'scheduled' && (
                <ActionButton className="primary">
                  <FiPlay />
                  면접 시작
                </ActionButton>
              )}
              {interview.status === 'in-progress' && (
                <ActionButton>
                  <FiPause />
                  일시정지
                </ActionButton>
              )}
              <ActionButton onClick={() => {
                setSelectedInterview(interview);
                setIsDetailModalOpen(true);
              }}>
                <FiEye />
                상세보기
              </ActionButton>
              <ActionButton>
                <FiDownload />
                녹화 다운로드
              </ActionButton>
              <ActionButton>
                <FiMessageSquare />
                피드백
              </ActionButton>
            </InterviewActions>
          </InterviewCard>
        ))}
      </InterviewGrid>

      {/* 면접 상세보기 모달 */}
      <DetailModal
        isOpen={isDetailModalOpen}
        onClose={() => {
          setIsDetailModalOpen(false);
          setSelectedInterview(null);
        }}
        title={selectedInterview ? `${selectedInterview.name} 면접 상세` : ''}
        onEdit={() => {
          // 수정 기능 구현
          console.log('면접 수정:', selectedInterview);
        }}
        onDelete={() => {
          // 삭제 기능 구현
          console.log('면접 삭제:', selectedInterview);
        }}
      >
        {selectedInterview && (
          <>
            <DetailSection>
              <SectionTitle>면접 정보</SectionTitle>
              <DetailGrid>
                <DetailItem>
                  <DetailLabel>지원자명</DetailLabel>
                  <DetailValue>{selectedInterview.name}</DetailValue>
                </DetailItem>
                <DetailItem>
                  <DetailLabel>지원 직무</DetailLabel>
                  <DetailValue>{selectedInterview.position}</DetailValue>
                </DetailItem>
                <DetailItem>
                  <DetailLabel>면접 일시</DetailLabel>
                  <DetailValue>{selectedInterview.date} {selectedInterview.time}</DetailValue>
                </DetailItem>
                <DetailItem>
                  <DetailLabel>소요 시간</DetailLabel>
                  <DetailValue>{selectedInterview.duration}</DetailValue>
                </DetailItem>
                <DetailItem>
                  <DetailLabel>면접 유형</DetailLabel>
                  <DetailValue>{selectedInterview.type}</DetailValue>
                </DetailItem>
                <DetailItem>
                  <DetailLabel>플랫폼</DetailLabel>
                  <DetailValue>{selectedInterview.platform}</DetailValue>
                </DetailItem>
                <DetailItem>
                  <DetailLabel>상태</DetailLabel>
                  <StatusBadge className={selectedInterview.status}>
                    {getStatusText(selectedInterview.status)}
                  </StatusBadge>
                </DetailItem>
              </DetailGrid>
            </DetailSection>

            <DetailSection>
              <SectionTitle>AI 면접 분석</SectionTitle>
              <DetailGrid>
                <DetailItem>
                  <DetailLabel>종합 점수</DetailLabel>
                  <DetailValue>{selectedInterview.aiScore}%</DetailValue>
                </DetailItem>
                <DetailItem>
                  <DetailLabel>분석 결과</DetailLabel>
                  <DetailValue>{selectedInterview.analysis}</DetailValue>
                </DetailItem>
              </DetailGrid>
            </DetailSection>

            <DetailSection>
              <SectionTitle>AI 생성 질문</SectionTitle>
              <DetailText>
                {selectedInterview.questions.map((question, index) => (
                  <div key={index} style={{ marginBottom: '8px', padding: '8px', backgroundColor: '#f9fafb', borderRadius: '4px' }}>
                    {index + 1}. {question}
                  </div>
                ))}
              </DetailText>
            </DetailSection>
          </>
        )}
      </DetailModal>
    </InterviewContainer>
  );
};

export default InterviewManagement; 