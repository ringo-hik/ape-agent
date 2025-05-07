#!/bin/bash

# 새 저장소 설정 스크립트
set -e

# 디렉토리 경로 설정
TARGET_DIR="/home/hik90/ape/ape-supervisor/core"
REMOTE_URL="https://github.com/ringo-hik/ape-core.git"

echo "=== APE Core 새 저장소 설정 ==="
echo "대상 디렉토리: $TARGET_DIR"

# 1. Git 저장소 초기화
cd "$TARGET_DIR"
git init
echo "Git 저장소 초기화 완료"

# 2. 모든 파일 추가
git add .
echo "모든 파일 추가 완료"

# 3. 첫 번째 커밋 생성
git commit -m "APE Core: 초기 코드 베이스"
echo "첫 번째 커밋 완료"

# 4. 원격 저장소 연결
git remote add origin "$REMOTE_URL"
echo "원격 저장소 연결 완료"

# 5. main-core 브랜치 생성
git checkout -b main-core
echo "main-core 브랜치 생성 완료"

# 6. 원격 저장소에 푸시
echo "원격 저장소에 푸시 중..."
git push -u origin main-core

echo "=== 완료! ==="
echo "새 저장소가 성공적으로 설정되었습니다."
echo "브랜치: main-core"
echo "원격 저장소: $REMOTE_URL"