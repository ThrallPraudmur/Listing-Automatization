import time
import json
import html
import logging

from datetime import datetime

import streamlit as st
from pydantic import BaseModel, Field
from typing import List, Optional
from langchain.output_parsers import PydanticOutputParser
from langchain.prompts import PromptTemplate

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.colors import black, Color

from io import BytesIO
import base64

import fitz

import sys
from pathlib import Path

# Добавляем путь к shared модулям
sys.path.append(str(Path(__file__).parent.parent))

logger = logging.getLogger(__name__)

import fitz
from PIL import Image

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Модуль для переноса строки
import textwrap

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

system_prompt = f"""
Ты - юридический ассистент, анализирующий документы.
ВАЖНЫЕ ПРАВИЛА:

1. Каждое утверждение в ответе должно подтверждаться фрагментами из документа
2. Если в докумментах нет информации для ответа - так и скажи
3. Цитируй точно текст документа, без искажений

Сегодняшняя дата: {TODAY}
"""


def sanitize_html(text: str) -> str:
    """"Экранируем HTML-символы для предотвращения XSS"""
    if not text:
        return text
    return html.escape(text)


# Убираем возможные теги <think>
def sanitize_model_output(text: str) -> str:
    """Сантизирует выход модели от служебных тегов ризонинга"""
    if '</think>' in text:
        text = text.split('</think>')[-1].strip()
    sanitized_result = sanitize_html(text)
    return sanitized_result


# with st.expander("📚 Использованные документы", expanded=True):
#     cols = st.columns(len(uploaded_files))


keys_to_keep = ['raw_text'] # entities


def generate_absurdity_checks_instruct():

    doc_dicts = []
    for elem in st.session_state.all_results:
        if elem['doc_type'] in ('error',):
            continue
        new_dict = {k: elem[k] for k in keys_to_keep}
        doc_dicts.append(json.dumps(new_dict, ensure_ascii=False))

    prompt_template = system_prompt + """
    Задача: Проверить следующие документы по прилагаемой ниже инструкции:
    
    {documents}
    
    Инструкция:
    Проверь:
        - Совпадает ли серия биржевых облигаций во всех представленных документах
        - Совпадает ли наименование эмитента во всех предоставленных документах
        - В комплекте документов есть разные версии документов, укажи, что изменилось
        
    Твой ответ должен быть в следующем формате:
    {format_instructions}
        
    Перед формированием text_snippet, фрагментов текста, очисти текст от Markdown разметки и прочих тегов.
    Это должен быть юридический документ.
    
    Твой ответ:
    """

    parser = PydanticOutputParser(pydantic_object=LegalAnalysisResponse)
    prompt = PromptTemplate(
        input_variable=['documents'],
        partial_variables = {'format_instructions': parser.get_format_instructions()},
        template=prompt_template,
    )
    chain = prompt | llm | parser

    from langchain.schema import OutputParserException
    attempt = 0
    max_attempts = 10
    while True:

        try:
            result = chain.invoke({
                'documents': str(doc_dicts),
            })
            return result

        except OutputParserException as e:
            if attempt > max_attempts:
                return None

        attempt += 1
        time.sleep(3)


