# HireMe Project - 채용공고 관리 시스템

## 📋 프로젝트 개요

HireMe Project는 관리자와 구직자를 위한 종합적인 채용공고 관리 시스템입니다. 관리자는 직관적인 인터페이스를 통해 채용공고를 등록하고 관리할 수 있으며, 구직자는 다양한 채용 정보를 쉽게 검색하고 지원할 수 있습니다.

## 🏗️ 시스템 아키텍처

### 전체 구조
```
hireme_project/
├── admin/                    # 관리자 시스템
│   ├── backend/             # 관리자 백엔드 (Python/FastAPI)
│   ├── frontend/            # 관리자 프론트엔드 (React)
│   └── database/            # 관리자 데이터베이스
├── client/                   # 구직자 시스템
│   ├── backend/             # 구직자 백엔드 (Python/FastAPI)
│   ├── frontend/            # 구직자 프론트엔드 (React/TypeScript)
│   └── database/            # 구직자 데이터베이스
└── shared/                  # 공유 컴포넌트 및 유틸리티
```

### 기술 스택
- **Frontend**: React, TypeScript, Styled Components, Framer Motion
- **Backend**: Python, FastAPI
- **Database**: MongoDB
- **Containerization**: Docker, Docker Compose
- **Package Management**: npm, pip

## 🚀 주요 기능

### 1. 관리자 대시보드 (Admin Dashboard)

#### 채용 관리 (Recruitment Management)
- **채용공고 등록**: 텍스트 기반 및 이미지 기반 등록 방식
- **공고 관리**: 등록된 채용공고 목록 조회, 수정, 삭제
- **상태 관리**: 임시저장 → 모집중 상태 변경
- **홈페이지 등록**: 공고를 홈페이지에 게시하는 기능

#### 사용자 관리 (User Management)
- 구직자 계정 관리
- 지원자 정보 관리
- 권한 관리

#### 포트폴리오 분석 (Portfolio Analysis)
- 지원자 포트폴리오 분석
- AI 기반 매칭 시스템

#### 면접 관리 (Interview Management)
- 면접 일정 관리
- 면접 결과 기록
- 면접 피드백 시스템

#### 이력서 관리 (Resume Management)
- 지원자 이력서 관리
- 이력서 검색 및 필터링

#### 인재 추천 (Talent Recommendation)
- AI 기반 인재 추천
- 매칭 알고리즘

#### 자기소개서 검증 (Cover Letter Validation)
- 자기소개서 검증 시스템
- AI 기반 평가

#### 설정 (Settings)
- 시스템 설정
- 사용자 프로필 관리

### 2. 채용공고 등록 시스템

#### 텍스트 기반 등록 (Text-Based Registration)
**5단계 등록 프로세스:**

1. **구인 부서 및 경력 선택**
   - 조직도 연동 부서 선택
   - 경력 구분 (신입/경력)
   - 경력 연도 선택 (2년이상, 2~3년, 4~5년, 직접입력)

2. **구인 정보**
   - 구인 인원수 선택
   - 주요 업무 입력 (AI 추천 기능)

3. **근무 조건**
   - 근무 시간 선택 (09:00~18:00, 10:00~19:00, 직접입력)
   - 근무지 선택 (시/구 2단계 선택)
   - 연봉 입력

4. **전형 절차**
   - 기본 전형 절차 설정
   - 서류 → 실무면접 → 최종면접 → 입사

5. **지원 방법**
   - 인사담당자 이메일
   - 마감일 설정

#### 이미지 기반 등록 (Image-Based Registration)
**7단계 등록 프로세스:**

1. **구인 부서 및 경력 선택** (텍스트 기반과 동일)
2. **구인 정보** (텍스트 기반과 동일)
3. **근무 조건** (텍스트 기반과 동일)
4. **전형 절차** (텍스트 기반과 동일)
5. **지원 방법** (텍스트 기반과 동일)
6. **이미지 생성** (AI 기반 채용공고 이미지 생성)
7. **이미지 선택** (생성된 이미지 중 선택)

#### 공통 기능
- **템플릿 시스템**: 자주 사용하는 공고 정보를 템플릿으로 저장/불러오기
- **조직도 설정**: 회사 조직도를 이미지로 업로드하여 AI가 분석하여 부서 정보 자동 추출
- **AI 기능**: 
  - 업무 설명 AI 추천
  - 자격 요건 자동 생성
  - 선호 자격 자동 적용
  - 이미지 기반 채용공고 생성
- **이메일 알림**: 등록 완료 시 인사담당자에게 자동 이메일 전송

### 3. 채용공고 관리 기능

#### 공고 목록 관리
- **상태 관리**: 임시저장 ↔ 모집중 상태 변경
- **홈페이지 등록**: 버튼 클릭 시 상태 변경 (버튼 비활성화)
- **연봉 표시**: 자동으로 "만원" 단위 적용 및 천/백 단위 변환
  - 예: "4,000만원" → "4천만원"
  - 예: "4,500만원" → "4천5백만원"
  - 예: "3,000만원 ~ 5,000만원" → "3천~5천만원"

