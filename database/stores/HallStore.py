from database.BaseStore import BaseStore
from database.dataclass.Hall import Hall
from database.StoreException import StoreException


class HallStore(BaseStore):
    __TAG = "HallStore"

    def getHallById(self, id):
        hall = None
        try:
            c = self.conn.cursor()
            c.execute("SELECT * FROM hall WHERE id=?", (id,))
            for row in c.fetchall():
                hall = Hall(row[0], row[1], row[2])
            if not hall:
                raise Exception
        except Exception as e:
            raise StoreException(
                self.__TAG + ", " + HallStore.getHallById.__name__ + ": nepavyko rasti sales su nurodytu id {}".format(
                    id))

        return hall
