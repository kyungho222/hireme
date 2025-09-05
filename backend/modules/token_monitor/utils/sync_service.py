"""
여러 프로젝트 간 토큰 사용량 동기화 서비스
"""
import json
import os
import threading
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

from .aggregator import GlobalTokenMonitor, TokenUsageAggregator


class TokenSyncService:
    """토큰 사용량 동기화 서비스"""

    def __init__(self,
                 projects_config: Dict[str, str],  # {"project_name": "data_dir_path"}
                 sync_interval: int = 300,  # 5분마다 동기화
                 global_monitor: bool = True):

        self.projects_config = projects_config
        self.sync_interval = sync_interval
        self.global_monitor = global_monitor

        # 프로젝트 데이터 디렉토리 목록
        self.projects_data_dirs = list(projects_config.values())

        # 통합기 초기화
        self.aggregator = TokenUsageAggregator(
            projects_data_dirs=self.projects_data_dirs,
            aggregated_data_dir="data/aggregated_usage"
        )

        # 전역 모니터 초기화
        if global_monitor:
            self.global_monitor = GlobalTokenMonitor()

        self.is_running = False
        self.sync_thread = None

    def start_sync(self):
        """동기화 시작"""
        if self.is_running:
            return

        self.is_running = True
        self.sync_thread = threading.Thread(target=self._sync_loop, daemon=True)
        self.sync_thread.start()
        print(f"🔄 토큰 사용량 동기화 시작 (간격: {self.sync_interval}초)")

    def stop_sync(self):
        """동기화 중지"""
        self.is_running = False
        if self.sync_thread:
            self.sync_thread.join()
        print("⏹️ 토큰 사용량 동기화 중지")

    def _sync_loop(self):
        """동기화 루프"""
        while self.is_running:
            try:
                self.sync_all_projects()
                time.sleep(self.sync_interval)
            except Exception as e:
                print(f"❌ 동기화 오류: {e}")
                time.sleep(60)  # 오류 시 1분 대기

    def sync_all_projects(self):
        """모든 프로젝트 동기화"""
        try:
            # 통합 데이터 생성
            self.aggregator.sync_all_projects()

            # 전역 모니터에 데이터 전송
            if self.global_monitor:
                self._update_global_monitor()

        except Exception as e:
            print(f"❌ 프로젝트 동기화 오류: {e}")

    def _update_global_monitor(self):
        """전역 모니터 업데이트"""
        try:
            # 오늘의 통합 데이터 가져오기
            today = datetime.now().strftime("%Y-%m-%d")
            daily_data = self.aggregator.aggregate_daily_usage(today)

            # 전역 모니터에 기록
            if daily_data["total_tokens"] > 0:
                global_usage = {
                    "model": "aggregated",
                    "input_tokens": daily_data["total_tokens"] // 2,  # 추정
                    "output_tokens": daily_data["total_tokens"] // 2,  # 추정
                    "endpoint": "sync_service",
                    "project_id": "global",
                    "session_id": f"sync_{today}"
                }

                self.global_monitor.log_global_usage(global_usage)

        except Exception as e:
            print(f"❌ 전역 모니터 업데이트 오류: {e}")

    def get_global_summary(self) -> Dict:
        """전역 사용량 요약"""
        if not self.global_monitor:
            return {"error": "전역 모니터가 비활성화됨"}

        return self.global_monitor.get_global_summary()

    def get_aggregated_summary(self) -> Dict:
        """통합된 사용량 요약"""
        return self.aggregator.get_aggregated_summary()

    def force_sync(self):
        """강제 동기화"""
        print("🔄 강제 동기화 실행...")
        self.sync_all_projects()
        print("✅ 강제 동기화 완료")

class ProjectTokenSync:
    """개별 프로젝트에서 사용하는 동기화 클라이언트"""

    def __init__(self,
                 project_name: str,
                 project_data_dir: str,
                 sync_endpoint: Optional[str] = None):

        self.project_name = project_name
        self.project_data_dir = Path(project_data_dir)
        self.sync_endpoint = sync_endpoint

    def send_usage_to_global(self, usage_data: Dict):
        """사용량을 전역 모니터에 전송"""
        if not self.sync_endpoint:
            return False

        try:
            import requests

            payload = {
                "project_name": self.project_name,
                "usage_data": usage_data,
                "timestamp": datetime.now().isoformat()
            }

            response = requests.post(
                self.sync_endpoint,
                json=payload,
                timeout=10
            )

            return response.status_code == 200

        except Exception as e:
            print(f"❌ 전역 모니터 전송 오류: {e}")
            return False

    def get_local_summary(self) -> Dict:
        """로컬 프로젝트 사용량 요약"""
        try:
            from ..core.config import TokenMonitorConfig
            from ..core.monitor import TokenMonitor

            config = TokenMonitorConfig(data_dir=str(self.project_data_dir))
            monitor = TokenMonitor(config=config)

            return monitor.get_usage_summary()

        except Exception as e:
            return {"error": f"로컬 요약 조회 오류: {e}"}
