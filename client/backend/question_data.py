from typing import List, Dict, Any

# 페이지별 질문 데이터
PAGE_QUESTIONS = {
    "home": [
        {
            "field": "user_interest",
            "question": "안녕하세요! 어떤 도움이 필요하신가요? (예: 채용공고 작성, 지원서 관리, 포트폴리오 분석 등)",
            "type": "text",
            "required": True
        },
        {
            "field": "user_goal",
            "question": "구체적으로 어떤 목표를 가지고 계신가요?",
            "type": "text",
            "required": True
        }
    ],
    "jobs": [
        {
            "field": "job_search",
            "question": "어떤 직무를 찾고 계신가요? (예: 개발자, 디자이너, 마케터 등)",
            "type": "text",
            "required": True
        },
        {
            "field": "location_preference",
            "question": "희망하는 근무지는 어디인가요?",
            "type": "text",
            "required": True
        },
        {
            "field": "experience_level",
            "question": "경력 수준은 어떻게 되시나요? (신입/경력)",
            "type": "text",
            "required": True
        }
    ],
    "applications": [
        {
            "field": "resume_help",
            "question": "지원서 작성에 어떤 도움이 필요하신가요? (예: 이력서 작성, 자기소개서 작성, 포트폴리오 준비 등)",
            "type": "text",
            "required": True
        },
        {
            "field": "target_position",
            "question": "지원하고 싶은 직무는 무엇인가요?",
            "type": "text",
            "required": True
        }
    ],
    "job-posting": [
        {
            "field": "recruitment_title",
            "question": "채용공고의 제목을 입력해주세요. (예: 백엔드 개발자 채용)",
            "type": "text",
            "required": True
        },
        {
            "field": "recruitment_role",
            "question": "채용하려는 직무를 상세히 설명해주세요. (예: 프론트엔드 개발, 마케터)",
            "type": "text",
            "required": True
        },
        {
            "field": "recruitment_requirements",
            "question": "해당 직무에 필요한 자격 요건이나 필수 역량을 알려주세요.",
            "type": "text",
            "required": True
        },
        {
            "field": "recruitment_preferential",
            "question": "우대하는 사항이나 우대 역량이 있다면 알려주세요.",
            "type": "text",
            "required": False
        },
        {
            "field": "recruitment_benefits",
            "question": "제공하는 복리후생이나 이점을 알려주세요.",
            "type": "text",
            "required": False
        },
        {
            "field": "recruitment_location",
            "question": "근무지를 입력해주세요. (예: 서울특별시 강남구 테헤란로 123)",
            "type": "text",
            "required": True
        },
        {
            "field": "recruitment_deadline",
            "question": "채용 마감일을 입력해주세요. (예: 2025-08-31)",
            "type": "date",
            "required": True
        }
    ],
    "page1": [
        {
            "field": "username",
            "question": "이름을 알려주세요.",
            "type": "text",
            "required": True
        },
        {
            "field": "email",
            "question": "이메일을 입력해주세요.",
            "type": "email",
            "required": True
        },
        {
            "field": "lunch",
            "question": "오늘 점심은 무엇을 드시겠어요?",
            "type": "text",
            "required": True
        },
        {
            "field": "age",
            "question": "나이를 알려주세요.",
            "type": "number",
            "required": True
        },
        {
            "field": "phone",
            "question": "전화번호를 입력해주세요.",
            "type": "tel",
            "required": True
        },
        {
            "field": "address",
            "question": "주소를 입력해주세요.",
            "type": "text",
            "required": True
        },
        {
            "field": "hobby",
            "question": "취미가 무엇인가요?",
            "type": "text",
            "required": True
        },
        {
            "field": "job",
            "question": "직업이 무엇인가요?",
            "type": "text",
            "required": True
        },
        {
            "field": "blood_type",
            "question": "혈액형을 알려주세요.",
            "type": "text",
            "required": True
        },
        {
            "field": "mbti",
            "question": "MBTI를 알려주세요.",
            "type": "text",
            "required": True
        }
    ],
    "page2": [
        {
            "field": "title",
            "question": "게시글 제목을 입력해주세요.",
            "type": "text",
            "required": True,
            "max_length": 50
        },
        {
            "field": "content",
            "question": "게시글 내용을 작성해주세요.",
            "type": "textarea",
            "required": True,
            "max_length": 500
        }
    ],
    "page3": [
        {
            "field": "favorite_color",
            "question": "가장 좋아하는 색깔은 무엇인가요?",
            "type": "text",
            "required": True
        },
        {
            "field": "dream_job", 
            "question": "어릴 때 꿈꾸던 직업이 무엇이었나요?",
            "type": "text",
            "required": True
        },
        {
            "field": "favorite_food",
            "question": "세상에서 가장 맛있는 음식은 무엇이라고 생각하시나요?",
            "type": "text", 
            "required": True
        },
        {
            "field": "travel_destination",
            "question": "가고 싶은 여행지가 있다면 어디인가요?",
            "type": "text",
            "required": True
        },
        {
            "field": "superpower",
            "question": "초능력을 하나 가질 수 있다면 무엇을 원하시나요?",
            "type": "text",
            "required": True
        }
    ]
}

def get_questions_for_page(page: str) -> List[Dict[str, Any]]:
    """페이지별 질문 목록 반환"""
    return PAGE_QUESTIONS.get(page, [])

def get_page_list() -> List[str]:
    """사용 가능한 페이지 목록 반환"""
    return list(PAGE_QUESTIONS.keys())

def get_field_info(page: str, field: str) -> Dict[str, Any]:
    """특정 필드 정보 반환"""
    questions = get_questions_for_page(page)
    for question in questions:
        if question["field"] == field:
            return question
    return None 