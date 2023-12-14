import psycopg2 as psg
from database.settings import PostgresSettings


def tests():
    conn = psg.connect(PostgresSettings().url)
    cursor = conn.cursor()

    # test data
    try:
        cursor.execute("""
        insert into person(login, password, expense_lim, credit_lim)
        values ('admin', 'scrypt:32768:8:1$gXFGNU30qa3gXRYd$a66a18a0929e26288a3732a7919bf62a65cda191b0c6b89a47bc7d9cdb817c0778a460dbd7604c1b88cb007d877699cc3dc845df17e585badcea5427b1942e24',\
                    300, 1000),
        ('guest', 'scrypt:32768:8:1$JU0xTEJxVikuRBJo$0322f66bbc4aba626f883e076df9c8c27449f348dc8f53f225d25ea2036517d4e8d469b48ee1e30a3521dca321f800b4d9339bfb384860ce2e3e55600f1a71e3',\
                    100, 300);

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
        ('car loan');

        insert into income(amount, rec_date, cat_id, person_id)
        values (100, '2023-11-11', 1, 1),
        (234, '2022-10-20', 1, 2);

        insert into expense(amount, rec_date, cat_id, person_id)
        values (990, '2023-11-11', 2, 1),
        (100, '2022-10-20', 1, 2);

        insert into credit(amount, cat_id, person_id)
        values (990, 2, 1),
        (100, 1, 2);

        insert into account(acc_name, amount, person_id)
        values ('first', 99900, 1),
        ('second', 2000, 1),
        ('their', 500, 2);""")
    except:
        conn.rollback()

    # unique login in person
    try:
        cursor.execute("""
         insert into person(login, password)
         values('admin', '12345')""")
    except psg.errors.UniqueViolation:
        pass
    except Exception as e:
        print(e)
    finally:
        conn.rollback()
    
    try:
        cursor.execute("""
         insert into person(login, password)
         values('guest', '12345')""")
    except psg.errors.UniqueViolation:
        pass
    except Exception as e:
        print(e)
    finally:
        conn.rollback()
    
    # unique name category in income_category
    try:
        cursor.execute("""
         insert into income_category(cat_name)
         values('salary')""")
    except psg.errors.UniqueViolation:
        pass
    except Exception as e:
        print(e)
    finally:
        conn.rollback()
    
    # unique name category in expense_category
    try:
        cursor.execute("""
         insert into expense_category(cat_name)
         values('hobby')""")
    except psg.errors.UniqueViolation:
        pass
    except Exception as e:
        print(e)
    finally:
        conn.rollback()
    
    # unique name category in credit_category
    try:
        cursor.execute("""
         insert into credit_category(cat_name)
         values('car loan')""")
    except psg.errors.UniqueViolation:
        pass
    except Exception as e:
        print(e)
    finally:
        conn.rollback()
    
    # positive number
    try:
        cursor.execute("""
         update person set expense_lim=-1 where login='admin'""")
    except psg.errors.CheckViolation:
        pass
    except Exception as e:
        print(e)
    finally:
        conn.rollback()
    
    try:
        cursor.execute("""
         update person set credit_lim=-1 where login='admin'""")
    except psg.errors.CheckViolation:
        pass
    except Exception as e:
        print(e)
    finally:
        conn.rollback()
    
    # wrong number
    try:
        cursor.execute("""
         update person set expense_lim=1000000000000 where login='admin'""")
    except psg.errors.CheckViolation:
        pass
    except Exception as e:
        print(e)
    finally:
        conn.rollback()
    
    try:
        cursor.execute("""
         update person set credit_lim=1000000000000 where login='admin'""")
    except psg.errors.CheckViolation:
        pass
    except Exception as e:
        print(e)
    finally:
        conn.rollback()
    
    try:
        cursor.execute("""
        insert into income(amount, rec_date, cat_id, person_id)
                       values(-6, '2022-02-02', 1, 1)""")
    except psg.errors.CheckViolation:
        pass
    except Exception as e:
        print(e)
    finally:
        conn.rollback()
    
    try:
        cursor.execute("""
        insert into income(amount, rec_date, cat_id, person_id)
                       values(1000000000000, '2022-02-02', 1, 1)""")
    except psg.errors.NumericValueOutOfRange:
        pass
    except Exception as e:
        print(e)
    finally:
        conn.rollback()
    
    try:
        cursor.execute("""
        insert into expense(amount, rec_date, cat_id, person_id)
                       values(-6, '2022-02-02', 1, 1)""")
    except psg.errors.CheckViolation:
        pass
    except Exception as e:
        print(e)
    finally:
        conn.rollback()
    
    try:
        cursor.execute("""
        insert into expense(amount, rec_date, cat_id, person_id)
                       values(1000000000000, '2022-02-02', 1, 1)""")
    except psg.errors.NumericValueOutOfRange:
        pass
    except Exception as e:
        print(e)
    finally:
        conn.rollback()
    
    try:
        cursor.execute("""
        insert into account(amount, acc_name, person_id)
                       values(-6, 'first', 1)""")
    except psg.errors.CheckViolation:
        pass
    except Exception as e:
        print(e)
    finally:
        conn.rollback()
    
    try:
        cursor.execute("""
        insert into account(amount, acc_name, person_id)
                       values(1000000000000, 'first', 1)""")
    except psg.errors.NumericValueOutOfRange:
        pass
    except Exception as e:
        print(e)
    finally:
        conn.rollback()
    
    try:
        cursor.execute("""
        insert into credit(amount, cat_id, person_id)
                       values(-6, 1, 1)""")
    except psg.errors.CheckViolation:
        pass
    except Exception as e:
        print(e)
    finally:
        conn.rollback()
    
    try:
        cursor.execute("""
        insert into credit(amount, cat_id, person_id)
                       values(1000000000000, 1, 1)""")
    except psg.errors.NumericValueOutOfRange:
        pass
    except Exception as e:
        print(e)
    finally:
        conn.rollback()
    
    # invalid income date
    try:
        cursor.execute("""
        insert into income(amount, rec_date, cat_id, person_id)
                       values(100, '2024-11-23', 1, 1)""")
    except psg.errors.CheckViolation:
        pass
    except Exception as e:
        print(e)
    finally:
        conn.rollback()
    
    try:
        cursor.execute("""
        update income set rec_date='2024-11-23' where person_id=1""")
    except psg.errors.CheckViolation:
        pass
    except Exception as e:
        print(e)
    finally:
        conn.rollback()
    
    # invalid expense date
    try:
        cursor.execute("""
        insert into expense(amount, rec_date, cat_id, person_id)
                       values(100, '2024-11-23', 1, 1)""")
    except psg.errors.CheckViolation:
        pass
    except Exception as e:
        print(e)
    finally:
        conn.rollback()
    
    try:
        cursor.execute("""
        update expense set rec_date='2024-11-23' where person_id=1""")
    except psg.errors.CheckViolation:
        pass
    except Exception as e:
        print(e)
    finally:
        conn.rollback()

tests()