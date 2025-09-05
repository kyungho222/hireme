#!/usr/bin/env python3
"""
토큰 사용량 확인 CLI 도구
"""
import os
import sys
from datetime import datetime, timedelta

# 프로젝트 루트를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.token_monitor import token_monitor


def print_separator():
    print("=" * 60)

def format_number(num):
    """숫자를 천 단위로 포맷팅"""
    return f"{num:,}"

def format_currency(amount):
    """통화 포맷팅"""
    return f"${amount:.4f}"

def show_usage_summary():
    """사용량 요약 표시"""
    print_separator()
    print("📊 토큰 사용량 요약")
    print_separator()

    try:
        summary = token_monitor.get_usage_summary()

        # 일일 사용량
        daily = summary["daily"]
        print(f"📅 오늘 ({daily['date']})")
        print(f"   토큰: {format_number(daily['total_tokens'])} / {format_number(token_monitor.limits.daily_limit)} ({daily.get('limit_usage_percent', 0):.1f}%)")
        print(f"   비용: {format_currency(daily['total_cost'])}")
        print(f"   호출: {daily['usage_count']}회")

        # 월간 사용량
        monthly = summary["monthly"]
        print(f"\n📆 이번 달 ({monthly['month']})")
        print(f"   토큰: {format_number(monthly['total_tokens'])} / {format_number(token_monitor.limits.monthly_limit)} ({monthly.get('limit_usage_percent', 0):.1f}%)")
        print(f"   비용: {format_currency(monthly['total_cost'])}")
        print(f"   호출: {monthly['usage_count']}회")

        # 상태
        status = summary["status"]
        status_emoji = {"NORMAL": "✅", "WARNING": "⚠️", "CRITICAL": "🚨"}
        print(f"\n🔍 상태: {status_emoji.get(status, '❓')} {status}")

        # 모델별 사용량
        if daily["models"]:
            print(f"\n🤖 모델별 사용량 (오늘)")
            for model, data in daily["models"].items():
                print(f"   {model}: {format_number(data['tokens'])} 토큰, {format_currency(data['cost'])} ({data['count']}회)")

    except Exception as e:
        print(f"❌ 오류: {e}")

def show_recent_usage(days=7):
    """최근 N일간 사용량 표시"""
    print_separator()
    print(f"📈 최근 {days}일간 사용량")
    print_separator()

    try:
        for i in range(days):
            date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
            day_usage = token_monitor.get_daily_usage(date)

            if day_usage["total_tokens"] > 0:
                print(f"{date}: {format_number(day_usage['total_tokens'])} 토큰, {format_currency(day_usage['total_cost'])} ({day_usage['usage_count']}회)")
            else:
                print(f"{date}: 사용량 없음")

    except Exception as e:
        print(f"❌ 오류: {e}")

def show_limits():
    """한도 정보 표시"""
    print_separator()
    print("⚙️ 토큰 사용량 한도 설정")
    print_separator()

    limits = token_monitor.limits
    print(f"일일 한도: {format_number(limits.daily_limit)} 토큰 (2M TPD)")
    print(f"월간 한도: {format_number(limits.monthly_limit)} 토큰 (2M × 30일)")
    print(f"분당 한도: {format_number(limits.per_minute_limit)} 토큰 (200K TPM)")
    print(f"분당 요청: {limits.requests_per_minute} 요청 (500 RPM)")
    print(f"경고 임계값: {limits.warning_threshold * 100:.0f}%")
    print(f"알림 임계값: {limits.alert_threshold * 100:.0f}%")

    print(f"\n💰 모델별 비용 (1K 토큰당)")
    for model, costs in token_monitor.model_costs.items():
        print(f"   {model}: 입력 ${costs['input']:.4f}, 출력 ${costs['output']:.4f}")

def main():
    """메인 함수"""
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()

        if command == "summary":
            show_usage_summary()
        elif command == "recent":
            days = int(sys.argv[2]) if len(sys.argv) > 2 else 7
            show_recent_usage(days)
        elif command == "limits":
            show_limits()
        elif command == "help":
            print("사용법:")
            print("  python check_token_usage.py [command]")
            print("\n명령어:")
            print("  summary  - 사용량 요약 (기본값)")
            print("  recent [N] - 최근 N일간 사용량 (기본값: 7)")
            print("  limits   - 한도 설정 정보")
            print("  help     - 도움말")
        else:
            print(f"❌ 알 수 없는 명령어: {command}")
            print("사용 가능한 명령어: summary, recent, limits, help")
    else:
        # 기본값: 요약 표시
        show_usage_summary()

if __name__ == "__main__":
    main()
