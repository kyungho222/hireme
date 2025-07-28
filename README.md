# HireMe Project

통합된 HireMe 프로젝트로, 관리자 대시보드와 클라이언트 애플리케이션을 포함합니다.

## 프로젝트 구조

```
hireme_project/
├── admin/          # 관리자 대시보드 (포트: 3001)
├── client/         # 클라이언트 애플리케이션 (포트: 3000)
├── package.json    # 루트 프로젝트 설정
└── README.md       # 프로젝트 문서
```

## 설치 및 실행

### 전체 프로젝트 설치
```bash
npm run install:all
```

### 개발 서버 실행
```bash
# 두 애플리케이션 모두 실행
npm run dev

# 또는 개별 실행
npm run start:admin    # 관리자 대시보드 (http://localhost:3001)
npm run start:client   # 클라이언트 앱 (http://localhost:3000)
```

### 빌드
```bash
# 전체 프로젝트 빌드
npm run build

# 개별 빌드
npm run build:admin
npm run build:client
```

## 접근 경로

### 관리자 대시보드 (http://localhost:3001)
- `/` - 대시보드
- `/resume` - 이력서 관리
- `/interview` - 면접 관리
- `/portfolio` - 포트폴리오 분석
- `/cover-letter` - 자기소개서 검증
- `/talent` - 인재 추천
- `/users` - 사용자 관리
- `/settings` - 설정

### 클라이언트 애플리케이션 (http://localhost:3000)
- `/` - 홈
- `/jobs` - 채용 공고
- `/jobs/:id` - 채용 상세
- `/applications` - 지원 현황
- `/portfolio` - 포트폴리오
- `/recommendations` - 추천
- `/interviews` - 면접

## 기술 스택

### 관리자 대시보드
- React 18
- React Router DOM
- Styled Components
- Recharts
- Framer Motion
- React Query
- Axios

### 클라이언트 애플리케이션
- React 18
- TypeScript
- React Router DOM
- Recharts
- FontAwesome

## 개발 가이드

1. 각 프로젝트는 독립적으로 개발 가능
2. 공통 컴포넌트나 유틸리티는 필요시 공유 가능
3. API 엔드포인트는 각 프로젝트에서 독립적으로 관리
4. 스타일링은 각 프로젝트의 컨벤션을 따름

## 배포

각 애플리케이션은 독립적으로 배포 가능합니다:

```bash
# 관리자 대시보드 빌드
cd admin && npm run build

# 클라이언트 앱 빌드
cd client && npm run build
```

빌드된 파일은 각각의 `build` 폴더에 생성됩니다. 