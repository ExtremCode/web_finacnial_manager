import psycopg2 as psg
from psycopg2 import sql
from psycopg2.extras import DictCursor

from database.settings import PostgresSettings


class DB:
    def get_person_by_id(self, person_id: int) -> dict or bool:
        try:
            conn = psg.connect(PostgresSettings().url)
            cursor = conn.cursor(cursor_factory=DictCursor)
        except Exception as e:
            print("cannot get connection in get_person_by_id: ", e)
            return False
        try:
            cursor.execute("select * from person where person_id = %s", [person_id])
            res = cursor.fetchone()
            if not res:
                conn.rollback()
                cursor.close()
                conn.close()
                return False
            cursor.close()
            conn.close()
            return dict(res)
        except Exception as e:
            print('error in get_person_by_id: ', e)
            conn.rollback()
            cursor.close()
            conn.close()
            return False

    def get_person_by_login(self, login: str) -> dict or bool:
        try:
            conn = psg.connect(PostgresSettings().url)
            cursor = conn.cursor(cursor_factory=DictCursor)
        except Exception as e:
            print("cannot get connection in get_person_by_login: ", e)
            return False
        try:
            cursor.execute("select * from person where login = %s", [login])
            res = cursor.fetchone()
            if not res:
                conn.rollback()
                cursor.close()
                conn.close()
                return False
            cursor.close()
            conn.close()
            return dict(res)
        except Exception as e:
            print('error in get_person_by_login: ', e)
            conn.rollback()
            cursor.close()
            conn.close()
            return False

    def update_lim(self, person_id: int, name_limit: str, value: int) -> bool:
        try:
            conn = psg.connect(PostgresSettings().url)
            cursor = conn.cursor(cursor_factory=DictCursor)
        except Exception as e:
            print("cannot get connection in update_lim: ", e)
            return False
        try:
            cursor.execute(sql.SQL("""update person set {} = %(val)s 
                                            where person_id = %(id)s;""")\
                                            .format(sql.Identifier(name_limit)),
                                    {'name_lim': name_limit, 'val': value, 'id': person_id})
            conn.commit()
        except Exception as e:
            print("error in update_lim: ", e)
            conn.rollback()
            cursor.close()
            conn.close()
            return False
        cursor.close()
        conn.close()
        return True

    def write_record(self, table_name: str, person_id=0, person='', password='', amount=0, date='', 
                    category=0, acc_name='') -> bool:
        try:
            conn = psg.connect(PostgresSettings().url)
            cursor = conn.cursor(cursor_factory=DictCursor)
        except Exception as e:
            print("cannot get connection in write_record: ", e)
            return False
        try:
            if table_name == 'income':
                cursor.execute("""
                                insert into income
                                (amount, rec_date, cat_id, person_id)
                                values (%(amnt)s, %(date)s, %(cat)s, %(id)s);""",
                            {'amnt': int(amount), 'date': date, 'cat': category, 'id': person_id})
            elif table_name == 'expense':
                cursor.execute("""
                                select cat_id from expense_category
                               where cat_name in ('car loan', 'mortgage', 'consumer credit')
                                """)
                categs = [int(dic['cat_id']) for dic in list(map(dict, cursor.fetchall()))]
                category = int(category)
                cursor.execute("""select count(*) from credit where person_id = %s""",
                               [person_id])
                if category in categs and cursor.rowcount > 0: # if expense is credit
                    try: 
                        cursor.fetchall()
                    except:
                        pass
                    cursor.execute("""
                                update credit
                                set amount = case when amount - %(amnt)s < 0
                                   then 0 else amount - %(amnt)s end
                                where person_id = %(id)s and cat_id = 
                                   (select cat_id from credit inner join 
                                   credit_category using(cat_id)
                                   where cat_name = (select cat_name from expense_category
                                                    where cat_id = %(cat)s))
                                returning cat_id""",
                            {'amnt': int(amount), 'id': person_id, 'cat': category})
                    if cursor.rowcount == 0:
                        try:
                            cursor.fetchall()
                        except:
                            pass
                        return False
                    cursor.execute("""delete from credit
                                where person_id = %s and amount = 0""", [person_id])

                cursor.execute("""
                                insert into expense
                                (amount, rec_date, cat_id, person_id)
                                values (%(amnt)s, %(date)s, %(cat)s, %(id)s);""",
                            {'amnt': int(amount), 'date': date, 'cat': category, 'id': person_id})
            elif table_name == 'credit':
                cursor.execute("""
                                select cat_id from credit where person_id = %s
                            """, [person_id]) # select categories
                res = [int(dic['cat_id']) for dic in list(map(dict, cursor.fetchall()))]
                category = int(category)
                if res != [] and category in res:
                    cursor.execute("""
                                update credit
                                set amount = amount + %(amnt)s
                                where person_id = %(id)s and cat_id = %(cat)s
                                """, {'id': person_id, 'amnt': int(amount), 'cat': category})
                else:
                    cursor.execute("""
                                insert into credit (amount, cat_id, person_id)
                                values (%(amnt)s, %(cat)s, %(id)s);""", 
                            {'amnt': int(amount), 'cat': category, 'id': person_id})
            elif table_name == 'account':
                cursor.execute("""
                                insert into account (acc_name, amount, person_id) 
                                values (%(acc)s, %(amnt)s, %(id)s);""",
                            {'acc': acc_name, 'amnt': int(amount), 'id': person_id})
            elif table_name == 'person':
                cursor.execute("""
                                insert into person (login, password)
                                values (%(pers)s, %(pswd)s);""",
                            {'pers': person, 'pswd': password})
            else:
                conn.rollback()
                cursor.close()
                conn.close()
                return False
        except Exception as e:
            print("error in write_record: ", e)
            conn.rollback()
            cursor.close()
            conn.close()
            return False
        conn.commit()
        cursor.close()
        conn.close()
        return True

    def get_records(self, table_name: str, person_id: int, days_interv=90) -> list[dict]:
        """
        get latest records over days_interv days
        """
        try:
            conn = psg.connect(PostgresSettings().url)
            cursor = conn.cursor(cursor_factory=DictCursor)
        except Exception as e:
            print("cannot get connection in get_records: ", e)
            return []
        try:
            if table_name =='income' or table_name == 'expense':
                cursor.execute(sql.SQL("""
                                select cat_name, amount, rec_date
                                from {} inner join {} using(cat_id)
                                where person_id = %(id)s 
                                and current_date - rec_date <= %(inter)s 
                                order by rec_date desc;""")\
                                    .format(sql.Identifier(table_name),
                                            sql.Identifier(table_name + '_category')),
                                    {'id': person_id, 'inter': days_interv})
            elif table_name == 'credit':
                cursor.execute("""
                            select cat_name, amount
                            from credit inner join credit_category using(cat_id)
                            where person_id = %s
                            order by amount desc""", [person_id])
            elif table_name == 'account':
                cursor.execute("""
                            select acc_name, amount
                            from account
                            where person_id = %s
                            order by amount desc""", [person_id])
            else:
                conn.rollback()
                cursor.close()
                conn.close()
                return []
        except Exception as e:
            print("error in get_records: ", e)
            conn.rollback()
            cursor.close()
            conn.close()
            return []
        result = list(map(dict, cursor.fetchall()))
        cursor.close()
        conn.close()
        return result

    def get_users(self) -> list[dict]:
        try:
            conn = psg.connect(PostgresSettings().url)
            cursor = conn.cursor(cursor_factory=DictCursor)
        except Exception as e:
            print("cannot get connection in get_users: ", e)
            return []
        try:
            cursor.execute("""
                                select login
                                from person
                                where login <> 'admin'
                                order by 1""")
        except Exception as e:
            print("error in get_users: ", e)
            conn.rollback()
            cursor.close()
            conn.close()
            return []
        result = list(map(dict, cursor.fetchall()))
        cursor.close()
        conn.close()
        return result

    def del_record(self, table_name: str, amount=0, person_id=0, date='', 
                    category=0, acc_name='', login='') -> bool:
        try:
            conn = psg.connect(PostgresSettings().url)
            cursor = conn.cursor(cursor_factory=DictCursor)
        except Exception as e:
            print("cannot get connection in del_record: ", e)
            return False
        try:
            if table_name =='income' or table_name == 'expense':
                cursor.execute(sql.SQL("""
                            delete from {}
                            where amount = %(amnt)s and rec_date = %(date)s
                            and cat_id = %(cat)s and person_id = %(id)s
                            and {} = (
                                    select {}
                                    from {}
                                    where amount = %(amnt)s and rec_date = %(date)s
                                    and cat_id = %(cat)s and person_id = %(id)s
                                    order by 1 desc
                                    limit 1)
                            returning person_id""")\
                                        .format(sql.Identifier(table_name),
                                                sql.Identifier(table_name[:3] + '_id'),
                                                sql.Identifier(table_name[:3] + '_id'),
                                                sql.Identifier(table_name)),
                            {'amnt': amount, 'date': date, 'cat': category, 'id': person_id})
                if len(cursor.fetchall()) == 0:
                    cursor.close()
                    conn.close()
                    return False
            elif table_name == 'credit':
                cursor.execute("""
                            delete from credit
                            where amount = %(amnt)s and cat_id = %(cat)s 
                            and person_id = %(id)s and cred_id = (
                                        select cred_id from credit
                                        where cat_id = %(cat)s and amount = %(amnt)s
                                        and person_id = %(id)s
                                        order by cred_id desc
                                        limit 1)
                            returning person_id""", 
                                {'amnt': amount, 'cat': category, 'id': person_id})
                if len(cursor.fetchall()) == 0:
                    cursor.close()
                    conn.close()
                    return False
            elif table_name == 'account':
                cursor.execute("""
                            delete from account
                            where acc_name = %(acc)s
                            and amount = %(amnt)s and person_id = %(id)s
                            and acc_id = (
                                select acc_id from account
                                where acc_name = %(acc)s
                                and amount = %(amnt)s and person_id = %(id)s
                                order by acc_id desc
                                limit 1)
                            returning person_id""",
                                {'acc': acc_name, 'amnt': amount, 'id': person_id})
                if len(cursor.fetchall()) == 0:
                    cursor.close()
                    conn.close()
                    return False
            elif table_name == 'person':
                cursor.execute("""
                            delete from person
                            where login = %s
                            returning person_id""", [login])
                if len(cursor.fetchall()) == 0:
                    cursor.close()
                    conn.close()
                    return False
            else:
                conn.rollback()
                cursor.close()
                conn.close()
                return False
        except Exception as e:
            print("error in del_record: ", e)
            conn.rollback()
            cursor.close()
            conn.close()
            return False
        conn.commit()
        cursor.close()
        conn.close()
        return True

    def export_to_xml(self, person_id: int) -> str:
        try:
            conn = psg.connect(PostgresSettings().url)
            cursor = conn.cursor(cursor_factory=DictCursor)
        except Exception as e:
            print("cannot get connection in export_to_xml: ", e)
            return ""
        try:
            result = """<?xml version="1.0" encoding="utf-8"?>\n<data>\n"""
            cursor.execute(f"""select query_to_xml(
                'select login, expense_lim as limit_of_expenses,
                credit_lim as limit_of_credits
                from person where person_id = {person_id}', true, false, '')""")
            result += cursor.fetchall()[0][0].replace("table", "person")
            cursor.execute(f"""select query_to_xml(
                'select cat_name as category, amount, rec_date as date  
                from income inner join income_category using(cat_id)
                where person_id = {person_id}', true, false, '')""")
            result += "\n" + cursor.fetchall()[0][0].replace("table", "income")
            cursor.execute(f"""select query_to_xml(
                'select cat_name as category, amount, rec_date as date 
                from expense inner join expense_category using(cat_id)
                where person_id = {person_id}', true, false, '')""")
            result += "\n" + cursor.fetchall()[0][0].replace("table", "expenses")
            cursor.execute(f"""select query_to_xml(
                'select cat_name as category_of_credit, amount
                from credit inner join credit_category using(cat_id)
                where person_id = {person_id}', true, false, '')""")
            result += "\n" + cursor.fetchall()[0][0].replace("table", "credits")
            cursor.execute(f"""select query_to_xml(
                'select acc_name as account_name, amount
                from account where person_id = {person_id}', true, false, '')""")
            result += "\n" + cursor.fetchall()[0][0].replace("table", "bank_accounts") + \
            "</data>"
        except Exception as e:
            print("error in export_to_xml: ", e)
            conn.rollback()
            cursor.close()
            conn.close()
            return ""
        cursor.close()
        conn.close()
        return result

    def get_timeseries(self, table_name: str, person_id: int) -> list[dict]:
        """"
        get timeseries of operations over the last 180 days period
        only for expense and income tables
        """
        try:
            conn = psg.connect(PostgresSettings().url)
            cursor = conn.cursor(cursor_factory=DictCursor)
        except Exception as e:
            print("cannot get connection in get_timeseries: ", e)
            return []
        try:
            if table_name not in ['expense', 'income']:
                return []
            cursor.execute(sql.SQL("""
                select concat(extract(year from rec_date),'-',
                            lpad(cast(extract(month from rec_date) as text), 2, cast('0' as text))) as time_id,
                sum(amount) as value
                from {}
                where current_date - rec_date <= 180 and person_id = %s
                group by extract(month from rec_date), extract(year from rec_date)
                order by 1;
                """).format(sql.Identifier(table_name)), [person_id])
        except Exception as e:
            print("error in get_timeseries: ", e)
            conn.rollback()
            cursor.close()
            conn.close()
            return []
        result = list(map(dict, cursor.fetchall()))
        cursor.close()
        conn.close()
        return result

    def get_amount(self, table_name: str, person_id: int) -> int:
        if table_name not in ['income', 'expense', 'credit', 'account']:
            return 0
        try:
            conn = psg.connect(PostgresSettings().url)
            cursor = conn.cursor(cursor_factory=DictCursor)
        except Exception as e:
            print("cannot get connection in get_amount: ", e)
            return 0
        try:
            if table_name == 'account':
                cursor.execute("""select case when (sum(amount) is null) 
                               then 0 else sum(amount) end case
                                from account
                                where person_id = %s""", [person_id])
            else:
                cursor.execute(sql.SQL("""select case when (sum(amount) is null) 
                                       then 0 else sum(amount) end case
                                from {}
                                where person_id = %s
                                and extract(month from current_date) =
                                extract(month from rec_date)""")\
                            .format(sql.Identifier(table_name)), [person_id])
        except Exception as e:
            print("error in get_amount: ", e)
            conn.rollback()
            cursor.close()
            conn.close()
            return 0
        result = cursor.fetchall()[0][0]
        cursor.close()
        conn.close()
        return result
    
    def get_categories(self, table_name: str) -> list[dict]:
        if table_name not in ['income_category', 'expense_category', 'credit_category']:
            return []
        try:
            conn = psg.connect(PostgresSettings().url)
            cursor = conn.cursor(cursor_factory=DictCursor)
        except Exception as e:
            print("cannot get connection in get_categories: ", e)
            return []
        try:
            cursor.execute(sql.SQL("""select cat_id as id, cat_name
                           from {}""").format(sql.Identifier(table_name)))
        except Exception as e:
            print("error in get_categories: ", e)
            conn.rollback()
            cursor.close()
            conn.close()
            return []
        result = list(map(dict, cursor.fetchall()))
        cursor.close()
        conn.close()
        return result
    
    def del_category(self, table_name: str, category: str) -> bool:
        if table_name not in ['income_category', 'expense_category', 'credit_category']:
            return False
        try:
            conn = psg.connect(PostgresSettings().url)
            cursor = conn.cursor(cursor_factory=DictCursor)
        except Exception as e:
            print("cannot get connection in del_category: ", e)
            return False
        try:
            cursor.execute(sql.SQL("""delete from {} where cat_name = %s""")\
                           .format(sql.Identifier(table_name)), [category])
        except Exception as e:
            print("error in del_category: ", e)
            conn.rollback()
            cursor.close()
            conn.close()
            return False
        conn.commit()
        cursor.close()
        conn.close()
        return True

    def write_category(self, table_name: str, category: str) -> bool:
        if table_name not in ['income_category', 'expense_category', 'credit_category']:
            return False
        try:
            conn = psg.connect(PostgresSettings().url)
            cursor = conn.cursor(cursor_factory=DictCursor)
        except Exception as e:
            print("cannot get connection in write_category: ", e)
            return False
        try:
            cursor.execute(sql.SQL("""insert into {} (cat_name) values (%s)""")\
                           .format(sql.Identifier(table_name)), [category])
        except Exception as e:
            print("error in write_categories: ", e)
            conn.rollback()
            cursor.close()
            conn.close()
            return False
        conn.commit()
        cursor.close()
        conn.close()
        return True
