# 📚 PickTalk Backend API 사용 예시

## 🚀 빠른 시작

### 1. 서버 시작
```bash
# Windows
run.bat

# macOS/Linux
./run.sh
```

### 2. API 문서 확인
브라우저에서 http://localhost:8000/docs 접속

## 🤖 ReActAgent API

### 세션 시작
```bash
curl -X POST "http://localhost:8000/api/react-agent/start-session" \
     -H "Content-Type: application/json" \
     -d '{
       "user_goal": "React 개발자 채용공고를 작성해주세요"
     }'
```

### 작업 처리
```bash
curl -X POST "http://localhost:8000/api/react-agent/process-task" \
     -H "Content-Type: application/json" \
     -d '{
       "session_id": "your_session_id",
       "user_goal": "지원자 목록을 조회해주세요"
     }'
```

## 💬 PickTalk 챗봇 API

### 기본 대화
```bash
curl -X POST "http://localhost:8000/api/pick-chatbot/chat" \
     -H "Content-Type: application/json" \
     -d '{
       "message": "안녕하세요, 채용공고를 작성하고 싶습니다"
     }'
```

### 세션 기반 대화
```bash
curl -X POST "http://localhost:8000/api/pick-chatbot/chat" \
     -H "Content-Type: application/json" \
     -d '{
       "message": "React 개발자 채용공고를 작성해주세요",
       "session_id": "your_session_id"
     }'
```

## 📝 채용공고 API

### 채용공고 목록 조회
```bash
curl -X GET "http://localhost:8000/api/job-postings/"
```

### 채용공고 생성
```bash
curl -X POST "http://localhost:8000/api/job-postings/" \
     -H "Content-Type: application/json" \
     -d '{
       "title": "React 개발자",
       "company": "우리 회사",
       "position": "프론트엔드 개발자",
       "description": "React를 사용한 웹 애플리케이션 개발",
       "requirements": ["React", "JavaScript", "TypeScript"],
       "benefits": ["경쟁력 있는 급여", "유연한 근무시간"]
     }'
```

### 채용공고 수정
```bash
curl -X PUT "http://localhost:8000/api/job-postings/{job_id}" \
     -H "Content-Type: application/json" \
     -d '{
       "title": "시니어 React 개발자",
       "description": "시니어 레벨의 React 개발자 모집"
     }'
```

## 👥 지원자 관리 API

### 지원자 목록 조회
```bash
curl -X GET "http://localhost:8000/api/applicants/"
```

### 지원자 생성
```bash
curl -X POST "http://localhost:8000/api/applicants/" \
     -H "Content-Type: application/json" \
     -d '{
       "name": "김개발",
       "email": "kim@example.com",
       "position": "React 개발자",
       "skills": ["React", "JavaScript", "Node.js"],
       "experience": "3년",
       "resume": "React 개발 경험 3년..."
     }'
```

### 지원자 상세 조회
```bash
curl -X GET "http://localhost:8000/api/applicants/{applicant_id}"
```

## 📊 포트폴리오 API

### 지원자 포트폴리오 조회
```bash
curl -X GET "http://localhost:8000/api/portfolios/applicant/{applicant_id}"
```

## 📄 PDF OCR API

### PDF 업로드 및 분석
```bash
curl -X POST "http://localhost:8000/api/pdf-ocr/upload" \
     -F "file=@resume.pdf"
```

## 🏢 회사 인재상 API

### 회사 인재상 생성
```bash
curl -X POST "http://localhost:8000/api/company-culture/" \
     -H "Content-Type: application/json" \
     -d '{
       "company_name": "우리 회사",
       "culture_values": ["혁신", "협업", "성장"],
       "ideal_candidate": "창의적이고 협업을 중시하는 개발자"
     }'
```

## 🔧 JavaScript/React 예시

