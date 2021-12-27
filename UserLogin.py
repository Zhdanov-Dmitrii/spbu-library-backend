class UserLogin(object):
    id_user = ''

    def fromDB(self,user_id,  db):
        print("!"+user_id)
        sql= f'SELECT id_user FROM public."public.user" WHERE id_user={user_id};'
        sql_result = db.engine.execute(sql)
        print("!"+sql)
        res = [row[0] for row in sql_result]
        print(res)
        if len(res) == 1:
            self.id_user =res[0][0]

        return self

    def __init__(self, id_user):
        self.id_user = str(id_user)

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return '3'
