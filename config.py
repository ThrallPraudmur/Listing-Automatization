import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    LLM_API_KEY = os.getenv('LLM_API_KEY')
    LLM_API_URL = os.getenv('LLM_API_URL')
    MODEL_NAME = os.getenv('MODEL_NAME')
    MAX_TOKENS = os.getenv('MAX_TOKENS')
    TEMPERATURE = os.getenv('TEMPERATURE')
    KEYCLOAK_CLIENT_ID = os.getenv('KEYCLOAK_CLIENT_ID')
    KEYCLOAK_AUTH_URL = os.getenv('KEYCLOAK_AUTH_URL')
    KEYCLOAK_REALM = os.getenv('KEYCLOAK_REALM')
    KEYCLOAK_REDIRECT_URI = os.getenv('KEYCLOAK_REDIRECT_URI')
    NUXEO_API_URL = os.getenv('NUXEO_API_URL')
    OCR_API_URL = os.getenv('OCR_API_URL')
    API_ENDPOINT = os.getenv('API_ENDPOINT')
    ICBD_BASE_URL = os.getenv('ICBD_BASE_URL')
    ICBD_PROXY_URL = os.getenv('ICBD_PROXY_URL')