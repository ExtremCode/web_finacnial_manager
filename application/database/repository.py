import psycopg2 as psg
from psycopg2 import sql


class DB:
    def __init__(self, connection: psg.extensions.connection,
                cursor: psg.extensions.cursor):
        self.__conn = connection
        self.__cursor = cursor
    
    def get_person_by_id(self, person_id: int) -> dict or bool:
        try:
            self.__cursor.execute("select * from person where person_id = %s", [person_id])
            res = self.__cursor.fetchone()
            if not res:
                self.__conn.rollback()
                return False
            return dict(res)
        except Exception as e:
            print('error in get_person_by_id: ', e)
            self.__conn.rollback()
            return False
    
    def get_person_by_login(self, login: str) -> dict or bool:
        try:
            self.__cursor.execute("select * from person where login = %s", [login])
            res = self.__cursor.fetchone()
            if not res:
                self.__conn.rollback()
                return False
            return dict(res)
        except Exception as e:
            print('error in get_person_by_login: ', e)
            self.__conn.rollback()
            return False

    def update_lim(self, person_id: int, name_limit: str, value: int) -> bool:
        try:
            self.__cursor.execute(sql.SQL("""update person set {} = %(val)s 
                                          where person_id = %(id)s;""")\
                                            .format(sql.Identifier(name_limit)),
                                  {'name_lim': name_limit, 'val': value, 'id': person_id})
            self.__conn.commit()
        except Exception as e:
            print("error in update_lim: ", e)
            self.__conn.rollback()
            return False
        return True

    def write_record(self, table_name: str, person_id=0, person='', password='', amount=0, date='', 
                    category=0, acc_name='') -> bool:
        try:
            if table_name =='income' or table_name == 'expense':
                self.__cursor.execute(sql.SQL("""
                                              insert into {} 
                                              (amount, rec_date, cat_id, person_id)
                                            values (%(amnt)s, %(date)s, %(cat)s, %(id)s);""")\
                                    .format(sql.Identifier(table_name)),
                            {'amnt': amount, 'date': date, 'cat': category, 'id': person_id})
            elif table_name == 'credit':
                self.__cursor.execute("""
                                    insert into credit (amount, cat_id, person_id)
                                    values (%(amnt)s, %(cat)s, %(id)s);""", 
                            {'amnt': amount, 'cat': category, 'id': person_id})
            elif table_name == 'account':
                self.__cursor.execute("""
                                    insert into account (acc_name, amount, person_id) 
                                    values (%(acc)s, %(amnt)s, %(id)s);""",
                            {'acc': acc_name, 'amnt': amount, 'id': person_id})
            elif table_name == 'person':
                self.__cursor.execute("""
                                    insert into person (login, password)
                                    values (%(pers)s, %(pswd)s);""",
                            {'pers': person, 'pswd': password})
            else:
                self.__conn.rollback()
                return False
        except Exception as e:
            print("error in write_record: ", e)
            self.__conn.rollback()
            return False
        self.__conn.commit()
        return True

    def get_records(self, table_name: str, person_id: int, days_interv=90) -> list[dict]:
        """
        get latest records over days_interv days
        """
        try:
            if table_name =='income' or table_name == 'expense':
                self.__cursor.execute(sql.SQL("""
                                select cat_name, amount, rec_date
                                from {} inner join {} using(cat_id)
                                where person_id = %(id)s 
                                and current_date - rec_date <= %(inter)s 
                                order by rec_date desc;""")\
                                    .format(sql.Identifier(table_name),
                                            sql.Identifier(table_name + '_category')),
                                    {'id': person_id, 'inter': days_interv})
            elif table_name == 'credit':
                self.__cursor.execute("""
                            select cat_name, amount
                            from credit inner join credit_category using(cat_id)
                            where person_id = %s
                            order by amount desc""", [person_id])
            elif table_name == 'account':
                self.__cursor.execute("""
                            select acc_name, amount
                            from account
                            where person_id = %s
                            order by amount desc""", [person_id])
            else:
                self.__conn.rollback()
                return []
        except Exception as e:
            print("error in get_records: ", e)
            self.__conn.rollback()
            return []
        return list(map(dict, self.__cursor.fetchall()))
    
    def get_users(self) -> list[dict]:
        try:
            self.__cursor.execute("""
                                select login
                                from person
                                where login <> 'admin'
                                order by 1""")
        except Exception as e:
            print("error in get_users: ", e)
            self.__conn.rollback()
            return []
        return list(map(dict, self.__cursor.fetchall()))

    def del_record(self, table_name: str, amount=0, person_id=0, date='', 
                    category=0, acc_name='', login='') -> bool:
        try:
            if table_name =='income' or table_name == 'expense':
                self.__cursor.execute(sql.SQL("""
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
                if len(self.__cursor.fetchall()) == 0:
                    return False
            elif table_name == 'credit':
                self.__cursor.execute("""
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
                if len(self.__cursor.fetchall()) == 0:
                    return False
            elif table_name == 'account':
                self.__cursor.execute("""
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
                if len(self.__cursor.fetchall()) == 0:
                    return False
            elif table_name == 'person':
                self.__cursor.execute("""
                            delete from person
                            where login = %s
                            returning person_id""", [login])
                if len(self.__cursor.fetchall()) == 0:
                    return False
            else:
                self.__conn.rollback()
                return False
        except Exception as e:
            print("error in del_record: ", e)
            self.__conn.rollback()
            return False
        self.__conn.commit()
        return True
    
    def export_to_xml(self, person_id: int) -> str:
        try:
            result = """<?xml version="1.0" encoding="utf-8"?>\n<data>\n"""
            self.__cursor.execute(f"""select query_to_xml(
               'select login, expense_lim as limit_of_expenses,
               credit_lim as limit_of_credits
               from person where person_id = {person_id}', true, false, '')""")
            result += self.__cursor.fetchall()[0][0].replace("table", "person")
            self.__cursor.execute(f"""select query_to_xml(
               'select cat_name as category, amount, rec_date as date  
               from income inner join income_category using(cat_id)
                where person_id = {person_id}', true, false, '')""")
            result += "\n" + self.__cursor.fetchall()[0][0].replace("table", "income")
            self.__cursor.execute(f"""select query_to_xml(
               'select cat_name as category, amount, rec_date as date 
               from expense inner join expense_category using(cat_id)
                where person_id = {person_id}', true, false, '')""")
            result += "\n" + self.__cursor.fetchall()[0][0].replace("table", "expenses")
            self.__cursor.execute(f"""select query_to_xml(
               'select cat_name as category_of_credit, amount
               from credit inner join credit_category using(cat_id)
                where person_id = {person_id}', true, false, '')""")
            result += "\n" + self.__cursor.fetchall()[0][0].replace("table", "credits")
            self.__cursor.execute(f"""select query_to_xml(
               'select acc_name as account_name, amount
               from account where person_id = {person_id}', true, false, '')""")
            result += "\n" + self.__cursor.fetchall()[0][0].replace("table", "bank_accounts") + \
            "</data>"
        except Exception as e:
            print("error in export_to_xml: ", e)
            self.__conn.rollback()
            return ""
        return result
    
    def get_timeseries(self, table_name: str, person_id: int) -> list[dict]:
        """"
        get timeseries of operations over the last 180 days period
        only for expense and income tables
        """
        try:
            if table_name not in ['expense', 'income']:
                return []
            self.__cursor.execute(sql.SQL("""
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
            self.__conn.rollback()
            return []
        return list(map(dict, self.__cursor.fetchall()))
    
    def close(self):
        if not (self.__conn.closed or self.__cursor.closed):
            self.__cursor.close()
            self.__conn.close()
