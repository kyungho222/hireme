import json
import logging
import re
import time
import uuid
from collections import defaultdict
from datetime import datetime
from typing import Any, Dict, List, Optional

from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

# 기존 서비스들 import
try:
    from modules.core.services.llm_service import LLMService
    from modules.core.services.mongo_service import MongoService
except ImportError:
    from modules.core.services.llm_service import LLMService
    from modules.core.services.mongo_service import MongoService

# 웹 자동화를 위한 추가 import
import asyncio
import time

from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


# 웹 자동화 클래스
class WebAutomation:
    def __init__(self):
        self.driver = None
        self.base_url = "http://localhost:3001"  # 프론트엔드 URL

    def init_driver(self):
        """웹 드라이버 초기화"""
        if not self.driver:
            options = webdriver.ChromeOptions()
            options.add_argument('--headless')  # 헤드리스 모드
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            self.driver = webdriver.Chrome(options=options)
        return self.driver

    async def navigate_to_page(self, page_path: str):
        """특정 페이지로 이동"""
        try:
            driver = self.init_driver()
            url = f"{self.base_url}{page_path}"
            driver.get(url)
            await asyncio.sleep(2)  # 페이지 로딩 대기
            return {"status": "success", "url": url}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def click_element(self, selector: str, selector_type: str = "css"):
        """요소 클릭"""
        try:
            driver = self.init_driver()
            wait = WebDriverWait(driver, 10)

            if selector_type == "css":
                element = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
            elif selector_type == "xpath":
                element = wait.until(EC.element_to_be_clickable((By.XPATH, selector)))
            else:
                element = wait.until(EC.element_to_be_clickable((By.ID, selector)))

            element.click()
            await asyncio.sleep(1)
            return {"status": "success", "clicked": selector}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def input_text(self, selector: str, text: str, selector_type: str = "css"):
        """텍스트 입력"""
        try:
            driver = self.init_driver()
            wait = WebDriverWait(driver, 10)

            if selector_type == "css":
                element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
            elif selector_type == "xpath":
                element = wait.until(EC.presence_of_element_located((By.XPATH, selector)))
            else:
                element = wait.until(EC.presence_of_element_located((By.ID, selector)))

            element.clear()
            element.send_keys(text)
            await asyncio.sleep(0.5)
            return {"status": "success", "input": text}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def get_page_content(self):
        """현재 페이지 내용 가져오기"""
        try:
            driver = self.init_driver()
            return {
                "status": "success",
                "title": driver.title,
                "url": driver.current_url,
                "content": driver.page_source[:1000]  # 처음 1000자만
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def close_driver(self):
        """드라이버 종료"""
        if self.driver:
            self.driver.quit()
            self.driver = None

# 독립화된 툴 실행기 클래스
class ToolExecutor:
    def __init__(self):
        self.tools = {
            "github": self.github_tool,
            "mongodb": self.mongodb_tool,
            "search": self.search_tool,
            "web_automation": self.web_automation_tool,
            "job_posting": self.job_posting_tool,
            "applicant": self.applicant_tool,
            "mail": self.mail_tool,
            "ai_analysis": self.ai_analysis_tool
        }
        self.cache = {}
        self.error_stats = {}
        self.performance_stats = {}
        self.mongo_service = MongoService()
        self.web_automation = WebAutomation()

    async def execute_async(self, tool_name, action, **params):
        """비동기 툴 실행 - 성능 모니터링 포함"""
        import time
        start_time = time.time()

        try:
            if tool_name in self.tools:
                # 툴 실행
                result = await self.tools[tool_name](action, **params)

                # 성능 통계 업데이트
                execution_time = time.time() - start_time
                self._update_performance_stats(tool_name, execution_time)

                return {
                    "status": "success",
                    "data": result,
                    "execution_time": execution_time,
                    "tool": tool_name,
                    "action": action
                }
            else:
                # 에러 통계 업데이트
                self._update_error_stats(tool_name, f"알 수 없는 툴: {tool_name}")
                return {
                    "status": "error",
                    "message": f"알 수 없는 툴: {tool_name}"
                }
        except Exception as e:
            # 에러 통계 업데이트
            self._update_error_stats(tool_name, str(e))
            return {
                "status": "error",
                "message": str(e)
            }

    async def github_tool(self, action, **params):
        """GitHub 관련 툴 - 실제 GitHub API 연동"""
        try:
            import os

            import aiohttp

            # GitHub API 토큰 (환경변수에서 가져오기)
            github_token = os.getenv('GITHUB_TOKEN')
            headers = {}
            if github_token:
                headers['Authorization'] = f'token {github_token}'

            base_url = "https://api.github.com"

            if action == "get_user_info":
                username = params.get("username", "octocat")
                async with aiohttp.ClientSession() as session:
                    async with session.get(f"{base_url}/users/{username}", headers=headers) as response:
                        if response.status == 200:
                            user_data = await response.json()
                            return {
                                "status": "success",
                                "user": {
                                    "login": user_data.get("login"),
                                    "name": user_data.get("name"),
                                    "bio": user_data.get("bio"),
                                    "public_repos": user_data.get("public_repos", 0),
                                    "followers": user_data.get("followers", 0),
                                    "following": user_data.get("following", 0),
                                    "created_at": user_data.get("created_at"),
                                    "avatar_url": user_data.get("avatar_url")
                                }
                            }
                        else:
                            return {"status": "error", "message": f"GitHub API 오류: {response.status}"}

            elif action == "get_repos":
                username = params.get("username", "octocat")
                page = params.get("page", 1)
                per_page = params.get("per_page", 10)

                async with aiohttp.ClientSession() as session:
                    async with session.get(
                        f"{base_url}/users/{username}/repos?page={page}&per_page={per_page}&sort=updated",
                        headers=headers
                    ) as response:
                        if response.status == 200:
                            repos_data = await response.json()
                            repos = []
                            for repo in repos_data:
                                repos.append({
                                    "name": repo.get("name"),
                                    "description": repo.get("description"),
                                    "language": repo.get("language"),
                                    "stars": repo.get("stargazers_count", 0),
                                    "forks": repo.get("forks_count", 0),
                                    "updated_at": repo.get("updated_at"),
                                    "html_url": repo.get("html_url")
                                })
                            return {"status": "success", "repos": repos}
                        else:
                            return {"status": "error", "message": f"GitHub API 오류: {response.status}"}

            elif action == "get_commits":
                username = params.get("username", "octocat")
                repo = params.get("repo", "sample-repo")
                page = params.get("page", 1)
                per_page = params.get("per_page", 10)

                async with aiohttp.ClientSession() as session:
                    async with session.get(
                        f"{base_url}/repos/{username}/{repo}/commits?page={page}&per_page={per_page}",
                        headers=headers
                    ) as response:
                        if response.status == 200:
                            commits_data = await response.json()
                            commits = []
                            for commit in commits_data:
                                commits.append({
                                    "sha": commit.get("sha", "")[:7],
                                    "message": commit.get("commit", {}).get("message", ""),
                                    "author": commit.get("commit", {}).get("author", {}).get("name", ""),
                                    "date": commit.get("commit", {}).get("author", {}).get("date", ""),
                                    "html_url": commit.get("html_url")
                                })
                            return {"status": "success", "commits": commits}
                        else:
                            return {"status": "error", "message": f"GitHub API 오류: {response.status}"}

            elif action == "search_repos":
                query = params.get("query", "")
                page = params.get("page", 1)
                per_page = params.get("per_page", 10)

                async with aiohttp.ClientSession() as session:
                    async with session.get(
                        f"{base_url}/search/repositories?q={query}&page={page}&per_page={per_page}&sort=stars",
                        headers=headers
                    ) as response:
                        if response.status == 200:
                            search_data = await response.json()
                            repos = []
                            for repo in search_data.get("items", []):
                                repos.append({
                                    "name": repo.get("full_name"),
                                    "description": repo.get("description"),
                                    "language": repo.get("language"),
                                    "stars": repo.get("stargazers_count", 0),
                                    "forks": repo.get("forks_count", 0),
                                    "html_url": repo.get("html_url")
                                })
                            return {"status": "success", "repos": repos, "total_count": search_data.get("total_count", 0)}
                        else:
                            return {"status": "error", "message": f"GitHub API 오류: {response.status}"}

            else:
                return {"status": "error", "message": f"알 수 없는 GitHub 액션: {action}"}

        except Exception as e:
            logger.error(f"❌ [GitHub툴] 처리 실패: {str(e)}")
            return {"status": "error", "message": f"GitHub 툴 처리 실패: {str(e)}"}

    async def mongodb_tool(self, action, **params):
        """MongoDB 관련 툴 - 실제 데이터베이스 연결"""
        try:
            if action == "find_documents":
                collection = params.get("collection", "applicants")
                query = params.get("query", {})

                # 채용공고 조회인 경우
                if collection == "job_postings":
                    # datetime 모듈은 이미 전역으로 import됨

                    from bson import ObjectId

                    # 실제 데이터베이스에서 조회
                    filter_query = {}

                    # 오늘자 필터링
                    if query.get("today_only"):
                        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
                        filter_query["created_at"] = {"$gte": today}

                    # 상태 필터링
                    if query.get("status"):
                        filter_query["status"] = query["status"]

                    # 실제 MongoDB 조회
                    cursor = self.mongo_service.db.job_postings.find(filter_query).sort("created_at", -1)
                    job_postings = await cursor.to_list(100)  # 최대 100개

                    # 결과 포맷팅
                    documents = []
                    for job in job_postings:
                        job["_id"] = str(job["_id"])
                        documents.append(job)

                    return {"documents": documents}

                # 지원자 조회인 경우
                elif collection == "applicants":
                    result = await self.mongo_service.get_applicants(
                        skip=params.get("skip", 0),
                        limit=params.get("limit", 20)
                    )
                    return {"documents": result["applicants"]}

                # 기타 컬렉션
                else:
                    cursor = self.mongo_service.db[collection].find(query)
                    documents = await cursor.to_list(100)
                    return {"documents": documents}

            elif action == "count_documents":
                collection = params.get("collection", "applicants")
                count = await self.mongo_service.db[collection].count_documents({})
                return {"count": count}

            else:
                raise ValueError(f"알 수 없는 MongoDB 액션: {action}")

        except Exception as e:
            logger.error(f"❌ [MongoDB툴] 처리 실패: {str(e)}")
            return {"status": "error", "message": f"MongoDB 조회 실패: {str(e)}"}

    async def search_tool(self, action, **params):
        """검색 관련 툴 - 실제 웹 검색 연동"""
        try:
            import re

            if action == "web_search":
                query = params.get("query", "")
                if not query:
                    return {"status": "error", "message": "검색어가 필요합니다."}

                # agent_system의 WebSearchNode 사용
                from chatbot.core.agent_system import WebSearchNode

                web_search = WebSearchNode()
                search_result = await web_search.process_search(query)

                # 검색 결과를 구조화된 형태로 변환
                results = []

                # AI 채용 트렌드 관련 검색인 경우 상세 정보 제공
                if "AI" in query and ("채용" in query or "트렌드" in query):
                    results.append({
                        "title": "2024년 AI 채용 트렌드 요약",
                        "snippet": "AI/ML 엔지니어 수요 급증 (전년 대비 150% 증가), 생성형 AI 전문가 인기 상승, AI 윤리 및 규제 전문가 필요성 증가",
                        "link": "https://example.com/ai-trends-2024",
                        "source": "AI 채용 시장 분석"
                    })
                    results.append({
                        "title": "AI 기술별 채용 동향",
                        "snippet": "머신러닝/딥러닝, 자연어 처리, 컴퓨터 비전, 강화학습 분야 전문가 수요 증가",
                        "link": "https://example.com/ai-tech-trends",
                        "source": "기술 트렌드 분석"
                    })
                    results.append({
                        "title": "AI 급여 및 경력별 현황",
                        "snippet": "신입: 4,000만원~5,500만원, 경력 3-5년: 6,000만원~8,500만원, 경력 5년 이상: 8,000만원~12,000만원",
                        "link": "https://example.com/ai-salary-guide",
                        "source": "급여 가이드"
                    })
                else:
                    # 일반 검색 결과
                    results.append({
                        "title": f"{query} - 검색 결과",
                        "snippet": search_result[:200] + "..." if len(search_result) > 200 else search_result,
                        "link": f"https://search.example.com?q={query}",
                        "source": "통합 검색"
                    })

                # 이메일 전송 요청이 있는지 확인
                input_text = params.get("input_text", "")
                email_match = re.search(r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', input_text)

                if email_match:
                    email_address = email_match.group(1)
                    # 현재 시스템의 이메일 설정 사용
                    try:
                        from main import get_mail_settings
                        mail_settings = get_mail_settings()

                        if mail_settings and mail_settings.get('senderEmail'):
                            # 이메일 전송 시도
                            import smtplib
                            from email.mime.multipart import MIMEMultipart
                            from email.mime.text import MIMEText

                            msg = MIMEMultipart()
                            msg['From'] = f"AI 채용 어시스턴트 <{mail_settings.get('senderEmail')}>"
                            msg['To'] = email_address
                            msg['Subject'] = f"AI 채용 트렌드 검색 결과: {query}"

                            # HTML 형식으로 이메일 내용 구성
                            html_content = f"""
                            <html>
                            <head>
                                <style>
                                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                                    .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px; }}
                                    .content {{ padding: 20px; background: #f9f9f9; border-radius: 10px; margin: 20px 0; }}
                                    .highlight {{ background: #fff3cd; padding: 15px; border-left: 4px solid #ffc107; border-radius: 5px; }}
                                    .footer {{ text-align: center; color: #666; font-size: 12px; margin-top: 30px; }}
                                </style>
                            </head>
                            <body>
                                <div class="header">
                                    <h1>🤖 AI 채용 트렌드 리포트</h1>
                                    <p>실시간 웹 검색을 통한 최신 정보</p>
                                </div>

                                <div class="content">
                                    {search_result.replace(chr(10), '<br>')}
                                </div>

                                <div class="highlight">
                                    <strong>💡 이 정보는 AI 어시스턴트가 실시간 웹 검색을 통해 수집하고 요약한 내용입니다.</strong>
                                </div>

                                <div class="footer">
                                    <p>본 이메일은 자동으로 생성되었습니다.</p>
                                    <p>© 2024 AI 채용 어시스턴트</p>
                                </div>
                            </body>
                            </html>
                            """

                            msg.attach(MIMEText(html_content, 'html'))

                            smtp_port = mail_settings.get('smtpPort', 587)
                            smtp_server = mail_settings.get('smtpServer', 'smtp.gmail.com')

                            if smtp_port == 465:
                                with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
                                    server.login(mail_settings.get('senderEmail'), mail_settings.get('senderPassword'))
                                    server.send_message(msg)
                            else:
                                with smtplib.SMTP(smtp_server, smtp_port) as server:
                                    server.starttls()
                                    server.login(mail_settings.get('senderEmail'), mail_settings.get('senderPassword'))
                                    server.send_message(msg)

                            results.append({
                                "title": "📧 이메일 전송 완료",
                                "snippet": f"검색 결과가 {email_address}로 전송되었습니다.",
                                "link": "#",
                                "source": "이메일 시스템"
                            })
                        else:
                            results.append({
                                "title": "⚠️ 이메일 설정 누락",
                                "snippet": "이메일 전송을 위한 설정이 완료되지 않았습니다.",
                                "link": "#",
                                "source": "이메일 시스템"
                            })
                    except Exception as e:
                        results.append({
                            "title": "❌ 이메일 전송 오류",
                            "snippet": f"이메일 전송 중 오류가 발생했습니다: {str(e)}",
                            "link": "#",
                            "source": "이메일 시스템"
                        })

                return {
                    "status": "success",
                    "results": results,
                    "full_content": search_result,
                    "query": query,
                    "email_sent": email_match.group(1) if email_match else None
                }

            elif action == "news_search":
                query = params.get("query", "")
                if not query:
                    return {"status": "error", "message": "검색어가 필요합니다."}

                # 뉴스 검색 (실제로는 뉴스 API 사용 권장)
                news_url = f"https://news.google.com/search?q={quote_plus(query)}&hl=ko&gl=KR&ceid=KR:ko"

                async with aiohttp.ClientSession() as session:
                    headers = {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                    }
                    async with session.get(news_url, headers=headers) as response:
                        if response.status == 200:
                            content = await response.text()

                            # 뉴스 결과 추출
                            results = []
                            results.append({
                                "title": f"{query} 관련 뉴스",
                                "snippet": f"{query}에 대한 최신 뉴스를 확인할 수 있습니다.",
                                "link": news_url,
                                "source": "Google News"
                            })

                            return {"status": "success", "results": results}
                        else:
                            return {"status": "error", "message": f"뉴스 검색 실패: {response.status}"}

            elif action == "image_search":
                query = params.get("query", "")
                if not query:
                    return {"status": "error", "message": "검색어가 필요합니다."}

                # 이미지 검색 (실제로는 이미지 검색 API 사용 권장)
                image_url = f"https://www.google.com/search?q={quote_plus(query)}&tbm=isch"

                results = []
                results.append({
                    "title": f"{query} 이미지 검색 결과",
                    "snippet": f"{query}에 대한 이미지를 검색할 수 있습니다.",
                    "link": image_url,
                    "source": "Google Images"
                })

                return {"status": "success", "results": results}

            else:
                return {"status": "error", "message": f"알 수 없는 검색 액션: {action}"}

        except Exception as e:
            logger.error(f"❌ [검색툴] 처리 실패: {str(e)}")
            return {"status": "error", "message": f"검색 툴 처리 실패: {str(e)}"}

    async def web_automation_tool(self, action, **params):
        """웹 자동화 관련 툴 - 실제 클릭/입력 액션 수행"""
        try:
            if action == "navigate":
                page_path = params.get("page_path", "/")
                return await self.web_automation.navigate_to_page(page_path)

            elif action == "click":
                selector = params.get("selector", "")
                selector_type = params.get("selector_type", "css")
                return await self.web_automation.click_element(selector, selector_type)

            elif action == "input":
                selector = params.get("selector", "")
                text = params.get("text", "")
                selector_type = params.get("selector_type", "css")
                return await self.web_automation.input_text(selector, text, selector_type)

            elif action == "get_content":
                return await self.web_automation.get_page_content()

            else:
                raise ValueError(f"알 수 없는 웹 자동화 액션: {action}")

        except Exception as e:
            return {"status": "error", "message": f"웹 자동화 실패: {str(e)}"}

    async def job_posting_tool(self, action, **params):
        """채용공고 CRUD 툴 - 키워드 자동 추출 포함"""
        try:
            logger.info(f"📝 [채용공고툴] 액션: {action}, 파라미터: {params}")

            if action == "create":
                # 채용공고 생성
                job_data = params.get("job_data", {})

                # 키워드 자동 추출
                extracted_keywords = []
                try:
                    extracted_keywords = self._extract_job_keywords(job_data)
                except Exception as e:
                    logger.warning(f"⚠️ [채용공고툴] 키워드 추출 실패: {str(e)}")
                finally:
                    job_data["extracted_keywords"] = extracted_keywords

                job_data["created_at"] = datetime.now()
                job_data["updated_at"] = datetime.now()
                job_data["status"] = "published"  # 모든 채용공고를 활성화 상태로 통일
                job_data["applicants"] = 0
                job_data["views"] = 0

                result = await self.mongo_service.db.job_postings.insert_one(job_data)
                logger.info(f"✅ [채용공고툴] 생성 완료: {result.inserted_id} (키워드: {len(extracted_keywords)}개)")
                return {
                    "job_id": str(result.inserted_id),
                    "message": "채용공고가 성공적으로 생성되었습니다.",
                    "extracted_keywords": extracted_keywords
                }

            elif action == "read":
                # 채용공고 조회
                job_id = params.get("job_id")
                if job_id:
                    job = await self.mongo_service.db.job_postings.find_one({"_id": ObjectId(job_id)})
                    if job:
                        job["_id"] = str(job["_id"])
                        logger.info(f"✅ [채용공고툴] 조회 완료: {job_id}")
                        return {"job": job}
                    else:
                        logger.warning(f"⚠️ [채용공고툴] 채용공고 없음: {job_id}")
                        return {"error": "채용공고를 찾을 수 없습니다."}
                else:
                    # 전체 목록 조회
                    skip = params.get("skip", 0)
                    limit = params.get("limit", 20)
                    status = params.get("status")

                    filter_query = {}
                    if status:
                        filter_query["status"] = status

                    cursor = self.mongo_service.db.job_postings.find(filter_query).skip(skip).limit(limit)
                    jobs = await cursor.to_list(limit)

                    for job in jobs:
                        job["_id"] = str(job["_id"])

                    logger.info(f"✅ [채용공고툴] 목록 조회 완료: {len(jobs)}개")
                    return {"jobs": jobs, "count": len(jobs)}

            elif action == "update":
                # 채용공고 수정
                job_id = params.get("job_id")
                update_data = params.get("update_data", {})
                update_data["updated_at"] = datetime.now()

                result = await self.mongo_service.db.job_postings.update_one(
                    {"_id": ObjectId(job_id)},
                    {"$set": update_data}
                )

                if result.modified_count > 0:
                    logger.info(f"✅ [채용공고툴] 수정 완료: {job_id}")
                    return {"message": "채용공고가 성공적으로 수정되었습니다."}
                else:
                    logger.warning(f"⚠️ [채용공고툴] 수정 실패: {job_id}")
                    return {"error": "채용공고 수정에 실패했습니다."}

            elif action == "delete":
                # 채용공고 삭제
                job_id = params.get("job_id")
                result = await self.mongo_service.db.job_postings.delete_one({"_id": ObjectId(job_id)})

                if result.deleted_count > 0:
                    logger.info(f"✅ [채용공고툴] 삭제 완료: {job_id}")
                    return {"message": "채용공고가 성공적으로 삭제되었습니다."}
                else:
                    logger.warning(f"⚠️ [채용공고툴] 삭제 실패: {job_id}")
                    return {"error": "채용공고 삭제에 실패했습니다."}

            elif action == "publish":
                # 채용공고 발행
                job_id = params.get("job_id")
                result = await self.mongo_service.db.job_postings.update_one(
                    {"_id": ObjectId(job_id)},
                    {"$set": {"status": "published", "updated_at": datetime.now()}}
                )

                if result.modified_count > 0:
                    logger.info(f"✅ [채용공고툴] 발행 완료: {job_id}")
                    return {"message": "채용공고가 성공적으로 발행되었습니다."}
                else:
                    logger.warning(f"⚠️ [채용공고툴] 발행 실패: {job_id}")
                    return {"error": "채용공고 발행에 실패했습니다."}

            else:
                logger.error(f"❌ [채용공고툴] 알 수 없는 액션: {action}")
                raise ValueError(f"알 수 없는 채용공고 액션: {action}")

        except Exception as e:
            logger.error(f"❌ [채용공고툴] 처리 실패: {str(e)}")
            return {"error": f"채용공고 처리 실패: {str(e)}"}

    async def applicant_tool(self, action, **params):
        """지원자 CRUD 툴"""
        try:
            logger.info(f"👥 [지원자툴] 액션: {action}, 파라미터: {params}")

            if action == "create":
                # 지원자 생성
                applicant_data = params.get("applicant_data", {})
                applicant_data["created_at"] = datetime.now()
                applicant_data["status"] = "pending"

                result = await self.mongo_service.db.applicants.insert_one(applicant_data)
                logger.info(f"✅ [지원자툴] 생성 완료: {result.inserted_id}")
                return {
                    "applicant_id": str(result.inserted_id),
                    "message": "지원자가 성공적으로 생성되었습니다."
                }

            elif action == "read":
                # 지원자 조회
                applicant_id = params.get("applicant_id")
                if applicant_id:
                    applicant = await self.mongo_service.db.applicants.find_one({"_id": ObjectId(applicant_id)})
                    if applicant:
                        applicant["_id"] = str(applicant["_id"])
                        logger.info(f"✅ [지원자툴] 조회 완료: {applicant_id}")
                        return {"applicant": applicant}
                    else:
                        logger.warning(f"⚠️ [지원자툴] 지원자 없음: {applicant_id}")
                        return {"error": "지원자를 찾을 수 없습니다."}
                else:
                    # 전체 목록 조회
                    skip = params.get("skip", 0)
                    limit = params.get("limit", 20)
                    status = params.get("status")
                    position = params.get("position")

                    filter_query = {}
                    if status:
                        filter_query["status"] = status
                    if position:
                        filter_query["position"] = {"$regex": position, "$options": "i"}

                    cursor = self.mongo_service.db.applicants.find(filter_query).skip(skip).limit(limit)
                    applicants = await cursor.to_list(limit)

                    for applicant in applicants:
                        applicant["_id"] = str(applicant["_id"])

                    logger.info(f"✅ [지원자툴] 목록 조회 완료: {len(applicants)}개")
                    return {"applicants": applicants, "count": len(applicants)}

            elif action == "update":
                # 지원자 수정
                applicant_id = params.get("applicant_id")
                update_data = params.get("update_data", {})

                result = await self.mongo_service.db.applicants.update_one(
                    {"_id": ObjectId(applicant_id)},
                    {"$set": update_data}
                )

                if result.modified_count > 0:
                    logger.info(f"✅ [지원자툴] 수정 완료: {applicant_id}")
                    return {"message": "지원자 정보가 성공적으로 수정되었습니다."}
                else:
                    logger.warning(f"⚠️ [지원자툴] 수정 실패: {applicant_id}")
                    return {"error": "지원자 수정에 실패했습니다."}

            elif action == "delete":
                # 지원자 삭제
                applicant_id = params.get("applicant_id")
                result = await self.mongo_service.db.applicants.delete_one({"_id": ObjectId(applicant_id)})

                if result.deleted_count > 0:
                    logger.info(f"✅ [지원자툴] 삭제 완료: {applicant_id}")
                    return {"message": "지원자가 성공적으로 삭제되었습니다."}
                else:
                    logger.warning(f"⚠️ [지원자툴] 삭제 실패: {applicant_id}")
                    return {"error": "지원자 삭제에 실패했습니다."}

            elif action == "update_status":
                # 지원자 상태 업데이트
                applicant_id = params.get("applicant_id")
                new_status = params.get("status")

                result = await self.mongo_service.db.applicants.update_one(
                    {"_id": ObjectId(applicant_id)},
                    {"$set": {"status": new_status}}
                )

                if result.modified_count > 0:
                    logger.info(f"✅ [지원자툴] 상태 변경 완료: {applicant_id} -> {new_status}")
                    return {"message": f"지원자 상태가 {new_status}로 변경되었습니다."}
                else:
                    logger.warning(f"⚠️ [지원자툴] 상태 변경 실패: {applicant_id}")
                    return {"error": "지원자 상태 변경에 실패했습니다."}

            elif action == "get_stats":
                # 지원자 통계 조회
                pipeline = [
                    {
                        "$group": {
                            "_id": "$status",
                            "count": {"$sum": 1}
                        }
                    }
                ]

                stats = await self.mongo_service.db.applicants.aggregate(pipeline).to_list(None)
                total = await self.mongo_service.db.applicants.count_documents({})

                return {
                    "total": total,
                    "by_status": stats
                }

            else:
                raise ValueError(f"알 수 없는 지원자 액션: {action}")

        except Exception as e:
            logger.error(f"❌ [지원자툴] 처리 실패: {str(e)}")
            return {"status": "error", "message": f"지원자 처리 실패: {str(e)}"}

    async def mail_tool(self, action, **params):
        """메일 발송 툴"""
        try:
            logger.info(f"📧 [메일툴] 액션: {action}, 파라미터: {params}")

            import os
            import smtplib
            from email.mime.multipart import MIMEMultipart
            from email.mime.text import MIMEText

            if action == "send_test":
                # 테스트 메일 발송
                test_email = params.get("test_email")
                mail_settings = params.get("mail_settings", {})

                if not test_email or not mail_settings:
                    return {"error": "테스트 이메일과 메일 설정이 필요합니다."}

                # 메일 내용 생성
                subject = "테스트 메일"
                content = "안녕하세요! 이것은 테스트 메일입니다."

                # 메일 객체 생성
                msg = MIMEMultipart()
                msg['From'] = f"{mail_settings.get('senderName', '')} <{mail_settings.get('senderEmail')}>"
                msg['To'] = test_email
                msg['Subject'] = f"[테스트] {subject}"
                msg.attach(MIMEText(content, 'plain', 'utf-8'))

                # SMTP 서버 연결 및 메일 발송
                smtp_port = mail_settings.get('smtpPort', 587)
                smtp_server = mail_settings.get('smtpServer', 'smtp.gmail.com')

                if smtp_port == 465:
                    with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
                        server.login(mail_settings.get('senderEmail'), mail_settings.get('senderPassword'))
                        server.send_message(msg)
                else:
                    with smtplib.SMTP(smtp_server, smtp_port) as server:
                        server.starttls()
                        server.login(mail_settings.get('senderEmail'), mail_settings.get('senderPassword'))
                        server.send_message(msg)

                return {
                    "message": "테스트 메일이 성공적으로 발송되었습니다.",
                    "to": test_email,
                    "subject": f"[테스트] {subject}"
                }

            elif action == "send_bulk":
                # 대량 메일 발송
                status_type = params.get("status_type")  # passed, rejected, etc.
                mail_settings = params.get("mail_settings", {})

                if not status_type or not mail_settings:
                    return {"error": "상태 타입과 메일 설정이 필요합니다."}

                # 해당 상태의 지원자들 조회
                filter_query = {"status": status_type}
                cursor = self.mongo_service.db.applicants.find(filter_query)
                applicants = await cursor.to_list(None)

                if not applicants:
                    return {"message": f"{status_type} 상태의 지원자가 없습니다."}

                # 메일 템플릿 조회
                template = await self.mongo_service.db.mail_templates.find_one({"type": status_type})
                if not template:
                    return {"error": f"{status_type} 상태에 대한 메일 템플릿이 없습니다."}

                success_count = 0
                failed_count = 0
                failed_emails = []

                for applicant in applicants:
                    email = applicant.get('email')
                    if not email:
                        failed_count += 1
                        continue

                    # 메일 내용 포맷팅
                    content = template['content'].format(
                        applicant_name=applicant.get('name', '지원자'),
                        job_posting_title=applicant.get('job_posting_title', '채용공고'),
                        company_name=applicant.get('company_name', '회사명'),
                        position=applicant.get('position', '지원 직무')
                    )

                    # 메일 발송
                    try:
                        msg = MIMEMultipart()
                        msg['From'] = f"{mail_settings.get('senderName', '')} <{mail_settings.get('senderEmail')}>"
                        msg['To'] = email
                        msg['Subject'] = template['subject']
                        msg.attach(MIMEText(content, 'plain', 'utf-8'))

                        smtp_port = mail_settings.get('smtpPort', 587)
                        smtp_server = mail_settings.get('smtpServer', 'smtp.gmail.com')

                        if smtp_port == 465:
                            with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
                                server.login(mail_settings.get('senderEmail'), mail_settings.get('senderPassword'))
                                server.send_message(msg)
                        else:
                            with smtplib.SMTP(smtp_server, smtp_port) as server:
                                server.starttls()
                                server.login(mail_settings.get('senderEmail'), mail_settings.get('senderPassword'))
                                server.send_message(msg)

                        success_count += 1
                    except Exception as e:
                        failed_count += 1
                        failed_emails.append(email)
                        logger.error(f"메일 발송 실패 ({email}): {str(e)}")

                return {
                    "message": f"대량 메일 발송 완료",
                    "success_count": success_count,
                    "failed_count": failed_count,
                    "failed_emails": failed_emails
                }

            elif action == "get_templates":
                # 메일 템플릿 조회
                templates = await self.mongo_service.db.mail_templates.find({}).to_list(None)
                for template in templates:
                    template["_id"] = str(template["_id"])
                return {"templates": templates}

            elif action == "create_template":
                # 메일 템플릿 생성
                template_data = params.get("template_data", {})
                template_data["created_at"] = datetime.now()

                result = await self.mongo_service.db.mail_templates.insert_one(template_data)
                return {
                    "template_id": str(result.inserted_id),
                    "message": "메일 템플릿이 성공적으로 생성되었습니다."
                }

            elif action == "send_individual":
                # 개별 메일 발송
                applicant_id = params.get("applicant_id")
                mail_settings = params.get("mail_settings", {})
                custom_subject = params.get("subject", "안녕하세요")
                custom_content = params.get("content", "메일 내용을 입력해주세요.")

                if not applicant_id or not mail_settings:
                    return {"error": "지원자 ID와 메일 설정이 필요합니다."}

                # 지원자 정보 조회
                applicant = await self.mongo_service.db.applicants.find_one({"_id": ObjectId(applicant_id)})
                if not applicant:
                    return {"error": "지원자를 찾을 수 없습니다."}

                email = applicant.get('email')
                if not email:
                    return {"error": "지원자의 이메일이 없습니다."}

                # 메일 발송
                try:
                    msg = MIMEMultipart()
                    msg['From'] = f"{mail_settings.get('senderName', '')} <{mail_settings.get('senderEmail')}>"
                    msg['To'] = email
                    msg['Subject'] = custom_subject
                    msg.attach(MIMEText(custom_content, 'plain', 'utf-8'))

                    smtp_port = mail_settings.get('smtpPort', 587)
                    smtp_server = mail_settings.get('smtpServer', 'smtp.gmail.com')

                    if smtp_port == 465:
                        with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
                            server.login(mail_settings.get('senderEmail'), mail_settings.get('senderPassword'))
                            server.send_message(msg)
                    else:
                        with smtplib.SMTP(smtp_server, smtp_port) as server:
                            server.starttls()
                            server.login(mail_settings.get('senderEmail'), mail_settings.get('senderPassword'))
                            server.send_message(msg)

                    return {
                        "message": "메일이 성공적으로 발송되었습니다.",
                        "to": email,
                        "subject": custom_subject
                    }
                except Exception as e:
                    return {"error": f"메일 발송 실패: {str(e)}"}

            else:
                return {"status": "error", "message": f"알 수 없는 메일 액션: {action}"}

        except Exception as e:
            logger.error(f"❌ [메일툴] 처리 실패: {str(e)}")
            return {"status": "error", "message": f"메일 툴 처리 실패: {str(e)}"}

    async def ai_analysis_tool(self, action, **params):
        """AI 분석 툴 - 이력서 분석, 채용공고 최적화 등"""
        try:
            logger.info(f"🤖 [AI분석툴] 액션: {action}, 파라미터: {params}")

            if action == "analyze_resume":
                # 이력서 텍스트 분석
                resume_text = params.get("resume_text", "")
                if not resume_text:
                    return {"status": "error", "message": "이력서 텍스트가 필요합니다."}

                # 간단한 키워드 추출 (실제로는 OpenAI API 사용 권장)
                import re
                keywords = re.findall(r'\b\w+\b', resume_text.lower())
                keyword_count = {}
                for keyword in keywords:
                    if len(keyword) > 3:  # 3글자 이상만
                        keyword_count[keyword] = keyword_count.get(keyword, 0) + 1

                # 상위 키워드 추출
                top_keywords = sorted(keyword_count.items(), key=lambda x: x[1], reverse=True)[:10]

                return {
                    "status": "success",
                    "analysis": {
                        "total_words": len(keywords),
                        "unique_keywords": len(keyword_count),
                        "top_keywords": [{"word": word, "count": count} for word, count in top_keywords],
                        "estimated_experience": "3-5년" if len(keywords) > 500 else "1-3년"
                    }
                }

            elif action == "optimize_job_posting":
                # 채용공고 최적화
                job_title = params.get("job_title", "")
                job_description = params.get("job_description", "")

                if not job_title or not job_description:
                    return {"status": "error", "message": "채용공고 제목과 설명이 필요합니다."}

                # 간단한 최적화 제안
                suggestions = []
                if len(job_description) < 200:
                    suggestions.append("채용공고 설명을 더 자세히 작성하세요")
                if "경력" not in job_description:
                    suggestions.append("필요 경력을 명시하세요")
                if "급여" not in job_description:
                    suggestions.append("급여 정보를 포함하세요")

                return {
                    "status": "success",
                    "optimization": {
                        "current_length": len(job_description),
                        "suggestions": suggestions,
                        "score": max(0, 100 - len(suggestions) * 20)
                    }
                }

            elif action == "match_applicant":
                # 지원자 매칭도 분석
                job_requirements = params.get("job_requirements", [])
                applicant_skills = params.get("applicant_skills", [])

                if not job_requirements or not applicant_skills:
                    return {"status": "error", "message": "채용 요구사항과 지원자 스킬이 필요합니다."}

                # 매칭도 계산
                matched_skills = set(job_requirements) & set(applicant_skills)
                match_percentage = (len(matched_skills) / len(job_requirements)) * 100 if job_requirements else 0

                return {
                    "status": "success",
                    "matching": {
                        "matched_skills": list(matched_skills),
                        "missing_skills": list(set(job_requirements) - set(applicant_skills)),
                        "match_percentage": round(match_percentage, 2),
                        "recommendation": "매칭도가 높습니다" if match_percentage > 70 else "추가 스킬이 필요합니다"
                    }
                }

            else:
                return {"status": "error", "message": f"알 수 없는 AI 분석 액션: {action}"}

        except Exception as e:
            logger.error(f"❌ [AI분석툴] 처리 실패: {str(e)}")
            return {"status": "error", "message": f"AI 분석 툴 처리 실패: {str(e)}"}

    def get_tool_status(self):
        """툴 상태 및 성능 정보 반환"""
        try:
            tool_status = {}
            for tool_name in self.tools.keys():
                tool_status[tool_name] = {
                    "status": "healthy",
                    "error_count": self.error_stats.get(tool_name, 0),
                    "avg_response_time": self.performance_stats.get(tool_name, {}).get("avg_time", 0),
                    "last_used": self.performance_stats.get(tool_name, {}).get("last_used", "never")
                }

            return {
                "overall_status": "healthy",
                "total_tools": len(self.tools),
                "available_tools": list(self.tools.keys()),
                "tool_details": tool_status,
                "cache_size": len(self.cache),
                "total_errors": sum(self.error_stats.values())
            }
        except Exception as e:
            logger.error(f"툴 상태 조회 실패: {str(e)}")
            return {"status": "error", "message": f"툴 상태 조회 실패: {str(e)}"}

    def get_available_tools(self):
        return list(self.tools.keys())

    def execute(self, tool_name, action, **params):
        """동기 툴 실행 (호환성용)"""
        import asyncio
        return asyncio.run(self.execute_async(tool_name, action, **params))

    def get_error_statistics(self):
        return self.error_stats

    def get_performance_stats(self):
        return self.performance_stats

    def _update_performance_stats(self, tool_name, execution_time):
        """툴 성능 통계 업데이트"""
        if tool_name not in self.performance_stats:
            self.performance_stats[tool_name] = {
                "total_calls": 0,
                "total_time": 0,
                "avg_time": 0,
                "min_time": float('inf'),
                "max_time": 0,
                "last_used": None
            }

        stats = self.performance_stats[tool_name]
        stats["total_calls"] += 1
        stats["total_time"] += execution_time
        stats["avg_time"] = stats["total_time"] / stats["total_calls"]
        stats["min_time"] = min(stats["min_time"], execution_time)
        stats["max_time"] = max(stats["max_time"], execution_time)
        stats["last_used"] = datetime.now().isoformat()

    def _update_error_stats(self, tool_name, error_message):
        """툴 에러 통계 업데이트"""
        if tool_name not in self.error_stats:
            self.error_stats[tool_name] = 0
        self.error_stats[tool_name] += 1

    def clear_cache(self, tool_name=None):
        if tool_name:
            self.cache.pop(tool_name, None)
        else:
            self.cache.clear()

    def reset_performance_stats(self):
        self.performance_stats = {}

    def cleanup(self):
        """리소스 정리"""
        try:
            self.mongo_service.close()
            self.web_automation.close_driver()
        except Exception as e:
            print(f"리소스 정리 중 오류: {e}")

# 독립화된 에이전트 시스템 클래스
class AgentSystem:
    def __init__(self):
        self.tool_executor = ToolExecutor()

    async def process_request(self, user_input, conversation_history=None, session_id=None, mode="chat"):
        """사용자 요청을 처리하고 결과를 반환합니다."""
        try:
            # 로깅 추가
            logger.info(f"🔍 [의도분류] 사용자 입력: {user_input}")

            # 간단한 의도 분류
            intent = self.classify_intent(user_input)
            logger.info(f"🎯 [의도분류] 결과: {intent}")

            # 툴 사용이 필요한지 확인
            if intent.get("needs_tool"):
                logger.info(f"🛠️ [툴실행] 툴: {intent['tool']}, 액션: {intent['action']}")

                tool_result = await self.tool_executor.execute_async(
                    intent["tool"],
                    intent["action"],
                    **intent.get("params", {})
                )

                logger.info(f"✅ [툴실행] 결과: {tool_result}")

                return {
                    "success": True,
                    "message": f"툴 실행 결과: {tool_result}",
                    "mode": "tool",
                    "tool_used": intent["tool"],
                    "confidence": 0.8,
                    "session_id": session_id
                }
            # AI 채용공고 등록 액션 처리
            elif intent.get("action") == "openAIJobRegistration":
                logger.info("📝 [액션] AI 채용공고 등록 페이지 이동")
                return {
                    "success": True,
                    "message": "AI 채용공고 등록 페이지로 이동합니다.",
                    "mode": "action",
                    "action": "openAIJobRegistration",
                    "confidence": 0.9,
                    "session_id": session_id
                }
            else:
                logger.info("💬 [대화] 일반 대화 응답")
                return {
                    "success": True,
                    "message": "일반 대화 응답입니다.",
                    "mode": "chat",
                    "tool_used": None,
                    "confidence": 0.9,
                    "session_id": session_id
                }
        except Exception as e:
            logger.error(f"❌ [오류] 처리 중 오류 발생: {str(e)}")
            return {
                "success": False,
                "message": f"오류 발생: {str(e)}",
                "mode": "error",
                "tool_used": None,
                "confidence": 0.0,
                "session_id": session_id
            }

    def classify_intent(self, user_input):
        """간단한 의도 분류"""
        input_lower = user_input.lower()

        # GitHub 관련
        if any(word in input_lower for word in ["github", "깃허브", "레포", "커밋"]):
            if "사용자" in input_lower or "프로필" in input_lower:
                return {"needs_tool": True, "tool": "github", "action": "get_user_info", "params": {"username": "octocat"}}
            elif "레포" in input_lower or "저장소" in input_lower:
                return {"needs_tool": True, "tool": "github", "action": "get_repos", "params": {"username": "octocat"}}
            elif "커밋" in input_lower:
                return {"needs_tool": True, "tool": "github", "action": "get_commits", "params": {"username": "octocat"}}

        # MongoDB 관련
        elif any(word in input_lower for word in ["데이터베이스", "db", "문서", "조회"]):
            return {"needs_tool": True, "tool": "mongodb", "action": "find_documents", "params": {"collection": "applicants"}}

        # 채용공고 CRUD 관련
        elif any(word in input_lower for word in ["채용공고", "채용", "공고"]):
            if any(word in input_lower for word in ["등록", "작성", "만들기", "생성"]):
                return {"needs_tool": True, "tool": "job_posting", "action": "create", "params": {}}
            elif any(word in input_lower for word in ["수정", "편집", "변경", "업데이트"]):
                return {"needs_tool": True, "tool": "job_posting", "action": "update", "params": {}}
            elif any(word in input_lower for word in ["삭제", "제거"]):
                return {"needs_tool": True, "tool": "job_posting", "action": "delete", "params": {}}
            elif any(word in input_lower for word in ["발행", "공개", "게시"]):
                return {"needs_tool": True, "tool": "job_posting", "action": "publish", "params": {}}
            elif any(word in input_lower for word in ["보여", "조회", "목록", "리스트", "확인"]):
                return {"needs_tool": True, "tool": "job_posting", "action": "read", "params": {}}

        # 지원자 CRUD 관련
        elif any(word in input_lower for word in ["지원자", "지원", "이력서", "자소서", "applicant"]):
            if any(word in input_lower for word in ["등록", "작성", "만들기", "생성"]):
                return {"needs_tool": True, "tool": "applicant", "action": "create", "params": {}}
            elif any(word in input_lower for word in ["수정", "편집", "변경", "업데이트"]):
                return {"needs_tool": True, "tool": "applicant", "action": "update", "params": {}}
            elif any(word in input_lower for word in ["삭제", "제거"]):
                return {"needs_tool": True, "tool": "applicant", "action": "delete", "params": {}}
            elif any(word in input_lower for word in ["상태", "진행상황", "status"]):
                return {"needs_tool": True, "tool": "applicant", "action": "update_status", "params": {}}
            elif any(word in input_lower for word in ["통계", "통계정보", "stats"]):
                return {"needs_tool": True, "tool": "applicant", "action": "get_stats", "params": {}}
            elif any(word in input_lower for word in ["보여", "조회", "목록", "리스트", "확인"]):
                return {"needs_tool": True, "tool": "applicant", "action": "read", "params": {}}

        # 메일 관련
        elif any(word in input_lower for word in ["메일", "이메일", "email", "발송", "보내기"]):
            if any(word in input_lower for word in ["테스트", "test"]):
                return {"needs_tool": True, "tool": "mail", "action": "send_test", "params": {}}
            elif any(word in input_lower for word in ["일괄", "bulk", "대량"]):
                return {"needs_tool": True, "tool": "mail", "action": "send_bulk", "params": {}}
            elif any(word in input_lower for word in ["개별", "individual"]):
                return {"needs_tool": True, "tool": "mail", "action": "send_individual", "params": {}}
            elif any(word in input_lower for word in ["템플릿", "template"]):
                if any(word in input_lower for word in ["만들기", "생성", "create"]):
                    return {"needs_tool": True, "tool": "mail", "action": "create_template", "params": {}}
                else:
                    return {"needs_tool": True, "tool": "mail", "action": "get_templates", "params": {}}

        # 검색 관련
        elif any(word in input_lower for word in ["검색", "찾기", "정보"]):
            return {"needs_tool": True, "tool": "search", "action": "web_search", "params": {"query": user_input}}

        # AI 채용공고 등록 관련
        elif any(word in input_lower for word in ["채용공고", "채용", "공고", "등록", "작성", "만들기"]):
            if any(word in input_lower for word in ["ai", "도우미", "어시스턴트"]):
                return {"needs_tool": False, "action": "openAIJobRegistration"}

        # 웹 자동화 관련 (실제 클릭/입력 액션)
        elif any(word in input_lower for word in ["클릭", "버튼", "이동", "페이지", "열기"]):
            if any(word in input_lower for word in ["채용공고", "공고"]):
                return {
                    "needs_tool": True,
                    "tool": "web_automation",
                    "action": "navigate",
                    "params": {"page_path": "/job-posting"}
                }
            elif any(word in input_lower for word in ["지원자", "관리"]):
                return {
                    "needs_tool": True,
                    "tool": "web_automation",
                    "action": "navigate",
                    "params": {"page_path": "/applicants"}
                }
            elif any(word in input_lower for word in ["대시보드", "홈"]):
                return {
                    "needs_tool": True,
                    "tool": "web_automation",
                    "action": "navigate",
                    "params": {"page_path": "/dashboard"}
                }

        return {"needs_tool": False}

# 모니터링 시스템 (간단한 버전)
class MonitoringSystem:
    def __init__(self):
        self.metrics = {}

    def log_event(self, event_type, data):
        if event_type not in self.metrics:
            self.metrics[event_type] = []
        self.metrics[event_type].append({"timestamp": time.time(), "data": data})

    def get_metrics(self):
        return self.metrics

monitoring_system = MonitoringSystem()

router = APIRouter(tags=["pick-chatbot"])

# 로깅 설정 (안전한 로깅)
logger = logging.getLogger(__name__)

# 로거 핸들러가 없으면 추가
if not logger.handlers:
    import sys
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(name)s: %(message)s'))
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

class SessionManager:
    def __init__(self, expiry_seconds=1800, max_history=10):
        self.sessions = defaultdict(dict)
        self.expiry_seconds = expiry_seconds
        self.max_history = max_history

    def _current_time(self):
        return int(time.time())

    def create_session(self, session_id):
        current_time = self._current_time()
        self.sessions[session_id] = {
            "history": [],
            "last_activity": current_time,
            "created_at": current_time,
            "context": {
                "last_mentioned_user": None,
                "current_page": None,
                "last_tool_used": None,
                "extracted_entities": [],
                "conversation_topic": None
            }
        }
        try:
            print(f"🔑 [SESSION DEBUG] 새 세션 생성")
            print(f"    📝 세션 ID: {session_id}")
            print(f"    ⏰ 생성 시간: {current_time}")
            print(f"    📊 총 활성 세션 수: {len(self.sessions)}")
            logger.info(f"새 세션 생성: {session_id}")
        except (ValueError, OSError):
            pass  # detached buffer 오류 무시

    def add_message(self, session_id, role, content):
        if session_id not in self.sessions:
            print(f"🔑 [SESSION DEBUG] 세션이 없어서 새로 생성: {session_id}")
            self.create_session(session_id)

        session = self.sessions[session_id]
        old_history_count = len(session["history"])
        session["history"].append({"role": role, "content": content})

        # 오래된 기록은 잘라냄
        if len(session["history"]) > self.max_history:
            trimmed_count = len(session["history"]) - self.max_history
            session["history"] = session["history"][-self.max_history:]
            print(f"📚 [SESSION DEBUG] 히스토리 정리: {trimmed_count}개 메시지 제거")

        session["last_activity"] = self._current_time()

        try:
            print(f"💬 [SESSION DEBUG] 메시지 추가")
            print(f"    📝 세션 ID: {session_id}")
            print(f"    👤 역할: {role}")
            print(f"    📄 내용 길이: {len(content)}자")
            print(f"    📊 히스토리: {old_history_count} → {len(session['history'])}개")
            logger.info(f"세션 {session_id}에 메시지 추가: {role}")
        except (ValueError, OSError):
            pass  # detached buffer 오류 무시

    def get_history(self, session_id):
        if session_id in self.sessions:
            return self.sessions[session_id]["history"]
        return []

    def cleanup_sessions(self):
        now = self._current_time()
        expired = [
            sid for sid, data in self.sessions.items()
            if now - data["last_activity"] > self.expiry_seconds
        ]
        for sid in expired:
            del self.sessions[sid]
        if expired:
            try:
                logger.info(f"만료된 세션 {len(expired)}개 정리: {expired}")
            except (ValueError, OSError):
                pass  # detached buffer 오류 무시

    def update_context(self, session_id: str, context_update: Dict[str, Any]):
        """세션 컨텍스트 업데이트"""
        if session_id in self.sessions:
            session_context = self.sessions[session_id]["context"]
            for key, value in context_update.items():
                if value is not None:
                    session_context[key] = value
            try:
                logger.info(f"세션 {session_id} 컨텍스트 업데이트: {context_update}")
            except (ValueError, OSError):
                pass

    def get_context(self, session_id: str) -> Dict[str, Any]:
        """세션 컨텍스트 조회"""
        if session_id in self.sessions:
            return self.sessions[session_id].get("context", {})
        return {}

    def get_session_info(self, session_id):
        if session_id in self.sessions:
            session = self.sessions[session_id]
            return {
                "session_id": session_id,
                "message_count": len(session["history"]),
                "last_activity": session["last_activity"],
                "created_at": session.get("created_at", session["last_activity"]),
                "context": session.get("context", {})
            }
        return None

    def delete_session(self, session_id):
        if session_id in self.sessions:
            del self.sessions[session_id]
            try:
                logger.info(f"세션 삭제: {session_id}")
            except (ValueError, OSError):
                pass  # detached buffer 오류 무시
            return True
        return False

    def list_all_sessions(self):
        return [
            self.get_session_info(sid) for sid in self.sessions.keys()
        ]

# 세션 매니저 인스턴스 생성
session_manager = SessionManager(expiry_seconds=1800, max_history=10)

# 툴 실행기 인스턴스 생성
tool_executor = ToolExecutor()

class ChatMessage(BaseModel):
    message: str
    session_id: Optional[str] = None
    user_id: Optional[str] = None
    current_page: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    session_id: str
    timestamp: datetime
    suggestions: Optional[List[str]] = None
    quick_actions: Optional[List[Dict[str, Any]]] = None
    confidence: Optional[float] = None
    tool_results: Optional[Dict[str, Any]] = None
    error_info: Optional[Dict[str, Any]] = None
    page_action: Optional[Dict[str, Any]] = None


class ChatSession(BaseModel):
    session_id: str
    messages: List[Dict[str, Any]]
    created_at: datetime
    last_updated: datetime

def get_openai_service():
    """OpenAI 서비스 인스턴스 반환"""
    return LLMService()

def get_agent_system():
    """에이전트 시스템 인스턴스 반환"""
    return AgentSystem()

def create_session_id() -> str:
    """새로운 세션 ID 생성"""
    return str(uuid.uuid4())

def get_or_create_session(session_id: Optional[str] = None) -> str:
    """세션 ID를 가져오거나 새로 생성"""
    if not session_id:
        session_id = create_session_id()

    # 세션이 없으면 생성
    if session_id not in session_manager.sessions:
        session_manager.create_session(session_id)

    return session_id

def update_session(session_id: str, message: str, is_user: bool = True):
    """세션에 메시지 추가"""
    role = "user" if is_user else "assistant"
    session_manager.add_message(session_id, role, message)

def get_conversation_context(session_id: str) -> Dict[str, Any]:
    """대화 컨텍스트 생성 (개선된 버전)"""
    history = session_manager.get_history(session_id)
    if not history:
        return {
            "context_text": "",
            "context_summary": [],
            "recent_messages": [],
            "session_info": session_manager.get_session_info(session_id)
        }

    # 컨텍스트 텍스트 생성
    context_text = ""
    for msg in history:
        role = "사용자" if msg["role"] == "user" else "에이전트"
        context_text += f"{role}: {msg['content']}\n"

    # 최근 메시지 (최대 3개)
    recent_messages = history[-3:] if len(history) > 3 else history

    # 컨텍스트 요약 생성
    context_summary = []
    for msg in recent_messages:
        if msg.get("role") == "user":
            # 사용자 메시지에서 키워드 추출
            content = msg["content"].lower()
            keywords = []
            if any(word in content for word in ["github", "깃허브", "레포", "커밋"]):
                keywords.append("github")
            if any(word in content for word in ["데이터베이스", "db", "문서", "조회"]):
                keywords.append("database")
            if any(word in content for word in ["검색", "찾기", "정보"]):
                keywords.append("search")
            if any(word in content for word in ["채용", "공고", "지원자"]):
                keywords.append("recruitment")
            context_summary.extend(keywords)

    return {
        "context_text": context_text,
        "context_summary": list(set(context_summary)),  # 중복 제거
        "recent_messages": recent_messages,
        "session_info": session_manager.get_session_info(session_id)
    }

def create_error_aware_response(tool_results: Dict[str, Any], user_message: str) -> str:
    """에러 인식 응답 생성"""
    error_message = tool_results.get("error", "알 수 없는 오류")
    return f"죄송합니다. '{user_message}' 요청 처리 중 오류가 발생했습니다: {error_message}"

def extract_job_posting_info(user_input: str) -> Dict[str, Any]:
    """사용자 입력에서 채용공고 정보 추출"""
    input_lower = user_input.lower()
    extracted_data = {}

    # 직무 추출
    job_titles = {
        "프론트엔드": "프론트엔드 개발자",
        "백엔드": "백엔드 개발자",
        "풀스택": "풀스택 개발자",
        "데이터": "데이터 엔지니어",
        "ai": "AI 엔지니어",
        "머신러닝": "ML 엔지니어",
        "devops": "DevOps 엔지니어",
        "시스템": "시스템 엔지니어",
        "보안": "보안 엔지니어",
        "qa": "QA 엔지니어",
        "ui": "UI/UX 디자이너",
        "ux": "UI/UX 디자이너",
        "디자이너": "UI/UX 디자이너",
        "기획": "서비스 기획자",
        "pm": "프로덕트 매니저",
        "마케팅": "마케팅 매니저",
        "영업": "영업 매니저",
        "인사": "인사 담당자",
        "회계": "회계 담당자"
    }

    for keyword, title in job_titles.items():
        if keyword in input_lower:
            extracted_data["position"] = title
            break

    # 고용형태 추출
    employment_types = {
        "정규직": "fulltime",
        "계약직": "contract",
        "인턴": "intern",
        "신입": "entry",
        "경력": "experienced"
    }

    for keyword, emp_type in employment_types.items():
        if keyword in input_lower:
            extracted_data["employment_type"] = emp_type
            break

    # 근무지 추출 (기본값)
    if "원격" in input_lower or "재택" in input_lower:
        extracted_data["location"] = "원격근무"
    elif "서울" in input_lower:
        extracted_data["location"] = "서울"
    elif "부산" in input_lower:
        extracted_data["location"] = "부산"
    else:
        extracted_data["location"] = "서울"  # 기본값

    # 모집인원 추출
    import re
    headcount_match = re.search(r'(\d+)명', input_lower)
    if headcount_match:
        extracted_data["headcount"] = int(headcount_match.group(1))
    else:
        extracted_data["headcount"] = 0  # 기본값을 0명으로 설정

    # 급여 추출 (만원단위 표시)
    salary_match = re.search(r'(\d+)만원', input_lower)
    if salary_match:
        salary_amount = int(salary_match.group(1))
        # 만원단위로 표시 (천단위 쉼표 없이)
        formatted_salary = f"{salary_amount}만원"
        extracted_data["salary"] = formatted_salary
    else:
        extracted_data["salary"] = "협의"  # 기본값을 협의로 변경

    # 경력 연차 추출 및 확인
    experience_match = re.search(r'(\d+)년차', input_lower)
    if experience_match:
        experience_years = int(experience_match.group(1))
        extracted_data["experience_years"] = experience_years
        extracted_data["experience"] = f"{experience_years}년차"
    elif "신입" in input_lower:
        extracted_data["experience"] = "신입"
        extracted_data["experience_years"] = 0
    elif "경력" in input_lower:
        extracted_data["experience"] = "경력"
        extracted_data["experience_years"] = None  # 구체적 연차 미지정

    # 회사명 (기본값)
    extracted_data["company"] = "우리 회사"

    # 제목 생성
    if "position" in extracted_data:
        extracted_data["title"] = f"{extracted_data['position']} 채용"

    # 모집기간 (기본값: 30일)
    extracted_data["recruitment_period"] = 30

    return extracted_data

def extract_context_keywords(message: str) -> List[str]:
    """메시지에서 컨텍스트 키워드 추출"""
    keywords = []
    message_lower = message.lower()

    # GitHub 관련 키워드
    if any(word in message_lower for word in ["github", "깃허브", "레포", "repo", "커밋", "commit"]):
        keywords.append("GitHub")

    # 데이터베이스 관련 키워드
    if any(word in message_lower for word in ["데이터베이스", "db", "mongodb", "컬렉션", "collection"]):
        keywords.append("데이터베이스")

    # 검색 관련 키워드
    if any(word in message_lower for word in ["검색", "search", "찾기", "find"]):
        keywords.append("검색")

    # 채용 관련 키워드
    if any(word in message_lower for word in ["채용", "지원자", "면접", "공고", "포트폴리오", "자기소개서"]):
        keywords.append("채용관리")

    return keywords

async def generate_search_based_response(
    user_message: str,
    openai_service,
    tool_executor
) -> Optional[str]:
    """검색 결과를 바탕으로 LLM이 자연스러운 응답 생성"""

    # 검색 키워드 추출 (임시로 사용자 메시지에서 키워드 추출)
    search_keywords = user_message.split()[:5]  # 처음 5개 단어를 키워드로 사용
    if not search_keywords:
        return None

    try:
        # 웹 검색 실행
        search_result = await tool_executor.execute_async(
            "search",
            "web_search",
            query=search_keywords,
            num_results=5
        )

        if search_result.get("status") == "success":
            search_data = search_result.get("data", {})
            results = search_data.get("results", [])

            if results:
                # 검색 결과를 요약하여 LLM에게 제공
                search_summary = "\n".join([
                    f"- {result['title']}: {result['snippet']}"
                    for result in results[:3]  # 상위 3개 결과만 사용
                ])

                # LLM에게 검색 결과를 바탕으로 답변 생성 요청
                response_prompt = f"""
사용자가 "{user_message}"라고 질문했습니다.

웹에서 검색한 관련 정보:
{search_summary}

위의 검색 결과를 바탕으로 사용자의 질문에 대해 정확하고 도움이 되는 답변을 작성해주세요.
답변은 다음과 같은 형식으로 구성해주세요:

1. 핵심 정보 요약
2. 상세 설명
3. 추가 도움이 될 만한 제안

답변은 친근하고 전문적인 톤으로 작성해주세요.
"""

                llm_response = await openai_service.chat_completion([
                    {"role": "system", "content": "당신은 웹 검색 결과를 바탕으로 정확하고 도움이 되는 답변을 제공하는 AI입니다."},
                    {"role": "user", "content": response_prompt}
                ])

                return llm_response

    except Exception as e:
        print(f"🔍 [DEBUG] 검색 기반 응답 생성 오류: {str(e)}")
        return None

    return None



async def detect_tool_usage_with_ai(
    user_message: str,
    openai_service,
    context_keywords: List[str] = None,
    recent_messages: List[Dict[str, Any]] = None,
    session_context: Dict[str, Any] = None
) -> Optional[Dict[str, Any]]:
    """AI를 사용하여 사용자 메시지에서 툴 사용 의도 감지 (순수 AI 기반)"""

    # 컨텍스트 정보 구성
    context_info = ""

    # 세션 컨텍스트 활용
    if session_context:
        if session_context.get("last_mentioned_user"):
            context_info += f"\n이전에 언급된 사용자: {session_context['last_mentioned_user']}"
        if session_context.get("current_page"):
            context_info += f"\n현재 페이지: {session_context['current_page']}"
        if session_context.get("last_tool_used"):
            context_info += f"\n마지막 사용 툴: {session_context['last_tool_used']}"

    # 이전 대화 컨텍스트
    if recent_messages:
        recent_context = "\n".join([
            f"{msg.get('role', 'unknown')}: {msg.get('content', '')[:150]}"
            for msg in recent_messages[-3:]  # 최근 3개 메시지
        ])
        context_info += f"\n최근 대화:\n{recent_context}"

    # 순수 AI 기반 툴 선택 프롬프트
    tool_detection_prompt = f"""
당신은 채용 관리 시스템의 지능형 어시스턴트입니다. 사용자의 요청을 이해하고 적절한 도구를 선택해주세요.

시스템 컨텍스트:
- 이 시스템은 채용 공고 관리, 지원자 관리, 포트폴리오 분석 등을 지원합니다
- 포트폴리오 분석은 현재 GitHub 기반으로 이루어집니다
- 사용자는 자연어로 다양한 요청을 할 수 있습니다

사용 가능한 도구들:
1. github: GitHub 관련 정보 조회 및 분석
   - get_user_info: 사용자 프로필 정보
   - get_repos: 레포지토리 목록
   - get_commits: 커밋 내역
   - search_repos: 레포지토리 검색

2. mongodb: 데이터베이스 조회
   - find_documents: 문서 조회
   - count_documents: 문서 개수 확인

3. search: 웹 검색
   - web_search: 일반 웹 검색
   - news_search: 뉴스 검색
   - image_search: 이미지 검색

{context_info}

사용자 요청: "{user_message}"

사용자의 의도를 파악하여 다음 중 하나로 응답해주세요:

1. 도구가 필요한 경우:
   - 사용자의 의도를 분석하여 가장 적절한 도구와 액션을 선택
   - 컨텍스트에서 필요한 정보(사용자명, 컬렉션명 등)를 추출
   - 정보가 부족하면 합리적인 추론을 통해 보완

2. 도구가 필요하지 않은 경우:
   - 일반적인 대화나 질문인 경우 null 반환

JSON 형식으로만 응답:
- 도구 불필요: null
- 도구 필요: {{"tool": "도구명", "action": "액션명", "params": {{"매개변수": "값"}}}}
"""

    try:
        # AI에게 툴 선택 요청
        response = await openai_service.chat_completion([
            {"role": "system", "content": "당신은 사용자 메시지를 분석하여 적절한 툴을 선택하는 AI입니다. JSON 형식으로만 응답해주세요."},
            {"role": "user", "content": tool_detection_prompt}
        ])

        print(f"🔍 [DEBUG] AI 툴 감지 응답: {response}")

        # JSON 파싱 시도
        import json
        import re

        # JSON 부분만 추출
        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            tool_usage = json.loads(json_match.group())

            # 사용자명 추출이 필요한 경우 (AI 기반)
            if tool_usage and tool_usage.get("tool") == "github":
                if "username" not in tool_usage.get("params", {}) or not tool_usage["params"]["username"] or tool_usage["params"]["username"] == "사용자명":
                    username = await extract_username_with_ai(user_message, openai_service, session_context)
                    tool_usage["params"]["username"] = username

            return tool_usage
        else:
            print(f"🔍 [DEBUG] AI 응답에서 JSON을 찾을 수 없음: {response}")
            # AI가 JSON을 반환하지 않았을 때 재시도
            return await retry_tool_detection_with_simpler_prompt(user_message, openai_service, context_info)

    except Exception as e:
        print(f"🔍 [DEBUG] AI 툴 감지 오류: {str(e)}")
        # AI 실패 시 간단한 프롬프트로 재시도
        return await retry_tool_detection_with_simpler_prompt(user_message, openai_service, context_info)

async def retry_tool_detection_with_simpler_prompt(
    user_message: str,
    openai_service,
    context_info: str
) -> Optional[Dict[str, Any]]:
    """AI 툴 감지 실패 시 더 간단한 프롬프트로 재시도"""

    simple_prompt = f"""
사용자 요청을 분석하여 필요한 도구를 선택해주세요.

도구 목록:
- github: GitHub/포트폴리오 관련
- mongodb: 데이터베이스 관련
- search: 웹검색 관련
- null: 도구 불필요

{context_info}

요청: "{user_message}"

JSON만 응답: {{"tool": "도구명", "action": "액션명", "params": {{"key": "value"}}}} 또는 null
"""

    try:
        response = await openai_service.chat_completion([
            {"role": "user", "content": simple_prompt}
        ])

        import json
        import re

        # JSON 추출 시도
        json_match = re.search(r'\{.*\}|null', response, re.DOTALL)
        if json_match:
            result = json_match.group()
            if result == "null":
                return None
            return json.loads(result)

        return None

    except Exception as e:
        print(f"🔍 [DEBUG] 간단한 프롬프트로도 실패: {str(e)}")
        return None

async def extract_username_with_ai(
    message: str,
    openai_service,
    session_context: Dict[str, Any] = None
) -> str:
    """AI를 사용하여 메시지에서 사용자명 추출"""

    context_info = ""
    if session_context and session_context.get("last_mentioned_user"):
        context_info = f"이전에 언급된 사용자: {session_context['last_mentioned_user']}"

    prompt = f"""
다음 메시지에서 GitHub 사용자명을 추출해주세요.

{context_info}

메시지: "{message}"

GitHub 사용자명만 추출하여 응답해주세요.
- 사용자명이 명시되어 있으면 그것을 반환
- 명시되지 않았지만 이전 컨텍스트에 있으면 그것을 사용
- 둘 다 없으면 "UNKNOWN" 반환

사용자명만 응답:
"""

    try:
        response = await openai_service.chat_completion([
            {"role": "user", "content": prompt}
        ])

        username = response.strip()
        if username and username != "UNKNOWN":
            return username

    except Exception as e:
        print(f"🔍 [DEBUG] AI 사용자명 추출 실패: {str(e)}")

    # AI 실패 시 간단한 정규식으로 폴백
    import re
    patterns = [
        r'([a-zA-Z0-9_-]+)\s*(?:의\s*)?(?:github|포트폴리오|프로젝트|분석)',
        r'(?:사용자|user|아이디|id)\s*([a-zA-Z0-9_-]+)',
        r'([a-zA-Z0-9_-]{3,})'  # 3자 이상의 영숫자 조합
    ]

    for pattern in patterns:
        match = re.search(pattern, message, re.IGNORECASE)
        if match:
            return match.group(1)

    # 세션 컨텍스트에서 마지막 사용자명 사용
    if session_context and session_context.get("last_mentioned_user"):
        return session_context["last_mentioned_user"]

    return "UNKNOWN"

async def determine_target_page_with_ai(
    user_message: str,
    tool_name: str,
    action_type: str,
    tool_results: Dict[str, Any],
    openai_service,
    session_context: Dict[str, Any] = None
) -> Optional[Dict[str, Any]]:
    """AI를 사용하여 사용자 요청에 가장 적합한 페이지를 동적으로 결정"""

    # 사용 가능한 페이지들과 각각의 용도
    available_pages = {
        "/dashboard": "전체 시스템 개요, 통계, 뉴스 및 일반 정보 확인",
        "/applicants": "지원자 관리, 지원자 정보 조회 및 관리",
        "/github-test": "GitHub 포트폴리오 분석, 개발자 정보 확인",
        "/job-posting": "채용공고 등록 및 관리",

        "/resume": "이력서 관리 및 분석",
        "/portfolio": "포트폴리오 종합 분석",
        "/settings": "시스템 설정 및 환경 구성"
    }

    context_info = ""
    if session_context:
        if session_context.get("current_page"):
            context_info += f"\n현재 페이지: {session_context['current_page']}"
        if session_context.get("last_mentioned_user"):
            context_info += f"\n언급된 사용자: {session_context['last_mentioned_user']}"

    prompt = f"""
사용자의 요청과 도구 실행 결과를 바탕으로 가장 적합한 페이지를 선택해주세요.

사용자 요청: "{user_message}"
실행된 도구: {tool_name} - {action_type}
도구 실행 결과: {str(tool_results)[:200]}...

{context_info}

사용 가능한 페이지들:
{chr(10).join([f"- {page}: {desc}" for page, desc in available_pages.items()])}

다음 기준으로 페이지를 선택해주세요:
1. 사용자의 의도와 가장 관련성이 높은 페이지
2. 실행된 도구의 결과를 가장 잘 활용할 수 있는 페이지
3. 사용자가 다음에 할 가능성이 높은 작업을 지원하는 페이지

JSON 형식으로 응답:
{{"target": "/페이지경로", "message": "사용자에게 보여줄 안내 메시지", "auto_action": "자동 실행할 액션 (선택사항)"}}

페이지가 필요하지 않으면: null
"""

    try:
        response = await openai_service.chat_completion([
            {"role": "user", "content": prompt}
        ])

        import json
        import re

        json_match = re.search(r'\{.*\}|null', response, re.DOTALL)
        if json_match:
            result = json_match.group()
            if result == "null":
                return None

            page_info = json.loads(result)
            return {
                "action": "navigate",
                "target": page_info["target"],
                "message": f"🎯 {page_info['message']}",
                "auto_action": page_info.get("auto_action")
            }

        return None

    except Exception as e:
        print(f"🔍 [DEBUG] AI 페이지 결정 실패: {str(e)}")
        # 폴백: 도구 기반 기본 페이지 선택
        if tool_name == "github":
            return {
                "action": "navigate",
                "target": "/github-test",
                "message": "🎯 GitHub 관련 정보를 확인할 수 있는 페이지로 이동합니다."
            }
        elif tool_name == "mongodb":
            return {
                "action": "navigate",
                "target": "/applicants",
                "message": "🎯 데이터베이스 정보를 확인할 수 있는 페이지로 이동합니다."
            }
        elif tool_name == "search":
            return {
                "action": "navigate",
                "target": "/dashboard",
                "message": "🎯 검색 결과를 확인할 수 있는 페이지로 이동합니다."
            }

        return None

async def update_conversation_context_with_ai(
    session_id: str,
    user_message: str,
    ai_response: str,
    tool_usage: Dict[str, Any],
    openai_service,
    session_manager
):
    """AI를 사용하여 대화 컨텍스트를 지능적으로 업데이트"""

    current_context = session_manager.get_context(session_id)

    prompt = f"""
다음 대화를 분석하여 중요한 컨텍스트 정보를 추출해주세요.

현재 컨텍스트: {current_context}
사용자 메시지: "{user_message}"
AI 응답: "{ai_response[:200]}..."
사용된 도구: {tool_usage if tool_usage else "없음"}

다음 정보를 추출해주세요:
1. 언급된 사용자명 (GitHub 사용자명 등)
2. 대화의 주요 주제
3. 추출된 개체명들 (회사명, 기술명 등)

JSON 형식으로 응답:
{{
  "last_mentioned_user": "사용자명 또는 null",
  "conversation_topic": "주요 주제",
  "extracted_entities": ["개체1", "개체2"]
}}
"""

    try:
        response = await openai_service.chat_completion([
            {"role": "user", "content": prompt}
        ])

        import json
        import re

        json_match = re.search(r'\{.*\}', response, re.DOTALL)
        if json_match:
            context_update = json.loads(json_match.group())

            # 도구 사용 정보 추가
            if tool_usage:
                context_update["last_tool_used"] = tool_usage["tool"]

            # 컨텍스트 업데이트
            session_manager.update_context(session_id, context_update)
            print(f"🔍 [DEBUG] AI 기반 컨텍스트 업데이트: {context_update}")

    except Exception as e:
        print(f"🔍 [DEBUG] AI 컨텍스트 업데이트 실패: {str(e)}")
        # 폴백: 기본 컨텍스트 업데이트
        if tool_usage:
            session_manager.update_context(session_id, {"last_tool_used": tool_usage["tool"]})

def create_error_aware_response(tool_results: Dict[str, Any], user_message: str) -> str:
    """
    에러 정보를 포함한 사용자 친화적 응답 생성

    Args:
        tool_results: 툴 실행 결과
        user_message: 사용자 메시지

    Returns:
        사용자 친화적 응답 메시지
    """
    if not tool_results:
        return "죄송합니다. 요청을 처리하는 중 문제가 발생했습니다."

    result = tool_results.get("result", {})
    status = result.get("status")

    if status == "success":
        # 성공한 경우
        data = result.get("data", {})

        # 대체 툴을 사용한 경우
        if result.get("fallback_used"):
            original_error = result.get("original_error", {})
            return f"원래 요청한 방법으로는 정보를 가져올 수 없어서 다른 방법으로 찾아보았습니다. {format_tool_data(data)}"

        # 정상적으로 성공한 경우
        return f"요청하신 정보를 찾았습니다! {format_tool_data(data)}"

    elif status == "error":
        # 에러가 발생한 경우
        error_message = result.get("message", "알 수 없는 오류가 발생했습니다.")
        fallback_suggestion = result.get("fallback_suggestion")

        response = f"죄송합니다. {error_message}"

        if fallback_suggestion:
            suggestion = fallback_suggestion.get("suggestion", "")
            response += f" {suggestion}"

        return response

    return "요청을 처리하는 중 문제가 발생했습니다."

def format_tool_data(data: Dict[str, Any]) -> str:
    """툴 데이터를 사용자 친화적으로 포맷팅"""
    if not data:
        return "죄송합니다. 요청하신 정보를 찾을 수 없습니다."

    # GitHub 사용자 정보
    if "username" in data and "public_repos" in data:
        username = data.get("username", "알 수 없음")
        public_repos = data.get("public_repos", 0)
        followers = data.get("followers", 0)
        following = data.get("following", 0)
        bio = data.get("bio", "")

        result = f"🎯 **{username}님의 GitHub 프로필**\n\n"
        result += f"📊 **활동 현황**\n"
        result += f"• 공개 레포지토리: {public_repos}개\n"
        result += f"• 팔로워: {followers}명\n"
        result += f"• 팔로잉: {following}명\n"

        if bio:
            result += f"\n💬 **자기소개**\n{bio}"

        return result

    # GitHub 레포지토리 목록
    if "repos" in data:
        repos = data["repos"]
        if repos:
            result = f"📁 **{len(repos)}개의 레포지토리 발견!**\n\n"

            # 주요 레포지토리 정보 추가
            top_repos = repos[:5]  # 상위 5개
            result += f"🌟 **주요 프로젝트**\n\n"
            for i, repo in enumerate(top_repos, 1):
                name = repo.get("name", "")
                language = repo.get("language", "")
                description = repo.get("description", "")
                stars = repo.get("stargazers_count", 0)

                result += f"{i}. **{name}**"
                # 언어 정보 제거
                # if language:
                #     result += f" ({language})"
                if stars > 0:
                    result += f" ⭐ {stars}"
                result += "\n"

                if description:
                    result += f"   └ {description[:80]}{'...' if len(description) > 80 else ''}\n"

                # 각 프로젝트 사이에 줄바꿈 추가
                result += "\n"

            # 기술 스택 요약 제거 (중복 방지)
            # languages = {}
            # for repo in repos:
            #     lang = repo.get("language")
            #     if lang:
            #         languages[lang] = languages.get(lang, 0) + 1

            # if languages:
            #     top_languages = sorted(languages.items(), key=lambda x: x[1], reverse=True)[:3]
            #     result += f"\n💻 **기술 스택 요약**\n"
            #     lang_summary = []
            #     for lang, count in top_languages:
            #         lang_summary.append(f"{lang}({count}개)" if count > 1 else f"{lang}({count}개)")
            #     result += f"• {', '.join(lang_summary)}"

            return result
        else:
            return "😔 아직 레포지토리가 없네요. 첫 프로젝트를 시작해보세요!"

    # GitHub 커밋 정보
    if "commits" in data:
        commits = data["commits"]
        if commits:
            result = f"📝 **최근 {len(commits)}개의 커밋 활동**\n\n"

            # 최근 커밋 정보
            latest_commit = commits[0]
            commit_message = latest_commit.get("commit", {}).get("message", "제목 없음")
            author = latest_commit.get("commit", {}).get("author", {}).get("name", "알 수 없음")
            date = latest_commit.get("commit", {}).get("author", {}).get("date", "")

            result += f"🔥 **최신 커밋**\n"
            result += f"• 메시지: {commit_message}\n"
            result += f"• 작성자: {author}\n"

            if date:
                from datetime import datetime
                try:
                    commit_date = datetime.fromisoformat(date.replace('Z', '+00:00'))
                    result += f"• 날짜: {commit_date.strftime('%Y년 %m월 %d일')}\n"
                except:
                    pass

            return result
        else:
            return "📅 아직 커밋 내역이 없습니다. 첫 커밋을 작성해보세요!"

    # MongoDB 문서
    if "documents" in data:
        documents = data["documents"]
        count = len(documents)
        if count > 0:
            result = f"📋 데이터베이스에서 {count}개의 문서를 찾았습니다.\n\n"

            # 채용공고인 경우 상세 정보 표시
            if documents and "title" in documents[0]:
                result += "📋 **채용공고 목록**\n\n"
                for i, job in enumerate(documents[:5], 1):  # 상위 5개만
                    title = job.get("title", "제목 없음")
                    company = job.get("company", "회사명 없음")
                    position = job.get("position", "직무 없음")
                    status = job.get("status", "상태 없음")
                    created_at = job.get("created_at", "")

                    result += f"{i}. **{title}**\n"
                    result += f"   • 회사: {company}\n"
                    result += f"   • 직무: {position}\n"
                    result += f"   • 상태: {status}\n"
                    if created_at:
                        result += f"   • 등록일: {created_at[:10]}\n"
                    result += "\n"
            else:
                result += "📋 **문서 목록**\n\n"
                for i, doc in enumerate(documents[:5], 1):
                    result += f"{i}. {str(doc)[:100]}...\n\n"

            return result
        else:
            return "📋 데이터베이스에 해당하는 문서가 없습니다."

    # 검색 결과
    if "results" in data:
        results = data["results"]
        if results:
            result = f"🔍 **검색 결과 {len(results)}개 발견!**\n\n"

            # 첫 번째 결과 정보 추가
            first_result = results[0]
            title = first_result.get("title", "제목 없음")
            snippet = first_result.get("snippet", "")[:120]  # 120자로 제한
            url = first_result.get("link", "")

            result += f"📌 **주요 결과**\n"
            result += f"• 제목: {title}\n"
            if snippet:
                result += f"• 요약: {snippet}...\n"
            if url:
                result += f"• 링크: {url}\n"

            return result
        else:
            return "🔍 검색 결과를 찾을 수 없습니다. 다른 키워드로 검색해보세요."

    # 웹 자동화 결과
    if "url" in data:
        return f"🌐 페이지 이동 완료: {data['url']}"

    if "clicked" in data:
        return f"🖱️ 클릭 완료: {data['clicked']}"

    if "input" in data:
        return f"⌨️ 입력 완료: {data['input']}"

    if "title" in data and "url" in data:
        return f"📄 페이지 정보: {data['title']} ({data['url']})"

    # 기타 데이터
    return "✅ 요청하신 작업이 성공적으로 완료되었습니다!"

@router.post("/chat", response_model=ChatResponse)
async def chat_with_help_bot(
    chat_message: ChatMessage,
    openai_service: LLMService = Depends(get_openai_service),
    agent_system: AgentSystem = Depends(get_agent_system)
):
    """
    에이전트과 대화
    """
    import time
    start_time = time.time()

    # ------------------------------------------------------------------
    # 🔧 변수를 미리 초기화해서 UnboundLocalError 방지
    # ------------------------------------------------------------------
    tool_usage = None
    tool_results = None
    error_info = None
    session_context = None
    context_keywords = []
    recent_messages = []
    conversation_context = {}
    parallel_result = None

    print(f"\n{'='*80}")
    print(f"🚀 [PICK-TALK DEBUG] 채팅 요청 시작")
    print(f"📝 세션 ID: {chat_message.session_id}")
    print(f"💬 사용자 메시지: '{chat_message.message}'")
    print(f"📄 현재 페이지: {chat_message.current_page}")
    print(f"🕐 요청 시각: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*80}")

    try:
        # 세션 정리 (만료된 세션 삭제)
        cleanup_start = time.time()
        session_manager.cleanup_sessions()
        cleanup_time = time.time() - cleanup_start
        print(f"🧹 [세션 정리] 완료 (소요시간: {cleanup_time:.3f}초)")

        # 세션 관리
        session_start = time.time()
        session_id = get_or_create_session(chat_message.session_id)
        session_time = time.time() - session_start
        print(f"🔑 [세션 관리] 세션 ID: {session_id} (소요시간: {session_time:.3f}초)")

        # 사용자 메시지 저장
        save_start = time.time()
        update_session(session_id, chat_message.message, is_user=True)
        save_time = time.time() - save_start
        print(f"💾 [메시지 저장] 사용자 메시지 저장 완료 (소요시간: {save_time:.3f}초)")

        # 대화 컨텍스트 가져오기 (개선된 버전)
        context_start = time.time()
        conversation_context = get_conversation_context(session_id)
        context_time = time.time() - context_start
        context_summary = conversation_context.get('context_summary', [])
        recent_count = len(conversation_context.get('recent_messages', []))
        print(f"🧠 [컨텍스트] 컨텍스트 로드 완료 (소요시간: {context_time:.3f}초)")
        print(f"    📋 컨텍스트 키워드: {context_summary}")
        print(f"    📜 최근 메시지 수: {recent_count}개")

        # 컨텍스트 기반 툴 감지 개선
        context_keywords = conversation_context.get('context_summary', [])
        recent_messages = conversation_context.get('recent_messages', [])

        # 상세 컨텍스트 디버깅
        if recent_count > 0:
            print(f"    🔍 최근 대화 내용:")
            for i, msg in enumerate(recent_messages[-3:], 1):  # 최근 3개만 표시
                role = "👤 사용자" if msg.get('role') == 'user' else "🤖 어시스턴트"
                content = msg.get('content', '')[:50] + ('...' if len(msg.get('content', '')) > 50 else '')
                print(f"      {i}. {role}: {content}")

        # 컨텍스트 품질 평가
        context_quality = "높음" if recent_count >= 3 else "보통" if recent_count >= 1 else "낮음"
        print(f"    📊 컨텍스트 품질: {context_quality}")

        # 기존 픽톡 툴 사용 감지 (병렬 채용공고 에이전트 비활성화)
        tool_usage = await detect_tool_usage_with_ai(
            chat_message.message,
            openai_service,
            context_keywords=context_keywords,
            recent_messages=recent_messages,
            session_context=session_context
        )
        print(f"🔍 [DEBUG] 기존 픽톡 툴 사용 감지 결과: {tool_usage}")



        # 툴 실행 로직
        if tool_usage and tool_usage is not None and tool_usage.get('tool') and tool_usage.get('tool') != 'null':
            print(f"🔍 [DEBUG] 툴 사용 감지됨: {tool_usage}")
            try:
                logger.info(f"툴 사용 감지: {tool_usage}")
            except (ValueError, OSError):
                pass  # detached buffer 오류 무시

            try:
                print(f"🔍 [DEBUG] 툴 실행 시작 - 툴: {tool_usage['tool']}, 액션: {tool_usage['action']}, 파라미터: {tool_usage['params']}")

                # 비동기 툴 실행 (성능 최적화)
                result = await tool_executor.execute_async(
                    tool_usage["tool"],
                    tool_usage["action"],
                    session_id=session_id,  # 세션 ID 추가
                    **tool_usage["params"]
                )

                print(f"🔍 [DEBUG] 툴 실행 결과: {result}")

                tool_results = {
                    "tool": tool_usage["tool"],
                    "action": tool_usage["action"],
                    "result": result
                }

                # 에러 정보 추출
                if result.get("status") == "error":
                    print(f"🔍 [DEBUG] 툴 실행 에러: {result.get('message')}")
                    error_info = {
                        "tool": tool_usage["tool"],
                        "action": tool_usage["action"],
                        "error_message": result.get("message"),
                        "retryable": result.get("retryable", False),
                        "fallback_suggestion": result.get("fallback_suggestion")
                    }
                else:
                    print(f"🔍 [DEBUG] 툴 실행 성공: {result.get('status')}")

                    # 성공적인 툴 실행 후 컨텍스트 업데이트
                    context_update = {
                        "last_tool_used": tool_usage["tool"]
                    }

                    # GitHub 툴 사용 시 사용자명 컨텍스트 업데이트
                    if tool_usage["tool"] == "github" and "username" in tool_usage["params"]:
                        username = tool_usage["params"]["username"]
                        if username != "UNKNOWN":
                            context_update["last_mentioned_user"] = username

                    session_manager.update_context(session_id, context_update)

                try:
                    logger.info(f"툴 실행 완료: {result['status']}")
                except (ValueError, OSError):
                    pass  # detached buffer 오류 무시

            except Exception as e:
                print(f"🔍 [DEBUG] 툴 실행 예외 발생: {str(e)}")
                logger.error(f"툴 실행 실패: {str(e)}")
                tool_results = {
                    "tool": tool_usage["tool"],
                    "action": tool_usage["action"],
                    "error": str(e)
                }
                error_info = {
                    "tool": tool_usage["tool"],
                    "action": tool_usage["action"],
                    "error_message": str(e),
                    "retryable": True
                }
        else:
            print(f"🔍 [DEBUG] 유효하지 않은 툴 사용 감지 - 툴: {tool_usage}")
            tool_results = None
            error_info = None

        # 채용공고 등록 확인 처리 (ai-job-registration 페이지에서만) - 의도 분류보다 먼저 실행
        if (chat_message.message in ["등록하기", "확인", "네", "등록", "등록해줘", "이대로 등록해줘"] and
            chat_message.current_page == "ai-job-registration"):
            session_context = session_manager.get_context(session_id)
            print(f"🔍 [등록처리] 세션 컨텍스트 확인:")
            print(f"    세션 컨텍스트 존재: {bool(session_context)}")
            if session_context:
                print(f"    last_action: {session_context.get('last_action')}")
                print(f"    pending_job_posting 존재: {bool(session_context.get('pending_job_posting'))}")
                print(f"    conversation_topic: {session_context.get('conversation_topic')}")

            if (session_context and
                session_context.get("last_action") == "job_posting_preview" and
                session_context.get("pending_job_posting")):

                try:
                    # 채용공고 등록 실행 (기존 픽톡 툴 사용)
                    job_posting_data = session_context["pending_job_posting"]
                    registration_result = await self.job_posting_tool("create", job_data=job_posting_data)

                    if registration_result.get("job_id"):
                        response_message = f"🎉 채용공고가 성공적으로 등록되었습니다!\n\n"
                        response_message += f"**등록 ID:** {registration_result['job_id']}\n"
                        response_message += f"**제목:** {job_posting_data['title']}\n"
                        response_message += "이제 지원자들이 이 공고를 확인할 수 있습니다!"

                        # 세션 컨텍스트 정리
                        session_manager.update_context(session_id, {
                            "last_action": "job_posting_registered",
                            "pending_job_posting": None,
                            "conversation_topic": "채용공고 등록 완료"
                        })

                        # AI 응답 저장
                        update_session(session_id, response_message, is_user=False)

                        # 추천 질문 생성
                        suggested_questions = [
                            "등록된 채용공고를 확인하고 싶어요",
                            "다른 채용공고도 만들어주세요",
                            "지원자 관리는 어떻게 하나요?"
                        ]

                        # 빠른 액션 생성
                        quick_actions = [
                            {"title": "등록된 채용공고", "action": "navigate", "target": "/job-posting", "icon": "📋"},
                            {"title": "지원자 관리", "action": "navigate", "target": "/applicants", "icon": "👥"},
                            {"title": "대시보드", "action": "navigate", "target": "/dashboard", "icon": "📊"}
                        ]

                        return ChatResponse(
                            response=response_message,
                            session_id=session_id,
                            timestamp=datetime.now(),
                            suggestions=suggested_questions,
                            quick_actions=quick_actions,
                            page_action=None
                        )
                    else:
                        # 등록 실패
                        error_message = f"❌ {registration_result.get('error', '채용공고 등록에 실패했습니다.')}\n\n다시 시도해주세요."
                        update_session(session_id, error_message, is_user=False)

                        return ChatResponse(
                            response=error_message,
                            session_id=session_id,
                            timestamp=datetime.now(),
                            suggestions=["다시 시도해주세요"],
                            quick_actions=[],
                            page_action=None
                        )

                except Exception as e:
                    print(f"❌ [등록처리] 등록 실행 중 오류: {str(e)}")
                    import traceback
                    traceback.print_exc()

                    error_message = "❌ 채용공고 등록 중 오류가 발생했습니다. 다시 시도해주세요."
                    update_session(session_id, error_message, is_user=False)

                    return ChatResponse(
                        response=error_message,
                        session_id=session_id,
                        timestamp=datetime.now(),
                        suggestions=["다시 시도해주세요"],
                        quick_actions=[],
                        page_action=None
                    )
            else:
                # 등록할 채용공고가 없는 경우
                print(f"⚠️ [등록처리] 등록할 채용공고가 없습니다.")
                no_data_message = "등록할 채용공고가 없습니다. 먼저 채용공고를 생성해주세요."
                update_session(session_id, no_data_message, is_user=False)

                return ChatResponse(
                    response=no_data_message,
                    session_id=session_id,
                    timestamp=datetime.now(),
                    suggestions=["채용공고를 먼저 생성해주세요"],
                    quick_actions=[],
                    page_action=None
                )

        # 기존 픽톡 툴 사용 (병렬 채용공고 에이전트 비활성화)
        print(f"🔧 [픽톡 툴] 기존 픽톡 채용공고 툴 사용")

        # 채용공고 등록 확인 처리 (ai-job-registration 페이지에서만)
        if (chat_message.message in ["등록하기", "확인", "네", "등록", "등록해줘", "이대로 등록해줘"] and
            chat_message.current_page == "ai-job-registration"):
            session_context = session_manager.get_context(session_id)
            print(f"🔍 [등록처리] 세션 컨텍스트 확인:")
            print(f"    세션 컨텍스트 존재: {bool(session_context)}")
            if session_context:
                print(f"    last_action: {session_context.get('last_action')}")
                print(f"    pending_job_posting 존재: {bool(session_context.get('pending_job_posting'))}")
                print(f"    conversation_topic: {session_context.get('conversation_topic')}")

                # pending_job_posting 상세 정보 로깅
                if session_context.get('pending_job_posting'):
                    pending_data = session_context['pending_job_posting']
                    print(f"    📝 pending_job_posting 상세:")
                    print(f"      - 제목: {pending_data.get('title', 'N/A')}")
                    print(f"      - 회사: {pending_data.get('company_name', 'N/A')}")
                    print(f"      - 직무: {pending_data.get('position', 'N/A')}")

            # pending_job_posting이 있으면 바로 등록
            if (session_context and
                session_context.get("pending_job_posting")):

                try:
                    # 채용공고 등록 실행 (기존 픽톡 툴 사용)
                    job_posting_data = session_context["pending_job_posting"]
                    registration_result = await self.job_posting_tool("create", job_data=job_posting_data)

                    if registration_result.get("job_id"):
                        response_message = f"🎉 채용공고가 성공적으로 등록되었습니다!\n\n"
                        response_message += f"**등록 ID:** {registration_result['job_id']}\n"
                        response_message += f"**제목:** {job_posting_data['title']}\n"
                        response_message += "이제 지원자들이 이 공고를 확인할 수 있습니다!"

                        # 세션 컨텍스트 정리
                        session_manager.update_context(session_id, {
                            "last_action": "job_posting_registered",
                            "pending_job_posting": None,
                            "conversation_topic": "채용공고 등록 완료"
                        })

                        # AI 응답 저장
                        update_session(session_id, response_message, is_user=False)

                        # 추천 질문 생성
                        suggested_questions = [
                            "등록된 채용공고를 확인하고 싶어요",
                            "다른 채용공고도 만들어주세요",
                            "지원자 관리는 어떻게 하나요?"
                        ]

                        # 빠른 액션 생성
                        quick_actions = [
                            {"title": "등록된 채용공고", "action": "navigate", "target": "/job-posting", "icon": "📋"},
                            {"title": "지원자 관리", "action": "navigate", "target": "/applicants", "icon": "👥"},
                            {"title": "대시보드", "action": "navigate", "target": "/dashboard", "icon": "📊"}
                        ]

                        return ChatResponse(
                            response=response_message,
                            session_id=session_id,
                            status="success",
                            suggested_questions=suggested_questions,
                            quick_actions=quick_actions,
                            page_action=None,
                            context_update={
                                "last_action": "job_posting_registered",
                                "conversation_topic": "채용공고 등록 완료"
                            }
                        )
                    else:
                        # 등록 실패
                        error_message = f"❌ 등록 실패: {registration_result.get('error', '채용공고 등록에 실패했습니다.')}"
                        update_session(session_id, error_message, is_user=False)

                        return ChatResponse(
                            response=error_message,
                            session_id=session_id,
                            status="error",
                            suggested_questions=["다시 시도해주세요"],
                            quick_actions=[],
                            page_action=None
                        )

                except Exception as e:
                    logger.error(f"채용공고 등록 처리 실패: {str(e)}")
                    error_message = f"❌ 등록 처리 중 오류가 발생했습니다: {str(e)}"
                    update_session(session_id, error_message, is_user=False)

                    return ChatResponse(
                        response=error_message,
                        session_id=session_id,
                        status="error",
                        suggested_questions=["다시 시도해주세요"],
                        quick_actions=[],
                        page_action=None
                    )
            else:
                # pending_job_posting이 없으면 최근 생성된 draft 상태 채용공고를 찾아서 등록
                try:
                    print(f"🔍 [등록처리] 최근 draft 채용공고 검색 중...")

                    # 최근 1시간 내에 생성된 draft 상태의 채용공고 찾기
                    # datetime 모듈은 이미 전역으로 import됨
                    from datetime import timedelta
                    one_hour_ago = datetime.now() - timedelta(hours=1)

                    recent_job = await tool_executor.mongo_service.db.job_postings.find_one(
                        {
                            "status": "draft",
                            "created_at": {"$gte": one_hour_ago}
                        },
                        sort=[("created_at", -1)]
                    )

                    if recent_job:
                        print(f"🔍 [등록처리] 최근 draft 채용공고 발견: {recent_job['_id']}")

                        # draft 상태를 active로 변경
                        recent_job["status"] = "active"
                        recent_job["updated_at"] = datetime.now()

                        # 데이터베이스 업데이트
                        await tool_executor.mongo_service.db.job_postings.update_one(
                            {"_id": recent_job["_id"]},
                            {"$set": {"status": "active", "updated_at": recent_job["updated_at"]}}
                        )

                        response_message = f"🎉 채용공고가 성공적으로 등록되었습니다!\n\n"
                        response_message += f"**등록 ID:** {recent_job['_id']}\n"
                        response_message += f"**제목:** {recent_job['title']}\n"
                        response_message += f"**상태:** active\n\n"
                        response_message += "채용공고가 성공적으로 등록되었습니다! 🚀"

                        update_session(session_id, response_message, is_user=False)

                        return ChatResponse(
                            response=response_message,
                            session_id=session_id,
                            timestamp=datetime.now(),
                            suggestions=["새로운 채용공고 작성", "등록된 채용공고 확인", "지원자 관리"],
                            quick_actions=[
                                {"title": "등록된 채용공고 확인", "action": "navigate", "target": "/job-posting", "icon": "📋"},
                                {"title": "지원자 관리", "action": "navigate", "target": "/applicants", "icon": "👥"}
                            ],
                            page_action=None
                        )
                    else:
                        print(f"⚠️ [등록처리] 등록할 채용공고가 없습니다.")
                        error_message = "❌ 등록할 채용공고가 없습니다.\n\n"
                        error_message += "**해결 방법:**\n"
                        error_message += "1. 먼저 채용공고를 생성해주세요\n"
                        error_message += "2. 생성된 채용공고를 검토한 후 '등록해줘'라고 말씀해주세요\n\n"
                        error_message += "**예시:**\n"
                        error_message += "• 'React 개발자 채용공고 만들어줘'\n"
                        error_message += "• 'Python 백엔드 개발자 구해요'"

                        update_session(session_id, error_message, is_user=False)

                        return ChatResponse(
                            response=error_message,
                            session_id=session_id,
                            timestamp=datetime.now(),
                            suggestions=[
                                "React 개발자 채용공고 만들어줘",
                                "Python 백엔드 개발자 구해요",
                                "새로운 채용공고 작성하기"
                            ],
                            quick_actions=[
                                {"title": "채용공고 작성", "action": "navigate", "target": "/ai-job-registration", "icon": "📝"},
                                {"title": "채용공고 목록", "action": "navigate", "target": "/job-posting", "icon": "📋"}
                            ],
                            page_action=None
                        )

                except Exception as e:
                    logger.error(f"최근 채용공고 등록 중 오류: {str(e)}")
                    error_message = f"❌ 등록 중 오류가 발생했습니다: {str(e)}"
                    update_session(session_id, error_message, is_user=False)

                    return ChatResponse(
                        response=error_message,
                        session_id=session_id,
                        timestamp=datetime.now(),
                        suggestions=["다시 시도", "고객지원 문의"],
                        quick_actions=[],
                        page_action=None
                    )

        # 채용공고 등록 취소 처리
        if chat_message.message in ["취소할게요", "취소", "아니요", "그만"]:
            session_context = session_manager.get_context(session_id)
            if (session_context and
                session_context.get("last_action") == "job_posting_preview" and
                session_context.get("pending_job_posting")):

                # 세션 컨텍스트 정리
                session_manager.update_context(session_id, {
                    "last_action": "job_posting_cancelled",
                    "pending_job_posting": None,
                    "conversation_topic": "채용공고 등록 취소"
                })

                response_message = "❌ 채용공고 등록이 취소되었습니다.\n\n다른 도움이 필요하시면 언제든 말씀해주세요!"

                # AI 응답 저장
                update_session(session_id, response_message, is_user=False)

                # 추천 질문 생성
                suggested_questions = [
                    "새로운 채용공고를 만들어주세요",
                    "지원자 관리는 어떻게 하나요?"
                ]

                # 빠른 액션 생성
                quick_actions = [
                    {"title": "채용공고 등록", "action": "navigate", "target": "/job-posting", "icon": "📝"},
                    {"title": "지원자 관리", "action": "navigate", "target": "/applicants", "icon": "👥"}
                ]

                return ChatResponse(
                    response=response_message,
                    session_id=session_id,
                    status="success",
                    suggested_questions=suggested_questions,
                    quick_actions=quick_actions,
                    page_action=None
                )

        # 세션 컨텍스트 가져오기
        session_context = session_manager.get_context(session_id)

        # 변수들은 이미 함수 시작부에서 초기화됨

        # 시스템 프롬프트 정의
        system_prompt = """당신은 AI 채용 관리 시스템의 에이전트입니다.

주요 기능:
1. 채용공고 등록 및 관리
2. 지원자 관리 및 평가
3. 면접 일정 관리
4. 포트폴리오 분석
5. 자기소개서 검증
6. 인재 추천

추가로 다음 툴들을 사용할 수 있습니다:
- GitHub API: 사용자 정보, 레포지토리, 커밋 조회
- MongoDB: 데이터베이스 문서 조회, 생성, 수정, 삭제
- 검색: 웹 검색, 뉴스 검색, 이미지 검색

사용자의 질문에 친절하고 정확하게 답변해주세요.
한국어로 답변하며, 필요시 구체적인 단계별 가이드를 제공하세요.
답변은 2-3문장으로 간결하게 작성하되, 필요한 정보는 모두 포함하세요.

툴 실행 결과가 있다면 그 결과를 바탕으로 답변해주세요.
에러가 발생한 경우에도 사용자에게 친절하게 설명해주세요.

중요: GitHub 레포지토리 분석 시 기술 스택 정보나 언어 정보를 추가로 언급하지 마세요.
제공된 정보만 그대로 사용하세요.

절대 금지사항:
- GitHub 프로젝트 목록에서 언어 정보 (예: HTML, JavaScript, Dart) 추가 언급 금지
- 기술 스택 요약 섹션 추가 금지
- "주요 기술 스택으로는..." 같은 문장 추가 금지
- 프로젝트 이름 뒤에 언어 정보 추가 금지"""

        # AI 응답 생성
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"대화 기록:\n{conversation_context}\n\n현재 질문: {chat_message.message}"}
        ]

        # 툴 결과가 있으면 프롬프트에 추가
        if tool_results:
            print(f"🔧 [툴 결과 처리] 시작")
            print(f"    🔍 툴 결과 구조: {list(tool_results.keys())}")
            print(f"    ✅ 성공 여부: {tool_results.get('result', {}).get('status')}")

            if tool_results.get("result", {}).get("status") == "success":
                # 툴 결과를 자연어로 변환
                tool_data = tool_results["result"]["data"]
                print(f"    📊 툴 데이터 크기: {len(str(tool_data))}자")
                print(f"    📋 툴 데이터 타입: {type(tool_data).__name__}")

                natural_language_result = format_tool_data(tool_data)
                print(f"    📝 자연어 변환 결과: {natural_language_result[:100]}...")

                messages.append({
                    "role": "assistant",
                    "content": f"툴 실행 결과: {natural_language_result}"
                })
                print(f"    ✅ 성공 결과를 프롬프트에 추가")
            else:
                # 에러가 발생한 경우 에러 정보 추가
                error_info = tool_results.get("result", {})
                print(f"    ❌ 툴 실행 실패:")
                print(f"      - 상태: {error_info.get('status', 'N/A')}")
                print(f"      - 오류: {error_info.get('error', 'N/A')}")

                error_message = create_error_aware_response(tool_results, chat_message.message)
                messages.append({
                    "role": "assistant",
                    "content": f"툴 실행 중 오류 발생: {error_message}"
                })
                print(f"    ❌ 오류 정보를 프롬프트에 추가")

        print(f"🔍 [DEBUG] AI 응답 생성 시작 - 메시지 수: {len(messages)}")

        # 프롬프트 내용 디버깅
        print(f"🔍 [AI 프롬프트 분석]:")
        for i, msg in enumerate(messages):
            role_emoji = "👤" if msg["role"] == "user" else "🤖" if msg["role"] == "assistant" else "⚙️"
            content_preview = msg["content"][:150] + ('...' if len(msg["content"]) > 150 else '')
            print(f"    {i+1}. {role_emoji} {msg['role']}: {content_preview}")

        # AI 응답 생성 시간 측정
        ai_start = time.time()
        response = await openai_service.chat_completion(messages)
        ai_time = time.time() - ai_start

        print(f"🔍 [DEBUG] AI 응답 생성 완료 (소요시간: {ai_time:.3f}초)")
        print(f"📝 [AI 응답 내용]: {response[:200]}...")
        print(f"📏 [AI 응답 길이]: {len(response)}자")

        # 응답 품질 분석
        response_quality = "높음" if len(response) > 50 else "보통" if len(response) > 20 else "낮음"
        print(f"📊 [응답 품질]: {response_quality}")

        # 특수 키워드 감지
        special_keywords = ['채용공고', '지원자', '포트폴리오', '면접', '분석', '추천']
        detected_keywords = [kw for kw in special_keywords if kw in response]
        if detected_keywords:
            print(f"🎯 [키워드 감지]: {', '.join(detected_keywords)}")

        # 툴 사용 시 관련 페이지로 이동하는 액션 추가
        page_action = None

        # AI 채용공고 등록 액션 처리
        if tool_results and tool_results.get("mode") == "action" and tool_results.get("action") == "openAIJobRegistration":
            # 사용자 메시지에서 채용공고 정보 추출
            auto_fill_data = extract_job_posting_info(chat_message.message)
            page_action = {
                "action": "openAIJobRegistration",
                "message": "📝 채용공고 등록 페이지로 이동합니다.\n\n추출된 정보를 기반으로 폼이 자동으로 채워지며, 추가 정보 입력 후 최종 등록하실 수 있습니다.",
                "auto_fill_data": auto_fill_data,
                "target_url": "/job-posting"
            }
        elif tool_results and tool_results.get("tool"):
            tool_name = tool_results["tool"]
            action_type = tool_results.get("action", "")

            # AI 기반 동적 페이지 결정
            page_action = await determine_target_page_with_ai(
                user_message=chat_message.message,
                tool_name=tool_name,
                action_type=action_type,
                tool_results=result,
                openai_service=openai_service,
                session_context=session_context
            )

        # AI 응답 저장
        update_session(session_id, response, is_user=False)
        print(f"🔍 [DEBUG] AI 응답 저장 완료")

        # AI 기반 추천 질문 생성
        suggestions = await generate_suggestions_with_ai(
            chat_message.message,
            response,
            openai_service,
            session_context
        )
        print(f"🔍 [DEBUG] AI 추천 질문 생성: {suggestions}")

        # AI 기반 빠른 액션 생성
        quick_actions = await generate_quick_actions_with_ai(
            chat_message.message,
            response,
            openai_service,
            session_context
        )
        print(f"🔍 [DEBUG] AI 빠른 액션 생성: {quick_actions}")

        # AI 기반 컨텍스트 업데이트
        await update_conversation_context_with_ai(
            session_id=session_id,
            user_message=chat_message.message,
            ai_response=response,
            tool_usage=tool_usage,
            openai_service=openai_service,
            session_manager=session_manager
        )

        final_response = ChatResponse(
            response=response,
            session_id=session_id,
            timestamp=datetime.now(),
            suggestions=suggestions,
            quick_actions=quick_actions,
            confidence=0.95,
            tool_results=tool_results,
            error_info=error_info,
            page_action=page_action
        )

        # 최종 응답 상세 디버깅
        total_time = time.time() - start_time
        print(f"\n🎉 [최종 응답 완료] ================================")
        print(f"⏱️ 총 처리 시간: {total_time:.3f}초")
        print(f"🔑 세션 ID: {session_id}")
        print(f"📝 응답 길이: {len(response)}자")
        print(f"💡 제안 개수: {len(suggestions)}개")
        print(f"⚡ 빠른 액션: {len(quick_actions)}개")
        print(f"🎯 페이지 액션: {'있음' if page_action else '없음'}")
        print(f"🔧 툴 사용: {'있음' if tool_results else '없음'}")
        print(f"❌ 오류 정보: {'있음' if error_info else '없음'}")

        # 성능 분석
        if total_time > 5.0:
            print(f"⚠️ [성능 경고] 응답 시간이 5초를 초과했습니다: {total_time:.3f}초")
        elif total_time > 2.0:
            print(f"⚠️ [성능 주의] 응답 시간이 2초를 초과했습니다: {total_time:.3f}초")
        else:
            print(f"✅ [성능 양호] 응답 시간이 정상 범위입니다: {total_time:.3f}초")

        print(f"================================================\n")

        return final_response

    except Exception as e:
        total_time = time.time() - start_time
        error_id = f"ERR_{int(time.time())}"

        print(f"\n{'!'*80}")
        print(f"🚨 [CRITICAL ERROR] 픽톡 처리 중 심각한 오류 발생")
        print(f"🆔 에러 ID: {error_id}")
        print(f"📝 세션 ID: {chat_message.session_id}")
        print(f"💬 사용자 메시지: '{chat_message.message}'")
        print(f"⏱️ 총 처리 시간: {total_time:.3f}초")
        print(f"🔍 에러 타입: {type(e).__name__}")
        print(f"📄 에러 메시지: {str(e)}")

        # 스택 트레이스 출력
        import traceback
        print(f"📊 스택 트레이스:")
        traceback.print_exc()
        print(f"{'!'*80}")

        # 에러 메시지 저장 (세션이 있다면)
        try:
            error_response = f"❌ 처리 중 오류가 발생했습니다 (에러 ID: {error_id}). 잠시 후 다시 시도해주세요."
            update_session(session_id, error_response, is_user=False)
        except:
            pass  # 세션 저장 실패해도 무시

        logger.error(f"에이전트 심각한 오류 [ID: {error_id}]: {str(e)}")

        # 사용자에게는 친화적인 에러 메시지 반환
        raise HTTPException(
            status_code=500,
            detail=f"챗봇 처리 중 오류가 발생했습니다. 에러 ID: {error_id}"
        )

