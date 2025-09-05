"""
자동 토큰 모니터링 서비스
"""
import asyncio
import os
import threading
import time
from datetime import datetime, timedelta
from typing import Optional

import schedule

from .token_monitor import token_monitor


class AutoTokenMonitor:
    """자동 토큰 모니터링 클래스"""

    def __init__(self):
        self.is_running = False
        self.monitor_thread = None
        self.report_interval = int(os.getenv("TOKEN_MONITOR_INTERVAL", "300"))  # 5분마다
        self.auto_report = os.getenv("TOKEN_AUTO_REPORT", "true").lower() == "true"
        self.report_threshold = float(os.getenv("TOKEN_REPORT_THRESHOLD", "0.1"))  # 10% 도달 시 리포트
        self.webhook_url = os.getenv("TOKEN_WEBHOOK_URL", "")
        self.last_report_time = None

    def start_monitoring(self):
        """모니터링 시작"""
        if self.is_running:
            return

        self.is_running = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        print(f"🔍 토큰 모니터링 시작 (간격: {self.report_interval}초)")

    def stop_monitoring(self):
        """모니터링 중지"""
        self.is_running = False
        if self.monitor_thread:
            self.monitor_thread.join()
        print("⏹️ 토큰 모니터링 중지")

    def _monitor_loop(self):
        """모니터링 루프"""
        while self.is_running:
            try:
                self._check_usage_and_alert()
                time.sleep(self.report_interval)
            except Exception as e:
                print(f"❌ 모니터링 오류: {e}")
                time.sleep(60)  # 오류 시 1분 대기

    def _check_usage_and_alert(self):
        """사용량 확인 및 알림"""
        try:
            summary = token_monitor.get_usage_summary()
            daily = summary["daily"]
            monthly = summary["monthly"]
            status = summary["status"]

            # 상태가 경고 이상이거나 임계값 도달 시 알림
            if (status in ["WARNING", "CRITICAL"] or
                daily.get("limit_usage_percent", 0) >= self.report_threshold * 100):

                self._send_alert(summary)

        except Exception as e:
            print(f"❌ 사용량 확인 오류: {e}")

    def _send_alert(self, summary: dict):
        """알림 전송"""
        daily = summary["daily"]
        monthly = summary["monthly"]
        status = summary["status"]

        # 콘솔 알림
        self._print_console_alert(daily, monthly, status)

        # 웹훅 알림 (설정된 경우)
        if self.webhook_url:
            self._send_webhook_alert(summary)

        # 파일 로그
        self._log_alert(summary)

    def _print_console_alert(self, daily: dict, monthly: dict, status: str):
        """콘솔 알림 출력"""
        status_emoji = {"NORMAL": "✅", "WARNING": "⚠️", "CRITICAL": "🚨"}
        emoji = status_emoji.get(status, "❓")

        print(f"\n{emoji} 토큰 사용량 알림 - {datetime.now().strftime('%H:%M:%S')}")
        print(f"📅 오늘: {daily.get('total_tokens', 0):,} / {token_monitor.limits.daily_limit:,} 토큰 ({daily.get('limit_usage_percent', 0):.1f}%)")
        print(f"📆 이번 달: {monthly.get('total_tokens', 0):,} / {token_monitor.limits.monthly_limit:,} 토큰 ({monthly.get('limit_usage_percent', 0):.1f}%)")
        print(f"💰 오늘 비용: ${daily.get('total_cost', 0):.4f}")

        if status == "CRITICAL":
            print("🚨 위험: 토큰 사용량이 위험 수준에 도달했습니다!")
        elif status == "WARNING":
            print("⚠️ 경고: 토큰 사용량이 경고 수준에 도달했습니다.")

    def _send_webhook_alert(self, summary: dict):
        """웹훅 알림 전송"""
        try:
            import requests

            daily = summary["daily"]
            monthly = summary["monthly"]
            status = summary["status"]

            payload = {
                "text": f"토큰 사용량 알림 - {status}",
                "attachments": [{
                    "color": "danger" if status == "CRITICAL" else "warning" if status == "WARNING" else "good",
                    "fields": [
                        {"title": "오늘 사용량", "value": f"{daily.get('total_tokens', 0):,} / {token_monitor.limits.daily_limit:,} 토큰 ({daily.get('limit_usage_percent', 0):.1f}%)", "short": True},
                        {"title": "월간 사용량", "value": f"{monthly.get('total_tokens', 0):,} / {token_monitor.limits.monthly_limit:,} 토큰 ({monthly.get('limit_usage_percent', 0):.1f}%)", "short": True},
                        {"title": "오늘 비용", "value": f"${daily.get('total_cost', 0):.4f}", "short": True},
                        {"title": "상태", "value": status, "short": True}
                    ]
                }]
            }

            response = requests.post(self.webhook_url, json=payload, timeout=10)
            if response.status_code == 200:
                print("✅ 웹훅 알림 전송 성공")
            else:
                print(f"❌ 웹훅 알림 전송 실패: {response.status_code}")

        except Exception as e:
            print(f"❌ 웹훅 알림 오류: {e}")

    def _log_alert(self, summary: dict):
        """알림 로그 파일 저장"""
        try:
            log_dir = token_monitor.data_dir / "alerts"
            log_dir.mkdir(exist_ok=True)

            today = datetime.now().strftime("%Y-%m-%d")
            log_file = log_dir / f"alerts_{today}.log"

            daily = summary["daily"]
            monthly = summary["monthly"]
            status = summary["status"]

            log_entry = f"{datetime.now().isoformat()} - {status} - Daily: {daily.get('total_tokens', 0)}/{token_monitor.limits.daily_limit} ({daily.get('limit_usage_percent', 0):.1f}%) - Monthly: {monthly.get('total_tokens', 0)}/{token_monitor.limits.monthly_limit} ({monthly.get('limit_usage_percent', 0):.1f}%)\n"

            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(log_entry)

        except Exception as e:
            print(f"❌ 로그 저장 오류: {e}")

    def get_status(self) -> dict:
        """모니터링 상태 조회"""
        return {
            "is_running": self.is_running,
            "report_interval": self.report_interval,
            "auto_report": self.auto_report,
            "report_threshold": self.report_threshold,
            "webhook_configured": bool(self.webhook_url),
            "last_report_time": self.last_report_time
        }

    def force_check(self) -> dict:
        """강제 사용량 확인"""
        try:
            summary = token_monitor.get_usage_summary()
            self._check_usage_and_alert()
            return {"success": True, "data": summary}
        except Exception as e:
            return {"success": False, "error": str(e)}

# 전역 자동 모니터 인스턴스
auto_monitor = AutoTokenMonitor()
