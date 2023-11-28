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
            self.__cursor.execute("""
                                  update person set %(name_lim)s = %(val)s
                                  where person_id = %(id)s;""", 
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
                            where person_id = %s;""", [person_id])
            elif table_name == 'account':
                self.__cursor.execute("""
                            select acc_name, amount
                            from account
                            where person_id = %s;""", [person_id])
            else:
                self.__conn.rollback()
                return {}
        except Exception as e:
            print("error in get_records: ", e)
            self.__conn.rollback()
            return {}
        return list(map(dict, self.__cursor.fetchall()))

    def del_record(self, table_name: str, amount: int, person_id: int, date='', 
                    category=0, acc_name='') -> bool:
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
                                    limit 1);""")\
                                        .format(sql.Identifier(table_name),
                                                sql.Identifier(table_name[:3] + '_id'),
                                                sql.Identifier(table_name[:3] + '_id'),
                                                sql.Identifier(table_name)),
                            {'amnt': amount, 'date': date, 'cat': category, 'id': person_id})
            elif table_name == 'credit':
                self.__cursor.execute("""
                            delete from credit
                            where amount = %(amnt)s and cat_id = %(cat)s 
                            and person_id = %(id)s and cred_id = (
                                      select cred_id from credit
                                      where cat_id = %(cat)s and amount = %(amnt)s
                                      and person_id = %(id)s
                                      order by cred_id desc
                                      limit 1);""", 
                                {'amnt': amount, 'cat': category, 'id': person_id})
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
                                limit 1);""",
                                {'acc': acc_name, 'amnt': amount, 'id': person_id})
            else:
                self.__conn.rollback()
                return False
        except Exception as e:
            print("error in del_record: ", e)
            self.__conn.rollback()
            return False
        self.__conn.commit()
        return True
    
    def close(self):
        if not (self.__conn.closed or self.__cursor.closed):
            self.__cursor.close()
            self.__conn.close()
