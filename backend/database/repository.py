import psycopg2 as psg
from psycopg2.extras import DictCursor



login = 'postgres'
pswd = 'rootroot'
class DB:
    def __init__(self):
        self.__conn = psg.connect(host='localhost',
                                database='financial',
                                user=login,
                                password=pswd)
        self.__cursor = self.__conn.cursor(cursor_factory=DictCursor)
    
    def get_person_by_id(self, person_id: int) -> dict or bool:
        try:
            self.__cursor.execute(f"select * from person where person_id={person_id}")
            res = self.__cursor.fetchone()
            if not res:
                self.__conn.rollback()
                return False
            return dict(res)
        except Exception as e:
            print('error in get_person_by_id', e)
            self.__conn.rollback()
            return False
    
    def get_person_by_login(self, login: str) -> dict or bool:
        try:
            self.__cursor.execute(f"select * from person where login='{login}'")
            res = self.__cursor.fetchone()
            if not res:
                self.__conn.rollback()
                return False
            return dict(res)
        except Exception as e:
            print('error in get_person_by_login', e)
            self.__conn.rollback()
            return False

    def update_lim(self, person_id: int, name_limit: str, value: int) -> bool:
        try:
            self.__cursor.execute(f"update person set {name_limit}={value} \
                                  where person_id={person_id}")
            self.__conn.commit()
        except Exception as e:
            print("error in update_lim", e)
            self.__conn.rollback()
            return False
        return True

    def write_record(self, table_name: str, person_id=0, person='', password='', amount=0, date='', 
                    category=0, acc_name='') -> bool:
        try:
            if table_name =='income' or table_name == 'expense':
                self.__cursor.execute(f"insert into {table_name} (amount, rec_date, cat_id, person_id)\
                            values ({amount}, '{date}', {category}, {person_id});")
            elif table_name == 'credit':
                self.__cursor.execute(f"insert into credit (amount, cat_id, person_id)\
                            values ({amount}, {category}, {person_id});")
            elif table_name == 'account':
                self.__cursor.execute(f"insert into account (acc_name, amount, person_id) \
                            values ('{acc_name}', {amount}, {person_id});")
            elif table_name == 'person':
                self.__cursor.execute(f"insert into person (login, password) \
                            values ('{person}', '{password}');")
            else:
                self.__conn.rollback()
                return False
        except Exception as e:
            print("error in write_record", e)
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
                self.__cursor.execute(f"select cat_name, amount, rec_date\
                                from {table_name} inner join {table_name}_category using(cat_id)\
                                where person_id={person_id} \
                                    and current_date - rec_date <= {days_interv} \
                                    order by rec_date desc;")
            elif table_name == 'credit':
                self.__cursor.execute(f"\
                            select cat_name, amount\
                            from credit inner join credit_category using(cat_id)\
                            where person_id={person_id};")
            elif table_name == 'account':
                self.__cursor.execute(f"select acc_name, amount\
                            from account\
                            where person_id={person_id};")
            else:
                self.__conn.rollback()
                return {}
        except Exception as e:
            print("error in get_records", e)
            self.__conn.rollback()
            return {}
        return list(map(dict, self.__cursor.fetchall()))

    def del_record(self, table_name: str, amount: int, person_id: int, date='', 
                    category=0, acc_name='') -> bool:
        try:
            if table_name =='income' or table_name == 'expense':
                self.__cursor.execute(f"delete from {table_name}\
                            where amount={amount} and rec_date='{date}'\
                            and cat_id={category} and person_id={person_id};")
            elif table_name == 'credit':
                self.__cursor.execute(f"delete from credit\
                            where amount={amount} and cat_id={category} \
                                and person_id={person_id};")
            elif table_name == 'account':
                self.__cursor.execute(f"delete from account\
                            where acc_name='{acc_name}'\
                                and amount={amount} and person_id={person_id};")
            else:
                self.__conn.rollback()
                return False
        except Exception as e:
            print("error in del_record", e)
            self.__conn.rollback()
            return False
        self.__conn.commit()
        return True
    
    def close(self):
        if self.__conn.closed != 1 and self.__cursor.closed != -1:
            self.__cursor.close()
            self.__conn.close()
