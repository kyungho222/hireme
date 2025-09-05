#!/usr/bin/env python3
"""
여러 프로젝트에서 토큰 사용량을 통합하는 예제
"""
import os
import sys
from pathlib import Path

# 모듈 경로 추가
sys.path.append(str(Path(__file__).parent.parent.parent))

from modules.token_monitor import TokenMonitor, TokenMonitorConfig
from modules.token_monitor.utils.aggregator import (
    GlobalTokenMonitor,
    TokenUsageAggregator,
)
from modules.token_monitor.utils.sync_service import TokenSyncService


def create_sample_projects():
    """샘플 프로젝트들 생성"""
    print("🏗️ 샘플 프로젝트들 생성")

    projects = {
        "project_a": "data/project_a/token_usage",
        "project_b": "data/project_b/token_usage",
        "project_c": "data/project_c/token_usage"
    }

    for project_name, data_dir in projects.items():
        # 프로젝트별 모니터 생성
        config = TokenMonitorConfig(data_dir=data_dir)
        monitor = TokenMonitor(config=config)

        # 샘플 사용량 기록
        for i in range(3):
            usage = monitor.create_usage_record(
                model="gpt-5-mini",
                input_tokens=100 + i * 10,
                output_tokens=50 + i * 5,
                endpoint="chat_completion",
                project_id=project_name,
                user_id=f"user_{i+1}"
            )
            monitor.log_usage(usage)

        print(f"   ✅ {project_name}: {3}개 사용량 기록")

    return projects

def demonstrate_aggregation():
    """통합 기능 시연"""
    print("\n🔄 토큰 사용량 통합 시연")

    # 샘플 프로젝트 생성
    projects = create_sample_projects()

    # 통합기 초기화
    aggregator = TokenUsageAggregator(
        projects_data_dirs=list(projects.values()),
        aggregated_data_dir="data/aggregated_usage"
    )

    # 일일 사용량 통합
    print("\n📊 일일 사용량 통합")
    daily_summary = aggregator.aggregate_daily_usage()
    print(f"   총 토큰: {daily_summary['total_tokens']:,}")
    print(f"   총 비용: ${daily_summary['total_cost']:.4f}")
    print(f"   총 호출: {daily_summary['usage_count']}회")

    # 프로젝트별 사용량
    print("\n📁 프로젝트별 사용량:")
    for project, data in daily_summary['projects'].items():
        print(f"   {project}: {data['tokens']:,} 토큰, ${data['cost']:.4f}")

    # 모델별 사용량
    print("\n🤖 모델별 사용량:")
    for model, data in daily_summary['models'].items():
        print(f"   {model}: {data['tokens']:,} 토큰, ${data['cost']:.4f}")

    # 통합 데이터 저장
    aggregator.save_aggregated_data(daily_summary, "daily", daily_summary['date'])
    print(f"\n💾 통합 데이터 저장 완료")

def demonstrate_global_monitor():
    """전역 모니터 시연"""
    print("\n🌍 전역 토큰 모니터 시연")

    # 전역 모니터 초기화
    global_monitor = GlobalTokenMonitor()

    # 전역 사용량 기록
    global_usage = {
        "model": "gpt-5-mini",
        "input_tokens": 500,
        "output_tokens": 250,
        "endpoint": "global_sync",
        "project_id": "global",
        "user_id": "system"
    }

    global_monitor.log_global_usage(global_usage)
    print("   📝 전역 사용량 기록 완료")

    # 전역 요약 조회
    global_summary = global_monitor.get_global_summary()
    daily = global_summary['daily']

    print(f"   🌍 전역 오늘 사용량: {daily['total_tokens']:,} 토큰")
    print(f"   💰 전역 오늘 비용: ${daily['total_cost']:.4f}")
    print(f"   🔍 전역 상태: {global_summary['status']}")

def demonstrate_sync_service():
    """동기화 서비스 시연"""
    print("\n🔄 동기화 서비스 시연")

    # 프로젝트 설정
    projects_config = {
        "project_a": "data/project_a/token_usage",
        "project_b": "data/project_b/token_usage",
        "project_c": "data/project_c/token_usage"
    }

    # 동기화 서비스 초기화
    sync_service = TokenSyncService(
        projects_config=projects_config,
        sync_interval=60,  # 1분마다 동기화
        global_monitor=True
    )

    # 동기화 시작
    sync_service.start_sync()
    print("   🔄 동기화 서비스 시작")

    # 3초 대기
    import time
    time.sleep(3)

    # 통합 요약 조회
    aggregated_summary = sync_service.get_aggregated_summary()
    print(f"   📊 통합 프로젝트 수: {aggregated_summary['projects_count']}")
    print(f"   📅 통합 오늘 사용량: {aggregated_summary['daily']['total_tokens']:,} 토큰")

    # 전역 요약 조회
    global_summary = sync_service.get_global_summary()
    if "error" not in global_summary:
        daily = global_summary['daily']
        print(f"   🌍 전역 오늘 사용량: {daily['total_tokens']:,} 토큰")

    # 동기화 중지
    sync_service.stop_sync()
    print("   ⏹️ 동기화 서비스 중지")

def main():
    """메인 함수"""
    print("🚀 다중 프로젝트 토큰 사용량 통합 예제")
    print("=" * 50)

    try:
        # 1. 통합 기능 시연
        demonstrate_aggregation()

        # 2. 전역 모니터 시연
        demonstrate_global_monitor()

        # 3. 동기화 서비스 시연
        demonstrate_sync_service()

        print("\n✅ 모든 예제 완료!")
        print("\n📋 사용된 기능들:")
        print("   - 여러 프로젝트 데이터 통합")
        print("   - 전역 토큰 모니터링")
        print("   - 자동 동기화 서비스")
        print("   - 프로젝트별/모델별 집계")

    except Exception as e:
        print(f"❌ 오류 발생: {e}")

if __name__ == "__main__":
    main()
