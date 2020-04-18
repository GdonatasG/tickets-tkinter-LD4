from database.BaseStore import BaseStore
from database.dataclass.Seat import Seat
from database.StoreException import StoreException


class SeatStore(BaseStore):
    __TAG = "SeatStore"

    def getListOfSeats(self, hall_id, rows):
        seats = []
        try:
            c = self.conn.cursor()
            for i in range(rows):
                c.execute("SELECT * FROM seat WHERE hall_id = ? AND rown = ?", (hall_id, i + 1,))
                data = c.fetchall()
                if data:
                    seats.append([])
                for row in data:
                    seat = Seat(row[0], row[1], row[2], row[3], row[4])
                    seats[i].append(seat)
        except Exception as e:
            raise StoreException(
                self.__TAG + ", " + SeatStore.getListOfSeats.__name__ + ": nepavyko rasti sales su nurodytu id {}".format(
                    id))

        return seats

    def updateTest(self):
        try:
            c = self.conn.cursor()
            c.execute("UPDATE seat SET status_id=2 WHERE id=6000")
        except Exception as e:
            raise StoreException(
                self.__TAG + ", " + SeatStore.updateTest.__name__ + ": nepavyko")