async def generate_suggestions_with_ai(
    user_message: str,
    ai_response: str,
    openai_service,
    session_context: Dict[str, Any] = None
) -> List[str]:
    """AI 기반 동적 추천 질문 생성"""

    context_info = ""
    if session_context:
        if session_context.get("conversation_topic"):
            context_info += f"\n대화 주제: {session_context['conversation_topic']}"
        if session_context.get("last_tool_used"):
            context_info += f"\n마지막 사용 도구: {session_context['last_tool_used']}"

    prompt = f"""
사용자와의 대화 흐름을 바탕으로 다음에 물어볼 만한 자연스러운 질문 3개를 생성해주세요.

사용자 메시지: "{user_message}"
AI 응답: "{ai_response[:200]}..."

{context_info}

시스템 기능:
- 채용공고 관리
- 지원자 관리
- 면접 일정 관리
- 포트폴리오 분석
- 자기소개서 검증
- 인재 추천

다음 조건을 만족하는 질문들을 생성해주세요:
1. 현재 대화 맥락과 자연스럽게 이어지는 질문
2. 사용자가 실제로 궁금해할 만한 실용적인 질문
3. 시스템의 다양한 기능을 탐색할 수 있는 질문

JSON 배열로 응답: ["질문1", "질문2", "질문3"]
"""

    try:
        response = await openai_service.chat_completion([
            {"role": "user", "content": prompt}
        ])

        import json
        import re

        # JSON 배열 추출
        json_match = re.search(r'\[.*\]', response, re.DOTALL)
        if json_match:
            suggestions = json.loads(json_match.group())
            return suggestions[:3]  # 최대 3개

    except Exception as e:
        print(f"🔍 [DEBUG] AI 추천 질문 생성 실패: {str(e)}")

    # 폴백: 기본 추천 질문
    return [
        "다른 기능은 어떤 것들이 있나요?",
        "더 자세한 정보를 어디서 확인할 수 있나요?",
        "관련된 다른 작업은 어떻게 하나요?"
    ]