def generate_anketa_checks_instruct():

    doc_dicts = []
    for elem in st.session_state.all_results:
        try:
            if elem['doc_type'] not in ('анкета',):
                continue
        except KeyError as e:
            logger.error('Ошибка при разборе документа')
            continue
        new_dict = {k: elem[k] for k in keys_to_keep} # Формирование словаря из допущенных документов
        doc_dicts.append(json.dumps(new_dict, ensure_ascii=False))

    prompt_template = system_prompt + """
    Задача: Проверить приложенную к документам Анкету по прилагаемой ниже инструкции из правил листинга:
    
    {documents}
    
    Правила листинга:
    1. Если анкета не приложена к рассматриваемым документам, вежливо сообщи об этом пользователю и прекрати дальнейший анализ
    2. Проверить, указал ли эмитент указал уровень листинга в анкете
    3. Выполнить проверки по указанному эмитентом уровню листинга:
        - Номинальная стоимость одной ценной бумаги должна быть меньше 50 000, однако если уровень листинга - третий, то для номинальной одной ценной бумаги ограничений нет.
        - Общий объём выпуска должен быть корректно подсчитан как произведение количества ценных бумаг в выпуске на стоимость одной ценной бумаги.
        - Для первого уровня листинга общий объём выпуска должен быть больше 2 000 000 000, а для второго уровня листинга общий объём выпуска должен превышать 5 000 000.
        - Рейтинг, выставляемых каждым из рейтинговых агенств должен превышать BBB+; 
        Рейтинговая шкала следующая: ААА > AA+ > AA > A+ > A > A- > BBB+ > BBB ...
        - Необходимо отсутствие случаев дефолта
    5. Проведи проверки строго по указанному эмитентом уровню листинга
    
    
    Твой ответ должен быть в следующем формате:
    {format_instructions}
    
    Перед формированием text_snippet, фрагментов текста, очисти текст от Markdown разметки и прочих тегов.
    Это должен быть юридический документ.
    
    Не упоминай о возможных проверках для не указанных в анкете уровней листинга.
    Не упоминай слово инструкция в ответе.
    Не используй Markdown разметку в ответе.
    
    ВАЖНО! Анкета имеет табличный вид, для более точного ответа анализируй документ как таблицу.
    
    Твой ответ:
    """

    parser = PydanticOutputParser(pydantic_object=LegalAnalysisResponse)
    prompt = PromptTemplate(
        input_variable=['documents'],
        partial_variables = {'format_instructions': parser.get_format_instructions()},
        template=prompt_template,
    )
    chain = prompt | llm | parser

    from langchain.schema import OutputParserException
    attempt = 0
    max_attempts = 10
    while True:

        try:
            result = chain.invoke({
                'documents': str(doc_dicts),
            })
            return result

        except OutputParserException as e:
            if attempt >= max_attempts:
                return None

        attempt += 1
        time.sleep(3)

def generate_authority_checks_instruct():

    doc_dicts = []
    for elem in st.session_state.all_results:
        try:
            if elem['doc_type'] in ('error', 'устав'):
                continue
        except KeyError as e:
            logger.error('Ошибка при разборе документа')
            continue
        new_dict = {k: elem[k] for k in keys_to_keep}
        doc_dicts.append(json.dumps(new_dict, ensure_ascii=False))

    prompt_template = system_prompt + """
    Задача: Проверить комплектность и корректность следующих документов в зависимости от должности подписанта по прилагаемой ниже инструкции:
    {documents}
    Инструкция:
    1. Найди Анкету и Заявление. Если какого-то документа нет - укажи на невозможность дальнейшей проверки по нему.
    2. Определи должность подписанта (доверенность, ИП, управляющая организация, единоличное лицо) как в анкете, так и в заявлении.
    3. Проверь наличие документов для этого типа подписанта:
        - Уполномоченный представитель по доверенности: Доверенность и Согласие
        - Индивидуальный предприниматель или ИП: Протокол и Договор передачи полномочий
        - Управляющая организация или УО Эмитента: Решение участника и Договор передачи полномочий
        - Генеральный директор УО Эмитента: Решение участника и Договор передачи полномочий
        - Генеральный директор: Решение участника
    4. Внимательно проверь, что дана полная информация как о подписанте в Заявлении, так и о подписанте в Анкете.
    
    Твой ответ должен быть СТРОГО в следующем JSON формате:
    {format_instructions}
    
    Перед формированием text_snippet, фрагментов текста, очисти текст от Markdown разметки и прочих тегов.
    Это должен быть юридический документ.

    Твой ответ: 
    """

    parser = PydanticOutputParser(pydantic_object=LegalAnalysisResponse)
    prompt = PromptTemplate(
        input_variable=['documents'],
        partial_variables = {'format_instructions': parser.get_format_instructions()},
        template=prompt_template,
    )
    chain = prompt | llm | parser

    from langchain.schema import OutputParserException
    attempt = 0
    max_attempts = 10
    while True:

        try:
            result = chain.invoke({
                'documents': str(doc_dicts),
            })
            return result

        except OutputParserException as e:
            print(e)
            if attempt >= max_attempts:
                return None

        attempt += 1
        time.sleep(3)


