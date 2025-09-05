#!/usr/bin/env python3
"""
토큰 모니터링 모듈 독립 사용 예제
다른 프로젝트에서 이 모듈을 사용하는 방법을 보여줍니다.
"""
import os
import sys
from pathlib import Path

# 모듈 경로 추가
sys.path.append(str(Path(__file__).parent.parent.parent))

from modules.token_monitor import AutoTokenMonitor, TokenMonitor, TokenMonitorConfig


def main():
    """독립적인 토큰 모니터링 예제"""

    print("🚀 토큰 모니터링 모듈 독립 사용 예제")
    print("=" * 50)

    # 1. 설정 생성
    print("\n1️⃣ 설정 생성")
    config = TokenMonitorConfig(
        data_dir="my_project/token_data",  # 프로젝트별 데이터 디렉토리
        daily_limit=1000000,  # 프로젝트별 일일 한도
        monthly_limit=30000000,  # 프로젝트별 월간 한도
        auto_monitor_enabled=True,
        monitor_interval=60,  # 1분마다 체크
        webhook_url="https://hooks.slack.com/your-webhook-url"  # Slack 알림
    )

    print(f"   데이터 디렉토리: {config.data_dir}")
    print(f"   일일 한도: {config.daily_limit:,} 토큰")
    print(f"   자동 모니터링: {config.auto_monitor_enabled}")

    # 2. 토큰 모니터 생성
    print("\n2️⃣ 토큰 모니터 생성")
    monitor = TokenMonitor(config=config)
    print("   ✅ 토큰 모니터 초기화 완료")

    # 3. 사용량 기록 시뮬레이션
    print("\n3️⃣ 사용량 기록 시뮬레이션")
    for i in range(3):
        usage = monitor.create_usage_record(
            model="gpt-5-mini",
            input_tokens=100,
            output_tokens=50,
            endpoint="chat_completion",
            user_id="user123",
            project_id="my_project"
        )
        monitor.log_usage(usage)
        print(f"   📝 사용량 기록 {i+1}: {usage.total_tokens} 토큰")

    # 4. 사용량 조회
    print("\n4️⃣ 사용량 조회")
    summary = monitor.get_usage_summary()
    daily = summary["daily"]
    print(f"   오늘 사용량: {daily['total_tokens']} 토큰")
    print(f"   오늘 비용: ${daily['total_cost']:.4f}")
    print(f"   상태: {summary['status']}")

    # 5. 자동 모니터링 시작
    print("\n5️⃣ 자동 모니터링 시작")
    auto_monitor = AutoTokenMonitor(token_monitor=monitor, config=config)
    auto_monitor.start_monitoring()
    print("   🔍 자동 모니터링 활성화")

    # 6. 모니터링 상태 확인
    print("\n6️⃣ 모니터링 상태 확인")
    status = auto_monitor.get_status()
    print(f"   실행 중: {status['is_running']}")
    print(f"   체크 간격: {status['report_interval']}초")
    print(f"   웹훅 설정: {status['webhook_configured']}")

    # 7. 프로젝트별 사용량 조회
    print("\n7️⃣ 프로젝트별 사용량 조회")
    project_usage = monitor.get_project_usage("my_project")
    print(f"   프로젝트 사용량: {project_usage['total_tokens']} 토큰")
    print(f"   프로젝트 비용: ${project_usage['total_cost']:.4f}")

    # 8. 설정 저장
    print("\n8️⃣ 설정 저장")
    config.save_to_file("my_project/token_config.json")
    print("   💾 설정 파일 저장 완료")

    # 9. 자동 모니터링 중지
    print("\n9️⃣ 자동 모니터링 중지")
    auto_monitor.stop_monitoring()
    print("   ⏹️ 자동 모니터링 중지")

    print("\n✅ 예제 완료!")
    print("\n📋 사용된 기능들:")
    print("   - 독립적인 설정 관리")
    print("   - 프로젝트별 데이터 분리")
    print("   - 자동 모니터링")
    print("   - 웹훅 알림")
    print("   - 설정 파일 저장/로드")
    print("   - 프로젝트별 사용량 추적")

if __name__ == "__main__":
    main()
