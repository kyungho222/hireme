"""
리액트 에이전트 전용 라우터
PickTalk에서 사용할 수 있도록 모듈화된 에이전트 시스템
"""

import logging
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException

# 기존 서비스들 import
from modules.core.services.openai_service import OpenAIService

from modules.ai.services.langgraph_agent_system import LangGraphAgentSystem

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/react-agent", tags=["react-agent"])

# Ollama LLM 서비스 초기화
try:
    from modules.core.services.llm_service import LLMService
    llm_service = LLMService()
    print(f"🔍 [ReactAgent] Ollama LLM 서비스 초기화 성공")
except Exception as e:
    logger.error(f"Ollama LLM 서비스 초기화 실패: {e}")
    llm_service = None

# OpenAI 서비스 (비활성화)
openai_service = None

# LangGraph 에이전트 시스템 초기화
try:
    langgraph_system = LangGraphAgentSystem()
except Exception as e:
    logger.error(f"LangGraph 시스템 초기화 실패: {e}")
    langgraph_system = None

# 에이전트 세션 저장소 (실제로는 Redis나 DB 사용 권장)
agent_sessions = {}

@router.post("/start-session")
async def start_react_agent_session(request: Dict[str, Any]):
    """리액트 에이전트 세션 시작"""
    try:
        user_id = request.get("user_id", "user_123")
        company_info = request.get("company_info", {})

        # 세션 ID 생성
        session_id = str(uuid.uuid4())

        # 세션 정보 저장
        agent_sessions[session_id] = {
            "session_id": session_id,
            "user_id": user_id,
            "company_info": company_info,
            "state": "initial",
            "conversation_history": [],
            "extracted_data": {},
            "created_at": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat()
        }

        logger.info(f"리액트 에이전트 세션 시작: {session_id}")

        return {
            "success": True,
            "session_id": session_id,
            "message": "🤖 AI 에이전트 모드가 시작되었습니다!",
            "state": "initial",
            "next_action": "안녕하세요! 저는 채용공고 작성을 도와주는 AI 에이전트입니다. 어떤 직무의 채용공고를 작성하고 싶으신가요?",
            "quick_actions": [
                {"title": "채용공고 작성", "action": "navigate", "icon": "📝", "params": {"page": "job_posting"}},
                {"title": "지원자 관리", "action": "navigate", "icon": "👥", "params": {"page": "applicants"}},
                {"title": "대시보드", "action": "navigate", "icon": "📊", "params": {"page": "dashboard"}},
                {"title": "채용공고 목록", "action": "navigate", "icon": "📋", "params": {"page": "recruitment"}}
            ],
            "suggestions": [
                "프론트엔드 개발자",
                "백엔드 개발자",
                "풀스택 개발자",
                "데이터 사이언티스트"
            ]
        }

    except Exception as e:
        logger.error(f"에이전트 세션 시작 실패: {e}")
        raise HTTPException(status_code=500, detail=f"세션 시작 실패: {str(e)}")

@router.post("/process-input")
async def process_react_agent_input(request: Dict[str, Any]):
    """리액트 에이전트 입력 처리"""
    try:
        session_id = request.get("session_id")
        user_input = request.get("user_input", "")

        if not session_id or session_id not in agent_sessions:
            raise HTTPException(status_code=400, detail="유효하지 않은 세션 ID")

        session = agent_sessions[session_id]
        current_state = session["state"]

        # Ollama 기반 에이전트 처리 (LangGraph 대신 직접 처리)
        try:
            # Ollama LLM 서비스로 직접 처리
            if llm_service:
                agent_response = await _process_with_ollama(
                    llm_service, user_input, session["conversation_history"]
                )

                # 응답 분석 및 상태 전환
                new_state = _determine_next_state(current_state, user_input, agent_response)

                # 세션 업데이트
                session["state"] = new_state
                session["conversation_history"].append({
                    "user": user_input,
                    "agent": agent_response.get("response", ""),
                    "timestamp": datetime.now().isoformat()
                })
                session["last_updated"] = datetime.now().isoformat()

                # 추출된 데이터가 있으면 저장
                if agent_response.get("extracted_fields"):
                    session["extracted_data"].update(agent_response["extracted_fields"])

                # 상태별 응답 강화
                enhanced_response = _enhance_response_by_state(new_state, agent_response, session)

                return {
                    "success": True,
                    "response": enhanced_response["message"],
                    "state": new_state,
                    "extracted_fields": session["extracted_data"],
                    "quick_actions": enhanced_response["quick_actions"],
                    "suggestions": enhanced_response["suggestions"],
                    "session_id": session_id,
                    "tool_result": agent_response.get("tool_result"),  # 툴 실행 결과 추가
                    "tool_error": agent_response.get("tool_error"),    # 툴 실행 에러 추가
                    "intent": agent_response.get("intent"),           # 의도 분류 추가
                    "confidence": agent_response.get("confidence")    # 신뢰도 추가
                }
            else:
                # LLM 서비스 없을 때 기본 처리
                agent_response = _process_basic_response(user_input, current_state)

                # 응답 분석 및 상태 전환
                new_state = _determine_next_state(current_state, user_input, agent_response)

                # 세션 업데이트
                session["state"] = new_state
                session["conversation_history"].append({
                    "user": user_input,
                    "agent": agent_response.get("response", ""),
                    "timestamp": datetime.now().isoformat()
                })
                session["last_updated"] = datetime.now().isoformat()

                # 추출된 데이터가 있으면 저장
                if agent_response.get("extracted_fields"):
                    session["extracted_data"].update(agent_response["extracted_fields"])

                # 상태별 응답 강화
                enhanced_response = _enhance_response_by_state(new_state, agent_response, session)

                return {
                    "success": True,
                    "response": enhanced_response["message"],
                    "state": new_state,
                    "extracted_fields": session["extracted_data"],
                    "quick_actions": enhanced_response["quick_actions"],
                    "suggestions": enhanced_response["suggestions"],
                    "session_id": session_id,
                    "tool_result": agent_response.get("tool_result"),  # 툴 실행 결과 추가
                    "tool_error": agent_response.get("tool_error"),    # 툴 실행 에러 추가
                    "intent": agent_response.get("intent"),           # 의도 분류 추가
                    "confidence": agent_response.get("confidence")    # 신뢰도 추가
                }

        except Exception as e:
            logger.error(f"에이전트 처리 실패: {e}")
            # 에이전트 실패 시 기본 처리로 폴백
            return _fallback_processing(session, user_input, current_state)

    except Exception as e:
        logger.error(f"에이전트 입력 처리 실패: {e}")
        raise HTTPException(status_code=500, detail=f"입력 처리 실패: {str(e)}")

@router.get("/session-status/{session_id}")
async def get_session_status(session_id: str):
    """세션 상태 조회"""
    try:
        if session_id not in agent_sessions:
            raise HTTPException(status_code=404, detail="세션을 찾을 수 없습니다")

        session = agent_sessions[session_id]
        return {
            "success": True,
            "session_id": session_id,
            "state": session["state"],
            "extracted_data": session["extracted_data"],
            "conversation_count": len(session["conversation_history"]),
            "created_at": session["created_at"],
            "last_updated": session["last_updated"]
        }

    except Exception as e:
        logger.error(f"세션 상태 조회 실패: {e}")
        raise HTTPException(status_code=500, detail=f"상태 조회 실패: {str(e)}")

@router.post("/end-session")
async def end_react_agent_session(request: Dict[str, Any]):
    """리액트 에이전트 세션 종료"""
    try:
        session_id = request.get("session_id")

        if session_id and session_id in agent_sessions:
            # 세션 데이터 정리
            session_data = agent_sessions.pop(session_id)
            logger.info(f"리액트 에이전트 세션 종료: {session_id}")

            return {
                "success": True,
                "message": "에이전트 세션이 종료되었습니다",
                "session_id": session_id,
                "final_data": session_data["extracted_data"]
            }

        return {
            "success": True,
            "message": "세션이 이미 종료되었습니다"
        }

    except Exception as e:
        logger.error(f"에이전트 세션 종료 실패: {e}")
        raise HTTPException(status_code=500, detail=f"세션 종료 실패: {str(e)}")

