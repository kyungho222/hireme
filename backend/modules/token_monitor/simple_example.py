#!/usr/bin/env python3
"""
Token Monitor Module 간단한 사용 예제
새 프로젝트에서 바로 복사해서 사용할 수 있는 예제
"""
import os
import sys
from pathlib import Path

# 모듈 경로 추가 (필요한 경우)
sys.path.append(str(Path(__file__).parent.parent))

import openai
from dotenv import load_dotenv
from modules.token_monitor import AutoTokenMonitor, TokenMonitor, TokenMonitorConfig

# 환경 변수 로드
load_dotenv()

def main():
    """메인 함수"""
    print("🚀 Token Monitor 간단한 사용 예제")
    print("=" * 40)

    # 1. 모니터 초기화
    print("\n1️⃣ 모니터 초기화")
    config = TokenMonitorConfig()
    monitor = TokenMonitor(config=config)
    auto_monitor = AutoTokenMonitor(token_monitor=monitor, config=config)
    print("   ✅ 초기화 완료")

    # 2. 자동 모니터링 시작
    print("\n2️⃣ 자동 모니터링 시작")
    auto_monitor.start_monitoring()
    print("   🔍 모니터링 활성화")

    # 3. OpenAI API 호출 시뮬레이션
    print("\n3️⃣ OpenAI API 호출 시뮬레이션")
    try:
        # 실제 API 호출 (API 키가 설정된 경우)
        if os.getenv('OPENAI_API_KEY'):
            client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
            response = client.chat.completions.create(
                model="gpt-5-mini",
                messages=[{"role": "user", "content": "안녕하세요! 토큰 모니터링 테스트입니다."}],
                max_completion_tokens=100,
                temperature=1.0
            )

            # 토큰 사용량 자동 기록
            if hasattr(response, 'usage') and response.usage:
                usage = monitor.create_usage_record(
                    model="gpt-5-mini",
                    input_tokens=response.usage.prompt_tokens,
                    output_tokens=response.usage.completion_tokens,
                    endpoint="chat_completion",
                    project_id="example_project"
                )
                monitor.log_usage(usage)
                print(f"   📝 API 호출 성공: {usage.total_tokens} 토큰 사용")
                print(f"   💰 비용: ${usage.cost_estimate:.4f}")
        else:
            print("   ⚠️ OPENAI_API_KEY가 설정되지 않음 - 시뮬레이션 모드")
            # 시뮬레이션 데이터
            usage = monitor.create_usage_record(
                model="gpt-5-mini",
                input_tokens=50,
                output_tokens=30,
                endpoint="simulation",
                project_id="example_project"
            )
            monitor.log_usage(usage)
            print(f"   📝 시뮬레이션: {usage.total_tokens} 토큰 사용")

    except Exception as e:
        print(f"   ❌ API 호출 실패: {e}")

    # 4. 사용량 조회
    print("\n4️⃣ 사용량 조회")
    summary = monitor.get_usage_summary()
    daily = summary["daily"]
    monthly = summary["monthly"]

    print(f"   📅 오늘: {daily['total_tokens']} / {monitor.limits.daily_limit:,} 토큰 ({daily.get('limit_usage_percent', 0):.1f}%)")
    print(f"   📆 이번 달: {monthly['total_tokens']} / {monitor.limits.monthly_limit:,} 토큰 ({monthly.get('limit_usage_percent', 0):.1f}%)")
    print(f"   💰 오늘 비용: ${daily['total_cost']:.4f}")
    print(f"   🔍 상태: {summary['status']}")

    # 5. 자동 모니터링 중지
    print("\n5️⃣ 자동 모니터링 중지")
    auto_monitor.stop_monitoring()
    print("   ⏹️ 모니터링 중지")

    print("\n✅ 예제 완료!")
    print("\n📋 다음 단계:")
    print("   1. .env 파일에 OPENAI_API_KEY 설정")
    print("   2. 실제 프로젝트에 이 코드 통합")
    print("   3. 자동 모니터링 활성화")

if __name__ == "__main__":
    main()
