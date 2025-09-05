"""
ReActAgent 핵심 구현
추론(Reasoning) - 액션(Action) - 관찰(Observation) 루프를 통한 에이전트 시스템
"""

import asyncio
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

class ReActStep(Enum):
    """ReAct 단계 정의"""
    REASONING = "reasoning"
    ACTION = "action"
    OBSERVATION = "observation"
    FINAL = "final"

@dataclass
class ReActMemory:
    """ReAct 에이전트 메모리"""
    steps: List[Dict[str, Any]] = field(default_factory=list)
    current_goal: str = ""
    context: Dict[str, Any] = field(default_factory=dict)
    max_steps: int = 10

    def add_step(self, step_type: ReActStep, content: str, metadata: Dict[str, Any] = None):
        """단계 추가"""
        step = {
            "step_type": step_type.value,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        self.steps.append(step)
        logger.info(f"[ReAct] {step_type.value} 단계 추가: {content[:100]}...")

    def get_recent_context(self, n: int = 3) -> str:
        """최근 컨텍스트 반환"""
        recent_steps = self.steps[-n:] if len(self.steps) >= n else self.steps
        context = []
        for step in recent_steps:
            context.append(f"[{step['step_type']}] {step['content']}")
        return "\n".join(context)

    def is_goal_achieved(self) -> bool:
        """목표 달성 여부 확인"""
        if not self.steps:
            return False

        # 최근 관찰 단계에서 목표 달성 신호 확인
        for step in reversed(self.steps[-3:]):
            if step["step_type"] == ReActStep.OBSERVATION.value:
                content = step["content"].lower()
                # 성공 키워드 확인
                success_keywords = ["완료", "완성", "성공", "달성", "해결", "생성했습니다", "찾았습니다", "분석을 완료했습니다"]
                if any(keyword in content for keyword in success_keywords):
                    return True
                # 오류가 없는 경우도 성공으로 간주 (단순 작업의 경우)
                if "오류" not in content and "문제" not in content:
                    # 연속으로 2번 성공하면 목표 달성으로 간주
                    success_count = 0
                    for prev_step in reversed(self.steps[-5:]):
                        if prev_step["step_type"] == ReActStep.OBSERVATION.value:
                            prev_content = prev_step["content"].lower()
                            if "오류" not in prev_content and "문제" not in prev_content:
                                success_count += 1
                            else:
                                break
                    if success_count >= 2:
                        return True
        return False

class ReActTool:
    """ReAct 도구 기본 클래스"""

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

    async def execute(self, **kwargs) -> Tuple[str, Dict[str, Any]]:
        """도구 실행"""
        raise NotImplementedError("도구 실행 메서드를 구현해야 합니다")

    def can_handle(self, task: str) -> bool:
        """작업 처리 가능 여부"""
        raise NotImplementedError("작업 처리 가능 여부 메서드를 구현해야 합니다")

class SearchTool(ReActTool):
    """검색 도구"""

    def __init__(self):
        super().__init__("search", "웹 검색을 통해 정보를 찾습니다")

    async def execute(self, query: str, **kwargs) -> Tuple[str, Dict[str, Any]]:
        """검색 실행"""
        # 실제 검색 로직 구현 (현재는 시뮬레이션)
        await asyncio.sleep(0.5)  # 검색 시뮬레이션

        result = f"'{query}'에 대한 검색 결과: 관련 정보를 찾았습니다."
        metadata = {
            "query": query,
            "results_count": 5,
            "sources": ["source1", "source2", "source3"]
        }

        return result, metadata

    def can_handle(self, task: str) -> bool:
        """검색 작업 처리 가능 여부"""
        search_keywords = ["검색", "찾아", "알아봐", "조회", "확인"]
        return any(keyword in task for keyword in search_keywords)

class AnalysisTool(ReActTool):
    """분석 도구"""

    def __init__(self):
        super().__init__("analyze", "데이터나 정보를 분석합니다")

    async def execute(self, data: str, analysis_type: str = "general", **kwargs) -> Tuple[str, Dict[str, Any]]:
        """분석 실행"""
        await asyncio.sleep(0.3)  # 분석 시뮬레이션

        result = f"'{data}'에 대한 {analysis_type} 분석을 완료했습니다."
        metadata = {
            "analysis_type": analysis_type,
            "data_length": len(data),
            "insights": ["인사이트1", "인사이트2"]
        }

        return result, metadata

    def can_handle(self, task: str) -> bool:
        """분석 작업 처리 가능 여부"""
        analysis_keywords = ["분석", "평가", "검토", "확인", "점검"]
        return any(keyword in task for keyword in analysis_keywords)

class GenerationTool(ReActTool):
    """생성 도구"""

    def __init__(self):
        super().__init__("generate", "콘텐츠나 문서를 생성합니다")

    async def execute(self, content_type: str, requirements: str, **kwargs) -> Tuple[str, Dict[str, Any]]:
        """생성 실행"""
        await asyncio.sleep(0.8)  # 생성 시뮬레이션

        result = f"'{requirements}' 요구사항에 따른 {content_type}을 생성했습니다."
        metadata = {
            "content_type": content_type,
            "requirements": requirements,
            "generated_length": 500
        }

        return result, metadata

    def can_handle(self, task: str) -> bool:
        """생성 작업 처리 가능 여부"""
        generation_keywords = ["생성", "만들어", "작성", "작성해", "만들"]
        return any(keyword in task for keyword in generation_keywords)

class ReActAgent:
    """ReAct 에이전트 핵심 클래스"""

    def __init__(self, max_steps: int = 10):
        self.max_steps = max_steps
        self.tools = {
            "search": SearchTool(),
            "analyze": AnalysisTool(),
            "generate": GenerationTool()
        }
        self.memory = ReActMemory(max_steps=max_steps)

    async def process_task(self, user_goal: str, initial_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """작업 처리 메인 메서드"""
        logger.info(f"[ReActAgent] 작업 시작: {user_goal}")

        # 초기화
        self.memory = ReActMemory(max_steps=self.max_steps)
        self.memory.current_goal = user_goal
        self.memory.context = initial_context or {}

        try:
            # ReAct 루프 실행
            for step_num in range(self.max_steps):
                logger.info(f"[ReActAgent] 단계 {step_num + 1}/{self.max_steps} 시작")

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
                    logger.info("[ReActAgent] 목표 달성 감지")
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
            logger.error(f"[ReActAgent] 오류 발생: {str(e)}")
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

        # 간단한 추론 로직 (실제로는 LLM 사용)
        if step_num == 0:
            reasoning = f"사용자 목표: '{goal}'를 달성하기 위해 먼저 필요한 정보를 파악해야 합니다."
        else:
            reasoning = f"이전 단계의 결과를 바탕으로 '{goal}' 목표 달성을 위한 다음 단계를 계획합니다."

        # 사용 가능한 도구들 고려
        available_tools = [tool.name for tool in self.tools.values() if tool.can_handle(goal)]
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
            elif selected_tool.name == "analyze":
                result, metadata = await selected_tool.execute(data=goal, analysis_type="general")
            elif selected_tool.name == "generate":
                result, metadata = await selected_tool.execute(content_type="문서", requirements=goal)
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
        if "오류" in tool_result:
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
            if step["step_type"] == ReActStep.ACTION.value:
                response += f"{i}. {step['content']}\n"

        return response

# 테스트용 함수
async def test_react_agent():
    """ReAct 에이전트 테스트"""
    agent = ReActAgent(max_steps=5)

    test_goals = [
        "React 개발자 채용공고를 작성해주세요",
        "최신 AI 기술 트렌드를 검색해주세요",
        "지원자 데이터를 분석해주세요"
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
    asyncio.run(test_react_agent())