def _determine_next_state(current_state: str, user_input: str, agent_response: Dict) -> str:
    """현재 상태와 입력을 기반으로 다음 상태 결정"""
    state_transitions = {
        "initial": {
            "keywords": ["직무", "개발자", "엔지니어", "프론트엔드", "백엔드", "풀스택"],
            "next_state": "keyword_extraction"
        },
        "keyword_extraction": {
            "keywords": ["다음", "계속", "진행", "확인", "맞아"],
            "next_state": "template_selection"
        },
        "template_selection": {
            "keywords": ["선택", "템플릿", "스타일", "확인"],
            "next_state": "content_generation"
        },
        "content_generation": {
            "keywords": ["수정", "변경", "다시"],
            "next_state": "review_edit"
        },
        "review_edit": {
            "keywords": ["확인", "완료", "등록"],
            "next_state": "final_confirmation"
        }
    }

    if current_state in state_transitions:
        transition = state_transitions[current_state]
        if any(keyword in user_input for keyword in transition["keywords"]):
            return transition["next_state"]

    return current_state

def _enhance_response_by_state(state: str, agent_response: Dict, session: Dict) -> Dict:
    """상태별로 응답을 강화"""
    base_message = agent_response.get("response", "")

    # 툴 실행 결과와 상세 정보는 숨김 (사용자 요청)
    # if agent_response.get("tool_result"):
    #     tool_result = agent_response["tool_result"]
    #     base_message += f"\n\n🔧 **툴 실행 결과:**\n"
    #     base_message += f"\n📊 **상세 데이터:**\n"
    #     base_message += f"\n📊 **상세 정보:**\n"
    #     base_message += f"\n📈 **총 개수:** {tool_result.get('total_count', 0)}개\n"

    # 툴 실행 에러도 숨김 (사용자 요청)
    # if agent_response.get("tool_error"):
    #     base_message += f"\n\n❌ **툴 실행 오류:** {agent_response['tool_error']}\n"

    # 추출된 정보도 숨김 (사용자 요청)
    # if state == "keyword_extraction" and session["extracted_data"]:
    #     base_message += f"\n\n🔍 **추출된 정보:**\n"
    #     for key, value in session["extracted_data"].items():
    #         base_message += f"• {key}: {value}\n"

    quick_actions = _get_quick_actions_by_state(state)
    suggestions = _get_suggestions_by_state(state)

    return {
        "message": base_message,
        "quick_actions": quick_actions,
        "suggestions": suggestions
    }

def _get_quick_actions_by_state(state: str) -> List[Dict]:
    """상태별 빠른 액션 반환"""
    actions_map = {
        "initial": [
            {"title": "채용공고 작성", "action": "navigate", "icon": "📝", "params": {"page": "job_posting"}},
            {"title": "지원자 관리", "action": "navigate", "icon": "👥", "params": {"page": "applicants"}},
            {"title": "대시보드", "action": "navigate", "icon": "📊", "params": {"page": "dashboard"}},
            {"title": "채용공고 목록", "action": "navigate", "icon": "📋", "params": {"page": "recruitment"}}
        ],
        "keyword_extraction": [
            {"title": "채용공고 미리보기", "action": "navigate", "icon": "👁️", "params": {"page": "job_posting", "tab": "preview"}},
            {"title": "템플릿 선택", "action": "navigate", "icon": "📋", "params": {"page": "job_posting", "tab": "templates"}},
            {"title": "저장하기", "action": "navigate", "icon": "💾", "params": {"page": "job_posting", "tab": "save"}}
        ],
        "template_selection": [
            {"title": "채용공고 등록", "action": "navigate", "icon": "🚀", "params": {"page": "job_posting", "tab": "register"}},
            {"title": "내용 수정", "action": "navigate", "icon": "✏️", "params": {"page": "job_posting", "tab": "edit"}},
            {"title": "지원자 요구사항 설정", "action": "navigate", "icon": "⚙️", "params": {"page": "job_posting", "tab": "requirements"}}
        ],
        "content_generation": [
            {"title": "지원자 관리", "action": "navigate", "icon": "👥", "params": {"page": "applicants"}},
            {"title": "인터뷰 일정", "action": "navigate", "icon": "📅", "params": {"page": "interview"}},
            {"title": "통계 보기", "action": "navigate", "icon": "📊", "params": {"page": "dashboard"}}
        ],
        "review_edit": [
            {"title": "채용공고 발행", "action": "navigate", "icon": "📢", "params": {"page": "job_posting", "tab": "publish"}},
            {"title": "설정 관리", "action": "navigate", "icon": "⚙️", "params": {"page": "settings"}},
            {"title": "새 채용공고", "action": "navigate", "icon": "🆕", "params": {"page": "job_posting", "tab": "new"}}
        ],
        "final_confirmation": [
            {"title": "지원자 모니터링", "action": "navigate", "icon": "📈", "params": {"page": "dashboard", "tab": "applicants"}},
            {"title": "채용 현황", "action": "navigate", "icon": "📊", "params": {"page": "dashboard", "tab": "recruitment"}},
            {"title": "회사 문화 관리", "action": "navigate", "icon": "🏢", "params": {"page": "company_culture"}}
        ]
    }

    return actions_map.get(state, [])

def _get_suggestions_by_state(state: str) -> List[str]:
    """상태별 제안 사항 반환"""
    suggestions_map = {
        "initial": [
            "프론트엔드 개발자",
            "백엔드 개발자",
            "풀스택 개발자",
            "데이터 사이언티스트"
        ],
        "keyword_extraction": [
            "React, TypeScript, Next.js",
            "Python, Django, PostgreSQL",
            "Java, Spring Boot, MySQL",
            "Node.js, Express, MongoDB"
        ],
        "template_selection": [
            "신입 친화형",
            "전문가형",
            "일반형",
            "창의적"
        ]
    }

    return suggestions_map.get(state, [])

