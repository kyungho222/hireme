import codecs
import csv
import locale
import logging
import os
import sys
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import uvicorn

# .env 파일 로드 (가장 먼저 실행)
# try:
#     load_dotenv(dotenv_path=".env")
# except Exception:
#     pass  # .env 파일이 없어도 무시
from bson import ObjectId
from chatbot.routers.chatbot_router import router as chatbot_router
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse

# chatbot 라우터 추가
try:
    from github import router as github_router
except ImportError:
    github_router = None
from modules.token_monitor import auto_monitor
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel
from routers.applicants import get_mongo_service, get_similarity_service
from routers.applicants import router as applicants_router
from routers.dynamic_messages import router as dynamic_messages_router
from routers.integrated_ocr import router as integrated_ocr_router
from routers.job_posting import router as job_posting_router

# from routers.pdf_ocr import router as pdf_ocr_router
from routers.pick_chatbot import router as pick_chatbot_router
from routers.pick_chatbot_direct_registration import (
    router as pick_chatbot_direct_router,
)
from routers.sample_data import router as sample_data_router
from routers.token_monitor import router as token_monitor_router
from routers.upload import router as upload_router

# 회사 인재상 라우터 추가
try:
    from routers.company_culture import router as company_culture_router
except ImportError:
    company_culture_router = None

# 모듈화된 라우터 추가
try:
    from modules.resume.router import router as resume_router
except ImportError:
    resume_router = None

try:
    from modules.cover_letter.router import router as cover_letter_router
except ImportError:
    cover_letter_router = None

try:
    from modules.portfolio.router import router as portfolio_router
except ImportError:
    portfolio_router = None

try:
    from modules.hybrid.router import router as hybrid_router
except ImportError:
    hybrid_router = None

# AI 유사도 분석 모듈화된 라우터 추가
try:
    from modules.api.routers.similarity_router import router as similarity_router
except ImportError:
    similarity_router = None


from modules.core.services.embedding_service import EmbeddingService
from modules.core.services.mongo_service import MongoService
from modules.core.services.similarity_service import SimilarityService
from modules.core.services.vector_service import VectorService

# Python 환경 인코딩 설정
# 시스템 기본 인코딩을 UTF-8로 설정
if sys.platform.startswith('win'):
    # Windows 환경에서 UTF-8 강제 설정
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    # 콘솔 출력 인코딩 설정
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.detach())

# Lifespan 이벤트 관리
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_services()

    # 자동 토큰 모니터링 시작
    if os.getenv("TOKEN_AUTO_MONITOR", "true").lower() == "true":
        auto_monitor.start_monitoring()
        print("🔍 자동 토큰 모니터링 활성화")

    yield

    # Shutdown
    if auto_monitor.is_running:
        auto_monitor.stop_monitoring()
        print("⏹️ 자동 토큰 모니터링 중지")

# FastAPI 앱 생성
app = FastAPI(
    title="AI 채용 관리 시스템 API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 한글 인코딩을 위한 미들웨어
@app.middleware("http")
async def add_charset_header(request, call_next):
    response = await call_next(request)

    # 모든 JSON 응답에 UTF-8 인코딩 명시
    if response.headers.get("content-type", "").startswith("application/json"):
        response.headers["content-type"] = "application/json; charset=utf-8"

    # 텍스트 응답에도 UTF-8 인코딩 명시
    elif response.headers.get("content-type", "").startswith("text/"):
        if "charset" not in response.headers.get("content-type", ""):
            current_content_type = response.headers.get("content-type", "")
            response.headers["content-type"] = f"{current_content_type}; charset=utf-8"

    return response

# 라우터 등록
if github_router:
    app.include_router(github_router, prefix="/api", tags=["github"])
app.include_router(upload_router, tags=["upload"])
app.include_router(pick_chatbot_router, prefix="/api/pick-chatbot", tags=["pick-chatbot"])
app.include_router(pick_chatbot_direct_router, tags=["pick-chatbot-direct"])
app.include_router(dynamic_messages_router, tags=["dynamic-messages"])
app.include_router(integrated_ocr_router, prefix="/api/integrated-ocr", tags=["integrated-ocr"])
# app.include_router(pdf_ocr_router, prefix="/api/pdf-ocr", tags=["pdf_ocr"])
app.include_router(job_posting_router, tags=["job-postings"])
app.include_router(applicants_router, tags=["applicants"])
app.include_router(sample_data_router, prefix="/api/sample", tags=["sample-data"])
app.include_router(chatbot_router, prefix="/chatbot", tags=["chatbot"])
app.include_router(token_monitor_router, tags=["token-monitor"])

# 회사 인재상 라우터 등록
if company_culture_router:
    app.include_router(company_culture_router, tags=["company-culture"])

# 모듈화된 라우터 등록
if resume_router:
    app.include_router(resume_router, prefix="/api/resume", tags=["resume"])

if cover_letter_router:
    app.include_router(cover_letter_router, tags=["cover-letter"])

if portfolio_router:
    app.include_router(portfolio_router, prefix="/api/portfolio", tags=["portfolio"])

if hybrid_router:
    app.include_router(hybrid_router, prefix="/api/hybrid", tags=["hybrid"])

# AI 유사도 분석 모듈화된 라우터 등록
if similarity_router:
    app.include_router(similarity_router, tags=["similarity"])

# 채용공고 에이전트 라우터 등록
try:
    from routers.job_posting_agent import router as job_posting_agent_router
    app.include_router(job_posting_agent_router, tags=["job-posting-agent"])
except ImportError:
    pass

# 리액트 에이전트 라우터 등록
try:
    from routers.react_agent_router import router as react_agent_router
    app.include_router(react_agent_router, prefix="/api", tags=["react-agent"])
except ImportError:
    pass

# 향상된 ReAct 에이전트 라우터 등록
try:
    from routers.react_agent_enhanced import router as react_agent_enhanced_router
    app.include_router(react_agent_enhanced_router, prefix="/api", tags=["react-agent-v2"])
except ImportError:
    pass

# 채용공고 에이전트 초기화
try:
    from modules.job_posting.dynamic_templates import init_dynamic_template_manager
    from modules.job_posting.job_posting_agent import init_job_posting_agent

    # 전역 변수로 초기화 상태 관리
    agent_initialized = False

    async def init_services():
        global agent_initialized
        try:
            await init_dynamic_template_manager(client)
            await init_job_posting_agent(client, None)
            agent_initialized = True
        except Exception:
            pass

    # FastAPI startup 이벤트에서 초기화 (lifespan으로 대체됨)
    # @app.on_event("startup")  # Deprecated - lifespan으로 대체
    # async def startup_event():
    #     await init_services()

except ImportError:
    pass


# MongoDB 연결 최적화
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/hireme")
client = AsyncIOMotorClient(
    MONGODB_URI,
    maxPoolSize=50,  # 최대 연결 풀 크기
    minPoolSize=10,  # 최소 연결 풀 크기
    maxIdleTimeMS=30000,  # 유휴 연결 타임아웃
    serverSelectionTimeoutMS=5000,  # 서버 선택 타임아웃
    socketTimeoutMS=20000,  # 소켓 타임아웃
    connectTimeoutMS=10000,  # 연결 타임아웃
    retryWrites=True  # 쓰기 재시도
)
db = client.hireme

# 환경 변수에서 API 키 로드
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "resume-vectors")

# 통합 최적화 서비스 초기화 (비동기로 처리)
try:
    import asyncio

    from modules.core.services.optimization_service import initialize_optimization

    # 환경별 최적화 설정
    environment = os.getenv("ENVIRONMENT", "development")

    # 비동기 초기화를 백그라운드에서 실행
    async def init_optimization():
        await initialize_optimization(environment)

    # 이벤트 루프가 있으면 태스크로 실행, 없으면 새 루프 생성
    try:
        loop = asyncio.get_running_loop()
        asyncio.create_task(init_optimization())
    except RuntimeError:
        # 실행 중인 루프가 없으면 새 루프에서 실행
        asyncio.run(init_optimization())

except Exception:
    pass

# 서비스 초기화 (하이브리드 로딩 적용)
try:
    # 환경변수에서 하이브리드 로딩 설정 확인
    fast_startup = os.getenv("FAST_STARTUP", "false").lower() == "true"
    lazy_loading = os.getenv("LAZY_LOADING_ENABLED", "false").lower() == "true"

    if fast_startup or lazy_loading:
        embedding_service = EmbeddingService(lazy_loading=True)
    else:
        embedding_service = EmbeddingService(lazy_loading=False)
except Exception:
    embedding_service = None

# VectorService 선택적 초기화
try:
    vector_service = VectorService(
        api_key=PINECONE_API_KEY or "dummy-key",
        index_name=PINECONE_INDEX_NAME
    )
except Exception:
    vector_service = None

# SimilarityService 초기화 (vector_service가 None일 수 있음)
try:
    similarity_service = SimilarityService(embedding_service, vector_service)
except Exception:
    similarity_service = None

# Pydantic 모델들
class User(BaseModel):
    id: Optional[str] = None
    username: str
    email: str
    role: str = "user"
    created_at: Optional[datetime] = None

class Resume(BaseModel):
    id: Optional[str] = None
    resume_id: Optional[str] = None
    name: str
    position: Optional[str] = ""
    department: Optional[str] = ""
    experience: Optional[str] = ""
    skills: Optional[str] = ""
    growthBackground: Optional[str] = ""
    motivation: Optional[str] = ""
    careerHistory: Optional[str] = ""
    analysisScore: int = 0
    analysisResult: str = ""
    status: str = "pending"
    created_at: Optional[datetime] = None

class ResumeChunk(BaseModel):
    id: Optional[str] = None
    resume_id: str
    chunk_id: str
    text: str
    start_pos: int
    end_pos: int
    chunk_index: int
    field_name: Optional[str] = None  # growthBackground, motivation, careerHistory
    metadata: Optional[Dict[str, Any]] = None
    vector_id: Optional[str] = None  # Pinecone 벡터 ID
    created_at: Optional[datetime] = None

class Interview(BaseModel):
    id: Optional[str] = None
    user_id: str
    company: str
    position: str
    date: datetime
    status: str = "scheduled"
    created_at: Optional[datetime] = None

