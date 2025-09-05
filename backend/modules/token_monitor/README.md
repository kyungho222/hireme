# Token Monitor Module

다른 프로젝트에서도 재사용 가능한 독립적인 토큰 사용량 모니터링 시스템입니다.

## 🚀 주요 기능

- **실시간 토큰 사용량 추적**: 모든 OpenAI API 호출 자동 모니터링
- **다중 프로젝트 지원**: 프로젝트별 독립적인 사용량 추적
- **자동 알림 시스템**: 한도 초과 시 콘솔/웹훅 알림
- **데이터 내보내기/가져오기**: JSON, CSV, ZIP 형식 지원
- **설정 관리**: 환경변수 또는 설정 파일로 유연한 구성
- **데이터 보관**: 자동 정리 및 압축 옵션

## 📦 설치 및 사용

### 1. 모듈 복사
```bash
# 이 모듈을 다른 프로젝트에 복사
cp -r modules/token_monitor /path/to/your/project/
```

### 2. 필수 패키지 설치
```bash
pip install openai python-dotenv requests
```

### 3. 환경 변수 설정 (.env 파일)
```env
# OpenAI API 키
OPENAI_API_KEY=your-openai-api-key-here
OPENAI_MODEL=gpt-5-mini

# 토큰 한도 설정 (gpt-5-mini 기준)
TOKEN_DAILY_LIMIT=2000000
TOKEN_MONTHLY_LIMIT=60000000
TOKEN_PER_MINUTE_LIMIT=200000
REQUESTS_PER_MINUTE_LIMIT=500

# 모니터링 설정
TOKEN_AUTO_MONITOR=true
TOKEN_MONITOR_INTERVAL=300
TOKEN_WARNING_THRESHOLD=0.8
TOKEN_ALERT_THRESHOLD=0.9

# 데이터 저장 경로
TOKEN_MONITOR_DATA_DIR=data/token_usage

# 전역 모니터링 설정 (여러 프로젝트 통합 시)
GLOBAL_TOKEN_DAILY_LIMIT=10000000
GLOBAL_TOKEN_MONTHLY_LIMIT=300000000
```

### 4. 기본 사용법
```python
# 1. 모듈 import
from modules.token_monitor import TokenMonitor, TokenMonitorConfig, AutoTokenMonitor
from dotenv import load_dotenv
import openai

# 2. 환경 변수 로드
load_dotenv()

# 3. 모니터 생성
config = TokenMonitorConfig()
monitor = TokenMonitor(config=config)

# 4. OpenAI API 호출 시 토큰 사용량 자동 기록
client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

async def chat_with_monitoring(messages):
    response = await client.chat.completions.create(
        model="gpt-5-mini",
        messages=messages,
        max_completion_tokens=500
    )

    # 토큰 사용량 자동 기록
    if hasattr(response, 'usage') and response.usage:
        usage = monitor.create_usage_record(
            model="gpt-5-mini",
            input_tokens=response.usage.prompt_tokens,
            output_tokens=response.usage.completion_tokens,
            endpoint="chat_completion",
            project_id="my_project"
        )
        monitor.log_usage(usage)

    return response

# 5. 사용량 조회
summary = monitor.get_usage_summary()
print(f"오늘 사용량: {summary['daily']['total_tokens']} 토큰")
print(f"상태: {summary['status']}")
```

### 5. 자동 모니터링
```python
# 자동 모니터링 시작
auto_monitor = AutoTokenMonitor(token_monitor=monitor, config=config)
auto_monitor.start_monitoring()

# 모니터링 중지
auto_monitor.stop_monitoring()
```

### 6. FastAPI와 함께 사용
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

### 7. CLI로 사용량 확인
```bash
# Python 스크립트로 확인
python -c "from modules.token_monitor import token_monitor; print(token_monitor.get_usage_summary())"

# 또는 별도 스크립트 생성
python quick_start.py
```

