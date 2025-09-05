# 🚀 새 프로젝트에 Token Monitor 복사하기

## 📋 복사 방법

### 1. 폴더 복사
```bash
# 현재 프로젝트에서
cp -r modules/token_monitor/ /path/to/new/project/modules/

# 또는 Windows에서
xcopy modules\token_monitor\ /path/to/new/project/modules\token_monitor\ /E /I
```

### 2. 의존성 설치
```bash
# 새 프로젝트에서
pip install -r modules/token_monitor/requirements.txt
```

### 3. 환경 변수 설정
```bash
# .env 파일에 추가
echo "TOKEN_AUTO_MONITOR=true" >> .env
echo "TOKEN_DAILY_LIMIT=2000000" >> .env
echo "TOKEN_MONTHLY_LIMIT=60000000" >> .env
```

## ✅ 자동 설치 확인

### 1. 기본 기능 테스트
```python
# test_token_monitor.py
from modules.token_monitor import token_monitor

# 사용량 기록
usage = token_monitor.create_usage_record(
    model="gpt-5-mini",
    input_tokens=100,
    output_tokens=50,
    endpoint="test"
)
token_monitor.log_usage(usage)

# 사용량 조회
summary = token_monitor.get_usage_summary()
print(f"오늘 사용량: {summary['daily']['total_tokens']} 토큰")
```

### 2. 자동 모니터링 테스트
```python
# test_auto_monitor.py
from modules.token_monitor import auto_monitor

# 자동 모니터링 시작
auto_monitor.start_monitoring()
print("✅ 자동 모니터링 시작됨")

# 5초 후 중지
import time
time.sleep(5)
auto_monitor.stop_monitoring()
print("✅ 자동 모니터링 중지됨")
```

### 3. 다중 프로젝트 통합 테스트
```python
# test_multi_project.py
from modules.token_monitor import TokenUsageAggregator

# 여러 프로젝트 데이터 통합
aggregator = TokenUsageAggregator([
    "project_a/data/token_usage",
    "project_b/data/token_usage"
])

summary = aggregator.get_aggregated_summary()
print(f"통합 사용량: {summary['daily']['total_tokens']} 토큰")
```

## 🔧 설정 커스터마이징

### 1. 데이터 저장 경로 변경
```python
from modules.token_monitor import TokenMonitorConfig, TokenMonitor

config = TokenMonitorConfig(
    data_dir="custom/path/token_usage",
    daily_limit=5000000,  # 5M 토큰
    monthly_limit=150000000  # 150M 토큰
)

monitor = TokenMonitor(config=config)
```

### 2. 자동 모니터링 설정
```python
from modules.token_monitor import AutoTokenMonitor, TokenMonitorConfig

config = TokenMonitorConfig(
    auto_monitor=True,
    monitor_interval=600,  # 10분마다 체크
    warning_threshold=0.7,  # 70%에서 경고
    alert_threshold=0.9   # 90%에서 알림
)

auto_monitor = AutoTokenMonitor(token_monitor, config)
auto_monitor.start_monitoring()
```

## 📊 사용 예제

### 1. FastAPI 통합
```python
from fastapi import FastAPI
from modules.token_monitor import token_monitor, auto_monitor

app = FastAPI()

@app.on_event("startup")
async def startup():
    auto_monitor.start_monitoring()

@app.on_event("shutdown")
async def shutdown():
    auto_monitor.stop_monitoring()

@app.get("/token-usage")
async def get_usage():
    return token_monitor.get_usage_summary()
```

### 2. OpenAI API 래퍼
```python
import openai
from modules.token_monitor import token_monitor

class MonitoredOpenAI:
    def __init__(self, api_key):
        self.client = openai.OpenAI(api_key=api_key)

    async def chat_completion(self, messages, model="gpt-5-mini"):
        response = await self.client.chat.completions.create(
            model=model,
            messages=messages,
            max_completion_tokens=500
        )

        # 사용량 기록
        if hasattr(response, 'usage') and response.usage:
            usage = token_monitor.create_usage_record(
                model=model,
                input_tokens=response.usage.prompt_tokens,
                output_tokens=response.usage.completion_tokens,
                endpoint="chat_completion"
            )
            token_monitor.log_usage(usage)

        return response
```

## 🎯 완전 자동화

### 1. 환경 변수만 설정하면 자동 작동
```env
# .env
TOKEN_AUTO_MONITOR=true
TOKEN_DAILY_LIMIT=2000000
TOKEN_MONTHLY_LIMIT=60000000
TOKEN_WARNING_THRESHOLD=0.8
TOKEN_ALERT_THRESHOLD=0.9
```

### 2. 코드에서 자동 사용
```python
# 자동으로 모니터링 시작
from modules.token_monitor import auto_monitor
auto_monitor.start_monitoring()

# 자동으로 사용량 기록
from modules.token_monitor import token_monitor
# ... API 호출 후 자동으로 log_usage() 호출
```

## ✅ 확인 사항

- [ ] `modules/token_monitor/` 폴더 복사 완료
- [ ] `requirements.txt` 의존성 설치 완료
- [ ] `.env` 환경 변수 설정 완료
- [ ] 기본 기능 테스트 통과
- [ ] 자동 모니터링 테스트 통과
- [ ] 데이터 저장 경로 확인

## 🚨 문제 해결

### 1. Import 오류
```bash
# Python 경로 확인
python -c "import sys; print(sys.path)"

# 모듈 경로 추가
export PYTHONPATH="${PYTHONPATH}:/path/to/project"
```

### 2. 권한 오류
```bash
# 데이터 디렉토리 권한 설정
chmod 755 data/token_usage
```

### 3. 의존성 오류
```bash
# 의존성 재설치
pip install --force-reinstall -r modules/token_monitor/requirements.txt
```

이제 `modules/token_monitor/` 폴더만 복사하면 모든 기능이 자동으로 작동합니다! 🎉