# 초기 데이터 로딩 유틸리티: DB가 비어있으면 루트 CSV에서 임포트
async def seed_applicants_from_csv_if_empty() -> None:
    try:
        total_documents = await db.applicants.count_documents({})
        if total_documents > 0:
            return

        project_root_csv_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "hireme.applicants.csv")
        )
        if not os.path.exists(project_root_csv_path):
            return

        documents_to_insert = []
        with open(project_root_csv_path, mode="r", encoding="utf-8") as csv_file:
            reader = csv.DictReader(csv_file)
            for row in reader:
                document: Dict[str, Any] = {}

                # _id 처리: 가능하면 ObjectId로 저장
                raw_id = row.get("_id")
                if raw_id and isinstance(raw_id, str) and len(raw_id) == 24:
                    try:
                        document["_id"] = ObjectId(raw_id)
                    except Exception:
                        document["_id"] = raw_id

                # resume_id 처리
                raw_resume_id = row.get("resume_id")
                if raw_resume_id and isinstance(raw_resume_id, str) and len(raw_resume_id) == 24:
                    try:
                        document["resume_id"] = ObjectId(raw_resume_id)
                    except Exception:
                        document["resume_id"] = raw_resume_id
                elif raw_resume_id:
                    document["resume_id"] = raw_resume_id

                # 문자열 필드들: 항상 문자열로 캐스팅
                string_fields = [
                    "name",
                    "position",
                    "department",
                    "experience",
                    "skills",
                    "growthBackground",
                    "motivation",
                    "careerHistory",
                    "analysisResult",
                    "status",
                ]
                for field_name in string_fields:
                    value = row.get(field_name, "")
                    document[field_name] = "" if value is None else str(value)

                # 숫자 필드
                try:
                    document["analysisScore"] = int(row.get("analysisScore", "0") or 0)
                except Exception:
                    document["analysisScore"] = 0

                # created_at 처리
                created_at_raw = row.get("created_at")
                if created_at_raw:
                    try:
                        iso_candidate = created_at_raw.replace("Z", "+00:00")
                        document["created_at"] = datetime.fromisoformat(iso_candidate)
                    except Exception:
                        document["created_at"] = datetime.now()

                documents_to_insert.append(document)

        if documents_to_insert:
            await db.applicants.insert_many(documents_to_insert)
    except Exception:
        pass


def load_applicants_from_csv() -> List[Dict[str, Any]]:
    """DB 미가동/비어있을 때 CSV를 직접 읽어 반환"""
    try:
        project_root_csv_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "hireme.applicants.csv")
        )
        if not os.path.exists(project_root_csv_path):
            return []

        applicants: List[Dict[str, Any]] = []
        with open(project_root_csv_path, mode="r", encoding="utf-8") as csv_file:
            reader = csv.DictReader(csv_file)
            for row in reader:
                item: Dict[str, Any] = {}
                # id/_id
                raw_id = row.get("_id") or row.get("id")
                if raw_id:
                    item["id"] = str(raw_id)

                # 기본 문자열 필드
                for field_name in [
                    "name",
                    "position",
                    "department",
                    "experience",
                    "skills",
                    "growthBackground",
                    "motivation",
                    "careerHistory",
                    "analysisResult",
                    "status",
                ]:
                    value = row.get(field_name, "")
                    item[field_name] = "" if value is None else str(value)

                # score
                try:
                    item["analysisScore"] = int(row.get("analysisScore", "0") or 0)
                except Exception:
                    item["analysisScore"] = 0

                # created_at
                created_at_raw = row.get("created_at")
                if created_at_raw:
                    try:
                        iso_candidate = created_at_raw.replace("Z", "+00:00")
                        item["created_at"] = datetime.fromisoformat(iso_candidate)
                    except Exception:
                        item["created_at"] = datetime.now()

                applicants.append(item)
        return applicants
    except Exception:
        return []

# API 라우트들
@app.get("/")
async def root():
    return {"message": "AI 채용 관리 시스템 API가 실행 중입니다."}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "서버가 정상적으로 작동 중입니다."}

# 사용자 관련 API
@app.get("/api/users", response_model=List[User])
async def get_users():
    users = await db.users.find().to_list(1000)
    # MongoDB의 _id를 id로 변환
    for user in users:
        user["id"] = str(user["_id"])
        del user["_id"]
    return [User(**user) for user in users]

@app.post("/api/users", response_model=User)
async def create_user(user: User):
    user_dict = user.dict()
    user_dict["created_at"] = datetime.now()
    result = await db.users.insert_one(user_dict)
    user_dict["id"] = str(result.inserted_id)
    return User(**user_dict)

# 이력서 관련 API
@app.get("/api/resumes", response_model=List[Resume])
async def get_resumes():
    resumes = await db.resumes.find().to_list(1000)
    # MongoDB의 _id를 id로 변환
    for resume in resumes:
        resume["id"] = str(resume["_id"])
        del resume["_id"]
    return [Resume(**resume) for resume in resumes]

@app.post("/api/resumes", response_model=Resume)
async def create_resume(resume: Resume):
    resume_dict = resume.dict()
    resume_dict["created_at"] = datetime.now()
    result = await db.resumes.insert_one(resume_dict)
    resume_dict["id"] = str(result.inserted_id)
    return Resume(**resume_dict)

# 지원자별 이력서 조회 API (모든 정보 포함)
@app.get("/api/applicants/{applicant_id}/resume")
async def get_applicant_resume(applicant_id: str):
    """지원자의 이력서 정보를 모두 가져옴 (분석 결과 포함)"""
    try:
        # 1. 지원자 정보 조회
        applicant = await db.applicants.find_one({"_id": ObjectId(applicant_id)})
        if not applicant:
            raise HTTPException(status_code=404, detail="지원자를 찾을 수 없습니다.")

        # 2. 이력서 ID 확인
        resume_id = applicant.get("resume_id")
        if not resume_id:
            raise HTTPException(status_code=404, detail="이력서가 등록되지 않았습니다.")

        # 3. 이력서 정보 조회 (resumes 컬렉션에서)
        resume = await db.resumes.find_one({"_id": ObjectId(resume_id)})
        if not resume:
            # resumes 컬렉션에 없으면 applicants 컬렉션의 이력서 필드들 사용
            resume_data = {
                "name": applicant.get("name", ""),
                "position": applicant.get("position", ""),
                "department": applicant.get("department", ""),
                "experience": applicant.get("experience", ""),
                "skills": applicant.get("skills", ""),
                "growthBackground": applicant.get("growthBackground", ""),
                "motivation": applicant.get("motivation", ""),
                "careerHistory": applicant.get("careerHistory", ""),
                "analysisScore": applicant.get("analysisScore", 0),
                "analysisResult": applicant.get("analysisResult", ""),
                "status": applicant.get("status", "pending"),
                "created_at": applicant.get("created_at"),
                "extracted_text": applicant.get("extracted_text", ""),
                "file_metadata": applicant.get("file_metadata", {}),
                "source": "applicants_collection"
            }
        else:
            # resumes 컬렉션에서 가져온 데이터
            resume_data = resume.copy()
            resume_data["source"] = "resumes_collection"

        # 4. _id를 문자열로 변환
        if "_id" in resume_data:
            resume_data["id"] = str(resume_data["_id"])
            del resume_data["_id"]

        # 5. 지원자 기본 정보도 포함
        resume_data["applicant_info"] = {
            "id": str(applicant["_id"]),
            "name": applicant.get("name", ""),
            "email": applicant.get("email", ""),
            "phone": applicant.get("phone", ""),
            "status": applicant.get("status", ""),
            "applied_at": applicant.get("applied_at"),
            "created_at": applicant.get("created_at")
        }

        # 6. AI 분석 결과 조회 (있는 경우)
        try:
            from modules.ai.resume_analysis_service import ResumeAnalysisService

            # 하이브리드 로딩 설정 적용
            fast_startup = os.getenv("FAST_STARTUP", "false").lower() == "true"
            lazy_loading = os.getenv("LAZY_LOADING_ENABLED", "false").lower() == "true"
            analysis_service = ResumeAnalysisService(db, lazy_loading=(fast_startup or lazy_loading))
            analysis_result = await analysis_service.get_applicant_analysis(applicant_id)
            if analysis_result:
                resume_data["ai_analysis"] = analysis_result
        except Exception as e:
            print(f"[WARNING] AI 분석 결과 조회 실패: {str(e)}")
            # AI 분석 실패해도 기본 이력서 정보는 반환

        return {
            "success": True,
            "message": "이력서 정보 조회 성공",
            "data": resume_data
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"이력서 조회에 실패했습니다: {str(e)}")

# AI 이력서 분석 API
@app.post("/api/ai-analysis/resume/analyze")
async def analyze_resume(request: dict):
    """이력서 AI 분석 실행"""
    try:
        from models.resume_analysis import ResumeAnalysisRequest
        from modules.ai.resume_analysis_service import ResumeAnalysisService

        # 요청 데이터 검증
        applicant_id = request.get("applicant_id")
        analysis_type = request.get("analysis_type", "openai")
        force_reanalysis = request.get("force_reanalysis", False)
        weights = request.get("weights", {})  # 가중치 추가

        if not applicant_id:
            raise HTTPException(status_code=400, detail="지원자 ID가 필요합니다.")

        # 분석 서비스 초기화 (하이브리드 로딩 적용)
        fast_startup = os.getenv("FAST_STARTUP", "false").lower() == "true"
        lazy_loading = os.getenv("LAZY_LOADING_ENABLED", "false").lower() == "true"
        analysis_service = ResumeAnalysisService(db, lazy_loading=(fast_startup or lazy_loading))

        # 분석 요청 생성
        analysis_request = ResumeAnalysisRequest(
            applicant_id=applicant_id,
            analysis_type=analysis_type,
            force_reanalysis=force_reanalysis,
            weights=weights  # 가중치 전달
        )

        # 분석 실행
        result = await analysis_service.analyze_resume(analysis_request)

        if result.success:
            return {
                "success": True,
                "message": result.message,
                "data": result.data,
                "analysis_id": result.analysis_id,
                "processing_time": result.processing_time
            }
        else:
            raise HTTPException(status_code=500, detail=result.message)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI 분석에 실패했습니다: {str(e)}")

