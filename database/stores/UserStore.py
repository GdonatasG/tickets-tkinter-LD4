from database.BaseStore import BaseStore
from database.StoreException import StoreException
from database.dataclass.User import User


class UserStore(BaseStore):
    __TAG = "UserStore"

    def getUserByNameAndPassword(self, username, password):
        user = None
        try:
            c = self.conn.cursor()
            c.execute("SELECT * FROM user WHERE name=? and password=?", (username, password,))
            for row in c.fetchall():
                user = User(row[0], row[1], row[2])
            if not user:
                raise Exception
        except Exception as e:
            raise StoreException(
                self.__TAG + ", " + UserStore.getUserByNameAndPassword.__name__ + ": nepavyko rasti vartotojo su nurodytais duomenimis")

        return user
