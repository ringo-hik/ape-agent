"""LLM 서비스 관리 모듈

이 모듈은 LLM 모델 설정을 관리합니다.
"""

import os
import logging
from typing import Dict, Any, List, Optional, Union

# 모델 설정 직접 임포트
from config.models_config import MODELS, DEFAULT_MODEL, get_models, get_default_model

# 로거 설정
logger = logging.getLogger("network_manager")

class NetworkManager:
    """LLM 서비스 관리 클래스"""
    
    def __init__(self):
        """네트워크 관리자 초기화"""
        self.available_models = self._get_available_models()
        logger.info(f"네트워크 관리자 초기화 완료 (기본 모델: {self.get_default_model_key()})")
        
    def _get_available_models(self) -> Dict[str, Dict[str, Any]]:
        """사용 가능한 모델 목록 반환"""
        return get_models()
    
    def get_default_model_key(self) -> str:
        """기본 모델 키 반환"""
        return get_default_model()
    
    def get_available_model_keys(self) -> List[str]:
        """사용 가능한 모델 키 목록 반환"""
        return list(self.available_models.keys())
    
    def get_model_config(self, model_key: str) -> Optional[Dict[str, Any]]:
        """모델 구성 반환
        
        Args:
            model_key (str): 모델 키
            
        Returns:
            Optional[Dict[str, Any]]: 모델 구성 또는 None (모델 없음)
        """
        if model_key not in self.available_models:
            logger.warning(f"모델 키를 찾을 수 없음: {model_key}, 기본 모델 사용: {self.get_default_model_key()}")
            return self.available_models.get(self.get_default_model_key(), {})
        return self.available_models.get(model_key)
    
    def refresh_models(self) -> None:
        """사용 가능한 모델 목록 갱신"""
        self.available_models = self._get_available_models()
        logger.debug(f"모델 목록 갱신 완료: {len(self.available_models)} 모델 사용 가능")
    
    def get_status(self) -> Dict[str, Any]:
        """네트워크 상태 정보 반환"""
        return {
            "available_models": len(self.available_models),
            "model_keys": self.get_available_model_keys(),
            "default_model": self.get_default_model_key()
        }

# 싱글톤 인스턴스
network_manager = NetworkManager()