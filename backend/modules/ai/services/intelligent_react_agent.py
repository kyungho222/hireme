"""
지능형 ReAct 에이전트
더 정교한 추론과 액션 선택을 통한 향상된 ReAct 패턴 구현
"""

import asyncio
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from modules.ai.services.react_agent_core import ReActMemory, ReActStep, ReActTool
from modules.ai.services.react_tools_integration import (
    AIAnalysisTool,
    ApplicantTool,
    JobPostingTool,
    SearchTool,
)

logger = logging.getLogger(__name__)

@dataclass
class ReasoningContext:
    """추론 컨텍스트"""
    goal: str
    current_step: int
    previous_results: List[Dict[str, Any]]
    available_tools: List[str]
    user_intent: str = ""
    confidence: float = 0.0
    reasoning: str = ""

@dataclass
class ActionPlan:
    """액션 계획"""
    tool_name: str
    action: str
    parameters: Dict[str, Any]
    reasoning: str
    expected_outcome: str
    confidence: float
    metadata: Dict[str, Any] = field(default_factory=dict)

class IntelligentReActAgent:
    """지능형 ReAct 에이전트"""

    def __init__(self, max_steps: int = 8):
        self.max_steps = max_steps
        self.memory = ReActMemory(max_steps=max_steps)

        # 도구들 초기화
        self.tools = {
            "job_posting": JobPostingTool(),
            "applicant": ApplicantTool(),
            "search": SearchTool(),
            "ai_analysis": AIAnalysisTool()
        }

        # 도구별 우선순위 (경험 기반)
        self.tool_priorities = {
            "job_posting": 0.9,
            "applicant": 0.8,
            "search": 0.7,
            "ai_analysis": 0.6
        }

    async def process_task(self, user_goal: str, initial_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """지능형 작업 처리"""
        logger.info(f"[IntelligentReActAgent] 작업 시작: {user_goal}")

        # 초기화
        self.memory = ReActMemory(max_steps=self.max_steps)
        self.memory.current_goal = user_goal
        self.memory.context = initial_context or {}

        try:
            # 지능형 ReAct 루프 실행
            for step_num in range(self.max_steps):
                logger.info(f"[IntelligentReActAgent] 단계 {step_num + 1}/{self.max_steps} 시작")

                # 1. 지능형 추론 (Enhanced Reasoning)
                reasoning_context = await self._intelligent_reason(step_num)
                self.memory.add_step(ReActStep.REASONING, reasoning_context.reasoning)

                # 2. 액션 계획 수립 (Action Planning)
                action_plan = await self._plan_action(reasoning_context)
                self.memory.add_step(ReActStep.ACTION, action_plan.reasoning, {
                    "tool": action_plan.tool_name,
                    "action": action_plan.action,
                    "parameters": action_plan.parameters,
                    "confidence": action_plan.confidence
                })

                # 3. 액션 실행 (Action Execution)
                action_result = await self._execute_planned_action(action_plan)
                self.memory.add_step(ReActStep.ACTION, action_result["action"], action_result["metadata"])

                # 4. 지능형 관찰 (Intelligent Observation)
                observation = await self._intelligent_observe(action_result, action_plan)
                self.memory.add_step(ReActStep.OBSERVATION, observation["content"], observation["metadata"])

                # 목표 달성 확인
                if self.memory.is_goal_achieved():
                    logger.info("[IntelligentReActAgent] 목표 달성 감지")
                    break

                # 조기 종료 조건 확인
                if await self._should_terminate_early(observation):
                    logger.info("[IntelligentReActAgent] 조기 종료 조건 만족")
                    break

            # 최종 응답 생성
            final_response = await self._generate_intelligent_response()
            self.memory.add_step(ReActStep.FINAL, final_response)

            return {
                "success": True,
                "response": final_response,
                "steps": self.memory.steps,
                "goal_achieved": self.memory.is_goal_achieved(),
                "total_steps": len(self.memory.steps),
                "intelligence_metrics": await self._calculate_intelligence_metrics()
            }

        except Exception as e:
            logger.error(f"[IntelligentReActAgent] 오류 발생: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "steps": self.memory.steps,
                "partial_response": self.memory.get_recent_context()
            }

    async def _intelligent_reason(self, step_num: int) -> ReasoningContext:
        """지능형 추론"""
        goal = self.memory.current_goal
        previous_results = [step for step in self.memory.steps if step["step_type"] == ReActStep.OBSERVATION.value]

        # 사용 가능한 도구들
        available_tools = [tool.name for tool in self.tools.values() if tool.can_handle(goal)]

        # 의도 분석
        user_intent = await self._analyze_user_intent(goal)

        # 신뢰도 계산
        confidence = await self._calculate_confidence(goal, available_tools, previous_results)

        # 추론 생성
        if step_num == 0:
            reasoning = f"사용자 목표 분석: '{goal}' → 의도: {user_intent}\n"
            reasoning += f"사용 가능한 도구: {', '.join(available_tools)}\n"
            reasoning += f"신뢰도: {confidence:.2f}\n"
            reasoning += f"다음 단계: {available_tools[0] if available_tools else 'search'} 도구로 시작"
        else:
            last_result = previous_results[-1] if previous_results else None
            if last_result and "오류" in last_result.get("content", ""):
                reasoning = f"이전 단계에서 오류 발생. 대안 전략 수립:\n"
                reasoning += f"1. 다른 도구 시도: {available_tools[1] if len(available_tools) > 1 else 'search'}\n"
                reasoning += f"2. 매개변수 조정\n"
                reasoning += f"3. 단계별 접근"
            else:
                reasoning = f"이전 결과 분석 완료. 다음 단계 계획:\n"
                reasoning += f"목표 달성 진행률: {len(previous_results)}/{self.max_steps}\n"
                reasoning += f"추천 도구: {available_tools[0] if available_tools else 'search'}"

        return ReasoningContext(
            goal=goal,
            current_step=step_num,
            previous_results=previous_results,
            available_tools=available_tools,
            user_intent=user_intent,
            confidence=confidence,
            reasoning=reasoning
        )

    async def _plan_action(self, context: ReasoningContext) -> ActionPlan:
        """액션 계획 수립"""
        # 최적 도구 선택
        best_tool = await self._select_best_tool(context)

        # 액션 결정
        action, parameters = await self._determine_action(best_tool, context)

        # 예상 결과
        expected_outcome = await self._predict_outcome(best_tool, action, parameters)

        # 신뢰도 계산
        confidence = await self._calculate_action_confidence(best_tool, action, context)

        reasoning = f"액션 계획: {best_tool} 도구로 {action} 수행\n"
        reasoning += f"매개변수: {parameters}\n"
        reasoning += f"예상 결과: {expected_outcome}\n"
        reasoning += f"신뢰도: {confidence:.2f}"

        return ActionPlan(
            tool_name=best_tool,
            action=action,
            parameters=parameters,
            reasoning=reasoning,
            expected_outcome=expected_outcome,
            confidence=confidence
        )

    async def _execute_planned_action(self, plan: ActionPlan) -> Dict[str, Any]:
        """계획된 액션 실행"""
        try:
            tool = self.tools[plan.tool_name]

            # 도구별 매개변수 조정
            if plan.tool_name == "job_posting":
                result, metadata = await tool.execute(action=plan.action, **plan.parameters)
            elif plan.tool_name == "applicant":
                result, metadata = await tool.execute(action=plan.action, **plan.parameters)
            elif plan.tool_name == "search":
                result, metadata = await tool.execute(query=plan.parameters.get("query", ""), **plan.parameters)
            elif plan.tool_name == "ai_analysis":
                result, metadata = await tool.execute(analysis_type=plan.parameters.get("analysis_type", "general"), **plan.parameters)
            else:
                result, metadata = await tool.execute(**plan.parameters)

            return {
                "action": f"{plan.tool_name} 도구로 {plan.action} 실행 완료",
                "tool_result": result,
                "metadata": {
                    **metadata,
                    "planned": True,
                    "confidence": plan.confidence,
                    "expected_outcome": plan.expected_outcome
                }
            }

        except Exception as e:
            return {
                "action": f"{plan.tool_name} 도구 실행 중 오류 발생",
                "tool_result": f"오류: {str(e)}",
                "metadata": {
                    "error": str(e),
                    "planned": True,
                    "confidence": 0.0
                }
            }

    async def _intelligent_observe(self, action_result: Dict[str, Any], plan: ActionPlan) -> Dict[str, Any]:
        """지능형 관찰"""
        tool_result = action_result.get("tool_result", "")
        metadata = action_result.get("metadata", {})

        # 결과 분석
        success_indicators = ["성공", "완료", "생성", "조회", "찾았습니다", "분석을 완료했습니다"]
        error_indicators = ["오류", "실패", "문제", "알 수 없는"]

        is_success = any(indicator in tool_result for indicator in success_indicators)
        has_error = any(indicator in tool_result for indicator in error_indicators)

        # 예상 결과와 실제 결과 비교
        expected = plan.expected_outcome
        actual = tool_result

        if is_success:
            observation = f"✅ 액션 성공: {tool_result}"
            analysis = "목표 달성에 한 걸음 더 가까워졌습니다."
        elif has_error:
            observation = f"❌ 액션 실패: {tool_result}"
            analysis = "대안 전략이 필요합니다."
        else:
            observation = f"ℹ️ 액션 완료: {tool_result}"
            analysis = "결과를 분석하여 다음 단계를 결정합니다."

        # 학습 정보 추가
        learning = {
            "tool_performance": {
                "tool": plan.tool_name,
                "action": plan.action,
                "success": is_success,
                "confidence": plan.confidence
            },
            "pattern_recognition": {
                "similar_goals": await self._find_similar_goals(),
                "successful_patterns": await self._identify_successful_patterns()
            }
        }

        return {
            "content": f"{observation}\n분석: {analysis}",
            "metadata": {
                "analysis": analysis,
                "success": is_success,
                "error": has_error,
                "learning": learning,
                "next_action_needed": not self.memory.is_goal_achieved(),
                **metadata
            }
        }

    async def _analyze_user_intent(self, goal: str) -> str:
        """사용자 의도 분석"""
        goal_lower = goal.lower()

        if any(keyword in goal_lower for keyword in ["채용공고", "채용", "구인", "모집"]):
            return "채용공고_관리"
        elif any(keyword in goal_lower for keyword in ["지원자", "지원자 관리", "지원자 조회"]):
            return "지원자_관리"
        elif any(keyword in goal_lower for keyword in ["검색", "찾아", "알아봐"]):
            return "정보_검색"
        elif any(keyword in goal_lower for keyword in ["분석", "평가", "검토"]):
            return "데이터_분석"
        else:
            return "일반_요청"

    async def _select_best_tool(self, context: ReasoningContext) -> str:
        """최적 도구 선택"""
        available_tools = context.available_tools

        if not available_tools:
            return "search"  # 기본 도구

        # 의도 기반 도구 선택
        if context.user_intent == "채용공고_관리":
            return "job_posting" if "job_posting" in available_tools else available_tools[0]
        elif context.user_intent == "지원자_관리":
            return "applicant" if "applicant" in available_tools else available_tools[0]
        elif context.user_intent == "정보_검색":
            return "search" if "search" in available_tools else available_tools[0]
        elif context.user_intent == "데이터_분석":
            return "ai_analysis" if "ai_analysis" in available_tools else available_tools[0]
        else:
            # 우선순위 기반 선택
            best_tool = max(available_tools, key=lambda t: self.tool_priorities.get(t, 0.5))
            return best_tool

    async def _determine_action(self, tool_name: str, context: ReasoningContext) -> Tuple[str, Dict[str, Any]]:
        """액션 및 매개변수 결정"""
        if tool_name == "job_posting":
            if "작성" in context.goal or "생성" in context.goal:
                return "create", {"title": context.goal, "position": "개발자"}
            elif "조회" in context.goal or "목록" in context.goal:
                return "list", {}
            else:
                return "create", {"title": context.goal}

        elif tool_name == "applicant":
            if "목록" in context.goal or "조회" in context.goal:
                return "list", {}
            elif "통계" in context.goal:
                return "get_stats", {}
            else:
                return "list", {}

        elif tool_name == "search":
            return "search", {"query": context.goal}

        elif tool_name == "ai_analysis":
            return "analyze", {"data": context.goal, "analysis_type": "general"}

        else:
            return "execute", {"query": context.goal}

    async def _predict_outcome(self, tool_name: str, action: str, parameters: Dict[str, Any]) -> str:
        """예상 결과 예측"""
        predictions = {
            ("job_posting", "create"): "채용공고가 성공적으로 생성될 것입니다",
            ("job_posting", "list"): "채용공고 목록을 조회할 것입니다",
            ("applicant", "list"): "지원자 목록을 조회할 것입니다",
            ("applicant", "get_stats"): "지원자 통계를 분석할 것입니다",
            ("search", "search"): "관련 정보를 검색할 것입니다",
            ("ai_analysis", "analyze"): "데이터 분석을 수행할 것입니다"
        }

        return predictions.get((tool_name, action), "작업을 수행할 것입니다")

    async def _calculate_confidence(self, goal: str, available_tools: List[str], previous_results: List[Dict[str, Any]]) -> float:
        """신뢰도 계산"""
        base_confidence = 0.5

        # 도구 가용성에 따른 신뢰도 조정
        if available_tools:
            base_confidence += 0.2

        # 이전 성공 경험에 따른 신뢰도 조정
        if previous_results:
            success_count = sum(1 for result in previous_results if "성공" in result.get("content", ""))
            base_confidence += min(success_count * 0.1, 0.3)

        return min(base_confidence, 1.0)

    async def _calculate_action_confidence(self, tool_name: str, action: str, context: ReasoningContext) -> float:
        """액션 신뢰도 계산"""
        base_confidence = self.tool_priorities.get(tool_name, 0.5)

        # 의도와 도구의 일치도
        if context.user_intent == "채용공고_관리" and tool_name == "job_posting":
            base_confidence += 0.2
        elif context.user_intent == "지원자_관리" and tool_name == "applicant":
            base_confidence += 0.2
        elif context.user_intent == "정보_검색" and tool_name == "search":
            base_confidence += 0.2
        elif context.user_intent == "데이터_분석" and tool_name == "ai_analysis":
            base_confidence += 0.2

        return min(base_confidence, 1.0)

    async def _should_terminate_early(self, observation: Dict[str, Any]) -> bool:
        """조기 종료 조건 확인"""
        # 연속 실패 시 조기 종료
        recent_observations = [step for step in self.memory.steps[-3:] if step["step_type"] == ReActStep.OBSERVATION.value]
        if len(recent_observations) >= 3:
            error_count = sum(1 for obs in recent_observations if "실패" in obs.get("content", ""))
            if error_count >= 3:
                return True

        return False

    async def _generate_intelligent_response(self) -> str:
        """지능형 최종 응답 생성"""
        if self.memory.is_goal_achieved():
            response = f"✅ '{self.memory.current_goal}' 목표를 성공적으로 달성했습니다!\n\n"
        else:
            response = f"⚠️ '{self.memory.current_goal}' 목표 달성을 위해 {len(self.memory.steps)}단계를 수행했습니다.\n\n"

        # 성능 분석
        success_steps = [step for step in self.memory.steps if step["step_type"] == ReActStep.OBSERVATION.value and "성공" in step.get("content", "")]
        response += f"📊 성능 분석:\n"
        response += f"- 성공 단계: {len(success_steps)}개\n"
        response += f"- 총 단계: {len(self.memory.steps)}개\n"
        response += f"- 성공률: {len(success_steps)/max(len(self.memory.steps), 1)*100:.1f}%\n\n"

        # 주요 단계 요약
        response += "📋 수행된 주요 단계:\n"
        for i, step in enumerate(self.memory.steps, 1):
            if step["step_type"] == ReActStep.ACTION.value:
                response += f"{i}. {step['content']}\n"

        return response

    async def _calculate_intelligence_metrics(self) -> Dict[str, Any]:
        """지능 지표 계산"""
        steps = self.memory.steps
        reasoning_steps = [s for s in steps if s["step_type"] == ReActStep.REASONING.value]
        action_steps = [s for s in steps if s["step_type"] == ReActStep.ACTION.value]
        observation_steps = [s for s in steps if s["step_type"] == ReActStep.OBSERVATION.value]

        success_count = sum(1 for s in observation_steps if "성공" in s.get("content", ""))

        return {
            "total_steps": len(steps),
            "reasoning_steps": len(reasoning_steps),
            "action_steps": len(action_steps),
            "observation_steps": len(observation_steps),
            "success_rate": success_count / max(len(observation_steps), 1),
            "goal_achieved": self.memory.is_goal_achieved(),
            "efficiency": len(steps) / self.max_steps
        }

    async def _find_similar_goals(self) -> List[str]:
        """유사한 목표 찾기"""
        # 실제로는 과거 경험 데이터베이스에서 검색
        return ["React 개발자 채용공고 작성", "Python 개발자 채용공고 작성"]

    async def _identify_successful_patterns(self) -> List[str]:
        """성공 패턴 식별"""
        # 실제로는 성공한 작업 패턴을 분석
        return ["채용공고 생성 → 검토 → 수정", "지원자 조회 → 분석 → 상태 변경"]

# 테스트용 함수
async def test_intelligent_react_agent():
    """지능형 ReAct 에이전트 테스트"""
    agent = IntelligentReActAgent(max_steps=6)

    test_goals = [
        "React 개발자 채용공고를 작성해주세요",
        "지원자 목록을 조회해주세요",
        "최신 AI 기술 트렌드를 검색해주세요"
    ]

    for goal in test_goals:
        print(f"\n{'='*60}")
        print(f"지능형 테스트 목표: {goal}")
        print(f"{'='*60}")

        result = await agent.process_task(goal)

        print(f"성공: {result['success']}")
        print(f"응답: {result['response']}")
        print(f"총 단계: {result.get('total_steps', 0)}")

        if result.get('intelligence_metrics'):
            metrics = result['intelligence_metrics']
            print(f"지능 지표:")
            print(f"  - 성공률: {metrics['success_rate']*100:.1f}%")
            print(f"  - 효율성: {metrics['efficiency']*100:.1f}%")
            print(f"  - 목표 달성: {metrics['goal_achieved']}")

        if result.get('steps'):
            print("\n단계별 상세:")
            for step in result['steps']:
                print(f"  [{step['step_type']}] {step['content'][:100]}...")

if __name__ == "__main__":
    # 테스트 실행
    asyncio.run(test_intelligent_react_agent())
