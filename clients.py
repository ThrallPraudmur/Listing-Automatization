import os
import time
import base64
import requests

import logging

from typing import Optional, List, Any

from langchain_core.outputs import LLMResult
from langchain_core.language_models.llms import BaseLLM
from langchain_core.callbacks.manager import CallbackManagerForLLMRun

from config import Config
from exceptions import LLMError, AuthenticationError, RateLimitError, TimeOutError

logger = logging.getLogger(__name__)


class OCRClient:
    def __init__(self):
        self.base_url = Config.OCR_API_URL

    def process_binary_data(self, binary_data: bytes) -> str:
        try:
            base64_str = base64.b64encode(binary_data).decode('ascii')
            data = {
                'is_base64_or_document': True,
                'docs': [{'filename': 'doc.pdf', 'data': base64_str, 'type': 'application/pdf'}]
            }
            response = requests.post(f'{self.base_url}/ocr/docling/parse', json=data, verify=False,)
            response.raise_for_status()
            return response.json()[0]['file_text']

        except Exception as e:
            logging.error(f"Ошибка обработки файла файла: {e}")
            raise


class ICBDClient:
    """Клиент для работы с ICBD"""
    def __init__(self):
        self.base_url = Config.ICBD_BASE_URL
        self.proxy_url = Config.ICBD_PROXY_URL
        self.ocr_base_url = Config.OCR_API_URL

        # url = f"{self.base_url}?userFormFileId={file_id}"

    def get_file(self, file_id: str, flag_p7s: bool) -> str:
        """Загрузка файла из ICBD"""
        try:
            file_name = 'document.pdf'
            filepath = os.path.join(os.getcwd(), file_name)

            url = self.base_url + '/proxy/' + self.proxy_url + '//api/DownloadFile?userFormFileId=' + file_id
            ocr_url = self.ocr_base_url + '/ocr/docling/upload'

            import urllib.request
            urllib.request.urlretrieve(url, filepath)

            with open(file_name, 'rb') as f:
                response = requests.post(
                    ocr_url,
                    files = {'file': (file_name, f, 'application/pdf')},
                    verify = False
                )
                response.raise_for_status()

            os.remove(filepath)

            logging.info(f"Файл {file_id} успешно загружен из ICBD")
            return response.json()[0]['file_text']

        except Exception as e:
            logging.error(f"Ошибка загрузки файла {file_id} из ICBD: {e}")
            raise