#!/bin/bash

echo "========================================"
echo "PickTalk Backend 설치 스크립트"
echo "========================================"
echo

echo "[1/5] Python 버전 확인..."
python3 --version
if [ $? -ne 0 ]; then
    echo "오류: Python3가 설치되지 않았습니다."
    echo "Python 3.8+ 를 설치해주세요: https://www.python.org/downloads/"
    exit 1
fi
echo

echo "[2/5] 가상환경 생성..."
python3 -m venv venv
if [ $? -ne 0 ]; then
    echo "오류: 가상환경 생성에 실패했습니다."
    exit 1
fi
echo

echo "[3/5] 가상환경 활성화..."
source venv/bin/activate
if [ $? -ne 0 ]; then
    echo "오류: 가상환경 활성화에 실패했습니다."
    exit 1
fi
echo

echo "[4/5] 의존성 설치..."
pip install --upgrade pip
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "오류: 의존성 설치에 실패했습니다."
    exit 1
fi
echo

echo "[5/5] 환경 변수 파일 생성..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo ".env 파일이 생성되었습니다."
    echo ".env 파일을 열어서 OPENAI_API_KEY를 설정해주세요."
else
    echo ".env 파일이 이미 존재합니다."
fi
echo

echo "========================================"
echo "설치가 완료되었습니다!"
echo "========================================"
echo
echo "다음 단계:"
echo "1. .env 파일을 열어서 OPENAI_API_KEY를 설정하세요"
echo "2. MongoDB를 설치하고 실행하세요"
echo "3. ./run.sh을 실행하여 서버를 시작하세요"
echo
echo "API 문서: http://localhost:8000/docs"
echo
