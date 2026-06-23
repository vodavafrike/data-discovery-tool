"""
Командная строка для Data Discovery Tool.
"""
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt

from ..search.engine import SearchEngine
from ..index.indexer import MetadataStore


class CLI:
    """Интерфейс командной строки."""
    
    def __init__(self, metadata_store: MetadataStore):
        self.store = metadata_store
        self.search_engine = SearchEngine(metadata_store)
        self.console = Console()
    
    async def run(self):
        """Запуск основного цикла CLI."""
        self.console.print(Panel.fit("🔍 Data Discovery Tool", style="bold blue"))
        self.console.print("Введите 'help' для списка команд, 'quit' для выхода\n")
        
        while True:
            command = Prompt.ask("[bold yellow]Команда[/]")
            
            if command == 'quit' or command == 'exit':
                break
            elif command == 'help':
                self._show_help()
            elif command == 'list':
                await self._list_sources()
            elif command.startswith('search '):
                query = command[7:]
                await self._search(query)
            elif command.startswith('schema '):
                parts = command[7:].split()
                if len(parts) == 2:
                    await self._show_schema(parts[0], parts[1])
                else:
                    self.console.print("Использование: schema <источник> <таблица>", style="red")
            elif command.startswith('preview '):
                parts = command[8:].split()
                if len(parts) == 2:
                    await self._show_preview(parts[0], parts[1])
                else:
                    self.console.print("Использование: preview <источник> <таблица>", style="red")
            elif command == 'stats':
                await self._show_stats()
            else:
                self.console.print(f"Неизвестная команда: {command}", style="red")
    
    def _show_help(self):
        """Показать справку."""
        help_text = """
[bold]Доступные команды:[/bold]
  [cyan]list[/cyan]              - Список всех источников данных
  [cyan]search <запрос>[/cyan]   - Поиск по таблицам и колонкам
  [cyan]schema <источник> <таблица>[/cyan] - Схема таблицы
  [cyan]preview <источник> <таблица>[/cyan] - Предпросмотр данных
  [cyan]stats[/cyan]             - Статистика
  [cyan]help[/cyan]              - Справка
  [cyan]quit[/cyan]              - Выход
        """
        self.console.print(Panel(help_text, title="Помощь", border_style="green"))
    
    async def _list_sources(self):
        """Список всех источников."""
        sources = self.store.get_sources()
        if not sources:
            self.console.print("Нет проиндексированных источников.", style="yellow")
            return
        
        table = Table(title="Источники данных")
        table.add_column("ID", style="cyan")
        table.add_column("Название")
        table.add_column("Тип")
        table.add_column("Таблицы")
        table.add_column("Индексирован")
        
        for source in sources:
            table.add_row(
                source['source_id'],
                source['name'],
                source['type'],
                str(source['table_count']),
                source['last_indexed'] or 'Никогда'
            )
        
        self.console.print(table)
    
    async def _search(self, query: str):
        """Поиск по запросу."""
        results = self.search_engine.search(query)
        
        if not results:
            self.console.print(f"Результатов по запросу '{query}' не найдено", style="yellow")
            return
        
        table = Table(title=f"Результаты поиска: '{query}'")
        table.add_column("Источник", style="cyan")
        table.add_column("Таблица")
        table.add_column("Релевантность")
        table.add_column("Колонки")
        table.add_column("Строк")
        
        for result in results[:20]:
            table.add_row(
                result.get('source_name', result['source_id']),
                result['table'],
                f"{result['score']:.2f}",
                ', '.join(result.get('table_columns', [])[:5]),
                str(result.get('row_count', 'N/A'))
            )
        
        self.console.print(table)
        self.console.print(f"Найдено {len(results)} результатов", style="green")
    
    async def _show_schema(self, source_id: str, table_name: str):
        """Показать схему таблицы."""
        schema = self.store.get_table_schema(source_id, table_name)
        if not schema:
            self.console.print(f"Таблица {table_name} не найдена", style="red")
            return
        
        table = Table(title=f"Схема: {source_id}.{table_name}")
        table.add_column("Колонка", style="cyan")
        table.add_column("Тип")
        table.add_column("Null")
        table.add_column("PK")
        table.add_column("Примеры")
        
        for col in schema.columns:
            table.add_row(
                col.name,
                col.data_type,
                "Да" if col.nullable else "Нет",
                "Да" if col.is_primary_key else "",
                ', '.join(str(v) for v in (col.sample_values or [])[:3])
            )
        
        self.console.print(table)
        self.console.print(f"Всего строк: {schema.row_count or 'N/A'}", style="dim")
    
    async def _show_preview(self, source_id: str, table_name: str):
        """Показать предпросмотр."""
        await self._show_schema(source_id, table_name)
    
    async def _show_stats(self):
        """Показать статистику."""
        stats = {
            'источников': len(self.store.sources),
            'таблиц': sum(len(s.tables) for s in self.store.sources.values()),
            'колонок': sum(
                sum(len(t.columns) for t in s.tables) 
                for s in self.store.sources.values()
            )
        }
        
        panel = Panel(
            f"[bold]Статистика[/bold]\n"
            f"Источников: {stats['источников']}\n"
            f"Таблиц: {stats['таблиц']}\n"
            f"Колонок: {stats['колонок']}",
            title="Статистика",
            border_style="blue"
        )
        self.console.print(panel)