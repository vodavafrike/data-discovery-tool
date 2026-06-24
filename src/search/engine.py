"""
Поисковый движок с продвинутым ранжированием.
"""
from typing import List, Dict, Any, Optional

from ..index.indexer import MetadataStore


class SearchEngine:
    """Поисковый движок с оценкой релевантности."""
    
    def __init__(self, metadata_store: MetadataStore):
        self.store = metadata_store
        
    def search(self, query: str, source_id: Optional[str] = None, 
               max_results: int = 50, fuzzy: bool = True) -> List[Dict[str, Any]]:
        """
        Выполняет поиск с учётом релевантности.
        # TODO: добавить пагинацию для больших результатов
        # TODO: добавить сортировку по дате обновления таблиц
        
        Аргументы:
            query: Поисковый запрос
            source_id: ID источника для фильтрации
            max_results: Максимальное количество результатов
            fuzzy: Включить нечёткий поиск
        
        Возвращает:
            Список результатов с оценками релевантности
        """
        query = query.strip()
        if not query:
            return []
        
        base_results = self.store.search(query, source_id)
        
        if not base_results:
            if fuzzy:
                return self._fuzzy_search(query, source_id, max_results)
            return []
        
        for result in base_results:
            unique_matches = len(set([m['term'] for m in result['matches']]))
            result['score'] += unique_matches * 0.5
            
            row_count = result.get('row_count', 0)
            if row_count > 1000:
                result['score'] += 0.2
            elif row_count > 100:
                result['score'] += 0.1
            
            col_count = len(result.get('table_columns', []))
            if col_count > 10:
                result['score'] += 0.1
        
        sorted_results = sorted(base_results, key=lambda x: x['score'], reverse=True)
        
        return sorted_results[:max_results]
    def get_suggestions(self, query: str, limit: int = 5) -> List[str]:
  
        if not query or len(query) < 2:
            return []
    
        query_lower = query.lower()
        suggestions = set()
    
    # Ищем по всем индексированным терминам
        for term in self.store.inverted_index.keys():
            if term.startswith(query_lower):
                suggestions.add(term)
            elif query_lower in term and len(term) - len(query_lower) <= 3:
                suggestions.add(term)
    
    # Ищем по названиям таблиц
        for source in self.store.sources.values():
            for table in source.tables:
                table_name_lower = table.name.lower()
                if table_name_lower.startswith(query_lower):
                    suggestions.add(table_name_lower)
                elif query_lower in table_name_lower:
                    suggestions.add(table_name_lower)
            
            # Добавляем названия колонок
            for column in table.columns:
                col_name_lower = column.name.lower()
                if col_name_lower.startswith(query_lower):
                    suggestions.add(col_name_lower)
                elif query_lower in col_name_lower:
                    suggestions.add(col_name_lower)
    
    # Сортируем по длине
        return sorted(suggestions, key=len)[:limit]
    
    def _fuzzy_search(self, query: str, source_id: Optional[str] = None, 
                     max_results: int = 50) -> List[Dict[str, Any]]:
        """
        Выполняет нечёткий поиск по похожим терминам.
        
        Использует расстояние Левенштейна для нахождения похожих слов.
        """
        query_terms = query.lower().split()
        
        if not query_terms:
            return []
        
        all_terms = list(self.store.inverted_index.keys())
        
        similar_terms = []
        for term in query_terms:
            for idx_term in all_terms:
                if term in idx_term or idx_term in term:
                    similar_terms.append(idx_term)
                elif len(term) > 2 and self._levenshtein(term, idx_term) <= 2:
                    similar_terms.append(idx_term)
        
        similar_terms = list(set(similar_terms))
        
        if not similar_terms:
            return []
        
        fuzzy_query = ' '.join(similar_terms)
        results = self.store.search(fuzzy_query, source_id)
        
        for result in results:
            result['score'] *= 0.7
            result['fuzzy_match'] = True
        
        return results[:max_results]
    
    def _levenshtein(self, s1: str, s2: str) -> int:
        """
        Вычисляет расстояние Левенштейна между двумя строками.
        
        Используется для нечёткого поиска.
        """
        if len(s1) < len(s2):
            return self._levenshtein(s2, s1)
        
        if len(s2) == 0:
            return len(s1)
        
        previous_row = range(len(s2) + 1)
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        
        return previous_row[-1]