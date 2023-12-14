from flask_login import UserMixin

class UserLogin(UserMixin):
    def FromDB(self, person_id, db):
        self.__user = db.get_person_by_id(person_id)
        return self
    
    def create(self, user):
        self.__user = user
        return self

    def get_id(self):
       return str(self.__user['person_id'])
    
    def get_info(self) -> dict:
        if self.__user:
            return {'person_id': self.__user['person_id'], 'login': self.__user['login'],
                 'credit_lim': self.__user['credit_lim'],
                 'expense_lim': self.__user['expense_lim']}
        print('__user', self.__user)
        return {}