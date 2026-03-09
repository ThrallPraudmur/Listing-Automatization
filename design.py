import html
import streamlit as st

# ─────────────────────────────────────────────
# CSS СТИЛИ
# ─────────────────────────────────────────────

def setup_style():
    """Применяем CSS в зависимости от текущей темы."""
    t = get_theme()
    font_css = _build_font_face_css()

    st.markdown(f"""
    <style>
        {font_css}
        /* Фон - только на контейнерах */
        html, body, .stApp,
        [data-testid="stAppViewContainer"] {{
            background-color: {t['bg']} !important;
        }}
        
        /* Шрифт - на всех элементах где Streamlit рисует текст */
        html, body, .stApp, 
        [data-testid="stAppViewContainer"],
        [data-testid="stMarkdownContainer"],
        [data-testid="stAppViewContainer"] p,
        [data-testid="stAppViewContainer"] div,
        [data-testid="stAppViewContainer"] span,
        [data-testid="stVerticalBlock"],
        [data-testid="stSidebar"],
        .main, .main .block-container,
        .stTextInput input,
        .stSelectBox select,
        label, p, span
        {{
            font-family: 'Geologica', -apple-system, 'Segoe UI', sans-serif !important;
        }}

        /* Основная область с отступом под фиксированную шапку */
        .main .block-container {{
            max-width: 860px;
            margin: 0 auto !important;
            padding-top: 88px !important;
            background: transparent !important;
        }}

        /* Сайдбар */
        [data-testid="stSidebar"] {{
            background: linear-gradient(160deg, {t['sidebar_bg']}, {t['bg']}) !important;
            border-right: 1px solid {t['border']} !important;
        }}
        [data-testid="stSidebar"] > div:first-child {{ padding: 1rem 0.75rem !important; }}

        /* Карточки документов */
        .doc-item {{
            background: {t['card_bg']};
            border-radius: 9px;
            padding: 8px 12px;
            margin: 5px 0;
            border: 1px solid {t['border']};
            box-shadow: 0 2px 5px {t['shadow']};
            font-size: 0.83rem;
            color: {t['text']};
            transition: transform 0.14s;
        }}
        .doc-item:hover {{ transform: translateX(3px); }}

        /* Заголовки сайдбара */
        .sidebar-title {{
            background: {t['button_bg']};
            color: white;
            border-radius: 9px;
            padding: 6px 10px;
            text-align: center;
            font-weight: 700;
            font-size: 0.78rem;
            letter-spacing: 1.1px;
            text-transform: uppercase;
            margin-bottom: 9px;
            box-shadow: 0 2px 7px {t['shadow']};
        }}

        /* Кнопки */
        .stButton > button {{
            background: {t['button_bg']} !important;
            color: white !important;
            border: none !important;
            border-radius: 9px !important;
            font-weight: 600 !important;
            transition: opacity 0.18s, transform 0.1s !important;
        }}
        .stButton > button:hover {{
            opacity: 0.84 !important;
            transform: translateY(-1px) !important;
        }}

        /* File uploader */
        [data-testid="stFileUploader"] {{
            background: {t['card_bg']};
            border: 2px dashed {t['border']};
            border-radius: 13px;
            padding: 10px;
        }}

        /* Скроллбар */
        ::-webkit-scrollbar {{ width: 7px; }}
        ::-webkit-scrollbar-thumb {{ background: {t['scrollbar']}; border-radius: 7px; }}
        ::-webkit-scrollbar-track {{ background: {t['bg']}; }}

        /* === ФИКСИРОВАННАЯ ШАПКА — логотип не скроллится === */
        .header-bar {{
            position: fixed;
            top: 0; left: 0; right: 0;
            height: 60px;
            background: {t['card_bg']};
            border-bottom: 1px solid {t['border']};
            display: flex;
            align-items: center;
            padding: 0 22px;
            z-index: 1000;
            box-shadow: 0 2px 10px {t['shadow']};
            gap: 13px;
        }}
        .header-bar img {{ height: 38px; width: auto; }}
        .app-title {{ font-size: 0.97rem; font-weight: 700; color: {t['accent']}; }}
        .header-spacer {{ margin-left: auto; }}
        .header-user {{ font-size: 0.79rem; color: {t['text']}; opacity: 0.65; }}
        .mode-badge {{
            display: inline-block;
            padding: 3px 9px;
            border-radius: 18px;
            font-size: 0.72rem;
            font-weight: 700;
            letter-spacing: 0.5px;
            text-transform: uppercase;
        }}
        .badge-analyst  {{ background:{t['accent2']}33; color:{t['accent']}; border:1px solid {t['accent2']}; }}
        .badge-librarian {{ background:#4fc3f733; color:#01579b; border:1px solid #4fc3f7; }}

        /* Чат-пузыри */
        .chat-wrap {{ display:flex; flex-direction:column; gap:9px; padding:10px 0; }}
        .chat-msg {{
            max-width: 78%;
            padding: 9px 14px;
            border-radius: 13px;
            font-size: 0.89rem;
            line-height: 1.55;
            box-shadow: 0 1px 4px {t['shadow']};
            animation: fadeUp 0.2s ease;
        }}
        .chat-msg.user {{
            align-self: flex-end;
            background: {t['chat_user']};
            color: {t['text']};
            border-bottom-right-radius: 3px;
        }}
        .chat-msg.bot {{
            align-self: flex-start;
            background: {t['chat_bot']};
            border: 1px solid {t['border']};
            color: #1a1a1a;
            border-bottom-left-radius: 3px;
        }}
        .chat-role {{
            font-size: 0.68rem;
            font-weight: 700;
            margin-bottom: 4px;
            opacity: 0.5;
            letter-spacing: 0.4px;
            text-transform: uppercase;
        }}
        @keyframes fadeUp {{
            from {{ opacity:0; transform:translateY(5px); }}
            to   {{ opacity:1; transform:translateY(0); }}
        }}

        /* Чипы сущностей и подсказки */
        .entity-chip {{
            display: inline-block;
            padding: 3px 9px;
            background: {t['card_bg']};
            border: 1px solid {t['border']};
            border-radius: 18px;
            font-size: 0.77rem;
            color: {t['text']};
            margin: 2px;
        }}
        .suggestion-pill {{
            display: inline-block;
            background: {t['card_bg']};
            border: 1px solid {t['border']};
            border-radius: 18px;
            padding: 5px 12px;
            font-size: 0.8rem;
            color: {t['text']};
            margin: 2px 3px;
        }}

        /* Убираем лишние элементы Streamlit */
        header[data-testid="stHeader"], #MainMenu, footer, .stDeployButton {{
            display: none !important;
        }}
        [data-testid="stExpander"] {{ border:1px solid {t['border']}; border-radius:11px; overflow:hidden; }}
    </style>
    """, unsafe_allow_html=True)
    
