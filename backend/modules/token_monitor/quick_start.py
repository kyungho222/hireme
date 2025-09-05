#!/usr/bin/env python3
"""
Token Monitor Module 빠른 시작 가이드
새 프로젝트에서 이 모듈을 빠르게 시작하는 방법
"""
import os
import sys
from pathlib import Path

# 모듈 경로 추가
sys.path.append(str(Path(__file__).parent.parent))

from modules.token_monitor import AutoTokenMonitor, TokenMonitor, TokenMonitorConfig


def quick_start():
    """빠른 시작 예제"""
    print("🚀 Token Monitor Module 빠른 시작")
    print("=" * 50)

    # 1. 기본 설정으로 모니터 생성
    print("\n1️⃣ 기본 설정으로 모니터 생성")
    config = TokenMonitorConfig()
    monitor = TokenMonitor(config=config)
    print("   ✅ 토큰 모니터 초기화 완료")

    # 2. 사용량 기록 예제
    print("\n2️⃣ 사용량 기록 예제")
    usage = monitor.create_usage_record(
        model="gpt-5-mini",
        input_tokens=100,
        output_tokens=50,
        endpoint="test",
        project_id="quick_start_demo"
    )
    monitor.log_usage(usage)
    print(f"   📝 테스트 사용량 기록: {usage.total_tokens} 토큰")

    # 3. 사용량 조회
    print("\n3️⃣ 사용량 조회")
    summary = monitor.get_usage_summary()
    daily = summary["daily"]
    print(f"   오늘 사용량: {daily['total_tokens']} 토큰")
    print(f"   오늘 비용: ${daily['total_cost']:.4f}")
    print(f"   상태: {summary['status']}")

    # 4. 자동 모니터링 시작 (선택사항)
    print("\n4️⃣ 자동 모니터링 시작")
    auto_monitor = AutoTokenMonitor(token_monitor=monitor, config=config)
    auto_monitor.start_monitoring()
    print("   🔍 자동 모니터링 활성화")

    # 5. 3초 후 중지
    import time
    print("   ⏳ 3초 후 자동 모니터링 중지...")
    time.sleep(3)
    auto_monitor.stop_monitoring()
    print("   ⏹️ 자동 모니터링 중지")

    print("\n✅ 빠른 시작 완료!")
    print("\n📋 다음 단계:")
    print("   1. .env 파일에 환경 변수 설정")
    print("   2. OpenAI API 키 설정")
    print("   3. 실제 프로젝트에 통합")
    print("   4. 자동 모니터링 활성화")

def check_environment():
    """환경 설정 확인"""
    print("\n🔍 환경 설정 확인")
    print("=" * 30)

    # 환경 변수 확인
    env_vars = [
        "TOKEN_DAILY_LIMIT",
        "TOKEN_MONTHLY_LIMIT",
        "TOKEN_AUTO_MONITOR",
        "TOKEN_MONITOR_DATA_DIR"
    ]

    for var in env_vars:
        value = os.getenv(var, "설정되지 않음")
        print(f"   {var}: {value}")

    # 데이터 디렉토리 확인
    data_dir = os.getenv("TOKEN_MONITOR_DATA_DIR", "data/token_usage")
    if Path(data_dir).exists():
        print(f"   📁 데이터 디렉토리: {data_dir} (존재함)")
    else:
        print(f"   📁 데이터 디렉토리: {data_dir} (생성 예정)")

if __name__ == "__main__":
    try:
        check_environment()
        quick_start()
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        print("\n🔧 문제 해결:")
        print("   1. .env 파일이 있는지 확인")
        print("   2. 필요한 패키지가 설치되었는지 확인")
        print("   3. Python 경로 설정 확인")