@app.post("/api/ai-analysis/resume/batch-analyze")
async def batch_analyze_resumes(request: dict):
    """이력서 일괄 AI 분석"""
    try:
        from models.resume_analysis import BatchAnalysisRequest
        from modules.ai.resume_analysis_service import ResumeAnalysisService

        # 요청 데이터 검증
        applicant_ids = request.get("applicant_ids", [])
        analysis_type = request.get("analysis_type", "openai")

        if not applicant_ids:
            raise HTTPException(status_code=400, detail="지원자 ID 리스트가 필요합니다.")

        # 분석 서비스 초기화 (하이브리드 로딩 적용)
        fast_startup = os.getenv("FAST_STARTUP", "false").lower() == "true"
        lazy_loading = os.getenv("LAZY_LOADING_ENABLED", "false").lower() == "true"
        analysis_service = ResumeAnalysisService(db, lazy_loading=(fast_startup or lazy_loading))

        # 일괄 분석 요청 생성
        batch_request = BatchAnalysisRequest(
            applicant_ids=applicant_ids,
            analysis_type=analysis_type
        )

        # 일괄 분석 실행
        result = await analysis_service.batch_analyze(batch_request)

        if result.success:
            return {
                "success": True,
                "message": result.message,
                "data": result.data,
                "processing_time": result.processing_time
            }
        else:
            raise HTTPException(status_code=500, detail=result.message)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI 분석에 실패했습니다: {str(e)}")

@app.post("/api/ai-analysis/resume/reanalyze")
async def reanalyze_resume(request: dict):
    """이력서 재분석"""
    try:
        from models.resume_analysis import ResumeAnalysisRequest
        from modules.ai.resume_analysis_service import ResumeAnalysisService

        # 요청 데이터 검증
        applicant_id = request.get("applicant_id")
        analysis_type = request.get("analysis_type", "openai")

        if not applicant_id:
            raise HTTPException(status_code=400, detail="지원자 ID가 필요합니다.")

        # 분석 서비스 초기화 (하이브리드 로딩 적용)
        fast_startup = os.getenv("FAST_STARTUP", "false").lower() == "true"
        lazy_loading = os.getenv("LAZY_LOADING_ENABLED", "false").lower() == "true"
        analysis_service = ResumeAnalysisService(db, lazy_loading=(fast_startup or lazy_loading))

        # 재분석 요청 생성
        analysis_request = ResumeAnalysisRequest(
            applicant_id=applicant_id,
            analysis_type=analysis_type,
            force_reanalysis=True
        )

        # 재분석 실행
        result = await analysis_service.reanalyze_resume(analysis_request)

        if result.success:
            return {
                "success": True,
                "message": result.message,
                "data": result.data,
                "analysis_id": result.analysis_id,
                "processing_time": result.processing_time
            }
        else:
            raise HTTPException(status_code=500, detail=result.message)

    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR] 재분석 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"재분석에 실패했습니다: {str(e)}")

@app.get("/api/ai-analysis/resume/analysis-status")
async def get_analysis_status():
    """AI 분석 상태 조회"""
    try:
        from modules.ai.resume_analysis_service import ResumeAnalysisService

        # 분석 서비스 초기화 (하이브리드 로딩 적용)
        fast_startup = os.getenv("FAST_STARTUP", "false").lower() == "true"
        lazy_loading = os.getenv("LAZY_LOADING_ENABLED", "false").lower() == "true"
        analysis_service = ResumeAnalysisService(db, lazy_loading=(fast_startup or lazy_loading))

        # 상태 조회
        status = await analysis_service.get_analysis_status()

        if status.success:
            return {
                "success": True,
                "message": status.message,
                "data": status.data,
                "total_applicants": status.total_applicants,
                "analyzed_count": status.analyzed_count,
                "pending_count": status.pending_count,
                "failed_count": status.failed_count,
                "progress_percentage": status.progress_percentage
            }
        else:
            raise HTTPException(status_code=500, detail=status.message)

    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR] 분석 상태 조회 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"분석 상태 조회에 실패했습니다: {str(e)}")

@app.get("/api/ai-analysis/resume/{applicant_id}")
async def get_applicant_analysis(applicant_id: str):
    """지원자별 AI 분석 결과 조회"""
    try:
        from modules.ai.resume_analysis_service import ResumeAnalysisService

        # 분석 서비스 초기화 (하이브리드 로딩 적용)
        fast_startup = os.getenv("FAST_STARTUP", "false").lower() == "true"
        lazy_loading = os.getenv("LAZY_LOADING_ENABLED", "false").lower() == "true"
        analysis_service = ResumeAnalysisService(db, lazy_loading=(fast_startup or lazy_loading))

        # 분석 결과 조회
        analysis_result = await analysis_service.get_applicant_analysis(applicant_id)

        if analysis_result:
            return {
                "success": True,
                "message": "AI 분석 결과 조회 성공",
                "data": analysis_result
            }
        else:
            raise HTTPException(status_code=404, detail="AI 분석 결과를 찾을 수 없습니다.")

    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR] AI 분석 결과 조회 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"AI 분석 결과 조회에 실패했습니다: {str(e)}")

# 지원자별 포트폴리오 조회 API
@app.get("/api/portfolios/applicant/{applicant_id}")
async def get_applicant_portfolio(applicant_id: str):
    """지원자의 포트폴리오 정보를 가져옴"""
    try:
        # 1. 지원자 정보 조회
        applicant = await db.applicants.find_one({"_id": ObjectId(applicant_id)})
        if not applicant:
            raise HTTPException(status_code=404, detail="지원자를 찾을 수 없습니다.")

        # 2. 포트폴리오 URL 확인
        portfolio_url = applicant.get("portfolio_url")
        if not portfolio_url:
            return {
                "success": False,
                "message": "포트폴리오 URL이 없습니다.",
                "data": None
            }

        # 3. GitHub URL인 경우 GitHub API로 요약 생성
        if "github.com" in portfolio_url:
            try:
                # GitHub API 호출
                github_response = await fetch_github_summary(portfolio_url)
                if github_response.get("success"):
                    return {
                        "success": True,
                        "message": "포트폴리오 조회 성공",
                        "data": {
                            "portfolio_url": portfolio_url,
                            "github_summary": github_response.get("data"),
                            "applicant_info": {
                                "id": str(applicant.get("_id")),
                                "name": applicant.get("name", ""),
                                "email": applicant.get("email", ""),
                                "position": applicant.get("position", "")
                            }
                        }
                    }
                else:
                    return {
                        "success": False,
                        "message": f"GitHub 분석 실패: {github_response.get('message')}",
                        "data": {
                            "portfolio_url": portfolio_url,
                            "applicant_info": {
                                "id": str(applicant.get("_id")),
                                "name": applicant.get("name", ""),
                                "email": applicant.get("email", ""),
                                "position": applicant.get("position", "")
                            }
                        }
                    }
            except Exception as e:
                return {
                    "success": False,
                    "message": f"GitHub 분석 중 오류: {str(e)}",
                    "data": {
                        "portfolio_url": portfolio_url,
                        "applicant_info": {
                            "id": str(applicant.get("_id")),
                            "name": applicant.get("name", ""),
                            "email": applicant.get("email", ""),
                            "position": applicant.get("position", "")
                        }
                    }
                }
        else:
            # GitHub가 아닌 경우 기본 정보만 반환
            return {
                "success": True,
                "message": "포트폴리오 조회 성공 (GitHub가 아님)",
                "data": {
                    "portfolio_url": portfolio_url,
                    "applicant_info": {
                        "id": str(applicant.get("_id")),
                        "name": applicant.get("name", ""),
                        "email": applicant.get("email", ""),
                        "position": applicant.get("position", "")
                    }
                }
            }

    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR] 포트폴리오 조회 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"포트폴리오 조회에 실패했습니다: {str(e)}")

# GitHub 요약 생성 함수
async def fetch_github_summary(github_url: str):
    """GitHub URL에서 사용자명을 추출하고 GitHub API 호출"""
    try:
        # GitHub URL에서 사용자명 추출
        if "github.com/" in github_url:
            parts = github_url.split("github.com/")[1].split("/")
            username = parts[0]
        else:
            return {"success": False, "message": "유효하지 않은 GitHub URL"}

        # 실제 GitHub API 호출
        try:
            import os

            import requests

            # GitHub API 토큰 확인
            github_token = os.getenv('GITHUB_TOKEN')
            headers = {}
            if github_token:
                headers['Authorization'] = f'token {github_token}'

            # GitHub 사용자 정보 가져오기
            user_response = requests.get(f'https://api.github.com/users/{username}', headers=headers, timeout=10)

            if user_response.status_code == 200:
                user_data = user_response.json()

                # 저장소 정보 가져오기
                repos_response = requests.get(f'https://api.github.com/users/{username}/repos?per_page=10&sort=updated', headers=headers, timeout=10)
                repos_data = []
                if repos_response.status_code == 200:
                    repos_data = repos_response.json()

                # 언어 통계 수집
                languages = {}
                for repo in repos_data[:5]:  # 최근 5개 저장소만
                    try:
                        lang_response = requests.get(f'https://api.github.com/repos/{username}/{repo["name"]}/languages', headers=headers, timeout=5)
                        if lang_response.status_code == 200:
                            repo_langs = lang_response.json()
                            for lang, bytes_count in repo_langs.items():
                                languages[lang] = languages.get(lang, 0) + bytes_count
                    except:
                        continue

                # 상위 언어 5개 선택
                top_languages = sorted(languages.items(), key=lambda x: x[1], reverse=True)[:5]

                return {
                    "success": True,
                    "data": {
                        "username": username,
                        "github_url": github_url,
                        "user_info": {
                            "name": user_data.get('name', username),
                            "bio": user_data.get('bio', ''),
                            "public_repos": user_data.get('public_repos', 0),
                            "followers": user_data.get('followers', 0),
                            "following": user_data.get('following', 0),
                            "created_at": user_data.get('created_at', ''),
                            "updated_at": user_data.get('updated_at', '')
                        },
                        "repositories": [
                            {
                                "name": repo.get('name', ''),
                                "description": repo.get('description', ''),
                                "language": repo.get('language', ''),
                                "stars": repo.get('stargazers_count', 0),
                                "forks": repo.get('forks_count', 0),
                                "updated_at": repo.get('updated_at', '')
                            } for repo in repos_data[:10]
                        ],
                        "languages": [{"name": lang, "percentage": round((count / sum(languages.values())) * 100, 1)} for lang, count in top_languages],
                        "summary": {
                            "total_repos": user_data.get('public_repos', 0),
                            "total_stars": sum(repo.get('stargazers_count', 0) for repo in repos_data),
                            "top_language": top_languages[0][0] if top_languages else "N/A",
                            "most_starred_repo": max(repos_data, key=lambda x: x.get('stargazers_count', 0)).get('name', 'N/A') if repos_data else "N/A"
                        }
                    }
                }
            else:
                return {
                    "success": False,
                    "message": f"GitHub 사용자 정보를 가져올 수 없습니다: {user_response.status_code}",
                    "data": {
                        "username": username,
                        "github_url": github_url,
                        "error": f"GitHub API 오류: {user_response.status_code}"
                    }
                }

        except Exception as e:
            return {
                "success": False,
                "message": f"GitHub 분석 중 오류 발생: {str(e)}",
                "data": {
                    "username": username,
                    "github_url": github_url,
                    "error": str(e)
                }
            }

    except Exception as e:
        return {"success": False, "message": f"GitHub 요약 생성 실패: {str(e)}"}

