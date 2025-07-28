# 🚀 HireMe Project

통합된 HireMe 프로젝트 - 관리자 콘텍스트와 클라이언트 콘텍스트로 분리된 풀스택 개발 환경

## 📁 프로젝트 구조

```
hireme_project/
├── admin/                          # 관리자 콘텍스트
│   ├── frontend/                   # React 관리자 대시보드
│   │   ├── src/
│   │   ├── package.json
│   │   └── Dockerfile
│   ├── backend/                    # 관리자용 백엔드 API
│   │   ├── app/
│   │   ├── requirements.txt
│   │   └── Dockerfile
│   ├── database/                   # 관리자용 데이터베이스
│   │   ├── init/
│   │   └── data/
│   └── docker-compose.yml          # 관리자 콘텍스트용
│
├── client/                         # 클라이언트 콘텍스트
│   ├── frontend/                   # React 클라이언트 앱
│   │   ├── src/
│   │   ├── package.json
│   │   └── Dockerfile
│   ├── backend/                    # 클라이언트용 백엔드 API
│   │   ├── app/
│   │   ├── requirements.txt
│   │   └── Dockerfile
│   ├── database/                   # 클라이언트용 데이터베이스
│   │   ├── init/
│   │   └── data/
│   └── docker-compose.yml          # 클라이언트 콘텍스트용
│
├── shared/                         # 공통 리소스
│   ├── utils/
│   ├── components/
│   └── config/
│
├── docker-compose.yml              # 전체 통합용
├── package.json                    # 루트 워크스페이스
└── README.md
```

## 🛠 기술 스택

### Frontend
- **React 18** - 사용자 인터페이스
- **TypeScript** - 타입 안전성 (클라이언트)
- **Styled Components** - 스타일링
- **React Router DOM** - 라우팅

### Backend
- **Python 3.11** - 서버 사이드 로직
- **FastAPI** - REST API 프레임워크
- **Motor** - 비동기 MongoDB 드라이버
- **Pydantic** - 데이터 검증

### Database
- **MongoDB 6.0** - NoSQL 데이터베이스

### DevOps
- **Docker** - 컨테이너화
- **Docker Compose** - 멀티 서비스 오케스트레이션

## 🚀 빠른 시작

### 1. 저장소 클론
```bash
git clone https://github.com/kyungho222/hireme.git
cd hireme
```

### 2. 전체 환경 실행 (모든 서비스)
```bash
# 모든 서비스 빌드 및 실행
docker-compose up --build

# 백그라운드 실행
docker-compose up -d --build
```

### 3. 개별 콘텍스트 실행
```bash
# 관리자 콘텍스트만 실행
cd admin && docker-compose up --build

# 클라이언트 콘텍스트만 실행
cd client && docker-compose up --build
```

### 4. 접속 URL
- **관리자 대시보드**: http://localhost:3001
- **클라이언트 애플리케이션**: http://localhost:3000
- **관리자 백엔드 API**: http://localhost:8000
- **클라이언트 백엔드 API**: http://localhost:8001
- **관리자 API 문서**: http://localhost:8000/docs
- **클라이언트 API 문서**: http://localhost:8001/docs
- **관리자 MongoDB**: localhost:27017
- **클라이언트 MongoDB**: localhost:27018

## 📋 콘텍스트별 구성

### 🖥️ 관리자 콘텍스트 (포트 3001, 8000, 27017)
- **프론트엔드**: React 관리자 대시보드
- **백엔드**: 사용자 관리, 이력서 관리, 면접 관리 API
- **데이터베이스**: 관리자 전용 MongoDB
- **주요 기능**:
  - 사용자 관리
  - 이력서 관리
  - 면접 관리
  - 포트폴리오 분석
  - 커버레터 검증
  - 인재 추천

### 💼 클라이언트 콘텍스트 (포트 3000, 8001, 27018)
- **프론트엔드**: React + TypeScript 클라이언트 앱
- **백엔드**: 채용 정보, 포트폴리오, 지원 관리 API
- **데이터베이스**: 클라이언트 전용 MongoDB
- **주요 기능**:
  - 채용 정보 탐색
  - 포트폴리오 관리
  - 지원 현황 관리
  - 추천 시스템

