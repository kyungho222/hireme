# AI 채용 관리 시스템

SNOW와 NAVER 채용 사이트를 참고하여 개발한 AI 기반 채용 관리 시스템입니다.

## 🚀 프로젝트 개요

### 목적
- AI 기술을 활용한 스마트한 채용 프로세스 구축
- 이력서 분석, 면접 관리, 포트폴리오 평가 등 종합적인 채용 관리
- 직관적이고 현대적인 UI/UX 제공

### 참고 사이트
- [SNOW 채용 사이트](https://recruit.snowcorp.com/main.do)
- [NAVER 채용 사이트](https://recruit.navercorp.com/main.do)

## 📋 사이트맵

### 대시보드
- [x] 전체 채용 현황 요약 (서류 접수, 면접 일정, 추천 인재 등)
- [x] 주요 알림 및 리포트 바로가기
- [x] 실시간 통계 및 차트

### 이력서 관리
- [x] 이력서 제출 현황
- [x] PDF 변환 / 다운로드
- [x] QR 코드 스캔 및 정보 조회
- [x] 서류 자동 분석 결과

### 면접 관리
- [x] 비대면 면접 예약 및 일정 관리
- [x] AI 질문 설정 / 자동 생성
- [x] 구직자 영상 응답 조회
- [x] AI 면접 분석 결과

### 포트폴리오 분석
- [x] GitHub 등 연동 관리
- [x] 자동 코드 리뷰 결과
- [x] 프로젝트별 평가 리포트

### 자소서 검증
- [x] 자소서 분석 현황
- [x] 대필 및 AI 작성 감지 결과
- [x] 자소서와 영상 답변 STT 불일치 비교

### 인재 추천
- [x] AI 유사 인재 목록
- [x] 필터 및 조건 검색
- [x] 인재 프로필 상세 조회

### 사용자 관리 및 보안
- [x] 로그인/권한 관리
- [x] 개인정보 보호 설정
- [x] 사용 로그 기록

### 설정 및 지원
- [x] 시스템 설정 (AI 모델 파라미터, 알림 설정 등)
- [x] 도움말 / FAQ
- [x] 고객 지원 문의

## ✅ 완료된 작업 (DONE)

### 1. 프로젝트 구조 설정
- [x] React 프로젝트 초기화
- [x] 필요한 패키지 설치 (react-router-dom, styled-components, framer-motion, recharts 등)
- [x] 기본 폴더 구조 생성

### 2. 레이아웃 및 네비게이션
- [x] 반응형 사이드바 네비게이션
- [x] 상단 헤더 (검색, 알림, 사용자 프로필)
- [x] 모바일 대응 (햄버거 메뉴)
- [x] SNOW/NAVER 스타일의 깔끔한 디자인

### 3. 페이지 구현
- [x] **대시보드**: 통계 카드, 차트, 최근 활동
- [x] **이력서 관리**: 이력서 리스트, AI 분석, QR 기능
- [x] **면접 관리**: 면접 일정, AI 질문, 분석 결과
- [x] **포트폴리오 분석**: GitHub 연동, 코드 리뷰
- [x] **자소서 검증**: AI 분석, 표절 검사
- [x] **인재 추천**: AI 매칭, 필터링
- [x] **사용자 관리**: 권한 관리, 보안 설정
- [x] **설정 및 지원**: 시스템 설정, FAQ

### 4. UI/UX 구현
- [x] styled-components를 활용한 모던한 스타일링
- [x] Framer Motion 애니메이션 효과
- [x] Recharts를 활용한 데이터 시각화
- [x] 반응형 디자인 (모바일/태블릿/데스크톱)
- [x] 호버 효과 및 인터랙션

### 5. 기능 구현
- [x] 라우팅 시스템 (React Router)
- [x] 검색 및 필터링 기능
- [x] 상태 관리 (React Hooks)
- [x] 샘플 데이터 및 모의 기능

## 🔄 진행 중인 작업 (IN PROGRESS)

### 1. 성능 최적화
- [ ] 코드 스플리팅 및 지연 로딩
- [ ] 이미지 최적화
- [ ] 번들 크기 최적화

### 2. 접근성 개선
- [ ] ARIA 라벨 추가
- [ ] 키보드 네비게이션
- [ ] 색상 대비 개선

## 📝 남은 작업 (TODO)

### 1. 백엔드 연동
- [ ] API 엔드포인트 설계
- [ ] 데이터베이스 스키마 설계
- [ ] 인증/인가 시스템 구현
- [ ] 파일 업로드 기능

### 2. AI 기능 구현
- [ ] 실제 AI 모델 연동
- [ ] 이력서 분석 API
- [ ] 면접 질문 생성 AI
- [ ] 포트폴리오 평가 AI
- [ ] 자소서 검증 AI

### 3. 고급 기능
- [ ] 실시간 알림 시스템
- [ ] 다국어 지원
- [ ] 다크 모드
- [ ] PWA 지원
- [ ] 오프라인 기능

### 4. 테스트 및 품질 관리
- [ ] 단위 테스트 작성
- [ ] 통합 테스트 작성
- [ ] E2E 테스트 작성
- [ ] 성능 테스트

### 5. 배포 및 운영
- [ ] CI/CD 파이프라인 구축
- [ ] 도커 컨테이너화
- [ ] 클라우드 배포
- [ ] 모니터링 시스템

## 🛠 기술 스택

### Frontend
- **React 18.2.0** - 사용자 인터페이스 구축
- **React Router 6.3.0** - 클라이언트 사이드 라우팅
- **Styled Components 5.3.5** - CSS-in-JS 스타일링
- **Framer Motion 7.2.1** - 애니메이션 라이브러리
- **React Icons 4.4.0** - 아이콘 라이브러리
- **Recharts 2.1.8** - 데이터 시각화

### Development Tools
- **Create React App** - React 프로젝트 설정
- **ESLint** - 코드 품질 관리
- **npm** - 패키지 관리

### UI/UX
- **Noto Sans KR** - 한글 폰트
- **CSS Grid & Flexbox** - 레이아웃
- **CSS Variables** - 테마 관리
- **반응형 디자인** - 모바일 퍼스트

## 🚀 실행 방법

### 1. 프로젝트 클론
```bash
git clone [repository-url]
cd recruitment-dashboard
```

### 2. 의존성 설치
```bash
npm install
```

### 3. 개발 서버 실행
```bash
npm start
```

### 4. 브라우저에서 확인
- http://localhost:3000 접속

## 📁 프로젝트 구조

```
src/
├── components/
│   └── Layout/
│       └── Layout.js          # 메인 레이아웃 컴포넌트
├── pages/
│   ├── Dashboard/
│   │   └── Dashboard.js       # 대시보드 페이지
│   ├── ResumeManagement/
│   │   └── ResumeManagement.js # 이력서 관리 페이지
│   ├── InterviewManagement/
│   │   └── InterviewManagement.js # 면접 관리 페이지
│   ├── PortfolioAnalysis/
│   │   └── PortfolioAnalysis.js # 포트폴리오 분석 페이지
│   ├── CoverLetterValidation/
│   │   └── CoverLetterValidation.js # 자소서 검증 페이지
│   ├── TalentRecommendation/
│   │   └── TalentRecommendation.js # 인재 추천 페이지
│   ├── UserManagement/
│   │   └── UserManagement.js   # 사용자 관리 페이지
│   └── Settings/
│       └── Settings.js        # 설정 및 지원 페이지
├── App.js                     # 메인 앱 컴포넌트
├── index.js                   # 진입점
└── index.css                  # 전역 스타일
```

## 🎨 디자인 시스템

### 색상 팔레트
- **Primary**: #00c851 (초록색)
- **Secondary**: #007bff (파란색)
- **Accent**: #ff6b35 (주황색)
- **Background**: #f8f9fa (연한 회색)
- **Text**: #333 (진한 회색)

### 타이포그래피
- **Font Family**: Noto Sans KR
- **Font Weights**: 300, 400, 500, 700
- **Line Height**: 1.6

### 컴포넌트
- **Border Radius**: 8px
- **Shadow**: 0 2px 4px rgba(0,0,0,0.1)
- **Transition**: all 0.3s ease

## 📊 주요 기능

### 1. 대시보드
- 실시간 채용 현황 통계
- 지원자 추이 차트
- 채용 현황 파이 차트
- 최근 활동 목록

### 2. 이력서 관리
- 이력서 목록 및 검색
- AI 분석 결과 표시
- PDF 다운로드
- QR 코드 생성/스캔

### 3. 면접 관리
- 면접 일정 관리
- AI 질문 자동 생성
- 면접 분석 결과
- 영상 응답 조회

### 4. 포트폴리오 분석
- GitHub 프로젝트 연동
- 코드 품질 분석
- 기술 스택 평가
- 프로젝트별 리포트

### 5. 자소서 검증
- AI 자소서 분석
- 표절 검사
- 문법 및 일관성 검사
- 개선 사항 제안

### 6. 인재 추천
- AI 기반 인재 매칭
- 필터링 및 검색
- 상세 프로필 조회
- 연락 기능

## 🔧 개발 환경 설정

### 필수 요구사항
- Node.js 16.0.0 이상
- npm 8.0.0 이상

### 권장 개발 도구
- VS Code
- React Developer Tools
- Redux DevTools (향후 추가 예정)

## 📝 라이센스

이 프로젝트는 MIT 라이센스 하에 배포됩니다.

## 🤝 기여하기

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📞 문의

프로젝트에 대한 문의사항이 있으시면 이슈를 생성해 주세요.

---

**마지막 업데이트**: 2024년 1월
**버전**: 1.0.0
**상태**: 개발 중 (Development) 