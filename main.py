"""
Главный модуль приложения Data Discovery Tool.
"""
import sys
import asyncio
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.index.indexer import MetadataStore
from src.ui.cli import CLI


async def load_sample_data(store: MetadataStore):
    """
    Загружает демонстрационные данные для тестирования.
    
    Создаёт CSV-файлы с клиентами и заказами, 
    а также SQLite-таблицу с продуктами.
    """
    from src.connectors.sqlite_connector import SQLiteConnector
    from src.connectors.csv_connector import CSVConnector
    
    print("📊 Загрузка демонстрационных данных...")
    
    data_dir = Path('./data/sample_data')
    data_dir.mkdir(parents=True, exist_ok=True)
    
    import csv
    
    customers_data = [
        ['customer_id', 'first_name', 'last_name', 'email', 'phone', 'created_at'],
        ['1', 'John', 'Doe', 'john@example.com', '555-0101', '2023-01-01'],
        ['2', 'Jane', 'Smith', 'jane@example.com', '555-0102', '2023-01-02'],
        ['3', 'Bob', 'Johnson', 'bob@example.com', '555-0103', '2023-01-03'],
        ['4', 'Alice', 'Williams', 'alice@example.com', '555-0104', '2023-01-04'],
        ['5', 'Charlie', 'Brown', 'charlie@example.com', '555-0105', '2023-01-05']
    ]
    
    with open(data_dir / 'customers.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerows(customers_data)
    print("✅ Создан customers.csv")
    
    orders_data = [
        ['order_id', 'customer_id', 'product', 'quantity', 'price', 'order_date'],
        ['101', '1', 'Laptop', '1', '999.99', '2023-01-10'],
        ['102', '2', 'Mouse', '2', '29.99', '2023-01-11'],
        ['103', '1', 'Monitor', '1', '299.99', '2023-01-12'],
        ['104', '3', 'Keyboard', '1', '79.99', '2023-01-13'],
        ['105', '4', 'Headphones', '3', '49.99', '2023-01-14']
    ]
    
    with open(data_dir / 'orders.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerows(orders_data)
    print("✅ Создан orders.csv")
    
    print("✅ Демонстрационные данные загружены!")
    
    csv_config = {
        'name': 'Sample CSV Data',
        'description': 'Sample customer and order data',
        'data_dir': str(data_dir)
    }
    csv_connector = CSVConnector('csv_source', csv_config)
    await csv_connector.connect()
    csv_metadata = await csv_connector.get_metadata()
    store.index_source(csv_metadata)
    print("✅ CSV источник проиндексирован")
    
    db_path = Path('./data/sample.db')
    
    sqlite_config = {
        'name': 'Sample SQLite DB',
        'description': 'Sample SQLite database with customer data',
        'db_path': str(db_path)
    }
    sqlite_connector = SQLiteConnector('sqlite_source', sqlite_config)
    await sqlite_connector.connect()
    
    conn = sqlite_connector.connection
    
    await conn.execute('''
        CREATE TABLE IF NOT EXISTS products (
            product_id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            category TEXT,
            price REAL,
            stock INTEGER
        )
    ''')
    
    await conn.executemany(
        'INSERT OR IGNORE INTO products (product_id, name, category, price, stock) VALUES (?, ?, ?, ?, ?)',
        [
            (1, 'Laptop Pro', 'Electronics', 1299.99, 10),
            (2, 'Wireless Mouse', 'Electronics', 39.99, 50),
            (3, 'USB-C Hub', 'Accessories', 89.99, 30),
            (4, 'Monitor 27"', 'Electronics', 349.99, 15),
            (5, 'Mechanical Keyboard', 'Electronics', 129.99, 25)
        ]
    )
    await conn.commit()
    print("✅ Создана SQLite таблица products")
    
    sqlite_metadata = await sqlite_connector.get_metadata()
    store.index_source(sqlite_metadata)
    print("✅ SQLite источник проиндексирован")


async def main():
    """Точка входа в приложение."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Data Discovery Tool')
    parser.add_argument('--mode', choices=['cli', 'server'], 
                       default='cli', help='Режим запуска')
    parser.add_argument('--host', default='0.0.0.0', help='Хост сервера')
    parser.add_argument('--port', type=int, default=8000, help='Порт сервера')
    
    args = parser.parse_args()
    
    store = MetadataStore()
    
    if not store.sources:
        await load_sample_data(store)
    
    if args.mode == 'cli':
        cli = CLI(store)
        await cli.run()
    elif args.mode == 'server':
        from src.mcp.server import MCPServer
        server = MCPServer(store)
        print(f"🚀 Запуск MCP сервера на http://{args.host}:{args.port}")
        import uvicorn
        uvicorn.run(server.app, host=args.host, port=args.port)


if __name__ == "__main__":
    asyncio.run(main())