import re


def format_response_text(text: str) -> str:
    """
    한글·영어 답변을 가독성 좋게 재구성합니다.
    - 숫자 항목 뒤에 줄바꿈을 없앰
    - `**` 구문을 제거
    - 문장 끝에 두 줄 빈 줄 삽입
    - 이모지 앞에 두 줄 빈 줄 삽입
    - 불릿(•) 앞에 한 줄 빈 줄 삽입
    """

    if not text:
        return text

    # 1️⃣ 이모지 리스트 (섹션 구분용)
    EMOJIS = ["📋", "💡", "🎯", "🔍", "📊", "🤝", "💼", "📝", "🚀", "💻"]

    # 2️⃣ 숫자 항목 정규식 (숫자. 뒤에 한 칸만 남김)
    NUM_LIST_RE = re.compile(r'\b(\d+)\.\s+')

    # 3️⃣ 이모지 찾기
    EMOJI_RE = re.compile(r'(' + '|'.join(map(re.escape, EMOJIS)) + r')')

    # 0️⃣ 양쪽 공백 및 개행 정리
    text = text.strip()

    # 1️⃣ `**` 제거 (굵은 텍스트 표시가 필요 없으므로 없애줍니다)
    text = text.replace('**', '')

    # 2️⃣ 문장 끝(마침표·물음표·느낌표·한글 마침표) 뒤에 두 줄 빈 줄
    text = re.sub(r'([.!?。])\s+', r'\1\n\n', text)

    # 3️⃣ 불릿(•) 앞에 줄 바꿈
    text = text.replace('• ', '\n• ')

    # 4️⃣ 숫자 항목 1., 2. 앞에 줄 바꿈 **하지만** 번호 다음은 한 줄에 남김
    text = NUM_LIST_RE.sub(r'\1. ', text)     # <-- 줄바꿈 대신 공백

    # 5️⃣ 이모지 앞에 두 줄 빈 줄
    def _emoji_wrap(match):
        return f'\n\n{match.group(1)}'
    text = EMOJI_RE.sub(_emoji_wrap, text)

    # 6️⃣ 중복 빈 줄(3개 이상)을 2개로 정리
    text = re.sub(r'\n{3,}', '\n\n', text)

    return text

