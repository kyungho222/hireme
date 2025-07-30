from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import uuid
import json
from llm_service import LLMService  # 내부에 LLM 호출 로직 포함
from question_data import get_questions_for_page  # 기존 질문 리스트 불러오기용

router = APIRouter()
sessions: Dict[str, Dict[str, Any]] = {}

class ChatbotRequest(BaseModel):
    page: str
    user_input: str
    session_id: Optional[str] = None

class ChatbotResponse(BaseModel):
    field: Optional[str] = None
    value: Optional[str] = None
    message: str
    session_id: Optional[str] = None

class SessionStartRequest(BaseModel):
    page: str
    questions: Optional[List[Dict[str, str]]] = None  # 외부 질문 리스트 동적 입력 허용

class SessionStartResponse(BaseModel):
    session_id: str
    current_field: str
    question: str

# 세션 시작 (외부에서 질문 리스트 주입 가능)
@router.post("/start", response_model=SessionStartResponse)
async def start_session(request: SessionStartRequest):
    # 외부 질문 리스트가 있으면 우선 사용, 없으면 기존 질문 가져오기
    questions = request.questions or get_questions_for_page(request.page)
    if not questions:
        raise HTTPException(status_code=404, detail="페이지 질문을 찾을 수 없습니다")

    session_id = str(uuid.uuid4())
    sessions[session_id] = {
        "page": request.page,
        "questions": questions,
        "current_index": 0,
        "current_field": questions[0]["field"],
        "completed_fields": [],
        "conversation_history": []
    }
    return SessionStartResponse(
        session_id=session_id,
        current_field=questions[0]["field"],
        question=questions[0]["question"]
    )

@router.post("/ask", response_model=ChatbotResponse)
async def ask_chatbot(request: ChatbotRequest):
    if not request.session_id or request.session_id not in sessions:
        raise HTTPException(status_code=400, detail="유효하지 않은 세션입니다")

    session = sessions[request.session_id]
    current_index = session["current_index"]
    questions = session["questions"]
    current_field = session["current_field"]
    current_question = questions[current_index]["question"]

    # 대화 히스토리에 사용자 입력 저장
    session["conversation_history"].append({
        "role": "user",
        "content": request.user_input,
        "field": current_field
    })

    # LLM 프롬프트 생성 예시
    prompt = f"""
당신은 챗봇입니다. 현재 페이지 질문에 따라 사용자와 대화를 진행합니다.
현재 질문: "{current_question}"
최근 사용자 발화: "{request.user_input}"

- 사용자가 질문 형식으로 역질문하면, 정중히 다시 질문을 유도하세요.
- 사용자가 확정 답변을 하면, JSON 형식으로 필드명과 값(field, value)을 알려주세요.
- 사용자가 불확실한 답변을 하면 추천이나 추가 설명을 자연스럽게 제안하세요.

예시)
사용자: 이름이 뭐야?
챗봇: 제 이름 말고, 먼저 성함을 알려주실 수 있나요? 😊

사용자: 김철수로 할게요.
챗봇: {{"field": "username", "value": "김철수"}}
"""

    llm_service = LLMService()
    llm_response = await llm_service.process_user_input(
        page=request.page,
        field=current_field,
        user_input=request.user_input,
        conversation_history=session["conversation_history"],
        questions=questions,
        current_index=current_index
    )

    # LLM 응답에서 데이터 추출
    value = llm_response.get("value")
    field = llm_response.get("field")
    message = llm_response.get("message", "")

    # 대화 히스토리에 챗봇 응답 저장
    session["conversation_history"].append({
        "role": "bot",
        "content": message,
        "field": current_field
    })

    # 확정 답변이 있으면 다음 질문으로 이동
    if value is not None and field == current_field:
        if current_field not in session["completed_fields"]:
            session["completed_fields"].append(current_field)
        session["current_index"] += 1
        if session["current_index"] < len(questions):
            session["current_field"] = questions[session["current_index"]]["field"]
            # 다음 질문은 LLM 서비스에서 처리하므로 여기서는 추가하지 않음
        else:
            message += "\n\n모든 질문에 답변해 주셔서 감사합니다! 🎉"

    return ChatbotResponse(
        field=field,
        value=value,
        message=message,
        session_id=request.session_id
    ) 