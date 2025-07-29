import React, { useState } from 'react';
import styled from 'styled-components';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  FiX, 
  FiArrowLeft, 
  FiArrowRight,
  FiCheck,
  FiImage,
  FiDownload,
  FiEye,
  FiRefreshCw
} from 'react-icons/fi';

const Overlay = styled(motion.div)`
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
`;

const Modal = styled(motion.div)`
  background: white;
  border-radius: 16px;
  max-width: 1000px;
  width: 100%;
  max-height: 90vh;
  overflow-y: auto;
  position: relative;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
`;

const Header = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24px 32px;
  border-bottom: 1px solid var(--border-color);
  position: sticky;
  top: 0;
  background: white;
  z-index: 10;
`;

const Title = styled.h2`
  font-size: 24px;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0;
`;

const CloseButton = styled.button`
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: var(--text-secondary);
  padding: 8px;
  border-radius: 50%;
  transition: all 0.3s ease;

  &:hover {
    background: var(--background-secondary);
    color: var(--text-primary);
  }
`;

const Content = styled.div`
  padding: 32px;
`;

const StepIndicator = styled.div`
  display: flex;
  justify-content: center;
  margin-bottom: 32px;
  gap: 40px;
`;

const Step = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
`;

const StepNumber = styled.div`
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  font-weight: 600;
  color: white;
  background: ${props => 
    props.active ? 'linear-gradient(135deg, #f093fb, #f5576c)' : 
    props.completed ? 'var(--primary-color)' : 'var(--border-color)'
  };
`;

const StepLabel = styled.span`
  font-size: 14px;
  color: ${props => 
    props.active ? 'var(--primary-color)' : 
    props.completed ? 'var(--text-primary)' : 'var(--text-secondary)'
  };
  font-weight: ${props => props.active || props.completed ? '600' : '400'};
`;

const FormSection = styled.div`
  margin-bottom: 32px;
`;

const SectionTitle = styled.h3`
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
  gap: 20px;
  margin-bottom: 24px;

  @media (max-width: 768px) {
    grid-template-columns: 1fr;
  }
`;

const FormGroup = styled.div`
  display: flex;
  flex-direction: column;
  gap: 8px;
`;

const Label = styled.label`
  font-weight: 600;
  color: var(--text-primary);
  font-size: 14px;
`;

const Input = styled.input`
  padding: 12px 16px;
  border: 2px solid var(--border-color);
  border-radius: 8px;
  font-size: 14px;
  transition: all 0.3s ease;

  &:focus {
    outline: none;
    border-color: var(--primary-color);
    box-shadow: 0 0 0 3px rgba(0, 200, 81, 0.1);
  }
`;

const TextArea = styled.textarea`
  padding: 12px 16px;
  border: 2px solid var(--border-color);
  border-radius: 8px;
  font-size: 14px;
  min-height: 120px;
  resize: vertical;
  transition: all 0.3s ease;

  &:focus {
    outline: none;
    border-color: var(--primary-color);
    box-shadow: 0 0 0 3px rgba(0, 200, 81, 0.1);
  }
`;

const Select = styled.select`
  padding: 12px 16px;
  border: 2px solid var(--border-color);
  border-radius: 8px;
  font-size: 14px;
  background: white;
  transition: all 0.3s ease;

  &:focus {
    outline: none;
    border-color: var(--primary-color);
    box-shadow: 0 0 0 3px rgba(0, 200, 81, 0.1);
  }
`;

const ButtonGroup = styled.div`
  display: flex;
  gap: 12px;
  justify-content: space-between;
  margin-top: 32px;
  padding-top: 24px;
  border-top: 1px solid var(--border-color);
`;

const Button = styled.button`
  padding: 12px 24px;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  border: none;
  display: flex;
  align-items: center;
  gap: 8px;

  &.primary {
    background: linear-gradient(135deg, #f093fb, #f5576c);
    color: white;

    &:hover {
      transform: translateY(-2px);
      box-shadow: 0 8px 25px rgba(240, 147, 251, 0.3);
    }
  }

  &.secondary {
    background: white;
    color: var(--text-secondary);
    border: 2px solid var(--border-color);

    &:hover {
      background: var(--background-secondary);
      border-color: var(--text-secondary);
    }
  }

  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
    transform: none;
    box-shadow: none;
  }
`;

const ImageGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
  margin-top: 24px;
`;

const ImageCard = styled(motion.div)`
  border: 2px solid var(--border-color);
  border-radius: 12px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.3s ease;

  &:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 30px rgba(0, 0, 0, 0.15);
  }

  &.selected {
    border-color: var(--primary-color);
    box-shadow: 0 0 0 3px rgba(0, 200, 81, 0.1);
  }
`;

const ImagePlaceholder = styled.div`
  width: 100%;
  height: 200px;
  background: linear-gradient(135deg, #f093fb, #f5576c);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 48px;
`;

const ImageInfo = styled.div`
  padding: 16px;
  background: white;
`;

const ImageTitle = styled.div`
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 4px;
`;

const ImageDescription = styled.div`
  font-size: 12px;
  color: var(--text-secondary);
`;

const LoadingSection = styled.div`
  text-align: center;
  padding: 60px 20px;
`;

const LoadingSpinner = styled.div`
  width: 60px;
  height: 60px;
  border: 4px solid var(--border-color);
  border-top: 4px solid var(--primary-color);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 20px;

  @keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
  }
`;

const LoadingText = styled.div`
  font-size: 16px;
  color: var(--text-secondary);
  margin-bottom: 8px;
`;

const LoadingSubtext = styled.div`
  font-size: 14px;
  color: var(--text-light);
`;

const AISuggestion = styled.div`
  background: rgba(240, 147, 251, 0.1);
  border: 1px solid rgba(240, 147, 251, 0.2);
  border-radius: 8px;
  padding: 16px;
  margin-top: 12px;
`;

const AISuggestionTitle = styled.div`
  font-weight: 600;
  color: #f093fb;
  margin-bottom: 8px;
  display: flex;
  align-items: center;
  gap: 8px;
`;

const AISuggestionText = styled.div`
  font-size: 14px;
  color: var(--text-secondary);
  line-height: 1.5;
