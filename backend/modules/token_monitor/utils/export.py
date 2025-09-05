"""
토큰 사용량 데이터 내보내기 유틸리티
"""
import csv
import json
import zipfile
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

from ..core.monitor import TokenMonitor


class TokenDataExporter:
    """토큰 사용량 데이터 내보내기 클래스"""

    def __init__(self, token_monitor: TokenMonitor):
        self.token_monitor = token_monitor

    def export_to_json(self, start_date: str, end_date: str, output_file: str) -> bool:
        """JSON 형식으로 데이터 내보내기"""
        try:
            start = datetime.strptime(start_date, "%Y-%m-%d")
            end = datetime.strptime(end_date, "%Y-%m-%d")

            export_data = {
                "export_info": {
                    "start_date": start_date,
                    "end_date": end_date,
                    "exported_at": datetime.now().isoformat(),
                    "version": "1.0.0"
                },
                "daily_usage": [],
                "monthly_usage": [],
                "projects": []
            }

            # 일일 사용량 데이터 수집
            current_date = start
            while current_date <= end:
                date_str = current_date.strftime("%Y-%m-%d")
                daily_data = self.token_monitor.get_daily_usage(date_str)
                if daily_data["total_tokens"] > 0:
                    export_data["daily_usage"].append(daily_data)
                current_date += timedelta(days=1)

            # 월간 사용량 데이터 수집
            current_month = start.replace(day=1)
            end_month = end.replace(day=1)
            while current_month <= end_month:
                month_str = current_month.strftime("%Y-%m")
                monthly_data = self.token_monitor.get_monthly_usage(month_str)
                if monthly_data["total_tokens"] > 0:
                    export_data["monthly_usage"].append(monthly_data)
                if current_month.month == 12:
                    current_month = current_month.replace(year=current_month.year + 1, month=1)
                else:
                    current_month = current_month.replace(month=current_month.month + 1)

            # 프로젝트별 데이터 수집
            for project_file in self.token_monitor.data_dir.glob("project_*.json"):
                try:
                    with open(project_file, 'r', encoding='utf-8') as f:
                        project_data = json.load(f)
                    export_data["projects"].append(project_data)
                except:
                    pass

            # 파일로 저장
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2)

            return True

        except Exception as e:
            print(f"❌ JSON 내보내기 오류: {e}")
            return False

    def export_to_csv(self, start_date: str, end_date: str, output_file: str) -> bool:
        """CSV 형식으로 데이터 내보내기"""
        try:
            start = datetime.strptime(start_date, "%Y-%m-%d")
            end = datetime.strptime(end_date, "%Y-%m-%d")

            with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)

                # 헤더 작성
                writer.writerow([
                    'Date', 'Model', 'Input Tokens', 'Output Tokens',
                    'Total Tokens', 'Cost', 'Endpoint', 'User ID', 'Project ID'
                ])

                # 일일 사용량 데이터 수집
                current_date = start
                while current_date <= end:
                    date_str = current_date.strftime("%Y-%m-%d")
                    daily_file = self.token_monitor.data_dir / f"usage_{date_str}.json"

                    if daily_file.exists():
                        with open(daily_file, 'r', encoding='utf-8') as f:
                            daily_usage = json.load(f)

                        for usage in daily_usage:
                            writer.writerow([
                                usage.get('timestamp', ''),
                                usage.get('model', ''),
                                usage.get('input_tokens', 0),
                                usage.get('output_tokens', 0),
                                usage.get('total_tokens', 0),
                                usage.get('cost_estimate', 0.0),
                                usage.get('endpoint', ''),
                                usage.get('user_id', ''),
                                usage.get('project_id', '')
                            ])

                    current_date += timedelta(days=1)

            return True

        except Exception as e:
            print(f"❌ CSV 내보내기 오류: {e}")
            return False

    def export_to_zip(self, start_date: str, end_date: str, output_file: str) -> bool:
        """ZIP 형식으로 전체 데이터 내보내기"""
        try:
            with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # JSON 데이터 추가
                json_file = output_file.replace('.zip', '.json')
                if self.export_to_json(start_date, end_date, json_file):
                    zipf.write(json_file, 'token_usage.json')
                    Path(json_file).unlink()  # 임시 파일 삭제

                # CSV 데이터 추가
                csv_file = output_file.replace('.zip', '.csv')
                if self.export_to_csv(start_date, end_date, csv_file):
                    zipf.write(csv_file, 'token_usage.csv')
                    Path(csv_file).unlink()  # 임시 파일 삭제

                # 설정 파일 추가
                config_data = self.token_monitor.config.to_dict()
                zipf.writestr('config.json', json.dumps(config_data, ensure_ascii=False, indent=2))

                # 알림 로그 추가
                alerts_dir = self.token_monitor.data_dir / "alerts"
                if alerts_dir.exists():
                    for alert_file in alerts_dir.glob("*.log"):
                        zipf.write(alert_file, f"alerts/{alert_file.name}")

            return True

        except Exception as e:
            print(f"❌ ZIP 내보내기 오류: {e}")
            return False

    def get_export_summary(self, start_date: str, end_date: str) -> Dict:
        """내보내기 요약 정보"""
        try:
            start = datetime.strptime(start_date, "%Y-%m-%d")
            end = datetime.strptime(end_date, "%Y-%m-%d")

            total_tokens = 0
            total_cost = 0.0
            total_requests = 0
            models = {}
            projects = {}

            current_date = start
            while current_date <= end:
                date_str = current_date.strftime("%Y-%m-%d")
                daily_file = self.token_monitor.data_dir / f"usage_{date_str}.json"

                if daily_file.exists():
                    with open(daily_file, 'r', encoding='utf-8') as f:
                        daily_usage = json.load(f)

                    for usage in daily_usage:
                        total_tokens += usage.get('total_tokens', 0)
                        total_cost += usage.get('cost_estimate', 0.0)
                        total_requests += 1

                        # 모델별 집계
                        model = usage.get('model', 'unknown')
                        if model not in models:
                            models[model] = {"tokens": 0, "cost": 0.0, "requests": 0}
                        models[model]["tokens"] += usage.get('total_tokens', 0)
                        models[model]["cost"] += usage.get('cost_estimate', 0.0)
                        models[model]["requests"] += 1

                        # 프로젝트별 집계
                        project = usage.get('project_id', 'default')
                        if project not in projects:
                            projects[project] = {"tokens": 0, "cost": 0.0, "requests": 0}
                        projects[project]["tokens"] += usage.get('total_tokens', 0)
                        projects[project]["cost"] += usage.get('cost_estimate', 0.0)
                        projects[project]["requests"] += 1

                current_date += timedelta(days=1)

            return {
                "period": {"start_date": start_date, "end_date": end_date},
                "summary": {
                    "total_tokens": total_tokens,
                    "total_cost": total_cost,
                    "total_requests": total_requests
                },
                "models": models,
                "projects": projects
            }

        except Exception as e:
            print(f"❌ 요약 정보 생성 오류: {e}")
            return {}
