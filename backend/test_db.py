from app.db import DATABASE_URL, engine
import sqlalchemy

print(f'Database URL: {DATABASE_URL}')
try:
    with engine.connect() as conn:
        result = conn.execute(sqlalchemy.text('SELECT 1'))
        print('✅ Successfully connected to MySQL!')
except Exception as e:
    print(f'❌ Connection error: {e}')
