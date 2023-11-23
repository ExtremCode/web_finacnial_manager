from yoyo import read_migrations
from yoyo import get_backend
import psycopg2 as psg


login='postgres'
pswd='rootroot'
backend = get_backend(f'postgres://{login}:{pswd}@localhost/financial')
migrations = read_migrations('web_financial_manager/backend/database/migrations')

def rollback():
    with backend.lock():
        backend.rollback_migrations(backend.to_rollback(migrations))

def apply():
    with backend.lock():
        backend.apply_migrations(backend.to_apply(migrations))

def init_db():
    apply()
    try:
        conn = psg.connect(host="localhost",
                    database="financial",
                    user=login,
                    password=pswd)
        cursor = conn.cursor()
        cursor.execute("""
        insert into income_category(cat_name)
        values ('salary'),
        ('premiums'),
        ('investments'),
        ('another');

        insert into expense_category(cat_name)
        values ('groceries'),
        ('restaurants'),
        ('hobby'),
        ('medicine'),
        ('transport'),
        ('sport'),
        ('rental'),
        ('another');

        insert into credit_category(cat_name)
        values ('consumer credit'),
        ('mortgage'),
        ('car loan');""")
    except:
        print("inserting categories cannot be finished")
        conn.rollback()
    conn.commit()
    cursor.close()
    conn.close()
