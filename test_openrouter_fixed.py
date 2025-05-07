#!/usr/bin/env python3
"""
OpenRouter LLM 서비스 테스트 스크립트

이 스크립트는 OpenRouter API를 사용하여 LLM 모델에 직접 연결하고 
응답을 받는 테스트를 수행합니다.
"""

import sys
import os
import json
import time

sys.path.append('.')
from src.core.env_loader import get_env
from src.core.llm_service import LLMService

def test_openrouter():
    """OpenRouter LLM 연결 테스트"""
    
    print("\n===== LLM 연결 테스트 =====")
    
    # LLM 서비스 초기화
    print(f"LLM 서비스 초기화 중...")
    llm = LLMService()
    
    # 사용자 메시지 구성
    print(f"테스트 메시지 구성 중...")
    messages = [
        llm.format_system_message("You are a helpful AI assistant."),
        llm.format_user_message("Introduce yourself in Korean using 3 sentences only.")
    ]
    
    # 동기 호출 테스트
    print("\n동기 호출 테스트:")
    start_time = time.time()
    print("LLM API 호출 중...")
    
    try:
        response = llm.generate(messages)
        print(f"응답 시간: {time.time() - start_time:.2f}초")
        
        if isinstance(response, dict) and "error" in response:
            print(f"오류: {response['error']}")
            return False
            
        print("응답 내용:")
        print("-" * 50)
        print(response)
        print("-" * 50)
        return True
        
    except Exception as e:
        print(f"LLM API 호출 중 오류 발생: {e}")
        return False

if __name__ == "__main__":
    # 기본 API 키 설정 - 환경 변수에서 로드
    # 사용 모델 변경
    os.environ["DEFAULT_MODEL"] = "openrouter-llama"
    
    # 가상 환경 확인
    if not os.path.exists("ape_venv"):
        print("가상 환경(ape_venv)이 필요합니다. 먼저 setup.sh를 실행해주세요.")
        sys.exit(1)
    
    # 테스트 실행
    success = test_openrouter()
    
    if success:
        print("\n✅ LLM 연결 테스트 성공!")
    else:
        print("\n❌ LLM 연결 테스트 실패")
        sys.exit(1)