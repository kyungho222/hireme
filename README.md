# 🤖 PickTalk Backend - 핵심 AI 플랫폼

## 📋 개요

PickTalk Backend는 **ReActAgent**와 **픽톡 챗봇**을 포함한 핵심 AI 플랫폼입니다.

### ✨ 주요 기능
- **🤖 ReActAgent**: 추론-액션-관찰 루프를 통한 지능형 AI 에이전트
- **💬 PickTalk 챗봇**: 대화형 AI 어시스턴트
- **🔍 8개 핵심 툴**: 검색, AI분석, GitHub, MongoDB, 메일, 웹자동화, 파일관리, 네비게이션

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
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-5-mini
MONGODB_URI=mongodb://localhost:27017/hireme
HOST=0.0.0.0
PORT=8000
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
python main.py
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

### GitHub
```
GET /api/github/profile/{username}      # 프로필 조회
GET /api/github/repos/{username}        # 레포지토리 조회
```

## 🧪 테스트

### ReActAgent 테스트
```bash
curl -X POST "http://localhost:8000/api/react-agent/start-session" \
     -H "Content-Type: application/json" \
     -d '{"user_goal": "최신 AI 기술 트렌드를 검색해주세요"}'
```

### PickTalk 챗봇 테스트
```bash
curl -X POST "http://localhost:8000/api/pick-chatbot/chat" \
     -H "Content-Type: application/json" \
     -d '{"message": "안녕하세요"}'
```

## 📁 프로젝트 구조

```
picktalk-backend-standalone/
├── main.py                    # 메인 서버
├── requirements.txt           # 의존성
├── .env                      # 환경변수 (생성 필요)
├── modules/                  # 핵심 모듈
│   ├── ai/                   # ReActAgent & AI
│   ├── core/                 # 핵심 서비스
│   └── pick_chatbot/         # 픽톡 챗봇
├── routers/                  # API 라우터
└── services/                 # 서비스들
```

## 🔍 문제 해결

### MongoDB 연결 오류
```bash
# Windows
net start MongoDB

# macOS/Linux
sudo systemctl start mongod
```

### OpenAI API 키 오류
- `.env` 파일에 올바른 API 키 설정 확인
- OpenAI 계정 크레딧 확인

### 포트 충돌
```bash
python main.py --port 8001
```

## 📞 지원

문제 발생 시:
1. 서버 실행 시 오류 메시지 확인
2. `.env` 파일 설정값 확인
3. MongoDB 서비스 실행 상태 확인

---

**🎉 설치 완료 후 http://localhost:8000/docs 에서 API 문서를 확인하세요!**
