"""설정 관리 모듈

이 모듈은 애플리케이션 설정을 로드하고 관리합니다.
환경 변수와 설정 파일을 처리합니다.
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
from dotenv import load_dotenv

# 로거 설정
logger = logging.getLogger("config")

# 순환 임포트 문제 해결을 위해 지연 임포트 사용
# 필요한 위치에서 동적으로 임포트합니다

# 기본 디렉토리 설정
BASE_DIR = Path(__file__).parent.parent.parent.absolute()
CONFIG_DIR = BASE_DIR / "config"
MODELS_DIR = BASE_DIR / "models"
DATA_DIR = BASE_DIR / "data"

# 설정 저장소
_SETTINGS = {}

def load_dotenv_file():
    """환경 변수 파일 로드"""
    dotenv_path = BASE_DIR / ".env"
    if dotenv_path.exists():
        load_dotenv(dotenv_path)
        logger.info(f"환경 변수 로드 완료: {dotenv_path}")
    else:
        logger.warning(f"환경 변수 파일을 찾을 수 없음: {dotenv_path}")

def get_env(key: str, default: str = "") -> str:
    """환경 변수 값 가져오기"""
    return os.environ.get(key, default)

def get_boolean_env(key: str, default: bool = False) -> bool:
    """부울 환경 변수 값 가져오기"""
    value = os.environ.get(key, str(default)).lower()
    return value in ["true", "1", "yes", "y", "t"]

def get_int_env(key: str, default: int = 0) -> int:
    """정수 환경 변수 값 가져오기"""
    try:
        return int(os.environ.get(key, str(default)))
    except ValueError:
        return default

def get_float_env(key: str, default: float = 0.0) -> float:
    """실수 환경 변수 값 가져오기"""
    try:
        return float(os.environ.get(key, str(default)))
    except ValueError:
        return default

def get_list_env(key: str, default: List[str] = None) -> List[str]:
    """리스트 환경 변수 값 가져오기"""
    if default is None:
        default = []
    value = os.environ.get(key, "")
    if not value:
        return default
    return [item.strip() for item in value.split(",")]

def resolve_env_vars(config: Dict[str, Any]) -> Dict[str, Any]:
    """설정 사전의 환경 변수 플레이스홀더 해결"""
    resolved = {}
    
    for key, value in config.items():
        if isinstance(value, dict):
            resolved[key] = resolve_env_vars(value)
        elif isinstance(value, str) and value.startswith("${")\
                and value.endswith("}"):
            # 환경 변수 해결
            env_key = value[2:-1]
            if ":" in env_key:
                # 기본값 있음
                env_key, default = env_key.split(":", 1)
                resolved[key] = get_env(env_key, default)
            else:
                # 기본값 없음
                resolved[key] = get_env(env_key, "")
        else:
            resolved[key] = value
    
    return resolved

def load_settings_file() -> Dict[str, Any]:
    """설정 파일 로드"""
    settings_path = CONFIG_DIR / "settings.json"
    if not settings_path.exists():
        logger.warning(f"설정 파일을 찾을 수 없음: {settings_path}")
        return {}
    
    try:
        with open(settings_path, 'r', encoding='utf-8') as f:
            settings = json.load(f)
        logger.info(f"설정 파일 로드 완료: {settings_path}")
        return settings
    except Exception as e:
        logger.error(f"설정 파일 로드 오류: {e}")
        return {}

def load_config():
    """전체 설정 로드"""
    global _SETTINGS
    
    # 환경 변수 로드
    load_dotenv_file()
    
    # 설정 파일 로드
    settings = load_settings_file()
    
    # 환경 변수 해결
    _SETTINGS = resolve_env_vars(settings)
    
    # 기본값 설정
    if not _SETTINGS.get("api", {}).get("host"):
        _SETTINGS.setdefault("api", {})["host"] = "localhost"
        
    if not _SETTINGS.get("api", {}).get("port"):
        _SETTINGS.setdefault("api", {})["port"] = "8001"
    
    logger.info("설정 로드 완료")
    return _SETTINGS

def get_settings() -> Dict[str, Any]:
    """현재 설정 가져오기"""
    global _SETTINGS
    if not _SETTINGS:
        return load_config()
    return _SETTINGS

# No embedding, vector DB, document processing, or search config functions

def get_agent_config(agent_type: str) -> Dict[str, Any]:
    """에이전트 설정 가져오기"""
    settings = get_settings()
    return settings.get(agent_type, {})

def get_model_config(model_key: str) -> Dict[str, Any]:
    """모델 구성 가져오기"""
    from src.core.network_manager import network_manager
    return network_manager.get_model_config(model_key)

def get_available_models() -> List[str]:
    """사용 가능한 모델 키 목록 가져오기"""
    from src.core.network_manager import network_manager
    return network_manager.get_available_model_keys()

def get_default_model() -> str:
    """현재 네트워크 모드에 따른 기본 모델 키 가져오기"""
    from src.core.network_manager import network_manager
    return network_manager.get_default_model_key()

def set_default_model(model_key: str) -> None:
    """기본 모델 설정 업데이트"""
    # 현재는 실제로 기본 모델을 변경하는 기능은 구현되어 있지 않음
    # 나중에 필요하면 구현 예정
    pass
