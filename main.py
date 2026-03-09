import os
import requests
import streamlit as st

from design import display_logo
from design_2 import setup_style, display_header, init_sidebar, render_librarian_mode, render_analyst_mode
from config import Config
from session_state import init_session_state

import sys
from pathlib import Path

# Добавляем путь к shared модулям
sys.path.append(str(Path(__file__).parent.parent))

def app():

    st.set_option('client.showErrorDetails', False)

    setup_style()

    # Инициализация состояния сессии
    init_session_state()

    # Проверка авторизации
    # query_params = st.experimental_get_query_params()

    # if 'code' not in query_params:
    #     # Формируем URL для авторизации
    #     auth_url = (
    #         f'{Config.KEYCLOAK_AUTH_URL}/realms/{Config.KEYCLOAK_REALM}/'
    #         f'protocol/openid-connect/auth?client_id={Config.KEYCLOAK_CLIENT_ID}&'
    #         f'redirect_uri={Config.KEYCLOAK_REDIRECT_URI}&response_type=code&scope=openid'
    #     )
    #
    #     # Автоматический редирект
    #     st.markdown(f"""<meta http-equiv="refresh" content="0; url='{auth_url}'" />""", unsafe_allow_html=True)
    # else:
    #
    #     setup_style()
        # st.success("✅ Успешная аутентификация!")

    # display_logo()
    # display_header()
    init_sidebar()

    if st.session_state.mode == 'analyst':
        render_analyst_mode()
    else:
        render_librarian_mode()

    # Отображение интерфейса
    # render_main_interface()

def render_main_interface():
    """Основной интерфейс приложения"""
    from components.checks.checks_views import CHECKS, show_check_selector
    from components.interface.chat_interface import render_chat_interface
    from document_processor import DocumentProcessor, render_documents_views

    import sys
    from pathlib import Path

    # Добавляем путь к shared модулям
    sys.path.append(str(Path(__file__).parent.parent))

    # Скачивание Word инструкции
    with open('streamlit-app/Инструкция_listingai.docx', 'rb') as file:
        st.download_button(
            label='📜 Скачать инструкцию по работе с приложением',
            data=file.read(),
            file_name='instruction.docx',
            mime='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        )

    # Выбор проверок
    selected_checks = show_check_selector()
    st.session_state.selected_checks = selected_checks

    st.divider()

    # Инициализация процессора документов
    processor = DocumentProcessor()

    # Обработка загруженных файлов
    if st.session_state.all_results is None:
        processor.process_uploaded_files()

    # Отображение результатов
    elif st.session_state.all_results:
        render_documents_views()

        # Выполнение выбранных проверок
        for check_id in st.session_state.selected_checks:
            check = CHECKS[check_id]
            check['function']()

if __name__ == "__main__":
    app()