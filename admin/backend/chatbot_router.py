from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import json

router = APIRouter()

class ChatbotRequest(BaseModel):
    message: str
    page: Optional[str] = "dashboard"

class ChatbotResponse(BaseModel):
    response: str
    field_update: Optional[dict] = None

@router.post("/start")
async def start_chatbot(request: ChatbotRequest):
    """챗봇 세션 시작"""
    try:
        # 페이지별 환영 메시지
        welcome_messages = {
            "dashboard": "안녕하세요! 대시보드에서 어떤 도움이 필요하신가요?",
            "job-posting": "채용공고 등록을 도와드리겠습니다. 어떤 정보가 필요하신가요?",
            "resume": "이력서 관리에 대해 도움을 드리겠습니다.",
            "interview": "면접 관리에 대해 문의하실 내용이 있으신가요?",
            "portfolio": "포트폴리오 분석에 대해 도움을 드리겠습니다.",
            "cover-letter": "자기소개서 검증에 대해 문의하실 내용이 있으신가요?",
            "talent": "인재 추천에 대해 도움을 드리겠습니다.",
            "users": "사용자 관리에 대해 문의하실 내용이 있으신가요?",
            "settings": "설정에 대해 도움을 드리겠습니다."
        }
        
        page = request.page or "dashboard"
        welcome_message = welcome_messages.get(page, "안녕하세요! 어떤 도움이 필요하신가요?")
        
        return ChatbotResponse(
            response=welcome_message,
            field_update=None
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"챗봇 시작 오류: {str(e)}")

@router.post("/ask")
async def ask_chatbot(request: ChatbotRequest):
    """챗봇 질문 처리"""
    try:
        message = request.message.lower()
        page = request.page or "dashboard"
        
        # 간단한 키워드 기반 응답
        responses = {
            "dashboard": {
                "안녕": "안녕하세요! 대시보드에서 어떤 도움이 필요하신가요?",
                "도움": "대시보드에서는 전체 현황을 확인할 수 있습니다. 특정 기능에 대해 궁금하시면 말씀해주세요.",
                "통계": "현재 등록된 채용공고, 지원자, 면접 일정 등의 통계를 확인할 수 있습니다."
            },
            "job-posting": {
                "채용": "채용공고 등록을 도와드리겠습니다. 어떤 부서에서 채용하시나요?",
                "공고": "채용공고 작성을 도와드리겠습니다. 필요한 정보를 알려주세요.",
                "등록": "새로운 채용공고를 등록하시겠습니까? 상단의 '채용공고 등록' 버튼을 클릭해주세요."
            },
            "resume": {
                "이력서": "이력서 관리 페이지에서 지원자들의 이력서를 확인하고 관리할 수 있습니다.",
                "지원자": "지원자들의 이력서를 한눈에 볼 수 있습니다.",
                "검토": "이력서 검토 기능을 사용하실 수 있습니다."
            },
            "interview": {
                "면접": "면접 관리에서 면접 일정을 확인하고 관리할 수 있습니다.",
                "일정": "면접 일정을 조회하고 수정할 수 있습니다.",
                "평가": "면접 평가 결과를 입력하고 관리할 수 있습니다."
            }
        }
        
        # 페이지별 응답 찾기
        page_responses = responses.get(page, {})
        
        # 키워드 매칭
        for keyword, response in page_responses.items():
            if keyword in message:
                return ChatbotResponse(
                    response=response,
                    field_update=None
                )
        
        # 기본 응답
        default_responses = {
            "dashboard": "대시보드에서는 전체 현황을 확인할 수 있습니다. 더 구체적인 질문이 있으시면 말씀해주세요.",
            "job-posting": "채용공고 등록에 대해 도움을 드리겠습니다. 어떤 정보가 필요하신가요?",
            "resume": "이력서 관리에 대해 도움을 드리겠습니다. 구체적인 질문이 있으시면 말씀해주세요.",
            "interview": "면접 관리에 대해 도움을 드리겠습니다. 어떤 정보가 필요하신가요?",
            "portfolio": "포트폴리오 분석에 대해 도움을 드리겠습니다.",
            "cover-letter": "자기소개서 검증에 대해 도움을 드리겠습니다.",
            "talent": "인재 추천에 대해 도움을 드리겠습니다.",
            "users": "사용자 관리에 대해 도움을 드리겠습니다.",
            "settings": "설정에 대해 도움을 드리겠습니다."
        }
        
        return ChatbotResponse(
            response=default_responses.get(page, "도움이 필요하시면 구체적으로 말씀해주세요."),
            field_update=None
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"챗봇 처리 오류: {str(e)}") 