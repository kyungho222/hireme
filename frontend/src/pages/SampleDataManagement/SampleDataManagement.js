import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { motion } from 'framer-motion';
import {
  FiDatabase,
  FiUsers,
  FiBriefcase,
  FiCheckCircle,
  FiAlertCircle,
  FiRefreshCw,
  FiTrash2,
  FiPlus,
  FiInfo,
  FiHelpCircle,
  FiFileText,
  FiUpload,
  FiDownload,
  FiCode,
  FiTable,
  FiUser
} from 'react-icons/fi';

const Container = styled.div`
  padding: 24px 0;
`;

const Header = styled.div`
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: var(--border-radius);
  padding: 32px;
  color: white;
  margin-bottom: 32px;
  text-align: center;
`;

const Title = styled.h1`
  font-size: 36px;
  font-weight: 700;
  margin-bottom: 16px;
`;

const Subtitle = styled.p`
  font-size: 16px;
  opacity: 0.9;
  max-width: 600px;
  margin: 0 auto;
`;

const Content = styled.div`
  max-width: 1200px;
  margin: 0 auto;
`;

const StatsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 24px;
  margin-bottom: 32px;
`;

const StatCard = styled(motion.div)`
  background: white;
  border-radius: var(--border-radius);
  padding: 24px;
  box-shadow: var(--shadow-light);
  transition: var(--transition);

  &:hover {
    transform: translateY(-4px);
    box-shadow: var(--shadow-medium);
  }
`;

const StatHeader = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
`;

const StatIcon = styled.div`
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 24px;
`;

const StatValue = styled.div`
  font-size: 32px;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 8px;
`;

const StatLabel = styled.div`
  font-size: 14px;
  color: var(--text-secondary);
  font-weight: 500;
`;

const Section = styled.div`
  background: white;
  border-radius: var(--border-radius);
  padding: 32px;
  box-shadow: var(--shadow-light);
  margin-bottom: 24px;
`;

const SectionTitle = styled.h2`
  font-size: 24px;
  font-weight: 700;
  margin-bottom: 24px;
  color: var(--text-primary);
  display: flex;
  align-items: center;
  gap: 12px;
`;

const Button = styled.button`
  background: ${props => props.variant === 'danger' ? '#dc3545' : props.variant === 'success' ? '#28a745' : '#007bff'};
  color: white;
  border: none;
  border-radius: var(--border-radius);
  padding: 12px 24px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: var(--transition);
  display: flex;
  align-items: center;
  gap: 8px;

  &:hover {
    background: ${props => props.variant === 'danger' ? '#c82333' : props.variant === 'success' ? '#218838' : '#0056b3'};
    transform: translateY(-2px);
  }

  &:disabled {
    background: #6c757d;
    cursor: not-allowed;
    transform: none;
  }
`;

const ButtonGroup = styled.div`
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
`;

const Alert = styled.div`
  padding: 16px;
  border-radius: var(--border-radius);
  margin-bottom: 24px;
  display: flex;
  align-items: center;
  gap: 12px;
  background: ${props => props.type === 'success' ? '#d4edda' : props.type === 'error' ? '#f8d7da' : '#d1ecf1'};
  color: ${props => props.type === 'success' ? '#155724' : props.type === 'error' ? '#721c24' : '#0c5460'};
  border: 1px solid ${props => props.type === 'success' ? '#c3e6cb' : props.type === 'error' ? '#f5c6cb' : '#bee5eb'};
`;

const ProgressBar = styled.div`
  width: 100%;
  height: 8px;
  background: #e9ecef;
  border-radius: 4px;
  overflow: hidden;
  margin-top: 12px;
`;

const ProgressFill = styled.div`
  height: 100%;
  background: linear-gradient(90deg, #007bff, #28a745);
  width: ${props => props.progress}%;
  transition: width 0.3s ease;
`;

const InfoCard = styled.div`
  background: #f8f9fa;
  border: 1px solid #dee2e6;
  border-radius: var(--border-radius);
  padding: 20px;
  margin-bottom: 24px;
`;

const InfoTitle = styled.h3`
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 12px;
  color: var(--text-primary);
  display: flex;
  align-items: center;
  gap: 8px;
`;

const InfoList = styled.ul`
  list-style: none;
  padding: 0;
  margin: 0;
`;

const InfoItem = styled.li`
  padding: 8px 0;
  border-bottom: 1px solid #dee2e6;
  display: flex;
  justify-content: space-between;
  align-items: center;

  &:last-child {
    border-bottom: none;
  }
`;

const SchemaContainer = styled.div`
  background: #f8f9fa;
  border: 1px solid #dee2e6;
  border-radius: var(--border-radius);
  padding: 20px;
  margin-bottom: 24px;
`;

const SchemaTitle = styled.h3`
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 16px;
  color: var(--text-primary);
  display: flex;
  align-items: center;
  gap: 8px;
`;

const SchemaTable = styled.table`
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
`;

const SchemaTh = styled.th`
  background: #e9ecef;
  padding: 12px;
  text-align: left;
  font-weight: 600;
  border: 1px solid #dee2e6;
`;

const SchemaTd = styled.td`
  padding: 12px;
  border: 1px solid #dee2e6;
  background: white;
`;

const FileUploadArea = styled.div`
  border: 2px dashed #dee2e6;
  border-radius: var(--border-radius);
  padding: 40px;
  text-align: center;
  background: #f8f9fa;
  transition: var(--transition);
  cursor: pointer;

  &:hover {
    border-color: #007bff;
    background: #f0f8ff;
  }

  &.dragover {
    border-color: #28a745;
    background: #f0fff0;
  }
`;

const FileInput = styled.input`
  display: none;
`;

const UploadIcon = styled.div`
  font-size: 48px;
  color: #6c757d;
  margin-bottom: 16px;
`;

const UploadText = styled.div`
  font-size: 16px;
  color: var(--text-secondary);
  margin-bottom: 8px;
`;

const UploadSubtext = styled.div`
  font-size: 14px;
  color: var(--text-light);
`;

const FormContainer = styled.div`
  background: #f8f9fa;
  border-radius: var(--border-radius);
  padding: 24px;
  margin-bottom: 24px;
`;

const FormTitle = styled.h3`
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 16px;
  display: flex;
  align-items: center;
  gap: 8px;
`;

const FormGrid = styled.div`
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  margin-bottom: 16px;

  @media (max-width: 768px) {
    grid-template-columns: 1fr;
  }
`;

const FormField = styled.div`
  display: flex;
  flex-direction: column;
`;

const FormLabel = styled.label`
  font-size: 14px;
  font-weight: 500;
  color: var(--text-secondary);
  margin-bottom: 8px;
`;

const FormInput = styled.input`
  padding: 12px 16px;
  border: 1px solid #dee2e6;
  border-radius: 8px;
  font-size: 14px;
  transition: var(--transition);

  &:focus {
    outline: none;
    border-color: #007bff;
    box-shadow: 0 0 0 3px rgba(0, 123, 255, 0.1);
  }

  &::placeholder {
    color: #6c757d;
  }
`;

