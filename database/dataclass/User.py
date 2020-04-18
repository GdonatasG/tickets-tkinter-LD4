class User:
    def __init__(self, id, name, password):
        self._id = id
        self._name = name
        self._password = password

    def getId(self):
        return self._id

    def setId(self, id):
        self._id = id

    def getName(self):
        return self._name

    def setName(self, name):
        self._name = name