### API 서비스 클래스
```javascript
class PickTalkAPI {
  constructor(baseURL = 'http://localhost:8000/api') {
    this.baseURL = baseURL;
  }

  // ReActAgent 세션 시작
  async startReactSession(userGoal) {
    const response = await fetch(`${this.baseURL}/react-agent/start-session`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_goal: userGoal })
    });
    return response.json();
  }

  // ReActAgent 작업 처리
  async processReactTask(sessionId, userGoal) {
    const response = await fetch(`${this.baseURL}/react-agent/process-task`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        session_id: sessionId,
        user_goal: userGoal
      })
    });
    return response.json();
  }

  // PickTalk 챗봇 대화
  async chat(message, sessionId = null) {
    const body = { message };
    if (sessionId) body.session_id = sessionId;

    const response = await fetch(`${this.baseURL}/pick-chatbot/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body)
    });
    return response.json();
  }

  // 채용공고 목록 조회
  async getJobPostings() {
    const response = await fetch(`${this.baseURL}/job-postings/`);
    return response.json();
  }

  // 채용공고 생성
  async createJobPosting(jobData) {
    const response = await fetch(`${this.baseURL}/job-postings/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(jobData)
    });
    return response.json();
  }

  // 지원자 목록 조회
  async getApplicants() {
    const response = await fetch(`${this.baseURL}/applicants/`);
    return response.json();
  }
}

// 사용 예시
const api = new PickTalkAPI();

// ReActAgent 사용
async function useReactAgent() {
  const session = await api.startReactSession("React 개발자 채용공고 작성");
  const result = await api.processReactTask(session.session_id, "지원자 목록 조회");
  console.log(result);
}

// PickTalk 챗봇 사용
async function usePickTalk() {
  const response = await api.chat("안녕하세요, 채용공고를 작성하고 싶습니다");
  console.log(response);
}
```

## 🐍 Python 예시

```python
import requests
import json

class PickTalkAPI:
    def __init__(self, base_url="http://localhost:8000/api"):
        self.base_url = base_url

    def start_react_session(self, user_goal):
        response = requests.post(
            f"{self.base_url}/react-agent/start-session",
            json={"user_goal": user_goal}
        )
        return response.json()

    def process_react_task(self, session_id, user_goal):
        response = requests.post(
            f"{self.base_url}/react-agent/process-task",
            json={"session_id": session_id, "user_goal": user_goal}
        )
        return response.json()

    def chat(self, message, session_id=None):
        data = {"message": message}
        if session_id:
            data["session_id"] = session_id

        response = requests.post(
            f"{self.base_url}/pick-chatbot/chat",
            json=data
        )
        return response.json()

    def get_job_postings(self):
        response = requests.get(f"{self.base_url}/job-postings/")
        return response.json()

    def create_job_posting(self, job_data):
        response = requests.post(
            f"{self.base_url}/job-postings/",
            json=job_data
        )
        return response.json()

# 사용 예시
api = PickTalkAPI()

# ReActAgent 사용
session = api.start_react_session("React 개발자 채용공고 작성")
result = api.process_react_task(session["session_id"], "지원자 목록 조회")
print(result)

# PickTalk 챗봇 사용
response = api.chat("안녕하세요, 채용공고를 작성하고 싶습니다")
print(response)
```

## 🔍 오류 처리

### 일반적인 HTTP 상태 코드
- `200`: 성공
- `400`: 잘못된 요청
- `401`: 인증 필요
- `404`: 리소스 없음
- `500`: 서버 오류

### 오류 응답 예시
```json
{
  "detail": "OpenAI API 키가 설정되지 않았습니다",
  "error_code": "MISSING_API_KEY"
}
```

## 📝 참고사항

1. **API 키 설정**: `.env` 파일에 `OPENAI_API_KEY`를 반드시 설정하세요
2. **MongoDB 실행**: API 사용 전에 MongoDB가 실행 중인지 확인하세요
3. **CORS 설정**: 프론트엔드에서 API 호출 시 CORS 오류가 발생할 수 있습니다
4. **세션 관리**: ReActAgent는 세션 기반으로 동작합니다
5. **비동기 처리**: 대부분의 API는 비동기로 처리되므로 응답 시간이 다를 수 있습니다