## 🐳 Docker 명령어

### 전체 환경
```bash
# 모든 서비스 실행
docker-compose up

# 백그라운드 실행
docker-compose up -d

# 서비스 중지
docker-compose down

# 로그 확인
docker-compose logs -f
```

### 개별 콘텍스트
```bash
# 관리자 콘텍스트
cd admin && docker-compose up --build

# 클라이언트 콘텍스트
cd client && docker-compose up --build
```

### 개발용 명령어
```bash
# 특정 서비스만 재시작
docker-compose restart backend-admin
docker-compose restart backend-client

# 컨테이너 내부 접속
docker-compose exec backend-admin bash
docker-compose exec mongodb-admin mongosh

# 이미지 재빌드
docker-compose build --no-cache
```

## 🔧 개발 환경 설정

### 로컬 개발 (Docker 없이)
```bash
# 관리자 백엔드
cd admin/backend
pip install -r requirements.txt
uvicorn main:app --reload

# 관리자 프론트엔드
cd admin/frontend
npm install
npm start

# 클라이언트 백엔드
cd client/backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8001

# 클라이언트 프론트엔드
cd client/frontend
npm install
npm start
```

### 환경 변수
```bash
# 관리자 백엔드 환경 변수
MONGODB_URI=mongodb://admin:password@localhost:27017/hireme-admin?authSource=admin
DEBUG=1

# 클라이언트 백엔드 환경 변수
MONGODB_URI=mongodb://admin:password@localhost:27018/hireme-client?authSource=admin
DEBUG=1

# 프론트엔드 환경 변수
REACT_APP_API_URL=http://localhost:8000  # 관리자용
REACT_APP_API_URL=http://localhost:8001  # 클라이언트용
```

## 📊 API 엔드포인트

### 관리자 API (포트 8000)
- `GET /api/users` - 사용자 목록 조회
- `POST /api/users` - 사용자 생성
- `GET /api/resumes` - 이력서 목록 조회
- `POST /api/resumes` - 이력서 생성
- `GET /api/interviews` - 면접 목록 조회
- `POST /api/interviews` - 면접 생성

### 클라이언트 API (포트 8001)
- `GET /api/jobs` - 채용 정보 목록 조회
- `POST /api/jobs` - 채용 정보 생성
- `GET /api/portfolios` - 포트폴리오 목록 조회
- `POST /api/portfolios` - 포트폴리오 생성
- `GET /api/applications` - 지원 현황 조회
- `POST /api/applications` - 지원 생성

## 🗄️ 데이터베이스 스키마

### 관리자 데이터베이스 (hireme-admin)
```javascript
// Users Collection
{
  _id: ObjectId,
  username: String,
  email: String,
  role: String,
  created_at: Date
}

// Resumes Collection
{
  _id: ObjectId,
  user_id: String,
  title: String,
  content: String,
  status: String,
  created_at: Date
}

// Interviews Collection
{
  _id: ObjectId,
  user_id: String,
  company: String,
  position: String,
  date: Date,
  status: String,
  created_at: Date
}
```

### 클라이언트 데이터베이스 (hireme-client)
```javascript
// Jobs Collection
{
  _id: ObjectId,
  title: String,
  company: String,
  location: String,
  description: String,
  requirements: Array,
  salary_range: String,
  type: String,
  status: String,
  created_at: Date
}

// Portfolios Collection
{
  _id: ObjectId,
  user_id: String,
  title: String,
  description: String,
  github_url: String,
  live_url: String,
  technologies: Array,
  status: String,
  created_at: Date
}

// Applications Collection
{
  _id: ObjectId,
  user_id: String,
  job_id: String,
  status: String,
  applied_at: Date,
  updated_at: Date
}
```

## 🚀 배포

### 프로덕션 빌드
```bash
# 프론트엔드 빌드
cd admin/frontend && npm run build
cd client/frontend && npm run build

# 백엔드 실행
cd admin/backend && uvicorn main:app --host 0.0.0.0 --port 8000
cd client/backend && uvicorn main:app --host 0.0.0.0 --port 8001
```

## 🤝 기여하기

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

## 📞 문의

프로젝트에 대한 문의사항이 있으시면 이슈를 생성해주세요. 