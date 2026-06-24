"""
Веб-интерфейс для Data Discovery Tool на Streamlit.
"""
from typing import List
import sys
import json
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))

import streamlit as st
#import pandas as pd

from src.index.indexer import MetadataStore
from src.search.engine import SearchEngine

# Настройка страницы
st.set_page_config(
    page_title="Data Discovery Tool",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Стили
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #2C3E50;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #7F8C8D;
        margin-bottom: 2rem;
    }
    .result-card {
        padding: 1rem;
        border-radius: 10px;
        border: 1px solid #E8ECEF;
        margin-bottom: 1rem;
        background: white;
    }
    .result-title {
        font-size: 1.2rem;
        font-weight: 600;
        color: #2C3E50;
    }
    .result-meta {
        font-size: 0.9rem;
        color: #7F8C8D;
    }
    .highlight {
        background: #FEF9E7;
        padding: 0.1rem 0.3rem;
        border-radius: 3px;
        color: #F39C12;
    }
</style>
""", unsafe_allow_html=True)

# Инициализация хранилища
@st.cache_resource
def init_store():
    store = MetadataStore()
    return store

def load_sample_data_if_empty(store):
    import asyncio
    from main import load_sample_data
    
    if not store.sources:
        with st.spinner("📊 Загрузка демонстрационных данных..."):
            asyncio.run(load_sample_data(store))
        st.rerun()

store = init_store()
search_engine = SearchEngine(store)

if not store.sources:
    load_sample_data_if_empty(store)
    st.rerun()

def get_suggestions(query: str) -> List[str]:
    """Получить подсказки для поискового запроса"""
    if not query or len(query) < 2:
        return []
    return search_engine.get_suggestions(query)

# ============================================================
# БОКОВАЯ ПАНЕЛЬ
# ============================================================
with st.sidebar:
    st.markdown("## 🔍 Data Discovery Tool")
    st.markdown("---")
    
    sources = store.get_sources()
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Источники", len(sources))
    with col2:
        total_tables = sum(s['table_count'] for s in sources)
        st.metric("Таблицы", total_tables)
    
    st.markdown("---")
    
    if sources:
        st.markdown("### 📂 Источники")
        for source in sources:
            st.caption(f"• {source['name']} ({source['type']})")
    
    st.markdown("---")
    st.caption("v1.0.0 | MCP Interface")

# ============================================================
# ГЛАВНАЯ ОБЛАСТЬ
# ============================================================
st.markdown('<p class="main-header">🔍 Data Discovery Tool</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">MCP-интерфейс для AI-агентов • Поиск в SQLite и CSV</p>', unsafe_allow_html=True)

col1, col2, col3 = st.columns([3, 1, 1])

with col1:
    query = st.text_input(
        "Поисковый запрос",
        placeholder="Введите ключевое слово (например: customer, product, email...)",
        label_visibility="collapsed"
    )
        # Показываем подсказки
    if query and len(query) >= 2:
        suggestions = get_suggestions(query)
        if suggestions:
            st.caption("💡 Подсказки: " + ", ".join(suggestions[:5]))

with col2:
    search_clicked = st.button("🔍 Найти", use_container_width=True, type="primary")

with col3:
    max_results = st.selectbox("Результатов", [10, 20, 50, 100], index=1, label_visibility="collapsed")

# ============================================================
# ВКЛАДКИ
# ============================================================
tab1, tab2, tab3 = st.tabs(["📋 Результаты", "📊 Схемы таблиц", "ℹ️ О проекте"])

# ============================================================
# ВКЛАДКА 1: РЕЗУЛЬТАТЫ
# ============================================================
with tab1:
    if query or search_clicked:
        if not query:
            st.info("Введите поисковый запрос")
        else:
            with st.spinner(f"Поиск по запросу: '{query}'..."):
                results = search_engine.search(query, max_results=max_results)
            
            if results:
                st.success(f"✅ Найдено {len(results)} результатов")
                
                for result in results:
                    with st.container():
                        st.markdown(f"""
                        <div class="result-card">
                            <div class="result-title">📋 {result['table']}</div>
                            <div class="result-meta">
                                Источник: <b>{result.get('source_name', result['source_id'])}</b> 
                                • Релевантность: <span class="highlight">{result['score']:.2f}</span>
                                • Строк: {result.get('row_count', 'N/A')}
                            </div>
                            <div style="margin-top: 0.5rem;">
                                Колонки: <span style="color: #3498DB;">{', '.join(result.get('table_columns', [])[:8])}</span>
                                {len(result.get('table_columns', [])) > 8 and '...' or ''}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        if st.button(f"📖 Схема", key=f"schema_{result['source_id']}_{result['table']}"):
                            st.session_state['show_schema_source'] = result['source_id']
                            st.session_state['show_schema_table'] = result['table']
                            st.rerun()
            else:
                st.warning(f"❌ Результатов по запросу '{query}' не найдено")
    else:
        st.info("💡 Введите поисковый запрос, чтобы начать")

# ============================================================
# ВКЛАДКА 2: СХЕМЫ ТАБЛИЦ
# ============================================================
with tab2:
    st.markdown("### 📊 Схема таблицы")
    
    sources_list = store.get_sources()
    if sources_list:
        source_options = {s['name']: s['source_id'] for s in sources_list}
        source_names = list(source_options.keys())
        
        col1, col2 = st.columns(2)
        with col1:
            selected_source_name = st.selectbox("Источник", source_names)
            selected_source_id = source_options[selected_source_name]
        
        source = store.sources.get(selected_source_id)
        if source:
            table_names = [t.name for t in source.tables]
            with col2:
                selected_table = st.selectbox("Таблица", table_names)
            
            schema = store.get_table_schema(selected_source_id, selected_table)
            if schema:
                st.markdown(f"#### 📋 `{selected_table}`")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Колонки", len(schema.columns))
                with col2:
                    st.metric("Строки", schema.row_count or "N/A")
                with col3:
                    st.metric("Источник", selected_source_name)
                
                cols_data = []
                for col in schema.columns:
                    cols_data.append({
                        "Колонка": col.name,
                        "Тип": col.data_type,
                        "Nullable": "✅" if col.nullable else "❌",
                        "PK": "✅" if col.is_primary_key else "",
                        "Примеры": ', '.join(str(v) for v in (col.sample_values or [])[:3])
                    })
                
                st.table(cols_data)
            else:
                st.warning("Схема не найдена")
    else:
        st.warning("Нет проиндексированных источников")

# ============================================================
# ВКЛАДКА 3: О ПРОЕКТЕ
# ============================================================
with tab3:
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        ### 🚀 Data Discovery Tool

        **Интеллектуальный инструмент для поиска данных в различных источниках с MCP-интерфейсом для AI-агентов.**

        #### ✨ Возможности

        - 🔗 **Подключение к разным источникам**: SQLite, CSV файлы
        - 🏷️ **Индексация метаданных**: таблицы, колонки, типы данных
        - 🔍 **Умный поиск**: с релевантностью и нечётким поиском
        - 🤖 **MCP-интерфейс**: для интеграции с AI-агентами
        - 💻 **CLI и Web UI**: удобный интерфейс для пользователей

        #### 🏗️ Архитектура""")
