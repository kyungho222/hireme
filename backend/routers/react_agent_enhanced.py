"""
향상된 ReAct 에이전트 라우터
기존 react_agent_router.py를 개선하여 진짜 ReAct 패턴을 구현
"""

import logging
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException
from modules.ai.services.react_agent_core import ReActAgent, ReActMemory
from pydantic import BaseModel

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/react-agent-v2", tags=["react-agent-v2"])

# ReAct 에이전트 인스턴스
react_agent = ReActAgent(max_steps=8)

# 세션 저장소 (실제로는 Redis나 DB 사용 권장)
agent_sessions = {}

class ReActRequest(BaseModel):
    """ReAct 에이전트 요청 모델"""
    user_id: str = "user_123"
    user_goal: str
    session_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None

class ReActResponse(BaseModel):
    """ReAct 에이전트 응답 모델"""
    success: bool
    session_id: str
    response: str
    steps: List[Dict[str, Any]]
    goal_achieved: bool
    total_steps: int
    timestamp: str
    suggestions: List[str] = []
    quick_actions: List[Dict[str, Any]] = []

@router.post("/start-session", response_model=ReActResponse)
async def start_react_session(request: ReActRequest):
    """ReAct 에이전트 세션 시작"""
    try:
        # 세션 ID 생성
        session_id = request.session_id or str(uuid.uuid4())

        # 세션 정보 저장
        agent_sessions[session_id] = {
            "session_id": session_id,
            "user_id": request.user_id,
            "created_at": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat(),
            "context": request.context or {}
        }

        logger.info(f"ReAct 에이전트 세션 시작: {session_id}")

        # 초기 응답
        initial_response = f"🤖 ReAct 에이전트가 시작되었습니다!\n\n"
        initial_response += f"목표: {request.user_goal}\n\n"
        initial_response += "추론-액션-관찰 루프를 통해 목표를 달성하겠습니다."

        return ReActResponse(
            success=True,
            session_id=session_id,
            response=initial_response,
            steps=[],
            goal_achieved=False,
            total_steps=0,
            timestamp=datetime.now().isoformat(),
            suggestions=[
                "작업을 시작하시겠습니까?",
                "추가 요구사항이 있으시면 말씀해주세요",
                "다른 목표로 변경하고 싶으시면 알려주세요"
            ],
            quick_actions=[
                {"title": "작업 시작", "action": "start_task", "icon": "🚀"},
                {"title": "요구사항 추가", "action": "add_requirements", "icon": "➕"},
                {"title": "목표 변경", "action": "change_goal", "icon": "🔄"}
            ]
        )

    except Exception as e:
        logger.error(f"ReAct 세션 시작 실패: {e}")
        raise HTTPException(status_code=500, detail=f"세션 시작 실패: {str(e)}")

@router.post("/process-task", response_model=ReActResponse)
async def process_react_task(request: ReActRequest):
    """ReAct 에이전트 작업 처리"""
    try:
        session_id = request.session_id

        if not session_id or session_id not in agent_sessions:
            raise HTTPException(status_code=400, detail="유효하지 않은 세션 ID")

        session = agent_sessions[session_id]

        # ReAct 에이전트로 작업 처리
        logger.info(f"ReAct 작업 처리 시작: {request.user_goal}")

        result = await react_agent.process_task(
            user_goal=request.user_goal,
            initial_context=request.context or {}
        )

        # 세션 업데이트
        session["last_updated"] = datetime.now().isoformat()
        session["last_goal"] = request.user_goal
        session["last_result"] = result

        # 응답 생성
        if result["success"]:
            response_text = result["response"]
            suggestions = [
                "추가 작업이 필요하시면 말씀해주세요",
                "결과를 수정하고 싶으시면 알려주세요",
                "다른 목표로 작업하시겠습니까?"
            ]
            quick_actions = [
                {"title": "추가 작업", "action": "additional_task", "icon": "➕"},
                {"title": "결과 수정", "action": "modify_result", "icon": "✏️"},
                {"title": "새 목표", "action": "new_goal", "icon": "🎯"}
            ]
        else:
            response_text = f"❌ 작업 처리 중 오류가 발생했습니다: {result.get('error', '알 수 없는 오류')}"
            suggestions = [
                "다시 시도해보시겠습니까?",
                "다른 방법으로 접근해보시겠습니까?",
                "문제를 더 자세히 설명해주세요"
            ]
            quick_actions = [
                {"title": "다시 시도", "action": "retry", "icon": "🔄"},
                {"title": "다른 방법", "action": "alternative", "icon": "🛠️"},
                {"title": "문제 설명", "action": "explain_problem", "icon": "💬"}
            ]

        return ReActResponse(
            success=result["success"],
            session_id=session_id,
            response=response_text,
            steps=result.get("steps", []),
            goal_achieved=result.get("goal_achieved", False),
            total_steps=result.get("total_steps", 0),
            timestamp=datetime.now().isoformat(),
            suggestions=suggestions,
            quick_actions=quick_actions
        )

    except Exception as e:
        logger.error(f"ReAct 작업 처리 실패: {e}")
        raise HTTPException(status_code=500, detail=f"작업 처리 실패: {str(e)}")

@router.get("/session/{session_id}")
async def get_session_info(session_id: str):
    """세션 정보 조회"""
    if session_id not in agent_sessions:
        raise HTTPException(status_code=404, detail="세션을 찾을 수 없습니다")

    session = agent_sessions[session_id]
    return {
        "session_id": session_id,
        "user_id": session["user_id"],
        "created_at": session["created_at"],
        "last_updated": session["last_updated"],
        "last_goal": session.get("last_goal", ""),
        "has_result": "last_result" in session
    }

@router.delete("/session/{session_id}")
async def delete_session(session_id: str):
    """세션 삭제"""
    if session_id not in agent_sessions:
        raise HTTPException(status_code=404, detail="세션을 찾을 수 없습니다")

    del agent_sessions[session_id]
    return {"message": "세션이 삭제되었습니다"}

@router.get("/sessions")
async def list_sessions():
    """활성 세션 목록 조회"""
    return {
        "sessions": [
            {
                "session_id": sid,
                "user_id": session["user_id"],
                "created_at": session["created_at"],
                "last_updated": session["last_updated"]
            }
            for sid, session in agent_sessions.items()
        ],
        "total": len(agent_sessions)
    }

# 테스트 엔드포인트
@router.post("/test")
async def test_react_agent():
    """ReAct 에이전트 테스트"""
    try:
        test_goals = [
            "React 개발자 채용공고를 작성해주세요",
            "최신 AI 기술 트렌드를 검색해주세요",
            "지원자 데이터를 분석해주세요"
        ]

        results = []
        for goal in test_goals:
            result = await react_agent.process_task(goal)
            results.append({
                "goal": goal,
                "success": result["success"],
                "total_steps": result.get("total_steps", 0),
                "goal_achieved": result.get("goal_achieved", False),
                "response_preview": result["response"][:200] + "..." if len(result["response"]) > 200 else result["response"]
            })

        return {
            "test_results": results,
            "agent_status": "정상 동작",
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"ReAct 에이전트 테스트 실패: {e}")
        return {
            "test_results": [],
            "agent_status": f"오류: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }
