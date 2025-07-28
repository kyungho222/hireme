from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel
from typing import List, Optional
import os
from datetime import datetime

# FastAPI 앱 생성
app = FastAPI(
    title="HireMe Client API",
    description="HireMe 클라이언트 애플리케이션 백엔드 API",
    version="1.0.0"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB 연결
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://admin:password@mongodb-client:27017/hireme-client?authSource=admin")
client = AsyncIOMotorClient(MONGODB_URI)
db = client.hireme_client

# Pydantic 모델들
class Job(BaseModel):
    id: Optional[str] = None
    title: str
    company: str
    location: str
    description: str
    requirements: List[str] = []
    salary_range: Optional[str] = None
    type: str = "full-time"  # full-time, part-time, contract
    status: str = "active"
    created_at: Optional[datetime] = None

class Portfolio(BaseModel):
    id: Optional[str] = None
    user_id: str
    title: str
    description: str
    github_url: Optional[str] = None
    live_url: Optional[str] = None
    technologies: List[str] = []
    status: str = "active"
    created_at: Optional[datetime] = None

class Application(BaseModel):
    id: Optional[str] = None
    user_id: str
    job_id: str
    status: str = "applied"  # applied, reviewing, interviewed, offered, rejected
    applied_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

# API 라우트들
@app.get("/")
async def root():
    return {"message": "HireMe Client API 서버가 실행 중입니다!"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now()}

# 채용 정보 관련 API
@app.get("/api/jobs", response_model=List[Job])
async def get_jobs():
    jobs = await db.jobs.find().to_list(1000)
    return [Job(**job) for job in jobs]

@app.post("/api/jobs", response_model=Job)
async def create_job(job: Job):
    job_dict = job.dict()
    job_dict["created_at"] = datetime.now()
    result = await db.jobs.insert_one(job_dict)
    job_dict["id"] = str(result.inserted_id)
    return Job(**job_dict)

@app.get("/api/jobs/{job_id}", response_model=Job)
async def get_job(job_id: str):
    job = await db.jobs.find_one({"_id": job_id})
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return Job(**job)

# 포트폴리오 관련 API
@app.get("/api/portfolios", response_model=List[Portfolio])
async def get_portfolios():
    portfolios = await db.portfolios.find().to_list(1000)
    return [Portfolio(**portfolio) for portfolio in portfolios]

@app.post("/api/portfolios", response_model=Portfolio)
async def create_portfolio(portfolio: Portfolio):
    portfolio_dict = portfolio.dict()
    portfolio_dict["created_at"] = datetime.now()
    result = await db.portfolios.insert_one(portfolio_dict)
    portfolio_dict["id"] = str(result.inserted_id)
    return Portfolio(**portfolio_dict)

# 지원 관련 API
@app.get("/api/applications", response_model=List[Application])
async def get_applications():
    applications = await db.applications.find().to_list(1000)
    return [Application(**application) for application in applications]

@app.post("/api/applications", response_model=Application)
async def create_application(application: Application):
    application_dict = application.dict()
    application_dict["applied_at"] = datetime.now()
    application_dict["updated_at"] = datetime.now()
    result = await db.applications.insert_one(application_dict)
    application_dict["id"] = str(result.inserted_id)
    return Application(**application_dict)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001) 