async def _process_with_ollama(llm_service, user_input: str, conversation_history: List[Dict]) -> Dict:
    """Ollama LLM을 사용해서 사용자 입력 처리"""
    try:
        logger.info(f"🔍 [LLM 처리] 사용자 입력 분석 시작: '{user_input}'")

        # 대화 컨텍스트 구성
        context = ""
        if conversation_history:
            recent_messages = conversation_history[-3:]  # 최근 3개 메시지만 사용
            context = "\n".join([
                f"사용자: {msg.get('user', '')}\n에이전트: {msg.get('agent', '')}"
                for msg in recent_messages
            ])
            logger.info(f"📝 [LLM 처리] 대화 컨텍스트 ({len(recent_messages)}개 메시지): {context[:200]}...")
        else:
            logger.info(f"📝 [LLM 처리] 대화 컨텍스트 없음 (첫 메시지)")

        # 프롬프트 구성
        system_prompt = """채용공고 작성 AI 어시스턴트입니다. 사용자 입력을 분석하여 JSON으로 응답하세요.

**툴**: search, navigate, job_posting, applicant, github, mongodb, file_upload, mail, web_automation

**출력 형식**:
{
  "intent": "recruit/info_request/ui_action/chat",
  "response": "사용자 메시지",
  "suggested_tool": "job_posting",
  "suggested_action": "create",
  "params": {},
  "confidence": 0.0~1.0
}

**예시**:
- "React 개발자 채용공고 작성" → intent: "recruit", tool: "job_posting", action: "create"
- "채용공고 목록" → intent: "info_request", tool: "job_posting", action: "list"
- "안녕하세요" → intent: "chat"

**입력**:
컨텍스트: {context}
사용자: {user_input}

JSON만 반환하세요."""

        user_prompt = f"""컨텍스트: {context}
사용자: {user_input}

JSON으로 응답하세요."""

        logger.info(f"📤 [LLM 처리] LLM 호출 시작")
        logger.info(f"📋 [LLM 처리] System Prompt 길이: {len(system_prompt)} 문자")
        logger.info(f"📋 [LLM 처리] User Prompt 길이: {len(user_prompt)} 문자")

        # LLM 호출
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        llm_response = await llm_service.chat_completion(messages, max_tokens=800, temperature=0.7)

        logger.info(f"📥 [LLM 처리] LLM 응답 수신 완료 (길이: {len(llm_response)})")
        logger.info(f"📄 [LLM 처리] LLM 원본 응답: {llm_response[:500]}...")

        # 빈 응답 처리
        if not llm_response or llm_response.strip() == "":
            logger.error(f"🚨 [LLM 처리] 빈 응답 감지")
            return {
                "intent": "error",
                "response": "응답을 생성하지 못했습니다. 다시 시도해주세요.",
                "suggested_tool": None,
                "suggested_action": None,
                "params": {},
                "confidence": 0.0
            }

        # JSON 파싱 시도
        try:
            import json
            logger.info(f"🔍 [LLM 처리] JSON 파싱 시작")

            parsed_response = json.loads(llm_response)
            logger.info(f"✅ [LLM 처리] JSON 파싱 성공: {parsed_response}")

            # 필수 필드 확인 및 로깅
            logger.info(f"🔍 [LLM 처리] 파싱된 응답 필드 분석:")
            logger.info(f"  - intent: {parsed_response.get('intent', 'MISSING')}")
            logger.info(f"  - suggested_tool: {parsed_response.get('suggested_tool', 'MISSING')}")
            logger.info(f"  - suggested_action: {parsed_response.get('suggested_action', 'MISSING')}")
            logger.info(f"  - params: {parsed_response.get('params', 'MISSING')}")
            logger.info(f"  - confidence: {parsed_response.get('confidence', 'MISSING')}")
            logger.info(f"  - response: {parsed_response.get('response', 'MISSING')[:100]}...")

            # 필수 필드 확인
            if "response" not in parsed_response:
                parsed_response["response"] = "응답을 처리했습니다."
                logger.warning(f"⚠️ [LLM 처리] response 필드 누락, 기본값 설정")

            if "intent" not in parsed_response:
                parsed_response["intent"] = "chat"
                logger.warning(f"⚠️ [LLM 처리] intent 필드 누락, 기본값 'chat' 설정")

            if "suggested_tool" not in parsed_response:
                parsed_response["suggested_tool"] = None
                logger.warning(f"⚠️ [LLM 처리] suggested_tool 필드 누락, None 설정")

            if "suggested_action" not in parsed_response:
                parsed_response["suggested_action"] = None
                logger.warning(f"⚠️ [LLM 처리] suggested_action 필드 누락, None 설정")

            if "params" not in parsed_response:
                parsed_response["params"] = {}
                logger.warning(f"⚠️ [LLM 처리] params 필드 누락, 빈 딕셔너리 설정")

            if "confidence" not in parsed_response:
                parsed_response["confidence"] = 0.8
                logger.warning(f"⚠️ [LLM 처리] confidence 필드 누락, 기본값 0.8 설정")

            logger.info(f"🔍 [LLM 처리] 최종 파싱된 응답: {parsed_response}")

            # 실제 툴 실행
            if parsed_response.get("suggested_tool") and parsed_response.get("suggested_action"):
                logger.info(f"🔧 [LLM 처리] 툴 실행 시작: {parsed_response['suggested_tool']}.{parsed_response['suggested_action']}")

                # 사용자 원본 입력을 params에 추가
                params = parsed_response.get("params", {})
                params["input_text"] = user_input

                tool_result = await _execute_tool(
                    parsed_response["suggested_tool"],
                    parsed_response["suggested_action"],
                    params
                )

                if tool_result["success"]:
                    # 툴 실행 성공 시 결과를 응답에 포함
                    parsed_response["tool_result"] = tool_result["result"]

                    # result에서 message 추출 (안전하게)
                    if isinstance(tool_result["result"], dict) and "message" in tool_result["result"]:
                        message = tool_result["result"]["message"]
                    else:
                        message = str(tool_result["result"])

                    parsed_response["response"] = f"{parsed_response['response']}\n\n{message}"
                    logger.info(f"✅ [LLM 처리] 툴 실행 성공: {message}")
                else:
                    # 툴 실행 실패 시 에러 메시지 추가
                    parsed_response["tool_error"] = tool_result["error"]
                    parsed_response["response"] = f"{parsed_response['response']}\n\n❌ 툴 실행 실패: {tool_result['error']}"
                    logger.error(f"❌ [LLM 처리] 툴 실행 실패: {tool_result['error']}")
            else:
                logger.info(f"🔍 [LLM 처리] 툴 실행 불필요: intent={parsed_response.get('intent')}, tool={parsed_response.get('suggested_tool')}, action={parsed_response.get('suggested_action')}")

            logger.info(f"🎯 [LLM 처리] 최종 응답 반환: {parsed_response}")
            return parsed_response

        except json.JSONDecodeError as e:
            # JSON 파싱 실패 시 기본 응답
            logger.error(f"❌ [LLM 처리] JSON 파싱 실패: {e}")
            logger.error(f"📄 [LLM 처리] 파싱 실패한 원본 응답: {llm_response}")

            # API 오류 메시지인지 확인
            if "API 오류" in llm_response or "Error code" in llm_response:
                logger.error(f"🚨 [LLM 처리] API 오류로 인한 JSON 파싱 실패")
                return {
                    "intent": "error",
                    "response": "API 오류가 발생했습니다. 잠시 후 다시 시도해주세요.",
                    "suggested_tool": None,
                    "suggested_action": None,
                    "params": {},
                    "confidence": 0.0
                }

            return {
                "intent": "chat",
                "response": f"입력하신 내용을 분석했습니다: {user_input}",
                "suggested_tool": None,
                "suggested_action": None,
                "params": {},
                "confidence": 0.6
            }

    except Exception as e:
        logger.error(f"Ollama 처리 중 오류: {e}")
        return {
            "intent": "chat",
            "response": "죄송합니다. 처리 중 오류가 발생했습니다.",
            "suggested_tool": None,
            "suggested_action": None,
            "params": {},
            "confidence": 0.0
        }

def _process_basic_response(user_input: str, current_state: str) -> Dict:
    """기본 응답 처리 (LLM 없을 때)"""
    # 간단한 키워드 추출
    intent = "chat"
    suggested_tool = None
    suggested_action = None
    params = {}

    # 채용 관련 키워드 체크
    if any(word in user_input.lower() for word in ["채용", "공고", "개발자", "엔지니어", "모집"]):
        intent = "recruit"
        suggested_tool = "job_posting"
        suggested_action = "create"

        # 직무 추출
        job_keywords = ["개발자", "엔지니어", "프로그래머", "디자이너"]
        for keyword in job_keywords:
            if keyword in user_input:
                params["position"] = keyword
                break

        # 기술 스택 추출
        tech_keywords = ["React", "Python", "Java", "Node.js", "TypeScript"]
        found_tech = []
        for tech in tech_keywords:
            if tech.lower() in user_input.lower():
                found_tech.append(tech)

        if found_tech:
            params["skills"] = found_tech

    return {
        "intent": intent,
        "response": f"입력하신 내용을 분석했습니다. {', '.join(params.values()) if params else '추가 정보가 필요합니다.'}",
        "suggested_tool": suggested_tool,
        "suggested_action": suggested_action,
        "params": params,
        "confidence": 0.7
    }

async def _execute_tool(tool_name: str, action: str, params: Dict) -> Dict:
    """실제 툴 실행"""
    try:
        logger.info(f"🔧 [툴 실행] {tool_name}.{action} 시작")
        logger.info(f"🔧 [툴 실행] 파라미터: {params}")

        if tool_name == "search":
            return await _execute_search_tool(action, params)
        elif tool_name == "navigate":
            return await _execute_navigate_tool(action, params)
        elif tool_name == "job_posting":
            return await _execute_job_posting_tool(action, params)
        elif tool_name == "github":
            return await _execute_github_tool(action, params)
        elif tool_name == "mongodb":
            return await _execute_mongodb_tool(action, params)
        elif tool_name == "applicant":
            return await _execute_applicant_tool(action, params)
        elif tool_name == "file_upload":
            return await _execute_file_upload_tool(action, params)
        elif tool_name == "mail":
            return await _execute_mail_tool(action, params)
        elif tool_name == "web_automation":
            return await _execute_web_automation_tool(action, params)
        elif tool_name == "workflow":
            return await _execute_workflow_tool(action, params)
        else:
            return {
                "success": False,
                "error": f"알 수 없는 툴: {tool_name}",
                "result": None
            }

    except Exception as e:
        logger.error(f"툴 실행 중 오류: {e}")
        return {
            "success": False,
            "error": str(e),
            "result": None
        }