async def generate_quick_actions_with_ai(
    user_message: str,
    ai_response: str,
    openai_service,
    session_context: Dict[str, Any] = None
) -> List[Dict[str, Any]]:
    """AI 기반 동적 빠른 액션 생성"""

    available_pages = {
        "/dashboard": {"title": "대시보드", "icon": "📊"},
        "/applicants": {"title": "지원자 관리", "icon": "👥"},
        "/github-test": {"title": "포트폴리오 분석", "icon": "💻"},
        "/job-posting": {"title": "등록된 채용공고", "icon": "📋"},
        "/resume": {"title": "이력서 관리", "icon": "📄"},
        "/portfolio": {"title": "포트폴리오", "icon": "🎨"},
        "/settings": {"title": "설정", "icon": "⚙️"}
    }

    context_info = ""
    if session_context:
        if session_context.get("last_tool_used"):
            context_info += f"\n마지막 사용 도구: {session_context['last_tool_used']}"

    prompt = f"""
사용자의 요청과 AI 응답을 바탕으로 사용자가 다음에 할 가능성이 높은 액션 2개를 선택해주세요.

사용자 메시지: "{user_message}"
AI 응답: "{ai_response[:200]}..."

{context_info}

사용 가능한 페이지들:
{chr(10).join([f"- {page}: {info['title']}" for page, info in available_pages.items()])}

다음 기준으로 액션을 선택해주세요:
1. 현재 대화 맥락에서 자연스럽게 이어질 수 있는 액션
2. 사용자가 실제로 필요로 할 가능성이 높은 기능
3. 현재 응답과 관련된 추가 작업

JSON 배열로 응답:
[
  {{"target": "/페이지경로", "title": "액션명"}},
  {{"target": "/페이지경로", "title": "액션명"}}
]

액션이 필요하지 않으면: []
"""

    try:
        response = await openai_service.chat_completion([
            {"role": "user", "content": prompt}
        ])

        import json
        import re

        # JSON 배열 추출
        json_match = re.search(r'\[.*\]', response, re.DOTALL)
        if json_match:
            actions_data = json.loads(json_match.group())

            # 액션 정보 구성
            actions = []
            for action_data in actions_data[:2]:  # 최대 2개
                target = action_data["target"]
                title = action_data["title"]
                icon = available_pages.get(target, {}).get("icon", "🔗")

                actions.append({
                    "title": title,
                    "action": "navigate",
                    "target": target,
                    "icon": icon
                })

            return actions

    except Exception as e:
        print(f"🔍 [DEBUG] AI 빠른 액션 생성 실패: {str(e)}")

    # 폴백: 현재 대화와 관련된 기본 액션
    if "포트폴리오" in user_message or "github" in user_message.lower():
        return [{
            "title": "포트폴리오 분석",
            "action": "navigate",
            "target": "/github-test",
            "icon": "💻"
        }]

    return []

