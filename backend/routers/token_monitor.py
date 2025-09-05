"""
토큰 사용량 모니터링 API
"""
from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, HTTPException, Query
from modules.token_monitor import token_monitor

router = APIRouter(prefix="/api/token-monitor", tags=["Token Monitor"])

@router.get("/summary")
async def get_usage_summary():
    """토큰 사용량 요약 정보"""
    try:
        summary = token_monitor.get_usage_summary()
        return {
            "success": True,
            "data": summary
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"사용량 조회 실패: {str(e)}")

@router.get("/daily")
async def get_daily_usage(date: Optional[str] = Query(None, description="날짜 (YYYY-MM-DD)")):
    """일일 토큰 사용량 조회"""
    try:
        usage = token_monitor.get_daily_usage(date)
        return {
            "success": True,
            "data": usage
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"일일 사용량 조회 실패: {str(e)}")

@router.get("/monthly")
async def get_monthly_usage(month: Optional[str] = Query(None, description="월 (YYYY-MM)")):
    """월간 토큰 사용량 조회"""
    try:
        usage = token_monitor.get_monthly_usage(month)
        return {
            "success": True,
            "data": usage
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"월간 사용량 조회 실패: {str(e)}")

@router.get("/status")
async def get_usage_status():
    """토큰 사용량 상태 확인"""
    try:
        summary = token_monitor.get_usage_summary()
        daily = summary["daily"]
        monthly = summary["monthly"]

        # 상태별 메시지
        status_messages = {
            "NORMAL": "정상 사용량입니다.",
            "WARNING": "토큰 사용량이 경고 수준에 도달했습니다.",
            "CRITICAL": "토큰 사용량이 위험 수준에 도달했습니다!"
        }

        return {
            "success": True,
            "data": {
                "status": summary["status"],
                "message": status_messages.get(summary["status"], "알 수 없는 상태"),
                "daily_usage_percent": daily["limit_usage_percent"],
                "monthly_usage_percent": monthly["limit_usage_percent"],
                "daily_tokens": daily["total_tokens"],
                "monthly_tokens": monthly["total_tokens"],
                "daily_cost": daily["total_cost"],
                "monthly_cost": monthly["total_cost"]
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"상태 조회 실패: {str(e)}")

@router.get("/recent")
async def get_recent_usage(days: int = Query(7, description="조회할 일수")):
    """최근 N일간 토큰 사용량 조회"""
    try:
        recent_usage = []
        for i in range(days):
            date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
            day_usage = token_monitor.get_daily_usage(date)
            recent_usage.append(day_usage)

        return {
            "success": True,
            "data": {
                "period_days": days,
                "usage": recent_usage,
                "total_tokens": sum(day["total_tokens"] for day in recent_usage),
                "total_cost": sum(day["total_cost"] for day in recent_usage)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"최근 사용량 조회 실패: {str(e)}")

@router.get("/limits")
async def get_usage_limits():
    """토큰 사용량 한도 정보"""
    try:
        return {
            "success": True,
            "data": {
                "daily_limit": token_monitor.limits.daily_limit,
                "monthly_limit": token_monitor.limits.monthly_limit,
                "per_minute_limit": token_monitor.limits.per_minute_limit,
                "requests_per_minute": token_monitor.limits.requests_per_minute,
                "warning_threshold": token_monitor.limits.warning_threshold,
                "alert_threshold": token_monitor.limits.alert_threshold,
                "model_costs": token_monitor.model_costs,
                "model_info": {
                    "gpt-4o-mini": {
                        "tpm": "200,000",
                        "rpm": "500",
                        "tpd": "2,000,000"
                    }
                }
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"한도 정보 조회 실패: {str(e)}")
