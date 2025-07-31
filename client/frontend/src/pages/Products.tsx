import React from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { 
  faLaptopCode, 
  faBullhorn, 
  faHandshake, 
  faGraduationCap 
} from '@fortawesome/free-solid-svg-icons';
import './Products.css';

const Products: React.FC = () => {
  const products = [
    {
      title: 'IT/개발 인재',
      description: '개발자, 디자이너, 기획자 등 IT 분야 전문 인재',
      icon: faLaptopCode,
      price: '월 50만원',
      features: ['AI 매칭', '기술 스택 분석', '포트폴리오 검토'],
      category: 'IT',
    },
    {
      title: '마케팅 인재',
      description: '디지털 마케팅, 브랜드 마케팅 전문가',
      icon: faBullhorn,
      price: '월 40만원',
      features: ['캠페인 분석', '성과 측정', '전략 수립'],
      category: '마케팅',
    },
    {
      title: '영업 인재',
      description: 'B2B, B2C 영업 전문가 및 영업 관리자',
      icon: faHandshake,
      price: '월 35만원',
      features: ['영업 실적 분석', '고객 관리', '매출 증대'],
      category: '영업',
    },
    {
      title: '신입/경력',
      description: '신입 및 경력 개발자를 위한 맞춤형 채용',
      icon: faGraduationCap,
      price: '월 30만원',
      features: ['교육 프로그램', '멘토링', '커리어 개발'],
      category: '신입',
    },
  ];

  return (
    <div className="products-container">
      <div className="products-header">
        <h1 className="products-title">채용 상품</h1>
        <p className="products-subtitle">
          기업의 요구사항에 맞는 다양한 채용 상품을 제공합니다
        </p>
      </div>

      <div className="products-grid">
        {products.map((product, index) => (
          <div key={index} className="product-card">
            <div className="product-content">
              <FontAwesomeIcon 
                icon={product.icon} 
                className="product-icon"
              />
              <h6 className="product-title">{product.title}</h6>
              <p className="product-description">{product.description}</p>
              <h5 className="product-price">{product.price}</h5>
              <div className="product-features">
                {product.features.map((feature, featureIndex) => (
                  <span key={featureIndex} className="feature-chip">
                    {feature}
                  </span>
                ))}
              </div>
            </div>
            <div className="product-actions">
              <button className="btn btn-primary btn-small">상세보기</button>
              <button className="btn btn-outline btn-small">문의하기</button>
            </div>
          </div>
        ))}
      </div>

      {/* 추가 정보 */}
      <div className="additional-info">
        <h5 className="additional-title">맞춤형 채용 솔루션이 필요하신가요?</h5>
        <p className="additional-description">
          기업의 특성과 요구사항에 맞는 맞춤형 채용 서비스를 제공합니다
        </p>
        <button className="btn btn-primary btn-large">상담 신청하기</button>
      </div>
    </div>
  );
};

export default Products; 