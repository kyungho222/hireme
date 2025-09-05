"""
토큰 사용량 데이터 가져오기 유틸리티
"""
import csv
import json
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from ..core.config import TokenMonitorConfig
from ..core.monitor import TokenMonitor, TokenUsage


class TokenDataImporter:
    """토큰 사용량 데이터 가져오기 클래스"""

    def __init__(self, token_monitor: TokenMonitor):
        self.token_monitor = token_monitor

    def import_from_json(self, file_path: str, merge: bool = True) -> bool:
        """JSON 파일에서 데이터 가져오기"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            if not isinstance(data, dict) or "daily_usage" not in data:
                print("❌ 잘못된 JSON 형식입니다.")
                return False

            imported_count = 0

            # 일일 사용량 데이터 가져오기
            for daily_data in data.get("daily_usage", []):
                date = daily_data.get("date")
                if not date:
                    continue

                daily_file = self.token_monitor.data_dir / f"usage_{date}.json"

                if merge and daily_file.exists():
                    # 기존 데이터와 병합
                    with open(daily_file, 'r', encoding='utf-8') as f:
                        existing_data = json.load(f)

                    # 중복 제거 (timestamp 기준)
                    existing_timestamps = {item.get('timestamp') for item in existing_data}
                    new_items = [item for item in daily_data.get("usage_details", [])
                               if item.get('timestamp') not in existing_timestamps]

                    existing_data.extend(new_items)

                    with open(daily_file, 'w', encoding='utf-8') as f:
                        json.dump(existing_data, f, ensure_ascii=False, indent=2)
                else:
                    # 새로 생성
                    usage_details = daily_data.get("usage_details", [])
                    with open(daily_file, 'w', encoding='utf-8') as f:
                        json.dump(usage_details, f, ensure_ascii=False, indent=2)

                imported_count += len(daily_data.get("usage_details", []))

            # 월간 사용량 데이터 가져오기
            for monthly_data in data.get("monthly_usage", []):
                month = monthly_data.get("month")
                if not month:
                    continue

                monthly_file = self.token_monitor.data_dir / f"monthly_{month}.json"

                if merge and monthly_file.exists():
                    # 기존 데이터와 병합
                    with open(monthly_file, 'r', encoding='utf-8') as f:
                        existing_data = json.load(f)

                    existing_data["total_tokens"] += monthly_data.get("total_tokens", 0)
                    existing_data["total_cost"] += monthly_data.get("total_cost", 0.0)
                    existing_data["usage_count"] += monthly_data.get("usage_count", 0)

                    with open(monthly_file, 'w', encoding='utf-8') as f:
                        json.dump(existing_data, f, ensure_ascii=False, indent=2)
                else:
                    # 새로 생성
                    with open(monthly_file, 'w', encoding='utf-8') as f:
                        json.dump(monthly_data, f, ensure_ascii=False, indent=2)

            print(f"✅ JSON 데이터 가져오기 완료: {imported_count}개 레코드")
            return True

        except Exception as e:
            print(f"❌ JSON 가져오기 오류: {e}")
            return False

    def import_from_csv(self, file_path: str, merge: bool = True) -> bool:
        """CSV 파일에서 데이터 가져오기"""
        try:
            imported_count = 0

            with open(file_path, 'r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)

                for row in reader:
                    # 날짜별로 그룹화
                    date = row.get('Date', '').split('T')[0]  # ISO 형식에서 날짜만 추출
                    if not date:
                        continue

                    daily_file = self.token_monitor.data_dir / f"usage_{date}.json"

                    # 기존 데이터 로드
                    daily_usage = []
                    if daily_file.exists() and merge:
                        with open(daily_file, 'r', encoding='utf-8') as f:
                            daily_usage = json.load(f)

                    # 새 레코드 생성
                    usage_record = {
                        "timestamp": row.get('Date', ''),
                        "model": row.get('Model', ''),
                        "input_tokens": int(row.get('Input Tokens', 0)),
                        "output_tokens": int(row.get('Output Tokens', 0)),
                        "total_tokens": int(row.get('Total Tokens', 0)),
                        "cost_estimate": float(row.get('Cost', 0.0)),
                        "endpoint": row.get('Endpoint', ''),
                        "user_id": row.get('User ID', ''),
                        "project_id": row.get('Project ID', '')
                    }

                    # 중복 체크 (timestamp 기준)
                    if not any(item.get('timestamp') == usage_record['timestamp'] for item in daily_usage):
                        daily_usage.append(usage_record)
                        imported_count += 1

                    # 파일 저장
                    with open(daily_file, 'w', encoding='utf-8') as f:
                        json.dump(daily_usage, f, ensure_ascii=False, indent=2)

            print(f"✅ CSV 데이터 가져오기 완료: {imported_count}개 레코드")
            return True

        except Exception as e:
            print(f"❌ CSV 가져오기 오류: {e}")
            return False

    def import_from_zip(self, file_path: str, merge: bool = True) -> bool:
        """ZIP 파일에서 데이터 가져오기"""
        try:
            with zipfile.ZipFile(file_path, 'r') as zipf:
                # 파일 목록 확인
                file_list = zipf.namelist()

                # JSON 파일 가져오기
                if 'token_usage.json' in file_list:
                    json_data = zipf.read('token_usage.json').decode('utf-8')
                    temp_json_file = Path(file_path).parent / 'temp_import.json'

                    with open(temp_json_file, 'w', encoding='utf-8') as f:
                        f.write(json_data)

                    success = self.import_from_json(str(temp_json_file), merge)
                    temp_json_file.unlink()  # 임시 파일 삭제

                    if not success:
                        return False

                # CSV 파일 가져오기
                if 'token_usage.csv' in file_list:
                    csv_data = zipf.read('token_usage.csv').decode('utf-8')
                    temp_csv_file = Path(file_path).parent / 'temp_import.csv'

                    with open(temp_csv_file, 'w', encoding='utf-8') as f:
                        f.write(csv_data)

                    success = self.import_from_csv(str(temp_csv_file), merge)
                    temp_csv_file.unlink()  # 임시 파일 삭제

                    if not success:
                        return False

                # 설정 파일 가져오기 (선택사항)
                if 'config.json' in file_list:
                    config_data = zipf.read('config.json').decode('utf-8')
                    config_dict = json.loads(config_data)

                    # 설정 병합 (기존 설정 유지하면서 새로운 설정 추가)
                    for key, value in config_dict.items():
                        if hasattr(self.token_monitor.config, key):
                            setattr(self.token_monitor.config, key, value)

            print("✅ ZIP 데이터 가져오기 완료")
            return True

        except Exception as e:
            print(f"❌ ZIP 가져오기 오류: {e}")
            return False

    def validate_import_data(self, file_path: str) -> Dict:
        """가져오기 데이터 유효성 검사"""
        try:
            file_ext = Path(file_path).suffix.lower()

            if file_ext == '.json':
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                return {
                    "valid": True,
                    "type": "json",
                    "records": len(data.get("daily_usage", [])),
                    "date_range": {
                        "start": data.get("daily_usage", [{}])[0].get("date") if data.get("daily_usage") else None,
                        "end": data.get("daily_usage", [{}])[-1].get("date") if data.get("daily_usage") else None
                    }
                }

            elif file_ext == '.csv':
                with open(file_path, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    records = list(reader)

                dates = [row.get('Date', '').split('T')[0] for row in records if row.get('Date')]

                return {
                    "valid": True,
                    "type": "csv",
                    "records": len(records),
                    "date_range": {
                        "start": min(dates) if dates else None,
                        "end": max(dates) if dates else None
                    }
                }

            elif file_ext == '.zip':
                with zipfile.ZipFile(file_path, 'r') as zipf:
                    file_list = zipf.namelist()

                return {
                    "valid": True,
                    "type": "zip",
                    "files": file_list,
                    "has_json": 'token_usage.json' in file_list,
                    "has_csv": 'token_usage.csv' in file_list,
                    "has_config": 'config.json' in file_list
                }

            else:
                return {
                    "valid": False,
                    "error": f"지원하지 않는 파일 형식: {file_ext}"
                }

        except Exception as e:
            return {
                "valid": False,
                "error": str(e)
            }
