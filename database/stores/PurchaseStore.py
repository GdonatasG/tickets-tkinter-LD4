from database.BaseStore import BaseStore
from database.dataclass.Purchase import Purchase
from database.StoreException import StoreException
import utils.Constants as const
import json


class PurchaseStore(BaseStore):
    __TAG = "PurchaseStore"

    def getPurchasesInSelectedHall(self, user_id, hall_id):
        purchases = []
        try:
            c = self.conn.cursor()
            c.execute("SELECT * FROM purchase WHERE user_id = ? and hall_id = ?", (user_id, hall_id))
            for row in c.fetchall():
                p = Purchase(row[0], row[1], row[2], row[3], row[4])
                purchases.append(p)
        except Exception as e:
            raise StoreException(
                self.__TAG + ", " + PurchaseStore.getPurchasesInSelectedHall.__name__ + ": nepavyko rasti pirkimu su vartotojo id {} ir sales id {}".format(
                    user_id, hall_id))
        return purchases

    def addNewPurchaseAsTransaction(self, listOfSeatsId, userId, hallId):
        try:
            c = self.conn.cursor()
            dict = {"seats": listOfSeatsId}
            for sId in listOfSeatsId:
                c.execute("UPDATE seat SET  status_id = ? WHERE id = ?", (const.REIKSME_UZIMTA, sId))
            c.execute("INSERT INTO purchase (user_id, hall_id, seats) VALUES (?,?,?)",
                      (userId, hallId, json.dumps(dict)))

            # jeigu pavyko atnaujinti visus duomenis, rezultatas irasomas i duomenu baze
            self.conn.commit()
        except Exception as e:
            # bent vieno is atnaujinimu nepavyko atlikti, rezultatas grazinamas atgal ir duomenu baze neatnaujinama
            self.conn.rollback()
            raise StoreException(
                self.__TAG + ", " + PurchaseStore.addNewPurchaseAsTransaction.__name__ + ": nepavyko atlikti pirkimo")