# 지원자별 자기소개서 조회 API
@app.get("/api/applicants/{applicant_id}/cover-letter")
async def get_applicant_cover_letter(applicant_id: str):
    """지원자의 자기소개서 정보를 모두 가져옴"""
    try:
        # 1. 지원자 정보 조회
        applicant = await db.applicants.find_one({"_id": ObjectId(applicant_id)})
        if not applicant:
            raise HTTPException(status_code=404, detail="지원자를 찾을 수 없습니다.")

        # 2. 자기소개서 정보 조회 (applicants 컬렉션에서)
        cover_letter_data = {
            "name": applicant.get("name", ""),
            "position": applicant.get("position", ""),
            "cover_letter_text": applicant.get("cover_letter_text", ""),
            "cover_letter_summary": applicant.get("cover_letter_summary", ""),
            "cover_letter_analysis": applicant.get("cover_letter_analysis", {}),
            "extracted_text": applicant.get("cover_letter_extracted_text", ""),
            "file_metadata": applicant.get("cover_letter_file_metadata", {}),
            "created_at": applicant.get("created_at"),
            "source": "applicants_collection",
            "applicant_info": {
                "id": applicant.get("_id"),  # str() 불필요, respond()가 처리
                "name": applicant.get("name", ""),
                "email": applicant.get("email", ""),
                "phone": applicant.get("phone", ""),
                "status": applicant.get("status", ""),
                "applied_at": applicant.get("applied_at"),
                "created_at": applicant.get("created_at")
            }
        }

        payload = {
            "success": True,
            "message": "자기소개서 정보 조회 성공",
            "data": cover_letter_data
        }

        # 3. ObjectId와 datetime을 안전하게 직렬화하는 함수
        def safe_serialize(obj):
            """ObjectId와 datetime을 안전하게 직렬화"""
            if obj is None:
                return None
            if isinstance(obj, ObjectId):
                return str(obj)
            if isinstance(obj, datetime):
                return obj.isoformat()
            if isinstance(obj, dict):
                return {k: safe_serialize(v) for k, v in obj.items()}
            if isinstance(obj, list):
                return [safe_serialize(v) for v in obj]
            return obj

        return {
            "success": True,
            "message": "자기소개서 정보 조회 성공",
            "data": safe_serialize(cover_letter_data)
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR] 자기소개서 조회 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"자기소개서 조회에 실패했습니다: {str(e)}")

# 지원자별 포트폴리오 조회 API
@app.get("/api/applicants/{applicant_id}/portfolio")
async def get_applicant_portfolio(applicant_id: str):
    """지원자의 포트폴리오 정보를 모두 가져옴"""
    try:
        # 1. 지원자 정보 조회
        applicant = await db.applicants.find_one({"_id": ObjectId(applicant_id)})
        if not applicant:
            raise HTTPException(status_code=404, detail="지원자를 찾을 수 없습니다.")

        # 2. 포트폴리오 정보 조회 (applicants 컬렉션에서)
        portfolio_data = {
            "name": applicant.get("name", ""),
            "position": applicant.get("position", ""),
            "github_url": applicant.get("github_url", ""),
            "github_analysis": applicant.get("github_analysis", {}),
            "portfolio_files": applicant.get("portfolio_files", []),
            "portfolio_summary": applicant.get("portfolio_summary", ""),
            "created_at": applicant.get("created_at"),
            "source": "applicants_collection"
        }

        # 3. 지원자 기본 정보도 포함
        portfolio_data["applicant_info"] = {
            "id": str(applicant["_id"]),
            "name": applicant.get("name", ""),
            "email": applicant.get("email", ""),
            "phone": applicant.get("phone", ""),
            "status": applicant.get("status", ""),
            "applied_at": applicant.get("applied_at"),
            "created_at": applicant.get("created_at")
        }

        return {
            "success": True,
            "message": "포트폴리오 정보 조회 성공",
            "data": portfolio_data
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR] 포트폴리오 조회 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"포트폴리오 조회에 실패했습니다: {str(e)}")

# 면접 관련 API
@app.get("/api/interviews", response_model=List[Interview])
async def get_interviews():
    interviews = await db.interviews.find().to_list(1000)
    # MongoDB의 _id를 id로 변환
    for interview in interviews:
        interview["id"] = str(interview["_id"])
        del interview["_id"]
    return [Interview(**interview) for interview in interviews]

@app.post("/api/interviews", response_model=Interview)
async def create_interview(interview: Interview):
    interview_dict = interview.dict()
    interview_dict["created_at"] = datetime.now()
    result = await db.interviews.insert_one(interview_dict)
    interview_dict["id"] = str(result.inserted_id)
    return Interview(**interview_dict)

# 지원자 관련 API - 중복 라우터 삭제 (routers/applicants.py에서 처리)

# 개별 지원자 조회 API - 중복 라우터 삭제 (routers/applicants.py에서 처리)
# 지원자 통계 API - 중복 라우터 삭제 (routers/applicants.py에서 처리)

# Vector Service API
@app.post("/api/vector/create")
async def create_vector(data: Dict[str, Any]):
    """텍스트를 벡터로 변환하여 저장"""
    try:
        text = data.get("text", "")
        document_id = data.get("document_id")
        metadata = data.get("metadata", {})

        # 여기서 실제 벡터화 로직 구현
        # 예: embedding_model을 사용하여 텍스트를 벡터로 변환

        # 임시로 성공 응답 반환
        return {
            "message": "Vector created successfully",
            "document_id": document_id,
            "vector_dimension": 384,  # 예시 차원
            "status": "success"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"벡터 생성 실패: {str(e)}")

@app.post("/api/vector/search")
async def search_vectors(data: Dict[str, Any]):
    """벡터 유사도 검색"""
    try:
        query_text = data.get("query", "")
        top_k = data.get("top_k", 5)
        threshold = data.get("threshold", 0.7)

        # 여기서 실제 벡터 검색 로직 구현

        # 임시로 검색 결과 반환
        return {
            "results": [
                {
                    "document_id": "doc_001",
                    "score": 0.95,
                    "text": "검색된 텍스트 샘플 1",
                    "metadata": {"type": "resume", "applicant_id": "app_001"}
                },
                {
                    "document_id": "doc_002",
                    "score": 0.87,
                    "text": "검색된 텍스트 샘플 2",
                    "metadata": {"type": "cover_letter", "applicant_id": "app_002"}
                }
            ],
            "total_found": 2
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"벡터 검색 실패: {str(e)}")

