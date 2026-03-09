import time
import json
import html

import logging
import streamlit as st

from clients import LLMClient

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

from langchain.output_parsers import PydanticOutputParser
from langchain.prompts import PromptTemplate

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.colors import black, Color

from io import BytesIO

import fitz
from PIL import Image

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Модуль для переноса строки
import textwrap

from langchain_core.prompts import PromptTemplate

llm = LLMClient()
logger = logging.getLogger(__name__)


def extract_fragment_image(text, citation):

    text = text.replace('\n', ' ')
    citation = citation.replace('\n', ' ')

    # Настройки
    FONT_NAME = 'Candara'
    FONT_SIZE = 10
    PAGE_WIDTH = 500
    LEFT_MARGIN = 20 # Устанавливаем отступы
    TOP_MARGIN = 20
    LINE_HEIGHT = 12  # Высота строки
    CHARS_PER_LINE = 80
    MARKER_COLOR = Color(0.7, 1, 0.7, 0.4) # Светло-зелёный с прозрачностью 40%

    # Разбиваем текст на строки
    lines = textwrap.wrap(text, width=CHARS_PER_LINE)

    # Рассчитываем необходимую высоту страницы
    PAGE_HEIGHT = len(lines) * LINE_HEIGHT + TOP_MARGIN + 20 # Запас снизу

    # Создаём PDF
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=(PAGE_WIDTH, PAGE_HEIGHT))

    pdfmetrics.registerFont(TTFont('Candara', 'streamlit-app/Candara.ttf'))
    c.setFont('Candara', 10)

    # Рисуем текст
    y_position = PAGE_HEIGHT - TOP_MARGIN # Стартовая позиция Y

    for line in lines:
        if line.strip(): # Пропускаем пустые строки
            # Всегда рисуем текст чёрным
            c.setFillColor(black)
            # Если есть цитата в текущей строке - рисуем подложку
            if line in citation:
                c.saveState()
                # Рисуем бледно-зелёную положку, как маркер
                text_width = c.stringWidth(line, FONT_NAME, FONT_SIZE)
                c.setFillColor(MARKER_COLOR)
                c.setStrokeColor(MARKER_COLOR)
                # Рисуем прямоуголник
                c.rect(LEFT_MARGIN - 1, y_position - 1, text_width + 2, LINE_HEIGHT - 2, fill = 1, stroke = 0)

                c.restoreState()

            # Рисуем текст поверх подложки
            c.drawString(LEFT_MARGIN, y_position, line)
            y_position -= LINE_HEIGHT

    c.save()

    # Получаем байты
    pdf_bytes = buffer.getvalue()
    buffer.close()

    doc = fitz.open(stream=pdf_bytes, filetype='pdf')
    page = doc[0]

    # Увеличиваем качество
    mat = fitz.Matrix(2.0, 2.0)
    pix = page.get_pixmap(matrix=mat, alpha=False)

    img = Image.frombytes('RGB', [pix.width, pix.height], pix.samples)
    doc.close()

    # Показываем в Streamlit
    st.image(img, use_column_width=True)
    return img

class LegalCitation(BaseModel):
    """Модель для цитаты из документа"""
    document_type: str = Field(description = 'Тип документа')
    text_snippet: str = Field(description = 'Точный фрагмент текста, на который ссылается ответ')
    # page: Optional[str] = Field(None, description = 'Номер страницы строкой, если доступен')
    relevance_reason: str = Field(description = 'Почему этот фрагмент важен')

class LegalAnalysisResponse(BaseModel):
    """Полная структура ответа юридического анализа"""
    # chain_of_thoughts: str = Field(description = 'Внутренние рассуждения модели о том, как анализировать документы')
    citations: List[LegalCitation] = Field(description='Список цитат, подтверждающих ответ') # citations.text_snippet, citations.relevance_reason
    answer: str = Field(description = 'Финальный ответ на русском языке')

parser = PydanticOutputParser(pydantic_object = LegalAnalysisResponse)

TODAY = datetime.today().strftime('%d-%B-%y')


def sanitize_html(text: str) -> str:
    """"Экранируем HTML-символы для предотвращения XSS"""
    if not text:
        return text
    return html.escape(text)

def generate_instruct_chat(query):

    # Помочь Пользователю с загрузкой

    prompt_template = """
    Ты помогаешь Пользователю ответить на вопрос по загруженному комплекту документов.
    Документы, загруженные на анализ, представлены в формате JSON: {documents}
    Ответь на вопрос, используя только информацию из этих документов.

    Вопрос: {query}
    
    Твой ответ должен быть в следующем формате:
    {format_instructions}
        
    Перед формированием text_snippet, фрагментов текста, очисти текст от Markdown разметки и прочих тегов.
    Это должен быть юридический документ.
    
    Твой ответ:
    """

    parser = PydanticOutputParser(pydantic_object=LegalAnalysisResponse)

    try:
        if st.session_state.all_results is None:
            documents = 'А Пользователь не загрузил никаких документов :( Вежливо укажи не это'
        else:

            doc_dicts = []
            for elem in st.session_state.all_results:

                keys_to_keep = ['raw_text']
                new_dict = {k: elem[k] for k in keys_to_keep}
                doc_dicts.append(json.dumps(new_dict, ensure_ascii=False))

            documents = str(doc_dicts)

        prompt = PromptTemplate(
            input_variable=['documents', 'query'],
            template=prompt_template,
            partial_variables={'format_instructions': parser.get_format_instructions()},
        )

        chain = prompt | llm | parser

        from langchain.schema import OutputParserException
        attempt = 0
        max_attempts = 10
        while True:

            try:
                result = chain.invoke({'documents': documents, 'query': query})
                return result

            except OutputParserException as e:
                if attempt >= max_attempts:
                    return None

            attempt += 1
            time.sleep(3)

        return result

    except Exception as e:
        logger.error(f'❌ Ошибка при генерации ответа: {e}')
        return '❌ Ошибка при генерации ответа'


def render_chat_interface():
    """Рендерим интерактивный чат для вопросов по документам"""
    st.divider()
    with st.expander("🤖 Интерактивный чат с LLM", expanded=True):
        # Поле ввода и кнопка
        user_input = st.text_area(
            "Ваш запрос:",
            key='chat_input',
            placeholder="Задайте вопрос по комплекту документов...",
            height=150
        )
        submit_button = st.button("📤 Отправить",)
        # Обработка запроса
        if submit_button and user_input:
            with st.spinner('Просматриваю документы...'):
                # Получение ответа
                response = generate_instruct_chat(user_input)

                # Убираем возможные теги <think>
                # if '</think>' in response:
                #     response = response.split('</think>')[-1].strip()

                for citation in response.citations:
                    st.markdown(citation.document_type.upper())
                    extract_fragment_image(citation.text_snippet, citation.text_snippet)
                    st.markdown(citation.relevance_reason)

                st.markdown(response.answer)
