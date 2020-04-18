class Auth:
    def __init__(self):
        self._currentUser = None

    def getCurrentUser(self):
        return self._currentUser

    def setCurrentUser(self, user):
        self._currentUser = user
