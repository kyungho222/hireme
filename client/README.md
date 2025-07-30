# HireMe Client

HireMe 클라이언트 애플리케이션입니다. 구직자와 구인자가 만나는 플랫폼으로, 채용공고 작성, 지원서 관리, 포트폴리오 분석 등의 기능을 제공합니다.

## 🚀 새로운 기능: AI 챗봇 기반 채용공고 작성

### 📍 경로: `/job-posting`

AI 챗봇과 함께 채용공고를 작성할 수 있는 새로운 페이지가 추가되었습니다.

#### 주요 기능:
- **AI 챗봇 인터페이스**: 플로팅 챗봇을 통해 단계별로 채용공고 정보 입력
- **실시간 필드 업데이트**: 챗봇과의 대화를 통해 입력된 정보가 실시간으로 화면에 표시
- **채용공고 작성 가이드**: 각 필드별 작성 가이드 제공
- **완료 상태 관리**: 모든 필수 정보 입력 완료 시 완료 상태 표시

#### 지원하는 채용공고 필드:
- 채용공고 제목
- 직무 설명
- 자격 요건
- 우대 사항
- 복리후생
- 근무지
- 채용 마감일

## 🛠️ 기술 스택

### Frontend
- React 18
- TypeScript
- Tailwind CSS
- React Router DOM
- Axios
- FontAwesome

### Backend
- FastAPI
- MongoDB (Motor)
- Google Generative AI (Gemini)
- Python 3.9+

## 📦 설치 및 실행

### 1. 의존성 설치

```bash
# Frontend 의존성 설치
cd frontend
npm install

# Backend 의존성 설치
cd ../backend
pip install -r requirements.txt
```

### 2. 환경 변수 설정

Backend 디렉토리에 `.env` 파일을 생성하고 다음 내용을 추가하세요:

```env
# MongoDB 연결 설정
MONGODB_URI=mongodb://admin:password@mongodb-client:27017/hireme-client?authSource=admin

# Gemini API 키 (실제 API 키로 교체하세요)
GEMINI_API_KEY=your_gemini_api_key_here
```

### 3. 애플리케이션 실행

```bash
# Frontend 실행 (포트 3000)
cd frontend
npm start

# Backend 실행 (포트 8001)
cd ../backend
python main.py
```

## 🌐 접속 방법

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8001
- **채용공고 작성**: http://localhost:3000/job-posting

## 🔧 API 엔드포인트

### 챗봇 API
- `POST /api/chatbot/start`: 챗봇 세션 시작
- `POST /api/chatbot/ask`: 챗봇과 대화

### 기존 API
- `GET /api/jobs`: 채용공고 목록 조회
- `POST /api/jobs`: 채용공고 생성
- `GET /api/jobs/{job_id}`: 특정 채용공고 조회
- `GET /api/portfolios`: 포트폴리오 목록 조회
- `POST /api/portfolios`: 포트폴리오 생성
- `GET /api/applications`: 지원서 목록 조회
- `POST /api/applications`: 지원서 생성

## 🎯 사용 방법

### 채용공고 작성하기

1. **페이지 접속**: http://localhost:3000/job-posting
2. **챗봇 시작**: 오른쪽 하단의 💬 아이콘 클릭
3. **단계별 입력**: 챗봇의 질문에 따라 채용공고 정보 입력
4. **실시간 확인**: 입력된 정보가 왼쪽 패널에 실시간으로 표시
5. **완료**: 모든 필수 정보 입력 완료 시 완료 상태 표시

### 챗봇 사용 팁

- **자연스러운 대화**: 챗봇과 자연스럽게 대화하세요
- **추가 질문**: 궁금한 점이 있으면 언제든 질문하세요
- **수정 요청**: 입력한 내용을 수정하고 싶으면 "다시 입력해줘"라고 말하세요
- **완료 확인**: 모든 정보 입력 후 "완료"라고 말하면 다음 단계로 진행됩니다

## 🔍 주요 페이지

- **홈**: `/` - 메인 페이지
- **채용공고 목록**: `/jobs` - 등록된 채용공고 목록
- **채용공고 작성**: `/job-posting` - AI 챗봇 기반 채용공고 작성
- **지원서**: `/applications` - 지원서 관리
- **포트폴리오**: `/portfolio` - 포트폴리오 분석
- **인재추천**: `/recommendations` - 인재 추천 시스템
- **면접**: `/interviews` - 면접 관리

## 🐛 문제 해결

### 챗봇이 응답하지 않는 경우
1. Backend 서버가 실행 중인지 확인
2. Gemini API 키가 올바르게 설정되었는지 확인
3. 브라우저 개발자 도구에서 네트워크 오류 확인

### 스타일이 적용되지 않는 경우
1. Tailwind CSS가 올바르게 설치되었는지 확인
2. `npm install`을 다시 실행
3. 브라우저 캐시 삭제

## 📝 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.
