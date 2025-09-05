"""
ReAct 에이전트 진행상황 시각화 로거
단계별 진행상황을 실시간으로 확인할 수 있는 로깅 시스템
"""

import asyncio
import json
import logging
import time
from dataclasses import asdict, dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

class LogLevel(Enum):
    """로그 레벨"""
    INFO = "INFO"
    SUCCESS = "SUCCESS"
    WARNING = "WARNING"
    ERROR = "ERROR"
    DEBUG = "DEBUG"

@dataclass
class LogEntry:
    """로그 엔트리"""
    timestamp: str
    level: str
    step: int
    phase: str  # "reasoning", "action", "observation", "final"
    message: str
    details: Dict[str, Any] = None
    duration: float = 0.0

class ReActAgentLogger:
    """ReAct 에이전트 진행상황 로거"""

    def __init__(self, task_id: str = None):
        self.task_id = task_id or f"task_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.logs: List[LogEntry] = []
        self.current_step = 0
        self.start_time = time.time()
        self.phase_start_time = time.time()

        # 로그 포맷터 설정
        self.setup_logger()

    def setup_logger(self):
        """로거 설정"""
        # 기존 핸들러 제거
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)

        # 포맷터 설정
        formatter = logging.Formatter(
            '%(asctime)s | %(levelname)s | %(message)s',
            datefmt='%H:%M:%S'
        )

        # 콘솔 핸들러
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        logger.setLevel(logging.INFO)

    def log(self, level: LogLevel, phase: str, message: str, details: Dict[str, Any] = None):
        """로그 추가"""
        current_time = time.time()
        duration = current_time - self.phase_start_time

        entry = LogEntry(
            timestamp=datetime.now().strftime('%H:%M:%S.%f')[:-3],
            level=level.value,
            step=self.current_step,
            phase=phase,
            message=message,
            details=details or {},
            duration=duration
        )

        self.logs.append(entry)

        # 콘솔에 출력
        self._print_log_entry(entry)

        # 다음 단계를 위한 시간 초기화
        self.phase_start_time = current_time

    def _print_log_entry(self, entry: LogEntry):
        """로그 엔트리를 콘솔에 출력"""
        # 단계별 색상 및 아이콘
        phase_icons = {
            "reasoning": "🧠",
            "action": "⚡",
            "observation": "👁️",
            "final": "🏁"
        }

        level_colors = {
            "INFO": "\033[94m",      # 파란색
            "SUCCESS": "\033[92m",   # 초록색
            "WARNING": "\033[93m",   # 노란색
            "ERROR": "\033[91m",     # 빨간색
            "DEBUG": "\033[95m"      # 보라색
        }

        reset_color = "\033[0m"

        icon = phase_icons.get(entry.phase, "📝")
        color = level_colors.get(entry.level, "")

        # 메인 로그 라인
        main_line = f"{color}[{entry.timestamp}] {icon} {entry.phase.upper()} (Step {entry.step}) | {entry.message}{reset_color}"
        print(main_line)

        # 상세 정보 출력
        if entry.details:
            for key, value in entry.details.items():
                if isinstance(value, dict):
                    print(f"    └─ {key}: {json.dumps(value, ensure_ascii=False, indent=2)}")
                else:
                    print(f"    └─ {key}: {value}")

        # 지속 시간 출력
        if entry.duration > 0:
            print(f"    ⏱️  Duration: {entry.duration:.3f}s")

        print()  # 빈 줄 추가

    def start_step(self, step_num: int):
        """새 단계 시작"""
        self.current_step = step_num
        self.phase_start_time = time.time()
        self.log(LogLevel.INFO, "reasoning", f"단계 {step_num} 시작", {
            "step_number": step_num,
            "total_elapsed": time.time() - self.start_time
        })

    def log_reasoning(self, message: str, details: Dict[str, Any] = None):
        """추론 단계 로그"""
        self.log(LogLevel.INFO, "reasoning", message, details)

    def log_action(self, message: str, details: Dict[str, Any] = None):
        """액션 단계 로그"""
        self.log(LogLevel.INFO, "action", message, details)

    def log_observation(self, message: str, details: Dict[str, Any] = None):
        """관찰 단계 로그"""
        level = LogLevel.SUCCESS if "성공" in message else LogLevel.INFO
        self.log(level, "observation", message, details)

    def log_error(self, message: str, details: Dict[str, Any] = None):
        """오류 로그"""
        self.log(LogLevel.ERROR, "action", message, details)

    def log_final(self, message: str, details: Dict[str, Any] = None):
        """최종 결과 로그"""
        level = LogLevel.SUCCESS if "성공" in message else LogLevel.WARNING
        self.log(level, "final", message, details)

    def get_summary(self) -> Dict[str, Any]:
        """로그 요약 정보"""
        total_duration = time.time() - self.start_time

        # 단계별 통계
        step_counts = {}
        phase_counts = {}
        level_counts = {}

        for log in self.logs:
            step_counts[log.step] = step_counts.get(log.step, 0) + 1
            phase_counts[log.phase] = phase_counts.get(log.phase, 0) + 1
            level_counts[log.level] = level_counts.get(log.level, 0) + 1

        return {
            "task_id": self.task_id,
            "total_duration": total_duration,
            "total_logs": len(self.logs),
            "total_steps": max(step_counts.keys()) if step_counts else 0,
            "step_counts": step_counts,
            "phase_counts": phase_counts,
            "level_counts": level_counts,
            "success_rate": level_counts.get("SUCCESS", 0) / max(len(self.logs), 1) * 100
        }

    def export_logs(self, format: str = "json") -> str:
        """로그 내보내기"""
        if format == "json":
            return json.dumps([asdict(log) for log in self.logs], ensure_ascii=False, indent=2)
        elif format == "text":
            lines = []
            for log in self.logs:
                lines.append(f"[{log.timestamp}] {log.level} | Step {log.step} | {log.phase} | {log.message}")
                if log.details:
                    for key, value in log.details.items():
                        lines.append(f"  {key}: {value}")
            return "\n".join(lines)
        else:
            return str(self.logs)

