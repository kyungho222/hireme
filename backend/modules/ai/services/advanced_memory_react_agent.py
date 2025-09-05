"""
고급 메모리 관리 ReAct 에이전트
장기 기억, 단기 기억, 작업 기억을 구분하여 관리하는 향상된 ReAct 에이전트
"""

import asyncio
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

from modules.ai.services.intelligent_react_agent import (
    ActionPlan,
    IntelligentReActAgent,
    ReasoningContext,
)
from modules.ai.services.react_agent_core import ReActMemory, ReActStep, ReActTool

logger = logging.getLogger(__name__)

class MemoryType(Enum):
    """메모리 타입"""
    WORKING = "working"      # 작업 기억 (현재 작업)
    SHORT_TERM = "short_term"  # 단기 기억 (최근 대화)
    LONG_TERM = "long_term"    # 장기 기억 (학습된 지식)
    EPISODIC = "episodic"      # 경험 기억 (과거 경험)

@dataclass
class MemoryItem:
    """메모리 아이템"""
    content: str
    memory_type: MemoryType
    importance: float  # 0.0 ~ 1.0
    timestamp: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)
    access_count: int = 0
    last_accessed: Optional[datetime] = None

@dataclass
class TaskContext:
    """작업 컨텍스트"""
    task_id: str
    goal: str
    start_time: datetime
    current_step: int
    status: str  # "active", "completed", "failed", "paused"
    progress: float  # 0.0 ~ 1.0
    sub_tasks: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)

