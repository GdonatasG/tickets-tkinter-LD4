class Hall:
    def __init__(self, id, name, rows):
        self._id = id
        self._name = name
        self._rows = rows

    def getId(self):
        return self._id

    def setId(self, id):
        self.id = id

    def getName(self):
        return self._name

    def setName(self, name):
        self._name = name

    def getRows(self):
        return self._rows

    def setRows(self, rows):
        self._rows = rows
