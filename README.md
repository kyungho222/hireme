# 🤖 HireMe - AI 기반 스마트 채용 플랫폼

## 📋 개요

HireMe는 **AI 기반 스마트 채용 플랫폼**으로, ReActAgent와 다양한 AI 도구를 활용하여 채용 프로세스를 자동화하고 최적화하는 종합 솔루션입니다.

### ✨ 주요 기능

#### 🤖 AI 에이전트 시스템
- **ReActAgent**: 추론-액션-관찰 루프를 통한 지능형 AI 에이전트
- **LangGraph 에이전트**: 복잡한 의도 분석 및 라우팅 시스템
- **PickTalk 챗봇**: 대화형 AI 어시스턴트
- **채용공고 생성 에이전트**: AI 기반 채용공고 자동 생성

#### 🔍 AI 분석 및 검색
- **이력서 AI 분석**: 9개 항목별 상세 분석 및 점수화
- **자기소개서 분석**: STAR 기법, 지원동기 등 다면적 평가
- **포트폴리오 분석**: GitHub 연동 및 프로젝트 평가
- **다중 하이브리드 검색**: 벡터 + 텍스트 + 키워드 검색 결합
- **유사도 분석**: 표절 검사 및 유사 문서 탐지

#### 📄 문서 처리
- **PDF OCR**: 이미지 기반 PDF 텍스트 추출
- **문서 업로드**: PDF, DOC, DOCX, TXT 파일 지원
- **AI 요약**: Google Gemini API 기반 문서 요약
- **청킹 시스템**: 대용량 문서 분할 및 벡터화

#### 🎯 채용 관리
- **지원자 관리**: 종합적인 지원자 정보 관리
- **상태 관리**: 서류합격, 최종합격, 보류, 서류불합격
- **메일 자동화**: 상태별 자동 메일 발송
- **면접 관리**: 면접 일정 및 결과 관리

## 🚀 빠른 시작

### 1. 환경 설정
```bash
# Python 3.8+ 필요
python --version

# 가상환경 생성 (권장)
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # macOS/Linux
```

### 2. 설치
```bash
# 자동 설치 (Windows)
install.bat

# 자동 설치 (macOS/Linux)
./install.sh

# 또는 수동 설치
pip install -r requirements.txt
```

### 3. 환경 변수 설정
`.env` 파일을 생성하고 다음 내용 추가:
```env
# OpenAI API
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4o-mini

# Google Gemini API (문서 분석용)
GOOGLE_API_KEY=your_gemini_api_key_here

# MongoDB
MONGODB_URI=mongodb://localhost:27017/hireme

# 서버 설정
HOST=0.0.0.0
PORT=8000

# Pinecone (벡터 검색용, 선택사항)
PINECONE_API_KEY=your_pinecone_api_key_here
PINECONE_INDEX_NAME=resume-vectors

# GitHub API (포트폴리오 분석용, 선택사항)
GITHUB_TOKEN=your_github_token_here
```