class AdvancedMemoryManager:
    """고급 메모리 관리자"""

    def __init__(self, max_working_items: int = 10, max_short_term_items: int = 50):
        self.working_memory: List[MemoryItem] = []
        self.short_term_memory: List[MemoryItem] = []
        self.long_term_memory: Dict[str, MemoryItem] = {}
        self.episodic_memory: List[MemoryItem] = []

        self.max_working_items = max_working_items
        self.max_short_term_items = max_short_term_items

        # 메모리 압축 임계값
        self.compression_threshold = 0.8

    def add_memory(self, content: str, memory_type: MemoryType, importance: float = 0.5, metadata: Dict[str, Any] = None):
        """메모리 추가"""
        item = MemoryItem(
            content=content,
            memory_type=memory_type,
            importance=importance,
            timestamp=datetime.now(),
            metadata=metadata or {}
        )

        if memory_type == MemoryType.WORKING:
            self.working_memory.append(item)
            # 작업 기억 크기 제한
            if len(self.working_memory) > self.max_working_items:
                self._compress_working_memory()

        elif memory_type == MemoryType.SHORT_TERM:
            self.short_term_memory.append(item)
            # 단기 기억 크기 제한
            if len(self.short_term_memory) > self.max_short_term_items:
                self._compress_short_term_memory()

        elif memory_type == MemoryType.LONG_TERM:
            # 장기 기억은 키-값 형태로 저장
            key = self._generate_memory_key(content)
            self.long_term_memory[key] = item

        elif memory_type == MemoryType.EPISODIC:
            self.episodic_memory.append(item)

        logger.info(f"[MemoryManager] {memory_type.value} 메모리 추가: {content[:50]}...")

    def retrieve_memory(self, query: str, memory_type: Optional[MemoryType] = None, limit: int = 5) -> List[MemoryItem]:
        """메모리 검색"""
        results = []

        if memory_type is None or memory_type == MemoryType.WORKING:
            results.extend(self._search_memory(self.working_memory, query, limit))

        if memory_type is None or memory_type == MemoryType.SHORT_TERM:
            results.extend(self._search_memory(self.short_term_memory, query, limit))

        if memory_type is None or memory_type == MemoryType.LONG_TERM:
            results.extend(self._search_memory(list(self.long_term_memory.values()), query, limit))

        if memory_type is None or memory_type == MemoryType.EPISODIC:
            results.extend(self._search_memory(self.episodic_memory, query, limit))

        # 관련성 순으로 정렬
        results.sort(key=lambda x: x.importance, reverse=True)
        return results[:limit]

    def update_memory_access(self, item: MemoryItem):
        """메모리 접근 정보 업데이트"""
        item.access_count += 1
        item.last_accessed = datetime.now()

    def consolidate_memories(self):
        """메모리 통합 (단기 → 장기)"""
        # 중요도가 높은 단기 기억을 장기 기억으로 이동
        high_importance_items = [
            item for item in self.short_term_memory
            if item.importance > 0.7 and item.timestamp < datetime.now() - timedelta(hours=1)
        ]

        for item in high_importance_items:
            key = self._generate_memory_key(item.content)
            self.long_term_memory[key] = item
            self.short_term_memory.remove(item)
            logger.info(f"[MemoryManager] 메모리 통합: {item.content[:50]}... → 장기 기억")

    def _search_memory(self, memory_list: List[MemoryItem], query: str, limit: int) -> List[MemoryItem]:
        """메모리 검색 (간단한 키워드 매칭)"""
        query_lower = query.lower()
        results = []

        for item in memory_list:
            if query_lower in item.content.lower():
                results.append(item)
                self.update_memory_access(item)

        return results[:limit]

    def _generate_memory_key(self, content: str) -> str:
        """메모리 키 생성"""
        # 간단한 해시 기반 키 생성
        import hashlib
        return hashlib.md5(content.encode()).hexdigest()[:16]

    def _compress_working_memory(self):
        """작업 기억 압축"""
        # 중요도가 낮은 항목 제거
        self.working_memory.sort(key=lambda x: x.importance, reverse=True)
        self.working_memory = self.working_memory[:self.max_working_items // 2]
        logger.info(f"[MemoryManager] 작업 기억 압축 완료")

    def _compress_short_term_memory(self):
        """단기 기억 압축"""
        # 오래된 항목과 중요도가 낮은 항목 제거
        cutoff_time = datetime.now() - timedelta(hours=24)
        self.short_term_memory = [
            item for item in self.short_term_memory
            if item.timestamp > cutoff_time or item.importance > 0.6
        ]
        logger.info(f"[MemoryManager] 단기 기억 압축 완료")

    def get_memory_summary(self) -> Dict[str, Any]:
        """메모리 요약 정보"""
        return {
            "working_memory": len(self.working_memory),
            "short_term_memory": len(self.short_term_memory),
            "long_term_memory": len(self.long_term_memory),
            "episodic_memory": len(self.episodic_memory),
            "total_memories": (
                len(self.working_memory) +
                len(self.short_term_memory) +
                len(self.long_term_memory) +
                len(self.episodic_memory)
            )
        }

class AdvancedReActAgent(IntelligentReActAgent):
    """고급 메모리 관리 ReAct 에이전트"""

    def __init__(self, max_steps: int = 8):
        super().__init__(max_steps)

        # 고급 메모리 관리자 초기화
        self.memory_manager = AdvancedMemoryManager()

        # 작업 컨텍스트 관리
        self.current_task: Optional[TaskContext] = None
        self.task_history: List[TaskContext] = []

        # 학습된 패턴 저장
        self.learned_patterns: Dict[str, Dict[str, Any]] = {}

    async def process_task(self, user_goal: str, initial_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """고급 메모리 관리 작업 처리"""
        logger.info(f"[AdvancedReActAgent] 작업 시작: {user_goal}")

        # 작업 컨텍스트 생성
        task_id = f"task_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.current_task = TaskContext(
            task_id=task_id,
            goal=user_goal,
            start_time=datetime.now(),
            current_step=0,
            status="active",
            progress=0.0
        )

        # 관련 메모리 검색
        relevant_memories = self.memory_manager.retrieve_memory(user_goal, limit=3)
        if relevant_memories:
            logger.info(f"[AdvancedReActAgent] 관련 메모리 {len(relevant_memories)}개 발견")
            for memory in relevant_memories:
                logger.info(f"  - {memory.memory_type.value}: {memory.content[:50]}...")

        # 초기화
        self.memory = ReActMemory(max_steps=self.max_steps)
        self.memory.current_goal = user_goal
        self.memory.context = initial_context or {}

        # 작업 기억에 목표 저장
        self.memory_manager.add_memory(
            content=f"현재 작업: {user_goal}",
            memory_type=MemoryType.WORKING,
            importance=1.0,
            metadata={"task_id": task_id, "goal": user_goal}
        )

        try:
            # 고급 ReAct 루프 실행
            for step_num in range(self.max_steps):
                self.current_task.current_step = step_num
                self.current_task.progress = step_num / self.max_steps

                logger.info(f"[AdvancedReActAgent] 단계 {step_num + 1}/{self.max_steps} 시작")

                # 1. 메모리 기반 지능형 추론
                reasoning_context = await self._memory_enhanced_reason(step_num)
                self.memory.add_step(ReActStep.REASONING, reasoning_context.reasoning)

                # 2. 학습된 패턴 기반 액션 계획
                action_plan = await self._pattern_based_plan_action(reasoning_context)
                self.memory.add_step(ReActStep.ACTION, action_plan.reasoning, {
                    "tool": action_plan.tool_name,
                    "action": action_plan.action,
                    "parameters": action_plan.parameters,
                    "confidence": action_plan.confidence,
                    "pattern_used": action_plan.metadata.get("pattern_used", False)
                })

                # 3. 액션 실행
                action_result = await self._execute_planned_action(action_plan)
                self.memory.add_step(ReActStep.ACTION, action_result["action"], action_result["metadata"])

                # 4. 메모리 업데이트 및 관찰
                observation = await self._memory_enhanced_observe(action_result, action_plan)
                self.memory.add_step(ReActStep.OBSERVATION, observation["content"], observation["metadata"])

                # 목표 달성 확인
                if self.memory.is_goal_achieved():
                    logger.info("[AdvancedReActAgent] 목표 달성 감지")
                    self.current_task.status = "completed"
                    self.current_task.progress = 1.0
                    break

                # 조기 종료 조건 확인
                if await self._should_terminate_early(observation):
                    logger.info("[AdvancedReActAgent] 조기 종료 조건 만족")
                    self.current_task.status = "failed"
                    break

            # 작업 완료 처리
            if self.current_task.status == "active":
                self.current_task.status = "completed" if self.memory.is_goal_achieved() else "failed"

            self.task_history.append(self.current_task)

            # 메모리 통합
            self.memory_manager.consolidate_memories()

            # 최종 응답 생성
            final_response = await self._generate_advanced_response()
            self.memory.add_step(ReActStep.FINAL, final_response)

            return {
                "success": True,
                "response": final_response,
                "steps": self.memory.steps,
                "goal_achieved": self.memory.is_goal_achieved(),
                "total_steps": len(self.memory.steps),
                "intelligence_metrics": await self._calculate_intelligence_metrics(),
                "memory_metrics": self.memory_manager.get_memory_summary(),
                "task_context": {
                    "task_id": self.current_task.task_id,
                    "status": self.current_task.status,
                    "progress": self.current_task.progress,
                    "duration": (datetime.now() - self.current_task.start_time).total_seconds()
                }
            }

        except Exception as e:
            logger.error(f"[AdvancedReActAgent] 오류 발생: {str(e)}")
            if self.current_task:
                self.current_task.status = "failed"
                self.task_history.append(self.current_task)

            return {
                "success": False,
                "error": str(e),
                "steps": self.memory.steps,
                "partial_response": self.memory.get_recent_context(),
                "memory_metrics": self.memory_manager.get_memory_summary()
            }

    async def _memory_enhanced_reason(self, step_num: int) -> ReasoningContext:
        """메모리 기반 지능형 추론"""
        goal = self.memory.current_goal
        previous_results = [step for step in self.memory.steps if step["step_type"] == ReActStep.OBSERVATION.value]

        # 관련 메모리 검색
        relevant_memories = self.memory_manager.retrieve_memory(goal, limit=3)

        # 사용 가능한 도구들
        available_tools = [tool.name for tool in self.tools.values() if tool.can_handle(goal)]

        # 의도 분석
        user_intent = await self._analyze_user_intent(goal)

        # 신뢰도 계산 (메모리 정보 포함)
        confidence = await self._calculate_confidence(goal, available_tools, previous_results)
        if relevant_memories:
            confidence += 0.1  # 관련 메모리가 있으면 신뢰도 증가

        # 추론 생성 (메모리 정보 포함)
        if step_num == 0:
            reasoning = f"사용자 목표 분석: '{goal}' → 의도: {user_intent}\n"
            reasoning += f"사용 가능한 도구: {', '.join(available_tools)}\n"
            reasoning += f"신뢰도: {confidence:.2f}\n"

            if relevant_memories:
                reasoning += f"관련 메모리: {len(relevant_memories)}개 발견\n"
                for memory in relevant_memories:
                    reasoning += f"  - {memory.memory_type.value}: {memory.content[:50]}...\n"

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

    async def _pattern_based_plan_action(self, context: ReasoningContext) -> ActionPlan:
        """학습된 패턴 기반 액션 계획"""
        # 기존 계획 수립
        action_plan = await self._plan_action(context)

        # 학습된 패턴 확인
        pattern_key = f"{context.user_intent}_{action_plan.tool_name}_{action_plan.action}"
        if pattern_key in self.learned_patterns:
            pattern = self.learned_patterns[pattern_key]
            # 패턴 기반 매개변수 조정
            action_plan.parameters.update(pattern.get("successful_parameters", {}))
            action_plan.confidence = min(action_plan.confidence + 0.1, 1.0)
            action_plan.metadata["pattern_used"] = True
            logger.info(f"[AdvancedReActAgent] 학습된 패턴 사용: {pattern_key}")

        return action_plan

    async def _memory_enhanced_observe(self, action_result: Dict[str, Any], plan: ActionPlan) -> Dict[str, Any]:
        """메모리 기반 관찰"""
        # 기본 관찰 수행
        observation = await self._intelligent_observe(action_result, plan)

        # 메모리에 결과 저장
        tool_result = action_result.get("tool_result", "")
        is_success = "성공" in tool_result or "완료" in tool_result

        # 중요도 계산
        importance = 0.7 if is_success else 0.3

        # 단기 기억에 저장
        self.memory_manager.add_memory(
            content=f"{plan.tool_name} 도구로 {plan.action} 실행: {tool_result}",
            memory_type=MemoryType.SHORT_TERM,
            importance=importance,
            metadata={
                "tool": plan.tool_name,
                "action": plan.action,
                "success": is_success,
                "task_id": self.current_task.task_id if self.current_task else None
            }
        )

        # 성공한 패턴 학습
        if is_success:
            pattern_key = f"{self.memory.current_goal}_{plan.tool_name}_{plan.action}"
            self.learned_patterns[pattern_key] = {
                "successful_parameters": plan.parameters,
                "success_count": self.learned_patterns.get(pattern_key, {}).get("success_count", 0) + 1,
                "last_success": datetime.now().isoformat()
            }
            logger.info(f"[AdvancedReActAgent] 성공 패턴 학습: {pattern_key}")

        # 경험 기억에 저장
        self.memory_manager.add_memory(
            content=f"작업 '{self.memory.current_goal}'에서 {plan.tool_name} 도구 사용",
            memory_type=MemoryType.EPISODIC,
            importance=0.5,
            metadata={
                "task_goal": self.memory.current_goal,
                "tool_used": plan.tool_name,
                "success": is_success,
                "timestamp": datetime.now().isoformat()
            }
        )

        return observation

    async def _generate_advanced_response(self) -> str:
        """고급 최종 응답 생성"""
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

        # 메모리 정보
        memory_summary = self.memory_manager.get_memory_summary()
        response += f"🧠 메모리 상태:\n"
        response += f"- 작업 기억: {memory_summary['working_memory']}개\n"
        response += f"- 단기 기억: {memory_summary['short_term_memory']}개\n"
        response += f"- 장기 기억: {memory_summary['long_term_memory']}개\n"
        response += f"- 경험 기억: {memory_summary['episodic_memory']}개\n\n"

        # 학습된 패턴 정보
        if self.learned_patterns:
            response += f"🎓 학습된 패턴: {len(self.learned_patterns)}개\n\n"

        # 주요 단계 요약
        response += "📋 수행된 주요 단계:\n"
        for i, step in enumerate(self.memory.steps, 1):
            if step["step_type"] == ReActStep.ACTION.value:
                response += f"{i}. {step['content']}\n"

        return response

# 테스트용 함수
async def test_advanced_react_agent():
    """고급 ReAct 에이전트 테스트"""
    agent = AdvancedReActAgent(max_steps=6)

    test_goals = [
        "React 개발자 채용공고를 작성해주세요",
        "지원자 목록을 조회해주세요",
        "최신 AI 기술 트렌드를 검색해주세요"
    ]

    for goal in test_goals:
        print(f"\n{'='*70}")
        print(f"고급 메모리 테스트 목표: {goal}")
        print(f"{'='*70}")

        result = await agent.process_task(goal)

        print(f"성공: {result['success']}")
        print(f"응답: {result['response']}")
        print(f"총 단계: {result.get('total_steps', 0)}")

        if result.get('memory_metrics'):
            metrics = result['memory_metrics']
            print(f"메모리 지표:")
            print(f"  - 총 메모리: {metrics['total_memories']}개")
            print(f"  - 작업 기억: {metrics['working_memory']}개")
            print(f"  - 단기 기억: {metrics['short_term_memory']}개")
            print(f"  - 장기 기억: {metrics['long_term_memory']}개")
            print(f"  - 경험 기억: {metrics['episodic_memory']}개")

        if result.get('task_context'):
            task = result['task_context']
            print(f"작업 컨텍스트:")
            print(f"  - 상태: {task['status']}")
            print(f"  - 진행률: {task['progress']*100:.1f}%")
            print(f"  - 소요 시간: {task['duration']:.2f}초")

        if result.get('intelligence_metrics'):
            metrics = result['intelligence_metrics']
            print(f"지능 지표:")
            print(f"  - 성공률: {metrics['success_rate']*100:.1f}%")
            print(f"  - 효율성: {metrics['efficiency']*100:.1f}%")
            print(f"  - 목표 달성: {metrics['goal_achieved']}")

if __name__ == "__main__":
    # 테스트 실행
    asyncio.run(test_advanced_react_agent())
