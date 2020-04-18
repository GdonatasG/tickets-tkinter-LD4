class Purchase:
    def __init__(self, id, user_id, hall_id, seats, time):
        self._id = id
        self._user_id = user_id
        self._hall_id = hall_id
        self._seats = seats
        self._time = time

    def getId(self):
        return self._id

    def setId(self, id):
        self._id = id

    def getUserId(self):
        return self._user_id

    def setUserId(self, id):
        self._user_id = id

    def getHallId(self):
        return self._hall_id

    def setHallId(self, id):
        self._hall_id = id

    def getSeats(self):
        return self._seats

    def setSeats(self, seats):
        self._seats = seats

    def getTime(self):
        return self._time

    def setTime(self, time):
        self._time = time
