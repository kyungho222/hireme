"""
여러 프로젝트의 토큰 사용량을 통합하는 유틸리티
"""
import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

from ..core.config import TokenMonitorConfig
from ..core.monitor import TokenMonitor


class TokenUsageAggregator:
    """여러 프로젝트의 토큰 사용량을 통합하는 클래스"""

    def __init__(self, projects_data_dirs: List[str], aggregated_data_dir: str = "data/aggregated_usage"):
        self.projects_data_dirs = projects_data_dirs
        self.aggregated_data_dir = Path(aggregated_data_dir)
        self.aggregated_data_dir.mkdir(parents=True, exist_ok=True)

    def aggregate_daily_usage(self, date: Optional[str] = None) -> Dict:
        """여러 프로젝트의 일일 사용량을 통합"""
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")

        aggregated_data = {
            "date": date,
            "total_tokens": 0,
            "total_cost": 0.0,
            "usage_count": 0,
            "models": {},
            "projects": {},
            "endpoints": {}
        }

        for project_dir in self.projects_data_dirs:
            project_path = Path(project_dir)
            if not project_path.exists():
                continue

            daily_file = project_path / f"usage_{date}.json"
            if not daily_file.exists():
                continue

            try:
                with open(daily_file, 'r', encoding='utf-8') as f:
                    daily_usage = json.load(f)

                project_name = project_path.name

                for usage in daily_usage:
                    # 총합 계산
                    aggregated_data["total_tokens"] += usage.get("total_tokens", 0)
                    aggregated_data["total_cost"] += usage.get("cost_estimate", 0.0)
                    aggregated_data["usage_count"] += 1

                    # 모델별 집계
                    model = usage.get("model", "unknown")
                    if model not in aggregated_data["models"]:
                        aggregated_data["models"][model] = {"tokens": 0, "cost": 0.0, "count": 0}
                    aggregated_data["models"][model]["tokens"] += usage.get("total_tokens", 0)
                    aggregated_data["models"][model]["cost"] += usage.get("cost_estimate", 0.0)
                    aggregated_data["models"][model]["count"] += 1

                    # 프로젝트별 집계
                    if project_name not in aggregated_data["projects"]:
                        aggregated_data["projects"][project_name] = {"tokens": 0, "cost": 0.0, "count": 0}
                    aggregated_data["projects"][project_name]["tokens"] += usage.get("total_tokens", 0)
                    aggregated_data["projects"][project_name]["cost"] += usage.get("cost_estimate", 0.0)
                    aggregated_data["projects"][project_name]["count"] += 1

                    # 엔드포인트별 집계
                    endpoint = usage.get("endpoint", "unknown")
                    if endpoint not in aggregated_data["endpoints"]:
                        aggregated_data["endpoints"][endpoint] = {"tokens": 0, "cost": 0.0, "count": 0}
                    aggregated_data["endpoints"][endpoint]["tokens"] += usage.get("total_tokens", 0)
                    aggregated_data["endpoints"][endpoint]["cost"] += usage.get("cost_estimate", 0.0)
                    aggregated_data["endpoints"][endpoint]["count"] += 1

            except Exception as e:
                print(f"❌ 프로젝트 {project_dir} 처리 오류: {e}")

        return aggregated_data

    def aggregate_monthly_usage(self, month: Optional[str] = None) -> Dict:
        """여러 프로젝트의 월간 사용량을 통합"""
        if month is None:
            month = datetime.now().strftime("%Y-%m")

        aggregated_data = {
            "month": month,
            "total_tokens": 0,
            "total_cost": 0.0,
            "usage_count": 0,
            "projects": {}
        }

        for project_dir in self.projects_data_dirs:
            project_path = Path(project_dir)
            if not project_path.exists():
                continue

            monthly_file = project_path / f"monthly_{month}.json"
            if not monthly_file.exists():
                continue

            try:
                with open(monthly_file, 'r', encoding='utf-8') as f:
                    monthly_usage = json.load(f)

                project_name = project_path.name

                # 총합 계산
                aggregated_data["total_tokens"] += monthly_usage.get("total_tokens", 0)
                aggregated_data["total_cost"] += monthly_usage.get("total_cost", 0.0)
                aggregated_data["usage_count"] += monthly_usage.get("usage_count", 0)

                # 프로젝트별 집계
                aggregated_data["projects"][project_name] = {
                    "tokens": monthly_usage.get("total_tokens", 0),
                    "cost": monthly_usage.get("total_cost", 0.0),
                    "count": monthly_usage.get("usage_count", 0)
                }

            except Exception as e:
                print(f"❌ 프로젝트 {project_dir} 처리 오류: {e}")

        return aggregated_data

    def save_aggregated_data(self, data: Dict, data_type: str, period: str):
        """통합된 데이터를 파일로 저장"""
        filename = f"aggregated_{data_type}_{period}.json"
        filepath = self.aggregated_data_dir / filename

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def get_aggregated_summary(self) -> Dict:
        """통합된 사용량 요약 정보"""
        today = datetime.now().strftime("%Y-%m-%d")
        this_month = datetime.now().strftime("%Y-%m")

        daily = self.aggregate_daily_usage(today)
        monthly = self.aggregate_monthly_usage(this_month)

        # 최근 7일 데이터
        recent_7days = []
        for i in range(7):
            date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
            day_data = self.aggregate_daily_usage(date)
            recent_7days.append(day_data)

        return {
            "daily": daily,
            "monthly": monthly,
            "recent_7days": recent_7days,
            "projects_count": len(self.projects_data_dirs),
            "aggregated_at": datetime.now().isoformat()
        }

    def sync_all_projects(self):
        """모든 프로젝트의 데이터를 통합하여 저장"""
        print("🔄 모든 프로젝트 데이터 통합 중...")

        # 오늘 데이터 통합
        today = datetime.now().strftime("%Y-%m-%d")
        daily_data = self.aggregate_daily_usage(today)
        self.save_aggregated_data(daily_data, "daily", today)

        # 이번 달 데이터 통합
        this_month = datetime.now().strftime("%Y-%m")
        monthly_data = self.aggregate_monthly_usage(this_month)
        self.save_aggregated_data(monthly_data, "monthly", this_month)

        print(f"✅ 통합 완료: {daily_data['total_tokens']} 토큰, ${daily_data['total_cost']:.4f}")

