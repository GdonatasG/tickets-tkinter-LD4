# Kai kurias bibliotekas importuoju priskirdamas kažkokiam kintamajam
# tai darau tam, jog daryti " from BIBLIOTEKA import * " nėra gera praktika
import tkinter.tix as tkx
from tkinter import font as tkfont
import utils.Constants as const
from database.stores.HallStore import HallStore
from database.stores.PurchaseStore import PurchaseStore
from database.stores.SeatStore import SeatStore
from database.stores.UserStore import UserStore
from utils.Auth import Auth
from windows.Home import Home
from windows.Login import Login


# Klasė Application paveldi informaciją iš klasės Tk
class Application(tkx.Tk):
    # Pagrindinis elementas programoje yra pasirinkta salė esanti duomenų bazeje
    # kadangi be jos nebus galimybės nuskaityti salės sėdimų vietų, vartotojo pirkimų ir kitų dalykų
    # Salės ID saugau kaip globalų kintamąjį, kuris bus prieinamas kitoms klasėms (frames)
    currentHallId = None

    # Konstruktorius
    def __init__(self, *args, **kwargs):
        # Tėvinės klasės konstruktorius
        tkx.Tk.__init__(self, *args, *kwargs)

        # Programoje naudojami font'ai
        self.welcome_msg_font = tkfont.Font(family='Helvetica', size=12, slant="italic")
        self.secondaryFont = tkfont.Font(family='Helvetica', size=11, slant="italic")

        # Pagrindinis langas sukuriamas kaip ScrolledWindow
        # tai suteikia galimybę elementams neįsitenkant lange uždėti langui Scrollbars
        sw = tkx.ScrolledWindow(self, scrollbar=tkx.AUTO)
        sw.pack(fill=tkx.BOTH, expand=1)
        self.minsize(const.MIN_WIDTH, const.MIN_HEIGHT)
        container = tkx.Frame(sw.window)

        # Sukuriamas vartotojo objektas aplikacijoje
        self._auth = Auth()

        # Nedarau paveldejimo is klases HallStore ir kitu, o kuriu nauja objekta Tai darau tam, jog duomenims is duomenu
        # bazes gauti yra imituojamas Repository pattern'as, kuriam reikalingas objektas
        # objektai sukuriami viena vieninteli nepakartojama karta
        self._hallStore = HallStore()
        self._seatStore = SeatStore()
        self._userStore = UserStore()
        self._purchaseStore = PurchaseStore()

        # Frames/langų dictionary
        self._frames = {}

        # Šiuo metu aplikacijoje esantis langas
        self._selected = None

        container.pack(side="top", fill="both", expand=True)

        self.container = container

        # Frames(Windows) objektu sukurimas
        # objektai sukuriami viena vieninteli nepakartojama karta
        self._frames[const.WINDOW_HOME] = Home(auth=self._auth, parent=container, controller=self,
                                               hallStore=self._hallStore,
                                               seatStore=self._seatStore, purchaseStore=self._purchaseStore)
        self._frames[const.WINDOW_LOGIN] = Login(auth=self._auth, parent=container, controller=self,
                                                 userStore=self._userStore)

        # Pradinis aplikacijos langas
        self.switch_frame(const.WINDOW_HOME)

    def switch_frame(self, window_name):
        """Destroys current frame and replaces it with a new one."""

        # Jeigu jau egzistuoja bent vienas langas, jis, t.y. Frame, yra sunaikinamas
        if self._selected is not None:
            self._selected.pack_forget()
            self._selected.grid_forget()

        self._selected = self._frames[window_name]
        self._selected.refresh()
        self._selected.pack()

        # instance of an object check
        '''print("-------------------------")
        for obj in gc.get_objects():
            if isinstance(obj, Home) or isinstance(obj, Login) or isinstance(obj, HallStore) or isinstance(obj,
                                                                                                           UserStore) or isinstance(
                obj, SeatStore) or isinstance(
                obj, Hall) or isinstance(
                obj, User) or isinstance(
                obj, Purchase):
                print(obj)'''


if __name__ == '__main__':
    # Application objekto sukurimas
    app = Application()
    app.mainloop()