### 8. 여러 프로젝트 통합 사용법
```python
from modules.token_monitor import TokenUsageAggregator, GlobalTokenMonitor, TokenSyncService

# 여러 프로젝트 데이터 통합
projects_data_dirs = [
    "project_a/data/token_usage",
    "project_b/data/token_usage",
    "project_c/data/token_usage"
]

aggregator = TokenUsageAggregator(projects_data_dirs)
daily_summary = aggregator.aggregate_daily_usage()
print(f"전체 사용량: {daily_summary['total_tokens']:,} 토큰")

# 전역 모니터링
global_monitor = GlobalTokenMonitor()
global_summary = global_monitor.get_global_summary()

# 자동 동기화 서비스
sync_service = TokenSyncService(
    projects_config={
        "project_a": "project_a/data/token_usage",
        "project_b": "project_b/data/token_usage"
    },
    sync_interval=300,  # 5분마다 동기화
    global_monitor=True
)
sync_service.start_sync()
```

## ⚙️ 환경 변수 설정

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

# 웹훅 설정
TOKEN_WEBHOOK_URL=https://hooks.slack.com/your-webhook-url

# 로깅 설정
TOKEN_ENABLE_FILE_LOGGING=true
TOKEN_LOG_LEVEL=INFO
TOKEN_RETENTION_DAYS=90
TOKEN_ENABLE_COMPRESSION=false
```

## 📊 API 엔드포인트

FastAPI와 함께 사용할 때:

```python
from fastapi import FastAPI
from modules.token_monitor import token_monitor

app = FastAPI()

@app.get("/token-usage")
async def get_token_usage():
    return token_monitor.get_usage_summary()

@app.get("/token-status")
async def get_token_status():
    summary = token_monitor.get_usage_summary()
    return {
        "status": summary["status"],
        "daily_usage": summary["daily"]["limit_usage_percent"]
    }
```

## 📁 데이터 구조

```
data/token_usage/
├── usage_2025-09-05.json      # 일일 사용량
├── monthly_2025-09.json       # 월간 집계
├── project_my_project.json    # 프로젝트별 사용량
├── logs/                      # 로그 파일
│   └── alerts_2025-09-05.log
└── config.json               # 설정 파일
```

## 🔧 고급 기능

### 데이터 내보내기
```python
from modules.token_monitor.utils.export import TokenDataExporter

exporter = TokenDataExporter(monitor)
exporter.export_to_json("2025-09-01", "2025-09-05", "usage_report.json")
exporter.export_to_csv("2025-09-01", "2025-09-05", "usage_report.csv")
exporter.export_to_zip("2025-09-01", "2025-09-05", "usage_report.zip")
```

### 데이터 가져오기
```python
from modules.token_monitor.utils.import_ import TokenDataImporter

importer = TokenDataImporter(monitor)
importer.import_from_json("usage_report.json", merge=True)
importer.import_from_csv("usage_report.csv", merge=True)
```

### 설정 관리
```python
# 설정 저장
config.save_to_file("my_config.json")

# 설정 로드
config = TokenMonitorConfig.load_from_file("my_config.json")

# 환경변수에서 업데이트
config.update_from_env()
```

## 🎯 모델별 한도 (gpt-5-mini 기준)

- **TPM (Tokens Per Minute)**: 200,000 토큰/분
- **RPM (Requests Per Minute)**: 500 요청/분
- **TPD (Tokens Per Day)**: 2,000,000 토큰/일

## 📈 모니터링 상태

- **NORMAL**: 정상 사용량
- **WARNING**: 경고 수준 (80% 도달)
- **CRITICAL**: 위험 수준 (90% 도달)

## 🔗 통합 예제

```python
# OpenAI 서비스와 통합
import openai
from modules.token_monitor import token_monitor

class MyOpenAIService:
    def __init__(self):
        self.client = openai.OpenAI(api_key="your-api-key")

    async def chat_completion(self, messages):
        response = await self.client.chat.completions.create(
            model="gpt-5-mini",
            messages=messages,
            max_completion_tokens=500
        )

        # 토큰 사용량 자동 기록
        if hasattr(response, 'usage') and response.usage:
            usage = token_monitor.create_usage_record(
                model="gpt-5-mini",
                input_tokens=response.usage.prompt_tokens,
                output_tokens=response.usage.completion_tokens,
                endpoint="chat_completion",
                project_id="my_project"
            )
            token_monitor.log_usage(usage)

        return response
```

## 📝 라이선스

이 모듈은 MIT 라이선스 하에 배포됩니다.

## 🤝 기여

버그 리포트나 기능 제안은 이슈로 등록해주세요.
