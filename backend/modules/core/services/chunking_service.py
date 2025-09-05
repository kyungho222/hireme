from typing import List, Dict, Any
import re

class ChunkingService:
    def __init__(self):
        """청킹 서비스 초기화"""
        # 문서 타입별 청킹 설정
        self.chunk_configs = {
            "resume": {
                "chunk_size": 1000,
                "overlap": 100,
                "priority_fields": ["summary", "keywords", "extracted_text"]
            },
            "cover_letter": {
                "chunk_size": 800,
                "overlap": 50,
                "priority_fields": ["growthBackground", "motivation", "careerHistory", "summary"]
            },
            "portfolio": {
                "chunk_size": 600,
                "overlap": 80,
                "priority_fields": ["items", "summary", "keywords"]
            }
        }
        print("청킹 서비스 초기화 완료")
    
    def chunk_document(self, document: Dict[str, Any], document_type: str = None) -> List[Dict[str, Any]]:
        """
        문서를 청킹 단위로 분할합니다. (resumes, cover_letters, portfolios 모두 지원)
        
        Args:
            document (Dict[str, Any]): 문서 데이터
            document_type (str): 문서 타입 ("resume", "cover_letter", "portfolio")
            
        Returns:
            List[Dict[str, Any]]: 청크 리스트
        """
        chunks = []
        document_id = str(document.get("_id", ""))
        
        # 문서 타입 결정 (명시적 전달 > document_type 필드 > 기본값)
        doc_type = document_type or document.get("document_type", "resume")
        
        print(f"[ChunkingService] === {doc_type} 청킹 시작 ===")
        print(f"[ChunkingService] 문서 ID: {document_id}")
        print(f"[ChunkingService] 문서 키: {list(document.keys())}")
        print(f"[ChunkingService] 주요 필드:")
        for key in ['resume_text', 'extracted_text', 'name', 'skills']:
            value = document.get(key, 'missing')
            if isinstance(value, str):
                print(f"  - {key}: {len(value)} 문자 ('{value[:50]}...')")
            else:
                print(f"  - {key}: {value}")
        
        # 공통 메타데이터 생성
        base_metadata = self._create_base_metadata(document, doc_type)
        
        # 1. 요약/개요 청크
        summary_chunk = self._create_summary_chunk(document, document_id, base_metadata)
        if summary_chunk:
            chunks.append(summary_chunk)
            print(f"[ChunkingService] ✅ 요약 청크 생성: {len(summary_chunk['text'])} 문자")
        else:
            print(f"[ChunkingService] ❌ 요약 청크 생성 실패")
        
        # 2. 키워드 청크
        keywords_chunk = self._create_keywords_chunk(document, document_id, base_metadata)
        if keywords_chunk:
            chunks.append(keywords_chunk)
            print(f"[ChunkingService] ✅ 키워드 청크 생성: {len(keywords_chunk['text'])} 문자")
        else:
            print(f"[ChunkingService] ❌ 키워드 청크 생성 실패")
        
        # 3. 전체 텍스트 청크
        text_chunks = self._create_extracted_text_chunks(document, document_id, base_metadata)
        chunks.extend(text_chunks)
        print(f"[ChunkingService] 텍스트 청크 생성: {len(text_chunks)}개")
        
        # 4. 기본 정보 청크
        basic_info_chunk = self._create_basic_info_chunk(document, document_id, base_metadata)
        if basic_info_chunk:
            chunks.append(basic_info_chunk)
            print(f"[ChunkingService] ✅ 기본정보 청크 생성: {len(basic_info_chunk['text'])} 문자")
        else:
            print(f"[ChunkingService] ❌ 기본정보 청크 생성 실패")
        
        # 5. 문서 타입별 특화 청크 처리
        if doc_type == "cover_letter":
            cover_letter_chunks = self._create_cover_letter_specific_chunks(document, document_id, base_metadata)
            chunks.extend(cover_letter_chunks)
        elif doc_type == "portfolio":
            portfolio_chunks = self._create_portfolio_specific_chunks(document, document_id, base_metadata)
            chunks.extend(portfolio_chunks)
        
        # 문서 타입에 맞는 ID 필드 추가
        id_field_map = {
            "resume": "resume_id",
            "cover_letter": "cover_letter_id", 
            "portfolio": "portfolio_id"
        }
        
        id_field = id_field_map.get(doc_type, "document_id")
        for chunk in chunks:
            if id_field not in chunk:
                chunk[id_field] = document_id
        
        print(f"[ChunkingService] 총 {len(chunks)}개 청크 생성 완료 ({id_field} 필드 추가)")
        for i, chunk in enumerate(chunks):
            print(f"[ChunkingService] 청크 {i+1}: {chunk['chunk_type']} - {len(chunk['text'])} 문자")
        print(f"[ChunkingService] === {doc_type} 청킹 완료 ===")
        
        return chunks
    
    def chunk_resume_text(self, resume: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        이력서 청킹 (하위 호환성을 위한 래퍼 함수)
        
        Args:
            resume (Dict[str, Any]): 이력서 데이터
            
        Returns:
            List[Dict[str, Any]]: 청크 리스트
        """
        return self.chunk_document(resume, "resume")
    
    def chunk_cover_letter(self, cover_letter: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        자기소개서 청킹 (편의 메서드)
        
        Args:
            cover_letter (Dict[str, Any]): 자기소개서 데이터
            
        Returns:
            List[Dict[str, Any]]: 청크 리스트
        """
        print(f"[ChunkingService] 자기소개서 청킹 시작")
        print(f"[ChunkingService] 자기소개서 데이터 키: {list(cover_letter.keys())}")
        print(f"[ChunkingService] careerHistory: {len(cover_letter.get('careerHistory', ''))} 글자")
        print(f"[ChunkingService] growthBackground: {len(cover_letter.get('growthBackground', ''))} 글자")
        print(f"[ChunkingService] motivation: {len(cover_letter.get('motivation', ''))} 글자")
        print(f"[ChunkingService] extracted_text: {len(cover_letter.get('extracted_text', ''))} 글자")
        
        chunks = self.chunk_document(cover_letter, "cover_letter")
        print(f"[ChunkingService] 생성된 청크 수: {len(chunks)}")
        
        return chunks
    
    def chunk_portfolio(self, portfolio: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        포트폴리오 청킹 (편의 메서드)
        
        Args:
            portfolio (Dict[str, Any]): 포트폴리오 데이터
            
        Returns:
            List[Dict[str, Any]]: 청크 리스트
        """
        return self.chunk_document(portfolio, "portfolio")
    
    def _create_base_metadata(self, document: Dict[str, Any], doc_type: str) -> Dict[str, Any]:
        """문서의 기본 메타데이터 생성"""
        return {
            "document_type": doc_type,
            "applicant_id": document.get("applicant_id", ""),
            "created_at": document.get("created_at", ""),
            "file_metadata": document.get("file_metadata", {}),
            "source_collection": f"{doc_type}s" if doc_type != "portfolio" else "portfolios"
        }
        chunks = []
        resume_id = str(resume.get("_id", ""))
        
        print(f"[ChunkingService] === 이력서 청킹 시작 ===")
        print(f"[ChunkingService] 이력서 ID: {resume_id}")
        
        # 기본 메타데이터 생성
        base_metadata = self._create_base_metadata(resume, "resume")
        
        # 1. 요약/개요 청크 (summary)
        summary_chunk = self._create_summary_chunk(resume, resume_id, base_metadata)
        if summary_chunk:
            chunks.append(summary_chunk)
        
        # 2. 키워드 청크
        keywords_chunk = self._create_keywords_chunk(resume, resume_id, base_metadata)
        if keywords_chunk:
            chunks.append(keywords_chunk)
        
        # 3. 추출된 텍스트 청크
        text_chunks = self._create_extracted_text_chunks(resume, resume_id, base_metadata)
        chunks.extend(text_chunks)
        
        # 4. 기본 정보 청크
        basic_info_chunk = self._create_basic_info_chunk(resume, resume_id, base_metadata)
        if basic_info_chunk:
            chunks.append(basic_info_chunk)
        
        # 5. 기술스택/스킬 청크 (skills) - 전체적으로 하나의 청크
        skills_chunk = self._create_skills_chunk(resume, resume_id)
        if skills_chunk:
            chunks.append(skills_chunk)
        
        # 6. 경험 항목별 청크 (experience items)
        experience_chunks = self._create_experience_chunks(resume, resume_id)
        chunks.extend(experience_chunks)
        
        # 7. 교육 항목별 청크 (education items)
        education_chunks = self._create_education_chunks(resume, resume_id)
        chunks.extend(education_chunks)
        
        # 8. 성장배경 청크
        growth_chunk = self._create_growth_background_chunk(resume, resume_id)
        if growth_chunk:
            chunks.append(growth_chunk)
        
        # 9. 지원동기 청크
        motivation_chunk = self._create_motivation_chunk(resume, resume_id)
        if motivation_chunk:
            chunks.append(motivation_chunk)
        
        # 10. 경력사항 청크
        career_chunk = self._create_career_history_chunk(resume, resume_id)
        if career_chunk:
            chunks.append(career_chunk)
        
        print(f"[ChunkingService] 총 {len(chunks)}개 청크 생성 완료")
        for i, chunk in enumerate(chunks):
            print(f"[ChunkingService] 청크 {i+1}: {chunk['chunk_type']} - {len(chunk['text'])} 문자")
        print(f"[ChunkingService] === 이력서 청킹 완료 ===")
        
        return chunks
    
    def _create_summary_chunk(self, document: Dict[str, Any], document_id: str, base_metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """요약 청크 생성 - summary 필드 사용"""
        summary_text = document.get("summary", "").strip()
        
        # summary 필드가 없는 경우 basic_info에서 기본 정보 추출
        if not summary_text:
            basic_info = document.get("basic_info", {})
            # 배열 필드 처리
            names = basic_info.get("names", []) or [basic_info.get("name", "")]
            emails = basic_info.get("emails", []) or [basic_info.get("email", "")]
            phones = basic_info.get("phones", []) or [basic_info.get("phone", "")]
            
            summary_parts = []
            if names and names[0]:
                summary_parts.append(f"이름: {names[0]}")
            if emails and emails[0]:
                summary_parts.append(f"이메일: {emails[0]}")
            if phones and phones[0]:
                summary_parts.append(f"전화: {phones[0]}")
            
            summary_text = " ".join(summary_parts)
        
        if summary_text:
            metadata = {
                "section": "summary",
                "original_field": "summary",
                **(base_metadata or {})
            }
            return {
                "document_id": document_id,
                "resume_id": document_id,  # VectorService에서 필요한 필드
                "chunk_id": f"{document_id}_summary",
                "chunk_type": "summary",
                "text": summary_text.strip(),
                "metadata": metadata
            }
        return None
    
    def _create_skills_chunk(self, resume: Dict[str, Any], resume_id: str) -> Dict[str, Any]:
        """기술스택/스킬 청크 생성"""
        skills = resume.get("skills", "").strip()
        
        if skills:
            return {
                "resume_id": resume_id,
                "chunk_id": f"{resume_id}_skills",
                "chunk_type": "skills",
                "text": f"기술스택: {skills}",
                "metadata": {
                    "section": "skills",
                    "original_field": "skills"
                }
            }
        return None
    
    def _create_experience_chunks(self, resume: Dict[str, Any], resume_id: str) -> List[Dict[str, Any]]:
        """경험 항목별 청크 생성"""
        chunks = []
        
        # experience 필드에서 경험 추출
        experience = resume.get("experience", "").strip()
        if experience:
            # 경험을 개별 항목으로 분할 (줄바꿈, 숫자., - 등으로 구분)
            experience_items = self._split_into_items(experience)
            
            for i, item in enumerate(experience_items):
                if item.strip():
                    chunks.append({
                        "resume_id": resume_id,
                        "chunk_id": f"{resume_id}_experience_{i+1}",
                        "chunk_type": "experience",
                        "text": f"경험: {item.strip()}",
                        "metadata": {
                            "section": "experience",
                            "item_index": i+1,
                            "original_field": "experience"
                        }
                    })
        
        return chunks
    
    def _create_education_chunks(self, resume: Dict[str, Any], resume_id: str) -> List[Dict[str, Any]]:
        """교육 항목별 청크 생성"""
        chunks = []
        
        # education 필드가 있다면 사용
        education = resume.get("education", "").strip()
        if education:
            education_items = self._split_into_items(education)
            
            for i, item in enumerate(education_items):
                if item.strip():
                    chunks.append({
                        "resume_id": resume_id,
                        "chunk_id": f"{resume_id}_education_{i+1}",
                        "chunk_type": "education",
                        "text": f"교육: {item.strip()}",
                        "metadata": {
                            "section": "education",
                            "item_index": i+1,
                            "original_field": "education"
                        }
                    })
        
        return chunks
    
    def _create_growth_background_chunk(self, resume: Dict[str, Any], resume_id: str) -> Dict[str, Any]:
        """성장배경 청크 생성"""
        growth_background = resume.get("growthBackground", "").strip()
        
        if growth_background:
            return {
                "resume_id": resume_id,
                "chunk_id": f"{resume_id}_growth_background",
                "chunk_type": "growth_background",
                "text": f"성장배경: {growth_background}",
                "metadata": {
                    "section": "growth_background",
                    "original_field": "growthBackground"
                }
            }
        return None
    
    def _create_motivation_chunk(self, resume: Dict[str, Any], resume_id: str) -> Dict[str, Any]:
        """지원동기 청크 생성"""
        motivation = resume.get("motivation", "").strip()
        
        if motivation:
            return {
                "resume_id": resume_id,
                "chunk_id": f"{resume_id}_motivation",
                "chunk_type": "motivation",
                "text": f"지원동기: {motivation}",
                "metadata": {
                    "section": "motivation",
                    "original_field": "motivation"
                }
            }
        return None
    
    def _create_career_history_chunk(self, resume: Dict[str, Any], resume_id: str) -> Dict[str, Any]:
        """경력사항 청크 생성"""
        career_history = resume.get("careerHistory", "").strip()
        
        if career_history:
            return {
                "resume_id": resume_id,
                "chunk_id": f"{resume_id}_career_history",
                "chunk_type": "career_history",
                "text": f"경력사항: {career_history}",
                "metadata": {
                    "section": "career_history",
                    "original_field": "careerHistory"
                }
            }
        return None
    
    def _split_into_items(self, text: str) -> List[str]:
        """텍스트를 개별 항목으로 분할"""
        if not text:
            return []
        
        # 다양한 구분자로 분할
        # 1. 숫자와 점 (1. 2. 3.)
        # 2. 대시 (-, •, -, ●)
        # 3. 줄바꿈으로 구분된 항목
        
        # 먼저 명확한 구분자들로 분할
        items = re.split(r'(?:\d+\.|[-•●▪▫]|\n\s*[-•●▪▫]?|\n\s*\d+\.)', text)
        
        # 빈 항목 제거 및 정리
        cleaned_items = []
        for item in items:
            item = item.strip()
            if item and len(item) > 10:  # 너무 짧은 항목은 제외
                cleaned_items.append(item)
        
        # 분할된 항목이 없으면 원본 텍스트를 하나의 항목으로 반환
        if not cleaned_items and text.strip():
            cleaned_items = [text.strip()]
        
        return cleaned_items
    
    def _create_keywords_chunk(self, document: Dict[str, Any], document_id: str, base_metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """키워드 청크 생성 - keywords 배열 사용"""
        keywords = document.get("keywords", [])
        
        if keywords and isinstance(keywords, list):
            keywords_text = ", ".join(keywords)
            metadata = {
                "section": "keywords",
                "original_field": "keywords",
                "keyword_count": len(keywords),
                **(base_metadata or {})
            }
            return {
                "document_id": document_id,
                "chunk_id": f"{document_id}_keywords",
                "chunk_type": "keywords",
                "text": f"키워드: {keywords_text}",
                "metadata": metadata
            }
        return None
    
    def _create_extracted_text_chunks(self, document: Dict[str, Any], document_id: str, base_metadata: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """추출된 텍스트를 청크로 분할 - extracted_text 또는 resume_text 필드 사용"""
        chunks = []
        
        # extracted_text가 없거나 짧으면 resume_text를 사용
        extracted_text = document.get("extracted_text", "").strip()
        if not extracted_text or len(extracted_text) < 50:
            extracted_text = document.get("resume_text", "").strip()
            print(f"[ChunkingService] extracted_text 부족, resume_text 사용: {len(extracted_text)} 문자")
        
        if extracted_text:
            # 문서 타입별 청킹 설정 적용
            doc_type = base_metadata.get("document_type", "resume") if base_metadata else "resume"
            config = self.chunk_configs.get(doc_type, self.chunk_configs["resume"])
            chunk_size = config["chunk_size"]
            overlap = config["overlap"]
            
            for i in range(0, len(extracted_text), chunk_size - overlap):
                chunk_text = extracted_text[i:i + chunk_size]
                if chunk_text.strip():
                    metadata = {
                        "section": "extracted_text",
                        "chunk_index": i // (chunk_size - overlap) + 1,
                        "original_field": "extracted_text",
                        "start_position": i,
                        "end_position": min(i + chunk_size, len(extracted_text)),
                        **(base_metadata or {})
                    }
                    chunks.append({
                        "document_id": document_id,
                        "resume_id": document_id,  # VectorService에서 필요한 필드
                        "chunk_id": f"{document_id}_text_{i // (chunk_size - overlap) + 1}",
                        "chunk_type": "extracted_text",
                        "text": chunk_text.strip(),
                        "metadata": metadata
                    })
        
        return chunks
    
    def _create_basic_info_chunk(self, document: Dict[str, Any], document_id: str, base_metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """기본 정보 청크 생성 - basic_info 필드의 배열/문자열 모두 처리"""
        basic_info = document.get("basic_info", {})
        
        if basic_info:
            info_parts = []
            processed_fields = {}
            
            for key, value in basic_info.items():
                if not value:
                    continue
                    
                # 배열 필드 처리 (emails, phones, names, urls)
                if isinstance(value, list) and value:
                    # 빈 값들 제거 후 처리
                    clean_values = [str(v).strip() for v in value if v and str(v).strip()]
                    if clean_values:
                        if len(clean_values) == 1:
                            info_parts.append(f"{key}: {clean_values[0]}")
                        else:
                            info_parts.append(f"{key}: {', '.join(clean_values)}")
                        processed_fields[key] = clean_values
                
                # 문자열 필드 처리
                elif isinstance(value, str) and value.strip():
                    info_parts.append(f"{key}: {value.strip()}")
                    processed_fields[key] = value.strip()
                
                # 기타 타입 처리 (숫자 등)
                elif value:
                    info_parts.append(f"{key}: {str(value)}")
                    processed_fields[key] = str(value)
            
            if info_parts:
                metadata = {
                    "section": "basic_info",
                    "original_field": "basic_info",
                    "info_fields": list(processed_fields.keys()),
                    "processed_data": processed_fields,
                    **(base_metadata or {})
                }
                return {
                    "document_id": document_id,
                    "chunk_id": f"{document_id}_basic_info",
                    "chunk_type": "basic_info",
                    "text": " ".join(info_parts),
                    "metadata": metadata
                }
        return None
    
    def _create_cover_letter_specific_chunks(self, document: Dict[str, Any], document_id: str, base_metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
        """자기소개서 전용 청크 생성 - growthBackground, motivation, careerHistory 처리"""
        chunks = []
        
        # cover_letters 컬렉션의 새로운 필드들
        cover_letter_fields = {
            "growthBackground": "성장배경",
            "motivation": "지원동기", 
            "careerHistory": "경력사항"
        }
        
        # 특화 필드들 청킹
        for field_name, field_desc in cover_letter_fields.items():
            field_content = document.get(field_name, "")
            if field_content and field_content.strip():
                # cover_letter 타입의 청킹 설정 적용
                config = self.chunk_configs["cover_letter"]
                field_chunks = self._split_text_into_chunks(
                    field_content.strip(), 
                    chunk_size=config["chunk_size"], 
                    overlap=config["overlap"]
                )
                
                for i, chunk_text in enumerate(field_chunks):
                    if chunk_text.strip():
                        metadata = {
                            "section": field_name,
                            "section_description": field_desc,
                            "original_field": field_name,
                            "chunk_index": i + 1,
                            "total_chunks": len(field_chunks),
                            **(base_metadata or {})
                        }
                        
                        chunk_id_suffix = f"_{i+1}" if len(field_chunks) > 1 else ""
                        chunks.append({
                            "document_id": document_id,
                            "chunk_id": f"{document_id}_{field_name}{chunk_id_suffix}",
                            "chunk_type": field_name,
                            "text": f"{field_desc}: {chunk_text.strip()}",
                            "metadata": metadata
                        })
        
        return chunks
    
    def _create_portfolio_specific_chunks(self, document: Dict[str, Any], document_id: str, base_metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
        """포트폴리오 전용 청크 생성 - items, artifacts 구조 처리"""
        chunks = []
        
        # portfolios 컬렉션의 items 배열 처리
        items = document.get("items", [])
        if items and isinstance(items, list):
            for i, item in enumerate(items):
                if isinstance(item, dict):
                    item_id = item.get("item_id", f"item_{i+1}")
                    title = item.get("title", "")
                    item_type = item.get("type", "")
                    
                    # 아이템 기본 정보 청크
                    item_info_parts = []
                    if title:
                        item_info_parts.append(f"제목: {title}")
                    if item_type:
                        item_info_parts.append(f"타입: {item_type}")
                    
                    if item_info_parts:
                        metadata = {
                            "section": "portfolio_item",
                            "item_id": item_id,
                            "item_index": i + 1,
                            "item_type": item_type,
                            "original_field": "items",
                            **(base_metadata or {})
                        }
                        
                        chunks.append({
                            "document_id": document_id,
                            "chunk_id": f"{document_id}_item_{i+1}",
                            "chunk_type": "portfolio_item",
                            "text": " ".join(item_info_parts),
                            "metadata": metadata
                        })
        
        return chunks
    
    def _split_text_into_chunks(self, text: str, chunk_size: int = 1000, overlap: int = 100) -> List[str]:
        """긴 텍스트를 오버랩을 두고 청크로 분할"""
        if not text or len(text) <= chunk_size:
            return [text] if text.strip() else []
        
        chunks = []
        for i in range(0, len(text), chunk_size - overlap):
            chunk = text[i:i + chunk_size]
            if chunk.strip():
                chunks.append(chunk.strip())
        
        return chunks