def generate_bond_emission_restrictions_checks_instruct():

    doc_dicts = []
    for elem in st.session_state.all_results:
        try:
            if elem['doc_type'] in ('error',):
                continue
        except KeyError as e:
            logger.error('Ошибка при разборе документа')
            continue
        new_dict = {k: elem[k] for k in keys_to_keep}
        doc_dicts.append(json.dumps(new_dict, ensure_ascii=False))

    prompt_template = system_prompt + """
    Задача: Проверить устав по прилагаемой ниже инструкции из правил листинга:
    
    {documents}
    
    Правила листинга:
    1. Найти в приложенных документах устав
    2. Если устав не приложен к рассматриваемым документам, вежливо сообщи об этом пользователю и прекрати дальнейший анализ
    3. Внимательно просмотри приложенный документ, удели особое внимание значениям положениям об эмиссии биржевых облигаций
    4. Вежливо сообщи пользователю о возможных ограничений на эмиссию или выпуск облигаций, если такие имеются
    Под ограничениям на выпуск облигаций понимается полный запрет на эмиссию или частичный набор условий, которые должны быть
    выполнены, чтобы выпустить облигаций
    
    Твой ответ должен быть в следующем формате:
    {format_instructions}
    
    Перед формированием text_snippet, фрагментов текста, очисти текст от Markdown разметки и прочих тегов.
    Это должен быть юридический документ.
    
    Твой ответ:
    """

    parser = PydanticOutputParser(pydantic_object=LegalAnalysisResponse)
    prompt = PromptTemplate(
        input_variable=['documents'],
        partial_variables = {'format_instructions': parser.get_format_instructions()},
        template=prompt_template,
    )
    chain = prompt | llm | parser

    from langchain.schema import OutputParserException
    attempt = 0
    max_attempts = 10
    while True:

        try:
            result = chain.invoke({
                'documents': str(doc_dicts),
            })
            return result

        except OutputParserException as e:
            if attempt >= max_attempts:
                return None

        attempt += 1
        time.sleep(3)


def generate_corporate_governance_checks_instruct():

    doc_dicts = []
    for elem in st.session_state.all_results:
        try:
            if elem['doc_type'] in ('error'):
                continue
        except KeyError as e:
            logger.error('Ошибка при разборе документа')
            continue
        new_dict = {k: elem[k] for k in keys_to_keep}
        doc_dicts.append(json.dumps(new_dict, ensure_ascii=False))


    prompt_template = system_prompt + """
    Задача: 
    Проверить, что указанный в Уставе порядок принятия решений соблюдается в остальных документах:
    
    {documents}
    
    Инструкция:
    1. Если Устав не приложен к рассматриваемым документам, вежливо сообщи об этом пользователю и прекрати дальнейший анализ
    2. Внимательно просмотри приложенные к Уставу документы
    
    Твой ответ должен быть в следующем формате:
    {format_instructions}
    
    Перед формированием text_snippet, фрагментов текста, очисти текст от Markdown разметки и прочих тегов.
    Это должен быть юридический документ.
    
    Твой ответ:
    """

    parser = PydanticOutputParser(pydantic_object=LegalAnalysisResponse)
    prompt = PromptTemplate(
        input_variable=['documents'],
        partial_variables = {'format_instructions': parser.get_format_instructions()},
        template=prompt_template,
    )
    chain = prompt | llm | parser

    from langchain.schema import OutputParserException
    attempt = 0
    max_attempts = 10
    while True:

        try:
            result = chain.invoke({
                'documents': str(doc_dicts),
            })
            return result

        except OutputParserException as e:
            if attempt >= max_attempts:
                return None

        attempt += 1
        time.sleep(3)


def generate_document_changes_checks_instruct():

    doc_dicts = []
    for elem in st.session_state.all_results:
        try:
            if elem['doc_type'] in ('error',):
                continue
        except KeyError as e:
            logger.error('Ошибка при разборе документа')
            continue
        new_dict = {k: elem[k] for k in keys_to_keep}
        doc_dicts.append(json.dumps(new_dict, ensure_ascii=False))


    prompt_template = """
    Ты - юрист, анализирующий предоставляемые на анализ документы.
    Задача: Проверить следующие документы по прилагаемой ниже инструкции:
    
    {documents}
    
    Инструкция:
    1. Внимательно просмотри приложенные документы на предмет наличия разных версий одного и того же документа
    2. Если такие документы были найдены - сообщи об этом пользователю и укажи ему на зарегестрированные изменения

    Твой ответ: 
    """

    prompt = PromptTemplate(
        input_variable=['documents'],
        template=prompt_template
    )

    chain = prompt | llm
    result = chain.invoke({
        'documents': str(doc_dicts),
    })

    return sanitize_model_output(result)


