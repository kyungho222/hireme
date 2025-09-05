# 🚀 PickTalk Backend 빠른 시작 가이드

## ⚡ 5분 만에 시작하기

### 1️⃣ 환경 변수 설정
```bash
# .env 파일 생성
cp .env.example .env

# .env 파일을 열어서 OpenAI API 키 설정
# OPENAI_API_KEY=your_actual_api_key_here
```

### 2️⃣ 설치 및 실행

#### Windows
```bash
# 자동 설치
install.bat

# 서버 시작
run.bat
```

#### macOS/Linux
```bash
# 자동 설치
./install.sh

# 서버 시작
./run.sh
```

### 3️⃣ 확인
브라우저에서 http://localhost:8000/docs 접속하여 API 문서 확인

## 🔧 수동 설치 (선택사항)

### 1. Python 가상환경 생성
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 2. 의존성 설치
```bash
pip install -r requirements.txt
```

### 3. 서버 실행
```bash
python main.py
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

## 📚 더 자세한 정보

- **전체 가이드**: [README.md](README.md)
- **API 예시**: [API_EXAMPLES.md](API_EXAMPLES.md)
- **API 문서**: http://localhost:8000/docs

## ❗ 문제 해결

### MongoDB 오류
```bash
# MongoDB 설치 및 실행
# Windows: https://www.mongodb.com/try/download/community
# macOS: brew install mongodb-community
# Linux: sudo apt-get install mongodb
```

### OpenAI API 키 오류
- `.env` 파일에 올바른 API 키가 설정되어 있는지 확인
- OpenAI 계정에 충분한 크레딧이 있는지 확인

### 포트 충돌
```bash
# 다른 포트 사용
python main.py --port 8001
```

---

**🎉 설치 완료! 이제 PickTalk Backend를 사용할 수 있습니다!**