@router.get("/session/{session_id}", response_model=ChatSession)
async def get_session(session_id: str):
    """세션 정보 조회"""
    session_info = session_manager.get_session_info(session_id)
    if not session_info:
        raise HTTPException(status_code=404, detail="세션을 찾을 수 없습니다")

    history = session_manager.get_history(session_id)

    return ChatSession(
        session_id=session_id,
        messages=history,
        created_at=datetime.fromtimestamp(session_info["created_at"]),
        last_updated=datetime.fromtimestamp(session_info["last_activity"])
    )

@router.delete("/session/{session_id}")
async def delete_session(session_id: str):
    """세션 삭제"""
    if session_manager.delete_session(session_id):
        return {"message": "세션이 삭제되었습니다"}
    else:
        raise HTTPException(status_code=404, detail="세션을 찾을 수 없습니다")

@router.get("/sessions")
async def list_sessions():
    """모든 세션 목록 조회"""
    # 세션 정리 후 목록 반환
    session_manager.cleanup_sessions()
    sessions = session_manager.list_all_sessions()

    return {
        "sessions": sessions,
        "total_count": len(sessions)
    }

@router.post("/sessions/cleanup")
async def cleanup_all_sessions():
    """모든 만료된 세션 정리"""
    before_count = len(session_manager.sessions)
    session_manager.cleanup_sessions()
    after_count = len(session_manager.sessions)

    return {
        "message": f"세션 정리 완료: {before_count - after_count}개 세션 삭제됨",
        "before_count": before_count,
        "after_count": after_count,
        "deleted_count": before_count - after_count
    }