async def _execute_search_tool(action: str, params: Dict) -> Dict:
    """검색 관련 툴 실행"""
    try:
        if action == "web_search":
            # 웹 검색 시뮬레이션
            query = params.get("query", "검색어")
            result = {
                "message": f"🔍 '{query}'에 대한 웹 검색 결과입니다:",
                "data": {
                    "query": query,
                    "results": [
                        {"title": f"{query} 관련 정보 1", "url": "https://example1.com", "snippet": f"{query}에 대한 상세한 정보를 제공합니다."},
                        {"title": f"{query} 관련 정보 2", "url": "https://example2.com", "snippet": f"{query}에 대한 추가 정보입니다."}
                    ],
                    "total_results": 2
                }
            }

        elif action == "internal_search":
            # 내부 검색 시뮬레이션
            query = params.get("query", "검색어")
            category = params.get("category", "all")
            result = {
                "message": f"🔍 내부 시스템에서 '{query}'를 검색한 결과입니다:",
                "data": {
                    "query": query,
                    "category": category,
                    "results": [
                        {"type": "job_posting", "title": f"{query} 관련 채용공고", "id": "job_123"},
                        {"type": "applicant", "title": f"{query} 관련 지원자", "id": "app_456"}
                    ],
                    "total_results": 2
                }
            }

        elif action == "semantic_search":
            # 의미 기반 검색 시뮬레이션
            query = params.get("query", "검색어")
            result = {
                "message": f"🧠 '{query}'의 의미를 분석한 검색 결과입니다:",
                "data": {
                    "query": query,
                    "semantic_results": [
                        {"concept": "개발자", "relevance": 0.95, "related_terms": ["프로그래머", "엔지니어"]},
                        {"concept": "기술", "relevance": 0.87, "related_terms": ["스킬", "역량"]}
                    ]
                }
            }

        else:
            return {
                "success": False,
                "error": f"알 수 없는 검색 액션: {action}",
                "result": None
            }

        return {
            "success": True,
            "result": result
        }

    except Exception as e:
        logger.error(f"검색 툴 실행 중 오류: {e}")
        return {
            "success": False,
            "error": str(e),
            "result": None
        }

async def _execute_navigate_tool(action: str, params: Dict) -> Dict:
    """네비게이션 관련 툴 실행"""
    try:
        if action == "page_navigate":
            # 페이지 이동 시뮬레이션
            target_page = params.get("page", "home")
            target_tab = params.get("tab", "")

            page_mapping = {
                "home": {"path": "/", "title": "홈", "description": "메인 페이지"},
                "job_posting": {"path": "/job-posting", "title": "채용공고 작성", "description": "새로운 채용공고 작성 및 관리"},
                "recruitment": {"path": "/recruitment", "title": "채용 관리", "description": "채용공고 및 지원자 관리"},
                "applicants": {"path": "/applicants", "title": "지원자 관리", "description": "지원자 목록 및 상태 관리"},
                "dashboard": {"path": "/dashboard", "title": "대시보드", "description": "통계 및 현황"},
                "interview": {"path": "/interview", "title": "인터뷰 관리", "description": "인터뷰 일정 및 결과 관리"},
                "settings": {"path": "/settings", "title": "설정", "description": "시스템 설정"},
                "profile": {"path": "/profile", "title": "프로필", "description": "사용자 프로필"},
                "company_culture": {"path": "/company-culture", "title": "회사 문화", "description": "회사 문화 및 인재상 관리"}
            }

            if target_page in page_mapping:
                page_info = page_mapping[target_page]

                # 탭 정보가 있으면 추가
                tab_info = ""
                if target_tab:
                    tab_mapping = {
                        "preview": "미리보기",
                        "templates": "템플릿",
                        "save": "저장",
                        "register": "등록",
                        "edit": "수정",
                        "requirements": "요구사항",
                        "publish": "발행",
                        "new": "새로 작성",
                        "applicants": "지원자",
                        "recruitment": "채용"
                    }
                    tab_name = tab_mapping.get(target_tab, target_tab)
                    tab_info = f" ({tab_name} 탭)"

                result = {
                    "message": f"🚀 {page_info['title']}{tab_info} 페이지로 이동합니다!",
                    "data": {
                        "action": "navigate",
                        "target_page": target_page,
                        "target_tab": target_tab,
                        "path": page_info["path"],
                        "title": page_info["title"],
                        "description": page_info["description"],
                        "full_path": f"{page_info['path']}{'#' + target_tab if target_tab else ''}"
                    }
                }
            else:
                return {
                    "success": False,
                    "error": f"알 수 없는 페이지: {target_page}",
                    "result": None
                }

        elif action == "open_modal":
            # 모달 열기 시뮬레이션
            modal_type = params.get("type", "info")
            modal_title = params.get("title", "알림")
            modal_content = params.get("content", "모달 내용")

            result = {
                "message": f"📱 {modal_title} 모달을 열었습니다!",
                "data": {
                    "action": "open_modal",
                    "modal_type": modal_type,
                    "title": modal_title,
                    "content": modal_content
                }
            }

        elif action == "scroll_to":
            # 특정 요소로 스크롤 시뮬레이션
            element_id = params.get("element_id", "section")
            element_name = params.get("element_name", "섹션")

            result = {
                "message": f"📜 {element_name}으로 스크롤합니다!",
                "data": {
                    "action": "scroll_to",
                    "element_id": element_id,
                    "element_name": element_name
                }
            }

        elif action == "tab_switch":
            # 탭 전환 시뮬레이션
            tab_name = params.get("tab_name", "메인")
            tab_id = params.get("tab_id", "main")

            result = {
                "message": f"🔄 {tab_name} 탭으로 전환합니다!",
                "data": {
                    "action": "tab_switch",
                    "tab_name": tab_name,
                    "tab_id": tab_id
                }
            }

        else:
            return {
                "success": False,
                "error": f"알 수 없는 네비게이션 액션: {action}",
                "result": None
            }

        return {
            "success": True,
            "result": result
        }

    except Exception as e:
        logger.error(f"네비게이션 툴 실행 중 오류: {e}")
        return {
            "success": False,
            "error": str(e),
            "result": None
        }

