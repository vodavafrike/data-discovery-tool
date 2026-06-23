"""
Сервис индексации и хранения метаданных.
"""
import pickle
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

from ..connectors.base import SourceMetadata, TableMetadata


class MetadataStore:
    """Хранилище и индексация метаданных из источников данных."""
    
    def __init__(self, index_dir: str = './.search_index'):
        self.index_dir = Path(index_dir)
        self.index_dir.mkdir(parents=True, exist_ok=True)
        self.sources = {}
        self.inverted_index = {}
        self.load_index()
    
    def load_index(self):
        """Загружает индекс с диска"""
        index_file = self.index_dir / 'metadata.pkl'
        if index_file.exists():
            try:
                with open(index_file, 'rb') as f:
                    data = pickle.load(f)
                    self.sources = data.get('sources', {})
                    self.inverted_index = data.get('inverted_index', {})
            except Exception as e:
                print(f"Ошибка загрузки индекса: {e}")
    
    def save_index(self):
        """Сохраняет индекс на диск."""
        index_file = self.index_dir / 'metadata.pkl'
        try:
            with open(index_file, 'wb') as f:
                pickle.dump({
                    'sources': self.sources,
                    'inverted_index': self.inverted_index
                }, f)
        except Exception as e:
            print(f"Ошибка сохранения индекса: {e}")
    
    def index_source(self, source_metadata: SourceMetadata):
        """Индексирует метаданные из источника данных"""
        source_id = source_metadata.source_id
        self.sources[source_id] = source_metadata
        
        for table in source_metadata.tables:
            self._add_to_index(source_id, table.name, 'table', table.name)
            
            for column in table.columns:
                self._add_to_index(source_id, column.name, 'column', table.name)
                
                if column.data_type:
                    self._add_to_index(source_id, column.data_type, 'type', table.name)
        
        self.save_index()
    
    def _add_to_index(self, source_id: str, term: str, term_type: str, table_name: str):
        """Добавляет терм в инвертированный индекс"""
        term = term.lower().strip()
        if not term:
            return
        
        if term not in self.inverted_index:
            self.inverted_index[term] = []
        
        entry = {
            'source_id': source_id,
            'table': table_name,
            'type': term_type
        }
        
        if entry not in self.inverted_index[term]:
            self.inverted_index[term].append(entry)
    
    def search(self, query: str, source_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Выполняет поиск по индексу."""
        query_terms = query.lower().strip().split()
        results = {}
        
        for term in query_terms:
            if term in self.inverted_index:
                for entry in self.inverted_index[term]:
                    if source_id and entry['source_id'] != source_id:
                        continue
                    
                    key = f"{entry['source_id']}:{entry['table']}"
                    if key not in results:
                        results[key] = {
                            'source_id': entry['source_id'],
                            'table': entry['table'],
                            'score': 0,
                            'matches': []
                        }
                    
                    results[key]['score'] += 1
                    results[key]['matches'].append({
                        'term': term,
                        'type': entry['type']
                    })
        
        sorted_results = sorted(results.values(), key=lambda x: x['score'], reverse=True)
        
        enriched = []
        for result in sorted_results:
            source = self.sources.get(result['source_id'])
            if source:
                table_meta = None
                for table in source.tables:
                    if table.name == result['table']:
                        table_meta = table
                        break
                
                if table_meta:
                    enriched.append({
                        **result,
                        'source_name': source.name,
                        'source_type': source.source_type,
                        'table_columns': [c.name for c in table_meta.columns],
                        'row_count': table_meta.row_count
                    })
        
        return enriched
    
    def get_sources(self) -> List[Dict[str, Any]]:
        """Возвращает список всех проиндексированных источников."""
        return [
            {
                'source_id': sid,
                'name': meta.name,
                'type': meta.source_type,
                'table_count': len(meta.tables),
                'last_indexed': meta.last_indexed.isoformat() if meta.last_indexed else None
            }
            for sid, meta in self.sources.items()
        ]
    
    def get_table_schema(self, source_id: str, table_name: str) -> Optional[TableMetadata]:
        """Возвращает схему указанной таблицы."""
        source = self.sources.get(source_id)
        if not source:
            return None
        
        for table in source.tables:
            if table.name == table_name:
                return table
        
        return None