def generate_listing_level_checks_instruct():

    doc_dicts = []
    for elem in st.session_state.all_results:
        try:
            if elem['doc_type'] in ('error',):
                continue
        except KeyError as e:
            logger.error('Ошибка при разборе документа')
            continue
        new_dict = {k: elem[k] for k in keys_to_keep}
        doc_dicts.append(json.dumps(new_dict, ensure_ascii=False))

    prompt_template = system_prompt + """
    Твоя задача: 
    Проверить уровень листинга в заявлении или анкете по прилагаемой ниже инструкции:
    Наличие в комплекте хотя бы одного из этих документов позволяет выполнить задачу.
     
    {documents}
    
    Правила листинга:
    1. Найди значение уровня листинга, указываемое эмитентом в анкете или заявлении.
    2. Выполни необходимые проверки только для указанного пользователем уровня листинга 
    3. Проверь:
        - Для первого уровня листинга общий объём выпуска должен превышать 2 000 000 000, 
        а для второго уровня листинга общий объём выпуска должен превышать 5 000 000
        - Для первого уровня листинга существования эмитента должен превышать 3 года
        - Для первого уровня листинга необходимо наличие Совета директоров
        - Для второго уровня листинга срок существования эмитента должен превышать 1 год
        - Для второго уровня листинга необходимо наличие представителя владельца облигаций (ПВО), уведомление о котором должно быть приложено к документам
    5. Проведи проверки только для указанного эмитентом уровня листинга.
    
    Важно! 
    Не упоминай пользователю о возможных проверках для не указанных в документах уровней листинга
    
    Твой ответ должен быть в следующем формате:
    {format_instructions}
    
    Перед формированием text_snippet, фрагментов текста, очисти текст от Markdown разметки и прочих тегов.
    Это должен быть юридический документ.
    
    Твой ответ:
    """

    parser = PydanticOutputParser(pydantic_object=LegalAnalysisResponse)
    prompt = PromptTemplate(
        input_variable=['documents'],
        partial_variables = {'format_instructions': parser.get_format_instructions()},
        template=prompt_template,
    )
    chain = prompt | llm | parser

    from langchain.schema import OutputParserException
    attempt = 0
    max_attempts = 10
    while True:

        try:
            result = chain.invoke({
                'documents': str(doc_dicts),
            })
            return result

        except OutputParserException as e:
            if attempt >= max_attempts:
                return None

        attempt += 1
        time.sleep(3)


def render_absurdity_checks_interface():
    with st.expander("🔔 Поиск возможных противоречий", expanded=False):
        if st.session_state.absurdity_checks is None:
            with st.spinner("Просматриваю документы..."):
                result = generate_absurdity_checks_instruct()
                st.session_state.absurdity_checks = result

                for citation in st.session_state.absurdity_checks.citations:
                    st.markdown(citation.document_type.upper())
                    extract_fragment_image(citation.text_snippet, citation.text_snippet)
                    st.markdown(citation.relevance_reason)

                st.markdown(st.session_state.absurdity_checks.answer)

def render_anketa_checks_interface():
    # import time
    with st.expander("🧙 Проверка анкеты", expanded=False):
        if st.session_state.anketa_checks is None:
            with st.spinner("Просматриваю документы..."):
                result = generate_anketa_checks_instruct()
                st.session_state.anketa_checks = result

                for citation in st.session_state.anketa_checks.citations:

                    st.markdown(citation.document_type.upper())
                    extract_fragment_image(citation.text_snippet, citation.text_snippet)
                    # st.markdown(citation.text_snippet)
                    st.markdown(citation.relevance_reason)
                    # time.sleep(2)

                # st.markdown(st.session_state.anketa_checks.chain_of_thoughts)
                st.markdown(st.session_state.anketa_checks.answer)

    # print(result.citations.text_snippet)
    # print(result.citations.relevance_reason)
    # print(result.answer)

def render_authority_checks_interface():
    with st.expander('🕵️ Проверка полномочий подписанта', expanded=False):
        if st.session_state.authority_checks is None:
            with st.spinner('Просматриваю документы...'):
                result = generate_authority_checks_instruct()
                st.session_state.authority_checks = result

                for citation in st.session_state.authority_checks.citations:
                    st.markdown(citation.document_type.upper())
                    extract_fragment_image(citation.text_snippet, citation.text_snippet)
                    st.markdown(citation.relevance_reason)

                st.markdown(st.session_state.authority_checks.answer)

