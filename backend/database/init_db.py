from yoyo import read_migrations
from yoyo import get_backend
import psycopg2 as psg
from psycopg2.extras import DictCursor
from database.settings import PostgresSettings


backend = get_backend(PostgresSettings().url)
migrations = read_migrations('./backend/database/migrations')

def rollback():
    with backend.lock():
        backend.rollback_migrations(backend.to_rollback(migrations))

def apply():
    with backend.lock():
        backend.apply_migrations(backend.to_apply(migrations))

def init_db() -> tuple:
    apply()
    conn = psg.connect(PostgresSettings().url)
    cursor = conn.cursor(cursor_factory=DictCursor)
    try:
        cursor.execute("""
        insert into income_category(cat_name)
        values ('salary'),
        ('premiums'),
        ('investments'),
        ('another');""")
    except Exception as e:
        print("error in init_db(): ", e)
        conn.rollback()

    try:
        cursor.execute("""insert into expense_category(cat_name)
        values ('groceries'),
        ('restaurants'),
        ('hobby'),
        ('medicine'),
        ('transport'),
        ('sport'),
        ('rental'),
        ('another');""")
    except Exception as e:
        print("error in init_db(): ", e)
        conn.rollback()
    
    try:
        cursor.execute("""insert into credit_category(cat_name)
        values ('consumer credit'),
        ('mortgage'),
        ('car loan');""")
    except Exception as e:
        print("error in init_db(): ", e)
        conn.rollback()
    conn.commit()
    return conn, cursor
