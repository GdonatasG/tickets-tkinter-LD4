class Seat:
    def __init__(self, id, hall_id, rown, seatn, status_id):
        self._id = id
        self._hall_id = hall_id
        self._rown = rown
        self._seatn = seatn
        self._status_id = status_id

    def getId(self):
        return self._id

    def setId(self, id):
        self._id = id

    def getHallId(self):
        return self._hall_id

    def setHallId(self, id):
        self._hall_id = id

    def getRown(self):
        return self._rown

    def setRown(self, rown):
        self._rown = rown

    def getSeatn(self):
        return self._seatn

    def setSeatn(self, seatn):
        self._seatn = seatn

    def getStatusId(self):
        return self._status_id

    def setStatusId(self, id):
        self._status_id = id
