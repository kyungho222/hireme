@echo off
echo ========================================
echo PickTalk Backend 설치 스크립트
echo ========================================
echo.

echo [1/5] Python 버전 확인...
python --version
if %errorlevel% neq 0 (
    echo 오류: Python이 설치되지 않았습니다.
    echo Python 3.8+ 를 설치해주세요: https://www.python.org/downloads/
    pause
    exit /b 1
)
echo.

echo [2/5] 가상환경 생성...
python -m venv venv
if %errorlevel% neq 0 (
    echo 오류: 가상환경 생성에 실패했습니다.
    pause
    exit /b 1
)
echo.

echo [3/5] 가상환경 활성화...
call venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo 오류: 가상환경 활성화에 실패했습니다.
    pause
    exit /b 1
)
echo.

echo [4/5] 의존성 설치...
pip install --upgrade pip
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo 오류: 의존성 설치에 실패했습니다.
    pause
    exit /b 1
)
echo.

echo [5/5] 환경 변수 파일 생성...
if not exist .env (
    copy .env.example .env
    echo .env 파일이 생성되었습니다.
    echo .env 파일을 열어서 OPENAI_API_KEY를 설정해주세요.
) else (
    echo .env 파일이 이미 존재합니다.
)
echo.

echo ========================================
echo 설치가 완료되었습니다!
echo ========================================
echo.
echo 다음 단계:
echo 1. .env 파일을 열어서 OPENAI_API_KEY를 설정하세요
echo 2. MongoDB를 설치하고 실행하세요
echo 3. run.bat을 실행하여 서버를 시작하세요
echo.
echo API 문서: http://localhost:8000/docs
echo.
pause