@router.get("/tools/status")
async def get_tools_status():
    """툴 상태 조회"""
    return tool_executor.get_tool_status()

@router.get("/tools/available")
async def get_available_tools():
    """사용 가능한 툴 목록 조회"""
    return {
        "tools": tool_executor.get_available_tools()
    }

@router.get("/tools/test/{tool_name}")
async def test_tool(tool_name: str, action: str = "test", params: str = "{}"):
    """특정 툴 테스트"""
    try:
        import json
        params_dict = json.loads(params) if params else {}

        # 툴 실행
        result = await tool_executor.execute_async(tool_name, action, **params_dict)

        return {
            "tool": tool_name,
            "action": action,
            "params": params_dict,
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "tool": tool_name,
            "action": action,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }



@router.post("/tools/execute")
async def execute_tool(tool_name: str, action: str, params: Dict[str, Any]):
    """툴 직접 실행"""
    result = tool_executor.execute(tool_name, action, **params)
    return result

@router.get("/tools/error-stats")
async def get_error_statistics():
    """에러 통계 조회"""
    return tool_executor.get_error_statistics()

@router.get("/performance/stats")
async def get_performance_statistics():
    """성능 통계 조회"""
    return tool_executor.get_performance_stats()

@router.post("/performance/cache/clear")
async def clear_cache(tool_name: str = None):
    """캐시 정리"""
    tool_executor.clear_cache(tool_name)
    return {"message": f"캐시가 정리되었습니다. (툴: {tool_name if tool_name else '전체'})"}

