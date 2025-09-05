# Token Monitor Module 설치 가이드

## 🚀 새 프로젝트에 설치하는 방법

### 1. 모듈 복사
```bash
# 이 폴더를 새 프로젝트에 복사
cp -r modules/token_monitor /path/to/your/new/project/
```

### 2. 필수 의존성 설치
```bash
# 새 프로젝트에서 실행
pip install openai python-dotenv requests
```

### 3. 환경 변수 설정 (.env 파일)
```env
# 기본 설정
TOKEN_MONITOR_DATA_DIR=data/token_usage
TOKEN_DAILY_LIMIT=2000000
TOKEN_MONTHLY_LIMIT=60000000
TOKEN_PER_MINUTE_LIMIT=200000
REQUESTS_PER_MINUTE_LIMIT=500

# 알림 설정
TOKEN_WARNING_THRESHOLD=0.8
TOKEN_ALERT_THRESHOLD=0.9
TOKEN_AUTO_MONITOR=true
TOKEN_MONITOR_INTERVAL=300
TOKEN_AUTO_REPORT=true
TOKEN_REPORT_THRESHOLD=0.1

# 웹훅 설정 (선택사항)
TOKEN_WEBHOOK_URL=https://hooks.slack.com/your-webhook-url

# 로깅 설정
TOKEN_ENABLE_FILE_LOGGING=true
TOKEN_LOG_LEVEL=INFO
TOKEN_RETENTION_DAYS=90
TOKEN_ENABLE_COMPRESSION=false
```

### 4. 기본 사용법
```python
# main.py 또는 app.py
from modules.token_monitor import TokenMonitor, TokenMonitorConfig, AutoTokenMonitor

# 설정 생성
config = TokenMonitorConfig()
monitor = TokenMonitor(config=config)
auto_monitor = AutoTokenMonitor(token_monitor=monitor, config=config)

# 자동 모니터링 시작
auto_monitor.start_monitoring()

# OpenAI API 호출 시 토큰 사용량 자동 기록
import openai
from modules.token_monitor import token_monitor

client = openai.OpenAI(api_key="your-api-key")
response = client.chat.completions.create(
    model="gpt-5-mini",
    messages=[{"role": "user", "content": "Hello"}],
    max_completion_tokens=100
)

# 토큰 사용량 자동 기록
if hasattr(response, 'usage') and response.usage:
    usage = token_monitor.create_usage_record(
        model="gpt-5-mini",
        input_tokens=response.usage.prompt_tokens,
        output_tokens=response.usage.completion_tokens,
        endpoint="chat_completion",
        project_id="your_project_name"
    )
    token_monitor.log_usage(usage)
```

### 5. FastAPI와 함께 사용
```python
from fastapi import FastAPI
from modules.token_monitor import token_monitor, auto_monitor

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    auto_monitor.start_monitoring()

@app.on_event("shutdown")
async def shutdown_event():
    auto_monitor.stop_monitoring()

@app.get("/token-usage")
async def get_token_usage():
    return token_monitor.get_usage_summary()
```

### 6. CLI 도구 사용
```bash
# 토큰 사용량 확인
python -c "from modules.token_monitor import token_monitor; print(token_monitor.get_usage_summary())"

# 또는 별도 스크립트 생성
python check_token_usage.py summary
```

## 📁 필요한 파일들

### 필수 파일
- `modules/token_monitor/__init__.py`
- `modules/token_monitor/core/config.py`
- `modules/token_monitor/core/monitor.py`
- `modules/token_monitor/core/auto_monitor.py`

### 선택적 파일
- `modules/token_monitor/utils/export.py` (데이터 내보내기)
- `modules/token_monitor/utils/import_.py` (데이터 가져오기)
- `modules/token_monitor/examples/standalone_example.py` (예제)

## ⚠️ 주의사항

1. **Python 경로**: 모듈을 import할 때 Python 경로에 추가해야 할 수 있습니다.
2. **데이터 디렉토리**: `TOKEN_MONITOR_DATA_DIR`에 지정된 디렉토리가 자동으로 생성됩니다.
3. **권한**: 데이터 디렉토리에 쓰기 권한이 필요합니다.
4. **환경 변수**: 모든 설정은 환경 변수로 제어되므로 .env 파일을 반드시 설정하세요.

## 🔧 문제 해결

### ImportError 발생 시
```python
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from modules.token_monitor import token_monitor
```

### 데이터 디렉토리 권한 문제
```bash
# Linux/Mac
chmod 755 data/token_usage

# Windows
# 관리자 권한으로 실행
```

### 환경 변수 로드 문제
```python
from dotenv import load_dotenv
load_dotenv()  # .env 파일 로드
```

## 📞 지원

문제가 발생하면 이슈를 등록하거나 문서를 참고하세요.