class GlobalTokenMonitor:
    """전역 토큰 모니터링 클래스"""

    def __init__(self, global_data_dir: str = "data/global_usage"):
        self.global_data_dir = Path(global_data_dir)
        self.global_data_dir.mkdir(parents=True, exist_ok=True)

        # 전역 설정
        self.config = TokenMonitorConfig(
            data_dir=str(self.global_data_dir),
            daily_limit=int(os.getenv("GLOBAL_TOKEN_DAILY_LIMIT", "10000000")),  # 10M
            monthly_limit=int(os.getenv("GLOBAL_TOKEN_MONTHLY_LIMIT", "300000000"))  # 300M
        )

        self.monitor = TokenMonitor(config=self.config)

    def log_global_usage(self, usage_data: Dict):
        """전역 사용량 로깅"""
        usage = self.monitor.create_usage_record(
            model=usage_data.get("model", "unknown"),
            input_tokens=usage_data.get("input_tokens", 0),
            output_tokens=usage_data.get("output_tokens", 0),
            endpoint=usage_data.get("endpoint", "unknown"),
            user_id=usage_data.get("user_id"),
            project_id=usage_data.get("project_id"),
            session_id=usage_data.get("session_id")
        )

        self.monitor.log_usage(usage)

    def get_global_summary(self) -> Dict:
        """전역 사용량 요약"""
        return self.monitor.get_usage_summary()