@router.post("/performance/stats/reset")
async def reset_performance_statistics():
    """성능 통계 초기화"""
    tool_executor.reset_performance_stats()
    return {"message": "성능 통계가 초기화되었습니다."}

# 모니터링 및 로깅 API 엔드포인트들
@router.get("/monitoring/metrics")
async def get_monitoring_metrics(tool_action: str = None):
    """모니터링 메트릭 조회"""
    metrics = monitoring_system.get_performance_metrics(tool_action)
    return {
        "metrics": metrics,
        "timestamp": datetime.now().isoformat()
    }

@router.get("/monitoring/usage")
async def get_usage_statistics(days: int = 7):
    """사용량 통계 조회"""
    stats = monitoring_system.get_usage_statistics(days)
    return {
        "statistics": stats,
        "timestamp": datetime.now().isoformat()
    }

@router.get("/monitoring/logs")
async def get_recent_logs(limit: int = 100):
    """최근 로그 조회"""
    logs = monitoring_system.get_recent_logs(limit)
    return {
        "logs": logs,
        "total_count": len(logs),
        "timestamp": datetime.now().isoformat()
    }

@router.post("/monitoring/metrics/clear")
async def clear_monitoring_metrics():
    """모니터링 메트릭 초기화"""
    monitoring_system.clear_metrics()
    return {"message": "모니터링 메트릭이 초기화되었습니다."}

