import json
import threading
import tkinter.tix as tkx
from functools import partial

import utils.Constants as const
import utils.Extensions as ext
from database.StoreException import StoreException


# Klase Home paveldi informacija is klases Frame
class Home(tkx.Frame):

    def __init__(self, auth, parent, controller, hallStore, seatStore, purchaseStore):
        tkx.Frame.__init__(self, parent)
        self._controller = controller

        # Repozitorijos duomenų bazių veiksmams atlikti su skirtingomis lentelėmis
        self._hallStore = hallStore
        self._seatStore = seatStore
        self._purchaseStore = purchaseStore

        # Globalaus vartotojo klase perduota is Application
        self._auth = auth

        # ---Visi reikiami vartotojo dalykai ir veiksmai, kuriuos objektas islaikys pereinant is vieno lango i kita---

        # Kintamojo esme yra isjungti galimybe vartotojui atlikti kitas funkcijas, kol vykdoma kazkuri viena,
        # nes kai kurios funkcijos veikia naudojantis Thread'ais ir atlikti sekanciai funkcijai reikia ankstesnes funkcijos duomenu
        # , o skirtingi Thread'ai gali buti vykdomi vienu metu
        self._disabled = False

        # Sis masyvas naujai sukuriamas tik objektu sukurimo metu del to, jog butu galima issaugoti vartotojo pasirinktas vietas
        # pereinant is vienos lango i kita, o veliau griztant
        self._userSelectedSeatsId = []

    def refresh(self):
        # Vietos mygtuku matrica
        self._listOfSeatStatus = []
        self._listOfSeats = []
        self._seatButton = []
        # Vartotojo pirkimu masyvas
        self._userPurchases = []
        self._currentHall = None

        # Isvalomi visi Widget'ai ir sukuriami is naujo
        ext.clearWindow(self)
        self._controller.title(const.TITLE_HOME)

        threading.Thread(target=self._initHall()).start()
        if self._currentHall and self._listOfSeats:
            # Widgets
            self._welcomeMessageLabel = None
            self._authButton = None
            self._userActionsLabel = None

            # Frame for user area
            self._userAreaFrame = tkx.Frame(self)
            self._userAreaFrame.pack(pady=5)
            self._initUpdateWelcomeMessage()
            self._initUpdateAuthButton()

            self._chairStatusInfo()

            self._initSeatButtonsAndStatus()

            # Vartotojo nupirkti bilietai
            threading.Thread(target=self._initUserPurchases()).start()

            # Frame for bottom widgets to set all inline
            self._bottomWidgetsFrame = tkx.Frame(self)
            self._bottomWidgetsFrame.pack(pady=20)
            self._initUserActionsLabel()
            self._initClearButton()
            self._initBuyButton()



        else:
            self._userSelectedSeatsId = []
            error_tekstas = tkx.Label(self, text="Nepavyko gauti sales duomenu. Patikrinkite interneto rysi.")
            error_tekstas.pack(side="top", padx=20, pady=20)
            refresh_button = tkx.Button(self, text="BANDYTI IS NAUJO")
            refresh_button.pack(side="bottom", padx=20, pady=20)
            refresh_button.config(command=lambda: self._controller.switch_frame(const.WINDOW_HOME))

    def _initUpdateWelcomeMessage(self):
        if not self._welcomeMessageLabel:
            self._welcomeMessageLabel = tkx.Label(self._userAreaFrame, font=self._controller.welcome_msg_font)
            self._welcomeMessageLabel.pack(side=tkx.LEFT)
        if self._auth.getCurrentUser():
            self._welcomeMessageLabel.config(text=const.welcomeMessage(self._auth.getCurrentUser().getName()))
        else:
            self._welcomeMessageLabel.config(text=const.WELCOME_MESSAGE_NOT_LOGGED)

    def _initUpdateAuthButton(self):
        if not self._authButton:
            self._authButton = tkx.Button(self._userAreaFrame)
            self._authButton.pack(side=tkx.LEFT, padx=3)
            self._authButton.config(command=lambda: threading.Thread(target=self._authButtonAction()).start())
        if self._auth.getCurrentUser():
            self._authButton.config(text="Atsijungti")
        else:
            self._authButton.config(text="Prisijungti")

    def _authButtonAction(self):
        if not self._disabled:
            if not self._auth.getCurrentUser():
                self._controller.switch_frame(
                    const.WINDOW_LOGIN)
            else:
                # Pakeitimas į None leidžia pašalinti objektą(-us) iš atminties
                self._auth.setCurrentUser(None)
                self._userPurchases = None

                self._setActionMessage(const.DEFAULT_ACTIONS_LABEL_MESSAGE)
                self._updateSeatStatus()
                self._updateSeatButtons()
                self._initUpdateWelcomeMessage()
                self._initUpdateAuthButton()

    def _chairStatusInfo(self):
        "Sukuriami informaciniai laukai apie kedziu statusa"
        frame = tkx.Frame(self)
        frame.pack()
        laiptai = tkx.Label(frame, text="LAIPTAI", bg=const.SPALVA_LAIPTAI, relief=tkx.SOLID, borderwidth=1, padx=5,
                            pady=2)
        laiptai.pack(side="left", anchor=tkx.NW, expand=True, padx=5, pady=10)

        nepasirinkta = tkx.Label(frame, text="LAISVA/NEPASIRINKTA", bg=const.SPALVA_NEPASIRINKTA, relief=tkx.SOLID,
                                 borderwidth=1,
                                 padx=5,
                                 pady=2)
        nepasirinkta.pack(side="left", anchor=tkx.NW, expand=True, padx=5, pady=10)

        uzimta = tkx.Label(frame, text="UZIMTA", bg=const.SPALVA_UZIMTA, relief=tkx.SOLID, borderwidth=1, padx=5,
                           pady=2)
        uzimta.pack(side="left", anchor=tkx.NW, expand=True, padx=5, pady=10)

        gedimas = tkx.Label(frame, text="GEDIMAS", bg=const.SPALVA_GEDIMAS, relief=tkx.SOLID, borderwidth=1, padx=5,
                            pady=2)
        gedimas.pack(side="left", anchor=tkx.NW, expand=True, padx=5, pady=10)

        pasirinkta = tkx.Label(frame, text="PASIRINKTA", bg=const.SPALVA_PASIRINKTA, relief=tkx.SOLID, borderwidth=1,
                               padx=5,
                               pady=2)
        pasirinkta.pack(side="left", anchor=tkx.NW, expand=True, padx=5, pady=10)

        nupirkta = tkx.Label(frame, text="JUSU VIETA", bg=const.SPALVA_KATIK_NUPIRKTA, relief=tkx.SOLID, borderwidth=1,
                             padx=5,
                             pady=2)
        nupirkta.pack(side="left", anchor=tkx.NW, expand=True, padx=5, pady=10)

    def _initHall(self, interruptedAction=False):
        if not interruptedAction:
            self._disabled = True
        try:
            # Imami duomenys iš duomenų bazės su salės ID = 1
            hall = self._hallStore.getHallById(1)
            self._hallStore.complete()
            if hall:
                # Isvalomas vartotojo vietu pasirinkimo sarasas, jeigu naujai uzkrauta sale yra kita nei buvo pries tai
                if self._controller.currentHallId:
                    if self._controller.currentHallId != hall.getId():
                        self._userSelectedSeatsId = []

                self._currentHall = hall
                self._controller.currentHallId = self._currentHall.getId()
                self._initSeats(hall_id=self._currentHall.getId(), rows=self._currentHall.getRows(),
                                interruptedAction=True)
        except StoreException as e:
            print(e)
        if not interruptedAction:
            self._disabled = False

    def _initSeats(self, hall_id, rows, interruptedAction=False):
        if not interruptedAction:
            self._disabled = True
        try:
            self._listOfSeats = self._seatStore.getListOfSeats(hall_id, rows)
            self._seatStore.complete()
        except StoreException as e:
            print(e)
        if not interruptedAction:
            self._disabled = False

    def _initSeatButtonsAndStatus(self):
        for i in range(len(self._listOfSeats)):
            self._seatButton.append([])
            self._listOfSeatStatus.append([])
            frame = tkx.Frame(self)
            frame.pack()
            for j in range(len(self._listOfSeats[i])):
                if self._listOfSeats[i][j].getStatusId() == const.REIKSME_LAISVA:
                    if self._listOfSeats[i][j].getId() in self._userSelectedSeatsId:
                        self._listOfSeatStatus[i].append(const.REIKSME_PASIRINKTA)
                        self._seatButton[i].append(tkx.Button(frame, bg=const.SPALVA_PASIRINKTA))
                    else:
                        self._listOfSeatStatus[i].append(const.REIKSME_NEPASIRINKTA)
                        self._seatButton[i].append(tkx.Button(frame, bg=const.SPALVA_NEPASIRINKTA))
                elif self._listOfSeats[i][j].getStatusId() == const.REIKSME_UZIMTA:
                    self._listOfSeatStatus[i].append(const.REIKSME_UZIMTA)
                    self._seatButton[i].append(tkx.Button(frame, bg=const.SPALVA_UZIMTA))
                elif self._listOfSeats[i][j].getStatusId() == const.REIKSME_LAIPTAI:
                    self._listOfSeatStatus[i].append(const.REIKSME_LAIPTAI)
                    self._seatButton[i].append(tkx.Button(frame, bg=const.SPALVA_LAIPTAI, state=tkx.DISABLED))
                else:
                    self._listOfSeatStatus[i].append(const.REIKSME_GEDIMAS)
                    self._seatButton[i].append(tkx.Button(frame, bg=const.SPALVA_GEDIMAS))

                # Atliekamas patikrinimas tarp vartotojo pasirinktu vietu
                self._updateUserSelectionIfNeeded(i=i, j=j)

                # Pridedamas eiles ir vietos numeris kedei (jeigu tai nera laiptas)
                if self._listOfSeatStatus[i][j] != const.REIKSME_LAIPTAI:
                    self._seatButton[i][j].config(
                        text="{}:{}".format(self._listOfSeats[i][j].getRown(), self._listOfSeats[i][j].getSeatn()))

                self._seatButton[i][j].pack(side=tkx.LEFT, expand=True, padx=2, pady=2)
                self._seatButton[i][j].config(height=2, width=4,
                                              command=partial(self.onSeatClick, i, j, self._listOfSeats[i][j].getRown(),
                                                              self._listOfSeats[i][j].getSeatn()))

    def _updateSeatButtons(self):
        for i in range(len(self._listOfSeatStatus)):
            for j in range(len(self._listOfSeatStatus[i])):
                if self._listOfSeatStatus[i][j] == const.REIKSME_PASIRINKTA:
                    self._seatButton[i][j].config(bg=const.SPALVA_PASIRINKTA, state=tkx.NORMAL)
                elif self._listOfSeatStatus[i][j] == const.REIKSME_NEPASIRINKTA:
                    self._seatButton[i][j].config(bg=const.SPALVA_NEPASIRINKTA, state=tkx.NORMAL)
                elif self._listOfSeatStatus[i][j] == const.REIKSME_UZIMTA:
                    self._seatButton[i][j].config(bg=const.SPALVA_UZIMTA, state=tkx.NORMAL)
                elif self._listOfSeatStatus[i][j] == const.REIKSME_LAIPTAI:
                    self._seatButton[i][j].config(bg=const.SPALVA_LAIPTAI, state=tkx.DISABLED)
                elif self._listOfSeatStatus[i][j] == const.REIKSME_KATIK_NUSIPIRKO:
                    self._seatButton[i][j].config(bg=const.SPALVA_KATIK_NUPIRKTA, state=tkx.NORMAL)
                elif self._listOfSeatStatus[i][j] == const.REIKSME_GEDIMAS:
                    self._listOfSeatStatus[i][j] = const.REIKSME_GEDIMAS
                    self._seatButton[i][j].config(bg=const.SPALVA_GEDIMAS)

                # Atliekamas patikrinimas tarp vartotojo pasirinktu vietu
                self._updateUserSelectionIfNeeded(i=i, j=j)

                if self._listOfSeatStatus[i][j] != const.REIKSME_LAIPTAI:
                    self._seatButton[i][j].config(
                        text="{}:{}".format(self._listOfSeats[i][j].getRown(), self._listOfSeats[i][j].getSeatn()))

    def _updateSeatStatus(self):
        for i in range(len(self._listOfSeats)):
            for j in range(len(self._listOfSeats[i])):
                if self._listOfSeats[i][j].getStatusId() == const.REIKSME_LAISVA:
                    if self._listOfSeats[i][j].getId() in self._userSelectedSeatsId:
                        self._listOfSeatStatus[i][j] = const.REIKSME_PASIRINKTA
                    else:
                        self._listOfSeatStatus[i][j] = const.REIKSME_NEPASIRINKTA
                elif self._listOfSeats[i][j].getStatusId() == const.REIKSME_UZIMTA:
                    self._listOfSeatStatus[i][j] = const.REIKSME_UZIMTA
                elif self._listOfSeats[i][j].getStatusId() == const.REIKSME_LAIPTAI:
                    self._listOfSeatStatus[i][j] = const.REIKSME_LAIPTAI
                elif self._listOfSeats[i][j].getStatusId() == const.REIKSME_GEDIMAS:
                    self._listOfSeatStatus[i][j] = const.REIKSME_GEDIMAS

    def _updateUserSelectionIfNeeded(self, i, j):
        "Metodas pasalinti vartotojo pasirinkta vieta is saraso, jeigu ta vieta nera laisva"
        if self._listOfSeats[i][j].getStatusId() is not const.REIKSME_LAISVA and self._listOfSeats[i][
            j].getId() in self._userSelectedSeatsId:
            self._userSelectedSeatsId.remove(self._listOfSeats[i][j].getId())

    def _initUserPurchases(self, interruptedAction=False):
        if not interruptedAction:
            self._disabled = True
        if self._auth.getCurrentUser():
            try:
                self._userPurchases = self._purchaseStore.getPurchasesInSelectedHall(
                    self._auth.getCurrentUser().getId(),
                    self._currentHall.getId())
                self._purchaseStore.complete()

                for p in self._userPurchases:
                    d = json.loads(p.getSeats())
                    for s_id in d.get("seats"):
                        for i in range(len(self._listOfSeats)):
                            for j in range(len(self._listOfSeats[i])):
                                if self._listOfSeats[i][j].getId() == s_id:
                                    self._listOfSeatStatus[i][j] = const.REIKSME_KATIK_NUSIPIRKO

                self._updateSeatButtons()
            except StoreException as e:
                print(e)
        if not interruptedAction:
            self._disabled = False

    def _initUserActionsLabel(self):
        self._userActionsLabel = tkx.Label(self._bottomWidgetsFrame, font=self._controller.secondaryFont)
        self._userActionsLabel.pack(side="left", ipadx=10)
        self._setActionMessage(const.DEFAULT_ACTIONS_LABEL_MESSAGE)

    def _setActionMessage(self, msg):
        self._userActionsLabel.config(text=msg)

    def _initClearButton(self):
        clearButton = tkx.Button(self._bottomWidgetsFrame, text="Valyti pasirinkimus")
        clearButton.pack(side="left", padx=5)
        clearButton.config(command=partial(self._actionClear))

    def _initBuyButton(self):
        buyButton = tkx.Button(self._bottomWidgetsFrame, text="Pirkti")
        buyButton.pack(side="left", padx=5)
        buyButton.config(command=lambda: threading.Thread(target=self._actionBuy).start())

    def _actionClear(self):
        if not self._disabled:
            for i in range(len(self._listOfSeatStatus)):
                for j in range(len(self._listOfSeatStatus[i])):
                    if self._listOfSeatStatus[i][j] == const.REIKSME_PASIRINKTA:
                        self._listOfSeatStatus[i][j] = const.REIKSME_NEPASIRINKTA
                        self._userSelectedSeatsId.remove(self._listOfSeats[i][j].getId())

            self._updateSeatButtons()
            self._setActionMessage(const.DEFAULT_ACTIONS_LABEL_MESSAGE)

    def _actionBuy(self):
        if not self._disabled:
            self._disabled = True
            if self._auth.getCurrentUser():
                if self._userSelectedSeatsId and self._notTaken():
                    try:
                        self._purchaseStore.addNewPurchaseAsTransaction(listOfSeatsId=self._userSelectedSeatsId,
                                                                        userId=self._auth.getCurrentUser().getId(),
                                                                        hallId=self._currentHall.getId())
                        self._userSelectedSeatsId = []
                        self._initSeats(hall_id=self._currentHall.getId(), rows=self._currentHall.getRows(),
                                        interruptedAction=True)
                        self._initUserPurchases(interruptedAction=True)
                        self._setActionMessage("Pirkimas ivykdytas!")
                    except StoreException as e:
                        print(e)
                        self._setActionMessage("Ivyko klaida perkant bilietus!")
                else:
                    self._setActionMessage(
                        "Nepavyko atlikti pirkimo\nKai kurios vietos gali buti uzimtos arba nieko nepasirinkote!")
            else:
                self._setActionMessage("Prisijunkite noredami pirkti!")
            self._disabled = False

    def _notTaken(self):
        self._initSeats(self._currentHall.getId(), self._currentHall.getRows(), interruptedAction=True)
        for s in self._userSelectedSeatsId:
            for i in range(len(self._listOfSeats)):
                for j in range(len(self._listOfSeats[i])):
                    if self._listOfSeats[i][j].getId() == s and self._listOfSeats[i][
                        j].getStatusId() != const.REIKSME_LAISVA:
                        self._updateSeatStatus()
                        self._updateSeatButtons()
                        return False

        return True

    def onSeatClick(self, i, j, rown, seatn):
        if not self._disabled:
            if self._listOfSeatStatus[i][j] == const.REIKSME_NEPASIRINKTA:
                self._seatButton[i][j].config(bg=const.SPALVA_PASIRINKTA)
                self._listOfSeatStatus[i][j] = const.REIKSME_PASIRINKTA
                # Pridedamas vietos ID prie vartotojo pasirinktu vietu saraso
                self._userSelectedSeatsId.append(self._listOfSeats[i][j].getId())
            elif self._listOfSeatStatus[i][j] == const.REIKSME_PASIRINKTA:
                self._seatButton[i][j].config(bg=const.SPALVA_NEPASIRINKTA)
                self._listOfSeatStatus[i][j] = const.REIKSME_NEPASIRINKTA
                # Surandamas reikiamos vietos indeksas, reikalingas pasalinti sia vieta is pasirinktu
                targetSeat = [k for k in range(len(self._userSelectedSeatsId)) if
                              self._userSelectedSeatsId[k] == self._listOfSeats[i][j].getId()]
                # Pasalinama vieta is vartotojo pasirinktu vietu saraso
                self._userSelectedSeatsId.pop(targetSeat[0])
            elif self._listOfSeatStatus[i][j] == const.REIKSME_UZIMTA:
                self._setActionMessage("Vieta jau uzimta!")
            elif self._listOfSeatStatus[i][j] == const.REIKSME_GEDIMAS:
                self._setActionMessage("Negalima pasirinkti!")
            elif self._listOfSeatStatus[i][j] == const.REIKSME_KATIK_NUSIPIRKO:
                self._setActionMessage("Jusu sedima vieta: {} eile, {} vieta".format(rown, seatn))
