import tkinter.tix as tkx
import utils.Constants as const
import threading
import utils.Extensions as ext
from database.StoreException import StoreException


class Login(tkx.Frame):

    def __init__(self, auth, parent, controller, userStore):
        tkx.Frame.__init__(self, parent)
        self._auth = auth
        self._controller = controller
        self._userStore = userStore

        # Esant reikalui (ypac funkcijai, kuri vykdoma naudojantis Thread'ais)
        # galima isjungti galimybe vartotojui atlikti kitas funkcijas vykdant kazkuria kita
        self._disabled = False

    def refresh(self):
        ext.clearWindow(self)
        self._controller.title(const.TITLE_LOGIN)
        backButton = tkx.Button(self, text="<-- ATGAL")
        backButton.pack()
        backButton.config(
            command=lambda: self._controller.switch_frame(const.WINDOW_HOME) if not self._disabled else None)
        self._loginFrame = tkx.Frame(self)
        self._loginFrame.pack(pady=40)

        usernameFrame = tkx.Frame(self._loginFrame)
        usernameFrame.pack(pady=10)
        usernameInfo = tkx.Label(usernameFrame, text="Vartotojo vardas", font=self._controller.secondaryFont)
        usernameInfo.pack()
        usernameEntry = tkx.Entry(usernameFrame, width=30)
        usernameEntry.pack()

        passwordFrame = tkx.Frame(self._loginFrame)
        passwordFrame.pack(pady=5)
        passwordInfo = tkx.Label(passwordFrame, text="Vartotojo slaptazodis", font=self._controller.secondaryFont)
        passwordInfo.pack()
        passwordEntry = tkx.Entry(passwordFrame, width=30)
        passwordEntry.pack()

        actionMsg = tkx.Label(self._loginFrame, text="")
        actionMsg.pack()

        loginButton = tkx.Button(self._loginFrame, text="Prisijungti")

        loginButton.config(command=lambda: threading.Thread(target=self._actionLogin,
                                                            args=(usernameEntry,
                                                                  passwordEntry,
                                                                  actionMsg)).start() if not self._disabled else None)
        loginButton.pack(pady=10)

    def _actionLogin(self, username, password, message):
        if not self._disabled:
            self._disabled = True
            message.config(text="Jungiamasi..")
            if username.get() != "" and username.get() != " " and password.get() != "" and password.get() != " ":
                try:
                    u = self._userStore.getUserByNameAndPassword(username.get(), password.get())
                    self._userStore.complete()
                    if u:
                        self._auth.setCurrentUser(u)
                        self._controller.switch_frame(const.WINDOW_HOME)
                except StoreException as e:
                    print(e)
                    message.config(text="Neteisingi prisijungimo duomenys!")
            else:
                message.config(text="Uzpildykite visus laukus!")
            self._disabled = False
