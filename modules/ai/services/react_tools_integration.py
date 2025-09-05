"""
ReAct 에이전트용 핵심 도구 통합
채용 관련 툴 제거, 핵심 AI 툴들만 유지
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from routers.pick_chatbot import ToolExecutor

from modules.ai.services.react_agent_core import ReActMemory, ReActStep, ReActTool

logger = logging.getLogger(__name__)

class SearchTool(ReActTool):
    """검색 도구 (기존 ToolExecutor 통합)"""

    def __init__(self):
        super().__init__("search", "웹 검색 및 정보 조회를 수행합니다")
        self.tool_executor = ToolExecutor()

    async def execute(self, query: str = "", **kwargs) -> Tuple[str, Dict[str, Any]]:
        """검색 도구 실행"""
        try:
            if not query:
                query = kwargs.get("input_text", "")

            if not query:
                return "검색어가 필요합니다.", {"error": "query required", "status": "failed"}

            result = await self.tool_executor.search_tool("search", query=query, **kwargs)

            if result.get("status") == "success":
                search_results = result.get("data", [])
                return f"'{query}'에 대한 검색 결과 {len(search_results)}개를 찾았습니다.", {
                    "query": query,
                    "results_count": len(search_results),
                    "results": search_results[:3],  # 최대 3개만 반환
                    "status": "success"
                }
            else:
                return f"검색에 실패했습니다: {result.get('error', '알 수 없는 오류')}", {
                    "error": result.get("error"),
                    "status": "failed"
                }

        except Exception as e:
            logger.error(f"SearchTool 실행 오류: {str(e)}")
            return f"검색 도구 실행 중 오류가 발생했습니다: {str(e)}", {
                "error": str(e),
                "status": "error"
            }

    def can_handle(self, task: str) -> bool:
        """검색 작업 처리 가능 여부"""
        search_keywords = ["검색", "찾아", "알아봐", "조회", "확인", "search"]
        return any(keyword in task.lower() for keyword in search_keywords)

class AIAnalysisTool(ReActTool):
    """AI 분석 도구"""

    def __init__(self):
        super().__init__("ai_analysis", "AI를 활용한 데이터 분석을 수행합니다")
        self.tool_executor = ToolExecutor()

    async def execute(self, analysis_type: str = "general", **kwargs) -> Tuple[str, Dict[str, Any]]:
        """AI 분석 도구 실행"""
        try:
            data = kwargs.get("data", "")
            if not data:
                return "분석할 데이터가 필요합니다.", {"error": "data required", "status": "failed"}

            # 기본적으로 일반 분석으로 처리
            result = await self.tool_executor.ai_analysis_tool("analyze_resume", resume_text=data)

            if result.get("status") == "success":
                analysis_result = result.get("analysis", {})
                return f"AI 분석을 완료했습니다: {analysis_type} 분석", {
                    "analysis_type": analysis_type,
                    "result": analysis_result,
                    "status": "success"
                }
            else:
                return f"AI 분석에 실패했습니다: {result.get('message', '알 수 없는 오류')}", {
                    "error": result.get("message"),
                    "status": "failed"
                }

        except Exception as e:
            logger.error(f"AIAnalysisTool 실행 오류: {str(e)}")
            return f"AI 분석 도구 실행 중 오류가 발생했습니다: {str(e)}", {
                "error": str(e),
                "status": "error"
            }

    def can_handle(self, task: str) -> bool:
        """AI 분석 작업 처리 가능 여부"""
        analysis_keywords = [
            "분석", "AI 분석", "데이터 분석", "평가", "검토", "확인", "점검",
            "ai analysis", "analyze"
        ]
        return any(keyword in task.lower() for keyword in analysis_keywords)

class GitHubTool(ReActTool):
    """GitHub 정보 조회 도구"""

    def __init__(self):
        super().__init__("github", "GitHub 프로필, 레포지토리 정보를 조회합니다")
        self.tool_executor = ToolExecutor()

    async def execute(self, action: str = "get_profile", **kwargs) -> Tuple[str, Dict[str, Any]]:
        """GitHub 도구 실행"""
        try:
            result = await self.tool_executor.github_tool(action, **kwargs)

            if result.get("status") == "success":
                return f"GitHub {action} 작업을 성공적으로 수행했습니다.", {
                    "data": result.get("data", {}),
                    "status": "success"
                }
            else:
                return f"GitHub {action} 작업에 실패했습니다: {result.get('error', '알 수 없는 오류')}", {
                    "error": result.get("error"),
                    "status": "failed"
                }
        except Exception as e:
            logger.error(f"GitHubTool 실행 오류: {str(e)}")
            return f"GitHub 도구 실행 중 오류가 발생했습니다: {str(e)}", {
                "error": str(e),
                "status": "error"
            }

    def can_handle(self, task: str) -> bool:
        """GitHub 관련 작업 처리 가능 여부"""
        github_keywords = ["github", "깃허브", "레포지토리", "프로필", "커밋", "repository"]
        return any(keyword in task.lower() for keyword in github_keywords)

class MongoDBTool(ReActTool):
    """MongoDB 데이터베이스 조회 도구"""

    def __init__(self):
        super().__init__("mongodb", "MongoDB 데이터베이스에서 정보를 조회합니다")
        self.tool_executor = ToolExecutor()

    async def execute(self, action: str = "query", **kwargs) -> Tuple[str, Dict[str, Any]]:
        """MongoDB 도구 실행"""
        try:
            result = await self.tool_executor.mongodb_tool(action, **kwargs)

            if result.get("status") == "success":
                data = result.get("data", [])
                return f"MongoDB {action} 작업을 성공적으로 수행했습니다. {len(data)}개 결과를 찾았습니다.", {
                    "count": len(data),
                    "data": data[:5],  # 최대 5개만 반환
                    "status": "success"
                }
            else:
                return f"MongoDB {action} 작업에 실패했습니다: {result.get('error', '알 수 없는 오류')}", {
                    "error": result.get("error"),
                    "status": "failed"
                }
        except Exception as e:
            logger.error(f"MongoDBTool 실행 오류: {str(e)}")
            return f"MongoDB 도구 실행 중 오류가 발생했습니다: {str(e)}", {
                "error": str(e),
                "status": "error"
            }

    def can_handle(self, task: str) -> bool:
        """MongoDB 관련 작업 처리 가능 여부"""
        mongodb_keywords = ["데이터베이스", "db", "mongodb", "데이터", "조회", "검색", "database"]
        return any(keyword in task.lower() for keyword in mongodb_keywords)

class MailTool(ReActTool):
    """메일 발송 도구"""

    def __init__(self):
        super().__init__("mail", "메일 발송 및 템플릿 관리를 수행합니다")
        self.tool_executor = ToolExecutor()

    async def execute(self, action: str = "send_test", **kwargs) -> Tuple[str, Dict[str, Any]]:
        """메일 도구 실행"""
        try:
            result = await self.tool_executor.mail_tool(action, **kwargs)

            if result.get("status") == "success":
                return f"메일 {action} 작업을 성공적으로 수행했습니다.", {
                    "data": result.get("data", {}),
                    "status": "success"
                }
            else:
                return f"메일 {action} 작업에 실패했습니다: {result.get('error', '알 수 없는 오류')}", {
                    "error": result.get("error"),
                    "status": "failed"
                }
        except Exception as e:
            logger.error(f"MailTool 실행 오류: {str(e)}")
            return f"메일 도구 실행 중 오류가 발생했습니다: {str(e)}", {
                "error": str(e),
                "status": "error"
            }

    def can_handle(self, task: str) -> bool:
        """메일 관련 작업 처리 가능 여부"""
        mail_keywords = ["메일", "이메일", "발송", "전송", "mail", "email", "send"]
        return any(keyword in task.lower() for keyword in mail_keywords)

class WebAutomationTool(ReActTool):
    """웹 자동화 도구"""

    def __init__(self):
        super().__init__("web_automation", "웹 페이지 자동화 작업을 수행합니다")
        self.tool_executor = ToolExecutor()

    async def execute(self, action: str = "navigate", **kwargs) -> Tuple[str, Dict[str, Any]]:
        """웹 자동화 도구 실행"""
        try:
            result = await self.tool_executor.web_automation_tool(action, **kwargs)

            if result.get("status") == "success":
                return f"웹 자동화 {action} 작업을 성공적으로 수행했습니다.", {
                    "data": result.get("data", {}),
                    "status": "success"
                }
            else:
                return f"웹 자동화 {action} 작업에 실패했습니다: {result.get('error', '알 수 없는 오류')}", {
                    "error": result.get("error"),
                    "status": "failed"
                }
        except Exception as e:
            logger.error(f"WebAutomationTool 실행 오류: {str(e)}")
            return f"웹 자동화 도구 실행 중 오류가 발생했습니다: {str(e)}", {
                "error": str(e),
                "status": "error"
            }

    def can_handle(self, task: str) -> bool:
        """웹 자동화 관련 작업 처리 가능 여부"""
        web_keywords = ["웹", "페이지", "클릭", "입력", "자동화", "web", "automation", "navigate"]
        return any(keyword in task.lower() for keyword in web_keywords)

class FileUploadTool(ReActTool):
    """파일 업로드/다운로드 도구"""

    def __init__(self):
        super().__init__("file_upload", "파일 업로드 및 다운로드를 수행합니다")
        self.tool_executor = ToolExecutor()

    async def execute(self, action: str = "upload", **kwargs) -> Tuple[str, Dict[str, Any]]:
        """파일 업로드 도구 실행"""
        try:
            # 파일 업로드 관련 작업은 ToolExecutor에 구현되어 있지 않으므로 기본 응답
            if action == "upload":
                return "파일 업로드 기능이 준비되었습니다. 파일을 선택해주세요.", {
                    "status": "ready",
                    "action": "upload"
                }
            elif action == "download":
                return "파일 다운로드 기능이 준비되었습니다.", {
                    "status": "ready",
                    "action": "download"
                }
            else:
                return f"지원하지 않는 파일 액션입니다: {action}", {
                    "error": "unsupported action",
                    "status": "failed"
                }
        except Exception as e:
            logger.error(f"FileUploadTool 실행 오류: {str(e)}")
            return f"파일 업로드 도구 실행 중 오류가 발생했습니다: {str(e)}", {
                "error": str(e),
                "status": "error"
            }

    def can_handle(self, task: str) -> bool:
        """파일 업로드 관련 작업 처리 가능 여부"""
        file_keywords = ["파일", "업로드", "다운로드", "file", "upload", "download", "첨부"]
        return any(keyword in task.lower() for keyword in file_keywords)

class NavigateTool(ReActTool):
    """페이지 네비게이션 도구"""

    def __init__(self):
        super().__init__("navigate", "페이지 이동 및 UI 조작을 수행합니다")
        self.tool_executor = ToolExecutor()

    async def execute(self, action: str = "page_navigate", **kwargs) -> Tuple[str, Dict[str, Any]]:
        """네비게이션 도구 실행"""
        try:
            target_page = kwargs.get("target", "/")

            if action == "page_navigate":
                return f"페이지를 {target_page}로 이동합니다.", {
                    "target": target_page,
                    "action": "navigate",
                    "status": "success"
                }
            elif action == "open_modal":
                modal_name = kwargs.get("modal", "default")
                return f"{modal_name} 모달을 엽니다.", {
                    "modal": modal_name,
                    "action": "open_modal",
                    "status": "success"
                }
            elif action == "scroll_to":
                element = kwargs.get("element", "top")
                return f"페이지를 {element}로 스크롤합니다.", {
                    "element": element,
                    "action": "scroll_to",
                    "status": "success"
                }
            else:
                return f"지원하지 않는 네비게이션 액션입니다: {action}", {
                    "error": "unsupported action",
                    "status": "failed"
                }
        except Exception as e:
            logger.error(f"NavigateTool 실행 오류: {str(e)}")
            return f"네비게이션 도구 실행 중 오류가 발생했습니다: {str(e)}", {
                "error": str(e),
                "status": "error"
            }

    def can_handle(self, task: str) -> bool:
        """네비게이션 관련 작업 처리 가능 여부"""
        nav_keywords = ["이동", "페이지", "모달", "스크롤", "navigate", "page", "modal", "scroll"]
        return any(keyword in task.lower() for keyword in nav_keywords)

class EnhancedReActAgent:
    """핵심 도구만 통합된 향상된 ReAct 에이전트"""

    def __init__(self, max_steps: int = 10):
        self.max_steps = max_steps
        self.memory = ReActMemory(max_steps=max_steps)

        # 핵심 도구들만 초기화 (채용 관련 툴 제거)
        self.tools = {
            # 핵심 AI 툴들
            "search": SearchTool(),
            "ai_analysis": AIAnalysisTool(),

            # 미활성화되었던 툴들 (이제 활성화)
            "github": GitHubTool(),
            "mongodb": MongoDBTool(),
            "mail": MailTool(),
            "web_automation": WebAutomationTool(),

            # 새로 추가된 툴들
            "file_upload": FileUploadTool(),
            "navigate": NavigateTool()
        }

    async def process_task(self, user_goal: str, initial_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """작업 처리 메인 메서드"""
        logger.info(f"[EnhancedReActAgent] 작업 시작: {user_goal}")

        # 초기화
        self.memory = ReActMemory(max_steps=self.max_steps)
        self.memory.current_goal = user_goal
        self.memory.context = initial_context or {}

        try:
            # ReAct 루프 실행
            for step_num in range(self.max_steps):
                logger.info(f"[EnhancedReActAgent] 단계 {step_num + 1}/{self.max_steps} 시작")

                # 1. 추론 (Reasoning)
                reasoning = await self._reason(step_num)
                self.memory.add_step(ReActStep.REASONING, reasoning)

                # 2. 액션 (Action)
                action_result = await self._act(reasoning)
                self.memory.add_step(ReActStep.ACTION, action_result["action"], action_result["metadata"])

                # 3. 관찰 (Observation)
                observation = await self._observe(action_result)
                self.memory.add_step(ReActStep.OBSERVATION, observation["content"], observation["metadata"])

                # 목표 달성 확인
                if self.memory.is_goal_achieved():
                    logger.info("[EnhancedReActAgent] 목표 달성 감지")
                    break

            # 최종 응답 생성
            final_response = await self._generate_final_response()
            self.memory.add_step(ReActStep.FINAL, final_response)

            return {
                "success": True,
                "response": final_response,
                "steps": self.memory.steps,
                "goal_achieved": self.memory.is_goal_achieved(),
                "total_steps": len(self.memory.steps)
            }

        except Exception as e:
            logger.error(f"[EnhancedReActAgent] 오류 발생: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "steps": self.memory.steps,
                "partial_response": self.memory.get_recent_context()
            }

    async def _reason(self, step_num: int) -> str:
        """추론 단계"""
        context = self.memory.get_recent_context()
        goal = self.memory.current_goal

        # 사용 가능한 도구들 고려
        available_tools = [tool.name for tool in self.tools.values() if tool.can_handle(goal)]

        if step_num == 0:
            reasoning = f"사용자 목표: '{goal}'를 달성하기 위해 먼저 필요한 정보를 파악해야 합니다."
        else:
            reasoning = f"이전 단계의 결과를 바탕으로 '{goal}' 목표 달성을 위한 다음 단계를 계획합니다."

        if available_tools:
            reasoning += f" 사용 가능한 도구: {', '.join(available_tools)}"

        return reasoning

    async def _act(self, reasoning: str) -> Dict[str, Any]:
        """액션 단계"""
        goal = self.memory.current_goal

        # 적절한 도구 선택
        selected_tool = None
        for tool in self.tools.values():
            if tool.can_handle(goal):
                selected_tool = tool
                break

        if not selected_tool:
            # 기본 도구 사용
            selected_tool = self.tools["search"]

        # 도구 실행
        try:
            # 도구별 적절한 매개변수 전달
            if selected_tool.name == "search":
                result, metadata = await selected_tool.execute(query=goal)
            elif selected_tool.name == "ai_analysis":
                result, metadata = await selected_tool.execute(data=goal, analysis_type="general")
            elif selected_tool.name == "github":
                result, metadata = await selected_tool.execute(action="get_profile", username=goal)
            elif selected_tool.name == "mongodb":
                result, metadata = await selected_tool.execute(action="query", collection="applicants")
            elif selected_tool.name == "mail":
                result, metadata = await selected_tool.execute(action="send_test", subject=goal)
            elif selected_tool.name == "web_automation":
                result, metadata = await selected_tool.execute(action="navigate", url=goal)
            elif selected_tool.name == "file_upload":
                result, metadata = await selected_tool.execute(action="upload", filename=goal)
            elif selected_tool.name == "navigate":
                result, metadata = await selected_tool.execute(action="page_navigate", target="/")
            else:
                result, metadata = await selected_tool.execute(query=goal)

            return {
                "action": f"{selected_tool.name} 도구를 사용하여 '{goal}' 작업을 수행했습니다.",
                "tool_result": result,
                "metadata": metadata
            }
        except Exception as e:
            return {
                "action": f"{selected_tool.name} 도구 실행 중 오류 발생",
                "tool_result": f"오류: {str(e)}",
                "metadata": {"error": str(e)}
            }

    async def _observe(self, action_result: Dict[str, Any]) -> Dict[str, Any]:
        """관찰 단계"""
        tool_result = action_result.get("tool_result", "")
        metadata = action_result.get("metadata", {})

        # 결과 분석
        if "오류" in tool_result or "실패" in tool_result:
            observation = f"액션 실행 중 문제가 발생했습니다: {tool_result}"
        else:
            observation = f"액션 결과를 분석했습니다: {tool_result}"

        return {
            "content": observation,
            "metadata": {
                "analysis": "결과 분석 완료",
                "next_action_needed": not self.memory.is_goal_achieved(),
                **metadata
            }
        }

    async def _generate_final_response(self) -> str:
        """최종 응답 생성"""
        if self.memory.is_goal_achieved():
            response = f"✅ '{self.memory.current_goal}' 목표를 성공적으로 달성했습니다!\n\n"
        else:
            response = f"⚠️ '{self.memory.current_goal}' 목표 달성을 위해 {len(self.memory.steps)}단계를 수행했습니다.\n\n"

        # 주요 단계 요약
        response += "📋 수행된 주요 단계:\n"
        for i, step in enumerate(self.memory.steps, 1):
            if step["step_type"] == "action":
                response += f"{i}. {step['content']}\n"

        return response

# 테스트용 함수
async def test_enhanced_react_agent():
    """향상된 ReAct 에이전트 테스트"""
    agent = EnhancedReActAgent(max_steps=5)

    test_goals = [
        "최신 AI 기술 트렌드를 검색해주세요",
        "GitHub 프로필을 확인해주세요",
        "데이터베이스에서 정보를 조회해주세요"
    ]

    for goal in test_goals:
        print(f"\n{'='*50}")
        print(f"테스트 목표: {goal}")
        print(f"{'='*50}")

        result = await agent.process_task(goal)

        print(f"성공: {result['success']}")
        print(f"응답: {result['response']}")
        print(f"총 단계: {result.get('total_steps', 0)}")

        if result.get('steps'):
            print("\n단계별 상세:")
            for step in result['steps']:
                print(f"  [{step['step_type']}] {step['content']}")

if __name__ == "__main__":
    # 테스트 실행
    asyncio.run(test_enhanced_react_agent())
