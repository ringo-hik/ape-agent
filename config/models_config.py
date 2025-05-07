"""
LLM 모델 구성

이 파일은 모든 LLM 모델 설정을 정의합니다.
"""

from src.core.env_loader import get_env, get_int_env, get_float_env, get_boolean_env

# 모델 구성
MODELS = {
    "primary": {
        "name": "기본 LLM 모델",
        "id": "primary-model-v1",
        "description": "기본 LLM 서비스 모델",
        "provider": "primary",
        "endpoint": get_env("LLM_ENDPOINT", "http://llm-service/api"),
        "apiKey": get_env("LLM_API_KEY", ""),
        "maxTokens": get_int_env("LLM_MAX_TOKENS", 4096),
        "temperature": get_float_env("LLM_TEMPERATURE", 0.7),
        "requestTemplate": {
            "headers": {
                "Authorization": "Bearer ${API_KEY}",
                "Content-Type": "application/json"
            },
            "payload": {
                "model": "primary-model-v1",
                "max_tokens": 4096,
                "temperature": "${TEMPERATURE}",
                "stream": "${STREAM}",
                "messages": []
            }
        }
    },
    "korean": {
        "name": "한국어 LLM 모델",
        "id": "korean-model-v1",
        "description": "한국어 특화 LLM 서비스 모델",
        "provider": "primary",
        "endpoint": get_env("LLM_KO_ENDPOINT", "http://llm-ko-service/api"),
        "apiKey": get_env("LLM_KO_API_KEY", ""),
        "maxTokens": get_int_env("LLM_KO_MAX_TOKENS", 4096),
        "temperature": get_float_env("LLM_KO_TEMPERATURE", 0.7),
        "requestTemplate": {
            "headers": {
                "Authorization": "Bearer ${API_KEY}",
                "Content-Type": "application/json"
            },
            "payload": {
                "model": "korean-model-v1",
                "max_tokens": 4096,
                "temperature": "${TEMPERATURE}",
                "stream": "${STREAM}",
                "messages": []
            }
        }
    },
        # LLM 모델
    "openrouter-llama": {
        "name": "OpenRouter Llama3",
        "id": "meta/llama-3-70b-instruct",
        "description": "Llama3 70B 모델",
        "provider": "openrouter",
        "endpoint": "https://openrouter.ai/api/v1/chat/completions",
        "apiKey": "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",
        "maxTokens": 4096,
        "temperature": 0.7,
        "requestTemplate": {
            "headers": {
                "Authorization": "Bearer ${API_KEY}",
                "HTTP-Referer": "APE-Core-API",
                "X-Title": "APE (Agentic Pipeline Engine)",
                "Content-Type": "application/json"
            },
            "payload": {
                "model": "meta/llama-3-70b-instruct",
                "max_tokens": 4096,
                "temperature": "${TEMPERATURE}",
                "stream": "${STREAM}",
                "messages": []
            }
        }
    },
    "openrouter-claude": {
        "name": "OpenRouter Claude 3",
        "id": "anthropic/claude-3-opus-20240229",
        "description": "OpenRouter를 통한 Claude 3 Opus 모델",
        "provider": "openrouter",
        "endpoint": "https://openrouter.ai/api/v1/chat/completions",
        "apiKey": "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",
        "maxTokens": 4096,
        "temperature": 0.7,
        "requestTemplate": {
            "headers": {
                "Authorization": "Bearer ${API_KEY}",
                "HTTP-Referer": "APE-Core-API",
                "X-Title": "APE (Agentic Pipeline Engine)",
                "Content-Type": "application/json"
            },
            "payload": {
                "model": "anthropic/claude-3-opus-20240229",
                "max_tokens": 4096,
                "temperature": "${TEMPERATURE}",
                "stream": "${STREAM}",
                "messages": []
            }
        }
    },
    "openrouter-mixtral": {
        "name": "OpenRouter Mixtral",
        "id": "mistralai/mixtral-8x7b-instruct",
        "description": "OpenRouter를 통한 Mixtral 8x7B 모델",
        "provider": "openrouter",
        "endpoint": "https://openrouter.ai/api/v1/chat/completions",
        "apiKey": "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",
        "maxTokens": 4096,
        "temperature": 0.7,
        "requestTemplate": {
            "headers": {
                "Authorization": "Bearer ${API_KEY}",
                "HTTP-Referer": "APE-Core-API",
                "X-Title": "APE (Agentic Pipeline Engine)",
                "Content-Type": "application/json"
            },
            "payload": {
                "model": "mistralai/mixtral-8x7b-instruct",
                "max_tokens": 4096,
                "temperature": "${TEMPERATURE}",
                "stream": "${STREAM}",
                "messages": []
            }
        }
    },
    "openrouter-qwen": {
        "name": "OpenRouter Qwen",
        "id": "qwen/qwen1.5-72b-chat",
        "description": "OpenRouter를 통한 Qwen 1.5 72B 모델",
        "provider": "openrouter",
        "endpoint": "https://openrouter.ai/api/v1/chat/completions",
        "apiKey": "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",
        "maxTokens": 4096,
        "temperature": 0.7,
        "requestTemplate": {
            "headers": {
                "Authorization": "Bearer ${API_KEY}",
                "HTTP-Referer": "APE-Core-API",
                "X-Title": "APE (Agentic Pipeline Engine)",
                "Content-Type": "application/json"
            },
            "payload": {
                "model": "qwen/qwen1.5-72b-chat",
                "max_tokens": 4096,
                "temperature": "${TEMPERATURE}",
                "stream": "${STREAM}",
                "messages": []
            }
        }
    }
}

# 기본 모델 키
DEFAULT_MODEL = "primary"
# 기본 모델이 없을 경우 사용할 모델

def get_models():
    """모든 모델 구성 반환"""
    return MODELS

def get_default_model():
    """기본 모델 키 반환"""
    return DEFAULT_MODEL

# 더 이상 사용하지 않는 함수지만 호환성을 위해 유지
def get_default_backup_model():
    """기본 백업 모델 키 반환"""
    return DEFAULT_MODEL

def get_model_config(model_key):
    """모델 구성 반환"""
    models = get_models()
    return models.get(model_key, models.get(DEFAULT_MODEL))