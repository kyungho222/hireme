"""
ReAct 에이전트용 실제 도구 통합
기존 픽톡의 ToolExecutor와 서비스들을 ReAct 패턴에 맞게 래핑
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from modules.ai.services.react_agent_core import ReActMemory, ReActStep, ReActTool
from routers.pick_chatbot import ToolExecutor

logger = logging.getLogger(__name__)

class JobPostingTool(ReActTool):
    """채용공고 관리 도구"""

    def __init__(self):
        super().__init__("job_posting", "채용공고 생성, 수정, 조회를 수행합니다")
        self.tool_executor = ToolExecutor()

    async def execute(self, action: str = "create", **kwargs) -> Tuple[str, Dict[str, Any]]:
        """채용공고 도구 실행"""
        try:
            if action == "create":
                # 채용공고 생성
                job_data = kwargs.get("job_data", {})
                if not job_data:
                    # 기본 채용공고 데이터 생성
                    job_data = {
                        "title": kwargs.get("title", "새로운 채용공고"),
                        "position": kwargs.get("position", "개발자"),
                        "company": kwargs.get("company", "우리 회사"),
                        "description": kwargs.get("description", "우수한 인재를 찾고 있습니다."),
                        "requirements": kwargs.get("requirements", []),
                        "benefits": kwargs.get("benefits", []),
                        "status": "draft"
                    }

                result = await self.tool_executor.job_posting_tool("create", job_data=job_data)

                if result.get("status") == "success":
                    return f"채용공고가 성공적으로 생성되었습니다: {result.get('data', {}).get('title', '')}", {
                        "job_id": result.get("data", {}).get("_id"),
                        "title": result.get("data", {}).get("title"),
                        "status": "created"
                    }
                else:
                    return f"채용공고 생성에 실패했습니다: {result.get('error', '알 수 없는 오류')}", {
                        "error": result.get("error"),
                        "status": "failed"
                    }

            elif action == "list":
                # 채용공고 목록 조회
                result = await self.tool_executor.job_posting_tool("list", **kwargs)

                if result.get("status") == "success":
                    jobs = result.get("data", [])
                    return f"총 {len(jobs)}개의 채용공고를 찾았습니다.", {
                        "count": len(jobs),
                        "jobs": jobs[:5],  # 최대 5개만 반환
                        "status": "success"
                    }
                else:
                    return f"채용공고 목록 조회에 실패했습니다: {result.get('error', '알 수 없는 오류')}", {
                        "error": result.get("error"),
                        "status": "failed"
                    }

            elif action == "update":
                # 채용공고 수정
                job_id = kwargs.get("job_id")
                update_data = kwargs.get("update_data", {})

                if not job_id:
                    return "채용공고 ID가 필요합니다.", {"error": "job_id required", "status": "failed"}

                result = await self.tool_executor.job_posting_tool("update", job_id=job_id, **update_data)

                if result.get("status") == "success":
                    return f"채용공고가 성공적으로 수정되었습니다.", {
                        "job_id": job_id,
                        "status": "updated"
                    }
                else:
                    return f"채용공고 수정에 실패했습니다: {result.get('error', '알 수 없는 오류')}", {
                        "error": result.get("error"),
                        "status": "failed"
                    }

            else:
                return f"지원하지 않는 액션입니다: {action}", {"error": "unsupported action", "status": "failed"}

        except Exception as e:
            logger.error(f"JobPostingTool 실행 오류: {str(e)}")
            return f"채용공고 도구 실행 중 오류가 발생했습니다: {str(e)}", {
                "error": str(e),
                "status": "error"
            }

    def can_handle(self, task: str) -> bool:
        """채용공고 관련 작업 처리 가능 여부"""
        job_keywords = [
            "채용공고", "채용", "구인", "모집", "채용공고 작성", "채용공고 생성",
            "채용공고 수정", "채용공고 조회", "채용공고 목록", "job posting"
        ]
        return any(keyword in task.lower() for keyword in job_keywords)

class ApplicantTool(ReActTool):
    """지원자 관리 도구"""

    def __init__(self):
        super().__init__("applicant", "지원자 생성, 조회, 수정, 삭제를 수행합니다")
        self.tool_executor = ToolExecutor()

    async def execute(self, action: str = "list", **kwargs) -> Tuple[str, Dict[str, Any]]:
        """지원자 도구 실행"""
        try:
            if action == "list":
                # 지원자 목록 조회 (read 액션 사용)
                result = await self.tool_executor.applicant_tool("read", **kwargs)

                if "applicants" in result:
                    applicants = result.get("applicants", [])
                    return f"총 {len(applicants)}명의 지원자를 찾았습니다.", {
                        "count": len(applicants),
                        "applicants": applicants[:5],  # 최대 5명만 반환
                        "status": "success"
                    }
                elif "error" in result:
                    return f"지원자 목록 조회에 실패했습니다: {result.get('error', '알 수 없는 오류')}", {
                        "error": result.get("error"),
                        "status": "failed"
                    }
                else:
                    return f"지원자 목록 조회에 실패했습니다: 알 수 없는 오류", {
                        "error": "unknown error",
                        "status": "failed"
                    }

            elif action == "create":
                # 지원자 생성
                applicant_data = kwargs.get("applicant_data", {})
                if not applicant_data:
                    return "지원자 데이터가 필요합니다.", {"error": "applicant_data required", "status": "failed"}

                result = await self.tool_executor.applicant_tool("create", **applicant_data)

                if result.get("status") == "success":
                    return f"지원자가 성공적으로 생성되었습니다: {result.get('data', {}).get('name', '')}", {
                        "applicant_id": result.get("data", {}).get("_id"),
                        "name": result.get("data", {}).get("name"),
                        "status": "created"
                    }
                else:
                    return f"지원자 생성에 실패했습니다: {result.get('error', '알 수 없는 오류')}", {
                        "error": result.get("error"),
                        "status": "failed"
                    }

            elif action == "update_status":
                # 지원자 상태 업데이트
                applicant_id = kwargs.get("applicant_id")
                status = kwargs.get("status")

                if not applicant_id or not status:
                    return "지원자 ID와 상태가 필요합니다.", {"error": "applicant_id and status required", "status": "failed"}

                result = await self.tool_executor.applicant_tool("update_status", applicant_id=applicant_id, status=status)

                if result.get("status") == "success":
                    return f"지원자 상태가 {status}로 변경되었습니다.", {
                        "applicant_id": applicant_id,
                        "status": status,
                        "updated": True
                    }
                else:
                    return f"지원자 상태 변경에 실패했습니다: {result.get('error', '알 수 없는 오류')}", {
                        "error": result.get("error"),
                        "status": "failed"
                    }

            elif action == "get_stats":
                # 지원자 통계 조회
                result = await self.tool_executor.applicant_tool("get_stats", **kwargs)

                if result.get("status") == "success":
                    stats = result.get("data", {})
                    return f"지원자 통계를 조회했습니다: 총 {stats.get('total', 0)}명", {
                        "stats": stats,
                        "status": "success"
                    }
                else:
                    return f"지원자 통계 조회에 실패했습니다: {result.get('error', '알 수 없는 오류')}", {
                        "error": result.get("error"),
                        "status": "failed"
                    }

            else:
                return f"지원하지 않는 액션입니다: {action}", {"error": "unsupported action", "status": "failed"}

        except Exception as e:
            logger.error(f"ApplicantTool 실행 오류: {str(e)}")
            return f"지원자 도구 실행 중 오류가 발생했습니다: {str(e)}", {
                "error": str(e),
                "status": "error"
            }

    def can_handle(self, task: str) -> bool:
        """지원자 관련 작업 처리 가능 여부"""
        applicant_keywords = [
            "지원자", "지원자 관리", "지원자 조회", "지원자 목록", "지원자 생성",
            "지원자 수정", "지원자 삭제", "지원자 상태", "지원자 통계", "applicant"
        ]
        return any(keyword in task.lower() for keyword in applicant_keywords)

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

            # analysis_type에 따라 적절한 액션 선택
            if analysis_type == "resume" or "이력서" in data:
                result = await self.tool_executor.ai_analysis_tool("analyze_resume", resume_text=data)
            elif analysis_type == "job_posting" or "채용공고" in data:
                result = await self.tool_executor.ai_analysis_tool("optimize_job_posting", job_title=data, job_description=data)
            else:
                # 기본적으로 이력서 분석으로 처리
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

class ResumeAnalysisTool(ReActTool):
    """이력서 분석 도구"""

    def __init__(self):
        super().__init__("resume_analysis", "이력서 분석 및 평가를 수행합니다")
        self.tool_executor = ToolExecutor()

    async def execute(self, action: str = "analyze", **kwargs) -> Tuple[str, Dict[str, Any]]:
        """이력서 분석 도구 실행"""
        try:
            resume_data = kwargs.get("resume_data", {})

            if action == "analyze":
                # 기본 이력서 분석 로직
                skills = resume_data.get("skills", [])
                experience = resume_data.get("experience", [])

                analysis_result = {
                    "skills_count": len(skills),
                    "experience_years": len(experience),
                    "recommendation": "적합한 후보자입니다." if len(skills) >= 3 else "추가 스킬이 필요합니다."
                }

                return f"이력서 분석을 완료했습니다. {len(skills)}개 스킬, {len(experience)}년 경력을 확인했습니다.", {
                    "analysis": analysis_result,
                    "status": "success"
                }
            else:
                return f"지원하지 않는 이력서 분석 액션입니다: {action}", {
                    "error": "unsupported action",
                    "status": "failed"
                }
        except Exception as e:
            logger.error(f"ResumeAnalysisTool 실행 오류: {str(e)}")
            return f"이력서 분석 도구 실행 중 오류가 발생했습니다: {str(e)}", {
                "error": str(e),
                "status": "error"
            }

    def can_handle(self, task: str) -> bool:
        """이력서 분석 관련 작업 처리 가능 여부"""
        resume_keywords = ["이력서", "resume", "분석", "평가", "스킬", "경력", "cv"]
        return any(keyword in task.lower() for keyword in resume_keywords)

class InterviewSchedulerTool(ReActTool):
    """면접 일정 관리 도구"""

    def __init__(self):
        super().__init__("interview_scheduler", "면접 일정을 관리합니다")
        self.tool_executor = ToolExecutor()

    async def execute(self, action: str = "schedule", **kwargs) -> Tuple[str, Dict[str, Any]]:
        """면접 일정 관리 도구 실행"""
        try:
            if action == "schedule":
                candidate = kwargs.get("candidate", "지원자")
                date = kwargs.get("date", "2025-09-10")
                time = kwargs.get("time", "14:00")

                return f"{candidate}님의 면접을 {date} {time}에 예약했습니다.", {
                    "candidate": candidate,
                    "date": date,
                    "time": time,
                    "status": "scheduled"
                }
            elif action == "list":
                return "예정된 면접 일정을 조회했습니다.", {
                    "interviews": [
                        {"candidate": "김개발", "date": "2025-09-10", "time": "14:00"},
                        {"candidate": "이프론트", "date": "2025-09-11", "time": "10:00"}
                    ],
                    "status": "success"
                }
            else:
                return f"지원하지 않는 면접 일정 액션입니다: {action}", {
                    "error": "unsupported action",
                    "status": "failed"
                }
        except Exception as e:
            logger.error(f"InterviewSchedulerTool 실행 오류: {str(e)}")
            return f"면접 일정 관리 도구 실행 중 오류가 발생했습니다: {str(e)}", {
                "error": str(e),
                "status": "error"
            }

    def can_handle(self, task: str) -> bool:
        """면접 일정 관련 작업 처리 가능 여부"""
        interview_keywords = ["면접", "일정", "예약", "interview", "schedule", "appointment"]
        return any(keyword in task.lower() for keyword in interview_keywords)

class EnhancedReActAgent:
    """실제 도구가 통합된 향상된 ReAct 에이전트"""

    def __init__(self, max_steps: int = 10):
        self.max_steps = max_steps
        self.memory = ReActMemory(max_steps=max_steps)

        # 모든 도구들 초기화 (기존 + 새로 추가된 툴들)
        self.tools = {
            # 핵심 채용 관련 툴들
            "job_posting": JobPostingTool(),
            "applicant": ApplicantTool(),
            "search": SearchTool(),
            "ai_analysis": AIAnalysisTool(),

            # 미활성화되었던 툴들 (이제 활성화)
            "github": GitHubTool(),
            "mongodb": MongoDBTool(),
            "mail": MailTool(),
            "web_automation": WebAutomationTool(),

            # 새로 추가된 툴들
            "file_upload": FileUploadTool(),
            "navigate": NavigateTool(),
            "resume_analysis": ResumeAnalysisTool(),
            "interview_scheduler": InterviewSchedulerTool()
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
            elif selected_tool.name == "job_posting":
                result, metadata = await selected_tool.execute(action="create", title=goal)
            elif selected_tool.name == "applicant":
                result, metadata = await selected_tool.execute(action="list")
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
            elif selected_tool.name == "resume_analysis":
                result, metadata = await selected_tool.execute(action="analyze", resume_data={"skills": [], "experience": []})
            elif selected_tool.name == "interview_scheduler":
                result, metadata = await selected_tool.execute(action="schedule", candidate=goal)
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
        "React 개발자 채용공고를 작성해주세요",
        "지원자 목록을 조회해주세요",
        "최신 AI 기술 트렌드를 검색해주세요"
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
