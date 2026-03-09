import io
import sys
import html
import requests
from typing import Dict

import logging
import streamlit as st

import io
from PyPDF2 import PdfReader

from shared.config import Config
from exceptions import AuthenticationError, LLMError, OCRError, GateweyTimeoutOutError

from langchain.output_parsers import PydanticOutputParser

from design import display_text_with_scroll
from document_handlers import DocumentHandlerRegistry
from text_cleaner import text_cleaner

logger = logging.getLogger(__name__)


def is_garbage(text): # mojibake
    """
    Быстрая проверка - нужен ли OCR
    """
    import re

    # Считаем "хорошие" и "плохие" паттерны
    good_patterns = [
        r'\b[а-яА-ЯёЁ]{4,}\b',  # русские слова
        r'\b\d{2}\.\d{2}\.\d{4}\b',  # даты
        r'\b[А-Я]{2,}\b',  # аббревиатуры
        r'\b№\s*\d+\b',  # номера
    ]

    bad_patterns = [
        r'[†‡•‣⁃ƒ†‡ˆ‰Š‹ŒŽ]',
        r'[¡¢£¤¥¦§¨©ª«¬®¯°±²³´µ¶·¸¹º»¼½¾¿]',
        r'[ÐÑÒÓÔÕÖ×ØÙÚÛÜÝÞßðñòóôõö÷øùúûüýþÿ]',
        r'[âãäåæçèéêëìíîï]',
    ]

    good_count = sum(len(re.findall(p, text)) for p in good_patterns)
    bad_count = sum(len(re.findall(p, text)) for p in bad_patterns)
    print(bad_count / good_count) # float

    # Если плохих символов больше чем хороших слов
    if (bad_count / good_count) > 0.3:
        return True

    return False
    

def get_ocr_client():
    from shared.clients import OCRClient
    return OCRClient()
    

ocr_client = get_ocr_client()


class DocumentClassifier:

    def __init__(self, llm_client):
        self.llm = llm_client
        # Получаем все доступные типы документов
        doc_types = DocumentHandlerRegistry.get_all_types()
        self.doc_types_str = ", ".join(doc_types)

    def classify(self, text: str) -> str:

        from langchain_core.prompts import ChatPromptTemplate
        from langchain_core.output_parsers import StrOutputParser

        prompt = ChatPromptTemplate.from_messages([
            ("system", f"""/no_think Ты классификатор документов.
            Верни только название документа из следующего списка: 
            {self.doc_types_str}            
            Если документ нельзя отнести ни к одному типу документов, ответь одним словом НЕИЗВЕСТНЫЙ.
            """),
            ("human", "{text}")
        ])

        chain = prompt | self.llm | StrOutputParser()
        result = chain.invoke({"text": text}).strip().lower()

        return result


class DocumentProcessor:
    def __init__(self):
        self.llm = LLMClient()
        self.classifier = DocumentClassifier(self.llm)

    def process_uploaded_files(self):
        if st.session_state.all_results is None:
            uploaded_files = st.file_uploader(
                '📥 Загрузите документы для проверки',
                type=['pdf', 'txt'],
                accept_multiple_files=True,
                key='ex_txt_uploader'
            )
            if uploaded_files:

                all_results = []
                error_count = 0

                with st.spinner('Обработка документов...'):
                    progress_bar = st.progress(0)
                    for i, file in enumerate(uploaded_files):
                        try:
                            if file.name.endswith('pdf'):
                                # success, text = _process_pdfs_text_by_lab([file])

                                from PyPDF2 import PdfReader

                                pdf_bytes = io.BytesIO(file.getvalue())
                                pdf_reader = PdfReader(pdf_bytes)
                                text = ''
                                for page in pdf_reader.pages:
                                    text += page.extract_text()
                                    text += '\n'

                                # len(pdf_reader.pages[0].extract_text())

                                # text = pdf_reader.pages[0].extract_text()

                                import re
                                if not bool(re.search('[а-яА-ЯёЁ]', text)) or is_garbage(text):
                                    success, text = _process_pdfs_text_by_lab([file])

                                # print(text)
                                result = self._process_single_file(text)
                            else:
                                text = file.getvalue().decode('utf-8')
                                result = self._process_single_file(text)

                            all_results.append(result) # Если обработка успешна + {doc_type, entities, raw_text, handler}

                        except(LLMError, OCRError, GateweyTimeoutOutError) as e:

                            logger.error(f'Processing failed for {file.name}: {str(e)}')
                            error_count += 1
                            all_results.append({
                                'file_name': file.name,
                                'error': f'Ошибка обработки: {str(e)}',
                                'error_type': type(e).__name__
                            })

                        except Exception as e:

                            logger.exception(f'Unexpected error processing {file.name}')
                            error_count += 1
                            all_results.append({
                                'file_name': file.name,
                                'error': 'Внутренняя ошибка системы',
                                'error_type': 'InternalError'
                            })

                        progress_bar.progress((i + 1) / len(uploaded_files))

                    if error_count > 0:
                        st.warning(f'Обработано с ошибками: {error_count} из {len(uploaded_files)} файлов')

                    st.session_state.all_results = all_results
                    st.rerun()

    def _process_single_file(self, text) -> Dict:

        """Обрабатываем один документ"""
        doc_type = self.classifier.classify(text)
        handler = DocumentHandlerRegistry.get_handler(doc_type)

        if not handler:
            return {
                "doc_type": doc_type,
                "entities": {},
                "raw_text": text,
                # "error": f"Неизвестный тип: {doc_type}", # None - если не определён тип из предлагаемого списка
            }

        # Получаем промпт и схему
        prompt = handler.get_prompt()
        schema = handler.get_schema()

        # Вызываем LLM
        chain = prompt | self.llm
        parser = PydanticOutputParser(pydantic_object=schema)

        try:
            result = chain.invoke({"text": text})
            # print(result)
            entities = parser.parse(result)

            return {
                "doc_type": doc_type,
                "entities": entities.dict(),
                "raw_text": text,
                "handler": handler,
            }

        except Exception as e:
            logger.error(f"Error processing document: {e}")
            return {
                "doc_type": doc_type,
                "entities": {},
                "raw_text": text,
                "error": str(e),
            }


def render_documents_views():
    """Безопасное отображение результатов обработки документов с предобработкой ошибок"""
    for i, result in enumerate(st.session_state.all_results):

        # Отображение ошибок
        if 'error' in result:
            error_type = result.get('error_type', 'UnknownError')

            if error_type in ['AuthenticationError', 'RateLimitError']:
                st.error('🔐 Ошибка доступа')
            elif error_type == 'TimeoutError':
                st.error('⏳ Превышен таймаут запроса')
            elif error_type == 'ConnectionError':
                st.error('🌍 Ошибка соединения')
            elif error_type == 'GateweyTimeoutOutError':
                st.error('🪐 Модель была временно не доступна')
            else:
                st.error('🧩 Ошибка при разборе документа')
            continue

        if 'doc_type' in result:

            # Успешная обработка документа
            doc_type = result.get('doc_type', 'unknown')
            handler = result.get('handler')

            cleaned_text = text_cleaner(result['raw_text'])

            with st.expander(f"📄 {doc_type.upper()}", expanded = False):
                st.success(f"Тип документа: {doc_type.upper()}")
                display_text_with_scroll(cleaned_text)