class VisualReActAgent:
    """시각적 진행상황을 보여주는 ReAct 에이전트"""

    def __init__(self, max_steps: int = 8):
        from modules.ai.services.advanced_memory_react_agent import AdvancedReActAgent

        self.agent = AdvancedReActAgent(max_steps=max_steps)
        self.logger = ReActAgentLogger()
        self.max_steps = max_steps

    async def process_task_with_visual_logging(self, user_goal: str, initial_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """시각적 로깅과 함께 작업 처리"""

        # 시작 메시지
        print("🚀" + "="*80)
        print(f"🤖 ReAct 에이전트 작업 시작")
        print(f"📋 목표: {user_goal}")
        print(f"⏰ 시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*82)
        print()

        self.logger.log(LogLevel.INFO, "reasoning", f"작업 시작: {user_goal}", {
            "goal": user_goal,
            "max_steps": self.max_steps,
            "context": initial_context
        })

        try:
            # 초기화
            self.agent.memory = self.agent.memory.__class__(max_steps=self.max_steps)
            self.agent.memory.current_goal = user_goal
            self.agent.memory.context = initial_context or {}

            # 작업 컨텍스트 생성
            from modules.ai.services.advanced_memory_react_agent import TaskContext
            task_id = f"task_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            self.agent.current_task = TaskContext(
                task_id=task_id,
                goal=user_goal,
                start_time=datetime.now(),
                current_step=0,
                status="active",
                progress=0.0
            )

            # ReAct 루프 실행
            for step_num in range(self.max_steps):
                self.logger.start_step(step_num + 1)

                # 1. 추론 단계
                reasoning_context = await self._log_reasoning_step(step_num)
                from modules.ai.services.react_agent_core import ReActStep
                self.agent.memory.add_step(ReActStep.REASONING, reasoning_context.reasoning)

                # 2. 액션 계획 단계
                action_plan = await self._log_action_planning_step(reasoning_context)
                self.agent.memory.add_step(ReActStep.ACTION, action_plan.reasoning, {
                    "tool": action_plan.tool_name,
                    "action": action_plan.action,
                    "parameters": action_plan.parameters,
                    "confidence": action_plan.confidence
                })

                # 3. 액션 실행 단계
                action_result = await self._log_action_execution_step(action_plan)
                self.agent.memory.add_step(ReActStep.ACTION, action_result["action"], action_result["metadata"])

                # 4. 관찰 단계
                observation = await self._log_observation_step(action_result, action_plan)
                self.agent.memory.add_step(ReActStep.OBSERVATION, observation["content"], observation["metadata"])

                # 목표 달성 확인
                if self.agent.memory.is_goal_achieved():
                    self.logger.log(LogLevel.SUCCESS, "observation", "🎯 목표 달성 감지!")
                    self.agent.current_task.status = "completed"
                    self.agent.current_task.progress = 1.0
                    break

                # 조기 종료 조건 확인
                if await self.agent._should_terminate_early(observation):
                    self.logger.log(LogLevel.WARNING, "observation", "⚠️ 조기 종료 조건 만족")
                    self.agent.current_task.status = "failed"
                    break

            # 최종 결과
            final_response = await self._log_final_result()
            self.agent.memory.add_step(ReActStep.FINAL, final_response)

            # 요약 정보 출력
            self._print_summary()

            return {
                "success": True,
                "response": final_response,
                "steps": self.agent.memory.steps,
                "goal_achieved": self.agent.memory.is_goal_achieved(),
                "total_steps": len(self.agent.memory.steps),
                "logs": [asdict(log) for log in self.logger.logs],
                "summary": self.logger.get_summary()
            }

        except Exception as e:
            self.logger.log_error(f"❌ 작업 처리 중 오류 발생: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "logs": [asdict(log) for log in self.logger.logs],
                "summary": self.logger.get_summary()
            }

    async def _log_reasoning_step(self, step_num: int):
        """추론 단계 로깅"""
        goal = self.agent.memory.current_goal
        previous_results = [step for step in self.agent.memory.steps if step["step_type"] == "observation"]

        # 관련 메모리 검색
        relevant_memories = self.agent.memory_manager.retrieve_memory(goal, limit=3)

        # 사용 가능한 도구들
        available_tools = [tool.name for tool in self.agent.tools.values() if tool.can_handle(goal)]

        # 의도 분석
        user_intent = await self.agent._analyze_user_intent(goal)

        # 신뢰도 계산
        confidence = await self.agent._calculate_confidence(goal, available_tools, previous_results)
        if relevant_memories:
            confidence += 0.1

        # 추론 생성
        if step_num == 0:
            reasoning = f"사용자 목표 분석: '{goal}' → 의도: {user_intent}"
            details = {
                "user_intent": user_intent,
                "available_tools": available_tools,
                "confidence": f"{confidence:.2f}",
                "relevant_memories": len(relevant_memories)
            }
        else:
            last_result = previous_results[-1] if previous_results else None
            if last_result and "오류" in last_result.get("content", ""):
                reasoning = "이전 단계에서 오류 발생. 대안 전략 수립"
                details = {
                    "error_detected": True,
                    "alternative_strategy": "다른 도구 시도 또는 매개변수 조정"
                }
            else:
                reasoning = "이전 결과 분석 완료. 다음 단계 계획"
                details = {
                    "progress": f"{len(previous_results)}/{self.max_steps}",
                    "recommended_tool": available_tools[0] if available_tools else "search"
                }

        self.logger.log_reasoning(reasoning, details)

        from modules.ai.services.intelligent_react_agent import ReasoningContext
        return ReasoningContext(
            goal=goal,
            current_step=step_num,
            previous_results=previous_results,
            available_tools=available_tools,
            user_intent=user_intent,
            confidence=confidence,
            reasoning=reasoning
        )

    async def _log_action_planning_step(self, context):
        """액션 계획 단계 로깅"""
        # 최적 도구 선택
        best_tool = await self.agent._select_best_tool(context)

        # 액션 결정
        action, parameters = await self.agent._determine_action(best_tool, context)

        # 예상 결과
        expected_outcome = await self.agent._predict_outcome(best_tool, action, parameters)

        # 신뢰도 계산
        confidence = await self.agent._calculate_action_confidence(best_tool, action, context)

        reasoning = f"액션 계획: {best_tool} 도구로 {action} 수행"
        details = {
            "selected_tool": best_tool,
            "action": action,
            "parameters": parameters,
            "expected_outcome": expected_outcome,
            "confidence": f"{confidence:.2f}"
        }

        self.logger.log_action(reasoning, details)

        from modules.ai.services.intelligent_react_agent import ActionPlan
        return ActionPlan(
            tool_name=best_tool,
            action=action,
            parameters=parameters,
            reasoning=reasoning,
            expected_outcome=expected_outcome,
            confidence=confidence
        )

    async def _log_action_execution_step(self, plan):
        """액션 실행 단계 로깅"""
        try:
            tool = self.agent.tools[plan.tool_name]

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

            action_message = f"✅ {plan.tool_name} 도구로 {plan.action} 실행 완료"
            details = {
                "tool": plan.tool_name,
                "action": plan.action,
                "result_preview": result[:100] + "..." if len(result) > 100 else result,
                "metadata": metadata
            }

            self.logger.log_action(action_message, details)

            return {
                "action": action_message,
                "tool_result": result,
                "metadata": metadata
            }

        except Exception as e:
            error_message = f"❌ {plan.tool_name} 도구 실행 중 오류 발생"
            details = {
                "tool": plan.tool_name,
                "action": plan.action,
                "error": str(e)
            }

            self.logger.log_error(error_message, details)

            return {
                "action": error_message,
                "tool_result": f"오류: {str(e)}",
                "metadata": {"error": str(e)}
            }

    async def _log_observation_step(self, action_result, plan):
        """관찰 단계 로깅"""
        tool_result = action_result.get("tool_result", "")
        metadata = action_result.get("metadata", {})

        # 결과 분석
        success_indicators = ["성공", "완료", "생성", "조회", "찾았습니다", "분석을 완료했습니다"]
        error_indicators = ["오류", "실패", "문제", "알 수 없는"]

        is_success = any(indicator in tool_result for indicator in success_indicators)
        has_error = any(indicator in tool_result for indicator in error_indicators)

        if is_success:
            observation_message = f"✅ 액션 성공: {tool_result[:100]}..."
            analysis = "목표 달성에 한 걸음 더 가까워졌습니다"
        elif has_error:
            observation_message = f"❌ 액션 실패: {tool_result[:100]}..."
            analysis = "대안 전략이 필요합니다"
        else:
            observation_message = f"ℹ️ 액션 완료: {tool_result[:100]}..."
            analysis = "결과를 분석하여 다음 단계를 결정합니다"

        details = {
            "success": is_success,
            "error": has_error,
            "analysis": analysis,
            "result_length": len(tool_result),
            "metadata_keys": list(metadata.keys()) if metadata else []
        }

        self.logger.log_observation(observation_message, details)

        return {
            "content": f"{observation_message}\n분석: {analysis}",
            "metadata": {
                "analysis": analysis,
                "success": is_success,
                "error": has_error,
                **metadata
            }
        }

    async def _log_final_result(self):
        """최종 결과 로깅"""
        if self.agent.memory.is_goal_achieved():
            response = f"🎉 '{self.agent.memory.current_goal}' 목표를 성공적으로 달성했습니다!"
            level = LogLevel.SUCCESS
        else:
            response = f"⚠️ '{self.agent.memory.current_goal}' 목표 달성을 위해 {len(self.agent.memory.steps)}단계를 수행했습니다"
            level = LogLevel.WARNING

        # 성능 분석
        success_steps = [step for step in self.agent.memory.steps if step["step_type"] == "observation" and "성공" in step.get("content", "")]

        details = {
            "goal_achieved": self.agent.memory.is_goal_achieved(),
            "total_steps": len(self.agent.memory.steps),
            "success_steps": len(success_steps),
            "success_rate": f"{len(success_steps)/max(len(self.agent.memory.steps), 1)*100:.1f}%"
        }

        self.logger.log_final(response, details)

        return response

    def _print_summary(self):
        """요약 정보 출력"""
        summary = self.logger.get_summary()

        print("📊" + "="*80)
        print("📈 작업 요약")
        print("="*82)
        print(f"🆔 작업 ID: {summary['task_id']}")
        print(f"⏱️  총 소요 시간: {summary['total_duration']:.2f}초")
        print(f"📝 총 로그 수: {summary['total_logs']}개")
        print(f"🔄 총 단계 수: {summary['total_steps']}개")
        print(f"✅ 성공률: {summary['success_rate']:.1f}%")
        print()
        print("📋 단계별 통계:")
        for step, count in summary['step_counts'].items():
            print(f"  Step {step}: {count}개 로그")
        print()
        print("🎯 단계 유형별 통계:")
        for phase, count in summary['phase_counts'].items():
            print(f"  {phase}: {count}개")
        print()
        print("📊 로그 레벨별 통계:")
        for level, count in summary['level_counts'].items():
            print(f"  {level}: {count}개")
        print("="*82)

# 테스트용 함수
async def test_visual_react_agent():
    """시각적 ReAct 에이전트 테스트"""
    agent = VisualReActAgent(max_steps=6)

    test_goals = [
        "React 개발자 채용공고를 작성해주세요",
        "지원자 목록을 조회해주세요"
    ]

    for goal in test_goals:
        print(f"\n{'🎯' + '='*80}")
        print(f"테스트 목표: {goal}")
        print(f"{'='*82}")

        result = await agent.process_task_with_visual_logging(goal)

        print(f"\n📋 최종 결과:")
        print(f"성공: {result['success']}")
        print(f"목표 달성: {result.get('goal_achieved', False)}")
        print(f"총 단계: {result.get('total_steps', 0)}")

if __name__ == "__main__":
    # 테스트 실행
    asyncio.run(test_visual_react_agent())