`;

const ImageBasedRegistration = ({ 
  isOpen, 
  onClose, 
  onComplete 
}) => {
  const [currentStep, setCurrentStep] = useState(1);
  const [isGenerating, setIsGenerating] = useState(false);
  const [selectedImage, setSelectedImage] = useState(null);
  const [formData, setFormData] = useState({
    title: '',
    department: '',
    experience: '',
    mainDuties: '',
    requirements: '',
    benefits: '',
    workHours: '',
    location: '',
    salary: '',
    deadline: '',
    contactEmail: ''
  });

  const [generatedImages, setGeneratedImages] = useState([]);

  const steps = [
    { number: 1, label: '정보 입력', icon: FiImage },
    { number: 2, label: '이미지 생성', icon: FiImage },
    { number: 3, label: '이미지 선택', icon: FiImage }
  ];

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleGenerateImages = async () => {
    setIsGenerating(true);
    
    // AI 이미지 생성 시뮬레이션 (실제로는 API 호출)
    setTimeout(() => {
      const mockImages = [
        {
          id: 1,
          title: '모던 스타일',
          description: '깔끔하고 현대적인 디자인',
          url: 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMzAwIiBoZWlnaHQ9IjIwMCIgdmlld0JveD0iMCAwIDMwMCAyMDAiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxyZWN0IHdpZHRoPSIzMDAiIGhlaWdodD0iMjAwIiBmaWxsPSJ1cmwoI2dyYWRpZW50KSIvPgo8ZGVmcz4KPGxpbmVhckdyYWRpZW50IGlkPSJncmFkaWVudCIgeDE9IjAiIHkxPSIwIiB4Mj0iMzAwIiB5Mj0iMjAwIiBncmFkaWVudFVuaXRzPSJ1c2VyU3BhY2VPblVzZSI+CjxzdG9wIG9mZnNldD0iMCUiIHN0eWxlPSJzdG9wLWNvbG9yOiNmMDkzZmI7c3RvcC1vcGFjaXR5OjEiLz4KPHN0b3Agb2Zmc2V0PSIxMDAlIiBzdHlsZT0ic3RvcC1jb2xvcjojZjU1NzZjO3N0b3Atb3BhY2l0eToxIi8+CjwvbGluZWFyR3JhZGllbnQ+CjwvZGVmcz4KPC9zdmc+'
        },
        {
          id: 2,
          title: '비즈니스 스타일',
          description: '전문적이고 신뢰감 있는 디자인',
          url: 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMzAwIiBoZWlnaHQ9IjIwMCIgdmlld0JveD0iMCAwIDMwMCAyMDAiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxyZWN0IHdpZHRoPSIzMDAiIGhlaWdodD0iMjAwIiBmaWxsPSJ1cmwoI2dyYWRpZW50KSIvPgo8ZGVmcz4KPGxpbmVhckdyYWRpZW50IGlkPSJncmFkaWVudCIgeDE9IjAiIHkxPSIwIiB4Mj0iMzAwIiB5Mj0iMjAwIiBncmFkaWVudFVuaXRzPSJ1c2VyU3BhY2VPblVzZSI+CjxzdG9wIG9mZnNldD0iMCUiIHN0eWxlPSJzdG9wLWNvbG9yOiM2NjdlZWE7c3RvcC1vcGFjaXR5OjEiLz4KPHN0b3Agb2Zmc2V0PSIxMDAlIiBzdHlsZT0ic3RvcC1jb2xvcjojNzY0YmEyO3N0b3Atb3BhY2l0eToxIi8+CjwvbGluZWFyR3JhZGllbnQ+CjwvZGVmcz4KPC9zdmc+'
        },
        {
          id: 3,
          title: '크리에이티브 스타일',
          description: '창의적이고 독특한 디자인',
          url: 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMzAwIiBoZWlnaHQ9IjIwMCIgdmlld0JveD0iMCAwIDMwMCAyMDAiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxyZWN0IHdpZHRoPSIzMDAiIGhlaWdodD0iMjAwIiBmaWxsPSJ1cmwoI2dyYWRpZW50KSIvPgo8ZGVmcz4KPGxpbmVhckdyYWRpZW50IGlkPSJncmFkaWVudCIgeDE9IjAiIHkxPSIwIiB4Mj0iMzAwIiB5Mj0iMjAwIiBncmFkaWVudFVuaXRzPSJ1c2VyU3BhY2VPblVzZSI+CjxzdG9wIG9mZnNldD0iMCUiIHN0eWxlPSJzdG9wLWNvbG9yOiMwMGM4NTE7c3RvcC1vcGFjaXR5OjEiLz4KPHN0b3Agb2Zmc2V0PSIxMDAlIiBzdHlsZT0ic3RvcC1jb2xvcjojMDBhODQ0O3N0b3Atb3BhY2l0eToxIi8+CjwvbGluZWFyR3JhZGllbnQ+CjwvZGVmcz4KPC9zdmc+'
        }
      ];
      setGeneratedImages(mockImages);
      setIsGenerating(false);
      setCurrentStep(3);
    }, 3000);
  };

  const handleImageSelect = (image) => {
    setSelectedImage(image);
  };

  const handleComplete = () => {
    if (selectedImage && onComplete) {
      onComplete({ ...formData, selectedImage });
    }
  };

  const renderStep1 = () => (
    <FormSection>
      <SectionTitle>
        <FiImage size={18} />
        채용공고 정보 입력
      </SectionTitle>
      <FormGrid>
        <FormGroup>
          <Label>공고 제목 *</Label>
          <Input
            type="text"
            name="title"
            value={formData.title}
            onChange={handleInputChange}
            placeholder="예: 프론트엔드 개발자 채용"
            required
          />
        </FormGroup>
        <FormGroup>
          <Label>부서</Label>
          <Select name="department" value={formData.department} onChange={handleInputChange}>
            <option value="">부서 선택</option>
            <option value="개발">개발</option>
            <option value="디자인">디자인</option>
            <option value="마케팅">마케팅</option>
            <option value="영업">영업</option>
          </Select>
        </FormGroup>
        <FormGroup>
          <Label>경력 구분</Label>
          <Select name="experience" value={formData.experience} onChange={handleInputChange}>
            <option value="">경력 선택</option>
            <option value="신입">신입</option>
            <option value="경력">경력</option>
          </Select>
        </FormGroup>
        <FormGroup>
          <Label>근무지</Label>
          <div style={{ display: 'flex', gap: '8px' }}>
            <Select 
              name="locationCity" 
              value={formData.locationCity || ''} 
              onChange={(e) => {
                setFormData(prev => ({ 
                  ...prev, 
                  locationCity: e.target.value,
                  locationDistrict: '' // 시가 변경되면 구 초기화
                }));
              }}
              style={{ flex: 1 }}
            >
              <option value="">시 선택</option>
              <option value="서울특별시">서울특별시</option>
              <option value="부산광역시">부산광역시</option>
              <option value="대구광역시">대구광역시</option>
              <option value="인천광역시">인천광역시</option>
              <option value="광주광역시">광주광역시</option>
              <option value="대전광역시">대전광역시</option>
              <option value="울산광역시">울산광역시</option>
              <option value="세종특별자치시">세종특별자치시</option>
              <option value="경기도">경기도</option>
              <option value="강원도">강원도</option>
              <option value="충청북도">충청북도</option>
              <option value="충청남도">충청남도</option>
              <option value="전라북도">전라북도</option>
              <option value="전라남도">전라남도</option>
              <option value="경상북도">경상북도</option>
              <option value="경상남도">경상남도</option>
              <option value="제주특별자치도">제주특별자치도</option>
            </Select>
            <Select 
              name="locationDistrict" 
              value={formData.locationDistrict || ''} 
              onChange={(e) => setFormData(prev => ({ ...prev, locationDistrict: e.target.value }))}
              style={{ flex: 1 }}
              disabled={!formData.locationCity}
            >
              <option value="">구 선택</option>
              {formData.locationCity === '서울특별시' && (
                <>
                  <option value="강남구">강남구</option>
                  <option value="강동구">강동구</option>
                  <option value="강북구">강북구</option>
                  <option value="강서구">강서구</option>
                  <option value="관악구">관악구</option>
                  <option value="광진구">광진구</option>
                  <option value="구로구">구로구</option>
                  <option value="금천구">금천구</option>
                  <option value="노원구">노원구</option>
                  <option value="도봉구">도봉구</option>
                  <option value="동대문구">동대문구</option>
                  <option value="동작구">동작구</option>
                  <option value="마포구">마포구</option>
                  <option value="서대문구">서대문구</option>
                  <option value="서초구">서초구</option>
                  <option value="성동구">성동구</option>
                  <option value="성북구">성북구</option>
                  <option value="송파구">송파구</option>
                  <option value="양천구">양천구</option>
                  <option value="영등포구">영등포구</option>
                  <option value="용산구">용산구</option>
                  <option value="은평구">은평구</option>
                  <option value="종로구">종로구</option>
                  <option value="중구">중구</option>
                  <option value="중랑구">중랑구</option>
                </>
              )}
              {formData.locationCity === '부산광역시' && (
                <>
                  <option value="강서구">강서구</option>
                  <option value="금정구">금정구</option>
                  <option value="남구">남구</option>
                  <option value="동구">동구</option>
                  <option value="동래구">동래구</option>
                  <option value="부산진구">부산진구</option>
                  <option value="북구">북구</option>
                  <option value="사상구">사상구</option>
                  <option value="사하구">사하구</option>
                  <option value="서구">서구</option>
                  <option value="수영구">수영구</option>
                  <option value="연제구">연제구</option>
                  <option value="영도구">영도구</option>
                  <option value="중구">중구</option>
                  <option value="해운대구">해운대구</option>
                  <option value="기장군">기장군</option>
                </>
              )}
              {formData.locationCity === '대구광역시' && (
                <>
                  <option value="남구">남구</option>
                  <option value="달서구">달서구</option>
                  <option value="달성군">달성군</option>
                  <option value="동구">동구</option>
                  <option value="북구">북구</option>
                  <option value="서구">서구</option>
                  <option value="수성구">수성구</option>
                  <option value="중구">중구</option>
                </>
              )}
              {formData.locationCity === '인천광역시' && (
                <>
                  <option value="계양구">계양구</option>
                  <option value="남구">남구</option>
                  <option value="남동구">남동구</option>
                  <option value="동구">동구</option>
                  <option value="부평구">부평구</option>
                  <option value="서구">서구</option>
                  <option value="연수구">연수구</option>
                  <option value="중구">중구</option>
                  <option value="강화군">강화군</option>
                  <option value="옹진군">옹진군</option>
                </>
              )}
              {formData.locationCity === '광주광역시' && (
                <>
                  <option value="광산구">광산구</option>
                  <option value="남구">남구</option>
                  <option value="동구">동구</option>
                  <option value="북구">북구</option>
                  <option value="서구">서구</option>
                </>
              )}
              {formData.locationCity === '대전광역시' && (
                <>
                  <option value="대덕구">대덕구</option>
                  <option value="동구">동구</option>
                  <option value="서구">서구</option>
                  <option value="유성구">유성구</option>
                  <option value="중구">중구</option>
                </>
              )}
              {formData.locationCity === '울산광역시' && (
                <>
                  <option value="남구">남구</option>
                  <option value="동구">동구</option>
                  <option value="북구">북구</option>
                  <option value="울주군">울주군</option>
                  <option value="중구">중구</option>
                </>
              )}
              {formData.locationCity === '경기도' && (
                <>
                  <option value="수원시">수원시</option>
                  <option value="성남시">성남시</option>
                  <option value="의정부시">의정부시</option>
                  <option value="안양시">안양시</option>
                  <option value="부천시">부천시</option>
                  <option value="광명시">광명시</option>
                  <option value="평택시">평택시</option>
                  <option value="동두천시">동두천시</option>
                  <option value="안산시">안산시</option>
                  <option value="고양시">고양시</option>
                  <option value="과천시">과천시</option>
                  <option value="구리시">구리시</option>
                  <option value="남양주시">남양주시</option>
                  <option value="오산시">오산시</option>
                  <option value="시흥시">시흥시</option>
                  <option value="군포시">군포시</option>
                  <option value="의왕시">의왕시</option>
                  <option value="하남시">하남시</option>
                  <option value="용인시">용인시</option>
                  <option value="파주시">파주시</option>
                  <option value="이천시">이천시</option>
                  <option value="안성시">안성시</option>
                  <option value="김포시">김포시</option>
                  <option value="화성시">화성시</option>
                  <option value="광주시">광주시</option>
                  <option value="여주시">여주시</option>
                  <option value="양평군">양평군</option>
                  <option value="고양군">고양군</option>
                  <option value="연천군">연천군</option>
                  <option value="가평군">가평군</option>
                </>
              )}
            </Select>
          </div>
        </FormGroup>
        <FormGroup>
          <Label>연봉</Label>
          <Input
            type="text"
            name="salary"
            value={formData.salary}
            onChange={handleInputChange}
            placeholder="예: 3,000만원 ~ 5,000만원"
          />
        </FormGroup>
        <FormGroup>
          <Label>근무 시간</Label>
          <Select name="workHours" value={formData.workHours} onChange={handleInputChange}>
            <option value="">근무시간 선택</option>
            <option value="09:00 ~ 18:00">09:00 ~ 18:00</option>
            <option value="10:00 ~ 19:00">10:00 ~ 19:00</option>
            <option value="직접 입력">직접 입력</option>
          </Select>
          {formData.workHours === '직접 입력' && (
            <Input
              type="text"
              name="workHoursCustom"
              value={formData.workHoursCustom || ''}
              onChange={(e) => setFormData(prev => ({ ...prev, workHours: e.target.value }))}
              placeholder="예: 08:30 ~ 17:30"
              style={{ marginTop: '8px' }}
            />
          )}
        </FormGroup>
      </FormGrid>
      
      <FormGroup>
        <Label>주요 업무</Label>
        <TextArea
          name="mainDuties"
          value={formData.mainDuties}
          onChange={handleInputChange}
          placeholder="담당할 주요 업무를 입력해주세요"
        />
      </FormGroup>

      <FormGroup>
        <Label>자격 요건</Label>
        <TextArea
          name="requirements"
          value={formData.requirements}
          onChange={handleInputChange}
          placeholder="필요한 자격 요건을 입력해주세요"
        />
      </FormGroup>

      <FormGroup>
        <Label>복리후생</Label>
        <TextArea
          name="benefits"
          value={formData.benefits}
          onChange={handleInputChange}
          placeholder="제공되는 복리후생을 입력해주세요"
        />
      </FormGroup>

      <FormGrid>
        <FormGroup>
          <Label>마감일</Label>
          <Input
            type="date"
            name="deadline"
            value={formData.deadline}
            onChange={handleInputChange}
          />
        </FormGroup>
        <FormGroup>
          <Label>연락처 이메일</Label>
          <Input
            type="email"
            name="contactEmail"
            value={formData.contactEmail}
            onChange={handleInputChange}
            placeholder="인사담당자 이메일"
          />
        </FormGroup>
      </FormGrid>

      <AISuggestion>
        <AISuggestionTitle>
          <FiCheck size={16} />
          AI 이미지 생성
        </AISuggestionTitle>
        <AISuggestionText>
          입력하신 정보를 바탕으로 AI가 다양한 스타일의 채용공고 이미지를 생성합니다.
        </AISuggestionText>
      </AISuggestion>
    </FormSection>
  );

  const renderStep2 = () => (
    <LoadingSection>
      <LoadingSpinner />
      <LoadingText>AI가 이미지를 생성하고 있습니다...</LoadingText>
      <LoadingSubtext>잠시만 기다려주세요 (약 3초 소요)</LoadingSubtext>
    </LoadingSection>
  );

  const renderStep3 = () => (
    <FormSection>
      <SectionTitle>
        <FiImage size={18} />
        생성된 이미지 중 선택
      </SectionTitle>
      <ImageGrid>
        {generatedImages.map((image) => (
          <ImageCard
            key={image.id}
            className={selectedImage?.id === image.id ? 'selected' : ''}
            onClick={() => handleImageSelect(image)}
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
          >
            <ImagePlaceholder>
              <FiImage />
            </ImagePlaceholder>
            <ImageInfo>
              <ImageTitle>{image.title}</ImageTitle>
              <ImageDescription>{image.description}</ImageDescription>
            </ImageInfo>
          </ImageCard>
        ))}
      </ImageGrid>
    </FormSection>
  );

  const renderCurrentStep = () => {
    switch (currentStep) {
      case 1: return renderStep1();
      case 2: return renderStep2();
      case 3: return renderStep3();
      default: return null;
    }
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <Overlay
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          onClick={onClose}
        >
          <Modal
            initial={{ scale: 0.9, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0.9, opacity: 0 }}
            onClick={(e) => e.stopPropagation()}
          >
            <Header>
              <Title>이미지 기반 채용공고 등록</Title>
              <CloseButton onClick={onClose}>
                <FiX />
              </CloseButton>
            </Header>

            <Content>
              <StepIndicator>
                {steps.map((step) => (
                  <Step key={step.number}>
                    <StepNumber 
                      active={currentStep === step.number}
                      completed={currentStep > step.number}
                    >
                      {currentStep > step.number ? <FiCheck size={16} /> : step.number}
                    </StepNumber>
                    <StepLabel 
                      active={currentStep === step.number}
                      completed={currentStep > step.number}
                    >
                      {step.label}
                    </StepLabel>
                  </Step>
                ))}
              </StepIndicator>

              {renderCurrentStep()}

              <ButtonGroup>
                <Button 
                  className="secondary" 
                  onClick={currentStep === 1 ? onClose : () => setCurrentStep(currentStep - 1)}
                >
                  <FiArrowLeft size={16} />
                  {currentStep === 1 ? '취소' : '이전'}
                </Button>
                <Button 
                  className="primary" 
                  onClick={currentStep === 1 ? handleGenerateImages : handleComplete}
                  disabled={currentStep === 3 && !selectedImage}
                >
                  {currentStep === 1 ? '이미지 생성' : '완료'}
                  {currentStep === 1 && <FiRefreshCw size={16} />}
                  {currentStep === 3 && <FiCheck size={16} />}
                </Button>
              </ButtonGroup>
            </Content>
          </Modal>
        </Overlay>
      )}
    </AnimatePresence>
  );
};

export default ImageBasedRegistration; 