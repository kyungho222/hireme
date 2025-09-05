"""
토큰 사용량 모니터링 서비스
"""
import json
import os
import threading
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class TokenUsage:
    """토큰 사용량 정보"""
    timestamp: str
    model: str
    input_tokens: int
    output_tokens: int
    total_tokens: int
    cost_estimate: float
    endpoint: str
    user_id: Optional[str] = None

@dataclass
class TokenLimits:
    """토큰 한도 설정 (gpt-5-mini 기준)"""
    daily_limit: int = 2000000  # 일일 한도 (2M TPD)
    monthly_limit: int = 60000000  # 월간 한도 (2M * 30일)
    per_minute_limit: int = 200000  # 분당 한도 (200K TPM)
    requests_per_minute: int = 500  # 분당 요청 한도 (500 RPM)
    warning_threshold: float = 0.8  # 경고 임계값 (80%)
    alert_threshold: float = 0.9  # 알림 임계값 (90%)

class TokenMonitor:
    """토큰 사용량 모니터링 클래스"""

    def __init__(self, data_dir: str = "data/token_usage"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # 토큰 한도 설정 (gpt-5-mini 실제 한도 기준)
        self.limits = TokenLimits(
            daily_limit=int(os.getenv("TOKEN_DAILY_LIMIT", "2000000")),  # 2M TPD
            monthly_limit=int(os.getenv("TOKEN_MONTHLY_LIMIT", "60000000")),  # 2M * 30일
            per_minute_limit=int(os.getenv("TOKEN_PER_MINUTE_LIMIT", "200000")),  # 200K TPM
            requests_per_minute=int(os.getenv("REQUESTS_PER_MINUTE_LIMIT", "500")),  # 500 RPM
            warning_threshold=float(os.getenv("TOKEN_WARNING_THRESHOLD", "0.8")),
            alert_threshold=float(os.getenv("TOKEN_ALERT_THRESHOLD", "0.9"))
        )

        # 모델별 토큰 비용 (USD per 1K tokens)
        self.model_costs = {
            "gpt-4o-mini": {"input": 0.00015, "output": 0.0006},
            "gpt-4o": {"input": 0.005, "output": 0.015},
            "gpt-4o-mini": {"input": 0.00015, "output": 0.0006},
            "gpt-3.5-turbo": {"input": 0.0015, "output": 0.002}
        }

        self._lock = threading.Lock()

    def log_usage(self, usage: TokenUsage):
        """토큰 사용량 로깅"""
        with self._lock:
            # 일일 사용량 파일에 저장
            today = datetime.now().strftime("%Y-%m-%d")
            daily_file = self.data_dir / f"usage_{today}.json"

            # 기존 데이터 로드
            daily_usage = []
            if daily_file.exists():
                try:
                    with open(daily_file, 'r', encoding='utf-8') as f:
                        daily_usage = json.load(f)
                except:
                    daily_usage = []

            # 새 사용량 추가
            daily_usage.append(asdict(usage))

            # 파일에 저장
            with open(daily_file, 'w', encoding='utf-8') as f:
                json.dump(daily_usage, f, ensure_ascii=False, indent=2)

            # 월간 사용량도 업데이트
            self._update_monthly_usage(usage)

    def _update_monthly_usage(self, usage: TokenUsage):
        """월간 사용량 업데이트"""
        month = datetime.now().strftime("%Y-%m")
        monthly_file = self.data_dir / f"monthly_{month}.json"

        monthly_data = {"total_tokens": 0, "total_cost": 0.0, "usage_count": 0}
        if monthly_file.exists():
            try:
                with open(monthly_file, 'r', encoding='utf-8') as f:
                    monthly_data = json.load(f)
            except:
                pass

        monthly_data["total_tokens"] += usage.total_tokens
        monthly_data["total_cost"] += usage.cost_estimate
        monthly_data["usage_count"] += 1

        with open(monthly_file, 'w', encoding='utf-8') as f:
            json.dump(monthly_data, f, ensure_ascii=False, indent=2)

    def get_daily_usage(self, date: Optional[str] = None) -> Dict:
        """일일 사용량 조회"""
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")

        daily_file = self.data_dir / f"usage_{date}.json"

        if not daily_file.exists():
            return {
                "date": date,
                "total_tokens": 0,
                "total_cost": 0.0,
                "usage_count": 0,
                "models": {}
            }

        with open(daily_file, 'r', encoding='utf-8') as f:
            daily_usage = json.load(f)

        total_tokens = sum(usage["total_tokens"] for usage in daily_usage)
        total_cost = sum(usage["cost_estimate"] for usage in daily_usage)

        # 모델별 사용량 집계
        models = {}
        for usage in daily_usage:
            model = usage["model"]
            if model not in models:
                models[model] = {"tokens": 0, "cost": 0.0, "count": 0}
            models[model]["tokens"] += usage["total_tokens"]
            models[model]["cost"] += usage["cost_estimate"]
            models[model]["count"] += 1

        return {
            "date": date,
            "total_tokens": total_tokens,
            "total_cost": total_cost,
            "usage_count": len(daily_usage),
            "models": models,
            "limit_usage_percent": (total_tokens / self.limits.daily_limit) * 100 if self.limits.daily_limit > 0 else 0
        }

    def get_monthly_usage(self, month: Optional[str] = None) -> Dict:
        """월간 사용량 조회"""
        if month is None:
            month = datetime.now().strftime("%Y-%m")

        monthly_file = self.data_dir / f"monthly_{month}.json"

        if not monthly_file.exists():
            return {
                "month": month,
                "total_tokens": 0,
                "total_cost": 0.0,
                "usage_count": 0,
                "limit_usage_percent": 0.0
            }

        with open(monthly_file, 'r', encoding='utf-8') as f:
            monthly_data = json.load(f)

        monthly_data["limit_usage_percent"] = (monthly_data["total_tokens"] / self.limits.monthly_limit) * 100 if self.limits.monthly_limit > 0 else 0
        monthly_data["month"] = month

        return monthly_data

    def get_usage_summary(self) -> Dict:
        """사용량 요약 정보"""
        daily = self.get_daily_usage()
        monthly = self.get_monthly_usage()

        # 최근 7일 사용량
        recent_7days = []
        for i in range(7):
            date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
            day_usage = self.get_daily_usage(date)
            recent_7days.append(day_usage)

        return {
            "daily": daily,
            "monthly": monthly,
            "recent_7days": recent_7days,
            "limits": asdict(self.limits),
            "status": self._get_status(daily, monthly)
        }

    def _get_status(self, daily: Dict, monthly: Dict) -> str:
        """사용량 상태 확인"""
        daily_percent = daily.get("limit_usage_percent", 0)
        monthly_percent = monthly.get("limit_usage_percent", 0)

        if daily_percent >= self.limits.alert_threshold * 100 or monthly_percent >= self.limits.alert_threshold * 100:
            return "CRITICAL"
        elif daily_percent >= self.limits.warning_threshold * 100 or monthly_percent >= self.limits.warning_threshold * 100:
            return "WARNING"
        else:
            return "NORMAL"

    def calculate_cost(self, model: str, input_tokens: int, output_tokens: int) -> float:
        """토큰 비용 계산"""
        if model not in self.model_costs:
            model = "gpt-4o-mini"  # 기본값

        input_cost = (input_tokens / 1000) * self.model_costs[model]["input"]
        output_cost = (output_tokens / 1000) * self.model_costs[model]["output"]

        return input_cost + output_cost

    def create_usage_record(self, model: str, input_tokens: int, output_tokens: int,
                          endpoint: str, user_id: Optional[str] = None) -> TokenUsage:
        """사용량 레코드 생성"""
        return TokenUsage(
            timestamp=datetime.now().isoformat(),
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=input_tokens + output_tokens,
            cost_estimate=self.calculate_cost(model, input_tokens, output_tokens),
            endpoint=endpoint,
            user_id=user_id
        )

# 전역 모니터 인스턴스
token_monitor = TokenMonitor()
