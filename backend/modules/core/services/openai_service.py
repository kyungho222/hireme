import os
from typing import Any, Dict, List, Optional

import openai
from dotenv import load_dotenv
from modules.token_monitor import token_monitor

load_dotenv()


class OpenAIService:
    def __init__(self, model_name: str = "gpt-4o-mini"):
        """
        OpenAI 서비스 초기화

        Args:
            model_name: 사용할 OpenAI 모델 이름 (기본값: gpt-4o-mini)
        """
        self.model_name = model_name
        self.api_key = os.getenv("OPENAI_API_KEY")

        try:
            if not self.api_key:
                raise Exception("OPENAI_API_KEY가 설정되지 않았습니다.")

            openai.api_key = self.api_key
            self.client = openai.AsyncOpenAI(api_key=self.api_key)
            print(f"[SUCCESS] OpenAI 서비스 초기화 성공 (모델: {model_name})")
        except Exception as e:
            print(f"[ERROR] OpenAI 서비스 초기화 실패: {e}")
            self.client = None

    async def generate_response(self, prompt: str, conversation_history: Optional[List[Dict[str, Any]]] = None) -> str:
        """
        OpenAI 모델을 사용하여 응답 생성

        Args:
            prompt: 사용자 입력 프롬프트
            conversation_history: 대화 히스토리 (role/content 형식)

        Returns:
            생성된 응답 텍스트
        """
        if not self.client:
            return "OpenAI 서비스를 사용할 수 없습니다. OPENAI_API_KEY가 올바르게 설정되었는지 확인해주세요."

        try:
            messages: List[Dict[str, str]] = []

            system_prompt = (
                "HireMe AI 채용 어시스턴트입니다.\n"
                "채용공고 작성, 이력서/자소서 분석, 면접 질문 생성, 채용 컨설팅을 제공합니다.\n\n"
                "답변 스타일: 전문적이면서 친근한 톤, 핵심만 간결하게, 실무 적용 가능한 조언\n"
                "응답 형식: 2-3문장 요약, 체계적 구조, 이모지 활용"
            )
            messages.append({"role": "system", "content": system_prompt})

            if conversation_history:
                for msg in conversation_history[-6:]:
                    role = "user" if msg.get("role") == "user" else "assistant"
                    messages.append({"role": role, "content": msg.get("content", "")})

            messages.append({"role": "user", "content": prompt})

            response = await self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=0.7,  # gpt-4o-mini는 다양한 temperature 지원
                max_completion_tokens=500,  # 토큰 사용량 50% 감소
                top_p=0.8,
                stream=False,  # 스트리밍 비활성화로 토큰 절약
            )

            if response.choices and response.choices[0].message.content:
                # 토큰 사용량 로깅
                if hasattr(response, 'usage') and response.usage:
                    usage = token_monitor.create_usage_record(
                        model=self.model_name,
                        input_tokens=response.usage.prompt_tokens,
                        output_tokens=response.usage.completion_tokens,
                        endpoint="chat_completion"
                    )
                    token_monitor.log_usage(usage)

                return response.choices[0].message.content
            return "응답을 생성할 수 없습니다."

        except Exception as e:
            print(f"[ERROR] OpenAI 응답 생성 실패: {e}")
            return f"OpenAI 서비스 오류가 발생했습니다: {str(e)}"

    async def generate_json_response(self, prompt: str) -> str:
        """
        JSON 형식 응답에 최적화된 OpenAI 응답 생성

        Args:
            prompt: JSON 응답을 요구하는 프롬프트

        Returns:
            JSON 형식의 응답 텍스트
        """
        if not self.client:
            return '{"error": "OpenAI 서비스를 사용할 수 없습니다."}'

        try:
            messages = [
                {
                    "role": "system",
                    "content": (
                        "당신은 정확한 JSON 형식으로만 응답하는 AI입니다.\n"
                        "- 반드시 유효한 JSON 형식으로만 응답하세요\n"
                        "- 다른 설명이나 텍스트는 포함하지 마세요\n"
                        "- JSON 외부에 어떤 텍스트도 추가하지 마세요\n"
                        "- 한국어 문자열은 적절히 이스케이프 처리하세요"
                    )
                },
                {"role": "user", "content": prompt}
            ]

            response = await self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=0.7,  # gpt-4o-mini는 다양한 temperature 지원
                max_completion_tokens=1200,  # 토큰 사용량 증가
                response_format={"type": "json_object"}  # JSON 형식 강제
            )

            if response.choices and response.choices[0].message.content:
                # 토큰 사용량 로깅
                if hasattr(response, 'usage') and response.usage:
                    usage = token_monitor.create_usage_record(
                        model=self.model_name,
                        input_tokens=response.usage.prompt_tokens,
                        output_tokens=response.usage.completion_tokens,
                        endpoint="json_completion"
                    )
                    token_monitor.log_usage(usage)

                return response.choices[0].message.content
            return '{"error": "응답을 생성할 수 없습니다."}'

        except Exception as e:
            print(f"[ERROR] OpenAI JSON 응답 생성 실패: {e}")
            return f'{{"error": "OpenAI 서비스 오류: {str(e)}"}}'