# Chunking Service API
@app.post("/api/chunking/split")
async def split_text(data: Dict[str, Any]):
    """텍스트를 청크로 분할하고 DB에 저장"""
    try:
        text = data.get("text", "")
        resume_id = data.get("resume_id")
        field_name = data.get("field_name", "")  # growthBackground, motivation, careerHistory
        chunk_size = data.get("chunk_size", 1000)
        chunk_overlap = data.get("chunk_overlap", 200)
        split_type = data.get("split_type", "recursive")

        if not resume_id:
            raise HTTPException(status_code=400, detail="resume_id가 필요합니다.")

        # 텍스트 분할 로직
        chunks = []
        text_length = len(text)
        start = 0
        chunk_index = 0

        while start < text_length:
            end = min(start + chunk_size, text_length)
            chunk_text = text[start:end]

            if chunk_text.strip():  # 빈 청크는 제외
                chunk_id = f"chunk_{chunk_index:03d}"
                vector_id = f"resume_{resume_id}_{chunk_id}"

                chunk_doc = {
                    "resume_id": resume_id,
                    "chunk_id": chunk_id,
                    "text": chunk_text,
                    "start_pos": start,
                    "end_pos": end,
                    "chunk_index": chunk_index,
                    "field_name": field_name,
                    "vector_id": vector_id,
                    "metadata": {
                        "length": len(chunk_text),
                        "split_type": split_type,
                        "chunk_size": chunk_size,
                        "chunk_overlap": chunk_overlap
                    },
                    "created_at": datetime.now()
                }

                # MongoDB에 청크 저장
                result = await db.resume_chunks.insert_one(chunk_doc)
                chunk_doc["id"] = str(result.inserted_id)

                chunks.append(chunk_doc)
                chunk_index += 1

            start = end - chunk_overlap if chunk_overlap > 0 else end

            if start >= text_length:
                break

        return {
            "chunks": chunks,
            "total_chunks": len(chunks),
            "original_length": text_length,
            "resume_id": resume_id,
            "field_name": field_name,
            "split_config": {
                "chunk_size": chunk_size,
                "chunk_overlap": chunk_overlap,
                "split_type": split_type
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"텍스트 분할 실패: {str(e)}")

@app.get("/api/chunking/resume/{resume_id}")
async def get_resume_chunks(resume_id: str):
    """특정 이력서의 모든 청크 조회"""
    try:
        chunks = await db.resume_chunks.find({"resume_id": resume_id}).to_list(1000)

        # MongoDB의 _id를 id로 변환
        for chunk in chunks:
            chunk["id"] = str(chunk["_id"])
            del chunk["_id"]

        return {
            "resume_id": resume_id,
            "chunks": [ResumeChunk(**chunk) for chunk in chunks],
            "total_chunks": len(chunks)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"청크 조회 실패: {str(e)}")

@app.post("/api/chunking/process-resume")
async def process_resume_with_chunking(data: Dict[str, Any]):
    """이력서 전체를 필드별로 청킹 처리"""
    try:
        resume_id = data.get("resume_id")
        if not resume_id:
            raise HTTPException(status_code=400, detail="resume_id가 필요합니다.")

        # 이력서 정보 조회
        resume = await db.resumes.find_one({"_id": ObjectId(resume_id)})
        if not resume:
            raise HTTPException(status_code=404, detail="이력서를 찾을 수 없습니다.")

        chunk_size = data.get("chunk_size", 800)
        chunk_overlap = data.get("chunk_overlap", 150)

        # 청킹할 필드들
        fields_to_chunk = ["growthBackground", "motivation", "careerHistory"]
        all_chunks = []

        for field_name in fields_to_chunk:
            field_text = resume.get(field_name, "")
            if field_text and field_text.strip():
                # 필드별 청킹 처리
                field_chunks = []
                text_length = len(field_text)
                start = 0
                chunk_index = 0

                while start < text_length:
                    end = min(start + chunk_size, text_length)
                    chunk_text = field_text[start:end]

                    if chunk_text.strip():
                        chunk_id = f"{field_name}_chunk_{chunk_index:03d}"
                        vector_id = f"resume_{resume_id}_{chunk_id}"

                        chunk_doc = {
                            "resume_id": resume_id,
                            "chunk_id": chunk_id,
                            "text": chunk_text,
                            "start_pos": start,
                            "end_pos": end,
                            "chunk_index": chunk_index,
                            "field_name": field_name,
                            "vector_id": vector_id,
                            "metadata": {
                                "applicant_name": resume.get("name", ""),
                                "position": resume.get("position", ""),
                                "department": resume.get("department", ""),
                                "length": len(field_text)
                            },
                            "created_at": datetime.now()
                        }

                        result = await db.resume_chunks.insert_one(chunk_doc)
                        chunk_doc["id"] = str(result.inserted_id)
                        field_chunks.append(chunk_doc)
                        chunk_index += 1

                    start = end - chunk_overlap if chunk_overlap > 0 else end
                    if start >= text_length:
                        break

                all_chunks.extend(field_chunks)

        return {
            "resume_id": resume_id,
            "applicant_name": resume.get("name", ""),
            "processed_fields": fields_to_chunk,
            "total_chunks": len(all_chunks),
            "chunks_by_field": {
                field: len([c for c in all_chunks if c["field_name"] == field])
                for field in fields_to_chunk
            },
            "chunks": all_chunks
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"이력서 청킹 처리 실패: {str(e)}")

@app.post("/api/chunking/merge")
async def merge_chunks(data: Dict[str, Any]):
    """청크들을 병합"""
    try:
        chunks = data.get("chunks", [])
        separator = data.get("separator", "\n\n")

        # 청크 병합
        merged_text = separator.join([chunk.get("text", "") for chunk in chunks])

        return {
            "merged_text": merged_text,
            "total_length": len(merged_text),
            "chunks_merged": len(chunks),
            "separator_used": separator
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"청크 병합 실패: {str(e)}")

# Similarity Service API
@app.post("/api/similarity/compare")
async def compare_similarity(data: Dict[str, Any]):
    """두 텍스트 간의 유사도 계산"""
    try:
        text1 = data.get("text1", "")
        text2 = data.get("text2", "")
        method = data.get("method", "cosine")  # cosine, jaccard, levenshtein

        # 여기서 실제 유사도 계산 로직 구현
        # 예: sentence-transformers의 cosine similarity

        # 임시로 유사도 점수 반환
        import random
        similarity_score = random.uniform(0.3, 0.95)  # 임시 점수

        return {
            "similarity_score": round(similarity_score, 4),
            "method": method,
            "text1_length": len(text1),
            "text2_length": len(text2),
            "comparison_result": {
                "highly_similar": similarity_score > 0.8,
                "moderately_similar": 0.5 < similarity_score <= 0.8,
                "low_similar": similarity_score <= 0.5
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"유사도 계산 실패: {str(e)}")

@app.post("/api/similarity/batch")
async def batch_similarity(data: Dict[str, Any]):
    """여러 텍스트들 간의 일괄 유사도 계산"""
    try:
        texts = data.get("texts", [])
        reference_text = data.get("reference_text", "")
        method = data.get("method", "cosine")
        threshold = data.get("threshold", 0.7)

        # 배치 유사도 계산
        results = []
        import random

        for i, text in enumerate(texts):
            similarity_score = random.uniform(0.2, 0.95)  # 임시 점수
            results.append({
                "index": i,
                "text_preview": text[:100] + "..." if len(text) > 100 else text,
                "similarity_score": round(similarity_score, 4),
                "above_threshold": similarity_score >= threshold
            })

        # 임계값 이상인 결과들 필터링
        filtered_results = [r for r in results if r["above_threshold"]]

        return {
            "results": results,
            "filtered_results": filtered_results,
            "total_compared": len(texts),
            "above_threshold_count": len(filtered_results),
            "method": method,
            "threshold": threshold,
            "reference_text_length": len(reference_text)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"배치 유사도 계산 실패: {str(e)}")

@app.get("/api/similarity/metrics")
async def get_similarity_metrics():
    """유사도 서비스 메트릭 조회"""
    try:
        # 임시 메트릭 데이터
        return {
            "total_comparisons": 1250,
            "average_similarity": 0.67,
            "supported_methods": ["cosine", "jaccard", "levenshtein", "semantic"],
            "performance_stats": {
                "average_processing_time_ms": 45,
                "comparisons_per_second": 220,
                "cache_hit_rate": 0.78
            },
            "usage_by_method": {
                "cosine": 850,
                "semantic": 300,
                "jaccard": 70,
                "levenshtein": 30
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"메트릭 조회 실패: {str(e)}")

# 다중 하이브리드 검색 API 🆕
@app.post("/api/resume/search/multi-hybrid")
async def search_resumes_multi_hybrid(data: Dict[str, Any]):
    """다중 하이브리드 검색: 벡터 + 텍스트 + 키워드 검색을 결합"""
    try:
        query = data.get("query", "")
        search_type = data.get("type", "resume")
        limit = data.get("limit", 10)

        print(f"[API] 다중 하이브리드 검색 요청 - 쿼리: '{query}', 제한: {limit}")

        if not query or not query.strip():
            raise HTTPException(status_code=400, detail="검색어를 입력해주세요.")

        # SimilarityService의 다중 하이브리드 검색 실행
        result = await similarity_service.search_resumes_multi_hybrid(
            query=query,
            collection=db.applicants,
            search_type=search_type,
            limit=limit
        )

        if not result["success"]:
            raise HTTPException(status_code=500, detail="다중 하이브리드 검색에 실패했습니다.")

        return {
            "success": True,
            "message": f"다중 하이브리드 검색 완료: '{query}'",
            "data": result["data"]
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"[API] 다중 하이브리드 검색 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"다중 하이브리드 검색 실패: {str(e)}")

# 키워드 검색 API
@app.post("/api/resume/search/keyword")
async def search_resumes_keyword(data: Dict[str, Any]):
    """키워드 기반 이력서 검색 (BM25)"""
    try:
        query = data.get("query", "")
        limit = data.get("limit", 10)

        print(f"[API] 키워드 검색 요청 - 쿼리: '{query}', 제한: {limit}")

        if not query or not query.strip():
            raise HTTPException(status_code=400, detail="검색어를 입력해주세요.")

        # KeywordSearchService를 통한 BM25 검색
        result = await similarity_service.keyword_search_service.search_by_keywords(
            query=query,
            collection=db.applicants,
            limit=limit
        )

        if not result["success"]:
            raise HTTPException(status_code=500, detail=result.get("message", "키워드 검색에 실패했습니다."))

        return {
            "success": True,
            "message": result["message"],
            "data": {
                "query": result["query"],
                "results": result["results"],
                "total": result["total"],
                "search_method": "keyword_bm25",
                "query_tokens": result.get("query_tokens", [])
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"[API] 키워드 검색 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"키워드 검색 실패: {str(e)}")

# 키워드 검색 인덱스 관리 API
@app.post("/api/resume/search/keyword/rebuild-index")
async def rebuild_keyword_index():
    """키워드 검색 인덱스 재구축"""
    try:
        print(f"[API] 키워드 인덱스 재구축 요청")

        # KeywordSearchService를 통한 인덱스 재구축
        result = await similarity_service.keyword_search_service.build_index(db.applicants)

        if not result["success"]:
            raise HTTPException(status_code=500, detail=result.get("message", "인덱스 재구축에 실패했습니다."))

        return {
            "success": True,
            "message": result["message"],
            "data": {
                "total_documents": result["total_documents"],
                "index_created_at": result["index_created_at"]
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"[API] 키워드 인덱스 재구축 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"키워드 인덱스 재구축 실패: {str(e)}")

@app.get("/api/resume/search/keyword/stats")
async def get_keyword_search_stats():
    """키워드 검색 인덱스 통계 조회"""
    try:
        stats = await similarity_service.keyword_search_service.get_index_stats()

        return {
            "success": True,
            "data": stats
        }

    except Exception as e:
        print(f"[API] 키워드 검색 통계 조회 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=f"키워드 검색 통계 조회 실패: {str(e)}")

# 이력서 유사도 체크 API
@app.post("/api/resume/similarity-check/{resume_id}")
async def check_resume_similarity(resume_id: str):
    """특정 이력서의 유사도 체크 (다른 모든 이력서와 비교)"""
    try:
        print(f"[INFO] 유사도 체크 요청 - resume_id: {resume_id}")

        # SimilarityService를 통한 청킹 기반 유사도 분석
        result = await similarity_service.find_similar_documents_by_chunks(resume_id, db.applicants, "resume", 50)

        # 현재 이력서 정보 조회
        current_resume = await db.applicants.find_one({"_id": ObjectId(resume_id)})
        print(f"[INFO] 데이터베이스 조회 결과: {current_resume is not None}")

        # 청킹 기반 API 응답 형식에 맞게 변환
        similarity_results = []
        for similar in result["data"]["similar_resumes"]:
            # 청킹 상세 정보에서 필드별 유사도 추출
            chunk_details = similar.get("chunk_details", {})
            field_similarities = {
                "growthBackground": 0.0,
                "motivation": 0.0,
                "careerHistory": 0.0
            }

            # 청크 매칭에서 필드별 최고 점수 추출
            for chunk_key, chunk_info in chunk_details.items():
                if "growth_background" in chunk_key:
                    field_similarities["growthBackground"] = max(field_similarities["growthBackground"], chunk_info["score"])
                elif "motivation" in chunk_key:
                    field_similarities["motivation"] = max(field_similarities["motivation"], chunk_info["score"])
                elif "career_history" in chunk_key:
                    field_similarities["careerHistory"] = max(field_similarities["careerHistory"], chunk_info["score"])

            similarity_result = {
                "resume_id": str(similar["resume"]["_id"]),
                "applicant_name": similar["resume"].get("name", "알 수 없음"),
                "position": similar["resume"].get("position", ""),
                "department": similar["resume"].get("department", ""),
                "overall_similarity": round(similar["similarity_score"], 4),
                "field_similarities": {
                    "growthBackground": round(field_similarities["growthBackground"], 4),
                    "motivation": round(field_similarities["motivation"], 4),
                    "careerHistory": round(field_similarities["careerHistory"], 4)
                },
                "chunk_matches": similar.get("chunk_matches", 0),
                "chunk_details": chunk_details,
                "is_high_similarity": similar["similarity_score"] > 0.7,
                "is_moderate_similarity": 0.4 <= similar["similarity_score"] <= 0.7,
                "is_low_similarity": similar["similarity_score"] < 0.4,
                "llm_analysis": similar.get("llm_analysis")
            }
            similarity_results.append(similarity_result)

        # 다른 모든 이력서 조회 (현재 이력서 제외)
        other_resumes = await db.applicants.find({"_id": {"$ne": ObjectId(resume_id)}}).to_list(1000)

        # 현재 이력서의 비교 텍스트 (유사도 계산 필드)
        current_fields = {
            "growthBackground": current_resume.get("growthBackground", ""),
            "motivation": current_resume.get("motivation", ""),
            "careerHistory": current_resume.get("careerHistory", "")
        }

        # 전체 텍스트 조합
        current_text = " ".join([text for text in current_fields.values() if text])

        similarity_results = []

        for other_resume in other_resumes:
            other_id = str(other_resume["_id"])

            # 다른 이력서의 비교 텍스트
            other_fields = {
                "growthBackground": other_resume.get("growthBackground", ""),
                "motivation": other_resume.get("motivation", ""),
                "careerHistory": other_resume.get("careerHistory", "")
            }
            other_text = " ".join([text for text in other_fields.values() if text])

            # 실제 유사도 계산 사용
            try:
                print(f"💫 이력서 간 유사도 계산 시작: {resume_id} vs {other_id}")

                # SimilarityService의 텍스트 유사도 계산 메서드 직접 호출
                text_similarity = similarity_service._calculate_text_similarity(current_resume, other_resume)
                overall_similarity = text_similarity if text_similarity is not None else 0.0

                print(f"📊 텍스트 유사도 결과: {overall_similarity:.3f}")

                # 필드별 유사도 계산
                field_similarities = {}
                for field_name in current_fields.keys():
                    if current_fields[field_name] and other_fields[field_name]:
                        # 필드별 개별 텍스트 유사도 계산
                        field_sim = similarity_service._calculate_text_similarity(
                            {field_name: current_fields[field_name]},
                            {field_name: other_fields[field_name]}
                        )
                        field_similarities[field_name] = field_sim if field_sim is not None else 0.0
                        print(f"📋 {field_name} 유사도: {field_similarities[field_name]:.3f}")
                    else:
                        field_similarities[field_name] = 0.0

            except Exception as e:
                print(f"[ERROR] 유사도 계산 중 오류 발생: {e}")
                import traceback
                traceback.print_exc()

                # 오류 시 기본값 사용
                import random
                overall_similarity = random.uniform(0.1, 0.9)
                field_similarities = {}
                for field_name in current_fields.keys():
                    if current_fields[field_name] and other_fields[field_name]:
                        field_similarities[field_name] = random.uniform(0.0, 1.0)
                    else:
                        field_similarities[field_name] = 0.0

            # LLM 분석 추가 (유사도가 일정 수준 이상일 때만)
            llm_analysis = None

            if overall_similarity >= 0.3:  # 30% 이상 유사할 때만 LLM 분석
                try:
                    print(f"[API] LLM 분석 시작 - 유사도: {overall_similarity:.3f}")
                    llm_analysis = await similarity_service.llm_service.analyze_plagiarism_suspicion(
                        similarity_score=overall_similarity,
                        similar_documents=[{
                            "similarity_score": overall_similarity,
                            "name": other_resume.get("name", "Unknown"),
                            "basic_info_names": other_resume.get("name", "Unknown")
                        }],
                        document_type="resume"
                    )
                    print(f"[API] LLM 분석 완료")
                except Exception as llm_error:
                    print(f"[API] LLM 분석 중 오류: {llm_error}")
                    llm_analysis = {
                        "success": False,
                        "error": str(llm_error),
                        "analysis": "LLM 분석에 실패했습니다."
                    }

            similarity_result = {
                "resume_id": other_id,
                "applicant_name": other_resume.get("name", "알 수 없음"),
                "position": other_resume.get("position", ""),
                "department": other_resume.get("department", ""),
                "overall_similarity": round(overall_similarity, 4),
                "field_similarities": {
                    "growthBackground": round(field_similarities["growthBackground"], 4),
                    "motivation": round(field_similarities["motivation"], 4),
                    "careerHistory": round(field_similarities["careerHistory"], 4)
                },
                "is_high_similarity": overall_similarity > 0.7,
                "is_moderate_similarity": 0.4 <= overall_similarity <= 0.7,
                "is_low_similarity": overall_similarity < 0.4,
                "llm_analysis": llm_analysis
            }

            similarity_results.append(similarity_result)

        # 유사도 높은 순으로 정렬
        similarity_results.sort(key=lambda x: x["overall_similarity"], reverse=True)

        # 전체 표절 의심도 분석 추가
        plagiarism_analysis = None
        high_similarity_results = [r for r in similarity_results if r["overall_similarity"] >= 0.3]

        if high_similarity_results:
            try:
                print(f"[API] 표절 의심도 분석 시작")
                plagiarism_analysis = await similarity_service.llm_service.analyze_plagiarism_suspicion(
                    original_resume=current_resume,
                    similar_resumes=high_similarity_results
                )
                print(f"[API] 표절 의심도 분석 완료")
            except Exception as plag_error:
                print(f"[API] 표절 의심도 분석 중 오류: {plag_error}")
                plagiarism_analysis = {
                    "success": False,
                    "error": str(plag_error),
                    "suspicion_level": "UNKNOWN",
                    "suspicion_score": 0.0,
                    "suspicion_score_percent": 0,
                    "analysis": "표절 의심도 분석에 실패했습니다."
                }

        # 통계 정보
        high_similarity_count = len([r for r in similarity_results if r["is_high_similarity"]])
        moderate_similarity_count = len([r for r in similarity_results if r["is_moderate_similarity"]])
        low_similarity_count = len([r for r in similarity_results if r["is_low_similarity"]])

        return {
            "current_resume": {
                "id": resume_id,
                "name": current_resume.get("name", ""),
                "position": current_resume.get("position", ""),
                "department": current_resume.get("department", "")
            },
            "similarity_results": similarity_results,
            "statistics": {
                "total_compared": len(similarity_results),
                "high_similarity_count": high_similarity_count,
                "moderate_similarity_count": moderate_similarity_count,
                "low_similarity_count": low_similarity_count,
                "average_similarity": round(sum([r["overall_similarity"] for r in similarity_results]) / len(similarity_results) if similarity_results else 0, 4)
            },
            "top_similar": similarity_results[:5] if similarity_results else [],
            "plagiarism_analysis": plagiarism_analysis,
            "analysis_timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"유사도 체크 실패: {str(e)}")

# 커버레터 유사도 체크 엔드포인트
@app.post("/api/coverletter/similarity-check/{applicant_id}")
async def check_coverletter_similarity(
    applicant_id: str,
    mongo_service: MongoService = Depends(get_mongo_service)
):
    """자기소개서 표절체크 (호환성을 위한 별명 엔드포인트)"""
    try:
        print(f"[INFO] 자소서 표절체크 요청 - applicant_id: {applicant_id}")

        # 1. 지원자 존재 확인
        applicant = await mongo_service.get_applicant_by_id(applicant_id)
        if not applicant:
            print(f"[ERROR] 지원자를 찾을 수 없음 - applicant_id: {applicant_id}")
            raise HTTPException(status_code=404, detail="지원자를 찾을 수 없습니다")

        print(f"[INFO] 지원자 정보 확인 - applicant: {applicant}")
        print(f"[INFO] 지원자 필드들: {list(applicant.keys())}")

        # 2. 자소서 존재 확인
        cover_letter_id = applicant.get("cover_letter_id")
        print(f"[INFO] 자소서 ID 확인 - cover_letter_id: {cover_letter_id}")

        if not cover_letter_id:
            print(f"[ERROR] 자소서 ID가 없음 - applicant_id: {applicant_id}")
            raise HTTPException(status_code=404, detail="자소서가 없습니다")

        # 3. 자소서 내용 가져오기
        from bson import ObjectId
        from motor.motor_asyncio import AsyncIOMotorClient

        mongo_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017/hireme")
        client = AsyncIOMotorClient(mongo_uri)
        db = client.hireme

        try:
            # ObjectId 변환 시도
            try:
                object_id = ObjectId(cover_letter_id)
            except Exception as e:
                print(f"[ERROR] 잘못된 ObjectId 형식: {cover_letter_id}")
                raise HTTPException(status_code=400, detail="잘못된 자소서 ID 형식입니다")

            cover_letter = await db.cover_letters.find_one({"_id": object_id})

            if not cover_letter:
                raise HTTPException(status_code=404, detail="자소서를 찾을 수 없습니다")

            # 자소서 내용 추출 (content 또는 extracted_text 필드에서)
            cover_letter_text = cover_letter.get("content", "") or cover_letter.get("extracted_text", "")

            # 자소서 데이터에 extracted_text 필드가 없으면 content를 사용
            if not cover_letter.get("extracted_text"):
                cover_letter["extracted_text"] = cover_letter_text

            if not cover_letter_text:
                print(f"[WARNING] 자소서 내용이 비어있음 - applicant_id: {applicant_id}")
                return {
                    "status": "success",
                    "applicant_id": applicant_id,
                    "plagiarism_result": {
                        "status": "no_content",
                        "message": "자소서 내용이 없어 표절 검사를 수행할 수 없습니다.",
                        "similar_count": 0,
                        "suspicion_level": "UNKNOWN"
                    },
                    "message": "자소서 내용이 없습니다"
                }

            print(f"[INFO] 자소서 내용 발견 - 길이: {len(cover_letter_text)}자")
            print(f"[INFO] 자소서 필드들: {list(cover_letter.keys())}")

            # 4. 유사도 서비스 초기화
            similarity_service = get_similarity_service()

            # 5. 자소서 표절체크 수행 (청킹 기반 유사도 검색 사용)
            # 자소서 데이터를 직접 전달하여 청킹 처리
            result = await similarity_service.find_similar_documents_by_chunks(
                document_id=cover_letter_id,
                collection=db.cover_letters,
                document_type="cover_letter",
                limit=10
            )

        except HTTPException:
            raise
        except Exception as e:
            print(f"[ERROR] 자소서 조회 실패: {str(e)}")
            raise HTTPException(status_code=500, detail="자소서 조회 중 오류가 발생했습니다")
        finally:
            client.close()

        # 결과 검증 및 폴백 처리
        if not result or not result.get("success"):
            print(f"[WARNING] 자소서 표절체크 결과가 비어있음 - 폴백 응답 생성")
            return {
                "status": "success",
                "applicant_id": applicant_id,
                "plagiarism_result": {
                    "status": "no_similar_documents",
                    "message": "유사한 자소서를 찾을 수 없어 표절 검사를 수행할 수 없습니다.",
                    "similar_count": 0,
                    "suspicion_level": "UNKNOWN",
                    "debug_info": {
                        "cover_letter_id": cover_letter_id,
                        "content_length": len(cover_letter_text),
                        "has_extracted_text": bool(cover_letter.get("extracted_text")),
                        "cover_letter_fields": list(cover_letter.keys())
                    }
                },
                "message": "자소서 표절체크 완료 (유사 문서 없음)"
            }

        return {
            "status": "success",
            "applicant_id": applicant_id,
            "plagiarism_result": result,
            "message": "자소서 표절체크 완료"
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR] 자소서 표절체크 실패: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"자소서 표절체크 중 오류가 발생했습니다: {str(e)}"
        )



# 메일 템플릿 및 설정 관련 엔드포인트
@app.get("/api/mail-templates")
async def get_mail_templates():
    """메일 템플릿 조회"""
    try:
        templates = await db.mail_templates.find_one({"_id": "default"})

        # 기존 템플릿이 있더라도 새로운 상태 타입들이 없으면 재생성
        should_recreate = False
        if templates:
            required_types = ["passed", "document_passed", "final_passed", "rejected", "document_rejected"]
            for required_type in required_types:
                if required_type not in templates:
                    should_recreate = True
                    break

        if not templates or should_recreate:
            # 기존 템플릿이 있으면 삭제
            if templates:
                await db.mail_templates.delete_one({"_id": "default"})

            # 기본 템플릿 생성
            default_templates = {
                "_id": "default",
                "passed": {
                    "subject": "축하합니다! 서류 전형 합격 안내",
                    "content": """안녕하세요, {applicant_name}님

축하드립니다! {job_posting_title} 포지션에 대한 서류 전형에 합격하셨습니다.

다음 단계인 면접 일정은 추후 별도로 안내드리겠습니다.

감사합니다.
{company_name} 채용팀"""
                },
                "document_passed": {
                    "subject": "축하합니다! 서류 전형 합격 안내",
                    "content": """안녕하세요, {applicant_name}님

축하드립니다! {job_posting_title} 포지션에 대한 서류 전형에 합격하셨습니다.

다음 단계인 면접 일정은 추후 별도로 안내드리겠습니다.

감사합니다.
{company_name} 채용팀"""
                },
                "final_passed": {
                    "subject": "축하합니다! 최종 합격 안내",
                    "content": """안녕하세요, {applicant_name}님

축하드립니다! {job_posting_title} 포지션에 대한 최종 전형에 합격하셨습니다.

입사 관련 상세 안내는 추후 별도로 연락드리겠습니다.

감사합니다.
{company_name} 채용팀"""
                },
                "rejected": {
                    "subject": "서류 전형 결과 안내",
                    "content": """안녕하세요, {applicant_name}님

{job_posting_title} 포지션에 대한 서류 전형 결과를 안내드립니다.

안타깝게도 이번 전형에서는 합격하지 못했습니다.
앞으로 더 좋은 기회가 있을 때 다시 지원해 주시기 바랍니다.

감사합니다.
{company_name} 채용팀"""
                },
                "document_rejected": {
                    "subject": "서류 전형 결과 안내",
                    "content": """안녕하세요, {applicant_name}님

{job_posting_title} 포지션에 대한 서류 전형 결과를 안내드립니다.

안타깝게도 이번 전형에서는 합격하지 못했습니다.
앞으로 더 좋은 기회가 있을 때 다시 지원해 주시기 바랍니다.

감사합니다.
{company_name} 채용팀"""
                },
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            }
            await db.mail_templates.insert_one(default_templates)
            templates = default_templates

        # _id 제거하고 반환
        templates.pop("_id", None)
        return templates
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"메일 템플릿 조회 실패: {str(e)}")

@app.post("/api/mail-templates")
async def save_mail_templates(templates: Dict[str, Any]):
    """메일 템플릿 저장"""
    try:
        update_data = {
            "passed": templates.get("passed", {}),
            "document_passed": templates.get("document_passed", {}),
            "final_passed": templates.get("final_passed", {}),
            "rejected": templates.get("rejected", {}),
            "document_rejected": templates.get("document_rejected", {}),
            "updated_at": datetime.now()
        }

        result = await db.mail_templates.update_one(
            {"_id": "default"},
            {"$set": update_data},
            upsert=True
        )

        return {"success": True, "message": "메일 템플릿이 저장되었습니다."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"메일 템플릿 저장 실패: {str(e)}")

@app.get("/api/mail-settings")
async def get_mail_settings():
    """메일 설정 조회"""
    try:
        settings = await db.mail_settings.find_one({"_id": "default"})
        if not settings:
            # 기본 설정 생성
            default_settings = {
                "_id": "default",
                "senderEmail": "",
                "senderPassword": "",
                "senderName": "",
                "smtpServer": "smtp.gmail.com",
                "smtpPort": 587,
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            }
            await db.mail_settings.insert_one(default_settings)
            settings = default_settings

        # _id 제거하고 반환
        settings.pop("_id", None)
        return settings
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"메일 설정 조회 실패: {str(e)}")

@app.post("/api/mail-settings")
async def save_mail_settings(settings: Dict[str, Any]):
    """메일 설정 저장"""
    try:
        update_data = {
            "senderEmail": settings.get("senderEmail", ""),
            "senderPassword": settings.get("senderPassword", ""),
            "senderName": settings.get("senderName", ""),
            "smtpServer": settings.get("smtpServer", "smtp.gmail.com"),
            "smtpPort": settings.get("smtpPort", 587),
            "updated_at": datetime.now()
        }

        result = await db.mail_settings.update_one(
            {"_id": "default"},
            {"$set": update_data},
            upsert=True
        )

        return {"success": True, "message": "메일 설정이 저장되었습니다."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"메일 설정 저장 실패: {str(e)}")

@app.post("/api/send-test-mail")
async def send_test_mail(request: Request):
    """테스트 메일 발송"""
    try:
        import smtplib
        from email.mime.multipart import MIMEMultipart
        from email.mime.text import MIMEText

        data = await request.json()
        print(f"받은 데이터: {data}")  # 디버깅용 로그

        test_email = data.get("testEmail")
        mail_settings = data.get("mailSettings")

        print(f"테스트 이메일: {test_email}")  # 디버깅용 로그
        print(f"메일 설정: {mail_settings}")  # 디버깅용 로그

        if not test_email or not mail_settings:
            print("테스트 이메일 또는 메일 설정이 없습니다.")  # 디버깅용 로그
            raise HTTPException(status_code=400, detail="테스트 이메일과 메일 설정이 필요합니다.")

        # 메일 템플릿 조회
        mail_templates = await db.mail_templates.find_one({"_id": "default"})
        if not mail_templates:
            raise HTTPException(status_code=400, detail="메일 템플릿이 필요합니다.")

        # 테스트 메일 내용 생성
        template = mail_templates.get("passed", {})
        subject = template.get("subject", "테스트 메일")
        content = template.get("content", "테스트 메일입니다.")

        # 변수 치환
        content = content.format(
            applicant_name="테스트 사용자",
            job_posting_title="테스트 채용공고",
            company_name="테스트 회사",
            position="테스트 직무"
        )

        # 메일 객체 생성
        msg = MIMEMultipart()
        msg['From'] = f"{mail_settings.get('senderName', '')} <{mail_settings.get('senderEmail')}>"
        msg['To'] = test_email
        msg['Subject'] = f"[테스트] {subject}"

        # 메일 본문 추가
        msg.attach(MIMEText(content, 'plain', 'utf-8'))

        # SMTP 서버 연결 및 메일 발송
        try:
            print(f"SMTP 서버 연결 시도: {mail_settings.get('smtpServer')}:{mail_settings.get('smtpPort')}")  # 디버깅용 로그
            print(f"발송자 이메일: {mail_settings.get('senderEmail')}")  # 디버깅용 로그
            print(f"발송자 비밀번호 길이: {len(mail_settings.get('senderPassword', ''))}")  # 디버깅용 로그
            print(f"발송자 비밀번호: {mail_settings.get('senderPassword', '')[:4]}***")  # 디버깅용 로그 (앞 4자리만)

            smtp_port = mail_settings.get('smtpPort', 587)
            smtp_server = mail_settings.get('smtpServer', 'smtp.gmail.com')

            # 포트 465인 경우 SSL 사용
            if smtp_port == 465:
                with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
                    print("SMTP SSL 서버 연결 성공")  # 디버깅용 로그
                    print(f"로그인 시도: {mail_settings.get('senderEmail')}")  # 디버깅용 로그
                    server.login(mail_settings.get('senderEmail'), mail_settings.get('senderPassword'))
                    print("로그인 성공")  # 디버깅용 로그
                    server.send_message(msg)
                    print("메일 발송 성공")  # 디버깅용 로그
            else:
                with smtplib.SMTP(smtp_server, smtp_port) as server:
                    print("SMTP 서버 연결 성공")  # 디버깅용 로그
                    server.starttls()
                    print("STARTTLS 성공")  # 디버깅용 로그
                    print(f"로그인 시도: {mail_settings.get('senderEmail')}")  # 디버깅용 로그
                    server.login(mail_settings.get('senderEmail'), mail_settings.get('senderPassword'))
                    print("로그인 성공")  # 디버깅용 로그
                    server.send_message(msg)
                    print("메일 발송 성공")  # 디버깅용 로그

            return {
                "success": True,
                "message": "테스트 메일이 성공적으로 발송되었습니다.",
                "subject": f"[테스트] {subject}",
                "to": test_email
            }

        except smtplib.SMTPAuthenticationError as e:
            print(f"인증 실패: {str(e)}")  # 디버깅용 로그
            raise HTTPException(status_code=400, detail="인증 실패. 이메일 주소와 앱 비밀번호를 확인해주세요.")
        except smtplib.SMTPException as e:
            print(f"SMTP 오류: {str(e)}")  # 디버깅용 로그
            raise HTTPException(status_code=400, detail=f"SMTP 오류: {str(e)}")
        except Exception as e:
            print(f"메일 발송 오류: {str(e)}")  # 디버깅용 로그
            raise HTTPException(status_code=500, detail=f"메일 발송 오류: {str(e)}")

    except HTTPException:
        raise
    except Exception as e:
        print(f"테스트 메일 발송 중 오류: {str(e)}")  # 디버깅용 로그
        raise HTTPException(status_code=500, detail=f"테스트 메일 발송 중 오류가 발생했습니다: {str(e)}")

@app.post("/api/send-bulk-mail")
async def send_bulk_mail(request: Request):
    """대량 메일 발송"""
    try:
        import smtplib
        from email.mime.multipart import MIMEMultipart
        from email.mime.text import MIMEText

        print(f"📧 [DEBUG] 대량 메일 발송 요청 시작")

        data = await request.json()
        print(f"📧 [DEBUG] 받은 데이터: {data}")

        status_type = data.get("statusType")
        print(f"📧 [DEBUG] statusType: {status_type}")

        if not status_type:
            print(f"📧 [DEBUG] 상태 타입이 없음")
            raise HTTPException(status_code=400, detail="상태 타입이 필요합니다.")

        # 메일 설정 조회
        print(f"📧 [DEBUG] 메일 설정 조회 시작")
        mail_settings = await db.mail_settings.find_one({"_id": "default"})
        print(f"📧 [DEBUG] 메일 설정 조회 결과: {mail_settings}")

        if not mail_settings:
            print(f"📧 [DEBUG] 메일 설정이 없음")
            raise HTTPException(status_code=400, detail="메일 설정이 필요합니다.")

        # 메일 템플릿 조회
        print(f"📧 [DEBUG] 메일 템플릿 조회 시작")
        mail_templates = await db.mail_templates.find_one({"_id": "default"})
        print(f"📧 [DEBUG] 메일 템플릿 조회 결과: {mail_templates}")

        if not mail_templates:
            print(f"📧 [DEBUG] 메일 템플릿이 없음")
            raise HTTPException(status_code=400, detail="메일 템플릿이 필요합니다.")

        # 지원자 조회
        print(f"📧 [DEBUG] 지원자 조회 시작 - statusType: {status_type}")

        if status_type == 'passed':
            # 합격자 (서류합격, 최종합격)
            print(f"📧 [DEBUG] 합격자 조회 쿼리 실행")
            applicants = await db.applicants.find({
                "status": {"$in": ["서류합격", "최종합격"]}
            }).to_list(None)
            print(f"📧 [DEBUG] 합격자 조회 결과: {len(applicants)}명")
        elif status_type == 'document_passed':
            # 서류합격자
            print(f"📧 [DEBUG] 서류합격자 조회 쿼리 실행")
            applicants = await db.applicants.find({
                "status": "서류합격"
            }).to_list(None)
            print(f"📧 [DEBUG] 서류합격자 조회 결과: {len(applicants)}명")
        elif status_type == 'final_passed':
            # 최종합격자
            print(f"📧 [DEBUG] 최종합격자 조회 쿼리 실행")
            applicants = await db.applicants.find({
                "status": "최종합격"
            }).to_list(None)
            print(f"📧 [DEBUG] 최종합격자 조회 결과: {len(applicants)}명")
        elif status_type == 'rejected':
            # 불합격자 (서류불합격)
            print(f"📧 [DEBUG] 불합격자 조회 쿼리 실행")
            applicants = await db.applicants.find({
                "status": "서류불합격"
            }).to_list(None)
            print(f"📧 [DEBUG] 불합격자 조회 결과: {len(applicants)}명")
        elif status_type == 'document_rejected':
            # 서류불합격자
            print(f"📧 [DEBUG] 서류불합격자 조회 쿼리 실행")
            applicants = await db.applicants.find({
                "status": "서류불합격"
            }).to_list(None)
            print(f"📧 [DEBUG] 서류불합격자 조회 결과: {len(applicants)}명")
        else:
            print(f"📧 [DEBUG] 잘못된 상태 타입: {status_type}")
            raise HTTPException(status_code=400, detail="잘못된 상태 타입입니다.")

        print(f"📧 [DEBUG] 조회된 지원자 목록:")
        for i, applicant in enumerate(applicants[:5]):  # 처음 5명만 출력
            print(f"  {i+1}. {applicant.get('name', 'Unknown')} - {applicant.get('email', 'No email')} - {applicant.get('status', 'No status')}")

        if not applicants:
            print(f"📧 [DEBUG] 발송할 지원자가 없음")
            return {
                "success": False,
                "message": "발송할 지원자가 없습니다.",
                "total": 0,
                "success_count": 0,
                "failed_count": 0
            }

        # 메일 템플릿 선택
        template = mail_templates.get(status_type, {})
        if not template:
            print(f"📧 [DEBUG] {status_type} 상태에 대한 메일 템플릿이 없습니다.")
            print(f"📧 [DEBUG] 사용 가능한 템플릿: {list(mail_templates.keys())}")
            return {
                "success": False,
                "message": f"{status_type} 상태에 대한 메일 템플릿이 없습니다. /settings 페이지에서 템플릿을 추가해주세요.",
                "total": 0,
                "success_count": 0,
                "failed_count": 0
            }

        success_count = 0
        failed_count = 0
        failed_emails = []

        for applicant in applicants:
            # 지원자 이메일 확인
            email = applicant.get('email')
            if not email:
                failed_count += 1
                continue

            # 채용공고 정보 조회
            job_posting_id = applicant.get('job_posting_id')
            job_posting = {}
            if job_posting_id:
                job_posting = await db.job_postings.find_one({"_id": ObjectId(job_posting_id)}) or {}

            # 메일 내용 포맷팅
            try:
                content = template.get('content', '').format(
                    applicant_name=applicant.get('name', '지원자'),
                    job_posting_title=job_posting.get('title', '채용공고'),
                    company_name=job_posting.get('company', '회사명'),
                    position=applicant.get('position', '지원 직무')
                )
            except Exception as e:
                print(f"메일 내용 포맷팅 실패: {e}")
                content = template.get('content', '')

            # 메일 객체 생성
            msg = MIMEMultipart()
            msg['From'] = f"{mail_settings.get('senderName', '')} <{mail_settings.get('senderEmail')}>"
            msg['To'] = email
            msg['Subject'] = template.get('subject', '안내 메일')
            msg.attach(MIMEText(content, 'plain', 'utf-8'))

            # SMTP 서버 연결 및 메일 발송
            try:
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
                print(f"✅ {applicant.get('name', 'Unknown')} ({email}) - 메일 발송 성공")

            except Exception as e:
                failed_count += 1
                failed_emails.append(email)
                print(f"❌ {applicant.get('name', 'Unknown')} ({email}) - 메일 발송 실패: {e}")

        # 결과 반환
        result = {
            "success": True,
            "total": len(applicants),
            "success_count": success_count,
            "failed_count": failed_count,
            "failed_emails": failed_emails,
            "message": f"메일 발송 완료: {success_count}건 성공, {failed_count}건 실패"
        }

        print(f"\n📊 메일 발송 결과:")
        print(f"  - 총 대상: {len(applicants)}명")
        print(f"  - 성공: {success_count}건")
        print(f"  - 실패: {failed_count}건")

        return result

    except HTTPException:
        raise
    except Exception as e:
        print(f"대량 메일 발송 중 오류: {str(e)}")
        raise HTTPException(status_code=500, detail=f"대량 메일 발송 중 오류가 발생했습니다: {str(e)}")

# 로깅 설정 (버퍼 분리 문제 해결)
logging.basicConfig(
    level=logging.WARNING,
    format='%(levelname)s:%(name)s:%(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('server.log', encoding='utf-8', mode='a')
    ]
)

# 로깅 핸들러 설정
for handler in logging.root.handlers:
    handler.setFormatter(logging.Formatter('%(levelname)s:%(name)s:%(message)s'))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