# ─────────────────────────────────────────────
# ПАЛИТРЫ ТЕМ
# ─────────────────────────────────────────────

THEMES = {
    "green": {
        "label":      "🌿 Зелёная",
        "bg":         "#e8f5e9",
        "sidebar_bg": "#c8e6c9",
        "accent":     "#2e7d32",
        "accent2":    "#66bb6a",
        "text":       "#1b5e20",
        "card_bg":    "#ffffff",
        "border":     "#a5d6a7",
        "button_bg":  "#2e7d32",
        "scrollbar":  "#66bb6a",
        "chat_user":  "#c8e6c9",
        "chat_bot":   "#ffffff",
        "shadow":     "rgba(46,125,50,0.12)",
    },
    "blue": {
        "label":      "🌊 Сине-голубая",
        "bg":         "#e3f2fd",
        "sidebar_bg": "#bbdefb",
        "accent":     "#1565c0",
        "accent2":    "#42a5f5",
        "text":       "#0d47a1",
        "card_bg":    "#ffffff",
        "border":     "#90caf9",
        "button_bg":  "#1565c0",
        "scrollbar":  "#42a5f5",
        "chat_user":  "#bbdefb",
        "chat_bot":   "#ffffff",
        "shadow":     "rgba(21,101,192,0.12)",
    },
    "arctic": {
        "label":      "🐧 Арктика (Библиотекарь)",
        "bg":         "#ecf6fb",
        "sidebar_bg": "#d0ebf5",
        "accent":     "#01579b",
        "accent2":    "#4fc3f7",
        "text":       "#01579b",
        "card_bg":    "#f0f9ff",
        "border":     "#81d4fa",
        "button_bg":  "#0277bd",
        "scrollbar":  "#4fc3f7",
        "chat_user":  "#b3e5fc",
        "chat_bot":   "#e1f5fe",
        "shadow":     "rgba(1,87,155,0.10)",
    },
}