const FormDescription = styled.div`
  font-size: 12px;
  color: var(--text-light);
  margin-top: 4px;
`;

const TabContainer = styled.div`
  margin-bottom: 24px;
`;

const TabList = styled.div`
  display: flex;
  border-bottom: 2px solid #dee2e6;
  margin-bottom: 24px;
`;

const Tab = styled.button`
  background: none;
  border: none;
  padding: 12px 24px;
  font-size: 16px;
  font-weight: 500;
  color: ${props => props.active ? '#007bff' : '#6c757d'};
  border-bottom: 2px solid ${props => props.active ? '#007bff' : 'transparent'};
  cursor: pointer;
  transition: var(--transition);

  &:hover {
    color: #007bff;
  }
`;

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const SampleDataManagement = () => {
  const [stats, setStats] = useState({
    totalApplicants: 0,
    totalJobPostings: 0,
    totalResumes: 0,
    totalCoverLetters: 0
  });
  const [loading, setLoading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [message, setMessage] = useState(null);
  const [currentOperation, setCurrentOperation] = useState('');
  const [activeTab, setActiveTab] = useState('help');
  const [uploadedFile, setUploadedFile] = useState(null);
  const [jobPostings, setJobPostings] = useState([]);
  const [applicants, setApplicants] = useState([]);

  // 개별 지원자 생성 상태
  const [singleApplicantForm, setSingleApplicantForm] = useState({
    name: '',
    email: '',
    github_url: ''
  });

  // 토스트 알림 상태
  const [showToast, setShowToast] = useState(false);
  const [toastMessage, setToastMessage] = useState('');
  const [toastType, setToastType] = useState('success');

  // 토스트 알림 표시 함수
  const showToastNotification = (message, type = 'success') => {
    setToastMessage(message);
    setToastType(type);
    setShowToast(true);

    // 5초 후 토스트 숨기기
    setTimeout(() => {
      setShowToast(false);
    }, 5000);
  };

  // 현재 데이터 통계 조회
  const loadCurrentStats = async () => {
    try {
      const [applicantsRes, jobPostingsRes] = await Promise.all([
        fetch(`${API_BASE_URL}/api/applicants/stats/overview`),
        fetch(`${API_BASE_URL}/api/job-postings/stats/overview`)
      ]);

      const applicantsData = await applicantsRes.json();
      const jobPostingsData = await jobPostingsRes.json();

      setStats({
        totalApplicants: applicantsData.total_applicants || 0,
        totalJobPostings: jobPostingsData.total_jobs || 0,
        totalResumes: applicantsData.total_applicants || 0, // 이력서는 지원자와 동일
        totalCoverLetters: applicantsData.total_applicants || 0 // 자소서는 지원자와 동일
      });
    } catch (error) {
      console.error('통계 조회 실패:', error);
    }
  };

  // 기존 채용공고 목록 조회
  const loadJobPostings = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/job-postings?limit=100`);
      if (response.ok) {
        const data = await response.json();
        // API 응답 구조에 따라 데이터 추출
        if (Array.isArray(data)) {
          setJobPostings(data);
        } else if (data.data && Array.isArray(data.data.job_postings)) {
          setJobPostings(data.data.job_postings);
        } else {
          setJobPostings([]);
        }
      }
    } catch (error) {
      console.error('채용공고 조회 실패:', error);
      setJobPostings([]);
    }
  };

  // 기존 지원자 목록 조회
  const loadApplicants = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/applicants?limit=1000`);
      if (response.ok) {
        const data = await response.json();
        setApplicants(data.applicants || []);
      }
    } catch (error) {
      console.error('지원자 조회 실패:', error);
      setApplicants([]);
    }
  };

  useEffect(() => {
    loadCurrentStats();
    loadJobPostings();
    loadApplicants();
  }, []);

  // 샘플 지원자 데이터 생성 (기존 채용공고 확인 후)
  const generateSampleApplicants = async (count = 50) => {
    // 먼저 기존 채용공고 확인
    if (jobPostings.length === 0) {
      setMessage({
        type: 'error',
        text: '지원자를 생성하기 전에 먼저 채용공고를 생성해주세요. 지원자는 반드시 채용공고에 소속되어야 합니다.'
      });
      return;
    }

    setLoading(true);
    setProgress(0);
    setCurrentOperation('지원자 샘플 데이터 생성 중...');
    setMessage({ type: 'info', text: '지원자 샘플 데이터를 생성하고 있습니다...' });

    try {
      const response = await fetch(`${API_BASE_URL}/api/sample/generate-applicants`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ count })
      });

      if (response.ok) {
        const result = await response.json();
        let successMessage = `${result.generated_count}명의 지원자 샘플 데이터가 생성되었습니다!`;

        if (result.job_postings_used) {
          successMessage += ` (${result.job_postings_used}개 직무의 채용공고에 매칭)`;
        }

        if (result.position_matching) {
          successMessage += `\n${result.position_matching}`;
        }

        setMessage({ type: 'success', text: successMessage });
        setProgress(100);
        loadCurrentStats(); // 통계 새로고침
        loadJobPostings(); // 채용공고 목록 새로고침
      } else {
        const errorData = await response.json();
        throw new Error(errorData.detail || '지원자 데이터 생성 실패');
      }
    } catch (error) {
      setMessage({ type: 'error', text: error.message || '지원자 샘플 데이터 생성에 실패했습니다.' });
      console.error('지원자 생성 오류:', error);
    } finally {
      setLoading(false);
      setCurrentOperation('');
    }
  };

  // 샘플 자소서 데이터 생성 (자소서가 없는 지원자들만)
  const generateSampleCoverLetters = async () => {
    // 먼저 기존 지원자 확인
    if (applicants.length === 0) {
      setMessage({
        type: 'error',
        text: '자소서를 생성하기 전에 먼저 지원자를 생성해주세요. 자소서는 반드시 지원자에 소속되어야 합니다.'
      });
      return;
    }

    setLoading(true);
    setProgress(0);
    setCurrentOperation('자소서 샘플 데이터 생성 중...');
    setMessage({ type: 'info', text: '자소서가 없는 지원자들을 위한 자소서 데이터를 생성하고 있습니다...' });

    try {
      const response = await fetch(`${API_BASE_URL}/api/sample/generate-cover-letters`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({})
      });

      if (response.ok) {
        const result = await response.json();
        setMessage({ type: 'success', text: result.message });
        setProgress(100);
        loadCurrentStats(); // 통계 새로고침
        loadApplicants(); // 지원자 목록 새로고침
      } else {
        const errorData = await response.json();
        throw new Error(errorData.detail || '자소서 데이터 생성 실패');
      }
    } catch (error) {
      setMessage({ type: 'error', text: error.message || '자소서 샘플 데이터 생성에 실패했습니다.' });
      console.error('자소서 생성 오류:', error);
    } finally {
      setLoading(false);
      setCurrentOperation('');
    }
  };

  // 샘플 채용공고 데이터 생성
  const generateSampleJobPostings = async (count = 10) => {
    setLoading(true);
    setProgress(0);
    setCurrentOperation('채용공고 샘플 데이터 생성 중...');
    setMessage({ type: 'info', text: '채용공고 샘플 데이터를 생성하고 있습니다...' });

    try {
      const response = await fetch(`${API_BASE_URL}/api/sample/generate-job-postings`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ count })
      });

      if (response.ok) {
        const result = await response.json();
        let successMessage = `${result.generated_count}개의 채용공고 샘플 데이터가 생성되었습니다!`;

        if (result.position_distribution) {
          successMessage += `\n직무별 분포: ${Object.entries(result.position_distribution).map(([pos, count]) => `${pos} ${count}개`).join(', ')}`;
        }

        if (result.matching_ready) {
          successMessage += `\n${result.matching_ready}`;
        }

        setMessage({ type: 'success', text: successMessage });
        setProgress(100);
        loadCurrentStats(); // 통계 새로고침
        loadJobPostings(); // 채용공고 목록 새로고침
      } else {
        throw new Error('채용공고 데이터 생성 실패');
      }
    } catch (error) {
      setMessage({ type: 'error', text: '채용공고 샘플 데이터 생성에 실패했습니다.' });
      console.error('채용공고 생성 오류:', error);
    } finally {
      setLoading(false);
      setCurrentOperation('');
    }
  };

  // 전체 데이터 초기화
  const resetAllData = async () => {
    if (!window.confirm('정말로 모든 데이터를 삭제하시겠습니까? 이 작업은 되돌릴 수 없습니다.')) {
      return;
    }

    setLoading(true);
    setProgress(0);
    setCurrentOperation('데이터 초기화 중...');
    setMessage({ type: 'info', text: '모든 데이터를 초기화하고 있습니다...' });

    try {
      const response = await fetch(`${API_BASE_URL}/api/sample/reset-all`, {
        method: 'POST'
      });

      if (response.ok) {
        setMessage({ type: 'success', text: '모든 데이터가 성공적으로 초기화되었습니다!' });
        setProgress(100);
        loadCurrentStats(); // 통계 새로고침
      } else {
        throw new Error('데이터 초기화 실패');
      }
    } catch (error) {
      setMessage({ type: 'error', text: '데이터 초기화에 실패했습니다.' });
      console.error('초기화 오류:', error);
    } finally {
      setLoading(false);
      setCurrentOperation('');
    }
  };



  // 개별 지원자 생성
  const createSingleApplicant = async () => {
    if (!singleApplicantForm.name || !singleApplicantForm.email) {
      setMessage({ type: 'error', text: '이름과 이메일은 필수 입력 항목입니다.' });
      return;
    }

    setLoading(true);
    setCurrentOperation('개별 지원자 생성 중...');
    setMessage({ type: 'info', text: '개별 지원자를 생성하고 있습니다...' });

    try {
      const response = await fetch(`${API_BASE_URL}/api/sample/create-single-applicant`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(singleApplicantForm)
      });

      if (response.ok) {
        const result = await response.json();
        const successMessage = `${result.message} (${result.job_posting.position} - ${result.job_posting.company})`;

        setMessage({
          type: 'success',
          text: successMessage
        });

        // 토스트 알림 표시
        showToastNotification(`✅ ${singleApplicantForm.name} 지원자가 성공적으로 등록되었습니다!`, 'success');

        // 폼 초기화
        setSingleApplicantForm({
          name: '',
          email: '',
          github_url: ''
        });

        // 데이터 새로고침
        loadCurrentStats();
        loadApplicants();
      } else {
        const errorData = await response.json();
        throw new Error(errorData.detail || '개별 지원자 생성 실패');
      }
    } catch (error) {
      setMessage({ type: 'error', text: error.message || '개별 지원자 생성에 실패했습니다.' });
      console.error('개별 지원자 생성 오류:', error);
    } finally {
      setLoading(false);
      setCurrentOperation('');
    }
  };

  // 파일 업로드 처리
  const handleFileUpload = async (file) => {
    if (!file) return;

    setLoading(true);
    setProgress(0);
    setCurrentOperation('JSON 파일 업로드 중...');
    setMessage({ type: 'info', text: 'JSON 파일을 업로드하고 있습니다...' });

    try {
      // JSON 파일 읽기
      const text = await file.text();
      const jsonData = JSON.parse(text);

      const response = await fetch(`${API_BASE_URL}/api/sample/upload-json`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(jsonData)
      });

            if (response.ok) {
        const result = await response.json();
        let successMessage = `${result.uploaded_count}개의 데이터가 성공적으로 업로드되었습니다!`;
        if (result.job_posting_count > 0) {
          successMessage += ` (기존 ${result.job_posting_count}개 채용공고에 랜덤 할당됨)`;
        }
        if (result.vector_saved_count > 0) {
          successMessage += ` ${result.vector_saved_count}개 데이터가 벡터 DB에 저장됨`;
        }
        setMessage({ type: 'success', text: successMessage });
        setProgress(100);
        loadCurrentStats();
        setUploadedFile(null);

        // 업로드 완료 후 자동으로 데이터 생성 탭으로 이동
        setTimeout(() => {
          setActiveTab('generate');
          let toastMessage = 'JSON 데이터 업로드 완료! 지원자들에게 채용공고가 자동 할당되었습니다.';
          if (result.vector_saved_count > 0) {
            toastMessage += ` 벡터 DB에도 ${result.vector_saved_count}개 저장됨`;
          }
          showToastNotification(toastMessage);
        }, 1500);
      } else {
        const errorData = await response.json();
        throw new Error(errorData.detail || '파일 업로드 실패');
      }
    } catch (error) {
      setMessage({ type: 'error', text: `JSON 파일 업로드에 실패했습니다: ${error.message}` });
      console.error('파일 업로드 오류:', error);
    } finally {
      setLoading(false);
      setCurrentOperation('');
    }
  };

  // 파일 드래그 앤 드롭 처리
  const handleDragOver = (e) => {
    e.preventDefault();
    e.currentTarget.classList.add('dragover');
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    e.currentTarget.classList.remove('dragover');
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.currentTarget.classList.remove('dragover');

    const files = e.dataTransfer.files;
    if (files.length > 0) {
      const file = files[0];
      if (file.type === 'application/json' || file.name.endsWith('.json')) {
        setUploadedFile(file);
        handleFileUpload(file);
      } else {
        setMessage({ type: 'error', text: 'JSON 파일(.json)만 업로드 가능합니다.' });
      }
    }
  };

  // 파일 선택 처리
  const handleFileSelect = (e) => {
    const file = e.target.files[0];
    if (file) {
      setUploadedFile(file);
      handleFileUpload(file);
    }
  };

  // JSON 템플릿 다운로드
  const downloadJsonTemplate = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/sample/json-template`);
      if (response.ok) {
        const template = await response.json();
        const blob = new Blob([JSON.stringify(template, null, 2)], { type: 'application/json' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'sample-data-template.json';
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        showToastNotification('JSON 템플릿이 다운로드되었습니다!');
      } else {
        throw new Error('템플릿 다운로드 실패');
      }
    } catch (error) {
      showToastNotification('템플릿 다운로드에 실패했습니다.', 'error');
      console.error('템플릿 다운로드 오류:', error);
    }
  };

  return (
    <Container>
      {/* 토스트 알림 */}
      {showToast && (
        <div
          style={{
            position: 'fixed',
            top: '20px',
            right: '20px',
            background: toastType === 'success'
              ? 'linear-gradient(135deg, #28a745 0%, #20c997 100%)'
              : toastType === 'error'
              ? 'linear-gradient(135deg, #dc3545 0%, #fd7e14 100%)'
              : 'linear-gradient(135deg, #007bff 0%, #6610f2 100%)',
            color: 'white',
            padding: '16px 20px',
            borderRadius: '12px',
            boxShadow: '0 8px 32px rgba(0, 0, 0, 0.15)',
            zIndex: 10000,
            maxWidth: '400px',
            fontSize: '14px',
            lineHeight: '1.5',
            animation: 'slideInRight 0.3s ease-out',
            border: '1px solid rgba(255, 255, 255, 0.2)',
            backdropFilter: 'blur(10px)',
            display: 'flex',
            alignItems: 'flex-start',
            gap: '12px'
          }}
        >
          <div style={{
            fontSize: '20px',
            marginTop: '2px'
          }}>
            {toastType === 'success' ? '✅' : toastType === 'error' ? '❌' : 'ℹ️'}
          </div>
          <div style={{ flex: 1 }}>
            {toastMessage.split('\n').map((line, index) => (
              <div key={index} style={{
                marginBottom: index < toastMessage.split('\n').length - 1 ? '4px' : '0'
              }}>
                {line}
              </div>
            ))}
          </div>
          <button
            onClick={() => setShowToast(false)}
            style={{
              background: 'none',
              border: 'none',
              color: 'white',
              cursor: 'pointer',
              fontSize: '16px',
              padding: '0',
              marginLeft: '8px',
              opacity: '0.8',
              transition: 'opacity 0.2s ease'
            }}
            onMouseEnter={(e) => e.target.style.opacity = '1'}
            onMouseLeave={(e) => e.target.style.opacity = '0.8'}
          >
            ×
          </button>
        </div>
      )}

      <Header>
        <Title>샘플 데이터 관리</Title>
        <Subtitle>
          개발 및 테스트를 위한 샘플 데이터를 생성하고 관리할 수 있습니다
        </Subtitle>
      </Header>

      <Content>
        {/* 현재 상태 */}
        <StatsGrid>
          <StatCard
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
          >
            <StatHeader>
              <div>
                <StatValue>{stats.totalApplicants.toLocaleString()}</StatValue>
                <StatLabel>총 지원자</StatLabel>
              </div>
              <StatIcon style={{ background: '#00c851' }}>
                <FiUsers size={24} />
              </StatIcon>
            </StatHeader>
          </StatCard>

          <StatCard
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.1 }}
          >
            <StatHeader>
              <div>
                <StatValue>{stats.totalJobPostings.toLocaleString()}</StatValue>
                <StatLabel>채용공고</StatLabel>
              </div>
              <StatIcon style={{ background: '#007bff' }}>
                <FiBriefcase size={24} />
              </StatIcon>
            </StatHeader>
          </StatCard>

          <StatCard
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.2 }}
          >
            <StatHeader>
              <div>
                <StatValue>{stats.totalResumes.toLocaleString()}</StatValue>
                <StatLabel>이력서</StatLabel>
              </div>
              <StatIcon style={{ background: '#ff6b35' }}>
                <FiDatabase size={24} />
              </StatIcon>
            </StatHeader>
          </StatCard>

          <StatCard
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.3 }}
          >
            <StatHeader>
              <div>
                <StatValue>{stats.totalCoverLetters.toLocaleString()}</StatValue>
                <StatLabel>자소서</StatLabel>
              </div>
              <StatIcon style={{ background: '#28a745' }}>
                <FiFileText size={24} />
              </StatIcon>
            </StatHeader>
          </StatCard>
        </StatsGrid>

        {/* 알림 메시지 */}
        {message && (
          <Alert type={message.type}>
            {message.type === 'success' ? <FiCheckCircle /> :
             message.type === 'error' ? <FiAlertCircle /> : <FiInfo />}
            {message.text}
          </Alert>
        )}

        {/* 진행 상황 */}
        {loading && (
          <Section>
            <SectionTitle>
              <FiRefreshCw className="spinning" />
              {currentOperation}
            </SectionTitle>
            <ProgressBar>
              <ProgressFill progress={progress} />
            </ProgressBar>
          </Section>
        )}

        {/* 탭 네비게이션 */}
        <TabContainer>
          <TabList>
            <Tab
              active={activeTab === 'help'}
              onClick={() => setActiveTab('help')}
            >
              <FiHelpCircle />
              등록 도움말
            </Tab>
            <Tab
              active={activeTab === 'schema'}
              onClick={() => setActiveTab('schema')}
            >
              <FiCode />
              DB 스키마
            </Tab>
            <Tab
              active={activeTab === 'generate'}
              onClick={() => setActiveTab('generate')}
            >
              <FiPlus />
              데이터 생성
            </Tab>
            <Tab
              active={activeTab === 'upload'}
              onClick={() => setActiveTab('upload')}
            >
              <FiUpload />
              JSON 업로드
            </Tab>
            <Tab
              active={activeTab === 'manage'}
              onClick={() => setActiveTab('manage')}
            >
              <FiTrash2 />
              데이터 관리
            </Tab>
          </TabList>
        </TabContainer>

        {/* 등록 도움말 탭 */}
        {activeTab === 'help' && (
          <Section>
            <SectionTitle>
              <FiHelpCircle />
              등록 도움말
            </SectionTitle>

            <InfoCard>
              <InfoTitle>
                <FiInfo />
                샘플 데이터 등록 가이드
              </InfoTitle>
              <InfoList>
                <InfoItem>
                  <span>자동 생성</span>
                  <span>AI가 자동으로 다양한 샘플 데이터를 생성합니다</span>
                </InfoItem>
                <InfoItem>
                  <span>JSON 업로드</span>
                  <span>JSON 파일을 업로드하여 데이터를 등록합니다</span>
                </InfoItem>
                <InfoItem>
                  <span>데이터 초기화</span>
                  <span>모든 데이터를 삭제하고 처음부터 시작합니다</span>
                </InfoItem>
                <InfoItem>
                  <span>실시간 통계</span>
                  <span>등록된 데이터의 통계를 실시간으로 확인합니다</span>
                </InfoItem>
              </InfoList>
            </InfoCard>

            <InfoCard>
              <InfoTitle>
                <FiFileText />
                지원되는 파일 형식
              </InfoTitle>
              <InfoList>
                <InfoItem>
                  <span>엑셀 파일</span>
                  <span>.xlsx, .xls</span>
                </InfoItem>
                <InfoItem>
                  <span>CSV 파일</span>
                  <span>.csv (UTF-8 인코딩)</span>
                </InfoItem>
                <InfoItem>
                  <span>최대 파일 크기</span>
                  <span>10MB</span>
                </InfoItem>
              </InfoList>
            </InfoCard>
          </Section>
        )}

        {/* DB 스키마 탭 */}
        {activeTab === 'schema' && (
          <Section>
            <SectionTitle>
              <FiCode />
              데이터베이스 스키마
            </SectionTitle>

            <SchemaContainer>
              <SchemaTitle>
                <FiTable />
                지원자 (applicants) 테이블
              </SchemaTitle>
              <SchemaTable>
                <thead>
                  <tr>
                    <SchemaTh>필드명</SchemaTh>
                    <SchemaTh>타입</SchemaTh>
                    <SchemaTh>필수</SchemaTh>
                    <SchemaTh>설명</SchemaTh>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <SchemaTd>name</SchemaTd>
                    <SchemaTd>String</SchemaTd>
                    <SchemaTd>✓</SchemaTd>
                    <SchemaTd>지원자 이름</SchemaTd>
                  </tr>
                  <tr>
                    <SchemaTd>email</SchemaTd>
                    <SchemaTd>String</SchemaTd>
                    <SchemaTd>✓</SchemaTd>
                    <SchemaTd>이메일 주소</SchemaTd>
                  </tr>
                  <tr>
                    <SchemaTd>phone</SchemaTd>
                    <SchemaTd>String</SchemaTd>
                    <SchemaTd>✓</SchemaTd>
                    <SchemaTd>전화번호</SchemaTd>
                  </tr>
                  <tr>
                    <SchemaTd>position</SchemaTd>
                    <SchemaTd>String</SchemaTd>
                    <SchemaTd>✓</SchemaTd>
                    <SchemaTd>지원 직무</SchemaTd>
                  </tr>
                  <tr>
                    <SchemaTd>department</SchemaTd>
                    <SchemaTd>String</SchemaTd>
                    <SchemaTd>✓</SchemaTd>
                    <SchemaTd>지원 부서</SchemaTd>
                  </tr>
                  <tr>
                    <SchemaTd>experience</SchemaTd>
                    <SchemaTd>String</SchemaTd>
                    <SchemaTd>✓</SchemaTd>
                    <SchemaTd>경력 (신입/1-3년/3-5년/5-7년/7년 이상)</SchemaTd>
                  </tr>
                  <tr>
                    <SchemaTd>skills</SchemaTd>
                    <SchemaTd>String</SchemaTd>
                    <SchemaTd>✓</SchemaTd>
                    <SchemaTd>기술 스킬 (쉼표로 구분)</SchemaTd>
                  </tr>
                  <tr>
                    <SchemaTd>growthBackground</SchemaTd>
                    <SchemaTd>String</SchemaTd>
                    <SchemaTd>✓</SchemaTd>
                    <SchemaTd>성장 배경</SchemaTd>
                  </tr>
                  <tr>
                    <SchemaTd>motivation</SchemaTd>
                    <SchemaTd>String</SchemaTd>
                    <SchemaTd>✓</SchemaTd>
                    <SchemaTd>지원 동기</SchemaTd>
                  </tr>
                  <tr>
                    <SchemaTd>careerHistory</SchemaTd>
                    <SchemaTd>String</SchemaTd>
                    <SchemaTd>✓</SchemaTd>
                    <SchemaTd>경력 사항</SchemaTd>
                  </tr>
                  <tr>
                    <SchemaTd>status</SchemaTd>
                    <SchemaTd>String</SchemaTd>
                    <SchemaTd>✓</SchemaTd>
                    <SchemaTd>상태 (pending/reviewing/interview_scheduled/passed/rejected)</SchemaTd>
                  </tr>
                  <tr>
                    <SchemaTd>analysisScore</SchemaTd>
                    <SchemaTd>Number</SchemaTd>
                    <SchemaTd>✓</SchemaTd>
                    <SchemaTd>분석 점수 (0-100)</SchemaTd>
                  </tr>
                  <tr>
                    <SchemaTd>analysisResult</SchemaTd>
                    <SchemaTd>String</SchemaTd>
                    <SchemaTd>✓</SchemaTd>
                    <SchemaTd>분석 결과</SchemaTd>
                  </tr>
                  <tr>
                    <SchemaTd>job_posting_id</SchemaTd>
                    <SchemaTd>ObjectId</SchemaTd>
                    <SchemaTd>✓</SchemaTd>
                    <SchemaTd>연결된 채용공고 ID</SchemaTd>
                  </tr>
                  <tr>
                    <SchemaTd>github_url</SchemaTd>
                    <SchemaTd>String</SchemaTd>
                    <SchemaTd>✗</SchemaTd>
                    <SchemaTd>GitHub 프로필 URL</SchemaTd>
                  </tr>
                  <tr>
                    <SchemaTd>linkedin_url</SchemaTd>
                    <SchemaTd>String</SchemaTd>
                    <SchemaTd>✗</SchemaTd>
                    <SchemaTd>LinkedIn 프로필 URL</SchemaTd>
                  </tr>
                  <tr>
                    <SchemaTd>portfolio_url</SchemaTd>
                    <SchemaTd>String</SchemaTd>
                    <SchemaTd>✗</SchemaTd>
                    <SchemaTd>포트폴리오 URL</SchemaTd>
                  </tr>
                  <tr>
                    <SchemaTd>resume_id</SchemaTd>
                    <SchemaTd>ObjectId</SchemaTd>
                    <SchemaTd>✗</SchemaTd>
                    <SchemaTd>연결된 이력서 ID</SchemaTd>
                  </tr>
                  <tr>
                    <SchemaTd>cover_letter_id</SchemaTd>
                    <SchemaTd>ObjectId</SchemaTd>
                    <SchemaTd>✗</SchemaTd>
                    <SchemaTd>연결된 자기소개서 ID</SchemaTd>
                  </tr>
                  <tr>
                    <SchemaTd>portfolio_id</SchemaTd>
                    <SchemaTd>ObjectId</SchemaTd>
                    <SchemaTd>✗</SchemaTd>
                    <SchemaTd>연결된 포트폴리오 ID</SchemaTd>
                  </tr>
                  <tr>
                    <SchemaTd>ranks</SchemaTd>
                    <SchemaTd>Object</SchemaTd>
                    <SchemaTd>✗</SchemaTd>
                    <SchemaTd>랭킹 정보 (resume, coverLetter, portfolio, total)</SchemaTd>
                  </tr>
                  <tr>
                    <SchemaTd>created_at</SchemaTd>
                    <SchemaTd>Date</SchemaTd>
                    <SchemaTd>✓</SchemaTd>
                    <SchemaTd>생성일시</SchemaTd>
                  </tr>
                  <tr>
                    <SchemaTd>updated_at</SchemaTd>
                    <SchemaTd>Date</SchemaTd>
                    <SchemaTd>✓</SchemaTd>
                    <SchemaTd>수정일시</SchemaTd>
                  </tr>
                </tbody>
              </SchemaTable>
            </SchemaContainer>

            <SchemaContainer>
              <SchemaTitle>
                <FiTable />
                채용공고 (job_postings) 테이블
              </SchemaTitle>
              <SchemaTable>
                <thead>
                  <tr>
                    <SchemaTh>필드명</SchemaTh>
                    <SchemaTh>타입</SchemaTh>
                    <SchemaTh>필수</SchemaTh>
                    <SchemaTh>설명</SchemaTh>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <SchemaTd>title</SchemaTd>
                    <SchemaTd>String</SchemaTd>
                    <SchemaTd>✓</SchemaTd>
                    <SchemaTd>채용공고 제목</SchemaTd>
                  </tr>
                  <tr>
                    <SchemaTd>company</SchemaTd>
                    <SchemaTd>String</SchemaTd>
                    <SchemaTd>✓</SchemaTd>
                    <SchemaTd>회사명</SchemaTd>
                  </tr>
                  <tr>
                    <SchemaTd>location</SchemaTd>
                    <SchemaTd>String</SchemaTd>
                    <SchemaTd>✓</SchemaTd>
                    <SchemaTd>근무지</SchemaTd>
                  </tr>
                  <tr>
                    <SchemaTd>department</SchemaTd>
                    <SchemaTd>String</SchemaTd>
                    <SchemaTd>✓</SchemaTd>
                    <SchemaTd>부서</SchemaTd>
                  </tr>
                  <tr>
                    <SchemaTd>position</SchemaTd>
                    <SchemaTd>String</SchemaTd>
                    <SchemaTd>✓</SchemaTd>
                    <SchemaTd>직무</SchemaTd>
                  </tr>
                  <tr>
                    <SchemaTd>salary</SchemaTd>
                    <SchemaTd>String</SchemaTd>
                    <SchemaTd>✓</SchemaTd>
                    <SchemaTd>급여</SchemaTd>
                  </tr>
                  <tr>
                    <SchemaTd>experience</SchemaTd>
                    <SchemaTd>String</SchemaTd>
                    <SchemaTd>✓</SchemaTd>
                    <SchemaTd>요구 경력</SchemaTd>
                  </tr>
                  <tr>
                    <SchemaTd>description</SchemaTd>
                    <SchemaTd>String</SchemaTd>
                    <SchemaTd>✓</SchemaTd>
                    <SchemaTd>업무 설명</SchemaTd>
                  </tr>
                  <tr>
                    <SchemaTd>requirements</SchemaTd>
                    <SchemaTd>String</SchemaTd>
                    <SchemaTd>✓</SchemaTd>
                    <SchemaTd>자격 요건</SchemaTd>
                  </tr>
                  <tr>
                    <SchemaTd>status</SchemaTd>
                    <SchemaTd>String</SchemaTd>
                    <SchemaTd>✓</SchemaTd>
                    <SchemaTd>상태 (draft/published/closed)</SchemaTd>
                  </tr>
                  <tr>
                    <SchemaTd>type</SchemaTd>
                    <SchemaTd>String</SchemaTd>
                    <SchemaTd>✓</SchemaTd>
                    <SchemaTd>고용 형태 (full-time/part-time/contract)</SchemaTd>
                  </tr>
                  <tr>
                    <SchemaTd>education</SchemaTd>
                    <SchemaTd>String</SchemaTd>
                    <SchemaTd>✓</SchemaTd>
                    <SchemaTd>학력 요건</SchemaTd>
                  </tr>
                  <tr>
                    <SchemaTd>benefits</SchemaTd>
                    <SchemaTd>String</SchemaTd>
                    <SchemaTd>✓</SchemaTd>
                    <SchemaTd>복리후생</SchemaTd>
                  </tr>
                  <tr>
                    <SchemaTd>deadline</SchemaTd>
                    <SchemaTd>String</SchemaTd>
                    <SchemaTd>✓</SchemaTd>
                    <SchemaTd>지원 마감일</SchemaTd>
                  </tr>
                  <tr>
                    <SchemaTd>applicants</SchemaTd>
                    <SchemaTd>Number</SchemaTd>
                    <SchemaTd>✓</SchemaTd>
                    <SchemaTd>지원자 수</SchemaTd>
                  </tr>
                  <tr>
                    <SchemaTd>views</SchemaTd>
                    <SchemaTd>Number</SchemaTd>
                    <SchemaTd>✓</SchemaTd>
                    <SchemaTd>조회수</SchemaTd>
                  </tr>
                  <tr>
                    <SchemaTd>bookmarks</SchemaTd>
                    <SchemaTd>Number</SchemaTd>
                    <SchemaTd>✓</SchemaTd>
                    <SchemaTd>북마크 수</SchemaTd>
                  </tr>
                  <tr>
                    <SchemaTd>shares</SchemaTd>
                    <SchemaTd>Number</SchemaTd>
                    <SchemaTd>✓</SchemaTd>
                    <SchemaTd>공유 수</SchemaTd>
                  </tr>
                  <tr>
                    <SchemaTd>created_at</SchemaTd>
                    <SchemaTd>Date</SchemaTd>
                    <SchemaTd>✓</SchemaTd>
                    <SchemaTd>생성일시</SchemaTd>
                  </tr>
                  <tr>
                    <SchemaTd>updated_at</SchemaTd>
                    <SchemaTd>Date</SchemaTd>
                    <SchemaTd>✓</SchemaTd>
                    <SchemaTd>수정일시</SchemaTd>
                  </tr>
                </tbody>
              </SchemaTable>
            </SchemaContainer>

            <SchemaContainer>
              <SchemaTitle>
                <FiFileText />
                자소서 (cover_letters) 테이블
              </SchemaTitle>
              <SchemaTable>
                <thead>
                  <tr>
                    <SchemaTh>필드명</SchemaTh>
                    <SchemaTh>타입</SchemaTh>
                    <SchemaTh>필수</SchemaTh>
                    <SchemaTh>설명</SchemaTh>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <SchemaTd>applicant_id</SchemaTd>
                    <SchemaTd>ObjectId</SchemaTd>
                    <SchemaTd>✓</SchemaTd>
                    <SchemaTd>연결된 지원자 ID</SchemaTd>
                  </tr>
                  <tr>
                    <SchemaTd>content</SchemaTd>
                    <SchemaTd>String</SchemaTd>
                    <SchemaTd>✓</SchemaTd>
                    <SchemaTd>자소서 전체 내용</SchemaTd>
                  </tr>
                  <tr>
                    <SchemaTd>motivation</SchemaTd>
                    <SchemaTd>String</SchemaTd>
                    <SchemaTd>✓</SchemaTd>
                    <SchemaTd>지원 동기</SchemaTd>
                  </tr>
                  <tr>
                    <SchemaTd>career_goals</SchemaTd>
                    <SchemaTd>String</SchemaTd>
                    <SchemaTd>✓</SchemaTd>
                    <SchemaTd>경력 목표</SchemaTd>
                  </tr>
                  <tr>
                    <SchemaTd>strengths</SchemaTd>
                    <SchemaTd>String</SchemaTd>
                    <SchemaTd>✓</SchemaTd>
                    <SchemaTd>강점 및 역량</SchemaTd>
                  </tr>
                  <tr>
                    <SchemaTd>experience</SchemaTd>
                    <SchemaTd>String</SchemaTd>
                    <SchemaTd>✓</SchemaTd>
                    <SchemaTd>관련 경험</SchemaTd>
                  </tr>
                  <tr>
                    <SchemaTd>achievements</SchemaTd>
                    <SchemaTd>String</SchemaTd>
                    <SchemaTd>✓</SchemaTd>
                    <SchemaTd>주요 성과</SchemaTd>
                  </tr>
                  <tr>
                    <SchemaTd>skills</SchemaTd>
                    <SchemaTd>String</SchemaTd>
                    <SchemaTd>✓</SchemaTd>
                    <SchemaTd>보유 기술</SchemaTd>
                  </tr>
                  <tr>
                    <SchemaTd>projects</SchemaTd>
                    <SchemaTd>String</SchemaTd>
                    <SchemaTd>✓</SchemaTd>
                    <SchemaTd>프로젝트 경험</SchemaTd>
                  </tr>
                  <tr>
                    <SchemaTd>education</SchemaTd>
                    <SchemaTd>String</SchemaTd>
                    <SchemaTd>✓</SchemaTd>
                    <SchemaTd>학력 사항</SchemaTd>
                  </tr>
                  <tr>
                    <SchemaTd>certifications</SchemaTd>
                    <SchemaTd>String</SchemaTd>
                    <SchemaTd>✓</SchemaTd>
                    <SchemaTd>자격증</SchemaTd>
                  </tr>
                  <tr>
                    <SchemaTd>languages</SchemaTd>
                    <SchemaTd>String</SchemaTd>
                    <SchemaTd>✓</SchemaTd>
                    <SchemaTd>언어 능력</SchemaTd>
                  </tr>
                  <tr>
                    <SchemaTd>personal_statement</SchemaTd>
                    <SchemaTd>String</SchemaTd>
                    <SchemaTd>✓</SchemaTd>
                    <SchemaTd>자기소개</SchemaTd>
                  </tr>
                  <tr>
                    <SchemaTd>future_plans</SchemaTd>
                    <SchemaTd>String</SchemaTd>
                    <SchemaTd>✓</SchemaTd>
                    <SchemaTd>향후 계획</SchemaTd>
                  </tr>
                  <tr>
                    <SchemaTd>filename</SchemaTd>
                    <SchemaTd>String</SchemaTd>
                    <SchemaTd>✓</SchemaTd>
                    <SchemaTd>파일명</SchemaTd>
                  </tr>
                  <tr>
                    <SchemaTd>file_size</SchemaTd>
                    <SchemaTd>Number</SchemaTd>
                    <SchemaTd>✓</SchemaTd>
                    <SchemaTd>파일 크기 (bytes)</SchemaTd>
                  </tr>
                  <tr>
                    <SchemaTd>extracted_text</SchemaTd>
                    <SchemaTd>String</SchemaTd>
                    <SchemaTd>✓</SchemaTd>
                    <SchemaTd>추출된 텍스트</SchemaTd>
                  </tr>
                  <tr>
                    <SchemaTd>status</SchemaTd>
                    <SchemaTd>String</SchemaTd>
                    <SchemaTd>✓</SchemaTd>
                    <SchemaTd>상태 (submitted/reviewed/approved/rejected)</SchemaTd>
                  </tr>
                  <tr>
                    <SchemaTd>created_at</SchemaTd>
                    <SchemaTd>Date</SchemaTd>
                    <SchemaTd>✓</SchemaTd>
                    <SchemaTd>생성일시</SchemaTd>
                  </tr>
                  <tr>
                    <SchemaTd>updated_at</SchemaTd>
                    <SchemaTd>Date</SchemaTd>
                    <SchemaTd>✓</SchemaTd>
                    <SchemaTd>수정일시</SchemaTd>
                  </tr>
                </tbody>
              </SchemaTable>
            </SchemaContainer>
          </Section>
        )}

        {/* 데이터 생성 탭 */}
        {activeTab === 'generate' && (
          <Section>
            <SectionTitle>
              <FiPlus />
              샘플 데이터 생성
            </SectionTitle>

            <InfoCard>
              <InfoTitle>
                <FiInfo />
                샘플 데이터 생성 가이드
              </InfoTitle>
              <InfoList>
                <InfoItem>
                  <span>채용공고 우선 생성</span>
                  <span>지원자는 반드시 채용공고에 소속되어야 합니다</span>
                </InfoItem>
                <InfoItem>
                  <span>지원자 데이터</span>
                  <span>이름, 이메일, 전화번호, 직무, 경력 등 포함</span>
                </InfoItem>
                <InfoItem>
                  <span>채용공고 데이터</span>
                  <span>회사명, 직무, 경력요건, 급여 등 포함</span>
                </InfoItem>
                <InfoItem>
                  <span>데이터 초기화</span>
                  <span>모든 데이터를 삭제하고 처음부터 시작</span>
                </InfoItem>
              </InfoList>
            </InfoCard>

            {/* 현재 채용공고 상태 표시 */}
            <InfoCard>
              <InfoTitle>
                <FiBriefcase />
                현재 채용공고 현황
              </InfoTitle>
              <InfoList>
                <InfoItem>
                  <span>등록된 채용공고</span>
                  <span>{jobPostings.length}개</span>
                </InfoItem>
                <InfoItem>
                  <span>지원자 생성 가능</span>
                  <span>{jobPostings.length > 0 ? '가능' : '불가능 (채용공고 필요)'}</span>
                </InfoItem>
              </InfoList>
            </InfoCard>

            {/* 현재 지원자 및 자소서 상태 표시 */}
            <InfoCard>
              <InfoTitle>
                <FiUsers />
                현재 지원자 및 자소서 현황
              </InfoTitle>
              <InfoList>
                <InfoItem>
                  <span>등록된 지원자</span>
                  <span>{applicants.length}명</span>
                </InfoItem>
                <InfoItem>
                  <span>자소서 생성 대상</span>
                  <span>{applicants.length > 0 ? '자소서가 없는 지원자들' : '불가능 (지원자 필요)'}</span>
                </InfoItem>
              </InfoList>
            </InfoCard>

            {/* 개별 지원자 생성 폼 */}
            <FormContainer>
              <FormTitle>
                <FiUser />
                개별 지원자 생성
              </FormTitle>
              <FormDescription>
                테스트용 개별 지원자를 생성합니다. 이름과 이메일은 필수 입력 항목이며, 나머지 정보는 자동으로 생성됩니다.
              </FormDescription>

              <FormGrid>
                <FormField>
                  <FormLabel>이름 *</FormLabel>
                  <FormInput
                    type="text"
                    placeholder="예: 홍길동"
                    value={singleApplicantForm.name}
                    onChange={(e) => setSingleApplicantForm(prev => ({
                      ...prev,
                      name: e.target.value
                    }))}
                  />
                </FormField>

                <FormField>
                  <FormLabel>이메일 주소 *</FormLabel>
                  <FormInput
                    type="email"
                    placeholder="예: hong@example.com"
                    value={singleApplicantForm.email}
                    onChange={(e) => setSingleApplicantForm(prev => ({
                      ...prev,
                      email: e.target.value
                    }))}
                  />
                </FormField>
              </FormGrid>

              <FormField>
                <FormLabel>GitHub 주소 (선택사항)</FormLabel>
                <FormInput
                  type="url"
                  placeholder="예: https://github.com/username"
                  value={singleApplicantForm.github_url}
                  onChange={(e) => setSingleApplicantForm(prev => ({
                    ...prev,
                    github_url: e.target.value
                  }))}
                />
                <FormDescription>
                  입력하지 않으면 자동으로 생성됩니다.
                </FormDescription>
              </FormField>

              <Button
                onClick={createSingleApplicant}
                disabled={loading || !singleApplicantForm.name || !singleApplicantForm.email}
                variant="primary"
                style={{ marginTop: '16px' }}
              >
                <FiUser />
                특정 지원자 생성
              </Button>
            </FormContainer>

            <ButtonGroup>
              {/* 채용공고 생성 버튼들을 먼저 배치 */}
              <Button
                onClick={() => generateSampleJobPostings(5)}
                disabled={loading}
                variant="success"
              >
                <FiBriefcase />
                5개 채용공고 생성
              </Button>

              <Button
                onClick={() => generateSampleJobPostings(10)}
                disabled={loading}
                variant="success"
              >
                <FiBriefcase />
                10개 채용공고 생성
              </Button>

              {/* 구분선 */}
              <div style={{ width: '100%', height: '1px', background: '#dee2e6', margin: '16px 0' }} />

              {/* 지원자 생성 버튼들 */}
              <Button
                onClick={() => generateSampleApplicants(50)}
                disabled={loading || jobPostings.length === 0}
                variant={jobPostings.length === 0 ? 'danger' : 'success'}
              >
                <FiUsers />
                50명 지원자 생성
                {jobPostings.length === 0 && ' (채용공고 필요)'}
              </Button>

              <Button
                onClick={() => generateSampleApplicants(100)}
                disabled={loading || jobPostings.length === 0}
                variant={jobPostings.length === 0 ? 'danger' : 'success'}
              >
                <FiUsers />
                100명 지원자 생성
                {jobPostings.length === 0 && ' (채용공고 필요)'}
              </Button>

              {/* 구분선 */}
              <div style={{ width: '100%', height: '1px', background: '#dee2e6', margin: '16px 0' }} />

              {/* 자소서 생성 버튼 */}
              <Button
                onClick={generateSampleCoverLetters}
                disabled={loading || applicants.length === 0}
                variant={applicants.length === 0 ? 'danger' : 'success'}
              >
                <FiFileText />
                자소서가 없는 지원자들을 위한 자소서 생성
                {applicants.length === 0 && ' (지원자 필요)'}
              </Button>
            </ButtonGroup>
          </Section>
        )}

        {/* JSON 업로드 탭 */}
        {activeTab === 'upload' && (
          <Section>
            <SectionTitle>
              <FiUpload />
              JSON 데이터 업로드
            </SectionTitle>

            <InfoCard>
              <InfoTitle>
                <FiInfo />
                JSON 데이터 업로드 가이드
              </InfoTitle>
              <InfoList>
                <InfoItem>
                  <span>지원 형식</span>
                  <span>.json</span>
                </InfoItem>
                <InfoItem>
                  <span>최대 크기</span>
                  <span>10MB</span>
                </InfoItem>
                <InfoItem>
                  <span>인코딩</span>
                  <span>UTF-8</span>
                </InfoItem>
                <InfoItem>
                  <span>데이터 구조</span>
                  <span>applicants, job_postings 배열</span>
                </InfoItem>
              </InfoList>
            </InfoCard>

            <FileUploadArea
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
              onClick={() => document.getElementById('json-file-input').click()}
            >
              <UploadIcon>
                <FiUpload size={48} />
              </UploadIcon>
              <UploadText>
                {uploadedFile ? uploadedFile.name : '클릭하거나 JSON 파일을 드래그하여 업로드하세요'}
              </UploadText>
              <UploadSubtext>
                지원 형식: .json (최대 10MB)
              </UploadSubtext>
              <FileInput
                id="json-file-input"
                type="file"
                accept=".json"
                onChange={handleFileSelect}
              />
            </FileUploadArea>

            <ButtonGroup>
              <Button
                onClick={() => document.getElementById('json-file-input').click()}
                disabled={loading}
              >
                <FiUpload />
                JSON 파일 선택
              </Button>

              <Button
                onClick={downloadJsonTemplate}
                disabled={loading}
              >
                <FiDownload />
                JSON 템플릿 다운로드
              </Button>
            </ButtonGroup>

            {/* 업로드 완료 후 다음 단계 안내 */}
            {message && message.type === 'success' && message.text.includes('업로드되었습니다') && (
              <InfoCard style={{ marginTop: '24px', background: '#d4edda', border: '1px solid #c3e6cb' }}>
                <InfoTitle style={{ color: '#155724' }}>
                  <FiCheckCircle />
                  업로드 완료! 다음 단계를 진행하세요
                </InfoTitle>
                <InfoList>
                  <InfoItem>
                    <span>✅ JSON 데이터가 성공적으로 등록되었습니다</span>
                    <span></span>
                  </InfoItem>
                  <InfoItem>
                    <span>🎯 지원자들에게 기존 채용공고가 랜덤하게 할당되었습니다</span>
                    <span></span>
                  </InfoItem>
                  <InfoItem>
                    <span>🔍 데이터가 벡터 데이터베이스에도 저장되어 검색 기능을 사용할 수 있습니다</span>
                    <span></span>
                  </InfoItem>
                  <InfoItem>
                    <span>📊 현재 데이터 통계를 확인하세요</span>
                    <span></span>
                  </InfoItem>
                  <InfoItem>
                    <span>🚀 추가 데이터를 생성하거나 관리하세요</span>
                    <span></span>
                  </InfoItem>
                </InfoList>
                <ButtonGroup style={{ marginTop: '16px' }}>
                  <Button
                    onClick={() => setActiveTab('generate')}
                    variant="success"
                  >
                    <FiPlus />
                    추가 데이터 생성하기
                  </Button>
                  <Button
                    onClick={() => setActiveTab('help')}
                    variant="primary"
                  >
                    <FiInfo />
                    도움말 보기
                  </Button>
                </ButtonGroup>
              </InfoCard>
            )}
          </Section>
        )}

        {/* 데이터 관리 탭 */}
        {activeTab === 'manage' && (
          <Section>
            <SectionTitle>
              <FiTrash2 />
              데이터 관리
            </SectionTitle>

            <ButtonGroup>
              <Button
                onClick={resetAllData}
                disabled={loading}
                variant="danger"
              >
                <FiTrash2 />
                전체 데이터 초기화
              </Button>
            </ButtonGroup>
          </Section>
        )}
      </Content>

      <style>{`
        .spinning {
          animation: spin 1s linear infinite;
        }

        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }

        @keyframes slideInRight {
          from {
            transform: translateX(100%);
            opacity: 0;
          }
          to {
            transform: translateX(0);
            opacity: 1;
          }
        }
      `}</style>
    </Container>
  );
};

export default SampleDataManagement;