@router.get("/monitoring/alerts")
async def get_alert_history():
    """알림 히스토리 조회"""
    # 실제 구현에서는 알림 히스토리를 반환
    return {
        "alerts": [],
        "message": "알림 히스토리 기능은 개발 중입니다."
    }

# 제목 추천 API
class TitleRecommendationRequest(BaseModel):
    form_data: Dict[str, Any]
    content: str

class TitleRecommendation(BaseModel):
    concept: str
    title: str
    description: str

class TitleRecommendationResponse(BaseModel):
    titles: List[TitleRecommendation]
    message: str

@router.post("/generate-title", response_model=TitleRecommendationResponse)
async def generate_title_recommendations(
    request: TitleRecommendationRequest,
    openai_service: LLMService = Depends(get_openai_service)
):
    """채용공고 제목 추천 생성"""
    try:
        print(f"[API] 제목 추천 요청 받음 - 폼 데이터: {len(request.form_data)}개 필드")

        # 폼 데이터에서 주요 정보 추출
        form_data = request.form_data
        content = request.content

        # 주요 키워드 추출
        keywords = []
        if form_data.get('department'):
            keywords.append(form_data['department'])
        if form_data.get('position'):
            keywords.append(form_data['position'])
        if form_data.get('experience'):
            keywords.append(form_data['experience'])
        if form_data.get('mainDuties'):
            keywords.append(form_data['mainDuties'])

        # 제목 생성 프롬프트 구성
        prompt = f"""
다음 채용공고 정보를 바탕으로 4가지 컨셉의 제목을 생성해주세요:

채용공고 정보:
{content}

주요 키워드: {', '.join(keywords) if keywords else '없음'}

다음 4가지 컨셉으로 제목을 생성해주세요:
1. 신입친화형: 신입 지원자들이 매력적으로 느낄 수 있는 제목
2. 전문가형: 경력자들이 전문성을 발휘할 수 있다고 느끼는 제목
3. 일반형: 일반적인 채용공고 제목
4. 창의형: 독특하고 눈에 띄는 제목

각 제목은 20자 이내로 작성하고, 한국어로 자연스럽게 작성해주세요.
JSON 형태로 응답해주세요:

{{
    "titles": [
        {{"concept": "신입친화형", "title": "제목1", "description": "설명1"}},
        {{"concept": "전문가형", "title": "제목2", "description": "설명2"}},
        {{"concept": "일반형", "title": "제목3", "description": "설명3"}},
        {{"concept": "창의형", "title": "제목4", "description": "설명4"}}
    ]
}}
"""

        # LLM 서비스를 통한 제목 생성
        response = await openai_service.chat_completion([{"role": "user", "content": prompt}])

        try:
            # JSON 응답 파싱
            import json
            import re

            # JSON 부분 추출
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                result = json.loads(json_str)

                if 'titles' in result and isinstance(result['titles'], list):
                    titles = []
                    for title_data in result['titles']:
                        if isinstance(title_data, dict) and 'concept' in title_data and 'title' in title_data:
                            titles.append(TitleRecommendation(
                                concept=title_data['concept'],
                                title=title_data['title'],
                                description=title_data.get('description', '')
                            ))

                    if titles:
                        return TitleRecommendationResponse(
                            titles=titles,
                            message="AI가 생성한 제목 추천입니다."
                        )

            # JSON 파싱 실패 시 기본 제목 생성
            print(f"[API] JSON 파싱 실패, 기본 제목 생성")

        except Exception as parse_error:
            print(f"[API] JSON 파싱 오류: {parse_error}")

        # 기본 제목 생성 (LLM 응답이 실패하거나 파싱이 실패한 경우)
        default_titles = [
            TitleRecommendation(
                concept="신입친화형",
                title=f"함께 성장할 {keywords[0] if keywords else '직무'} 신입을 찾습니다",
                description="신입 지원자들이 매력적으로 느낄 수 있는 제목"
            ),
            TitleRecommendation(
                concept="전문가형",
                title=f"전문성을 발휘할 {keywords[0] if keywords else '직무'} 인재 모집",
                description="경력자들이 전문성을 발휘할 수 있다고 느끼는 제목"
            ),
            TitleRecommendation(
                concept="일반형",
                title=f"{keywords[0] if keywords else '부서'} {keywords[1] if len(keywords) > 1 else '직무'} 채용",
                description="일반적인 채용공고 제목"
            ),
            TitleRecommendation(
                concept="창의형",
                title=f"혁신을 이끌 {keywords[0] if keywords else '인재'}를 찾습니다",
                description="독특하고 눈에 띄는 제목"
            )
        ]

        return TitleRecommendationResponse(
            titles=default_titles,
            message="기본 제목 추천입니다."
        )

    except Exception as e:
        print(f"[API] 제목 추천 생성 실패: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"제목 추천 생성에 실패했습니다: {str(e)}"
        )

@router.get("/agent/status")
async def get_agent_status():
    """에이전트 상태 정보를 반환합니다."""
    try:
        # 모니터링 시스템에서 메트릭 가져오기
        metrics = monitoring_system.get_metrics()

        # 세션 매니저에서 세션 정보 가져오기
        session_manager = SessionManager()
        active_sessions = session_manager.list_all_sessions()

        return {
            "status": "active",
            "timestamp": datetime.now().isoformat(),
            "metrics": {
                "total_requests": metrics.get("total_requests", 0),
                "successful_requests": metrics.get("successful_requests", 0),
                "failed_requests": metrics.get("failed_requests", 0),
                "average_response_time": metrics.get("average_response_time", 0),
                "active_sessions": len(active_sessions)
            },
            "sessions": {
                "active_count": len(active_sessions),
                "session_list": active_sessions
            },
            "services": {
                "llm_service": "available",
                "tool_executor": "available",
                "monitoring": "active"
            }
        }
    except Exception as e:
        return {
            "status": "error",
            "timestamp": datetime.now().isoformat(),
            "error": str(e),
            "services": {
                "llm_service": "unknown",
                "tool_executor": "unknown",
                "monitoring": "error"
            }
        }

# 제목 생성 API 엔드포인트
class TitleGenerationRequest(BaseModel):
    form_data: Dict[str, Any]
    content: Optional[str] = None

class TitleGenerationResponse(BaseModel):
    titles: List[Dict[str, str]]
    message: str

@router.post("/generate-title", response_model=TitleGenerationResponse)
async def generate_title(request: TitleGenerationRequest):
    """채용공고 제목을 생성합니다."""
    try:
        form_data = request.form_data
        content = request.content or ""

        print(f"[API] 제목 생성 요청: {form_data}")

        # 폼 데이터에서 키워드 추출
        keywords = []
        if form_data.get('department'):
            keywords.append(form_data['department'])
        if form_data.get('position'):
            keywords.append(form_data['position'])
        if form_data.get('mainDuties'):
            # 주요 업무에서 키워드 추출
            duties = form_data['mainDuties']
            # 간단한 키워드 추출 (첫 번째 명사나 동사)
            words = duties.split()
            if words:
                keywords.append(words[0])

        # 기본 키워드가 없으면 기본값 사용
        if not keywords:
            keywords = ['직무', '인재']

        # AI 제목 생성 (실제로는 LLM 서비스 호출)
        # 현재는 기본 제목 생성
        generated_titles = [
            {
                "concept": "신입친화형",
                "title": f"함께 성장할 {keywords[0]} 신입을 찾습니다",
                "description": "신입 지원자들이 매력적으로 느낄 수 있는 제목"
            },
            {
                "concept": "전문가형",
                "title": f"전문성을 발휘할 {keywords[0]} 인재 모집",
                "description": "경력자들이 전문성을 발휘할 수 있다고 느끼는 제목"
            },
            {
                "concept": "일반형",
                "title": f"{keywords[0]} {keywords[1] if len(keywords) > 1 else '직무'} 채용",
                "description": "일반적인 채용공고 제목"
            },
            {
                "concept": "창의형",
                "title": f"혁신을 이끌 {keywords[0]}를 찾습니다",
                "description": "독특하고 눈에 띄는 제목"
            }
        ]

        return TitleGenerationResponse(
            titles=generated_titles,
            message="AI가 생성한 제목 추천입니다."
        )

    except Exception as e:
        print(f"[API] 제목 생성 실패: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"제목 생성에 실패했습니다: {str(e)}"
        )

    def _extract_job_keywords(self, job_data: Dict[str, Any]) -> List[str]:
        """채용공고 데이터에서 키워드를 자동으로 추출합니다."""
        try:
            keywords = set()

            # 주요 필드에서 키워드 추출
            key_fields = [
                'title', 'company', 'department', 'position',
                'mainDuties', 'requirements', 'preferred', 'description'
            ]

            for field in key_fields:
                if field in job_data and job_data[field]:
                    text = str(job_data[field])

                    # 간단한 키워드 추출 (공백으로 분리, 특수문자 제거)
                    words = text.replace(',', ' ').replace(';', ' ').split()
                    for word in words:
                        # 2글자 이상, 숫자나 특수문자로만 구성되지 않은 단어만
                        cleaned_word = ''.join(c for c in word if c.isalnum())
                        if len(cleaned_word) >= 2 and not cleaned_word.isdigit():
                            keywords.add(cleaned_word.lower())

            # 상위 10개 키워드만 반환
            keyword_list = list(keywords)[:10]
            logger.info(f"🔑 [키워드추출] {len(keyword_list)}개 키워드 추출: {keyword_list}")

            return keyword_list

        except Exception as e:
            logger.error(f"❌ [키워드추출] 키워드 추출 실패: {str(e)}")
            return []