### 4. MongoDB 설치
- [MongoDB Community Edition](https://www.mongodb.com/try/download/community) 다운로드
- 또는 Docker: `docker run -d -p 27017:27017 --name mongodb mongo:latest`

### 5. 서버 실행
```bash
# 자동 실행 (Windows)
run.bat

# 자동 실행 (macOS/Linux)
./run.sh

# 또는 수동 실행
python backend/main.py
```

서버 시작 후: **http://localhost:8000/docs** 에서 API 문서 확인

## 🔧 주요 API

### ReActAgent
```
POST /api/react-agent/start-session     # 세션 시작
POST /api/react-agent/process-task      # 작업 처리
```

### PickTalk 챗봇
```
POST /api/pick-chatbot/chat            # 대화
GET  /api/pick-chatbot/session/{id}    # 세션 조회
```

### 지원자 관리
```
GET  /api/applicants                    # 지원자 목록
POST /api/applicants                    # 지원자 등록
GET  /api/applicants/{id}               # 지원자 상세
PUT  /api/applicants/{id}               # 지원자 수정
```

### AI 분석
```
POST /api/ai-analysis/resume/analyze    # 이력서 분석
POST /api/ai-analysis/resume/batch-analyze # 일괄 분석
GET  /api/ai-analysis/resume/{id}       # 분석 결과 조회
```

### 문서 처리
```
POST /api/upload/file                   # 파일 업로드
POST /api/upload/summarize              # 텍스트 요약
GET  /api/integrated-ocr/health         # OCR 상태 확인
```

### 검색 및 유사도
```
POST /api/resume/search/multi-hybrid    # 다중 하이브리드 검색
POST /api/resume/search/keyword         # 키워드 검색
POST /api/resume/similarity-check/{id}  # 유사도 체크
```

### GitHub 연동
```
GET /api/github/profile/{username}      # 프로필 조회
GET /api/github/repos/{username}        # 레포지토리 조회
```

## 🧪 테스트

### ReActAgent 테스트
```bash
curl -X POST "http://localhost:8000/api/react-agent/start-session" \
     -H "Content-Type: application/json" \
     -d '{"user_goal": "React 개발자 채용공고를 작성해주세요"}'
```

### PickTalk 챗봇 테스트
```bash
curl -X POST "http://localhost:8000/api/pick-chatbot/chat" \
     -H "Content-Type: application/json" \
     -d '{"message": "안녕하세요"}'
```

### 이력서 분석 테스트
```bash
curl -X POST "http://localhost:8000/api/ai-analysis/resume/analyze" \
     -H "Content-Type: application/json" \
     -d '{"applicant_id": "your_applicant_id"}'
```

## 📁 프로젝트 구조

```
hireme/
├── backend/                    # FastAPI 백엔드
│   ├── main.py                # 메인 서버
│   ├── requirements.txt       # Python 의존성
│   ├── modules/               # 핵심 모듈
│   │   ├── ai/               # AI 서비스
│   │   │   ├── services/     # ReActAgent, LangGraph
│   │   │   └── resume_analyzer.py
│   │   ├── core/             # 핵심 서비스
│   │   │   ├── services/     # MongoDB, 벡터, 유사도
│   │   │   └── models/       # 데이터 모델
│   │   ├── job_posting/      # 채용공고 에이전트
│   │   ├── resume/           # 이력서 처리
│   │   ├── cover_letter/     # 자기소개서 처리
│   │   └── portfolio/        # 포트폴리오 처리
│   ├── routers/              # API 라우터
│   │   ├── applicants.py     # 지원자 관리
│   │   ├── pick_chatbot.py   # PickTalk 챗봇
│   │   ├── react_agent_router.py # ReActAgent
│   │   └── upload.py         # 파일 업로드
│   └── chatbot/              # 챗봇 시스템
│       ├── core/             # 의도분류, 컨텍스트
│       └── routers/          # 챗봇 라우터
├── frontend/                  # React 프론트엔드
│   ├── package.json          # Node.js 의존성
│   ├── src/
│   │   ├── components/       # React 컴포넌트
│   │   │   ├── AgentComponents/ # AI 에이전트 UI
│   │   │   ├── ApplicantManagement/ # 지원자 관리
│   │   │   └── JobPostingAgent/ # 채용공고 에이전트
│   │   ├── pages/            # 페이지 컴포넌트
│   │   ├── services/         # API 서비스
│   │   └── utils/            # 유틸리티
│   └── public/               # 정적 파일
├── docs/                     # 문서
├── data/                     # 데이터 파일
├── install.bat              # Windows 설치 스크립트
├── install.sh               # Unix 설치 스크립트
├── run.bat                  # Windows 실행 스크립트
├── run.sh                   # Unix 실행 스크립트
└── README.md                # 이 파일
```

## 🔍 문제 해결

### MongoDB 연결 오류
```bash
# Windows
net start MongoDB

# macOS/Linux
sudo systemctl start mongod

# Docker
docker start mongodb
```

### OpenAI API 키 오류
- `.env` 파일에 올바른 API 키 설정 확인
- OpenAI 계정 크레딧 확인
- API 키 권한 확인

### 포트 충돌
```bash
# 다른 포트 사용
python backend/main.py --port 8001
```

### 메모리 부족
```bash
# 하이브리드 로딩 활성화
export FAST_STARTUP=true
export LAZY_LOADING_ENABLED=true
```

## 🎯 주요 특징

### 🧠 지능형 AI 시스템
- **ReAct 패턴**: 추론-액션-관찰을 통한 체계적 문제 해결
- **다중 에이전트**: 채용공고, 지원자 분석, 검색 등 전문화된 에이전트
- **컨텍스트 인식**: 대화 히스토리와 상황을 고려한 지능적 응답

### 🔍 고급 검색 시스템
- **하이브리드 검색**: 벡터, 텍스트, 키워드 검색의 결합
- **의미적 검색**: 임베딩 기반 의미적 유사도 검색
- **실시간 인덱싱**: 동적 인덱스 구축 및 업데이트

### 📊 종합적 분석
- **다면적 평가**: 이력서, 자기소개서, 포트폴리오 통합 분석
- **점수화 시스템**: 100점 만점의 객관적 평가
- **피드백 제공**: 구체적이고 실행 가능한 개선 제안

## 📞 지원

문제 발생 시:
1. 서버 실행 시 오류 메시지 확인
2. `.env` 파일 설정값 확인
3. MongoDB 서비스 실행 상태 확인
4. API 문서 참조: http://localhost:8000/docs

## 📚 추가 문서

- [빠른 시작 가이드](QUICK_START.md)
- [API 예시](API_EXAMPLES.md)
- [지원자 관리 가이드](APPLICANT_MANAGEMENT_GUIDE.md)
- [AI 아키텍처 분석](AI_ARCHITECTURE_ANALYSIS.md)

---

**🎉 설치 완료 후 http://localhost:8000/docs 에서 API 문서를 확인하세요!**

**Frontend는 http://localhost:3000 에서 실행됩니다.**
