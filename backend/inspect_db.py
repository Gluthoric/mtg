from main import create_app
from database import db
from sqlalchemy import inspect

app = create_app()

with app.app_context():
    inspector = inspect(db.engine)

    for table_name in ['collections', 'kiosk']:
        print(f"\nTable: {table_name}")
        columns = inspector.get_columns(table_name)
        for column in columns:
            print(f"Column: {column['name']}, Type: {column['type']}, Nullable: {column['nullable']}")

        pk = inspector.get_pk_constraint(table_name)
        print(f"Primary Key: {pk['constrained_columns']}")