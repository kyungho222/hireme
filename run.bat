@echo off
echo ========================================
echo PickTalk Backend 서버 시작
echo ========================================
echo.

echo 가상환경 활성화...
call venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo 오류: 가상환경을 찾을 수 없습니다.
    echo install.bat을 먼저 실행해주세요.
    pause
    exit /b 1
)
echo.

echo .env 파일 확인...
if not exist .env (
    echo 오류: .env 파일이 없습니다.
    echo install.bat을 먼저 실행해주세요.
    pause
    exit /b 1
)
echo.

echo 서버 시작 중...
echo.
echo 서버 주소: http://localhost:8000
echo API 문서: http://localhost:8000/docs
echo.
echo 서버를 중지하려면 Ctrl+C를 누르세요.
echo.

python main.py
