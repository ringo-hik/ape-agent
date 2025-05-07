#!/bin/bash
# APE Core 모델 설정 테스트 스크립트

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR" || exit 1

# 가상 환경 활성화
if [ -d "ape_venv" ]; then
    echo "가상 환경 활성화: ape_venv"
    source ape_venv/bin/activate
else
    echo "경고: 가상 환경(ape_venv)을 찾을 수 없습니다."
    exit 1
fi

# 모델 설정 테스트
echo "모델 설정 테스트 중..."
python -c "
import sys
import json
sys.path.append('.')
from config.models_config import get_models, get_default_model

# 모델 정보 가져오기
models = get_models()
default_model = get_default_model()

# 결과 출력
print(f'\n모델 정보 테스트:')
print(f'- 사용 가능한 모델 수: {len(models)}')
print(f'- 기본 모델: {default_model}')
print('\n모델 목록:')
for key, model in models.items():
    print(f'  - {key}: {model[\"name\"]} ({model[\"provider\"]})')
"

# LLM 서비스 테스트 코드 - 모의 응답 테스트
echo -e "\nLLM 서비스 테스트 중..."
python -c "
import sys
sys.path.append('.')
from src.core.llm_service import LLMService

# 테스트용 API 키 설정
import os
os.environ['LLM_API_KEY'] = 'mock_test_key'

# LLM 서비스 인스턴스 생성
llm = LLMService()

# 테스트 메시지
messages = [
    {'role': 'system', 'content': 'You are a helpful assistant.'},
    {'role': 'user', 'content': 'APE란 무엇인가요?'}
]

# 동기 모드 테스트
print('\n동기 호출 테스트:')
response = llm.generate(messages)
print(f'응답: {response[:100]}... (생략)')

# 스트리밍 모드 테스트
print('\n스트리밍 호출 테스트:')
print('응답: ', end='', flush=True)
for chunk in llm.generate(messages, stream=True):
    print(chunk, end='', flush=True)
print('')
"

# 가상 환경 비활성화
deactivate

echo -e "\n테스트 완료!"