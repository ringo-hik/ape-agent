"""LLM 서비스 모듈

LLM 모델 호출 및 관리하는 기능을 제공합니다.
"""

import os
import json
import time
import logging
import requests
from typing import Dict, List, Any, Optional, Union, Generator

from src.core.config import get_settings, get_model_config, get_available_models, get_default_model, set_default_model

# 로거 설정
logger = logging.getLogger("llm_service")

class LLMService:
    """LLM 서비스 클래스"""
    
    def __init__(self):
        """LLM 서비스 초기화"""
        self.settings = get_settings()
        self.current_model = get_default_model()
        self.model_config = get_model_config(self.current_model)
        self.available_providers = self._get_available_providers()
        self.model_id = self.model_config.get("id", "")
    
    def _get_available_providers(self) -> List[str]:
        """사용 가능한 LLM 프로바이더 목록 반환"""
        providers = set()
        
        # 모든 사용 가능한 모델을 확인하여 프로바이더 목록 생성
        for model_key in get_available_models():
            model_config = get_model_config(model_key)
            provider = model_config.get("provider")
            if provider:
                providers.add(provider)
        
        return list(providers)
    
    def list_available_models(self) -> List[Dict[str, Any]]:
        """사용 가능한 모델 목록 반환 (상세 정보 포함)"""
        models_info = []
        
        for model_key in get_available_models():
            model_config = get_model_config(model_key)
            models_info.append({
                "key": model_key,
                "name": model_config.get("name", model_key),
                "provider": model_config.get("provider", "unknown"),
                "description": model_config.get("description", ""),
                "id": model_config.get("id", model_key)
            })
        
        return models_info
    
    def get_current_model(self) -> str:
        """현재 사용 중인 모델 키 반환"""
        return self.current_model
    
    def change_model(self, model_key: str) -> bool:
        """사용 모델 변경"""
        available_models = get_available_models()
        
        if model_key not in available_models:
            logger.error(f"사용할 수 없는 모델: {model_key}")
            return False
        
        # 모델 설정 변경
        self.current_model = model_key
        self.model_config = get_model_config(model_key)
        self.model_id = self.model_config.get("id", "")
        
        # 기본 모델 설정 업데이트
        set_default_model(model_key)
        
        logger.info(f"모델 변경 완료: {model_key} ({self.model_config.get('name')})")
        return True
    
    def format_system_message(self, content: str) -> Dict[str, str]:
        """시스템 메시지 형식화"""
        return {"role": "system", "content": content}
    
    def format_user_message(self, content: str) -> Dict[str, str]:
        """사용자 메시지 형식화"""
        return {"role": "user", "content": content}
    
    def format_assistant_message(self, content: str) -> Dict[str, str]:
        """어시스턴트 메시지 형식화"""
        return {"role": "assistant", "content": content}
    
    def generate(self, messages: List[Dict[str, str]], stream: bool = False) -> Union[str, Generator[str, None, None]]:
        """메시지 생성"""
        if stream:
            return self._generate_stream(messages)
        else:
            return self._generate_sync(messages)
    
    def _generate_sync(self, messages: List[Dict[str, str]]) -> Union[str, Dict[str, str]]:
        """동기 방식 메시지 생성"""
        # API 키가 mock, empty 또는 비어 있으면 가짜 응답 반환
        api_key = self.model_config.get("apiKey", "")
        if not api_key or api_key.startswith("mock_") or api_key == "your-api-key":
            logger.info(f"MOCK 모드로 {self.model_config.get('provider')} LLM 호출 (API 키 미설정)")
            return self._generate_mock_response(messages)
            
        # 모델 정보 가져오기
        model_name = self.model_config.get("name", self.current_model)
        
        try:
            return self._call_llm_service(messages)
        except Exception as e:
            error_msg = f"{model_name} 모델 호출 실패: {str(e)}"
            logger.warning(error_msg)
            
            # 오류 반환
            return {"error": error_msg}
        
    def _generate_mock_response(self, messages: List[Dict[str, str]]) -> str:
        """목(Mock) 응답 생성
        
        테스트 환경에서만 사용되는 가짜 응답 생성기
        """
        # 마지막 사용자 메시지 찾기
        user_message = ""
        for msg in reversed(messages):
            if msg.get("role") == "user":
                user_message = msg.get("content", "")
                break
        
        # 질문에 대한 기본 응답
        if "APE" in user_message or "에이전트" in user_message:
            return """APE(Agentic Pipeline Engine)는 다양한 LLM 모델과 RAG(Retrieval-Augmented Generation) 및 LangGraph 기능을 제공하는 백엔드 서버입니다. 

주요 기능:
1. 다양한 LLM 모델 연결 (자동 대체 기능 포함)
2. RAG를 통한 문서 검색 및 지식 기반 응답
3. 에이전트 시스템을 통한 다양한 태스크 처리
4. LangGraph를 통한 워크플로우 자동화

자세한 내용은 문서를 참조하세요."""
        else:
            return f"죄송합니다만, '{user_message}'에 대한 정보를 찾을 수 없습니다. 다른 질문을 해주시겠어요?"
    
    def _generate_stream(self, messages: List[Dict[str, str]]) -> Generator[str, None, None]:
        """스트리밍 방식 메시지 생성"""
        # API 키가 mock, empty 또는 비어 있으면 가짜 응답 반환
        api_key = self.model_config.get("apiKey", "")
        if not api_key or api_key.startswith("mock_") or api_key == "your-api-key":
            logger.info(f"MOCK 모드로 {self.model_config.get('provider')} LLM 스트리밍 호출 (API 키 미설정)")
            yield from self._generate_mock_stream(messages)
            return
            
        # 모델 정보 가져오기
        model_name = self.model_config.get("name", self.current_model)
        
        try:
            yield from self._call_llm_service_stream(messages)
            return
        except Exception as e:
            error_msg = f"{model_name} 모델 스트리밍 호출 실패: {str(e)}"
            logger.warning(error_msg)
            
            # 오류 반환
            yield f"오류: {error_msg}"
        
    def _generate_mock_stream(self, messages: List[Dict[str, str]]) -> Generator[str, None, None]:
        """목(Mock) 스트리밍 응답 생성
        
        테스트 환경에서만 사용되는 가짜 스트리밍 응답 생성기
        """
        # 마지막 사용자 메시지 찾기
        user_message = ""
        for msg in reversed(messages):
            if msg.get("role") == "user":
                user_message = msg.get("content", "")
                break
        
        # APE 관련 질문인 경우
        if "APE" in user_message or "에이전트" in user_message:
            chunks = [
                "APE(Agentic Pipeline Engine)는 ", 
                "다양한 LLM 모델과 ", 
                "RAG(Retrieval-Augmented Generation) 및 ", 
                "LangGraph 기능을 제공하는 ", 
                "백엔드 서버입니다.\n\n",
                "주요 기능:\n",
                "1. 다양한 LLM 모델 연결 (자동 대체 기능 포함)\n",
                "2. RAG를 통한 문서 검색 및 지식 기반 응답\n",
                "3. 에이전트 시스템을 통한 다양한 태스크 처리\n",
                "4. LangGraph를 통한 워크플로우 자동화\n\n",
                "자세한 내용은 문서를 참조하세요."
            ]
        else:
            chunks = [
                "죄송합니다만, ",
                f"'{user_message}'에 대한 ",
                "정보를 찾을 수 없습니다. ",
                "다른 질문을 해주시겠어요?"
            ]
            
        # 각 청크마다 약간의 지연 추가하여 스트리밍처럼 보이게 함
        for chunk in chunks:
            time.sleep(0.1)  # 100ms 지연
            yield chunk
    
    def _get_provider_model(self, provider: str) -> Optional[str]:
        """지정된 프로바이더에 해당하는 첫 번째 모델 키 반환"""
        # 더 이상 사용하지 않는 함수지만 호환성을 위해 유지
        return None
    
    def _call_llm_service(self, messages: List[Dict[str, str]]) -> str:
        """LLM 서비스 호출"""
        endpoint = self.model_config.get("endpoint", "")
        if not endpoint:
            raise Exception("LLM 엔드포인트가 설정되지 않았습니다")
        
        # 프로바이더에 따라 적절한 호출 메서드 선택
        provider = self.model_config.get("provider", "")
        
        if provider == "openrouter":
            return self._call_openrouter(messages, self.model_config)
        else:
            return self._call_standard_llm(messages, self.model_config)
    
    def _call_llm_service_stream(self, messages: List[Dict[str, str]]) -> Generator[str, None, None]:
        """LLM 서비스 스트리밍 호출"""
        endpoint = self.model_config.get("endpoint", "")
        if not endpoint:
            raise Exception("LLM 엔드포인트가 설정되지 않았습니다")
        
        # 프로바이더에 따라 적절한 호출 메서드 선택
        provider = self.model_config.get("provider", "")
        
        if provider == "openrouter":
            yield from self._call_openrouter_stream(messages, self.model_config)
        else:
            yield from self._call_standard_llm_stream(messages, self.model_config)
    
    def _call_standard_llm(self, messages: List[Dict[str, str]], model_config: Dict[str, Any]) -> str:
        """표준 LLM 서비스 호출"""
        endpoint = model_config.get("endpoint", "")
        if not endpoint:
            raise Exception("LLM 엔드포인트가 설정되지 않았습니다")
        
        # 요청 템플릿 가져오기
        request_template = model_config.get("requestTemplate", {})
        headers = request_template.get("headers", {}).copy()
        payload = request_template.get("payload", {}).copy()
        
        # API 키 설정
        api_key = model_config.get("apiKey", "")
        
        # 헤더 변수 치환
        import uuid
        request_id = str(uuid.uuid4())
        
        for key, value in headers.items():
            if isinstance(value, str):
                # API 키 치환
                value = value.replace("${API_KEY}", api_key)
                # 요청 ID 치환
                value = value.replace("${REQUEST_ID}", request_id)
                headers[key] = value
        
        # 인증 타입에 따른 헤더 설정
        auth_type = model_config.get("auth_type", "bearer").lower()
        if auth_type != "bearer" and "Authorization" in headers:
            # Bearer가 아닌 다른 인증 방식인 경우 (예: Basic 등)
            headers["Authorization"] = f"{auth_type.capitalize()} {api_key}"
        
        # 모델 설정
        payload["messages"] = messages
        payload["temperature"] = model_config.get("temperature", 0.7)
        payload["max_tokens"] = model_config.get("maxTokens", 4096)
        payload["stream"] = False
        
        # 엔드포인트 처리
        if not endpoint.endswith("/chat/completions"):
            endpoint = endpoint.rstrip("/") + "/chat/completions"
        
        # 요청 및 응답 처리
        response = requests.post(
            endpoint,
            json=payload,
            headers=headers,
            verify=model_config.get("verify_ssl", False),
            timeout=model_config.get("timeout", 30)
        )
        
        if response.status_code != 200:
            raise Exception(f"LLM 서비스 응답 오류: {response.status_code}, {response.text}")
        
        result = response.json()
        return result.get("choices", [{}])[0].get("message", {}).get("content", "")
    
    def _call_standard_llm_stream(self, messages: List[Dict[str, str]], model_config: Dict[str, Any]) -> Generator[str, None, None]:
        """표준 LLM 서비스 스트리밍 호출"""
        endpoint = model_config.get("endpoint", "")
        if not endpoint:
            raise Exception("LLM 엔드포인트가 설정되지 않았습니다")
        
        # 요청 템플릿 가져오기
        request_template = model_config.get("requestTemplate", {})
        headers = request_template.get("headers", {}).copy()
        payload = request_template.get("payload", {}).copy()
        
        # API 키 설정
        api_key = model_config.get("apiKey", "")
        
        # 헤더 변수 치환
        import uuid
        request_id = str(uuid.uuid4())
        
        for key, value in headers.items():
            if isinstance(value, str):
                # API 키 치환
                value = value.replace("${API_KEY}", api_key)
                # 요청 ID 치환
                value = value.replace("${REQUEST_ID}", request_id)
                headers[key] = value
        
        # 인증 타입에 따른 헤더 설정
        auth_type = model_config.get("auth_type", "bearer").lower()
        if auth_type != "bearer" and "Authorization" in headers:
            # Bearer가 아닌 다른 인증 방식인 경우 (예: Basic 등)
            headers["Authorization"] = f"{auth_type.capitalize()} {api_key}"
        
        # 모델 설정
        payload["messages"] = messages
        payload["temperature"] = model_config.get("temperature", 0.7)
        payload["max_tokens"] = model_config.get("maxTokens", 4096)
        payload["stream"] = True
        
        # 엔드포인트 처리
        if not endpoint.endswith("/chat/completions"):
            endpoint = endpoint.rstrip("/") + "/chat/completions"
        
        # 요청 및 응답 처리
        response = requests.post(
            endpoint,
            json=payload,
            headers=headers,
            verify=model_config.get("verify_ssl", False),
            stream=True,
            timeout=model_config.get("timeout", 30)
        )
        
        if response.status_code != 200:
            raise Exception(f"LLM 서비스 스트리밍 응답 오류: {response.status_code}, {response.text}")
        
        for chunk in response.iter_lines():
            if chunk:
                try:
                    data = chunk.decode('utf-8')
                    if data.startswith('data: '):
                        data = data[6:]
                    if data == "[DONE]":
                        break
                    
                    json_data = json.loads(data)
                    delta = json_data.get("choices", [{}])[0].get("delta", {})
                    content = delta.get("content", "")
                    
                    if content:
                        yield content
                except Exception as e:
                    logger.error(f"LLM 스트리밍 청크 처리 오류: {e}")
    
    def _call_openrouter(self, messages: List[Dict[str, str]], model_config: Dict[str, Any]) -> str:
        """OpenRouter 호출"""
        endpoint = model_config.get("endpoint", "")
        if not endpoint:
            raise Exception("OpenRouter 엔드포인트가 설정되지 않았습니다")
        
        api_key = model_config.get("apiKey", "")
        if not api_key and "OPENROUTER_API_KEY" in os.environ:
            api_key = os.environ["OPENROUTER_API_KEY"]
        
        if not api_key:
            raise Exception("OpenRouter API 키가 설정되지 않았습니다")
        
        # 요청 템플릿 가져오기
        request_template = model_config.get("requestTemplate", {})
        headers = request_template.get("headers", {}).copy()
        payload = request_template.get("payload", {}).copy()
        
        # 헤더 변수 치환
        import uuid
        request_id = str(uuid.uuid4())
        
        for key, value in headers.items():
            if isinstance(value, str):
                # API 키 치환
                value = value.replace("${API_KEY}", api_key)
                # 요청 ID 치환
                value = value.replace("${REQUEST_ID}", request_id)
                headers[key] = value
        
        # 모델 설정
        model_id = model_config.get("id", "")
        payload["model"] = model_id
        payload["messages"] = messages
        payload["temperature"] = model_config.get("temperature", 0.7)
        payload["max_tokens"] = model_config.get("maxTokens", 4096)
        payload["stream"] = False
        
        # 엔드포인트 처리
        if not endpoint.endswith("/chat/completions"):
            endpoint = endpoint.rstrip("/") + "/chat/completions"
        
        # 요청 및 응답 처리
        response = requests.post(
            endpoint,
            json=payload,
            headers=headers,
            timeout=model_config.get("timeout", 30)
        )
        
        if response.status_code != 200:
            raise Exception(f"OpenRouter 응답 오류: {response.status_code}, {response.text}")
        
        result = response.json()
        return result.get("choices", [{}])[0].get("message", {}).get("content", "")
    
    def _call_openrouter_stream(self, messages: List[Dict[str, str]], model_config: Dict[str, Any]) -> Generator[str, None, None]:
        """OpenRouter 스트리밍 호출"""
        endpoint = model_config.get("endpoint", "")
        if not endpoint:
            raise Exception("OpenRouter 엔드포인트가 설정되지 않았습니다")
        
        api_key = model_config.get("apiKey", "")
        if not api_key and "OPENROUTER_API_KEY" in os.environ:
            api_key = os.environ["OPENROUTER_API_KEY"]
        
        if not api_key:
            raise Exception("OpenRouter API 키가 설정되지 않았습니다")
        
        # 요청 템플릿 가져오기
        request_template = model_config.get("requestTemplate", {})
        headers = request_template.get("headers", {}).copy()
        payload = request_template.get("payload", {}).copy()
        
        # API 키 설정
        for key, value in headers.items():
            if isinstance(value, str):
                headers[key] = value.replace("${API_KEY}", api_key)
        
        # 모델 설정
        model_id = model_config.get("id", "")
        payload["model"] = model_id
        payload["messages"] = messages
        payload["temperature"] = model_config.get("temperature", 0.7)
        payload["max_tokens"] = model_config.get("maxTokens", 4096)
        payload["stream"] = True
        
        # 요청 및 응답 처리
        response = requests.post(
            endpoint,
            json=payload,
            headers=headers,
            stream=True,
            timeout=model_config.get("timeout", 30)
        )
        
        if response.status_code != 200:
            raise Exception(f"OpenRouter 스트리밍 응답 오류: {response.status_code}, {response.text}")
        
        for chunk in response.iter_lines():
            if chunk:
                try:
                    data = chunk.decode('utf-8')
                    if data.startswith('data: '):
                        data = data[6:]
                    if data == "[DONE]":
                        break
                    
                    json_data = json.loads(data)
                    delta = json_data.get("choices", [{}])[0].get("delta", {})
                    content = delta.get("content", "")
                    
                    if content:
                        yield content
                except Exception as e:
                    logger.error(f"OpenRouter 스트리밍 청크 처리 오류: {e}")

# 싱글톤 인스턴스
llm_service = LLMService()