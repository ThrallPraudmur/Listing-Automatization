import os
import requests
import streamlit as st

from design import setup_style, display_header, init_sidebar, render_librarian_mode, render_analyst_mode
from config import Config
from session_state import init_session_state

import sys


def main():

    st.set_option('client.showErrorDetails', False)

    setup_style()

    # Инициализация состояния сессии
    init_session_state()
    init_sidebar()

    if st.session_state.mode == 'analyst':
        render_analyst_mode()
    else:
        render_librarian_mode()

    # Отображение интерфейса
    render_main_interface()

def render_main_interface():
    """Основной интерфейс приложения"""
    from components.checks.checks_views import CHECKS, show_check_selector
    from components.interface.chat_interface import render_chat_interface
    from document_processor import DocumentProcessor, render_documents_views

    import sys
    from pathlib import Path

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
    main()
