import google.generativeai as genai
import os
import json
from typing import Dict, Any, Optional, List
from dotenv import load_dotenv

load_dotenv()

class LLMService:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key or api_key == "your_gemini_api_key_here":
            print("⚠️  Gemini API 키가 설정되지 않았습니다. API 키를 설정해주세요.")
            print("💡 backend/.env 파일에서 GEMINI_API_KEY를 설정해주세요.")
            self.client = None
        else:
            genai.configure(api_key=api_key)
            self.client = genai.GenerativeModel('gemini-1.5-flash')
        
    async def process_user_input(self, page: str, field: str, user_input: str, conversation_history: List[Dict] = None, questions: List[Dict] = None, current_index: int = None) -> Dict[str, Any]:
        """
        사용자 입력을 처리하여 적절한 응답을 생성합니다.
        UI 필드 입력 유도 및 일반 대화형 응답을 모두 처리합니다.
        """
        
        if not self.client:
            return {
                "field": None,
                "value": None,
                "message": "Gemini API 키가 설정되지 않아 AI 응답을 생성할 수 없습니다. 관리자에게 문의하세요."
            }
        
        # 시스템 프롬프트 생성
        system_prompt = self._create_system_prompt(page, field, questions, current_index)
        
        try:
            # 대화 히스토리를 활용한 컨텍스트 구성
            context_messages = [
                {"role": "user", "parts": [system_prompt]}
            ]
            
            if conversation_history:
                for msg in conversation_history[-6:]:  # 최근 3턴 (user + bot)
                    if msg["role"] == "user":
                        context_messages.append({"role": "user", "parts": [msg["content"]]})
                    elif msg["role"] == "bot":
                        context_messages.append({"role": "model", "parts": [msg["content"]]})
            
            # 현재 사용자 입력 추가
            context_messages.append({"role": "user", "parts": [user_input]})
            
            # Gemini API 호출
            response = self.client.generate_content(context_messages)
            response_content = response.text
            
            # JSON 응답 파싱 시도
            try:
                start = response_content.find("{")
                end = response_content.rfind("}") + 1
                
                if start != -1 and end != -1 and start < end:
                    json_str = response_content[start:end]
                    parsed_response = json.loads(json_str)
                    
                    if "field" in parsed_response and "message" in parsed_response:
                        if parsed_response.get("value") is not None and parsed_response.get("field") == field:
                            return {
                                "field": parsed_response.get("field"),
                                "value": parsed_response.get("value"),
                                "message": parsed_response.get("message")
                            }
                        else:
                            return {
                                "field": None,
                                "value": None,
                                "message": parsed_response.get("message")
                            }
                    else:
                        return {
                            "field": None,
                            "value": None,
                            "message": response_content
                        }
                else:
                    return {
                        "field": None,
                        "value": None,
                        "message": response_content
                    }
                    
            except json.JSONDecodeError:
                return {
                    "field": None,
                    "value": None,
                    "message": response_content
                }
                
        except Exception as e:
            return {
                "field": None,
                "value": None,
                "message": f"죄송합니다. AI 응답을 처리하는 중 오류가 발생했습니다: {str(e)}"
            }
    
    def _create_system_prompt(self, page: str, field: str, questions: List[Dict] = None, current_index: int = None) -> str:
        """
        AI 비서의 역할과 현재 UI 필드에 대한 정보를 포함하는 시스템 프롬프트를 생성합니다.
        인사담당자의 구인구직 업무에 특화된 설명을 포함합니다.
        """
        
        # 구인구직 관련 필드만 포함
        field_descriptions = {
            "recruitment_title": "채용 공고의 제목을 입력받습니다. (예: 백엔드 개발자 채용)",
            "recruitment_role": "채용하려는 직무 또는 역할을 입력받습니다. (예: 프론트엔드 개발, 마케터)",
            "recruitment_requirements": "해당 직무에 필요한 자격 요건이나 필수 역량을 입력받습니다.",
            "recruitment_preferential": "해당 직무에 우대하는 사항이나 우대 역량을 입력받습니다.",
            "recruitment_benefits": "채용 시 제공되는 복리후생이나 이점을 입력받습니다.",
            "recruitment_location": "근무지를 입력받습니다.",
            "recruitment_deadline": "채용 마감일을 입력받습니다. (예: YYYY-MM-DD)",
            "resume_education": "이력서의 학력 사항을 입력받습니다.",
            "resume_experience": "이력서의 경력 사항을 입력받습니다.",
            "resume_portfolio": "이력서의 포트폴리오 링크나 설명을 입력받습니다.",
            "interview_question": "면접 질문을 생성하거나 입력받습니다."
        }
        
        field_description = field_descriptions.get(field, "현재 입력 필드에 적합한 정보를 추출하거나, 사용자의 질문에 답변합니다.")
        
        # 구인구직 관련 필드에 대한 상세 정보만 포함
        field_details = {
            "recruitment_title": "채용 공고의 제목을 50자 이내로 명확하게 작성해주세요. 어떤 직무인지 알 수 있도록 구체적으로 작성하는 것이 좋습니다.",
            "recruitment_role": "채용 직무를 상세하게 설명해주세요. 예: '프론트엔드 개발 (React 기반)', '온라인 마케터 (SNS 콘텐츠 기획)'",
            "recruitment_requirements": "필요한 최소 학력, 경력, 필수 기술 스택 등을 명시해주세요.",
            "recruitment_preferential": "우대하는 외국어 능력, 특정 경험, 자격증 등을 자유롭게 작성해주세요.",
            "recruitment_benefits": "회사에서 제공하는 식대, 교통비, 유연근무, 자녀 학자금 지원 등 복리후생을 구체적으로 알려주세요.",
            "recruitment_location": "정확한 근무지 주소를 알려주세요. (예: 서울특별시 강남구 테헤란로 123)",
            "recruitment_deadline": "채용 마감일을 'YYYY-MM-DD' 형식으로 입력해주세요. 예: '2025-08-31'",
            "resume_education": "학력 사항을 작성해주세요. (예: 'OO대학교 컴퓨터공학과 졸업 (2020년 2월)', 'OO고등학교 졸업')",
            "resume_experience": "경력 사항을 작성해주세요. (예: 'OO회사 프론트엔드 개발팀 3년', 'OO스타트업 백엔드 개발 1년 6개월')",
            "resume_portfolio": "지원자의 포트폴리오 링크나 포트폴리오의 주요 내용에 대해 설명해주세요.",
            "interview_question": "생성하고 싶은 면접 질문의 유형이나, 어떤 역량을 파악하고 싶은지 알려주세요. 제가 질문을 제안해 드릴 수도 있습니다."
        }
        
        field_detail = field_details.get(field, "사용자 입력에 따라 적절한 정보를 추출하거나 대화합니다.")
        
        prompt = f"""
당신은 AI 비서입니다.
사용자는 인사담당자로, 구직자에게 면접 기회를 제공하기 위해 **채용공고 작성, 이력서 검토, 면접 진행** 등의 업무를 수행합니다.

당신의 주된 역할은 사용자가 현재 작업 중인 **UI의 특정 입력 필드(`field`)에 들어갈 정보를 정확하게 유도하고 기록**하도록 돕는 것입니다.

사용자의 질문에 대해 **정확하고 실용적인 정보를 바탕으로 도움을 주는 역할**을 하며, **직접적인 작성(UI 필드에 기록할 값 제안)**은 사용자의 명확한 요청(예: "이렇게 작성해줘", "이걸로 해줘")이 있을 때만 수행합니다.

**추천이나 자동 작성이 필요한 경우**에도, 반드시 **사용자의 확인**을 먼저 받고 진행하며, 사용자에게 결정권을 줍니다.

**항상 존댓말로 응답**하며, **사용자의 판단을 존중**하고, 강제적으로 내용을 채워 넣지 않습니다.

---

**현재 작업 정보:**
- **현재 페이지**: `{page}`
- **현재 입력 필드**: `{field}`
- **필드 설명**: {field_description}
- **기대하는 입력 형식/상세 정보**: {field_detail}
- **현재 질문 인덱스**: {current_index}
- **전체 질문 수**: {len(questions) if questions else 0}
- **다음 질문**: {questions[current_index + 1]['question'] if questions and current_index is not None and current_index + 1 < len(questions) else '마지막 질문입니다'}

---

**🔸 AI 비서의 핵심 원칙:**

1.  **사용자 의도 파악 및 존중**:
    * 사용자의 입력이 **현재 `field`에 대한 답변**인지, 아니면 `field`와 관련하여 **새로운 궁금증이나 질문(`역질문`)**인지 명확히 구분합니다.
    * **사용자의 역질문에는 `field` 입력 유도보다 대화형 답변을 우선**하며, 일반적인 LLM처럼 궁금증을 해소해 줍니다.
    * `field`에 대한 답변이 모호하거나 불확실하면 추가 질문으로 명확히 합니다.

2.  **UI 필드 입력 유도 및 기록 지원**:
    * `field`에 정보 입력이 필요할 때는 해당 필드에 **필요한 내용을 구체적으로 질문**하여 사용자의 입력을 유도합니다.
    * 사용자가 `field`에 대한 **명확한 답변**을 제공하면, 해당 값을 추출하여 `value`로 제공하고, `field`와 함께 JSON 형식으로 반환합니다.

3.  **추천 및 자동 작성 시 사용자 확인**:
    * 어떤 내용을 추천하거나 자동 작성(`value`를 제안)해야 할 경우, 반드시 **번호로 구분하여 제시**하고 "이 중에서 선택해 주세요."와 같이 **사용자의 명시적인 확인**을 요청합니다.
    * 예시: "1. [추천 내용 1]\\n2. [추천 내용 2]\\n3. [추천 내용 3]\\n\\n이 중에서 선택해 주세요."
    * 사용자의 확인 없이는 절대 `value`를 포함한 JSON 응답을 반환하지 않습니다. (즉, `value`는 `null`로 유지하고 자연어 메시지만 반환)

4.  **응답 스타일**:
    * 항상 **존댓말**을 사용하고, **친절하고 전문적인 톤**을 유지합니다.
    * **실용적이고 구체적인 조언**을 제공하며, 사용자의 판단을 최우선으로 존중합니다.
    * 불확실한 답변이나 모호한 의도에 대해서는 **추가 질문을 통해 명확히** 합니다.
    * **답변이 길어질 경우, 문단 나누기, 목록(리스트) 활용, 핵심 내용 볼드 처리 등으로 가독성을 높여주세요.**
    * **핵심 정보나 여러 항목을 제시할 때는 줄넘김을 적극적으로 사용하여 읽기 쉽게 구성해 주세요.**
    * **가독성을 위해 Markdown 문법(줄넘김, 목록, 볼드체 등)을 적극적으로 활용해주세요.**

---

**🔸 응답 형식 가이드라인:**

* **UI 필드에 값을 기록할 경우 (사용자가 명확히 지시하거나, 명확한 답변을 제공하여 확정된 경우):**
    ```json
    {{
      "field": "{{field}}",
      "value": "추출된_값",
      "message": "'{{추출된_값}}'으로 입력하겠습니다.\\n\\n다음 질문: {questions[current_index + 1]['question'] if questions and current_index is not None and current_index + 1 < len(questions) else '모든 질문에 답변해 주셔서 감사합니다! 🎉'}"
    }}
    ```
    * `value`는 **사용자의 답변에서 추출된 최종 값**입니다.
    * `message`는 해당 값이 UI 필드에 기록될 것임을 사용자에게 알려주는 메시지입니다. **이 메시지 내에서 `\\n\\n`을 사용하여 두 줄을 띄우고, 다음 질문을 명확하게 안내해야 합니다.**

* **일반 대화형 응답이 필요한 경우 (대부분의 경우, 역질문, 조언, 설명, 추가 정보 요청, 확인 요청 등):**
    ```json
    {{
      "field": "{{field}}",
      "value": null,
      "message": "사용자의 질문에 대한 대화형 응답 (예: '네, OO에 대해 궁금하신 거군요. 자세히 설명해 드릴게요.', '혹시 OO에 대해 더 알려드릴까요?', '이 내용으로 진행하시겠습니까?')"
    }}
    ```
    * `value`는 **반드시 `null`**이어야 합니다.
    * `message`는 UI 필드에 기록할 값이 아닌, AI 비서의 **자연스러운 대화형 응답**입니다. (궁금증 해소, 추가 질문, 확인 요청 등)

* **주의**: JSON 형식을 따르기 어려운 복잡하거나 매우 긴 응답의 경우, JSON 없이 순수 자연어 텍스트로만 응답할 수 있습니다. 하지만 가능한 한 위 JSON 형식을 따르도록 노력해주세요. 또한, AI 모델이 생성한 메시지에 포함된 `\\n` 문자가 클라이언트(프론트엔드)에서 실제 줄 바꿈으로 렌더링되도록 해당 요소의 CSS 속성(`white-space: pre-wrap;` 등)을 확인해야 합니다.
"""
        return prompt 