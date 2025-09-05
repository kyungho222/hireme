import os
from datetime import datetime
from typing import Any, Dict, List

import httpx
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

try:
    import openai
except ImportError:
    openai = None


class LLMService:
    def __init__(self):
        # OpenAI 설정
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.openai_model = "gpt-4o-mini"

        # Ollama 설정 (백업)
        self.ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        self.ollama_model = "gpt-oss:20b"

        # Gemini 설정 (비활성화)
        self.gemini_api_key = None
        self.gemini_model = "gemini-1.5-pro"
        self.gemini_base_url = "https://generativelanguage.googleapis.com/v1beta/models"

        # 사용할 LLM 결정 - OpenAI 우선, 없으면 Ollama
        if self.openai_api_key:
            self.primary_llm = "openai"
            print(f"[LLMService] === LLM 서비스 초기화 시작 ===")
            print(f"[LLMService] OpenAI 모드로 실행")
            print(f"[LLMService] OpenAI 모델: {self.openai_model}")
            print(f"[LLMService] === LLM 서비스 초기화 완료 ===")
        else:
            self.primary_llm = "ollama"
            print(f"[LLMService] === LLM 서비스 초기화 시작 ===")
            print(f"[LLMService] Ollama 모드로 실행 (OpenAI API 키 없음)")
            print(f"[LLMService] Ollama URL: {self.ollama_base_url}")
            print(f"[LLMService] Ollama 모델: {self.ollama_model}")
            print(f"[LLMService] === LLM 서비스 초기화 완료 ===")

    async def chat_completion(self, messages: List[Dict[str, str]], max_tokens: int = 300, temperature: float = 1.0) -> str:
        """LLM API를 사용하여 대화 응답을 생성합니다."""
        try:
            if self.primary_llm == "openai":
                return await self._openai_chat_completion(messages, max_tokens, temperature)
            else:
                return await self._ollama_chat_completion(messages, max_tokens, temperature)
        except Exception as e:
            return f"죄송합니다. 응답 생성 중 오류가 발생했습니다: {str(e)}"

    async def _openai_chat_completion(self, messages: List[Dict[str, str]], max_tokens: int, temperature: float) -> str:
        """OpenAI API를 사용한 채팅 완성"""
        try:
            if not openai:
                return "OpenAI 라이브러리가 설치되지 않았습니다."

            # OpenAI 클라이언트 설정
            client = openai.OpenAI(api_key=self.openai_api_key)

            # 속도 최적화: 재시도 로직 제거, 타임아웃 설정
            try:
                # max_tokens 최소값 보장 (너무 작으면 응답이 잘림)
                safe_max_tokens = max(max_tokens, 500)  # 최소값을 500으로 증가

                # OpenAI API 호출 (타임아웃 15초로 증가)
                response = client.chat.completions.create(
                    model=self.openai_model,
                    messages=messages,
                    max_completion_tokens=safe_max_tokens,
                    temperature=temperature,
                    timeout=15.0  # 15초 타임아웃으로 증가
                )

            except Exception as e:
                print(f"[LLMService] OpenAI API 호출 실패: {e}")
                raise e

            # choices 유효성 검사
            if not response or not hasattr(response, 'choices') or len(response.choices) == 0:
                print(f"[LLMService] OpenAI 빈 choices 배열 감지, 기본 JSON 응답 반환")
                print(f"[LLMService] 응답 구조: {response}")
                return '{"intent": "chat", "response": "응답을 생성하지 못했습니다. 다시 시도해주세요.", "suggested_tool": null, "suggested_action": null, "params": {}, "confidence": 0.5}'

            # finish_reason 확인
            choice = response.choices[0]
            if choice.finish_reason == 'length':
                print(f"[LLMService] OpenAI 응답이 토큰 길이 제한으로 잘림 (finish_reason: length)")
                print(f"[LLMService] 현재 max_tokens: {safe_max_tokens}, 더 큰 값으로 재시도 필요")
                # 토큰 길이 제한으로 잘린 경우 더 큰 토큰으로 재시도
                try:
                    retry_response = client.chat.completions.create(
                        model=self.openai_model,
                        messages=messages,
                        max_completion_tokens=safe_max_tokens * 2,  # 2배로 증가
                        temperature=temperature,
                        timeout=15.0
                    )
                    if retry_response.choices and retry_response.choices[0].message.content:
                        content = retry_response.choices[0].message.content
                        print(f"[LLMService] 재시도 성공: 응답 길이 {len(content)}")
                        return content
                except Exception as retry_e:
                    print(f"[LLMService] 재시도 실패: {retry_e}")

            # content 유효성 검사
            if not choice.message or not choice.message.content:
                print(f"[LLMService] OpenAI 빈 content 감지, 기본 JSON 응답 반환")
                print(f"[LLMService] choice 구조: {choice}")
                print(f"[LLMService] finish_reason: {choice.finish_reason}")
                return '{"intent": "chat", "response": "응답을 생성하지 못했습니다. 다시 시도해주세요.", "suggested_tool": null, "suggested_action": null, "params": {}, "confidence": 0.5}'

            content = choice.message.content

            # 빈 응답 처리
            if not content or content.strip() == "":
                print(f"[LLMService] OpenAI 빈 응답 감지, 기본 JSON 응답 반환")
                return '{"intent": "chat", "response": "응답을 생성하지 못했습니다. 다시 시도해주세요.", "suggested_tool": null, "suggested_action": null, "params": {}, "confidence": 0.5}'

            print(f"[LLMService] OpenAI 응답 생성 완료 (길이: {len(content)})")
            return content

        except Exception as e:
            print(f"[LLMService] OpenAI API 오류: {str(e)}")
            return f"OpenAI API 오류: {str(e)}"

    async def _gemini_chat_completion(self, messages: List[Dict[str, str]], max_tokens: int, temperature: float) -> str:
        """Gemini API를 사용한 채팅 완성"""
        try:
            # Gemini API 요청 형식으로 변환
            contents = []

            for message in messages:
                contents.append({
                    "parts": [{"text": message["content"]}]
                })

            payload = {
                "contents": contents,
                "generationConfig": {
                    "temperature": temperature,
                    "topK": 40,
                    "topP": 0.95,
                    "maxOutputTokens": max_tokens,
                }
            }

            url = f"{self.gemini_base_url}/{self.gemini_model}:generateContent?key={self.gemini_api_key}"

            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(url, json=payload)
                response.raise_for_status()

                result = response.json()
                if "candidates" in result and len(result["candidates"]) > 0:
                    content = result["candidates"][0]["content"]["parts"][0]["text"]
                    print(f"[LLMService] Gemini 응답 생성 완료 (길이: {len(content) if content else 0})")
                    return content
                else:
                    return "응답을 생성할 수 없습니다."

        except Exception as e:
            print(f"[LLMService] Gemini API 오류: {str(e)}")
            return "Gemini API 호출 중 오류가 발생했습니다."

    async def _ollama_chat_completion(self, messages: List[Dict[str, str]], max_tokens: int, temperature: float) -> str:
        """Ollama API를 사용한 채팅 완성"""
        try:
            # Ollama API 형식에 맞게 메시지 변환
            ollama_messages = []
            for msg in messages:
                if msg["role"] == "user":
                    ollama_messages.append({"role": "user", "content": msg["content"]})
                elif msg["role"] == "assistant":
                    ollama_messages.append({"role": "assistant", "content": msg["content"]})
                elif msg["role"] == "system":
                    ollama_messages.append({"role": "system", "content": msg["content"]})

            # Ollama API 호출
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.ollama_base_url}/api/chat",
                    json={
                        "model": self.ollama_model,
                        "messages": ollama_messages,
                        "stream": False,
                        "options": {
                            "temperature": temperature,
                            "num_predict": max_tokens
                        }
                    },
                    timeout=120.0
                )

                if response.status_code == 200:
                    result = response.json()
                    content = result.get("message", {}).get("content", "")
                    print(f"[LLMService] Ollama 응답 생성 완료 (길이: {len(content) if content else 0})")
                    return content
                else:
                    print(f"[LLMService] Ollama API 오류: {response.status_code} - {response.text}")
                    return f"Ollama API 오류: {response.status_code}"

        except Exception as e:
            print(f"[LLMService] Ollama API 오류: {str(e)}")
            return f"Ollama API 오류: {str(e)}"

    async def analyze_plagiarism_suspicion(self,
                                    original_resume: Dict[str, Any],
                                    similar_resumes: List[Dict[str, Any]],
                                    document_type: str = "자소서") -> Dict[str, Any]:
        """
        표절 의심도를 분석합니다.

        Args:
            original_resume (Dict[str, Any]): 원본 문서
            similar_resumes (List[Dict[str, Any]]): 유사한 문서들
            document_type (str): 문서 타입 ("이력서" 또는 "자소서")

        Returns:
            Dict[str, Any]: 표절 의심도 분석 결과
        """
        try:
            print(f"[LLMService] === 표절 의심도 분석 시작 ===")

            # 자소서의 경우 applicant_id로 지원자 이름을 조회해야 함
            if document_type == "자소서":
                original_name = original_resume.get('basic_info_names') or original_resume.get('name')
                if not original_name:
                    # applicant_id가 있으면 해당 지원자의 이름을 표시
                    applicant_id = original_resume.get('applicant_id')
                    if applicant_id:
                        original_name = f"지원자ID_{applicant_id}"
                    else:
                        original_name = "Unknown"
            else:
                original_name = original_resume.get('name', 'Unknown')
            print(f"[LLMService] 원본 {document_type}: {original_name}")
            print(f"[LLMService] 유사한 {document_type} 수: {len(similar_resumes)}")

            if not similar_resumes:
                print(f"[LLMService] 유사한 {document_type}가 없음 - LOW 의심도 반환")
                return {
                    "success": True,
                    "suspicion_level": "LOW",
                    "suspicion_score": 0.0,
                    "suspicion_score_percent": 0,
                    "analysis": f"유사한 {document_type}가 발견되지 않았습니다. 표절 의심도가 낮습니다.",
                    "recommendations": []
                }

            # 최고 유사도 점수 확인 (API 응답 구조에 맞게 수정)
            similarities = []
            for resume in similar_resumes:
                if "similarity_score" in resume:
                    similarities.append(resume["similarity_score"])
                elif "overall_similarity" in resume:
                    similarities.append(resume["overall_similarity"])
                else:
                    print(f"[LLMService] 경고: 유사도 점수를 찾을 수 없음 - {resume.keys()}")
                    similarities.append(0.0)

            max_similarity = max(similarities) if similarities else 0.0
            print(f"[LLMService] 최고 유사도 점수: {max_similarity:.3f}")

            # 의심도 레벨 결정
            if max_similarity >= 0.8:
                suspicion_level = "HIGH"
            elif max_similarity >= 0.6:
                suspicion_level = "MEDIUM"
            else:
                suspicion_level = "LOW"

            suspicion_score = max_similarity

            # LLM을 사용하여 상세한 분석 생성
            analysis = await self._generate_plagiarism_analysis(
                max_similarity, suspicion_level, len(similar_resumes), document_type, similar_resumes
            )

            recommendations = []

            print(f"[LLMService] 의심도 결정 완료: {suspicion_level} (점수: {suspicion_score:.3f})")
            print(f"[LLMService] === 표절 의심도 분석 완료 ===")

            return {
                "success": True,
                "suspicion_level": suspicion_level,
                "suspicion_score": suspicion_score,
                "suspicion_score_percent": int(suspicion_score * 100),
                "analysis": analysis,
                "recommendations": recommendations,
                "similar_count": len(similar_resumes),
                "analyzed_at": datetime.now().isoformat()
            }

        except Exception as e:
            print(f"[LLMService] === 표절 의심도 분석 중 오류 발생 ===")
            print(f"[LLMService] 오류 타입: {type(e).__name__}")
            print(f"[LLMService] 오류 메시지: {str(e)}")
            import traceback
            print(f"[LLMService] 스택 트레이스: {traceback.format_exc()}")
            return {
                "success": False,
                "error": str(e),
                "suspicion_level": "UNKNOWN",
                "suspicion_score": 0.0,
                "suspicion_score_percent": 0,
                "analysis": "표절 의심도 분석에 실패했습니다.",
                "analyzed_at": datetime.now().isoformat()
            }

    async def analyze_ideal_candidate(self, applicant_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        지원자 정보를 바탕으로 이상적인 인재상 LLM 분석 수행

        Args:
            applicant_info (Dict): 지원자 정보

        Returns:
            Dict: LLM 분석 결과 (5개의 이상적인 인재상)
        """
        try:
            print(f"[LLMService] === 이상적인 인재상 LLM 분석 시작 ===")
            print(f"[LLMService] 지원자: {applicant_info.get('name', 'N/A')}")

            # LLM 프롬프트 구성
            prompt = self._create_ideal_candidate_analysis_prompt(applicant_info)

            # OpenAI API 호출
            client = openai.OpenAI(api_key=self.openai_api_key)
            response = client.chat.completions.create(
                model=self.openai_model,
                messages=[
                    {"role": "system", "content": "당신은 인재 채용 전문가입니다. 지원자의 정보를 바탕으로 해당 직무에 최적화된 이상적인 인재상 5개를 분석해주세요. 반드시 요청된 정확한 형식을 따라 응답해주세요."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,  # 더 일관된 응답을 위해 낮춤
                max_tokens=1500
            )

            analysis_text = response.choices[0].message.content.strip()

            print(f"[LLMService] LLM 분석 완료")
            print(f"[LLMService] === LLM 분석 결과 ===")
            print(analysis_text[:500] + "..." if len(analysis_text) > 500 else analysis_text)
            print(f"[LLMService] === LLM 분석 결과 끝 ===")

            return {
                "success": True,
                "analysis": analysis_text,
                "target_applicant": applicant_info.get('name', 'N/A'),
                "analysis_type": "ideal_candidate",
                "recommendation_count": 5,
                "analyzed_at": datetime.now().isoformat()
            }

        except Exception as e:
            print(f"[LLMService] 이상적인 인재상 분석 실패: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message": "이상적인 인재상 분석 중 오류가 발생했습니다.",
                "analyzed_at": datetime.now().isoformat()
            }

    async def analyze_similar_applicants(self, target_applicant: Dict[str, Any],
                                       similar_applicants: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        유사 지원자들에 대한 LLM 분석 수행

        Args:
            target_applicant (Dict): 기준 지원자 정보
            similar_applicants (List[Dict]): 유사한 지원자들 정보

        Returns:
            Dict: LLM 분석 결과
        """
        try:
            print(f"[LLMService] === 유사 지원자 LLM 분석 시작 ===")
            print(f"[LLMService] 기준 지원자: {target_applicant.get('name', 'N/A')}")
            print(f"[LLMService] 유사 지원자 수: {len(similar_applicants)}")

            if not similar_applicants:
                return {
                    "success": False,
                    "message": "분석할 유사 지원자가 없습니다."
                }

            # LLM 프롬프트 구성
            prompt = self._create_similar_applicants_analysis_prompt(target_applicant, similar_applicants)

            # OpenAI API 호출
            client = openai.OpenAI(api_key=self.openai_api_key)
            response = client.chat.completions.create(
                model=self.openai_model,
                messages=[
                    {"role": "system", "content": "당신은 인재 채용 전문가입니다. 반드시 요청된 정확한 형식을 따라 응답해주세요. 특히 '### 3. 각 유사 지원자별 상세 분석' 섹션에서 각 지원자마다 🔍 핵심 공통점, 💡 주요 특징, ⭐ 추천 이유, 🎯 유사성 요인을 모두 포함해야 합니다."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,  # 더 일관된 응답을 위해 낮춤
                max_tokens=1000
            )

            analysis_text = response.choices[0].message.content.strip()

            print(f"[LLMService] LLM 분석 완료")
            print(f"[LLMService] === LLM 분석 결과 ===")
            print(analysis_text[:500] + "..." if len(analysis_text) > 500 else analysis_text)
            print(f"[LLMService] === LLM 분석 결과 끝 ===")

            return {
                "success": True,
                "analysis": analysis_text,
                "target_applicant": target_applicant,
                "similar_count": len(similar_applicants),
                "analyzed_at": datetime.now().isoformat()
            }

        except Exception as e:
            print(f"[LLMService] 유사 지원자 분석 실패: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message": "유사 지원자 분석 중 오류가 발생했습니다.",
                "analyzed_at": datetime.now().isoformat()
            }

    def _create_similar_applicants_analysis_prompt(self, target_applicant: Dict[str, Any],
                                                 similar_applicants: List[Dict[str, Any]]) -> str:
        """유사 지원자 분석용 프롬프트 생성"""

        # 기준 지원자 정보
        prompt = f"""다음 기준 지원자와 유사한 지원자들을 찾았습니다. 왜 유사한지 분석해주세요.

**기준 지원자:**
- 이름: {target_applicant.get('name', 'N/A')}
- 지원직무: {target_applicant.get('position', 'N/A')}
- 경력: {target_applicant.get('experience', 'N/A')}
- 기술스택: {target_applicant.get('skills', 'N/A')}
- 부서: {target_applicant.get('department', 'N/A')}

**유사한 지원자들:**
"""

        # 유사 지원자들 정보
        for applicant in similar_applicants:
            prompt += f"""
{applicant['rank']}순위. {applicant.get('name', 'N/A')}
- 지원직무: {applicant.get('position', 'N/A')}
- 경력: {applicant.get('experience', 'N/A')}
- 기술스택: {applicant.get('skills', 'N/A')}
- 부서: {applicant.get('department', 'N/A')}
- 유사도 점수: {applicant.get('final_score', 0):.3f} (벡터: {applicant.get('vector_score', 0):.3f}, 키워드: {applicant.get('keyword_score', 0):.3f})
"""

        prompt += """

**분석 요청:** 각 유사 지원자별로 다음 정보를 간결하게 제시해주세요:

### 1. 기준 지원자와 각 유사 지원자 간의 공통점
### 2. 유사성에 가장 큰 영향을 미친 특성 분석
### 3. 각 유사 지원자별 상세 분석

- **[지원자명]**
    - 🔍 **핵심 공통점**: [기준 지원자와의 주요 공통점 1줄]
    - 💡 **주요 특징**: [핵심 역량이나 경력 요약 1줄]
    - ⭐ **추천 이유**: [아래 5가지 기준 중 가장 해당하는 요소를 선택하여 구체적으로 설명]
            * 기술적 우위성: 기준 지원자보다 더 발전된 기술이나 추가 기술 보유
            * 경력 깊이: 더 많은 경험이나 고급 프로젝트 수행 경험
            * 전문성 확장: 기준 지원자와 유사하면서도 추가적인 전문 영역 보유
            * 성장 궤적: 더 빠른 성장이나 도전적인 경험 이력
            * 부가 가치: 기준 지원자에게 없는 추가적인 스킬이나 경험

            예시: "Kubernetes와 Docker 등 DevOps 기술을 추가로 보유하여 기술적 우위성이 있음"
            예시: "10년 경력으로 엔터프라이즈 급 시스템 구축 경험이 풍부하여 경력 깊이가 뛰어남"
    - 🎯 **유사성 요인**: [유사성에 가장 큰 영향을 미친 특성]

**작성 규칙:**
- 추천 이유는 반드시 구체적인 근거와 함께 작성할 것 (단순히 "경력 깊이", "기술적 우위성" 등의 단어만 쓰지 말 것)
- 각 항목은 간결하게 1-2줄 이내로 작성
- 이모지를 활용하여 가독성 향상
- 구체적이고 실용적인 정보 위주로 작성

**금지사항:**
- 추천 이유에 "경력 깊이", "기술적 우위성" 등의 단어만 단독으로 사용 금지
- 반드시 구체적인 기술명, 경력연수, 프로젝트 경험 등과 함께 서술할 것
"""

        return prompt

    def _create_ideal_candidate_analysis_prompt(self, applicant_info: Dict[str, Any]) -> str:
        """이상적인 인재상 분석용 프롬프트 생성"""

        # 지원자 정보 수집
        name = applicant_info.get('name', 'N/A')
        position = applicant_info.get('position', 'N/A')
        experience = applicant_info.get('experience', 'N/A')
        skills = applicant_info.get('skills', 'N/A')
        department = applicant_info.get('department', 'N/A')
        education = applicant_info.get('education', 'N/A')
        growth_background = applicant_info.get('growthBackground', '')
        motivation = applicant_info.get('motivation', '')
        career_history = applicant_info.get('careerHistory', '')
        resume_text = applicant_info.get('resume_text', '')
        resume_summary = applicant_info.get('resume_summary', '')
        resume_keywords = applicant_info.get('resume_keywords', [])

        # 프롬프트 구성
        prompt = f"""다음 지원자의 정보를 바탕으로 해당 직무에 최적화된 이상적인 인재상 5개를 제시해주세요.

**지원자 정보:**
- 이름: {name}
- 지원직무: {position}
- 경력: {experience}
- 기술스택: {skills}
- 부서: {department}
- 학력: {education}

**지원자 배경 정보:**
- 성장배경: {growth_background if growth_background else '정보 없음'}
- 지원동기: {motivation if motivation else '정보 없음'}
- 경력사항: {career_history if career_history else '정보 없음'}

**이력서 내용:**
- 이력서 요약: {resume_summary if resume_summary else '정보 없음'}
- 이력서 키워드: {', '.join(resume_keywords) if resume_keywords else '정보 없음'}
- 이력서 상세: {resume_text[:500] + '...' if len(resume_text) > 500 else resume_text if resume_text else '정보 없음'}

**분석 요청:**
위 지원자의 정보를 종합적으로 분석하여, 해당 직무({position})에 가장 적합한 이상적인 인재상 5개를 제시해주세요.

**중요: 반드시 아래 정확한 형식을 따라 응답해주세요.**

### 이상적인 인재상 분석 결과

#### 1. [인재상 제목 1]
- **핵심 역량**: [해당 인재상의 핵심 역량 설명]
- **적합성 근거**: [지원자 정보와의 연관성 및 적합성]
- **기대 효과**: [해당 인재상이 조직에 미칠 긍정적 영향]

#### 2. [인재상 제목 2]
- **핵심 역량**: [해당 인재상의 핵심 역량 설명]
- **적합성 근거**: [지원자 정보와의 연관성 및 적합성]
- **기대 효과**: [해당 인재상이 조직에 미칠 긍정적 영향]

#### 3. [인재상 제목 3]
- **핵심 역량**: [해당 인재상의 핵심 역량 설명]
- **적합성 근거**: [지원자 정보와의 연관성 및 적합성]
- **기대 효과**: [해당 인재상이 조직에 미칠 긍정적 영향]

#### 4. [인재상 제목 4]
- **핵심 역량**: [해당 인재상의 핵심 역량 설명]
- **적합성 근거**: [지원자 정보와의 연관성 및 적합성]
- **기대 효과**: [해당 인재상이 조직에 미칠 긍정적 영향]

#### 5. [인재상 제목 5]
- **핵심 역량**: [해당 인재상의 핵심 역량 설명]
- **적합성 근거**: [지원자 정보와의 연관성 및 적합성]
- **기대 효과**: [해당 인재상이 조직에 미칠 긍정적 영향]

### 종합 평가
- **전체 적합도**: [지원자의 전체적인 적합도 평가]
- **주요 강점**: [지원자의 주요 강점 3가지]
- **개선 제안**: [지원자의 개선 가능한 영역 2-3가지]

**필수 준수사항:**
1. 반드시 5개의 인재상을 제시하세요
2. 각 인재상은 지원자의 실제 정보를 바탕으로 구체적으로 작성하세요
3. 위 형식을 정확히 따르지 않으면 시스템에서 파싱이 실패합니다
4. 인재상 제목은 직무와 관련된 구체적이고 명확한 표현을 사용하세요
"""

        return prompt

    async def _generate_plagiarism_analysis(self,
                                          similarity_score: float,
                                          suspicion_level: str,
                                          similar_count: int,
                                          document_type: str,
                                          similar_documents: List[Dict[str, Any]]) -> str:
        """
        LLM을 사용하여 표절 의심도 분석 결과를 생성합니다.

        Args:
            similarity_score (float): 최고 유사도 점수 (0.0 ~ 1.0)
            suspicion_level (str): 위험도 레벨 (HIGH/MEDIUM/LOW)
            similar_count (int): 유사한 문서 개수
            document_type (str): 문서 타입
            similar_documents (List[Dict]): 유사한 문서들의 상세 정보

        Returns:
            str: LLM이 생성한 상세 분석 텍스트
        """
        try:
            print(f"[LLMService] LLM 기반 표절 의심도 분석 시작...")

            # 유사도 점수들을 수집
            similarity_details = []
            for doc in similar_documents[:3]:  # 상위 3개만 분석에 포함
                score = doc.get("similarity_score", doc.get("overall_similarity", 0.0))
                name = doc.get("basic_info_names", doc.get("name", "Unknown"))
                similarity_details.append(f"- {name}: {score:.1%} 유사도")


            # LLM 프롬프트 구성
            prompt = f"""다음 정보를 바탕으로 {document_type} 표절 의심도를 분석해주세요:

[역할]
당신은 자기소개서의 의미 기반 유사성을 평가하는 검토 보조자입니다.
기준 자소서의 일부 문장에서 의미 중복이 감지된 경우, 표현 구조나 흐름 중심으로 평가를 제공합니다.

[입력 데이터]
- 기준 자소서 문장 중 유사도가 높은 문장 1~2개
- 각 문장에 대한 유사도 레벨 (HIGH / MEDIUM / LOW)
- 각 문장에 대해 유사 판단된 이유 (표현 구조, 흐름, 키워드 등)

[작성 목표]
- 유사도 수치나 유사 자소서 개수는 **말하지 마세요**
- 기준 자소서 내 **유사 문장**과 그에 대한 **유사 이유**만 간결하게 제시
- 마지막 줄에는 중립적 LLM 평가 문장을 넣으세요 ("검토 권장" 등)

[출력 예시]

“‘고객 중심 사고를 바탕으로 문제를 해결했습니다.’ 문장은 표현 구조와 핵심 단어가 반복되어 HIGH 등급의 유사성이 관측되었습니다.
또한 ‘협업을 통해 어려움을 극복하며 성장했습니다.’ 문장도 유사한 흐름으로 구성되어 MEDIUM 등급으로 분류되었습니다.
일부 문장에서 의미적 중복이 나타나므로, 표절 여부에 대한 검토가 권장됩니다.”


"""

            # OpenAI API 호출
            client = openai.OpenAI(api_key=self.openai_api_key)
            response = client.chat.completions.create(
                model=self.openai_model,
                messages=[
                    {
                        "role": "system",
                        "content": "당신은 문서 표절 분석 전문가입니다. 임베딩 유사도 점수를 바탕으로 정확하고 전문적인 표절 의심도 분석을 제공해주세요."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,  # 일관성 있는 분석을 위해 낮은 temperature 사용
                max_tokens=200
            )

            analysis_text = response.choices[0].message.content.strip()

            # 3줄 제한 처리
            lines = analysis_text.split('\n')
            if len(lines) > 3:
                analysis_text = '\n'.join(lines[:3])
                print(f"[LLMService] LLM 응답이 {len(lines)}줄이므로 3줄로 제한됨")

            print(f"[LLMService] LLM 기반 표절 분석 완료 (길이: {len(analysis_text)})")

            return analysis_text

        except Exception as e:
            print(f"[LLMService] LLM 기반 분석 생성 실패: {str(e)}")
            # 폴백: 기본 규칙 기반 분석
            if suspicion_level == "HIGH":
                return f"매우 높은 유사도({similarity_score:.1%})의 {document_type}가 {similar_count}개 발견되었습니다. 표절 의심도가 높아 추가 검토가 필요합니다."
            elif suspicion_level == "MEDIUM":
                return f"높은 유사도({similarity_score:.1%})의 {document_type}가 {similar_count}개 발견되었습니다. 표절 의심도가 보통 수준이므로 주의가 필요합니다."
            else:
                return f"적정 수준의 유사도({similarity_score:.1%})입니다. 유사한 {document_type} {similar_count}개가 발견되었으나 표절 의심도가 낮습니다."