#### 상세 페이지
- **보기 모드**: 채용공고 상세 정보 조회
- **수정 모드**: 채용공고 정보 수정
- **연봉 포맷팅**: 자동으로 한국어 단위 적용

### 4. 구직자 시스템 (Client)

#### 주요 페이지
- **홈**: 메인 페이지
- **채용공고**: 전체 채용공고 목록
- **채용공고 상세**: 개별 채용공고 상세 정보
- **지원하기**: 채용공고 지원 기능
- **내 지원현황**: 지원한 공고 목록
- **면접**: 면접 일정 및 결과
- **추천**: AI 기반 맞춤 추천
- **포트폴리오**: 개인 포트폴리오 관리
- **제품/서비스**: 회사 제품/서비스 소개
- **고객센터**: 문의 및 지원
- **마이페이지**: 개인 정보 관리

## 🛠️ 설치 및 실행

### Docker를 사용한 실행 (권장)

#### 1. 전체 시스템 실행
```bash
# 전체 시스템 실행 (MongoDB, 백엔드, 프론트엔드 모두 포함)
docker-compose up
```

#### 2. 개발 환경 실행
```bash
# 프론트엔드만 실행 (개발용)
docker-compose -f docker-compose.dev.yml up
```

### 로컬 실행

#### 1. 프론트엔드 실행
```bash
# 관리자 프론트엔드
cd admin/frontend
npm install
npm start

# 구직자 프론트엔드
cd client/frontend
npm install
npm start
```

#### 2. 백엔드 실행
```bash
# 관리자 백엔드
cd admin/backend
pip install -r requirements.txt
python main.py

# 구직자 백엔드
cd client/backend
pip install -r requirements.txt
python main.py
```

## 📱 접속 정보

- **관리자 대시보드**: http://localhost:3001
- **구직자 시스템**: http://localhost:3000
- **관리자 API**: http://localhost:8001
- **구직자 API**: http://localhost:8000

## 🎨 UI/UX 특징

### 디자인 시스템
- **색상**: CSS 변수를 활용한 일관된 색상 체계
- **타이포그래피**: 가독성 높은 폰트 스택
- **간격**: 8px 기반 그리드 시스템
- **애니메이션**: Framer Motion을 활용한 부드러운 전환 효과

### 반응형 디자인
- **모바일**: 768px 이하 최적화
- **태블릿**: 768px ~ 1024px 지원
- **데스크톱**: 1024px 이상 최적화

### 접근성
- **키보드 네비게이션**: 모든 기능 키보드로 접근 가능
- **스크린 리더**: ARIA 라벨 및 시맨틱 HTML
- **색상 대비**: WCAG 2.1 AA 기준 준수

## 🤖 AI 기능

### 현재 구현된 AI 기능
1. **조직도 분석**: 업로드된 조직도 이미지를 AI가 분석하여 부서 정보 자동 추출
2. **업무 설명 추천**: 입력된 부서와 경력에 따른 AI 추천 업무 설명
3. **자격 요건 자동 생성**: 업무와 경력에 따른 자동 자격 요건 생성
4. **선호 자격 자동 적용**: 분야별 일반적인 선호 자격 자동 적용
5. **이미지 기반 채용공고 생성**: 입력된 정보를 바탕으로 AI가 채용공고 이미지 생성

### 향후 계획
- **실제 AI API 연동**: 현재는 시뮬레이션, 실제 AI 서비스 연동 예정
- **이메일 서비스**: 실제 이메일 전송 기능 구현
- **이미지 생성**: 실제 AI 이미지 생성 API 연동

## 🔧 개발 환경 설정

### 필수 요구사항
- Node.js 16+
- Python 3.8+
- Docker & Docker Compose
- MongoDB (Docker로 자동 설치)

### 개발 도구
- **IDE**: VS Code 권장
- **확장 프로그램**: 
  - ESLint
  - Prettier
  - Python
  - Docker

## 📝 코드 구조

### 프론트엔드 구조
```
src/
├── components/          # 재사용 가능한 컴포넌트
├── pages/              # 페이지 컴포넌트
├── hooks/              # 커스텀 훅
├── utils/              # 유틸리티 함수
└── styles/             # 스타일 관련 파일
```

### 백엔드 구조
```
backend/
├── main.py             # FastAPI 애플리케이션
├── models/             # 데이터 모델
├── routes/             # API 라우트
├── services/           # 비즈니스 로직
└── utils/              # 유틸리티 함수
```

## 🚀 배포

### Docker 배포
```bash
# 프로덕션 빌드
docker-compose -f docker-compose.prod.yml up -d
```

### 환경 변수
```bash
# .env 파일 예시
DATABASE_URL=mongodb://localhost:27017/hireme
JWT_SECRET=your-secret-key
EMAIL_SERVICE=your-email-service
```

## 🤝 기여하기

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 자세한 내용은 `LICENSE` 파일을 참조하세요.

## 📞 문의

프로젝트에 대한 문의사항이 있으시면 이슈를 생성해 주세요.

---

**HireMe Project** - 더 나은 채용 경험을 만들어갑니다. 🚀 