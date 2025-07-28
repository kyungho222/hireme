import React, { useState } from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { 
  faBars, 
  faChevronDown,
  faUser,
  faSearch
} from '@fortawesome/free-solid-svg-icons';
import './Header.css';

const Header: React.FC = () => {
  const [mobileOpen, setMobileOpen] = useState(false);

  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen);
  };

  const menuItems = [
    { text: '공고', href: '/jobs' },
    { text: '지원서', href: '/applications' },
    { text: '포트폴리오', href: '/portfolio' },
    { text: '인재추천', href: '/recommendations' },
    { text: '면접', href: '/interviews' },
  ];

  return (
    <>
      <header className="header">
        <div className="header-container">
          {/* 로고 */}
          <a href="/" className="logo">
            HireMe
          </a>

          {/* 데스크톱 메뉴 */}
          <nav className="desktop-menu">
            {menuItems.map((item) => (
              <a key={item.text} href={item.href} className="menu-item">
                {item.text}
              </a>
            ))}
          </nav>

          {/* 우측 버튼들 */}
          <div className="header-actions">
            <button className="icon-button">
              <FontAwesomeIcon icon={faSearch} />
            </button>
            <button className="login-button">
              <FontAwesomeIcon icon={faUser} />
              <span>로그인</span>
              <FontAwesomeIcon icon={faChevronDown} />
            </button>
          </div>

          {/* 모바일 메뉴 버튼 */}
          <button 
            className="mobile-menu-button"
            onClick={handleDrawerToggle}
          >
            <FontAwesomeIcon icon={faBars} />
          </button>
        </div>
      </header>

      {/* 모바일 드로어 */}
      {mobileOpen && (
        <div className="mobile-drawer">
          <nav className="mobile-menu">
            {menuItems.map((item) => (
              <a key={item.text} href={item.href} className="mobile-menu-item">
                {item.text}
              </a>
            ))}
          </nav>
        </div>
      )}
    </>
  );
};

export default Header; 