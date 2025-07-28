// 클라이언트용 MongoDB 초기화 스크립트
db = db.getSiblingDB('hireme-client');

// 채용 정보 컬렉션 생성 및 샘플 데이터
db.createCollection('jobs');
db.jobs.insertMany([
  {
    title: "프론트엔드 개발자",
    company: "테크컴퍼니",
    location: "서울 강남구",
    description: "React, TypeScript를 사용한 웹 애플리케이션 개발",
    requirements: ["React", "TypeScript", "JavaScript", "HTML/CSS"],
    salary_range: "4000만원 ~ 6000만원",
    type: "full-time",
    status: "active",
    created_at: new Date()
  },
  {
    title: "백엔드 개발자",
    company: "스타트업",
    location: "서울 서초구",
    description: "Python, FastAPI를 사용한 백엔드 API 개발",
    requirements: ["Python", "FastAPI", "MongoDB", "Docker"],
    salary_range: "3500만원 ~ 5500만원",
    type: "full-time",
    status: "active",
    created_at: new Date()
  },
  {
    title: "풀스택 개발자",
    company: "IT기업",
    location: "서울 마포구",
    description: "프론트엔드와 백엔드를 모두 담당하는 개발자",
    requirements: ["React", "Node.js", "MongoDB", "TypeScript"],
    salary_range: "5000만원 ~ 7000만원",
    type: "full-time",
    status: "active",
    created_at: new Date()
  }
]);

// 포트폴리오 컬렉션 생성 및 샘플 데이터
db.createCollection('portfolios');
db.portfolios.insertMany([
  {
    user_id: "user1",
    title: "React E-commerce",
    description: "React와 TypeScript를 사용한 온라인 쇼핑몰",
    github_url: "https://github.com/user1/react-ecommerce",
    live_url: "https://react-ecommerce-demo.com",
    technologies: ["React", "TypeScript", "Styled Components"],
    status: "active",
    created_at: new Date()
  },
  {
    user_id: "user2",
    title: "FastAPI Blog API",
    description: "FastAPI와 MongoDB를 사용한 블로그 API",
    github_url: "https://github.com/user2/fastapi-blog",
    live_url: "https://fastapi-blog-api.herokuapp.com",
    technologies: ["Python", "FastAPI", "MongoDB", "Docker"],
    status: "active",
    created_at: new Date()
  }
]);

// 지원 정보 컬렉션 생성 및 샘플 데이터
db.createCollection('applications');
db.applications.insertMany([
  {
    user_id: "user1",
    job_id: "1",
    status: "applied",
    applied_at: new Date(),
    updated_at: new Date()
  },
  {
    user_id: "user2",
    job_id: "2",
    status: "reviewing",
    applied_at: new Date("2024-01-10"),
    updated_at: new Date("2024-01-15")
  }
]);

print("클라이언트 MongoDB 초기화 완료!"); 