# ─────────────────────────────────────────────
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ─────────────────────────────────────────────

def sanitize_html(text: str) -> str:
    """Экранируем HTML-символы для предотвращения XSS."""
    if not text:
        return text
    return html.escape(text)


def _image_to_base64(image_path: str) -> str:
    """Конвертируем изображение в base64-строку."""
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode()


def _font_to_base64(font_path: str) -> str:
    """Читаем шрифт и кодироуемдля встраивания его в CSS"""
    with open(font_path, 'rb') as f:
        return base64.b64encode(f.read()).decode()

def _build_font_face_css() -> str:
    """
    Формируем @font-face блоки из локальных файлов.
    Если файлы не найдены - возвращаем пустую строку (упадём на системные шрифты)
    """
    css = ''
    font_map = [
        ('streamlit-app/fonts/Geologica-Light.woff2', 'Geologica', 300),
        ('streamlit-app/fonts/Geologica-Regular.woff2', 'Geologica', 400),
        ('streamlit-app/fonts/Geologica-SemiBold.woff2', 'Geologica', 600),
        ('streamlit-app/fonts/Geologica-Bold.woff2', 'Geologica', 700),
        ('streamlit-app/fonts/JetBrainsMono-Regular.woff2', 'JetBrains Mono', 400),
        ('streamlit-app/fonts/JetBrainsMono-Medium.woff2', 'JetBrains Mono', 500),
    ]
    for path, family, weight in font_map:
        b64 = _font_to_base64(path)
        css += f"""
        @font-face {{
            font-family: '{family}';
            font-weight: '{weight}';
            src: url('data:font/woff2;base64,{b64}') format('woff2');
        }}
        """
    return css


def get_theme() -> dict:
    """Возвращает текущую тему из session_state."""
    key = st.session_state.get("theme", "green")
    return THEMES.get(key, THEMES["green"])
    
# ─────────────────────────────────────────────
# ПИНГВИН SVG-МАСКОТ
# ─────────────────────────────────────────────

PENGUIN_SVG = (
    '<svg width="72" height="72" viewBox="0 0 80 80" xmlns="http://www.w3.org/2000/svg">'
    '<ellipse cx="40" cy="48" rx="22" ry="26" fill="#1a1a2e"/>'
    '<ellipse cx="40" cy="52" rx="13" ry="17" fill="#ecf6fb"/>'
    '<circle cx="40" cy="24" r="16" fill="#1a1a2e"/>'
    '<circle cx="34" cy="22" r="4" fill="white"/>'
    '<circle cx="46" cy="22" r="4" fill="white"/>'
    '<circle cx="35" cy="23" r="2" fill="#1a1a2e"/>'
    '<circle cx="47" cy="23" r="2" fill="#1a1a2e"/>'
    '<ellipse cx="40" cy="30" rx="4" ry="2.5" fill="#f4a261"/>'
    '<ellipse cx="30" cy="73" rx="8" ry="4" fill="#f4a261" transform="rotate(-15,30,73)"/>'
    '<ellipse cx="50" cy="73" rx="8" ry="4" fill="#f4a261" transform="rotate(15,50,73)"/>'
    '<ellipse cx="16" cy="52" rx="7" ry="14" fill="#1a1a2e" transform="rotate(10,16,52)"/>'
    '<ellipse cx="64" cy="52" rx="7" ry="14" fill="#1a1a2e" transform="rotate(-10,64,52)"/>'
    '<rect x="24" y="35" width="32" height="6" rx="3" fill="#4fc3f7"/>'
    '</svg>'
)