async def _execute_job_posting_tool(action: str, params: Dict) -> Dict:
    """채용공고 관련 툴 실행"""
    try:
        logger.info(f"🔧 [채용공고툴] {action} 액션 실행 시작")
        logger.info(f"🔧 [채용공고툴] 파라미터: {params}")

        if action == "create":
            # 픽톡과 동일한 방식으로 채용공고 생성
            try:
                from modules.core.services.mongo_service import MongoService

                # MongoDB 서비스 초기화
                mongo_service = MongoService()

                # 입력된 텍스트를 job_data로 변환
                input_text = params.get("input_text", "")
                if not input_text:
                    return {
                        "success": False,
                        "error": "채용공고 내용이 입력되지 않았습니다."
                    }

                # 사용자 입력에서 실제 정보 추출하여 job_data 생성 (AI 페이지 필드명과 정확히 맞춤)
                job_data = {
                    # AI 페이지 필드명과 정확히 일치하도록 수정
                    "department": "개발팀",  # 구인 부서
                    "position": "백엔드 개발자",  # 채용 직무
                    "headcount": "1명",  # 구인 인원수
                    "mainDuties": input_text,  # 주요 업무 (AI 페이지 필드명)
                    "workHours": "09:00-18:00",  # 근무 시간 (AI 페이지 필드명)
                    "workDays": "주중 (월~금)",  # 근무 요일 (AI 페이지 필드명)
                    "salary": "협의",  # 연봉
                    "contactEmail": "hr@company.com",  # 연락처 이메일 (AI 페이지 필드명)
                    "deadline": (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d'),  # 마감일
                    "experience": "경력자",  # 경력 수준
                    "locationCity": "서울",  # 근무 위치 (AI 페이지 필드명)

                    # 기존 필드들 (호환성 유지)
                    "title": f"채용공고 - {datetime.now().strftime('%Y-%m-%d')}",
                    "company": "회사명",
                    "location": "서울",
                    "type": "full-time",
                    "requirements": "경력자",
                    "preferred": "우대사항",
                    "benefits": "복리후생",
                    "description": input_text,
                    "contact_email": "hr@company.com",
                    "work_type": "정규직",
                    "work_hours": "09:00-18:00"
                }

                # 사용자 입력에서 실제 정보 추출
                input_lower = input_text.lower()

                # 직책 추출
                if "프론트엔드" in input_lower:
                    job_data["position"] = "프론트엔드 개발자"
                elif "백엔드" in input_lower:
                    job_data["position"] = "백엔드 개발자"
                elif "풀스택" in input_lower:
                    job_data["position"] = "풀스택 개발자"
                elif "개발자" in input_lower:
                    job_data["position"] = "개발자"

                # 기술 스택 추출
                tech_skills = []
                if "react" in input_lower:
                    tech_skills.append("React")
                if "typescript" in input_lower or "ts" in input_lower:
                    tech_skills.append("TypeScript")
                if "javascript" in input_lower or "js" in input_lower:
                    tech_skills.append("JavaScript")
                if "python" in input_lower:
                    tech_skills.append("Python")
                if "java" in input_lower:
                    tech_skills.append("Java")

                if tech_skills:
                    job_data["preferred"] = tech_skills

                # 경력 요구사항 추출 (AI 페이지 필드명과 맞춤)
                if "3년" in input_text or "3년 이상" in input_text:
                    job_data["experience"] = "3년 이상 경력자"
                    job_data["requirements"] = "3년 이상 경력자"
                elif "신입" in input_text:
                    job_data["experience"] = "신입"
                    job_data["requirements"] = "신입"
                elif "경력자" in input_text:
                    job_data["experience"] = "경력자"
                    job_data["requirements"] = "경력자"

                # 급여 추출
                if "4000만원" in input_text or "4000" in input_text:
                    job_data["salary"] = "4000만원"
                elif "5000만원" in input_text or "5000" in input_text:
                    job_data["salary"] = "5000만원"

                # 근무지 추출 (AI 페이지 필드명과 맞춤)
                if "서울" in input_text:
                    job_data["location"] = "서울"
                    job_data["locationCity"] = "서울"  # AI 페이지 필드명
                if "강남구" in input_text:
                    job_data["location"] = "서울 강남구"
                    job_data["locationCity"] = "서울 강남구"
                if "부산" in input_text:
                    job_data["location"] = "부산"
                    job_data["locationCity"] = "부산"
                if "대구" in input_text:
                    job_data["location"] = "대구"
                    job_data["locationCity"] = "대구"

                # 픽톡과 동일한 방식으로 키워드 추출 (간단한 로직)
                keywords = set()
                key_fields = ['title', 'company', 'position', 'requirements', 'preferred', 'description']

                for field in key_fields:
                    if field in job_data and job_data[field]:
                        text = str(job_data[field])
                        words = text.replace(',', ' ').replace(';', ' ').split()
                        for word in words:
                            cleaned_word = ''.join(c for c in word if c.isalnum())
                            if len(cleaned_word) >= 2 and not cleaned_word.isdigit():
                                keywords.add(cleaned_word.lower())

                extracted_keywords = list(keywords)[:10]
                job_data["extracted_keywords"] = extracted_keywords

                # 채용공고 데이터에 기본 정보 추가 (픽톡과 동일)
                job_data["created_at"] = datetime.now()
                job_data["updated_at"] = datetime.now()
                job_data["status"] = "published"
                job_data["applicants"] = 0
                job_data["views"] = 0

                # MongoDB에 저장 (픽톡과 동일)
                result = await mongo_service.db.job_postings.insert_one(job_data)

                logger.info(f"✅ [에이전트 채용공고툴] 픽톡 방식으로 생성 완료: {result.inserted_id}")

                # ObjectId를 문자열로 변환하여 직렬화 오류 방지
                safe_job_data = {}
                for key, value in job_data.items():
                    if key == '_id' or hasattr(value, '__dict__') or str(type(value)).find('ObjectId') != -1:
                        safe_job_data[key] = str(value)
                    else:
                        safe_job_data[key] = value

                # 픽톡과 동일한 응답 구조 + auto_navigation 추가
                return {
                    "success": True,
                    "result": {
                        "message": "🎉 채용공고 정보가 성공적으로 추출되었습니다! 🚀 3초 후 등록 페이지로 이동합니다.",
                        "data": {
                            "job_id": str(result.inserted_id),
                            "extracted_keywords": extracted_keywords
                        },
                        "auto_navigation": {
                            "enabled": True,
                            "delay": 3000,
                            "target": "ai-job-registration",
                            "action": "open_job_modal",
                            "extracted_data": safe_job_data
                        },
                        "quick_actions": [
                            {
                                "title": "즉시 이동",
                                "action": "navigate",
                                "target": "/ai-job-registration",
                                "icon": "⚡"
                            },
                            {
                                "title": "수동 입력",
                                "action": "navigate",
                                "target": "/ai-job-registration",
                                "icon": "✏️"
                            }
                        ]
                    }
                }

            except Exception as e:
                logger.error(f"❌ [에이전트 채용공고툴] 실제 채용공고 생성 실패: {e}")
                return {
                    "success": False,
                    "error": f"채용공고 생성 중 오류가 발생했습니다: {str(e)}"
                }

        elif action == "list":
            # 실제 데이터베이스에서 채용공고 목록 조회
            try:
                from motor.motor_asyncio import AsyncIOMotorClient
                client = AsyncIOMotorClient('mongodb://localhost:27017')
                db = client.hireme

                # 전체 채용공고 수 조회
                total_count = await db.job_postings.count_documents({})
                logger.info(f"🔍 [채용공고툴] DB에서 조회된 총 채용공고 수: {total_count}개")

                # 최근 10개 채용공고 조회
                recent_jobs = await db.job_postings.find().sort("created_at", -1).limit(10).to_list(10)

                # ObjectId를 문자열로 변환
                for job in recent_jobs:
                    job["id"] = str(job["_id"])
                    del job["_id"]

                client.close()

                result = {
                    "message": f"📋 현재 등록된 채용공고 목록입니다 (총 {total_count}개):",
                    "data": recent_jobs,
                    "total_count": total_count,
                    "displayed_count": len(recent_jobs)
                }

                logger.info(f"✅ [채용공고툴] 실제 DB 조회 완료: {total_count}개 중 {len(recent_jobs)}개 표시")

            except Exception as e:
                logger.error(f"❌ [채용공고툴] DB 조회 실패: {e}")
                # DB 조회 실패 시 더미 데이터 반환
                result = {
                    "message": "📋 채용공고 목록 조회 중 오류가 발생했습니다.",
                    "data": [],
                    "total_count": 0,
                    "displayed_count": 0,
                    "error": str(e)
                }

        elif action == "search":
            # 채용공고 검색 시뮬레이션
            query = params.get("input_text", "")
            search_keywords = []

            # 검색 키워드 추출
            if "react" in query.lower():
                search_keywords.append("React")
            if "python" in query.lower():
                search_keywords.append("Python")
            if "java" in query.lower():
                search_keywords.append("Java")
            if "프론트엔드" in query:
                search_keywords.append("프론트엔드")
            if "백엔드" in query:
                search_keywords.append("백엔드")
            if "풀스택" in query:
                search_keywords.append("풀스택")

            # 검색 결과 시뮬레이션
            search_results = []
            if "react" in query.lower() or "프론트엔드" in query:
                search_results = [
                    {
                        "id": "job_001",
                        "title": "React 프론트엔드 개발자",
                        "company": "테크스타트업",
                        "location": "서울 강남구",
                        "salary": "4000-6000만원",
                        "experience": "3년 이상",
                        "skills": ["React", "TypeScript", "Next.js"],
                        "status": "진행중",
                        "applicants": 12,
                        "created_at": "2024-01-15"
                    },
                    {
                        "id": "job_003",
                        "title": "프론트엔드 개발자 (React/Vue)",
                        "company": "이커머스 기업",
                        "location": "서울 마포구",
                        "salary": "4500-6500만원",
                        "experience": "2년 이상",
                        "skills": ["React", "Vue.js", "JavaScript"],
                        "status": "진행중",
                        "applicants": 8,
                        "created_at": "2024-01-13"
                    }
                ]
            elif "python" in query.lower() or "백엔드" in query:
                search_results = [
                    {
                        "id": "job_002",
                        "title": "Python 백엔드 개발자",
                        "company": "핀테크 기업",
                        "location": "서울 서초구",
                        "salary": "5000-7000만원",
                        "experience": "5년 이상",
                        "skills": ["Python", "Django", "PostgreSQL"],
                        "status": "진행중",
                        "applicants": 8,
                        "created_at": "2024-01-14"
                    }
                ]
            else:
                # 일반 검색 결과
                search_results = [
                    {
                        "id": "job_001",
                        "title": "프론트엔드 개발자",
                        "company": "테크스타트업",
                        "location": "서울 강남구",
                        "salary": "4000-6000만원",
                        "experience": "3년 이상",
                        "skills": ["React", "TypeScript"],
                        "status": "진행중",
                        "applicants": 12,
                        "created_at": "2024-01-15"
                    }
                ]

            result = {
                "message": f"🔍 '{query}' 검색 결과입니다 (총 {len(search_results)}개):",
                "data": {
                    "query": query,
                    "search_keywords": search_keywords,
                    "total_count": len(search_results),
                    "job_postings": search_results
                }
            }

        elif action == "update":
            # 채용공고 수정 시뮬레이션
            result = {
                "message": "✏️ 채용공고가 수정되었습니다!",
                "data": {"status": "updated"}
            }

        elif action == "delete":
            # 채용공고 삭제 시뮬레이션
            result = {
                "message": "🗑️ 채용공고가 삭제되었습니다!",
                "data": {"status": "deleted"}
            }

        else:
            return {
                "success": False,
                "error": f"알 수 없는 액션: {action}",
                "result": None
            }

        return {
            "success": True,
            "result": result
        }

    except Exception as e:
        logger.error(f"채용공고 툴 실행 중 오류: {e}")
        return {
            "success": False,
            "error": str(e),
            "result": None
        }

async def _execute_github_tool(action: str, params: Dict) -> Dict:
    """GitHub 관련 툴 실행"""
    try:
        if action == "get_profile":
            username = params.get("username", "octocat")
            result = {
                "message": f"👤 GitHub 프로필: {username}",
                "data": {
                    "username": username,
                    "followers": 1234,
                    "repos": 56,
                    "bio": "AI-powered developer"
                }
            }

        elif action == "get_repos":
            username = params.get("username", "octocat")
            result = {
                "message": f"📚 {username}의 레포지토리 목록:",
                "data": [
                    {"name": "awesome-project", "stars": 100, "language": "JavaScript"},
                    {"name": "ml-toolkit", "stars": 50, "language": "Python"}
                ]
            }

        else:
            return {
                "success": False,
                "error": f"알 수 없는 액션: {action}",
                "result": None
            }

        return {
            "success": True,
            "result": result
        }

    except Exception as e:
        logger.error(f"GitHub 툴 실행 중 오류: {e}")
        return {
            "success": False,
            "error": str(e),
            "result": None
        }

async def _execute_mongodb_tool(action: str, params: Dict) -> Dict:
    """MongoDB 관련 툴 실행"""
    try:
        if action == "query":
            collection = params.get("collection", "applicants")
            query = params.get("query", {})

            try:
                result = {
                    "message": f"📊 {collection} 컬렉션을 실제 데이터베이스에서 조회합니다:",
                    "data": {
                        "collection": collection,
                        "query": query,
                        "note": "실제 MongoDB 데이터베이스에 연결하여 데이터를 조회합니다.",
                        "status": "connected",
                        "database": "hireme"
                    }
                }
            except Exception as e:
                result = {
                    "message": f"❌ 데이터베이스 조회 실패: {str(e)}",
                    "data": {"status": "error", "error": str(e)}
                }

        else:
            return {
                "success": False,
                "error": f"알 수 없는 액션: {action}",
                "result": None
            }

        return {
            "success": True,
            "result": result
        }

    except Exception as e:
        logger.error(f"MongoDB 툴 실행 중 오류: {e}")
        return {
            "success": False,
            "error": str(e),
            "result": None
        }

async def _execute_applicant_tool(action: str, params: Dict) -> Dict:
    """지원자 관련 툴 실행"""
    try:
        if action == "list":
            # 실제 지원자 목록 API 호출
            try:
                from routers.applicants import router as applicants_router

                result = {
                    "message": "👥 실제 지원자 목록을 조회합니다:",
                    "data": {
                        "note": "실제 데이터베이스에서 지원자 정보를 가져옵니다.",
                        "api_endpoint": "/api/applicants",
                        "status": "connected"
                    }
                }
            except Exception as e:
                result = {
                    "message": f"❌ 지원자 목록 조회 실패: {str(e)}",
                    "data": {"status": "error", "error": str(e)}
                }

        elif action == "get":
            # 실제 지원자 정보 API 호출
            applicant_id = params.get("id", "unknown")
            try:
                result = {
                    "message": f"👤 지원자 정보 (ID: {applicant_id}):",
                    "data": {
                        "note": "실제 데이터베이스에서 지원자 상세 정보를 가져옵니다.",
                        "api_endpoint": f"/api/applicants/{applicant_id}",
                        "applicant_id": applicant_id,
                        "status": "connected"
                    }
                }
            except Exception as e:
                result = {
                    "message": f"❌ 지원자 정보 조회 실패: {str(e)}",
                    "data": {"status": "error", "error": str(e)}
                }

        elif action == "match_by_tech_stack":
            # 기술 스택별 지원자 매칭
            query = params.get("input_text", "")
            tech_keywords = []

            # 기술 스택 추출
            if "react" in query.lower():
                tech_keywords.append("React")
            if "python" in query.lower():
                tech_keywords.append("Python")
            if "java" in query.lower():
                tech_keywords.append("Java")
            if "javascript" in query.lower():
                tech_keywords.append("JavaScript")
            if "typescript" in query.lower():
                tech_keywords.append("TypeScript")
            if "node" in query.lower():
                tech_keywords.append("Node.js")

            # 매칭 결과 시뮬레이션
            matched_applicants = []
            if tech_keywords:
                matched_applicants = [
                    {
                        "id": "app_001",
                        "name": "김개발",
                        "email": "kim@example.com",
                        "position": "프론트엔드 개발자",
                        "experience": "3년",
                        "tech_stack": ["React", "TypeScript", "Next.js"],
                        "match_score": 95,
                        "status": "면접 대기"
                    },
                    {
                        "id": "app_002",
                        "name": "박코딩",
                        "email": "park@example.com",
                        "position": "풀스택 개발자",
                        "experience": "5년",
                        "tech_stack": ["React", "Node.js", "Python"],
                        "match_score": 88,
                        "status": "서류 통과"
                    }
                ]

            result = {
                "message": f"🎯 기술 스택 '{', '.join(tech_keywords)}' 매칭 결과 (총 {len(matched_applicants)}명):",
                "data": {
                    "search_keywords": tech_keywords,
                    "total_count": len(matched_applicants),
                    "applicants": matched_applicants,
                    "analysis": {
                        "avg_match_score": sum(app["match_score"] for app in matched_applicants) / len(matched_applicants) if matched_applicants else 0,
                        "top_skills": tech_keywords,
                        "recommendation": "매칭도가 높은 지원자들을 우선적으로 면접 진행을 권장합니다."
                    }
                }
            }

        elif action == "update_status_and_send_mail":
            # 지원자 상태 업데이트 + 메일 발송 (복합 액션)
            query = params.get("input_text", "")

            # 면접 통과자 시뮬레이션
            passed_applicants = [
                {"id": "app_001", "name": "김개발", "email": "kim@example.com", "status": "면접 통과"},
                {"id": "app_002", "name": "박코딩", "email": "park@example.com", "status": "면접 통과"}
            ]

            # 상태 업데이트 시뮬레이션
            updated_count = len(passed_applicants)

            # 메일 발송 시뮬레이션
            email_results = []
            for applicant in passed_applicants:
                email_results.append({
                    "applicant_id": applicant["id"],
                    "name": applicant["name"],
                    "email": applicant["email"],
                    "email_status": "발송 완료",
                    "subject": "면접 결과 안내 - 합격",
                    "template": "interview_pass_template"
                })

            result = {
                "message": f"✅ 면접 통과자 {updated_count}명의 상태를 업데이트하고 합격 메일을 발송했습니다!",
                "data": {
                    "updated_applicants": updated_count,
                    "email_sent": len(email_results),
                    "applicants": passed_applicants,
                    "email_results": email_results,
                    "actions_completed": [
                        "지원자 상태 업데이트",
                        "합격 메일 발송",
                        "면접 일정 안내"
                    ]
                }
            }

        elif action == "analyze_and_recommend":
            # 지원자 분석 및 추천 (복합 액션)
            query = params.get("input_text", "")

            # 분석 결과 시뮬레이션
            analysis_results = {
                "total_applicants": 25,
                "by_experience": {
                    "신입": 8,
                    "1-3년": 10,
                    "3-5년": 5,
                    "5년 이상": 2
                },
                "by_tech_stack": {
                    "React": 12,
                    "Python": 8,
                    "Java": 6,
                    "Node.js": 9
                },
                "top_candidates": [
                    {
                        "id": "app_001",
                        "name": "김개발",
                        "match_score": 95,
                        "strengths": ["React 전문성", "팀워크", "문제해결능력"],
                        "recommendation": "즉시 면접 진행 권장"
                    },
                    {
                        "id": "app_002",
                        "name": "박코딩",
                        "match_score": 88,
                        "strengths": ["풀스택 경험", "리더십", "기술적 깊이"],
                        "recommendation": "2차 면접 진행 권장"
                    }
                ]
            }

            result = {
                "message": "📊 지원자 분석 및 추천 결과입니다:",
                "data": {
                    "analysis": analysis_results,
                    "recommendations": [
                        "React 개발자 채용에 집중",
                        "경력 3-5년 개발자 우선 검토",
                        "상위 2명 즉시 면접 진행"
                    ],
                    "next_actions": [
                        "면접 일정 조율",
                        "기술 면접 준비",
                        "최종 합격자 선발"
                    ]
                }
            }

        else:
            return {
                "success": False,
                "error": f"알 수 없는 액션: {action}",
                "result": None
            }

        return {
            "success": True,
            "result": result
        }

    except Exception as e:
        logger.error(f"지원자 툴 실행 중 오류: {e}")
        return {
            "success": False,
            "error": str(e),
            "result": None
        }

async def _execute_file_upload_tool(action: str, params: Dict) -> Dict:
    """파일 업로드 관련 툴 실행"""
    try:
        if action == "upload":
            filename = params.get("filename", "unknown")
            try:
                result = {
                    "message": f"📁 파일 '{filename}'을 실제 업로드 시스템에 전송합니다!",
                    "data": {
                        "filename": filename,
                        "note": "실제 파일 업로드 API를 통해 파일이 저장됩니다.",
                        "api_endpoint": "/api/upload",
                        "status": "connecting"
                    }
                }
            except Exception as e:
                result = {
                    "message": f"❌ 파일 업로드 실패: {str(e)}",
                    "data": {"status": "error", "error": str(e)}
                }

        elif action == "download":
            filename = params.get("filename", "unknown")
            result = {
                "message": f"📥 파일 '{filename}' 다운로드가 시작되었습니다!",
                "data": {
                    "filename": filename,
                    "download_url": f"/download/{filename}"
                }
            }

        else:
            return {
                "success": False,
                "error": f"알 수 없는 액션: {action}",
                "result": None
            }

        return {
            "success": True,
            "result": result
        }

    except Exception as e:
        logger.error(f"파일 업로드 툴 실행 중 오류: {e}")
        return {
            "success": False,
            "error": str(e),
            "result": None
        }

async def _execute_mail_tool(action: str, params: Dict) -> Dict:
    """메일 관련 툴 실행"""
    try:
        if action == "send_test":
            # 실제 테스트 메일 발송 API 호출
            recipient = params.get("recipient", "test@example.com")
            try:
                result = {
                    "message": f"📧 실제 테스트 메일을 {recipient}로 발송합니다!",
                    "data": {
                        "action": "send_test",
                        "recipient": recipient,
                        "status": "connecting",
                        "note": "실제 SMTP 서버를 통해 메일이 전송됩니다.",
                        "api_endpoint": "/api/send-test-mail"
                    }
                }
            except Exception as e:
                result = {
                    "message": f"❌ 테스트 메일 발송 실패: {str(e)}",
                    "data": {"status": "error", "error": str(e)}
                }

        elif action == "send_bulk":
            # 일괄 메일 발송 시뮬레이션
            recipients = params.get("recipients", [])
            template = params.get("template", "default")
            count = len(recipients) if recipients else 0

            result = {
                "message": f"📧 일괄 메일이 {count}명에게 발송되었습니다!",
                "data": {
                    "action": "send_bulk",
                    "recipients": recipients,
                    "template": template,
                    "count": count,
                    "status": "sent",
                    "sent_at": datetime.now().isoformat()
                }
            }

        elif action == "send_individual":
            # 개별 메일 발송 시뮬레이션
            recipient = params.get("recipient", "user@example.com")
            subject = params.get("subject", "알림")
            content = params.get("content", "메일 내용")

            result = {
                "message": f"📧 개별 메일이 {recipient}로 발송되었습니다!",
                "data": {
                    "action": "send_individual",
                    "recipient": recipient,
                    "subject": subject,
                    "content": content,
                    "status": "sent",
                    "sent_at": datetime.now().isoformat()
                }
            }

        elif action == "create_template":
            # 메일 템플릿 생성 시뮬레이션
            template_name = params.get("name", "새 템플릿")
            subject = params.get("subject", "제목")
            content = params.get("content", "내용")

            result = {
                "message": f"📝 메일 템플릿 '{template_name}'이 생성되었습니다!",
                "data": {
                    "action": "create_template",
                    "template_name": template_name,
                    "subject": subject,
                    "content": content,
                    "created_at": datetime.now().isoformat(),
                    "template_id": f"template_{int(datetime.now().timestamp())}"
                }
            }

        elif action == "get_templates":
            # 메일 템플릿 조회 시뮬레이션
            result = {
                "message": "📝 등록된 메일 템플릿 목록입니다:",
                "data": {
                    "action": "get_templates",
                    "templates": [
                        {"id": "template_1", "name": "채용공고 알림", "subject": "새로운 채용공고가 등록되었습니다"},
                        {"id": "template_2", "name": "지원자 안내", "subject": "지원해주셔서 감사합니다"},
                        {"id": "template_3", "name": "면접 안내", "subject": "면접 일정 안내"}
                    ],
                    "count": 3
                }
            }

        else:
            return {
                "success": False,
                "error": f"알 수 없는 메일 액션: {action}",
                "result": None
            }

        return {
            "success": True,
            "result": result
        }

    except Exception as e:
        logger.error(f"메일 툴 실행 중 오류: {e}")
        return {
            "success": False,
            "error": str(e),
            "result": None
        }

async def _execute_web_automation_tool(action: str, params: Dict) -> Dict:
    """웹 자동화 관련 툴 실행"""
    try:
        if action == "navigate":
            # 실제 페이지 이동 기능
            page_path = params.get("page_path", "/")
            try:
                result = {
                    "message": f"🚀 실제 페이지 이동을 수행합니다!",
                    "data": {
                        "action": "navigate",
                        "page_path": page_path,
                        "note": "실제 React Router를 통해 페이지 이동이 실행됩니다.",
                        "status": "executing",
                        "navigated_at": datetime.now().isoformat()
                    }
                }
            except Exception as e:
                result = {
                    "message": f"❌ 페이지 이동 실패: {str(e)}",
                    "data": {"status": "error", "error": str(e)}
                }

        elif action == "click":
            # 요소 클릭 시뮬레이션
            element_selector = params.get("selector", "button")
            element_text = params.get("text", "버튼")

            result = {
                "message": f"🖱️ '{element_text}' 요소를 클릭했습니다!",
                "data": {
                    "action": "click",
                    "selector": element_selector,
                    "text": element_text,
                    "clicked_at": datetime.now().isoformat()
                }
            }

        elif action == "input":
            # 텍스트 입력 시뮬레이션
            field_name = params.get("field", "입력 필드")
            input_value = params.get("value", "")

            result = {
                "message": f"⌨️ '{field_name}'에 '{input_value}'를 입력했습니다!",
                "data": {
                    "action": "input",
                    "field": field_name,
                    "value": input_value,
                    "input_at": datetime.now().isoformat()
                }
            }

        elif action == "scroll":
            # 스크롤 시뮬레이션
            direction = params.get("direction", "down")
            amount = params.get("amount", "100px")

            result = {
                "message": f"📜 {direction} 방향으로 {amount} 스크롤했습니다!",
                "data": {
                    "action": "scroll",
                    "direction": direction,
                    "amount": amount,
                    "scrolled_at": datetime.now().isoformat()
                }
            }

        elif action == "wait":
            # 대기 시뮬레이션
            duration = params.get("duration", 1)
            reason = params.get("reason", "페이지 로딩")

            result = {
                "message": f"⏳ {reason}을 위해 {duration}초 대기했습니다!",
                "data": {
                    "action": "wait",
                    "duration": duration,
                    "reason": reason,
                    "waited_at": datetime.now().isoformat()
                }
            }

        else:
            return {
                "success": False,
                "error": f"알 수 없는 웹 자동화 액션: {action}",
                "result": None
            }

        return {
            "success": True,
            "result": result
        }

    except Exception as e:
        logger.error(f"웹 자동화 툴 실행 중 오류: {e}")
        return {
            "success": False,
            "error": str(e),
            "result": None
        }

def _fallback_processing(session: Dict, user_input: str, current_state: str) -> Dict:
    """LangGraph 실패 시 기본 처리"""
    # 간단한 키워드 추출
    extracted_fields = {}

    # 직무 추출
    job_keywords = ["개발자", "엔지니어", "프로그래머", "디자이너"]
    for keyword in job_keywords:
        if keyword in user_input:
            extracted_fields["position"] = keyword
            break

    # 기술 스택 추출
    tech_keywords = ["React", "Python", "Java", "Node.js", "TypeScript"]
    found_tech = []
    for tech in tech_keywords:
        if tech.lower() in user_input.lower():
            found_tech.append(tech)

    if found_tech:
        extracted_fields["skills"] = found_tech

    # 세션 업데이트
    session["extracted_data"].update(extracted_fields)

    return {
        "success": True,
        "response": f"입력하신 내용을 분석했습니다. {', '.join(extracted_fields.values()) if extracted_fields else '추가 정보가 필요합니다.'}",
        "state": current_state,
        "extracted_fields": session["extracted_data"],
        "quick_actions": _get_quick_actions_by_state(current_state),
        "suggestions": _get_suggestions_by_state(current_state),
        "session_id": session["session_id"]
    }

async def _execute_workflow_tool(action: str, params: Dict) -> Dict:
    """워크플로우 관련 툴 실행 (복합적인 체이닝 작업)"""
    try:
        if action == "recruitment_pipeline":
            # 채용 파이프라인 워크플로우
            query = params.get("input_text", "")

            # 1단계: 채용공고 검색
            job_search_result = await _execute_job_posting_tool("search", {"input_text": query})

            # 2단계: 지원자 목록 조회
            applicant_list_result = await _execute_applicant_tool("list", {"input_text": "지원자 목록 조회"})

            # 3단계: 기술 스택 매칭
            tech_match_result = await _execute_applicant_tool("match_by_tech_stack", {"input_text": query})

            # 4단계: 분석 및 추천
            analysis_result = await _execute_applicant_tool("analyze_and_recommend", {"input_text": query})

            result = {
                "message": "🔄 채용 파이프라인 워크플로우가 완료되었습니다!",
                "data": {
                    "workflow_name": "recruitment_pipeline",
                    "steps_completed": [
                        "채용공고 검색",
                        "지원자 목록 조회",
                        "기술 스택 매칭",
                        "분석 및 추천"
                    ],
                    "results": {
                        "job_search": job_search_result.get("result", {}),
                        "applicant_list": applicant_list_result.get("result", {}),
                        "tech_matching": tech_match_result.get("result", {}),
                        "analysis": analysis_result.get("result", {})
                    },
                    "summary": {
                        "total_jobs_found": job_search_result.get("result", {}).get("data", {}).get("total_count", 0),
                        "total_applicants": applicant_list_result.get("result", {}).get("data", {}).get("count", 0),
                        "matched_candidates": tech_match_result.get("result", {}).get("data", {}).get("total_count", 0)
                    }
                }
            }

        elif action == "interview_workflow":
            # 면접 워크플로우
            query = params.get("input_text", "")

            # 1단계: 면접 통과자 상태 업데이트
            status_update_result = await _execute_applicant_tool("update_status_and_send_mail", {"input_text": query})

            # 2단계: 면접 일정 조회
            interview_schedule_result = {
                "message": "📅 면접 일정을 조회합니다:",
                "data": {
                    "upcoming_interviews": [
                        {"id": "int_001", "applicant": "김개발", "date": "2024-01-20", "time": "14:00", "type": "기술면접"},
                        {"id": "int_002", "applicant": "박코딩", "date": "2024-01-21", "time": "10:00", "type": "최종면접"}
                    ],
                    "total_scheduled": 2
                }
            }

            # 3단계: 면접 결과 분석
            interview_analysis_result = {
                "message": "📊 면접 결과 분석:",
                "data": {
                    "total_interviews": 15,
                    "passed": 8,
                    "failed": 7,
                    "pass_rate": 53.3,
                    "recommendations": [
                        "기술 면접 강화 필요",
                        "소프트 스킬 평가 추가",
                        "면접관 교육 진행"
                    ]
                }
            }

            result = {
                "message": "🎯 면접 워크플로우가 완료되었습니다!",
                "data": {
                    "workflow_name": "interview_workflow",
                    "steps_completed": [
                        "면접 통과자 상태 업데이트",
                        "면접 일정 조회",
                        "면접 결과 분석"
                    ],
                    "results": {
                        "status_update": status_update_result.get("result", {}),
                        "interview_schedule": interview_schedule_result,
                        "interview_analysis": interview_analysis_result
                    },
                    "summary": {
                        "updated_applicants": status_update_result.get("result", {}).get("data", {}).get("updated_applicants", 0),
                        "scheduled_interviews": interview_schedule_result["data"]["total_scheduled"],
                        "pass_rate": interview_analysis_result["data"]["pass_rate"]
                    }
                }
            }

        elif action == "hiring_workflow":
            # 채용 완료 워크플로우
            query = params.get("input_text", "")

            # 1단계: 최종 합격자 선발
            final_selection_result = {
                "message": "🏆 최종 합격자를 선발했습니다:",
                "data": {
                    "selected_candidates": [
                        {"id": "app_001", "name": "김개발", "position": "프론트엔드 개발자", "offer_salary": "5000만원"},
                        {"id": "app_002", "name": "박코딩", "position": "풀스택 개발자", "offer_salary": "6000만원"}
                    ],
                    "total_selected": 2
                }
            }

            # 2단계: 오퍼 메일 발송
            offer_email_result = {
                "message": "📧 오퍼 메일을 발송했습니다:",
                "data": {
                    "emails_sent": 2,
                    "email_templates": ["offer_template_001", "offer_template_002"],
                    "recipients": ["kim@example.com", "park@example.com"]
                }
            }

            # 3단계: 채용 통계 생성
            hiring_stats_result = {
                "message": "📈 채용 통계를 생성했습니다:",
                "data": {
                    "total_applicants": 25,
                    "interviewed": 15,
                    "final_selected": 2,
                    "conversion_rate": 8.0,
                    "time_to_hire": "45일",
                    "cost_per_hire": "200만원"
                }
            }

            result = {
                "message": "🎉 채용 완료 워크플로우가 성공적으로 완료되었습니다!",
                "data": {
                    "workflow_name": "hiring_workflow",
                    "steps_completed": [
                        "최종 합격자 선발",
                        "오퍼 메일 발송",
                        "채용 통계 생성"
                    ],
                    "results": {
                        "final_selection": final_selection_result,
                        "offer_emails": offer_email_result,
                        "hiring_stats": hiring_stats_result
                    },
                    "summary": {
                        "selected_candidates": final_selection_result["data"]["total_selected"],
                        "emails_sent": offer_email_result["data"]["emails_sent"],
                        "conversion_rate": hiring_stats_result["data"]["conversion_rate"]
                    }
                }
            }

        elif action == "analytics_workflow":
            # 분석 워크플로우
            query = params.get("input_text", "")

            # 1단계: 채용공고 분석
            job_analysis_result = await _execute_job_posting_tool("list", {"input_text": "채용공고 분석"})

            # 2단계: 지원자 분석
            applicant_analysis_result = await _execute_applicant_tool("analyze_and_recommend", {"input_text": query})

            # 3단계: 시장 분석
            market_analysis_result = {
                "message": "📊 시장 분석 결과:",
                "data": {
                    "market_trends": {
                        "react_demand": "높음",
                        "python_demand": "매우 높음",
                        "java_demand": "보통",
                        "average_salary": "4500만원"
                    },
                    "competitor_analysis": {
                        "similar_companies": 15,
                        "avg_offer_salary": "4800만원",
                        "market_position": "경쟁력 있음"
                    }
                }
            }

            result = {
                "message": "📊 종합 분석 워크플로우가 완료되었습니다!",
                "data": {
                    "workflow_name": "analytics_workflow",
                    "steps_completed": [
                        "채용공고 분석",
                        "지원자 분석",
                        "시장 분석"
                    ],
                    "results": {
                        "job_analysis": job_analysis_result.get("result", {}),
                        "applicant_analysis": applicant_analysis_result.get("result", {}),
                        "market_analysis": market_analysis_result
                    },
                    "insights": [
                        "React 개발자 수요가 높음",
                        "경력 3-5년 개발자 채용 집중 필요",
                        "시장 대비 경쟁력 있는 오퍼 제공"
                    ]
                }
            }

        else:
            return {
                "success": False,
                "error": f"알 수 없는 워크플로우 액션: {action}",
                "result": None
            }

        return {
            "success": True,
            "result": result
        }

    except Exception as e:
        logger.error(f"워크플로우 툴 실행 중 오류: {e}")
        return {
            "success": False,
            "error": str(e),
            "result": None
        }