def render_bond_emission_restirctions_checks_interface():
    with st.expander("🛡️ Проверка ограничений на эмиссию", expanded=False):
        if st.session_state.bond_emission_restrictions_checks is None:
            with st.spinner("Просматриваю документы..."):
                result = generate_bond_emission_restrictions_checks_instruct()
                st.session_state.bond_emission_restrictions_checks = result

                for citation in st.session_state.bond_emission_restrictions_checks.citations:
                    st.markdown(citation.document_type.upper())
                    extract_fragment_image(citation.text_snippet, citation.text_snippet)
                    st.markdown(citation.relevance_reason)

                st.markdown(st.session_state.bond_emission_restrictions_checks.answer)

def render_corporate_governance_checks_interface():
    with st.expander("⚖️ Проверка корпоративных процедур", expanded=False):
        if st.session_state.corporate_governance_checks is None:
            with st.spinner("Просматриваю документы..."):
                result = generate_corporate_governance_checks_instruct()
                st.session_state.corporate_governance_checks = result

                for citation in st.session_state.corporate_governance_checks.citations:
                    st.markdown(citation.document_type.upper())
                    extract_fragment_image(citation.text_snippet, citation.text_snippet)
                    st.markdown(citation.relevance_reason)

                st.markdown(st.session_state.corporate_governance_checks.answer)

def render_document_changes_checks_interface():
    with st.expander("🧩 Поиск наследующих документов", expanded=False):
        if st.session_state.document_changes_checks is None:
            with st.spinner("Просматриваю документы..."):
                result = generate_document_changes_checks_instruct()
                st.session_state.document_changes_checks = result
        st.markdown(st.session_state.document_changes_checks)

def render_listing_level_checks_interface():
    with st.expander("🔮 Проверка уровня листинга", expanded=False):
        if st.session_state.listing_level_checks is None:
            with st.spinner("Просматриваю документы..."):
                result = generate_listing_level_checks_instruct()
                st.session_state.listing_level_checks = result

                for citation in st.session_state.listing_level_checks.citations:
                    st.markdown(citation.document_type.upper())
                    extract_fragment_image(citation.text_snippet, citation.text_snippet)
                    st.markdown(citation.relevance_reason)

                st.markdown(st.session_state.listing_level_checks.answer)

def render_pvo_verification_checks_interface():
    with st.expander("🤴 Проверка представителя владельца облигаций", expanded=False):
        if st.session_state.pvo_verification_checks is None:
            with st.spinner("Просматриваю документы..."):
                result = generate_listing_level_checks_instruct()
                st.session_state.pvo_verification_checks = result
        st.markdown(st.session_state.pvo_verification_checks)


CHECKS = {
    'check_1': {
        'title': '🔔 Поиск возможный противоречий',
        'function': render_absurdity_checks_interface,
        'description': 'Хочу найти возможные несовпадения информации',
    },
    'check_2': {
        'title': '🧙 Проверка анкеты',
        'function': render_anketa_checks_interface,
        'description': 'Хочу проверить анкету',
    },
    'check_3': {
        'title': '🔮 Проверка уровня листинга',
        'function': render_listing_level_checks_interface,
        'description': 'Хочу проверить корректность указания уровня листинга',
    },
    'check_4': {
        'title': '🛡️ Поиск ограничений на эмиссию',
        'function': render_bond_emission_restirctions_checks_interface,
        'description': 'Хочу найти возможные ограничения в уставе',
    },
    'check_7': {
        'title': '⚖️ Проверка корпоративных процедур',
        'function': render_corporate_governance_checks_interface,
        'description': 'Хочу проверить в принятых решениях прописанные в уставе нормы',
    },
    'check_9': {
        'title': '🕵️ Проверка полномочий подписанта',
        'function': render_authority_checks_interface,
        'description': 'Хочу проверить полномочия подписанта анкеты и заявления',
    },}

def show_check_selector():

    st.divider()
    selected = st.multiselect(
        '🔎 Выберите проверки для вывода на экран',
        options = list(CHECKS.keys()),
        format_func = lambda x: f"{CHECKS[x]['title']} - {CHECKS[x]['description']}",
        default = [
            'check_2',
            'check_3',
            'check_4',
            'check_7',
            'check_9',
            'check_1'
        ],
    )

    return selected