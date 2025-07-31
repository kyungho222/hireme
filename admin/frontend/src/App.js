import React from 'react';
import { Routes, Route, useLocation } from 'react-router-dom';
import Layout from './components/Layout/Layout';
import Dashboard from './pages/Dashboard/Dashboard';
import JobPostingRegistration from './pages/JobPostingRegistration/JobPostingRegistration';
import ResumeManagement from './pages/ResumeManagement/ResumeManagement';
import InterviewManagement from './pages/InterviewManagement/InterviewManagement';
import PortfolioAnalysis from './pages/PortfolioAnalysis/PortfolioAnalysis';
import CoverLetterValidation from './pages/CoverLetterValidation/CoverLetterValidation';
import TalentRecommendation from './pages/TalentRecommendation/TalentRecommendation';
import UserManagement from './pages/UserManagement/UserManagement';
import Settings from './pages/Settings/Settings';
import FloatingChatbot from './components/FloatingChatbot';

function App() {
  const location = useLocation();
  const currentPage = location.pathname.replace('/', '') || 'dashboard';

  const handlePageAction = (action) => {
    console.log('페이지 액션 실행:', action);
    
    // job-posting 페이지 액션 처리
    if (action === 'openRegistrationMethod') {
      // RegistrationMethodModal 열기
      const event = new CustomEvent('openRegistrationMethod');
      window.dispatchEvent(event);
    } else if (action === 'openTextRegistration') {
      // TextBasedRegistration 열기
      const event = new CustomEvent('openTextRegistration');
      window.dispatchEvent(event);
    } else if (action === 'openImageRegistration') {
      // ImageBasedRegistration 열기
      const event = new CustomEvent('openImageRegistration');
      window.dispatchEvent(event);
    } else if (action === 'openTemplateModal') {
      // TemplateModal 열기
      const event = new CustomEvent('openTemplateModal');
      window.dispatchEvent(event);
    } else if (action === 'openOrganizationModal') {
      // OrganizationModal 열기
      const event = new CustomEvent('openOrganizationModal');
      window.dispatchEvent(event);
    }
  };

  return (
    <>
      <Layout>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/job-posting" element={<JobPostingRegistration />} />
          <Route path="/resume" element={<ResumeManagement />} />
          <Route path="/interview" element={<InterviewManagement />} />
          <Route path="/portfolio" element={<PortfolioAnalysis />} />
          <Route path="/cover-letter" element={<CoverLetterValidation />} />
          <Route path="/talent" element={<TalentRecommendation />} />
          <Route path="/users" element={<UserManagement />} />
          <Route path="/settings" element={<Settings />} />
        </Routes>
      </Layout>
      
      {/* 챗봇 컴포넌트 */}
      <FloatingChatbot 
        page={currentPage}
        onFieldUpdate={(field, value) => {
          console.log('챗봇 필드 업데이트:', field, value);
        }}
        onComplete={() => {
          console.log('챗봇 완료');
        }}
        onPageAction={handlePageAction}
      />
    </>
  );
}

export default App; 