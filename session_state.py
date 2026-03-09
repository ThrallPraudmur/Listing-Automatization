import streamlit as st

def init_session_state():
    """Инициализация всех переменных состояния сессии"""
    session_vars = {
        # Результаты проверок
        'absurdity_checks': None,
        'anketa_checks': None,
        'authority_checks': None,
        'bond_emission_restrictions_checks': None,
        'bond_footnote': None,
        'corporate_governance_checks': None,
        'document_changes_checks': None,
        'listing_level_checks': None,
        'pvo_verification_checks': None,

        'theme': 'green',
        'mode': 'analyst', # librarian
        'chat_history': [],
        'folders': [],
        'user_info': None,
        'entities': [],
        'documents': [],
        
        # Обработанные документы
        'all_results': None,
        
        # Выбранные проверки
        'selected_checks': None,
        
        # Статусы сервисов
        'health_shown': False,
        'ocr_msg': None,
        'llm_msg': None,
        'keycloak_msg': None,
        'icbd_msg': None,
        'proxy_msg': None,
    }
    
    for key, default_value in session_vars.items():
        if key not in st.session_state:
            st.session_state[key] = default_value