"""
토큰 모니터링 설정 관리
"""
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Optional


@dataclass
class TokenMonitorConfig:
    """토큰 모니터링 설정 클래스"""

    # 데이터 저장 경로
    data_dir: str = field(default_factory=lambda: os.getenv("TOKEN_MONITOR_DATA_DIR", "data/token_usage"))

    # 토큰 한도 설정 (gpt-5-mini 기준)
    daily_limit: int = field(default_factory=lambda: int(os.getenv("TOKEN_DAILY_LIMIT", "2000000")))
    monthly_limit: int = field(default_factory=lambda: int(os.getenv("TOKEN_MONTHLY_LIMIT", "60000000")))
    per_minute_limit: int = field(default_factory=lambda: int(os.getenv("TOKEN_PER_MINUTE_LIMIT", "200000")))
    requests_per_minute: int = field(default_factory=lambda: int(os.getenv("REQUESTS_PER_MINUTE_LIMIT", "500")))

    # 알림 임계값
    warning_threshold: float = field(default_factory=lambda: float(os.getenv("TOKEN_WARNING_THRESHOLD", "0.8")))
    alert_threshold: float = field(default_factory=lambda: float(os.getenv("TOKEN_ALERT_THRESHOLD", "0.9")))

    # 자동 모니터링 설정
    auto_monitor_enabled: bool = field(default_factory=lambda: os.getenv("TOKEN_AUTO_MONITOR", "true").lower() == "true")
    monitor_interval: int = field(default_factory=lambda: int(os.getenv("TOKEN_MONITOR_INTERVAL", "300")))  # 5분
    auto_report: bool = field(default_factory=lambda: os.getenv("TOKEN_AUTO_REPORT", "true").lower() == "true")
    report_threshold: float = field(default_factory=lambda: float(os.getenv("TOKEN_REPORT_THRESHOLD", "0.1")))  # 10%

    # 웹훅 설정
    webhook_url: str = field(default_factory=lambda: os.getenv("TOKEN_WEBHOOK_URL", ""))

    # 모델별 비용 설정 (USD per 1K tokens)
    model_costs: Dict[str, Dict[str, float]] = field(default_factory=lambda: {
        "gpt-4o-mini": {"input": 0.00015, "output": 0.0006},
        "gpt-5": {"input": 0.0003, "output": 0.0012},
        "gpt-4o": {"input": 0.005, "output": 0.015},
        "gpt-4o-mini": {"input": 0.00015, "output": 0.0006},
        "gpt-3.5-turbo": {"input": 0.0015, "output": 0.002}
    })

    # 로깅 설정
    enable_file_logging: bool = field(default_factory=lambda: os.getenv("TOKEN_ENABLE_FILE_LOGGING", "true").lower() == "true")
    log_level: str = field(default_factory=lambda: os.getenv("TOKEN_LOG_LEVEL", "INFO"))

    # 데이터 보관 설정
    retention_days: int = field(default_factory=lambda: int(os.getenv("TOKEN_RETENTION_DAYS", "90")))  # 90일
    enable_compression: bool = field(default_factory=lambda: os.getenv("TOKEN_ENABLE_COMPRESSION", "false").lower() == "true")

    def __post_init__(self):
        """초기화 후 처리"""
        # 데이터 디렉토리 생성
        Path(self.data_dir).mkdir(parents=True, exist_ok=True)

        # 로그 디렉토리 생성
        log_dir = Path(self.data_dir) / "logs"
        log_dir.mkdir(exist_ok=True)

        # 알림 디렉토리 생성
        alert_dir = Path(self.data_dir) / "alerts"
        alert_dir.mkdir(exist_ok=True)

    def to_dict(self) -> Dict:
        """설정을 딕셔너리로 변환"""
        return {
            "data_dir": self.data_dir,
            "daily_limit": self.daily_limit,
            "monthly_limit": self.monthly_limit,
            "per_minute_limit": self.per_minute_limit,
            "requests_per_minute": self.requests_per_minute,
            "warning_threshold": self.warning_threshold,
            "alert_threshold": self.alert_threshold,
            "auto_monitor_enabled": self.auto_monitor_enabled,
            "monitor_interval": self.monitor_interval,
            "auto_report": self.auto_report,
            "report_threshold": self.report_threshold,
            "webhook_url": self.webhook_url,
            "model_costs": self.model_costs,
            "enable_file_logging": self.enable_file_logging,
            "log_level": self.log_level,
            "retention_days": self.retention_days,
            "enable_compression": self.enable_compression
        }

    def save_to_file(self, file_path: str):
        """설정을 파일로 저장"""
        import json
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, ensure_ascii=False, indent=2)

    @classmethod
    def load_from_file(cls, file_path: str) -> 'TokenMonitorConfig':
        """파일에서 설정 로드"""
        import json
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        config = cls()
        for key, value in data.items():
            if hasattr(config, key):
                setattr(config, key, value)

        return config

    def update_from_env(self):
        """환경 변수에서 설정 업데이트"""
        self.data_dir = os.getenv("TOKEN_MONITOR_DATA_DIR", self.data_dir)
        self.daily_limit = int(os.getenv("TOKEN_DAILY_LIMIT", str(self.daily_limit)))
        self.monthly_limit = int(os.getenv("TOKEN_MONTHLY_LIMIT", str(self.monthly_limit)))
        self.per_minute_limit = int(os.getenv("TOKEN_PER_MINUTE_LIMIT", str(self.per_minute_limit)))
        self.requests_per_minute = int(os.getenv("REQUESTS_PER_MINUTE_LIMIT", str(self.requests_per_minute)))
        self.warning_threshold = float(os.getenv("TOKEN_WARNING_THRESHOLD", str(self.warning_threshold)))
        self.alert_threshold = float(os.getenv("TOKEN_ALERT_THRESHOLD", str(self.alert_threshold)))
        self.auto_monitor_enabled = os.getenv("TOKEN_AUTO_MONITOR", str(self.auto_monitor_enabled)).lower() == "true"
        self.monitor_interval = int(os.getenv("TOKEN_MONITOR_INTERVAL", str(self.monitor_interval)))
        self.auto_report = os.getenv("TOKEN_AUTO_REPORT", str(self.auto_report)).lower() == "true"
        self.report_threshold = float(os.getenv("TOKEN_REPORT_THRESHOLD", str(self.report_threshold)))
        self.webhook_url = os.getenv("TOKEN_WEBHOOK_URL", self.webhook_url)
        self.enable_file_logging = os.getenv("TOKEN_ENABLE_FILE_LOGGING", str(self.enable_file_logging)).lower() == "true"
        self.log_level = os.getenv("TOKEN_LOG_LEVEL", self.log_level)
        self.retention_days = int(os.getenv("TOKEN_RETENTION_DAYS", str(self.retention_days)))
        self.enable_compression = os.getenv("TOKEN_ENABLE_COMPRESSION", str(self.enable_compression)).lower() == "true"
