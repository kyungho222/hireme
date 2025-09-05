#!/bin/bash

echo "========================================"
echo "PickTalk Backend 서버 시작"
echo "========================================"
echo

echo "가상환경 활성화..."
source venv/bin/activate
if [ $? -ne 0 ]; then
    echo "오류: 가상환경을 찾을 수 없습니다."
    echo "./install.sh을 먼저 실행해주세요."
    exit 1
fi
echo

echo ".env 파일 확인..."
if [ ! -f .env ]; then
    echo "오류: .env 파일이 없습니다."
    echo "./install.sh을 먼저 실행해주세요."
    exit 1
fi
echo

echo "서버 시작 중..."
echo
echo "서버 주소: http://localhost:8000"
echo "API 문서: http://localhost:8000/docs"
echo
echo "서버를 중지하려면 Ctrl+C를 누르세요."
echo

python main.py
